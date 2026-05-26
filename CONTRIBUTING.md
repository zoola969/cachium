# Contributing

## Setup

```bash
# Install all dependency groups (dev, docs, test)
uv sync

# Install pre-commit hooks
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

## Development workflow

```bash
# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test__decorator.py

# Type checking
uv run mypy cachium

# Run coverage
uv run coverage run -m pytest && uv run coverage report

# Lint and format manually (pre-commit also runs these)
uv run ruff check --fix cachium tests
uv run ruff format cachium tests
```

## Commit messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/). The `commit-msg` pre-commit hook enforces this automatically.

Format: `<type>(<optional scope>): <description>`

Allowed types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`

Examples:
```
feat: add Redis storage backend
fix: prevent dog-pile under high concurrency
docs: add CacheWith usage example
chore: bump ruff to v0.16
```

Breaking changes: append `!` after the type or add `BREAKING CHANGE:` in the footer.

## Pre-commit hooks

The following hooks run on every commit:

| Hook | Purpose |
|------|---------|
| `check-added-large-files` | Prevent accidental large file commits |
| `check-json`, `check-yaml`, `check-toml` | Validate config files |
| `check-merge-conflict` | Catch unresolved merge conflict markers |
| `detect-private-key` | Block accidental secret commits |
| `end-of-file-fixer`, `trailing-whitespace` | Normalize whitespace |
| `no-commit-to-branch` | Block direct commits to `master` |
| `add-trailing-comma` | Enforce trailing commas |
| `ruff` | Lint and auto-fix Python code (includes import sorting) |
| `ruff-format` | Format Python code |
| `toml-sort` | Keep `pyproject.toml` keys sorted |
| `conventional-pre-commit` | Enforce conventional commit message format (commit-msg stage) |

## Pull requests

- Direct pushes to `master` are blocked; open a PR instead.
- PRs should be small and focused. One logical change per PR.
- All CI checks (tests, type checking, pre-commit) must pass before merging.

## Extending the library

See [CLAUDE.md](CLAUDE.md) / [AGENTS.md](AGENTS.md) for the architecture overview and guidance on adding new storage backends, serializers, and key builders.
