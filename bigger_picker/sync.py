from pyairtable.api.types import RecordDict
from rich.console import Console

import bigger_picker.config as config
from bigger_picker.airtable import AirtableManager
from bigger_picker.asana import AsanaManager
from bigger_picker.datamodels import Article, ArticleLLMExtract
from bigger_picker.openai import OpenAIManager
from bigger_picker.rayyan import RayyanManager
from bigger_picker.utils import (
    compute_dataset_value,
    fix_dataset,
    identify_duplicate_datasets,
)


class IntegrationManager:
    def __init__(
        self,
        asana_manager: AsanaManager,
        rayyan_manager: RayyanManager,
        airtable_manager: AirtableManager,
        openai_manager: OpenAIManager,
        console: Console | None = None,
        debug: bool = False,
    ):
        self.asana = asana_manager
        self.rayyan = rayyan_manager
        self.airtable = airtable_manager
        self.openai = openai_manager
        self.console = console or Console()
        self.debug = debug

    def sync_airtable_and_asana(
        self,
    ) -> None:
        self._log("Getting Asana tasks")
        self.asana.get_tasks(refresh=True)

        tasks = {}

        self._log("Getting Asana task IDs")
        for task in self.asana.tasks:
            tasks[
                self.asana.get_custom_field_value(
                    task, config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]
                )
            ] = task

        self._log("Getting Airtable records")
        datasets = self.airtable.tables["Datasets"].all()

        for dataset in datasets:
            dataset_bpipd = dataset["fields"].get("Dataset ID", None)

            if dataset_bpipd in tasks:
                # If the dataset has a matching task, update it
                self._log(f"Updating task {dataset_bpipd}...")
                updated_task = self.update_task_from_dataset(
                    tasks[dataset_bpipd],
                    dataset,
                )
            else:
                # If the dataset does not have a matching task, create one
                self._log("Creating task for dataset")
                updated_task = self.create_task_from_dataset(dataset)

                # Update the Airtable records with the Asana task IDs
                task_bpipd = self.asana.get_custom_field_value(
                    updated_task, config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]
                )
                payload = {"Dataset ID": task_bpipd}
                self._log(f"Updating Airtable record for {task_bpipd}")
                self.airtable.update_record("Datasets", dataset["id"], payload)
        self._log("Starting status sync")
        self.update_airtable_statuses()

    def update_task_from_dataset(self, task: dict, dataset: RecordDict) -> dict:
        dataset_vals = {
            "name": dataset["fields"].get("Dataset Name", None),
            "value": round(dataset["fields"]["Dataset Value"], 3)
            if dataset["fields"].get("Dataset Value", None) is not None
            else None,
            "url": self.airtable.make_url(dataset["id"]),
        }
        task_vals = {
            "name": task.get("name", None),
            "value": self.asana.get_custom_field_value(
                task, config.ASANA_CUSTOM_FIELD_IDS["Dataset Value"]
            ),
            "url": self.asana.get_custom_field_value(
                task, config.ASANA_CUSTOM_FIELD_IDS["Airtable Data"]
            ),
        }

        if dataset_vals == task_vals:
            self._log(
                f"No changes detected in {dataset['fields']['Dataset ID']}, skipping update."  # noqa: E501
            )
            return task

        update_payload = {
            "data": {
                "name": dataset_vals["name"],
                "custom_fields": {
                    config.ASANA_CUSTOM_FIELD_IDS["Dataset Value"]: dataset_vals[
                        "value"
                    ],
                    config.ASANA_CUSTOM_FIELD_IDS["Airtable Data"]: dataset_vals["url"],
                },
            }
        }

        task_gid = task.get("gid", None)
        if task_gid is None:
            raise ValueError("Task GID is missing in the provided task dictionary.")

        return self.asana.update_task(update_payload, task_gid)

    def create_task_from_dataset(self, dataset: RecordDict) -> dict:
        dataset_status = dataset["fields"].get("Status", None)
        if dataset_status is None:
            dataset_status = "Awaiting Triage"

        dataset_value = dataset["fields"].get("Dataset Value", None)
        airtable_url = self.airtable.make_url(dataset["id"])
        dataset_status_id = config.ASANA_STATUS_ENUM_VALUES.get(dataset_status, None)

        task_payload = {
            "data": {
                "name": dataset["fields"]["Dataset Name"],
                "projects": self.asana.project_id,
                "custom_fields": {
                    config.ASANA_CUSTOM_FIELD_IDS["Dataset Value"]: dataset_value,
                    config.ASANA_CUSTOM_FIELD_IDS["Airtable Data"]: airtable_url,
                    config.ASANA_CUSTOM_FIELD_IDS["Status"]: dataset_status_id,
                },
            }
        }

        created_task = self.asana.create_task(task_payload)

        # Set the BPIPD custom field to the Dataset ID
        updated_created_task = self.asana.fetch_task_with_custom_field(
            created_task["gid"], config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]
        )

        if updated_created_task is None:
            raise ValueError(
                f"Failed to fetch the created task with ID {created_task['gid']}."
            )

        created_task_bpipd = self.asana.get_custom_field_value(
            updated_created_task, config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]
        )

        payload = {"Dataset ID": created_task_bpipd}
        self.airtable.update_record("Datasets", dataset["id"], payload)

        return updated_created_task

    def update_airtable_statuses(self) -> None:
        self._log("Getting Asana tasks")
        # Always force refresh since we need up-to-date statuses from Asana
        tasks = self.asana.get_tasks(refresh=True)
        status_map = {}
        for task in tasks:
            status_dict = self.asana.get_custom_field_value(
                task, config.ASANA_CUSTOM_FIELD_IDS["Status"]
            )
            if status_dict is None:
                # For some reason, this task does not have a status set.
                continue

            if isinstance(status_dict, dict):
                status_name = status_dict.get("name")
            else:
                status_name = None

            status_map[
                self.asana.get_custom_field_value(
                    task, config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]
                )
            ] = status_name

        self._log("Getting Airtable records")
        datasets = self.airtable.tables["Datasets"].all()

        for dataset in datasets:
            dataset_bpipd = dataset["fields"].get("Dataset ID", None)

            if dataset_bpipd is None:
                # We are out of sync, so we skip this dataset.
                continue

            if dataset_bpipd in status_map:
                # If the dataset has a matching task, update it
                task_status = status_map[dataset_bpipd]
                dataset_status = dataset["fields"].get("Status", None)

                if task_status != dataset_status:
                    payload = {"Status": task_status}
                    self._log(f"Updating Airtable record {dataset['id']}")
                    self.airtable.update_record("Datasets", dataset["id"], payload)

                else:
                    self._log(f"No status change for dataset {dataset_bpipd}.")

    def upload_extraction_to_airtable(
        self,
        llm_extraction: ArticleLLMExtract,
        article_metadata: dict,
        pdf_path: str | None = None,
    ) -> RecordDict:
        def _convert_to_title_case(value):
            if isinstance(value, str):
                return value.title()
            elif isinstance(value, list):
                return [
                    item.title() if isinstance(item, str) else item for item in value
                ]
            return value

        extraction_dict = ArticleLLMExtract.model_dump(
            llm_extraction, by_alias=True, exclude_unset=True
        )

        article = Article(
            **article_metadata,
            **extraction_dict,
        )

        article_dict = article.model_dump(by_alias=True, exclude_unset=True)

        populations = article_dict.pop("populations", [])
        screen_time_measures = article_dict.pop("screen_time_measures", [])
        outcomes = article_dict.pop("outcomes", [])
        dataset_name = article_dict.pop("Dataset Name", None)

        article_record = self.airtable.create_record("Articles", article_dict)
        article_record_id = article_record["id"]

        if pdf_path is not None:
            self.airtable.upload_attachment(
                "Articles", article_record_id, "Fulltext", pdf_path
            )

        for population in populations:
            population["Rayyan ID"] = [article_record_id]
            self.airtable.create_record("Populations", population)

        for screen_time_measure in screen_time_measures:
            for key in screen_time_measure.keys():
                screen_time_measure[key] = _convert_to_title_case(
                    screen_time_measure[key]
                )
            screen_time_measure["Rayyan ID"] = [article_record_id]
            self.airtable.create_record("Screen Time Measures", screen_time_measure)

        for outcome in outcomes:
            for key in outcome.keys():
                outcome[key] = _convert_to_title_case(outcome[key])
            outcome["Rayyan ID"] = [article_record_id]
            self.airtable.create_record("Outcomes", outcome)

        # Create the dataset and sync to Airtable
        if dataset_name is None:
            author_last = article_metadata["Authors"].split(",")[0]
            year = article_metadata["Year"]
            dataset_name = f"{author_last}, {year}"

        dataset_payload = {
            "Dataset Name": dataset_name,
            "Status": "Awaiting Triage",
            "Total Sample Size": article_dict.get("Total Sample Size", None),
            "Dataset Contact Name": article_dict.get("Corresponding Author", None),
            "Dataset Contact Email": article_dict.get(
                "Corresponding Author Email", None
            ),
            "Countries of Data": article_dict.get("Countries of Data", []),
            "Articles: IDs": [article_record_id],
        }

        return self.airtable.create_record("Datasets", dataset_payload)

    def process_article(self, article: dict):
        pdf_path = self.rayyan.download_pdf(article)
        if pdf_path is None:
            # This shouldn't happen, but just in case, we skip this article
            return
        article_metadata = self.rayyan.extract_article_metadata(article)
        llm_extraction = self.openai.extract_article_info(pdf_path)
        if llm_extraction is None:
            # If the LLM extraction failed, we skip this article
            return
        dataset = self.upload_extraction_to_airtable(
            llm_extraction, article_metadata, pdf_path
        )
        self.create_task_from_dataset(dataset)
        self.rayyan.update_article_labels(article["id"])

    def updated_datasets_scores(self) -> bool:
        self._log("Scoring datasets...")

        datasets_included_statuses = ["Included", "Agreed & Awaiting Data"]
        datasets_potential_statuses = [
            "Validated",
            "Non-Priority",
            "Contacting Authors",
        ]
        self._log("Fetching datasets from Airtable")
        datasets = self.airtable.tables["Datasets"].all()

        datasets_included = []
        datasets_potential = []
        for dataset in datasets:
            if dataset["fields"].get("Status") in datasets_included_statuses:
                datasets_included.append(fix_dataset(dataset))

            elif dataset["fields"].get("Status") in datasets_potential_statuses:
                datasets_potential.append(fix_dataset(dataset))

        updated_any_datasets = False

        for dataset in datasets_potential:
            dataset_value = round(
                compute_dataset_value(dataset, datasets_included, datasets_potential), 3
            )
            payload = {"Dataset Value": dataset_value}
            if dataset["fields"].get("Dataset Value") != dataset_value:
                updated_any_datasets = True
                self.airtable.update_record("Datasets", dataset["id"], payload)

        return updated_any_datasets

    def mark_duplicates(self, thereshold=0.51):
        self._log("Marking duplicates...")
        datasets = self.airtable.tables["Datasets"].all()
        duplicates = identify_duplicate_datasets(datasets, threshold=thereshold)

        for dataset in datasets:
            dataset_id = dataset["id"]
            if dataset_id in duplicates:
                dataset_duplicates = dataset["fields"].get("Duplicates", [])
                for duplicate in duplicates[dataset_id]:
                    if duplicate not in dataset_duplicates:
                        dataset_duplicates.append(duplicate)
                payload = {"Possible Duplicates": dataset_duplicates}
                self.airtable.update_record("Datasets", dataset_id, payload)

    def sync(self):
        self.sync_airtable_and_asana()  # HACK: need to update status first
        any_datasets_updated = self.updated_datasets_scores()
        if any_datasets_updated:
            self._log("Datasets updated, syncing Airtable and Asana again.")
            self.sync_airtable_and_asana()
        else:
            self._log("No datasets updated, skipping second sync.")

    def _log(self, *args, **kwargs):
        if self.debug:
            self.console.log(*args, **kwargs)
