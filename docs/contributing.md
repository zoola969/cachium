# Contributing

Thank you for considering contributing!

This page combines our previous Development Guide and contribution guidelines.

## Local environment

- Python 3.9+
- Optional tools for docs: mkdocs, mkdocs-material, mkdocstrings[python]

Install the docs toolchain:

```bash
pip install mkdocs mkdocs-material "mkdocstrings[python]"
```

Preview documentation locally:

```bash
mkdocs serve
```

This will start a local server (usually http://127.0.0.1:8000/).

## Running tests

```bash
pytest -q
```

## Linting and typing

- Use Python 3.9+ and run linters before committing
- Follow typing and docstring conventions used in the project

## Opening issues and PRs

Open issues and PRs on GitHub: https://github.com/zoola969/py-cashier
