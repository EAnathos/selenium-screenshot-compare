# Contributing

## Development setup

```bash
python3 -m venv .venv
./.venv/bin/pip install -e ".[dev]"
./.venv/bin/pre-commit install
```

## Linting & formatting

Orchestrated by **pre-commit** — every `git commit` runs them automatically.

| Tool | Scope | What it does |
|---|---|---|
| **Ruff** | Python (`src/`) | lint + format (replaces flake8 / black / isort) |
| **Robocop** | `.robot` files | lint + format |
| **pre-commit-hooks** | everything | trailing whitespace, EOF, YAML/TOML, large files, debug statements |

Run manually:

```bash
./.venv/bin/ruff check src/             # Python lint
./.venv/bin/ruff format src/            # Python format
./.venv/bin/robocop format              # format .robot
./.venv/bin/robocop check               # lint .robot
./.venv/bin/pre-commit run --all-files  # everything at once
```

## Continuous integration

A [GitHub Actions workflow](.github/workflows/ci.yml) runs on every push and
pull request:

- **Lint** — `pre-commit run --all-files` (Python 3.12)
- **Smoke test** — install + import on Python 3.10 and 3.14
- **Build** — `python -m build`, install the wheel, verify the import
- **Robot dry-run** — `robot --dryrun tests/` to validate the library loads

## Checks before submitting

```bash
./.venv/bin/pre-commit run --all-files
./.venv/bin/python -c "import selenium_screenshot_compare as s; print(s.__version__)"
./.venv/bin/robot --dryrun tests/
```
