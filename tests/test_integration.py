"""Tests for IntegrationManager class."""

from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

import bigger_picker.config as config
from bigger_picker.datamodels import ArticleLLMExtract, ScreeningDecision
from bigger_picker.integration import IntegrationManager, requires_services


class TestRequiresServicesDecorator:
    def test_allows_when_all_services_present(self):
        class MockManager:
            asana = MagicMock()
            airtable = MagicMock()

            @requires_services("asana", "airtable")
            def method(self):
                return "success"

        mgr = MockManager()
        assert mgr.method() == "success"

    def test_raises_when_service_missing(self):
        class MockManager:
            asana = MagicMock()
            airtable = None

            @requires_services("asana", "airtable")
            def method(self):
                return "success"

        mgr = MockManager()
        with pytest.raises(RuntimeError, match="Missing required services: airtable"):
            mgr.method()

    def test_raises_with_multiple_missing_services(self):
        class MockManager:
            asana = None
            airtable = None
            rayyan = MagicMock()

            @requires_services("asana", "airtable", "rayyan")
            def method(self):
                return "success"

        mgr = MockManager()
        with pytest.raises(RuntimeError, match="asana"):
            mgr.method()


class TestIntegrationManagerInit:
    def test_init_with_no_services(self):
        mgr = IntegrationManager()
        assert mgr.asana is None
        assert mgr.rayyan is None
        assert mgr.airtable is None
        assert mgr.openai is None
        assert mgr.tracker is None
        assert mgr.debug is False

    def test_init_with_all_services(self):
        asana = MagicMock()
        rayyan = MagicMock()
        airtable = MagicMock()
        openai = MagicMock()
        tracker = MagicMock()
        console = Console()

        mgr = IntegrationManager(
            asana_manager=asana,
            rayyan_manager=rayyan,
            airtable_manager=airtable,
            openai_manager=openai,
            batch_tracker=tracker,
            console=console,
            debug=True,
        )

        assert mgr.asana is asana
        assert mgr.rayyan is rayyan
        assert mgr.airtable is airtable
        assert mgr.openai is openai
        assert mgr.tracker is tracker
        assert mgr.console is console
        assert mgr.debug is True


@pytest.fixture
def mock_asana():
    asana = MagicMock()
    asana.tasks = []
    asana.project_id = "proj_123"
    return asana


@pytest.fixture
def mock_airtable():
    airtable = MagicMock()
    airtable.tables = {"Datasets": MagicMock(), "Articles": MagicMock()}
    return airtable


@pytest.fixture
def mock_rayyan():
    rayyan = MagicMock()
    rayyan.unextracted_label = "Unextracted"
    rayyan.extracted_label = "Extracted"
    return rayyan


@pytest.fixture
def mock_openai():
    openai = MagicMock()
    return openai


@pytest.fixture
def mock_tracker():
    tracker = MagicMock()
    return tracker


@pytest.fixture
def integration_manager(
    mock_asana, mock_airtable, mock_rayyan, mock_openai, mock_tracker
):
    return IntegrationManager(
        asana_manager=mock_asana,
        airtable_manager=mock_airtable,
        rayyan_manager=mock_rayyan,
        openai_manager=mock_openai,
        batch_tracker=mock_tracker,
        debug=True,
    )


class TestUpdateTaskFromDataset:
    def test_skips_when_no_changes(
        self, integration_manager, mock_asana, mock_airtable
    ):
        task = {
            "gid": "task_1",
            "name": "Dataset A",
            "custom_fields": [],
        }
        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset Name": "Dataset A",
                "Dataset Value": 0.5,
                "Dataset ID": "BP001",
            },
        }

        # Mock get_custom_field_value to return matching values
        mock_asana.get_custom_field_value.side_effect = lambda t, fid: {
            config.ASANA_CUSTOM_FIELD_IDS["Dataset Value"]: 0.5,
            config.ASANA_CUSTOM_FIELD_IDS["Airtable Data"]: mock_airtable.make_url(
                "rec_1"
            ),
        }.get(fid)

        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"

        _ = integration_manager.update_task_from_dataset(task, dataset)
        # Should return original task, no update called
        mock_asana.update_task.assert_not_called()

    def test_updates_when_values_differ(
        self, integration_manager, mock_asana, mock_airtable
    ):
        task = {
            "gid": "task_1",
            "name": "Old Name",
            "custom_fields": [],
        }
        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset Name": "New Name",
                "Dataset Value": 0.75,
                "Dataset ID": "BP001",
            },
        }

        mock_asana.get_custom_field_value.return_value = None
        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"
        mock_asana.update_task.return_value = {"gid": "task_1", "name": "New Name"}

        result = integration_manager.update_task_from_dataset(task, dataset)

        mock_asana.update_task.assert_called_once()
        assert result["name"] == "New Name"

    def test_raises_when_task_gid_missing(
        self, integration_manager, mock_asana, mock_airtable
    ):
        task = {"name": "No GID"}  # Missing gid
        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset Name": "Test",
                "Dataset Value": 0.5,
            },
        }

        mock_asana.get_custom_field_value.return_value = None
        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"

        with pytest.raises(ValueError, match="Task GID is missing"):
            integration_manager.update_task_from_dataset(task, dataset)


