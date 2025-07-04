# Bigger Picker

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![GitHub License](https://img.shields.io/github/license/Motivation-and-Behaviour/bigger_picker)
[![Actions status](https://github.com/Motivation-and-Behaviour/bigger_picker/workflows/Tests/badge.svg)](https://github.com/Motivation-and-Behaviour/bigger_picker/actions)
[![codecov](https://codecov.io/gh/Motivation-and-Behaviour/bigger_picker/graph/badge.svg?token=QvpFlLP1JD)](https://codecov.io/gh/Motivation-and-Behaviour/bigger_picker)

Bigger Picker is a a simple set of tools to support the [Bigger Picture](https://github.com/Motivation-and-Behaviour/bigger_picture) project.
It is meant to streamline the process of extracting, managing, and syncing research article metadata and datasets across multiple platforms, including Airtable, Asana, Rayyan, and OpenAI.

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/Motivation-and-Behaviour/bigger_picker.git
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

Most settings for the project are set in the [bigger_picker/config.py](bigger_picker/config.py) file.
If you are using this package for a project other than the Bigger Picture, you will need to adjust the settings there.
Some other components are also hardcoded.

You will need API keys for Airtable, Asana, and OpenAI.
You will also need a `rayyan_tokens.json` file for Rayyan API authentication.

## Usage

Once installed, you can use the command-line interface (CLI) to interact with the Bigger Picker tools.

The CLI provides two main commands:

- **Process articles and extract data:**

  ```sh
  bigger_picker process
  ```

- **Sync Airtable and Asana statuses:**

  ```sh
  bigger_picker sync
  ```

Appending `--help` to either command will provide additional options and usage information.
See `python -m bigger_picker.cli --help` for all options.

## License

This project is licensed under the MIT License.
