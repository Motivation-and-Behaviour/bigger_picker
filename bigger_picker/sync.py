from pyairtable.api.types import RecordDict

import bigger_picker.config as config
from bigger_picker.airtable import AirtableManager
from bigger_picker.asana import AsanaManager
from bigger_picker.datamodels import Article, ArticleLLMExtract
from bigger_picker.openai import OpenAIManager
from bigger_picker.rayyan import RayyanManager


class IntegrationManager:
    def __init__(
        self,
        asana_manager: AsanaManager,
        rayyan_manager: RayyanManager,
        airtable_manager: AirtableManager,
        openai_manager: OpenAIManager,
    ):
        self.asana = asana_manager
        self.rayyan = rayyan_manager
        self.airtable = airtable_manager
        self.openai = openai_manager

    def sync_airtable_and_asana(
        self,
    ) -> None:
        self.asana.get_tasks(refresh=True)

        task_ids = {}
        for task in self.asana.tasks:
            task_ids[
                self.asana.get_custom_field_value(
                    task, config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]
                )
            ] = task.get("gid")

        datasets = self.airtable.tables["Datasets"].all()

        for dataset in datasets:
            dataset_bpipd = dataset["fields"].get("Dataset ID", None)

            if dataset_bpipd in task_ids.keys():
                # If the dataset has a matching task, update it
                updated_task = self.update_task_from_dataset(
                    task_ids[dataset_bpipd],
                    dataset,
                )
            else:
                # If the dataset does not have a matching task, create one
                updated_task = self.create_task_from_dataset(dataset)

            # Update the Airtable records with the Asana task IDs
            task_bpipd = self.asana.get_custom_field_value(
                updated_task, config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]
            )
            payload = {"Dataset ID": task_bpipd}
            self.airtable.update_record("Datasets", dataset["id"], payload)
        self.update_airtable_statuses()

    def update_task_from_dataset(self, task_id: str, dataset: RecordDict) -> dict:
        dataset_value = dataset["fields"].get("Dataset Value", None)
        airtable_url = self.airtable.make_url(dataset["id"])

        update_payload = {
            "data": {
                "name": dataset["fields"]["Dataset Name"],
                "custom_fields": {
                    config.ASANA_CUSTOM_FIELD_IDS["Dataset Value"]: dataset_value,
                    config.ASANA_CUSTOM_FIELD_IDS["Airtable Data"]: airtable_url,
                },
            }
        }

        return self.asana.update_task(update_payload, task_id)

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

        datasets = self.airtable.tables["Datasets"].all()

        for dataset in datasets:
            dataset_bpipd = dataset["fields"].get("Dataset ID", None)

            if dataset_bpipd is None:
                # We are out of sync, so we skip this dataset.
                continue

            if dataset_bpipd in status_map.keys():
                # If the dataset has a matching task, update it
                status = status_map[dataset_bpipd]
                payload = {"Status": status}
                self.airtable.update_record("Datasets", dataset["id"], payload)

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

    def sync(self):
        self.sync_airtable_and_asana()
        # TODO: Calculate revised dataset value
        # TODO: Update dataset value in Airtable
        # TODO: Update the dataset value in Asana
