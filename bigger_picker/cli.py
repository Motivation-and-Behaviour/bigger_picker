import os

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress

from bigger_picker.airtable import AirtableManager
from bigger_picker.asana import AsanaManager
from bigger_picker.openai import OpenAIManager
from bigger_picker.rayyan import RayyanManager
from bigger_picker.sync import IntegrationManager

app = typer.Typer()


@app.command()
def process(
    dotenv_path: str = typer.Option(None, help="Path to .env file with credentials"),
    airtable_api_key: str = typer.Option(None, help="Airtable API key"),
    asana_token: str = typer.Option(None, help="Asana API token"),
    openai_api_key: str = typer.Option(None, help="OpenAI API key"),
    openai_model: str = typer.Option("gpt-4.1", help="OpenAI model to use"),
    rayyan_creds_path: str = typer.Option(
        None, help="Path to Rayyan credentials JSON file"
    ),
):
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(BASE_DIR, ".env"))

    console = Console()

    airtable = AirtableManager(airtable_api_key)
    asana = AsanaManager(asana_token)
    openai = OpenAIManager(openai_api_key, openai_model)
    rayyan = RayyanManager(rayyan_creds_path)
    integration = IntegrationManager(
        asana_manager=asana,
        airtable_manager=airtable,
        openai_manager=openai,
        rayyan_manager=rayyan,
    )

    with console.status("Getting unextracted articles..."):
        articles = integration.rayyan.get_unextracted_articles()
        console.log(f"Found {len(articles)} unextracted articles.")

    with Progress(console=console) as progress:
        task = progress.add_task("Extracting articles...", total=len(articles))
        for article in articles:
            integration.process_article(article)
            progress.advance(task, advance=1)
    console.log("Extraction complete.")

    with console.status("Updating AirTable statuses"):
        integration.sync()


@app.command()
def sync(
    dotenv_path: str = typer.Option(None, help="Path to .env file with credentials"),
    airtable_api_key: str = typer.Option(None, help="Airtable API key"),
    asana_token: str = typer.Option(None, help="Asana API token"),
    openai_api_key: str = typer.Option(None, help="OpenAI API key"),
    openai_model: str = typer.Option("gpt-4.1", help="OpenAI model to use"),
    rayyan_creds_path: str = typer.Option(
        None, help="Path to Rayyan credentials JSON file"
    ),
):
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(BASE_DIR, ".env"))

    console = Console()

    airtable = AirtableManager(airtable_api_key)
    asana = AsanaManager(asana_token)
    openai = OpenAIManager(openai_api_key, openai_model)
    rayyan = RayyanManager(rayyan_creds_path)
    integration = IntegrationManager(
        asana_manager=asana,
        airtable_manager=airtable,
        openai_manager=openai,
        rayyan_manager=rayyan,
    )

    with console.status("Updating AirTable statuses"):
        integration.sync()


if __name__ == "__main__":
    app()
