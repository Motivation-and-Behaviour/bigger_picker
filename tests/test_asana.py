import time
from unittest.mock import MagicMock

import pytest

import bigger_picker.config as config
from bigger_picker.asana import AsanaManager

# Test constants
author_token = "asana_test_token"
project_id = "proj123"
field_id = "fld456"


@pytest.fixture(autouse=True)
def patch_config(monkeypatch):
    # Ensure config.ASANA_PROJECT_ID env var and config attr
    monkeypatch.setenv("ASANA_TOKEN", author_token)
    monkeypatch.setattr(config, "ASANA_PROJECT_ID", project_id)


@pytest.fixture
def manager():
    # Explicitly pass project_id so defaults are correct
    mgr = AsanaManager(asana_token=author_token, project_id=project_id)
    # Inject mock TasksApi instance
    mgr.tasks_api_instance = MagicMock()
    return mgr


def test_get_tasks_initial_and_cached(manager):
    # Setup dummy get_tasks_for_project
    manager.tasks_api_instance.get_tasks_for_project.return_value = [{"id": "1"}]

    # First call should fetch and cache
    tasks1 = manager.get_tasks()
    manager.tasks_api_instance.get_tasks_for_project.assert_called_once_with(
        project_id, {"opt_fields": manager._OPT_FIELDS}
    )
    assert tasks1 == [{"id": "1"}]

    # Change return; without refresh, should return cached
    manager.tasks_api_instance.get_tasks_for_project.return_value = [{"id": "2"}]
    tasks2 = manager.get_tasks()
    assert tasks2 == [{"id": "1"}]

    # With refresh=True, should re-fetch
    tasks3 = manager.get_tasks(refresh=True)
    # Called a second time with same args
    manager.tasks_api_instance.get_tasks_for_project.assert_called_with(
        project_id, {"opt_fields": manager._OPT_FIELDS}
    )
    assert tasks3 == [{"id": "2"}]


def test_create_and_update_task(manager):
    # create_task should pass payload
    payload = {"name": "New Task"}
    manager.tasks_api_instance.create_task.return_value = {"id": "42", **payload}
    new = manager.create_task(payload)
    manager.tasks_api_instance.create_task.assert_called_once_with(payload, {})
    assert new["id"] == "42" and new["name"] == "New Task"

    # update_task should pass update_payload and task_id
    upd_payload = {"completed": True}
    manager.tasks_api_instance.update_task.return_value = {"id": "42", **upd_payload}
    updated = manager.update_task(upd_payload, "42")
    manager.tasks_api_instance.update_task.assert_called_once_with(
        upd_payload, "42", {}
    )
    assert updated["completed"] is True


def test_get_custom_field_value_and_fetch(manager, monkeypatch):
    # Prepare a fake task with custom fields
    task_dict = {
        "gid": "1",
        "custom_fields": [
            {"gid": field_id, "type": "text", "text_value": "hello"},
            {"gid": "other", "type": "number", "number_value": 123},
        ],
    }
    # Stub get_task: empty first two, then full
    calls = {"count": 0}

    def fake_get_task(tid, params):
        calls["count"] += 1
        if calls["count"] < 3:
            return {"gid": tid, "custom_fields": []}
        return task_dict

    manager.tasks_api_instance.get_task.side_effect = fake_get_task
    # Speed up sleep
    monkeypatch.setattr(time, "sleep", lambda x: None)

    result = manager.fetch_task_with_custom_field(
        "1", field_id, max_attempts=5, delay=0.1
    )
    assert result == task_dict
    assert calls["count"] == 3

    # Non-dict return should error
    manager.tasks_api_instance.get_task.side_effect = lambda tid, params: [
        "not",
        "a",
        "dict",
    ]
    with pytest.raises(ValueError):
        manager.fetch_task_with_custom_field("1", field_id, max_attempts=1, delay=0)


def test_fetch_timeout_returns_none(manager, monkeypatch):
    # Always return no matching custom field
    manager.tasks_api_instance.get_task.return_value = {"gid": "1", "custom_fields": []}
    monkeypatch.setattr(time, "sleep", lambda x: None)
    result = manager.fetch_task_with_custom_field(
        "1", "nonexistent", max_attempts=2, delay=0
    )
    assert result is None