class TestCreateTaskFromDataset:
    def test_creates_task_and_updates_airtable(
        self, integration_manager, mock_asana, mock_airtable
    ):
        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset Name": "New Dataset",
                "Status": "Awaiting Triage",
                "Dataset Value": 0.5,
                "Searches": [],
            },
        }

        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"
        mock_asana.create_task.return_value = {"gid": "new_task_1"}
        mock_asana.fetch_task_with_custom_field.return_value = {
            "gid": "new_task_1",
            "custom_fields": [],
        }
        mock_asana.get_custom_field_value.return_value = "BP001"

        _ = integration_manager.create_task_from_dataset(dataset)

        mock_asana.create_task.assert_called_once()
        mock_airtable.update_record.assert_called()

    def test_raises_when_fetch_fails(
        self, integration_manager, mock_asana, mock_airtable
    ):
        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset Name": "New Dataset",
                "Searches": [],
            },
        }

        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"
        mock_asana.create_task.return_value = {"gid": "task_1"}
        mock_asana.fetch_task_with_custom_field.return_value = None

        with pytest.raises(ValueError, match="Failed to fetch"):
            integration_manager.create_task_from_dataset(dataset)


class TestUploadExtractionToAirtable:
    def test_creates_article_and_related_records(
        self, integration_manager, mock_airtable
    ):
        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 500,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        article_metadata = {
            "Rayyan ID": 123,
            "Article Title": "Test Article",
            "Authors": "Smith, Jones",
            "Journal": "Test Journal",
            "DOI": "10.1000/xyz",
            "Year": 2020,
            "Search": [],
        }

        mock_airtable.create_record.return_value = {"id": "rec_article_1"}

        _ = integration_manager.upload_extraction_to_airtable(
            llm_extraction, article_metadata
        )

        # Should create Article, then Dataset
        assert mock_airtable.create_record.call_count >= 2

    def test_uploads_pdf_attachment(self, integration_manager, mock_airtable, tmp_path):
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"PDF content")

        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 100,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        article_metadata = {
            "Rayyan ID": 123,
            "Article Title": "Test",
            "Authors": "Smith",
            "Journal": "Journal",
            "DOI": "",
            "Year": 2020,
            "Search": [],
        }

        mock_airtable.create_record.return_value = {"id": "rec_1"}

        integration_manager.upload_extraction_to_airtable(
            llm_extraction, article_metadata, pdf_path=str(pdf_path)
        )

        mock_airtable.upload_attachment.assert_called_once()


class TestMarkDuplicates:
    def test_marks_duplicates_in_airtable(self, integration_manager, mock_airtable):
        datasets = [
            {"id": "rec_1", "fields": {"Dataset Name": "Smith 2020", "Duplicates": []}},
            {"id": "rec_2", "fields": {"Dataset Name": "Smith 2020", "Duplicates": []}},
        ]
        mock_airtable.tables["Datasets"].all.return_value = datasets

        with patch(
            "bigger_picker.integration.utils.identify_duplicate_datasets"
        ) as mock_dup:
            mock_dup.return_value = {"rec_1": ["rec_2"], "rec_2": ["rec_1"]}
            integration_manager.mark_duplicates()

        # Should update both records
        assert mock_airtable.update_record.call_count == 2

    def test_skips_already_marked_duplicates(self, integration_manager, mock_airtable):
        datasets = [
            {
                "id": "rec_1",
                "fields": {"Dataset Name": "Smith 2020", "Duplicates": ["rec_2"]},
            },
            {
                "id": "rec_2",
                "fields": {"Dataset Name": "Smith 2020", "Duplicates": ["rec_1"]},
            },
        ]
        mock_airtable.tables["Datasets"].all.return_value = datasets

        with patch(
            "bigger_picker.integration.utils.identify_duplicate_datasets"
        ) as mock_dup:
            mock_dup.return_value = {"rec_1": ["rec_2"], "rec_2": ["rec_1"]}
            integration_manager.mark_duplicates()

        # Should not update if duplicates already match
        mock_airtable.update_record.assert_not_called()


