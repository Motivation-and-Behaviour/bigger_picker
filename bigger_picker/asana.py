import time

import asana

import bigger_picker.config as config
from bigger_picker.credentials import load_token


class AsanaManager:
    _OPT_FIELDS = ",".join(
        [
            "name",
            "projects",
            "projects.name",
            "completed",
            "custom_fields.display_value",
            "custom_fields.enum_value",
            "custom_fields.name",
            "custom_fields.number_value",
            "custom_fields.text_value",
            "custom_fields.type",
        ]
    )

    def __init__(self, asana_token: str | None = None, project_id: str | None = None):
        if asana_token is None:
            asana_token = load_token("ASANA_TOKEN")

        configuration = asana.Configuration()
        configuration.access_token = asana_token
        self.client = asana.ApiClient(configuration)
        self.tasks_api_instance = asana.TasksApi(self.client)
        self.project_id = project_id if project_id else config.ASANA_PROJECT_ID
        self.tasks: list[dict] = []

    def fetch_tasks(self):
        self.tasks = self.tasks_api_instance.get_tasks_for_project(
            self.project_id,
            {"opt_fields": self._OPT_FIELDS},
        )  # type: ignore

    def get_tasks(self, refresh: bool = False) -> list[dict]:
        if not self.tasks or refresh:
            self.fetch_tasks()
        return self.tasks

    def create_task(self, payload: dict) -> dict:
        return self.tasks_api_instance.create_task(payload, {})  # type: ignore

    def update_task(self, task_id: str, update_payload: dict) -> dict:
        return self.tasks_api_instance.update_task(update_payload, task_id, {})  # type: ignore

    def fetch_task_with_custom_field(
        self, task_id: str, field_id: str, max_attempts=5, delay=0.5
    ) -> dict | None:
        for _ in range(max_attempts):
            time.sleep(delay)
            task = self.tasks_api_instance.get_task(
                task_id, {"opt_fields": self._OPT_FIELDS}
            )

            if not isinstance(task, dict):
                raise ValueError(
                    f"Expected a dictionary for task, got {type(task)} instead."
                )

            field_value = self.get_custom_field_value(task, field_id)
            if field_value is not None:
                return task

            delay *= 2

        return None

    @staticmethod
    def get_custom_field_value(
        task: dict, field_id: str
    ) -> str | float | int | dict | None:
        type_lookup = {
            "text": "text_value",
            "number": "number_value",
            "enum": "enum_value",
        }

        for field in task.get("custom_fields", []):
            if field.get("gid") == field_id:
                return field.get(type_lookup.get(field["type"]), None)

        return None
