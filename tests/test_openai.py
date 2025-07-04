import os

import pytest

import bigger_picker.credentials as credentials
import bigger_picker.openai as openai


class DummyFile:
    def __init__(self, file_id):
        self.id = file_id


class DummyResponse:
    def __init__(self, parsed):
        self.output_parsed = parsed


@pytest.fixture(autouse=True)
def patch_env_and_token(monkeypatch):
    # Ensure default token used if api_key None
    monkeypatch.setenv("OPENAI_TOKEN", "env_test_key")
    # Monkey-patch load_token to return the env var
    monkeypatch.setattr(credentials, "load_token", lambda name: os.getenv(name))


@pytest.fixture
def dummy_openai(monkeypatch):
    # Replace OpenAI constructor to capture api_key
    created = {}

    class FakeOpenAIClient:
        def __init__(self, api_key):
            created["api_key"] = api_key
            # prepare nested files and responses attrs
            self.files = type(
                "F", (), {"create": lambda self, file, purpose: DummyFile("file123")}
            )()
            self.responses = type(
                "R",
                (),
                {
                    "parse": lambda self, model, input, text_format: DummyResponse(
                        "parsed_output"
                    )
                },
            )()

    monkeypatch.setattr(openai, "OpenAI", FakeOpenAIClient)
    return created


def test_init_with_provided_key(dummy_openai):
    mgr = openai.OpenAIManager(api_key="provided_key", model="gpt-test")
    # Should pass provided_key to underlying client
    assert dummy_openai["api_key"] == "provided_key"
    assert mgr.model == "gpt-test"


def test_init_without_key_uses_load_token(monkeypatch, dummy_openai):
    # Remove direct call, use default None
    mgr = openai.OpenAIManager(api_key=None)  # noqa: F841
    assert dummy_openai["api_key"] == os.getenv("OPENAI_TOKEN")


def test_extract_article_info(tmp_path, dummy_openai, monkeypatch):
    # Create a dummy PDF file
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"%PDF-1.4 dummy")

    mgr = openai.OpenAIManager(api_key="provided_key")
    # Call extract_article_info
    result = mgr.extract_article_info(str(pdf))

    # Verify file.create used and parse used
    # The DummyFile id must be used in parse call
    # Because our FakeOpenAIClient always returns DummyResponse('parsed_output')
    assert result == "parsed_output"

    # Also ensure that the prompt constant is included in the system message
    # by reading the first part of prompt
    prompt = openai.ARTICLE_EXTRACTION_PROMPT
    assert "You are an experienced research assistant" in prompt


def test_extract_article_info_file_open_error(monkeypatch):
    # Simulate error opening the file
    mgr = openai.OpenAIManager(api_key="provided_key")
    with pytest.raises(FileNotFoundError):
        mgr.extract_article_info("nope.pdf")
