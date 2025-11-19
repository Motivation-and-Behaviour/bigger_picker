from openai import OpenAI
from openai.types import FileObject
from openai.types.responses.response_input_param import ResponseInputItemParam

from bigger_picker.config import (
    ABSTRACT_SCREENING_INSTRUCTIONS,
    ARTICLE_EXTRACTION_PROMPT,
    EXCLUSION_CRITERIA,
    FULLTEXT_SCREENING_INSTRUCTIONS,
    INCLUSION_CRITERIA,
    INCLUSION_HEADER,
    STUDY_OBJECTIVES,
)
from bigger_picker.credentials import load_token
from bigger_picker.datamodels import ArticleLLMExtract, ScreeningDecision


class OpenAIManager:
    def __init__(self, api_key: str | None = None, model: str = "gpt-5.1"):
        if api_key is None:
            api_key = load_token("OPENAI_TOKEN")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def extract_article_info(self, pdf_path: str):
        file = self._upload_file(pdf_path)

        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": ARTICLE_EXTRACTION_PROMPT},
                {
                    "role": "user",
                    "content": [{"type": "input_file", "file_id": file.id}],
                },
            ],
            text_format=ArticleLLMExtract,
        )

        return response.output_parsed

    def screen_record_abstract(self, abstract: str):
        inputs = self._build_abstract_prompt(abstract)

        response = self.client.responses.parse(
            model=self.model,
            input=inputs,
            text_format=ScreeningDecision,
        )
        return response.output_parsed

    def screen_record_fulltext(self, pdf_path: str):
        file = self._upload_file(pdf_path)

        inputs = self._build_fulltext_prompt(file.id)

        response = self.client.responses.parse(
            model=self.model,
            input=inputs,
            text_format=ScreeningDecision,
        )

        return response.output_parsed

    def _build_abstract_prompt(self, abstract: str) -> list[ResponseInputItemParam]:
        prompt = (
            STUDY_OBJECTIVES
            + "\n"
            + INCLUSION_HEADER
            + "\n"
            + "Inclusion criteria (all must be met):\n"
            + self._number_criteria(INCLUSION_CRITERIA)
            + "\n"
            + "Exclusion criteria (any triggers exclusion):\n"
            + self._number_criteria(EXCLUSION_CRITERIA)
            + "\n"
            + ABSTRACT_SCREENING_INSTRUCTIONS
        )
        return [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Abstract:\n{abstract}"},
        ]

    def _build_fulltext_prompt(self, file_id: str) -> list[ResponseInputItemParam]:
        prompt = (
            STUDY_OBJECTIVES
            + "\n"
            + INCLUSION_HEADER
            + "\n"
            + "Inclusion criteria (all must be met):\n"
            + self._number_criteria(INCLUSION_CRITERIA)
            + "\n"
            + "Exclusion criteria (any triggers exclusion):\n"
            + self._number_criteria(EXCLUSION_CRITERIA)
            + "\n"
            + FULLTEXT_SCREENING_INSTRUCTIONS
        )
        return [
            {"role": "system", "content": prompt},
            {"role": "user", "content": [{"type": "input_file", "file_id": file_id}]},
            {"role": "system", "content": prompt},
        ]

    @staticmethod
    def _number_criteria(criteria: list[str]) -> str:
        return "\n".join(f"{i + 1}. {c}" for i, c in enumerate(criteria))

    def _upload_file(self, pdf_path: str) -> FileObject:
        with open(pdf_path, "rb") as f:
            return self.client.files.create(file=f, purpose="user_data")
