from pyairtable.api.types import RecordDict

import bigger_picker.config as config
from bigger_picker.airtable import AirtableManager
from bigger_picker.asana import AsanaManager
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
                    task_ids[dataset_bpipd], dataset
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
        update_payload = {
            "data": {
                "name": dataset["fields"]["Dataset Name"],
                "custom_fields": {
                    config.ASANA_CUSTOM_FIELD_IDS["Dataset Value"]: dataset["fields"][
                        "Dataset Value"
                    ],
                    config.ASANA_CUSTOM_FIELD_IDS[
                        "AirTable Data"
                    ]: self.airtable.make_url(dataset["id"]),
                },
            }
        }

        return self.asana.update_task(task_id, update_payload)

    def create_task_from_dataset(self, dataset: RecordDict) -> dict:
        dataset_status = dataset["fields"].get("Status", None)
        if dataset_status is None:
            dataset_status = "Awaiting Triage"

        dataset_status_id = config.ASANA_STATUS_ENUM_VALUES.get(dataset_status, None)

        task_payload = {
            "data": {
                "name": dataset["fields"]["Dataset Name"],
                "projects": self.asana.project_id,
                "custom_fields": {
                    config.ASANA_CUSTOM_FIELD_IDS["Dataset Value"]: dataset["fields"][
                        "Dataset Value"
                    ],
                    config.ASANA_CUSTOM_FIELD_IDS[
                        "AirTable Data"
                    ]: self.airtable.make_url(dataset["id"]),
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
