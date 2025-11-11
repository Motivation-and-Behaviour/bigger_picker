import os

import requests
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

import bigger_picker.config as config
from bigger_picker.airtable import AirtableManager
from bigger_picker.asana import AsanaManager
from bigger_picker.credentials import load_token
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
        TimeElapsedColumn(),
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
    console.log("Screening complete.")


@app.command()
def register_webhook(
    dotenv_path: str = typer.Option(None, help="Path to .env file with credentials"),
    asana_token: str = typer.Option(None, help="Asana API token"),
    revoke: bool = typer.Option(
        False, help="Revoke existing webhook before creating a new one"
    ),
):
    if asana_token is None:
        asana_token = load_token("ASANA_TOKEN")

    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        load_dotenv(os.path.join(BASE_DIR, ".env"))

    PROJECT_GID = config.ASANA_PROJECT_ID
    WEBHOOK_URL = config.RENDER_WEBHOOK_URL
    ASANA_WORKSPACE = config.ASANA_WORKSPACE_ID

    console = Console()

    if revoke:
        console.log("Revoking existing webhooks...")
        response = requests.get(
            "https://app.asana.com/api/1.0/webhooks",
            headers={
                "Authorization": f"Bearer {asana_token}",
                "Content-Type": "application/json",
            },
            params={
                "workspace": ASANA_WORKSPACE,
                "resource": PROJECT_GID,
            },
        )
        if response.status_code == 200:
            webhooks = response.json().get("data", [])
            for webhook in webhooks:
                gid = webhook["gid"]
                del_response = requests.delete(
                    f"https://app.asana.com/api/1.0/webhooks/{gid}",
                    headers={
                        "Authorization": f"Bearer {asana_token}",
                        "Content-Type": "application/json",
                    },
                )
                if del_response.status_code == 200:
                    console.log(f"✅ Revoked webhook {gid}")
                else:
                    console.log(
                        f"❌ Failed to revoke webhook {gid}: {del_response.json()}"
                    )
        else:
            console.log(f"❌ Failed to fetch webhooks: {response.json()}")

    console.log("Registering new webhook...")
    response = requests.post(
        "https://app.asana.com/api/1.0/webhooks",
        headers={
            "Authorization": f"Bearer {asana_token}",
            "Content-Type": "application/json",
        },
        json={
            "data": {
                "resource": PROJECT_GID,
                "target": WEBHOOK_URL,
                "filters": [{"resource_type": "task", "action": "changed"}],
            }
        },
    )

    if response.status_code == 201:
        console.log("✅ Webhook created!")
        console.log("Check your Render logs for the WEBHOOK_SECRET")
        console.log(f"Webhook GID: {response.json()['data']['gid']}")
    else:
        console.log(f"Error: {response.json()}")


click_app = typer.main.get_command(app)

if __name__ == "__main__":
    app()
