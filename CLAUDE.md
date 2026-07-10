# CLAUDE.md

Ce fichier oriente Claude Code (et les agents Claude) quand ils travaillent
dans ce dépôt.

## Le projet en une phrase

Package Python + librairie Robot Framework qui compare le rendu d'un site
entre **deux versions de Firefox** pilotées en parallèle via Selenium.

## Structure

- `src/selenium_screenshot_compare/` — package installable (layout `src/`).
  - Cœur Python pur : `capture.py`, `comparison.py`, `session.py`,
    `storage.py`, `naming.py`.
  - `ScreenshotCompareLibrary.py` : wrapper Robot Framework autour du cœur.
    **Ne pas** dupliquer de logique métier ici — juste des `@keyword`.
- `tests/` — suites `.robot` d'exemple ; elles importent `Library
  selenium_screenshot_compare.ScreenshotCompareLibrary` (le package doit être
  installé, cf. README).
- `resources/env/` — storage state (`auth.json`), **gitignore**. Contient des
  cookies de session : ne jamais committer, ne jamais logger le contenu.
- `firefoxes/` — binaires Firefox téléchargés, **gitignore**.
- `output/` — captures, diffs, `result.json`, rapports Robot, **gitignore**.

## Convention d'installation

Toujours en éditable avec l'extra `dev` pendant le dev :

```bash
./.venv/bin/pip install -e ".[dev]"
```

Les fichiers `requirements*.txt` renvoient à `pip install -e .[…]` — ils sont
là pour rester rétrocompatibles, mais `pyproject.toml` est la source de vérité.

## Style de code

- Python **3.10+** (on utilise `X | None`, `from __future__ import annotations`
  déjà en place).
- Ruff est configuré dans `pyproject.toml` (`[tool.ruff]`, `line-length = 100`,
  règles `E,F,W,I,UP,B,SIM,RUF`).
- Docstrings et commentaires **en français** — c'est la convention du projet,
  ne pas les traduire en anglais.
- Pas d'accents dans les identifiants ni dans les commentaires (héritage :
  compatibilité shells/CI) ; les docstrings sans accents restent le standard.
- Ne pas ajouter d'abstractions/factories/couches spéculatives. Le code est
  volontairement plat.

## Qualité — hooks

Le projet utilise `pre-commit` avec :

- **ruff** (lint + format Python)
- **robocop / robocop-format** (lint + format `.robot`)
- **pre-commit-hooks** standard (whitespace, EOF, YAML/TOML, gros fichiers,
  `debug-statements`)

À faire une fois par clone :

```bash
./.venv/bin/pre-commit install
```

Après toute modification substantielle, faire tourner :

```bash
./.venv/bin/pre-commit run --all-files
```

Ne **jamais** committer avec `--no-verify` sans y avoir été explicitement
autorisé — si un hook échoue, corriger la cause.

## Ajouter un keyword Robot Framework

1. Écrire la logique dans un module Python du package (pas dans
   `ScreenshotCompareLibrary.py`).
2. Exposer une fonction/objet propre dans `src/selenium_screenshot_compare/__init__.py`
   si elle fait partie de l'API publique.
3. Ajouter une méthode `@keyword("Nom Human Readable")` dans
   `ScreenshotCompareLibrary.py` qui délègue au cœur.
4. Documenter le keyword (docstring courte) et l'ajouter au tableau du README.

## Robot Framework — points à connaître

- Le `.robot` charge la librairie par **nom de module** :
  `Library    selenium_screenshot_compare.ScreenshotCompareLibrary`. Cela
  suppose que le package est **installé** dans le venv actif.
- Les chemins Windows dans les `.robot` s'écrivent avec des slashes `/` (le
  `\` est un caractère d'échappement Robot Framework).
- La comparaison est **pixel-par-pixel** ; un décalage vertical gonfle le
  pourcentage même si visuellement identique. `first_diff_y` aide à
  distinguer les deux cas.

## Ce qu'il ne faut pas faire

- Ne pas remettre le hack `sys.path.insert` de l'ancienne version dans la
  librairie Robot Framework — le package est désormais importable
  normalement.
- Ne pas relire ni committer `resources/env/auth.json` (secrets).
- Ne pas installer geckodriver à la main : Selenium Manager s'en charge.
- Ne pas ajouter de dépendance runtime sans mise à jour de `pyproject.toml`
  (`dependencies` pour le cœur, `optional-dependencies` pour le reste).

## Vérifications avant de dire « c'est prêt »

- `./.venv/bin/pre-commit run --all-files` passe.
- `./.venv/bin/python -c "import selenium_screenshot_compare as s;
  print(s.__version__)"` répond sans erreur.
- Si un `.robot` a bougé : `./.venv/bin/robot --dryrun tests/` reste vert
  (nécessite Firefox mais valide au moins l'import de la librairie).
