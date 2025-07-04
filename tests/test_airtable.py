import pytest
from pyairtable.testing import MockAirtable

import bigger_picker.config as config
from bigger_picker.airtable import AirtableManager


@pytest.fixture(autouse=True)
def airtable_config(monkeypatch):
    """
    Ensure config constants and AirtableManager.make_url defaults are set for tests.
    """
    # Environment token
    monkeypatch.setenv("AIRTABLE_TOKEN", "test_token")
    # Patch config values
    monkeypatch.setattr(config, "AIRTABLE_BASE_ID", "base123")
    monkeypatch.setattr(
        config, "AIRTABLE_TABLE_IDS", {"Datasets": "tbl123", "Articles": "tbl456"}
    )
    monkeypatch.setattr(config, "AIRTABLE_DEFAULT_VIEW_ID", "viw123")
    # Override make_url default parameters (defaults are bound at definition time)
    AirtableManager.make_url.__defaults__ = ("base123", "tbl123", "viw123")


@pytest.fixture
def manager():
    """Create an AirtableManager with explicit api_key to avoid loading from disk."""
    return AirtableManager(api_key="key123", base_id="base123")


def test_make_url_defaults(manager):
    # Now defaults for base_id, table_id, view_id are patched
    url = manager.make_url("recABC")
    assert url == ("https://airtable.com/base123/tbl123/viw123/recABC?blocks=hide")


def test_get_table_invalid(manager):
    with pytest.raises(ValueError) as exc:
        manager.get_table("UnknownTable")
    assert "does not exist" in str(exc.value)


def test_create_and_update_record(manager):
    table = manager.get_table("Datasets")
    with MockAirtable():
        assert table.all() == []

        payload = {"Dataset Name": "Test Dataset"}
        rec = manager.create_record("Datasets", payload)
        all_records = table.all()
        assert len(all_records) == 1
        assert all_records[0]["id"] == rec["id"]
        assert all_records[0]["fields"]["Dataset Name"] == "Test Dataset"

        updated = manager.update_record(
            "Datasets", rec["id"], {"Dataset Name": "New Test Dataset"}
        )
        assert updated["fields"]["Dataset Name"] == "New Test Dataset"
        assert table.all()[0]["fields"]["Dataset Name"] == "New Test Dataset"