class TestScreenAbstract:
    def test_screens_and_actions_decision(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        article = {"id": 123, "abstracts": [{"content": "This is the abstract text"}]}

        decision = ScreeningDecision(
            vote="include",
            matched_inclusion=[1, 2],
            failed_inclusion=None,
            triggered_exclusion=None,
            exclusion_reasons=None,
            rationale="Meets criteria",
        )
        mock_openai.screen_record_abstract.return_value = decision

        integration_manager.screen_abstract(article)

        mock_openai.screen_record_abstract.assert_called_once_with(
            "This is the abstract text"
        )
        mock_rayyan.update_article_labels.assert_called_once()

    def test_skips_when_no_abstract(self, integration_manager, mock_openai):
        article = {"id": 123, "abstracts": []}

        integration_manager.screen_abstract(article)

        mock_openai.screen_record_abstract.assert_not_called()


class TestScreenFulltext:
    def test_screens_fulltext(
        self, integration_manager, mock_openai, mock_rayyan, tmp_path
    ):
        pdf_path = str(tmp_path / "article.pdf")
        article = {"id": 123}

        mock_rayyan.download_pdf.return_value = pdf_path
        decision = ScreeningDecision(
            vote="exclude",
            matched_inclusion=None,
            failed_inclusion=None,
            triggered_exclusion=[1],
            exclusion_reasons=None,
            rationale="Wrong population",
        )
        mock_openai.screen_record_fulltext.return_value = decision

        integration_manager.screen_fulltext(article)

        mock_rayyan.download_pdf.assert_called_once_with(article)
        mock_openai.screen_record_fulltext.assert_called_once_with(pdf_path)

    def test_skips_when_no_pdf(self, integration_manager, mock_rayyan, mock_openai):
        article = {"id": 123}
        mock_rayyan.download_pdf.return_value = None

        integration_manager.screen_fulltext(article)

        mock_openai.screen_record_fulltext.assert_not_called()


class TestActionScreeningDecision:
    def test_include_abstract_decision(self, integration_manager, mock_rayyan):
        decision = {"vote": "include", "rationale": "Meets criteria"}

        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=True
        )

        mock_rayyan.update_article_labels.assert_called_once()
        call_args = mock_rayyan.update_article_labels.call_args
        assert config.RAYYAN_LABELS["abstract_included"] in call_args[0][1]

    def test_exclude_fulltext_decision_with_reason(
        self, integration_manager, mock_rayyan
    ):
        decision = {
            "vote": "exclude",
            "triggered_exclusion": [1],
            "rationale": "Wrong population",
        }

        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=False
        )

        mock_rayyan.update_article_labels.assert_called()
        mock_rayyan.create_article_note.assert_called_once()

    def test_invalid_vote_skipped(self, integration_manager, mock_rayyan):
        decision = {"vote": "maybe", "rationale": "Unsure"}

        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=True
        )

        mock_rayyan.update_article_labels.assert_not_called()

    def test_batch_removes_pending_label(self, integration_manager, mock_rayyan):
        decision = {"vote": "include", "rationale": "Good"}

        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=True, is_batch=True
        )

        call_args = mock_rayyan.update_article_labels.call_args
        plan = call_args[0][1]
        assert config.RAYYAN_LABELS["batch_pending"] in plan
        assert plan[config.RAYYAN_LABELS["batch_pending"]] == -1


class TestCreateAbstractScreeningBatch:
    def test_prepares_and_submits_batch(
        self, integration_manager, mock_openai, mock_rayyan, mock_tracker, tmp_path
    ):
        articles = [
            {"id": 1, "abstracts": [{"content": "Abstract 1"}]},
            {"id": 2, "abstracts": [{"content": "Abstract 2"}]},
            {"id": 3, "abstracts": []},  # Should be skipped
        ]

        mock_openai.prepare_abstract_body.return_value = {"model": "test", "input": []}

        with patch.object(integration_manager, "_submit_batch") as mock_submit:
            integration_manager.create_abstract_screening_batch(articles)

        # Should have prepared 2 requests (article 3 has no abstract)
        assert mock_openai.prepare_abstract_body.call_count == 2
        mock_submit.assert_called_once()


