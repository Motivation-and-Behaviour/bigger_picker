import json
import os
import tempfile

import requests
from rayyan import Rayyan
from rayyan.notes import Notes
from rayyan.review import Review

import bigger_picker.config as config
from bigger_picker.credentials import load_rayyan_credentials


class RayyanManager:
    def __init__(
        self,
        rayyan_creds_path: str | None = None,
        review_id: int = config.RAYYAN_REVIEW_ID,
        unextracted_label: str = config.RAYYAN_LABELS["unextracted"],
        extracted_label: str = config.RAYYAN_LABELS["extracted"],
    ):
        if rayyan_creds_path is None:
            rayyan_creds_path = load_rayyan_credentials()

        self._rayyan_creds_path = rayyan_creds_path
        self.rayyan_instance = Rayyan(rayyan_creds_path)
        self.review = Review(self.rayyan_instance)
        self.review_id = review_id
        self.notes_instance = Notes(self.rayyan_instance)
        self.unextracted_label = unextracted_label
        self.extracted_label = extracted_label

    def get_unextracted_articles(self) -> list[dict]:
        results_params = {"extra[user_labels][]": self.unextracted_label}

        included_results = self._retry_on_auth_error(
            lambda: self.review.results(self.review_id, results_params)  # type: ignore
        )

        return included_results["data"]  # type: ignore

    def get_unscreened_fulltext(self) -> list[dict]:
        results_params = {"extra[mode]": "included"}
        labels_to_check = (
            list(config.RAYYAN_LABELS.values()) + config.RAYYAN_EXCLUSION_LABELS
        )

        results = self._retry_on_auth_error(
            lambda: self.review.results(self.review_id, results_params)  # type: ignore
        )

        unscreened = []
        priority = []

        for article in results["data"]:
            fulltext_id = self._get_fulltext_id(article)  # type: ignore
            if fulltext_id is None:
                continue

            article_labels = article.get("customizations", {}).get("labels", {})  # type: ignore
            if any(label in labels_to_check for label in article_labels):
                continue

            if any(
                label in config.ASANA_SEARCHES_ENUM_VALUES for label in article_labels
            ):
                priority.append(article)
            else:
                unscreened.append(article)

        unscreened = priority + unscreened

        return unscreened

    def update_article_labels(self, article_id: int, plan: dict) -> None:
        self._retry_on_auth_error(
            lambda: self.review.customize(self.review_id, article_id, plan)
        )

    def create_article_note(self, article_id: int, note_content: str) -> None:
        self._retry_on_auth_error(
            lambda: self.notes_instance.create_note(
                self.review_id, article_id, note_content
            )
        )

    def download_pdf(self, article: dict) -> str:
        fulltext_id = self._get_fulltext_id(article)

        if fulltext_id is None:
            raise ValueError("No fulltext found in the article.")

        fulltext_details = self.rayyan_instance.request.request_handler(
            method="GET", path=f"/api/v1/fulltexts/{fulltext_id}"
        )

        fulltext_url = fulltext_details.get("url", None)

        if fulltext_url is None:
            raise ValueError("No URL found for the fulltext.")

        temp_dir = tempfile.mkdtemp()

        filename = f"{article['id']}.pdf"

        file_path = os.path.join(temp_dir, filename)
        response = requests.get(str(fulltext_url))
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    def _retry_on_auth_error(self, operation):
        try:
            return operation()
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                # If we get a 401 error, refresh the tokens and retry
                self._refresh_tokens()
                return operation()
            else:
                raise e

    def _refresh_tokens(self, update_local: bool = True):
        with open(self._rayyan_creds_path) as f:
            api_tokens = json.load(f)

        url = "https://rayyan.ai/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": api_tokens["refresh_token"],
            "client_id": "rayyan.ai",
        }

        response = requests.post(url, data=payload)
        if not response.ok:
            raise Exception(f"Token refresh failed: {response.text}")

        api_tokens_fresh = response.json()

        if update_local:
            with open(self._rayyan_creds_path, "w") as f:
                json.dump(api_tokens_fresh, f, indent=2)
            self.rayyan_instance = Rayyan(self._rayyan_creds_path)
        else:
            temp_creds_path = tempfile.NamedTemporaryFile(
                mode="w+", delete=False, suffix=".json"
            )
            with open(temp_creds_path.name, "w") as f:
                json.dump(api_tokens_fresh, f, indent=2)
            self.rayyan_instance = Rayyan(temp_creds_path.name)

        self.review = Review(self.rayyan_instance)

    @staticmethod
    def extract_article_metadata(rayyan_article: dict) -> dict:
        searches = [
            label
            for label in rayyan_article.get("customizations", {})
            .get("labels", [])
            .keys()
            if label in config.ASANA_SEARCHES_ENUM_VALUES.keys()
        ]
        extracted_info = {
            "Rayyan ID": rayyan_article["id"],
            "Article Title": rayyan_article.get("title", ""),
            "Authors": RayyanManager._join_names(rayyan_article.get("authors", "")),
            "Journal": RayyanManager._extract_journal(
                rayyan_article.get("citation", "")
            ),
            "DOI": rayyan_article.get("doi", ""),
            "Year": rayyan_article.get("year", ""),
            "Search": searches,
        }

        return extracted_info

    @staticmethod
    def _join_names(names: list[str]) -> str:
        if not names:
            return ""
        if len(names) == 1:
            return names[0]
        return ", ".join(names[:-1]) + " and " + names[-1]

    @staticmethod
    def _extract_journal(citation_str: str) -> str:
        parts = citation_str.split("-")
        return parts[0].strip() if parts else ""

    @staticmethod
    def _get_fulltext_id(article: dict) -> str | None:
        fulltext_id = None
        for fulltext in article["fulltexts"]:
            if fulltext["marked_as_deleted"]:
                # Skip deleted files
                continue
            fulltext_id = fulltext.get("id", None)
            if fulltext_id:
                break

        return fulltext_id
