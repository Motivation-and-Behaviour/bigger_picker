from pyairtable import Api
from pyairtable.api.table import Table
from pyairtable.api.types import RecordDict

import bigger_picker.config as config
from bigger_picker.credentials import load_token


class AirtableManager:
    def __init__(
        self, api_key: str | None = None, base_id: str = config.AIRTABLE_BASE_ID
    ):
        if api_key is None:
            api_key = load_token("AIRTABLE_TOKEN")

        self.api = Api(api_key)
        self.base_id = base_id
        self.tables = {
            table_name: self.api.table(base_id, table_id)
            for table_name, table_id in config.AIRTABLE_TABLE_IDS.items()
        }

    def make_url(
        self,
        record_id: str,
        base_id: str = config.AIRTABLE_BASE_ID,
        table_id: str = config.AIRTABLE_TABLE_IDS["Datasets"],
        view_id: str = config.AIRTABLE_DEFAULT_VIEW_ID,
    ) -> str:
        return (
            f"https://airtable.com/{base_id}/{table_id}/{view_id}/{record_id}"
            "?copyLinkToCellOrRecordOrigin=gridView&blocks=hide"
        )

    def update_record(
        self, table_name: str, record_id: str, payload: dict
    ) -> RecordDict:
        table = self.get_table(table_name)
        return table.update(record_id, payload)

    def create_record(self, table_name: str, payload: dict) -> RecordDict:
        table = self.get_table(table_name)

        return table.create(payload)

    def get_table(self, table_name: str) -> Table:
        table = self.tables.get(table_name, None)
        if table is None:
            raise ValueError(
                f"Table '{table_name}' does not exist in the Airtable base."
            )
        return table