class TestCreateFulltextScreeningBatch:
    def test_prepares_and_submits_batch(
        self, integration_manager, mock_openai, mock_rayyan, mock_tracker, tmp_path
    ):
        articles = [{"id": 1}, {"id": 2}]

        mock_rayyan.download_pdf.return_value = "/path/to/pdf"
        mock_file = MagicMock()
        mock_file.id = "file_123"
        mock_openai.upload_file.return_value = mock_file
        mock_openai.prepare_fulltext_body.return_value = {
            "model": "test",
            "messages": [],
        }

        with patch.object(integration_manager, "_submit_batch") as mock_submit:
            integration_manager.create_fulltext_screening_batch(articles)

        assert mock_openai.upload_file.call_count == 2
        mock_submit.assert_called_once()

    def test_skips_articles_without_pdf(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        articles = [{"id": 1}]
        mock_rayyan.download_pdf.return_value = None

        with patch.object(integration_manager, "_submit_batch") as mock_submit:
            integration_manager.create_fulltext_screening_batch(articles)

        mock_openai.upload_file.assert_not_called()
        mock_submit.assert_not_called()


class TestSubmitBatch:
    def test_writes_jsonl_and_creates_batch(
        self, integration_manager, mock_openai, mock_tracker, tmp_path, monkeypatch
    ):
        # Change to tmp_path for file operations
        monkeypatch.chdir(tmp_path)

        requests = [
            {"custom_id": "abstract-1", "method": "POST", "body": {}},
            {"custom_id": "abstract-2", "method": "POST", "body": {}},
        ]

        mock_batch = MagicMock()
        mock_batch.id = "batch_123"
        mock_openai.create_batch.return_value = mock_batch

        integration_manager._submit_batch(requests, "abstract_screen")

        mock_openai.create_batch.assert_called_once()
        mock_tracker.add_batch.assert_called_once_with("batch_123", "abstract_screen")


class TestProcessPendingBatches:
    def test_processes_completed_batch(self, integration_manager, mock_openai):
        pending = {"batch_1": {"type": "abstract_screen"}}

        mock_batch = MagicMock()
        mock_batch.status = "completed"
        mock_batch.output_file_id = "output_123"
        mock_openai.retrieve_batch.return_value = mock_batch

        with patch.object(
            integration_manager, "_handle_completed_batch"
        ) as mock_handle:
            integration_manager.process_pending_batches(pending)

        mock_handle.assert_called_once_with("output_123", "abstract_screen", "batch_1")

    def test_handles_failed_batch(self, integration_manager, mock_openai):
        pending = {"batch_1": {"type": "abstract_screen"}}

        mock_batch = MagicMock()
        mock_batch.status = "failed"
        mock_openai.retrieve_batch.return_value = mock_batch

        # Should not raise, just log
        integration_manager.process_pending_batches(pending)

    def test_handles_in_progress_batch(self, integration_manager, mock_openai):
        pending = {"batch_1": {"type": "abstract_screen"}}

        mock_batch = MagicMock()
        mock_batch.status = "in_progress"
        mock_openai.retrieve_batch.return_value = mock_batch

        # Should not call handle
        with patch.object(
            integration_manager, "_handle_completed_batch"
        ) as mock_handle:
            integration_manager.process_pending_batches(pending)

        mock_handle.assert_not_called()


class TestHandleCompletedBatch:
    def test_processes_abstract_results(
        self, integration_manager, mock_openai, mock_tracker
    ):
        output_file_id = "output_123"
        batch_type = "abstract_screen"
        batch_id = "batch_1"

        # Mock file content response
        mock_content = MagicMock()
        mock_content.text = '{"custom_id": "abstract-123", "response": {"status_code": 200, "body": {"choices": [{"message": {"content": "{\\"vote\\": \\"include\\", \\"rationale\\": \\"Good\\"}"}}]}}}'  # noqa: E501
        mock_openai.client.files.content.return_value = mock_content

        decision = ScreeningDecision(
            vote="include",
            matched_inclusion=None,
            failed_inclusion=None,
            triggered_exclusion=None,
            exclusion_reasons=None,
            rationale="Good",
        )
        mock_openai.parse_screening_decision.return_value = decision

        with patch.object(integration_manager, "_action_screening_decision"):
            integration_manager._handle_completed_batch(
                output_file_id, batch_type, batch_id
            )

        mock_tracker.mark_completed.assert_called_once_with(batch_id)


class TestSync:
    def test_calls_sync_methods(self, integration_manager):
        with (
            patch.object(integration_manager, "sync_airtable_and_asana") as mock_sync,
            patch.object(integration_manager, "updated_datasets_scores") as mock_scores,
        ):
            mock_scores.return_value = False
            integration_manager.sync()

        mock_sync.assert_called_once()
        mock_scores.assert_called_once()

    def test_syncs_again_when_datasets_updated(self, integration_manager):
        with (
            patch.object(integration_manager, "sync_airtable_and_asana") as mock_sync,
            patch.object(integration_manager, "updated_datasets_scores") as mock_scores,
        ):
            mock_scores.return_value = True
            integration_manager.sync()

        # Should be called twice
        assert mock_sync.call_count == 2


class TestLog:
    def test_logs_when_debug_enabled(self, integration_manager):
        integration_manager.debug = True
        integration_manager.console = MagicMock()

        integration_manager._log("Test message")

        integration_manager.console.log.assert_called_once_with("Test message")

    def test_does_not_log_when_debug_disabled(self, integration_manager):
        integration_manager.debug = False
        integration_manager.console = MagicMock()

        integration_manager._log("Test message")

        integration_manager.console.log.assert_not_called()


class TestSyncAirtableAndAsana:
    def test_syncs_tasks_and_datasets(
        self, integration_manager, mock_asana, mock_airtable
    ):
        # Setup mock tasks
        task1 = {"gid": "task_1", "custom_fields": []}
        mock_asana.tasks = [task1]
        mock_asana.get_custom_field_value.return_value = "BP001"
        mock_asana.get_tasks.return_value = [task1]

        # Setup mock datasets
        dataset1 = {
            "id": "rec_1",
            "fields": {
                "Dataset ID": "BP001",
                "Dataset Name": "Test Dataset",
                "Dataset Value": 0.5,
            },
        }
        mock_airtable.tables["Datasets"].all.return_value = [dataset1]
        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"

        with patch.object(integration_manager, "update_airtable_statuses"):
            integration_manager.sync_airtable_and_asana()

        mock_asana.get_tasks.assert_called()
        mock_airtable.tables["Datasets"].all.assert_called()

    def test_creates_task_for_new_dataset(
        self, integration_manager, mock_asana, mock_airtable
    ):
        # No existing tasks
        mock_asana.tasks = []
        mock_asana.get_tasks.return_value = []

        # Dataset without matching task
        dataset = {
            "id": "rec_new",
            "fields": {
                "Dataset Name": "New Dataset",
                "Dataset ID": None,
            },
        }
        mock_airtable.tables["Datasets"].all.return_value = [dataset]
        mock_airtable.make_url.return_value = "https://airtable.com/rec_new"
        mock_asana.create_task.return_value = {"gid": "new_task"}
        mock_asana.fetch_task_with_custom_field.return_value = {
            "gid": "new_task",
            "custom_fields": [],
        }
        mock_asana.get_custom_field_value.return_value = "BP002"

        with patch.object(integration_manager, "update_airtable_statuses"):
            integration_manager.sync_airtable_and_asana()

        mock_asana.create_task.assert_called_once()
        assert mock_airtable.update_record.call_count >= 1


class TestUpdateAirtableStatuses:
    def test_updates_dataset_status_from_asana(
        self, integration_manager, mock_asana, mock_airtable
    ):
        task = {
            "gid": "task_1",
            "custom_fields": [],
        }
        mock_asana.get_tasks.return_value = [task]

        # Mock status retrieval
        def get_field_value(t, field_id):
            if field_id == config.ASANA_CUSTOM_FIELD_IDS["Status"]:
                return {"name": "Validated"}
            elif field_id == config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]:
                return "BP001"
            return None

        mock_asana.get_custom_field_value.side_effect = get_field_value

        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset ID": "BP001",
                "Status": "Awaiting Triage",
            },
        }
        mock_airtable.tables["Datasets"].all.return_value = [dataset]

        integration_manager.update_airtable_statuses()

        mock_airtable.update_record.assert_called_once()

    def test_skips_when_status_matches(
        self, integration_manager, mock_asana, mock_airtable
    ):
        task = {"gid": "task_1", "custom_fields": []}
        mock_asana.get_tasks.return_value = [task]

        def get_field_value(t, field_id):
            if field_id == config.ASANA_CUSTOM_FIELD_IDS["Status"]:
                return {"name": "Validated"}
            elif field_id == config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]:
                return "BP001"
            return None

        mock_asana.get_custom_field_value.side_effect = get_field_value

        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset ID": "BP001",
                "Status": "Validated",
            },
        }
        mock_airtable.tables["Datasets"].all.return_value = [dataset]

        integration_manager.update_airtable_statuses()

        mock_airtable.update_record.assert_not_called()

    def test_skips_dataset_without_bpipd(
        self, integration_manager, mock_asana, mock_airtable
    ):
        mock_asana.get_tasks.return_value = []

        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset Name": "Test",
                "Dataset ID": None,
            },
        }
        mock_airtable.tables["Datasets"].all.return_value = [dataset]

        integration_manager.update_airtable_statuses()

        mock_airtable.update_record.assert_not_called()

    def test_skips_task_without_status(
        self, integration_manager, mock_asana, mock_airtable
    ):
        task = {"gid": "task_1", "custom_fields": []}
        mock_asana.get_tasks.return_value = [task]

        def get_field_value(t, field_id):
            if field_id == config.ASANA_CUSTOM_FIELD_IDS["Status"]:
                return None  # No status
            elif field_id == config.ASANA_CUSTOM_FIELD_IDS["BPIPD"]:
                return "BP001"
            return None

        mock_asana.get_custom_field_value.side_effect = get_field_value

        dataset = {
            "id": "rec_1",
            "fields": {
                "Dataset ID": "BP001",
                "Status": "Validated",
            },
        }
        mock_airtable.tables["Datasets"].all.return_value = [dataset]

        integration_manager.update_airtable_statuses()

        mock_airtable.update_record.assert_not_called()


