import os
import tempfile

import requests
from rayyan import Rayyan
from rayyan.review import Review

import bigger_picker.config as config
from bigger_picker.credentials import load_rayyan_credentials


class RayyanManager:
    def __init__(
        self,
        rayyan_creds_path: str | None = None,
        review_id: int = config.RAYYAN_REVIEW_ID,
        unextracted_label: str = config.RAYYAN_LABELS["unextracted"],
    ):
        if rayyan_creds_path is None:
            rayyan_creds_path = load_rayyan_credentials()

        self.rayyan_instance = Rayyan(rayyan_creds_path)
        self.review = Review(self.rayyan_instance)
        self.review_id = review_id
        self.unextracted_label = unextracted_label

    def get_unextracted_articles(
        self,
    ) -> list[dict]:
        results_params = {"extra[user_labels][]": self.unextracted_label}

        included_results = self.review.results(self.review_id, results_params)  # type: ignore

        # TODO: If 401 error, I think we are meant to call 'user_info' to refresh token.
        return included_results["data"]  # type: ignore

    def update_article_labels(
        self,
        article_id: int,
    ) -> None:
        plan = {
            config.RAYYAN_LABELS["unextracted"]: -1,
            config.RAYYAN_LABELS["extracted"]: 1,
        }
        self.review.customize(self.review_id, article_id, plan)

    @staticmethod
    def download_pdf(article: dict) -> str:
        url = None
        for fulltext in article["fulltexts"]:
            if fulltext["marked_as_deleted"]:
                # Skip deleted files
                continue
            url = fulltext.get("url", None)
            if url:
                break
        if url is None:
            raise ValueError("No valid PDF URL found in the article.")

        temp_dir = tempfile.mkdtemp()

        filename = f"{article['id']}.pdf"

        file_path = os.path.join(temp_dir, filename)
        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path
