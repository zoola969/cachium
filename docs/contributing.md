# Contributing

Thank you for considering contributing!

This page combines our previous Development Guide and contribution guidelines.

## Local environment

- Python 3.10+
- Optional tools for docs: mkdocs, mkdocs-material, mkdocstrings[python]

Install the docs toolchain:

```bash
uv sync --group docs
```

Preview documentation locally:

```bash
uv run mkdocs serve
```

This will start a local server (usually http://127.0.0.1:8000/).

## Running tests

```bash
uv run pytest
```

## Linting and typing

- Use Python 3.10+ and run linters before committing
- Follow typing and docstring conventions used in the project

## Opening issues and PRs

Open issues and PRs on GitHub: https://github.com/zoola969/cachium