class TestUpdatedDatasetsScores:
    def test_updates_dataset_scores(self, integration_manager, mock_airtable):
        datasets = [
            {
                "id": "rec_1",
                "fields": {
                    "Dataset Name": "Dataset 1",
                    "Status": "Validated",
                    "Dataset Value": 0.5,
                },
            }
        ]
        mock_airtable.tables["Datasets"].all.return_value = datasets

        with (
            patch("bigger_picker.integration.utils.fix_dataset") as mock_fix,
            patch(
                "bigger_picker.integration.utils.compute_year_range"
            ) as mock_year,
            patch(
                "bigger_picker.integration.utils.compute_age_cache"
            ) as mock_cache,
            patch(
                "bigger_picker.integration.utils.compute_dataset_value"
            ) as mock_value,
        ):
            mock_fix.return_value = datasets[0]
            mock_year.return_value = (2015, 2020)
            mock_cache.return_value = {}
            mock_value.return_value = 0.75

            result = integration_manager.updated_datasets_scores()

        assert result is True
        mock_airtable.update_record.assert_called_once()

    def test_returns_false_when_no_updates(self, integration_manager, mock_airtable):
        datasets = [
            {
                "id": "rec_1",
                "fields": {
                    "Dataset Name": "Dataset 1",
                    "Status": "Validated",
                    "Dataset Value": 0.75,
                },
            }
        ]
        mock_airtable.tables["Datasets"].all.return_value = datasets

        with (
            patch("bigger_picker.integration.utils.fix_dataset") as mock_fix,
            patch(
                "bigger_picker.integration.utils.compute_year_range"
            ) as mock_year,
            patch(
                "bigger_picker.integration.utils.compute_age_cache"
            ) as mock_cache,
            patch(
                "bigger_picker.integration.utils.compute_dataset_value"
            ) as mock_value,
        ):
            mock_fix.return_value = datasets[0]
            mock_year.return_value = (2015, 2020)
            mock_cache.return_value = {}
            mock_value.return_value = 0.75

            result = integration_manager.updated_datasets_scores()

        assert result is False
        mock_airtable.update_record.assert_not_called()


