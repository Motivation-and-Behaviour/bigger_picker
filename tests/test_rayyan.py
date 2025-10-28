import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

import bigger_picker.config as config
from bigger_picker.rayyan import RayyanManager


# Sample config values
def test_init_uses_default_path_and_labels(monkeypatch, tmp_path):
    # Create a fake credentials file path in env
    fake_path = tmp_path / "creds.json"
    fake_path.write_text(json.dumps({"refresh_token": "old"}))
    monkeypatch.setenv("RAYYAN_JSON_PATH", str(fake_path))
    # Patch Rayyan and Review to dummy constructors
    DummyRayyan = MagicMock()
    DummyReview = MagicMock()
    monkeypatch.setattr("bigger_picker.rayyan.Rayyan", lambda p: DummyRayyan)
    monkeypatch.setattr("bigger_picker.rayyan.Review", lambda inst: DummyReview)
    # Instantiate without args
    mgr = RayyanManager()
    # Should load creds path from env
    assert mgr._rayyan_creds_path == str(fake_path)
    # Instance attributes
    assert mgr.rayyan_instance is DummyRayyan
    assert mgr.review is DummyReview
    assert mgr.review_id == config.RAYYAN_REVIEW_ID
    assert mgr.unextracted_label == config.RAYYAN_LABELS["unextracted"]
    assert mgr.extracted_label == config.RAYYAN_LABELS["extracted"]


def test_extract_article_metadata_and_helpers():
    art = {
        "id": 123,
        "title": "Test Article",
        "authors": ["Alice"],
        "citation": "Journal Name - Some other info",
        "doi": "10.1000/xyz",
        "year": "2022",
        "customizations": {"labels": {"SDQ": 1}},
    }
    meta = RayyanManager.extract_article_metadata(art)
    assert meta == {
        "Rayyan ID": 123,
        "Article Title": "Test Article",
        "Authors": "Alice",
        "Journal": "Journal Name",
        "DOI": "10.1000/xyz",
        "Year": "2022",
        "Search": ["SDQ"],
    }

    # Test join_names multiline
    assert RayyanManager._join_names([]) == ""
    assert RayyanManager._join_names(["A"]) == "A"
    assert RayyanManager._join_names(["A", "B"]) == "A and B"
    assert RayyanManager._join_names(["A", "B", "C"]) == "A, B and C"
    # Test extract_journal edge
    assert RayyanManager._extract_journal("") == ""
    assert RayyanManager._extract_journal("OnlyJournal") == "OnlyJournal"


def test_download_pdf_success_and_no_url(monkeypatch, tmp_path):
    # Create dummy article dict with two fulltexts, one deleted, one valid
    article = {
        "id": 99,
        "fulltexts": [
            {"marked_as_deleted": True, "id": "bad_id"},
            {"marked_as_deleted": False, "id": "good_id"},
        ],
    }

    # Mock the RayyanManager instance and its dependencies
    mock_rayyan_instance = MagicMock()
    mock_rayyan_instance.request.request_handler.return_value = {
        "url": "http://example.com/pdf99"
    }

    # Mock requests.get
    class DummyResponse:
        def __init__(self, content, ok=True):
            self.content = content
            self.ok = ok
            self.status_code = 200

        def raise_for_status(self):
            if not self.ok:
                raise requests.HTTPError()

    dummy = DummyResponse(b"binarypdf")
    monkeypatch.setattr("bigger_picker.rayyan.requests.get", lambda url: dummy)

    # Mock tempfile.mkdtemp to use tmp_path
    monkeypatch.setattr("bigger_picker.rayyan.tempfile.mkdtemp", lambda: str(tmp_path))

    # Create RayyanManager instance with mocked rayyan_instance
    fake_path = tmp_path / "creds.json"
    fake_path.write_text(
        json.dumps({"refresh_token": "old", "access_token": "faketoken"})
    )
    monkeypatch.setenv("RAYYAN_JSON_PATH", str(fake_path))
    manager = RayyanManager()
    manager.rayyan_instance = mock_rayyan_instance

    path = manager.download_pdf(article)

    # Verify API was called with correct fulltext ID
    mock_rayyan_instance.request.request_handler.assert_called_once_with(
        method="GET", path="/api/v1/fulltexts/good_id"
    )

    # File exists and matches id
    assert Path(path).exists()
    assert Path(path).name == "99.pdf"
    assert Path(path).read_bytes() == b"binarypdf"

    # Now test no valid fulltext ID
    bad_article = {"id": 100, "fulltexts": []}
    with pytest.raises(ValueError, match="No fulltext found in the article."):
        manager.download_pdf(bad_article)

    # Test no URL in fulltext details
    mock_rayyan_instance.request.request_handler.return_value = {}
    article_no_url = {
        "id": 101,
        "fulltexts": [{"marked_as_deleted": False, "id": "no_url_id"}],
    }
    with pytest.raises(ValueError, match="No URL found for the fulltext."):
        manager.download_pdf(article_no_url)
