# CLAUDE.md

This file guides Claude Code (and Claude agents) when working in this repo.

## The project in one sentence

Python package + Robot Framework library that compares a website's rendering
between **two Firefox versions** driven in parallel via Selenium.

## Structure

- `src/selenium_screenshot_compare/` — installable package (`src/` layout).
  - Plain Python core: `capture.py`, `comparison.py`, `session.py`,
    `storage.py`, `naming.py`.
  - `ScreenshotCompareLibrary.py`: Robot Framework wrapper around the core.
    **Do not** duplicate business logic here — only `@keyword` methods.
- `tests/` — example `.robot` suites; they import `Library
  selenium_screenshot_compare.ScreenshotCompareLibrary` (the package must be
  installed, see README).
- `resources/env/` — storage state (`auth.json`), **gitignored**. Contains
  session cookies: never commit, never log the contents.
- `firefoxes/` — downloaded Firefox binaries, **gitignored**.
- `output/` — captures, diffs, `result.json`, Robot reports, **gitignored**.

## Installation convention

Always editable with the `dev` extra during development:

```bash
./.venv/bin/pip install -e ".[dev]"
```

The `requirements*.txt` files just forward to `pip install -e .[…]` — they
exist for backwards compatibility, but `pyproject.toml` is the source of truth.

## Code style

- Python **3.10+** (we use `X | None`, `from __future__ import annotations`
  is already in place).
- Ruff is configured in `pyproject.toml` (`[tool.ruff]`, `line-length = 100`,
  rule set `E,F,W,I,UP,B,SIM,RUF`).
- Docstrings and comments **in English**.
- No abstractions/factories/speculative layers. The code is intentionally flat.

## Quality — hooks

The project uses `pre-commit` with:

- **ruff** (Python lint + format)
- **robocop / robocop-format** (`.robot` lint + format)
- standard **pre-commit-hooks** (whitespace, EOF, YAML/TOML, large files,
  `debug-statements`)

To do once per clone:

```bash
./.venv/bin/pre-commit install
```

After any substantive change, run:

```bash
./.venv/bin/pre-commit run --all-files
```

Never commit with `--no-verify` unless explicitly authorised — if a hook
fails, fix the root cause.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request:

- `pre-commit run --all-files` on Python 3.12
- Package build (`python -m build`)
- `robot --dryrun tests/` to verify the library imports cleanly

If you change tooling (Ruff rules, Robocop config, hook versions), update the
workflow accordingly.

## Adding a Robot Framework keyword

1. Write the logic in a Python module of the package (not in
   `ScreenshotCompareLibrary.py`).
2. Expose a clean function/object in `src/selenium_screenshot_compare/__init__.py`
   if it belongs to the public API.
3. Add a `@keyword("Human Readable Name")` method in
   `ScreenshotCompareLibrary.py` that delegates to the core.
4. Document the keyword (short docstring) and add it to the README table.

## Robot Framework — good to know

- The `.robot` files load the library by **module name**:
  `Library    selenium_screenshot_compare.ScreenshotCompareLibrary`. This
  requires the package to be **installed** in the active venv.
- Windows paths inside `.robot` files must use forward slashes `/` (`\` is a
  Robot Framework escape character).
- The comparison is **pixel-by-pixel**; a vertical offset inflates the
  percentage even when the pages look identical. `first_diff_y` helps tell
  the two cases apart.

## What not to do

- Do not reintroduce the old `sys.path.insert` hack in the Robot Framework
  library — the package is now importable normally.
- Do not read or commit `resources/env/auth.json` (secrets).
- Do not install geckodriver manually: Selenium Manager handles it.
- Do not add a runtime dependency without updating `pyproject.toml`
  (`dependencies` for the core, `optional-dependencies` for the rest).

## Checks before saying "it's ready"

- `./.venv/bin/pre-commit run --all-files` passes.
- `./.venv/bin/python -c "import selenium_screenshot_compare as s;
  print(s.__version__)"` responds without error.
- If a `.robot` moved: `./.venv/bin/robot --dryrun tests/` stays green
  (requires Firefox but at least validates the library import).