class TestProcessArticle:
    def test_processes_article_successfully(
        self, integration_manager, mock_rayyan, mock_openai, mock_airtable, mock_asana
    ):
        article = {"id": 123}

        mock_rayyan.download_pdf.return_value = "/path/to/pdf"
        mock_rayyan.extract_article_metadata.return_value = {
            "Rayyan ID": 123,
            "Article Title": "Test",
            "Authors": "Smith",
            "Journal": "Journal",
            "DOI": "",
            "Year": 2020,
            "Search": [],
        }

        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 100,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        mock_openai.extract_article_info.return_value = llm_extraction

        mock_airtable.create_record.return_value = {
            "id": "rec_1",
            "fields": {"Dataset Name": "Smith 2020"},
        }
        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"
        mock_asana.create_task.return_value = {"gid": "task_1"}
        mock_asana.fetch_task_with_custom_field.return_value = {
            "gid": "task_1",
            "custom_fields": [],
        }
        mock_asana.get_custom_field_value.return_value = "BP001"

        integration_manager.process_article(article)

        mock_rayyan.download_pdf.assert_called_once_with(article)
        mock_openai.extract_article_info.assert_called_once()
        mock_rayyan.update_article_labels.assert_called_once()

    def test_skips_when_no_pdf(self, integration_manager, mock_rayyan, mock_openai):
        article = {"id": 123}
        mock_rayyan.download_pdf.return_value = None

        integration_manager.process_article(article)

        mock_openai.extract_article_info.assert_not_called()

    def test_skips_when_extraction_fails(
        self, integration_manager, mock_rayyan, mock_openai
    ):
        article = {"id": 123}
        mock_rayyan.download_pdf.return_value = "/path/to/pdf"
        mock_rayyan.extract_article_metadata.return_value = {}
        mock_openai.extract_article_info.return_value = None

        integration_manager.process_article(article)

        mock_rayyan.update_article_labels.assert_not_called()


class TestUploadExtractionWithNestedObjects:
    def test_creates_populations_records(self, integration_manager, mock_airtable):
        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 500,
                "Dataset Name": "Smith 2020",
                "populations": [
                    {
                        "Age: Lower Range": 18.0,
                        "Age: Upper Range": 25.0,
                        "Age: Mean": 21.5,
                        "Age: Standard Deviation": 2.0,
                        "Sample Size: Total N": 250,
                        "Sample Size: N Girls": 125,
                        "Sample Size: % Girls": 50.0,
                    }
                ],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        article_metadata = {
            "Rayyan ID": 123,
            "Article Title": "Test",
            "Authors": "Smith",
            "Journal": "Journal",
            "DOI": "",
            "Year": 2020,
            "Search": [],
        }

        mock_airtable.create_record.return_value = {"id": "rec_1"}

        integration_manager.upload_extraction_to_airtable(
            llm_extraction, article_metadata
        )

        # Should create Article + 1 Population + Dataset
        assert mock_airtable.create_record.call_count >= 3

    def test_creates_screen_time_measures(self, integration_manager, mock_airtable):
        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 500,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [
                    {
                        "Screen Time Measure: Type": "Survey",
                        "Screen Time Measure: Name": "TV Watching Survey",
                        "Types of Screen Time Measured": ["Television"],
                        "Locations of Screen Time Measured": ["Home"],
                    }
                ],
                "outcomes": [],
            }
        )
        article_metadata = {
            "Rayyan ID": 123,
            "Article Title": "Test",
            "Authors": "Smith",
            "Journal": "Journal",
            "DOI": "",
            "Year": 2020,
            "Search": [],
        }

        mock_airtable.create_record.return_value = {"id": "rec_1"}

        integration_manager.upload_extraction_to_airtable(
            llm_extraction, article_metadata
        )

        # Verify screen time measure was created
        assert mock_airtable.create_record.call_count >= 3

    def test_creates_outcomes(self, integration_manager, mock_airtable):
        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 500,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [
                    {
                        "Outcome Group": "Mental Health",
                        "Outcome": "depression",
                        "Outcome Measure": "PHQ-9",
                    }
                ],
            }
        )
        article_metadata = {
            "Rayyan ID": 123,
            "Article Title": "Test",
            "Authors": "Smith",
            "Journal": "Journal",
            "DOI": "",
            "Year": 2020,
            "Search": [],
        }

        mock_airtable.create_record.return_value = {"id": "rec_1"}

        integration_manager.upload_extraction_to_airtable(
            llm_extraction, article_metadata
        )

        # Verify outcome was created
        assert mock_airtable.create_record.call_count >= 3

    def test_generates_dataset_name_from_metadata(
        self, integration_manager, mock_airtable
    ):
        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 500,
                "Dataset Name": None,
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        article_metadata = {
            "Rayyan ID": 123,
            "Article Title": "Test",
            "Authors": "Smith, Jones",
            "Journal": "Journal",
            "DOI": "",
            "Year": 2020,
            "Search": [],
        }

        mock_airtable.create_record.return_value = {"id": "rec_1"}

        integration_manager.upload_extraction_to_airtable(
            llm_extraction, article_metadata
        )

        # Check that dataset was created with generated name
        calls = mock_airtable.create_record.call_args_list
        dataset_call = [c for c in calls if c[0][0] == "Datasets"][0]
        assert "Smith, 2020" in dataset_call[0][1]["Dataset Name"]


