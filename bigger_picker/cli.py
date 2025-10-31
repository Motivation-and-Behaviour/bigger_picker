import os

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

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
    max_articles: int = typer.Option(
        None, help="Maximum number of articles to process"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging to console"
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
        console=console,
        debug=debug,
    )

    with console.status("Getting unextracted articles..."):
        articles = integration.rayyan.get_unextracted_articles()
        if max_articles is not None:
            articles = articles[:max_articles]
        console.log(f"Found {len(articles)} unextracted articles.")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),  #
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Extracting articles...", total=len(articles))
        for article in articles:
            integration.process_article(article)
            progress.advance(task, advance=1)
    console.log("Extraction complete.")

    with console.status("Updating Airtable statuses"):
        console.log("Starting sync...")
        integration.sync()
        console.log("Sync complete")

    with console.status("Marking duplicates"):
        console.log("Identifying duplicates...")
        integration.mark_duplicates()
        console.log("Duplicates marked.")


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
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging to console"
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
        console=console,
        debug=debug,
    )

    with console.status("Updating Airtable statuses"):
        console.log("Starting sync...")
        integration.sync()
        console.log("Sync complete")


@app.command()
def screenft(
    dotenv_path: str = typer.Option(None, help="Path to .env file with credentials"),
    airtable_api_key: str = typer.Option(None, help="Airtable API key"),
    asana_token: str = typer.Option(None, help="Asana API token"),
    openai_api_key: str = typer.Option(None, help="OpenAI API key"),
    openai_model: str = typer.Option("gpt-5", help="OpenAI model to use"),
    rayyan_creds_path: str = typer.Option(
        None, help="Path to Rayyan credentials JSON file"
    ),
    max_articles: int = typer.Option(
        None, help="Maximum number of articles to process"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging to console"
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
        console=console,
        debug=debug,
    )

    with console.status("Getting unscreened fulltexts..."):
        articles = integration.rayyan.get_unscreened_fulltext()
        if max_articles is not None:
            articles = articles[:max_articles]
        console.log(f"Found {len(articles)} unscreened fulltexts.")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),  #
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Screening fulltexts...", total=len(articles))
        for article in articles:
            integration.screen_fulltext(article)
            progress.advance(task, advance=1)
    console.log("Extraction complete.")


click_app = typer.main.get_command(app)

if __name__ == "__main__":
    app()
