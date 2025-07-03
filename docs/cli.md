# CLI Reference

The Bigger Picker tool is a command-line interface (CLI) for syncing the various applications used by the Bigger Picture team.
It orchestrates the automated data extraction process for articles identified in Rayyan, and maintains a sync between Rayyan, Airtable, and Asana.

These docs are a very brief reference for how to use the CLI tool.

## Installation

1. Clone the repository:

    ```sh
    git clone <https://github.com/Motivation-and-Behaviour/bigger_picker.git>
    cd bigger_picker
    ```

2. Install dependencies:

    ```sh
    pip install -e .
    ```

    You can also optionally install the development dependencies:

    ```sh
    pip install -e .[dev]
    ```

3. Set up your `.env` file with the required API keys and configuration values.
   The provided `.env.example` can be used as a template.

## Configuration

Most settings for the project are set in the [bigger_picker/config.py](https://github.com/Motivation-and-Behaviour/bigger_picker/blob/main/bigger_picker/config.py) file.
If you are using this package for a project other than the Bigger Picture, you will need to adjust the settings there.
Some other components are also hardcoded.

You will need API keys for Airtable, Asana, and OpenAI.
You will also need a `rayyan_tokens.json` file for Rayyan API authentication.

## Usage

Once installed, you can use the command-line interface (CLI) to interact with the Bigger Picker tools.

The methods for interacting with the CLI are outlined below.

::: mkdocs-click
    :module: bigger_picker.cli
    :command: click_app
    :prog_name: bigger-picker
    :depth: 2