class TestCreateExtractionBatch:
    def test_prepares_extraction_batch(
        self, integration_manager, mock_openai, mock_rayyan, mock_tracker
    ):
        articles = [{"id": 1}, {"id": 2}]

        mock_rayyan.download_pdf.return_value = "/path/to/pdf"
        mock_file = MagicMock()
        mock_file.id = "file_123"
        mock_openai.upload_file.return_value = mock_file
        mock_openai.prepare_extraction_body.return_value = {
            "model": "test",
            "messages": [],
        }

        with patch.object(integration_manager, "_submit_batch") as mock_submit:
            integration_manager.create_extraction_batch(articles)

        assert mock_openai.upload_file.call_count == 2
        mock_submit.assert_called_once()

    def test_skips_articles_without_pdf(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        articles = [{"id": 1}]
        mock_rayyan.download_pdf.return_value = None

        with patch.object(integration_manager, "_submit_batch") as mock_submit:
            integration_manager.create_extraction_batch(articles)

        mock_openai.upload_file.assert_not_called()
        mock_submit.assert_not_called()

    def test_handles_upload_errors(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        articles = [{"id": 1}, {"id": 2}]

        mock_rayyan.download_pdf.return_value = "/path/to/pdf"
        mock_openai.upload_file.side_effect = [
            Exception("Upload failed"),
            MagicMock(id="file_2"),
        ]
        mock_openai.prepare_extraction_body.return_value = {}

        with patch.object(integration_manager, "_submit_batch"):
            integration_manager.create_extraction_batch(articles)

        # Should have created only 1 request (second article)
        assert mock_openai.prepare_extraction_body.call_count == 1


class TestProcessAbstractResults:
    def test_processes_successful_results(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        results = [
            {
                "custom_id": "abstract-123",
                "response": {
                    "status_code": 200,
                    "body": {
                        "output": [
                            {
                                "content": [
                                    {"text": '{"vote": "include", "rationale": "Good"}'}
                                ]
                            }
                        ]
                    },
                },
            }
        ]

        decision = ScreeningDecision(
            vote="include",
            matched_inclusion=None,
            failed_inclusion=None,
            triggered_exclusion=None,
            exclusion_reasons=None,
            rationale="Good",
        )
        mock_openai.parse_screening_decision.return_value = decision

        integration_manager._process_abstract_results(results)

        mock_rayyan.update_article_labels.assert_called_once()

    def test_handles_error_results(self, integration_manager, mock_openai, mock_rayyan):
        results = [
            {
                "custom_id": "abstract-123",
                "response": {
                    "status_code": 500,
                    "body": {"error": "Internal error"},
                },
            }
        ]

        integration_manager._process_abstract_results(results)

        # Should update labels to remove batch_pending
        mock_rayyan.update_article_labels.assert_called_once()

    def test_handles_parsing_errors(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        results = [
            {
                "custom_id": "abstract-123",
                "response": {
                    "status_code": 200,
                    "body": {
                        "output": [
                            {
                                "content": [
                                    {
                                        "text": "invalid json"
                                    }
                                ]
                            }
                        ]
                    },
                },
            }
        ]

        mock_openai.parse_screening_decision.side_effect = Exception("Parse error")

        # Should not raise, just log
        integration_manager._process_abstract_results(results)


class TestProcessFulltextResults:
    def test_processes_successful_fulltext_results(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        results = [
            {
                "custom_id": "fulltext-456",
                "response": {
                    "status_code": 200,
                    "body": {
                        "output": [
                            {
                                "content": [
                                    {
                                        "text": (
                                            '{"vote": "exclude", '
                                            '"triggered_exclusion": [1], '
                                            '"rationale": "Wrong"}'
                                        )
                                    }
                                ]
                            }
                        ]
                    },
                },
            }
        ]

        decision = ScreeningDecision(
            vote="exclude",
            matched_inclusion=None,
            failed_inclusion=None,
            triggered_exclusion=[1],
            exclusion_reasons=None,
            rationale="Wrong",
        )
        mock_openai.parse_screening_decision.return_value = decision

        integration_manager._process_fulltext_results(results)

        mock_rayyan.update_article_labels.assert_called_once()


class TestProcessExtractionResults:
    def test_processes_extraction_results(
        self, integration_manager, mock_openai, mock_rayyan, mock_airtable, mock_asana
    ):
        results = [
            {
                "custom_id": "extraction-789",
                "response": {
                    "status_code": 200,
                    "body": {
                        "output": [
                            {
                                "content": [
                                    {
                                        "text": '{"Corresponding Author": "Smith"}'
                                    }
                                ]
                            }
                        ]
                    },
                },
            }
        ]

        llm_extraction = ArticleLLMExtract.model_validate(
            {
                "Corresponding Author": "Dr. Smith",
                "Corresponding Author Email": "smith@uni.edu",
                "Year of Last Data Point": 2020,
                "Study Design": "Cross-sectional",
                "Countries of Data": ["USA"],
                "Total Sample Size": 100,
                "Dataset Name": "Smith 2020",
                "populations": [],
                "screen_time_measures": [],
                "outcomes": [],
            }
        )
        mock_openai.parse_extraction_result.return_value = llm_extraction

        article = {"id": 789}
        mock_rayyan.get_article_by_id.return_value = article
        mock_rayyan.extract_article_metadata.return_value = {
            "Rayyan ID": 789,
            "Article Title": "Test",
            "Authors": "Smith",
            "Journal": "Journal",
            "DOI": "",
            "Year": 2020,
            "Search": [],
        }
        mock_rayyan.download_pdf.return_value = "/path/to/pdf"

        mock_airtable.create_record.return_value = {
            "id": "rec_1",
            "fields": {"Dataset Name": "Test"},
        }
        mock_airtable.make_url.return_value = "https://airtable.com/rec_1"
        mock_asana.create_task.return_value = {"gid": "task_1"}
        mock_asana.fetch_task_with_custom_field.return_value = {
            "gid": "task_1",
            "custom_fields": [],
        }
        mock_asana.get_custom_field_value.return_value = "BP001"

        integration_manager._process_extraction_results(results)

        mock_rayyan.update_article_labels.assert_called_once()

    def test_handles_extraction_errors(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        results = [
            {
                "custom_id": "extraction-789",
                "response": {
                    "status_code": 500,
                    "body": {"error": "Failed"},
                },
            }
        ]

        integration_manager._process_extraction_results(results)

        mock_rayyan.update_article_labels.assert_called_once()


class TestActionScreeningDecisionEdgeCases:
    def test_exclude_with_failed_inclusion(self, integration_manager, mock_rayyan):
        decision = {
            "vote": "exclude",
            "failed_inclusion": [2],
            "rationale": "Failed inclusion criteria",
        }

        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=False
        )

        mock_rayyan.create_article_note.assert_called_once()
        mock_rayyan.update_article_labels.assert_called_once()

    def test_long_rationale_truncated(self, integration_manager, mock_rayyan):
        decision = {
            "vote": "exclude",
            "triggered_exclusion": [1],
            "rationale": "x" * 1500,  # Very long rationale
        }

        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=False
        )

        # Should truncate to ~1000 chars
        call_args = mock_rayyan.create_article_note.call_args
        note_text = call_args[0][1]
        assert len(note_text) <= 1020
        assert "..." in note_text

    def test_note_creation_failure(self, integration_manager, mock_rayyan):
        decision = {
            "vote": "exclude",
            "triggered_exclusion": [1],
            "rationale": "Excluded",
        }

        mock_rayyan.create_article_note.side_effect = Exception("Note failed")

        # Should not raise
        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=False
        )

        mock_rayyan.update_article_labels.assert_called_once()

    def test_include_fulltext_adds_unextracted(self, integration_manager, mock_rayyan):
        decision = {
            "vote": "include",
            "rationale": "Good",
        }

        integration_manager._action_screening_decision(
            decision, article_id=123, is_abstract=False
        )

        call_args = mock_rayyan.update_article_labels.call_args
        plan = call_args[0][1]
        assert config.RAYYAN_LABELS["included"] in plan
        assert config.RAYYAN_LABELS["unextracted"] in plan


class TestScreenAbstractEdgeCases:
    def test_skips_empty_abstract_content(self, integration_manager, mock_openai):
        article = {"id": 123, "abstracts": [{"content": ""}]}

        integration_manager.screen_abstract(article)

        mock_openai.screen_record_abstract.assert_not_called()

    def test_handles_llm_failure(self, integration_manager, mock_openai, mock_rayyan):
        article = {"id": 123, "abstracts": [{"content": "Test abstract"}]}
        mock_openai.screen_record_abstract.return_value = None

        integration_manager.screen_abstract(article)

        mock_rayyan.update_article_labels.assert_not_called()


class TestScreenFulltextEdgeCases:
    def test_handles_llm_failure_fulltext(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        article = {"id": 123}
        mock_rayyan.download_pdf.return_value = "/path/to/pdf"
        mock_openai.screen_record_fulltext.return_value = None

        integration_manager.screen_fulltext(article)

        mock_rayyan.update_article_labels.assert_not_called()


class TestCreateAbstractBatchEdgeCases:
    def test_marks_missing_abstracts(
        self, integration_manager, mock_openai, mock_rayyan
    ):
        articles = [
            {"id": 1, "abstracts": []},
            {"id": 2, "abstracts": [{"content": ""}]},
        ]

        with patch.object(integration_manager, "_submit_batch") as mock_submit:
            integration_manager.create_abstract_screening_batch(articles)

        # Should update labels for both articles with missing abstract
        assert mock_rayyan.update_article_labels.call_count == 2
        mock_submit.assert_not_called()

    def test_submits_batch_when_no_requests(self, integration_manager):
        articles = []

        with patch.object(integration_manager, "_submit_batch") as mock_submit:
            integration_manager.create_abstract_screening_batch(articles)

        mock_submit.assert_not_called()
