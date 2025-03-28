# Social Media Scraper

A modular and extensible social media scraping tool.

## Project Structure

The project follows a clean architecture pattern with clear separation of concerns:

- `src/`: Source code
  - `core/`: Core functionality and types
  - `utils/`: Utility functions and helpers
  - `browser/`: Browser automation
  - `fetchers/`: Platform-specific scrapers
- `tests/`: Test suite
- `config/`: Configuration files
- `data/`: Data storage
- `docs/`: Documentation

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Install playwright browsers: `playwright install`

## Configuration

Copy `config/app_config.json` to create your local configuration and update the values.

## Usage

[Usage instructions to be added]

## Development

See `docs/development.md` for development guidelines.