import os
import time
from datetime import datetime

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

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
def monitor(
    dotenv_path: str = typer.Option(None, help="Path to .env file with credentials"),
    airtable_api_key: str = typer.Option(None, help="Airtable API key"),
    asana_token: str = typer.Option(None, help="Asana API token"),
    openai_api_key: str = typer.Option(None, help="OpenAI API key"),
    openai_model: str = typer.Option("gpt-4.1", help="OpenAI model to use"),
    rayyan_creds_path: str = typer.Option(
        None, help="Path to Rayyan credentials JSON file"
    ),
    interval: int = typer.Option(
        60, help="Interval in seconds between checks for changes"
    ),
    max_errors: int = typer.Option(
        5, help="Maximum number of consecutive errors before stopping"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug logging to console"
    ),
):
    def create_stats_table(stats):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Status", stats["status"])
        table.add_row("Uptime", str(stats["uptime"]))
        table.add_row("Last Check", stats["last_check"])
        table.add_row("Total Syncs", str(stats["total_syncs"]))
        table.add_row("Total Polls", str(stats["total_polls"]))
        table.add_row("Consecutive Errors", str(stats["consecutive_errors"]))

        return table

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

    stats = {
        "status": "[green]Running[/green]",
        "uptime": datetime.now() - datetime.now(),
        "last_check": "Never",
        "total_syncs": 0,
        "consecutive_errors": 0,
        "total_polls": 0,
        "start_time": datetime.now(),
    }

    try:
        with Live(
            create_stats_table(stats), refresh_per_second=1, console=console
        ) as live:
            while True:
                try:
                    stats["uptime"] = datetime.now() - stats["start_time"]
                    stats["status"] = "[cyan]Checking...[/cyan]"
                    stats["total_polls"] += 1
                    live.update(create_stats_table(stats))

                    events = integration.asana.get_events()
                    check_time = datetime.now().strftime("%H:%M:%S")
                    stats["last_check"] = check_time

                    if events or stats["total_syncs"] == 0:
                        stats["consecutive_errors"] = 0
                        stats["status"] = "[yellow]Syncing...[/yellow]"
                        live.update(create_stats_table(stats))

                        integration.sync()
                        stats["total_syncs"] += 1
                        integration.asana.get_events()  # Clear events after sync
                        stats["status"] = "[green]✓ Sync complete[/green]"
                    else:
                        stats["status"] = "[green]Idle[/green]"

                    live.update(create_stats_table(stats))

                except Exception as e:
                    stats["consecutive_errors"] += 1
                    stats["status"] = f"[red]Error: {e}[/red]"
                    live.update(create_stats_table(stats))

                    if stats["consecutive_errors"] >= max_errors:
                        stats["status"] = (
                            "[bold red]Stopped (too many errors)[/bold red]"
                        )
                        live.update(create_stats_table(stats))
                        break

                for t in range(interval):
                    time_to_sync = interval - t
                    stats["status"] = (
                        f"[green]Idle (syncing in {time_to_sync}s)[/green]"
                    )
                    live.update(create_stats_table(stats))
                    time.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped by user[/yellow]")


click_app = typer.main.get_command(app)

if __name__ == "__main__":
    app()
