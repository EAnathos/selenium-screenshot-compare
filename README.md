# selenium-screenshot-compare

Compare le rendu d'un site entre **deux versions de Firefox** au fil d'un
**scénario de navigation** : on ouvre le site dans les deux versions en
parallèle, on **clique** sur des boutons/liens (keywords façon Selenium) et à
chaque étape on capture les deux rendus en pleine page et on mesure leur
différence — comme un test fonctionnel classique en Robot Framework.

## Architecture

```
src/                              tout le code Python
├── capture.py                    driver Firefox + capture pleine page (scroll anti lazy-load)
├── comparison.py                 diff d'images (numpy) -> DiffResult
├── session.py                    session double : 2 Firefox pilotés en lockstep
├── naming.py                     slugify (nom de dossier par étape)
└── ScreenshotCompareLibrary.py   librairie Robot Framework (les fonctions -> keywords)
tests/interactive_navigation.robot  la suite de test
output/                           sorties (gitignore)
├── interactive/<étape>/          version_a.png, version_b.png, diff.png, result.json
└── robot/                        rapports Robot Framework (log.html, report.html)
```

La logique métier vit dans `src/` ; la suite Robot Framework n'en est qu'une
enveloppe.

## Installation

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

geckodriver n'a **pas** besoin d'être installé : Selenium Manager (inclus dans
selenium >= 4.6) le télécharge automatiquement au premier lancement.

## Obtenir un second binaire Firefox

Pour comparer deux **versions**, il faut deux binaires distincts. Sans toucher au
Firefox système, on peut récupérer une release précise (ESR par exemple) :

```bash
mkdir -p firefoxes && cd firefoxes
wget "https://ftp.mozilla.org/pub/firefox/releases/128.0esr/linux-x86_64/en-US/firefox-128.0esr.tar.bz2"
tar xjf firefox-128.0esr.tar.bz2 && mv firefox firefox-128esr
```

Toutes les versions : <https://ftp.mozilla.org/pub/firefox/releases/>. Le dossier
`firefoxes/` est gitignoré (binaire lourd, ~90 Mo).

## Usage

```bash
./.venv/bin/robot --outputdir output/robot tests/interactive_navigation.robot
```

La librairie est référencée par chemin relatif dans le `.robot`, donc **pas
besoin de `--pythonpath`** ni d'être dans un répertoire précis.

Le test se lit comme un test Selenium classique :

```robotframework
Open Versions    ${SITE}    ${FIREFOX_A}    ${FIREFOX_B}
Capture And Compare    accueil    ${CAPTURES_DIR}
Click Element    css=a[href="/photographie"]
Capture And Compare    apres-clic-photographie    ${CAPTURES_DIR}
Go Back
Click Element    css=a[href="/en"]
Capture And Compare    apres-clic-bouton-langue    ${CAPTURES_DIR}
[Teardown]    Close Versions
```

Variables surchargeables avec `--variable` : `SITE`, `FIREFOX_A`, `FIREFOX_B`,
`CAPTURES_DIR`, `FAIL_OVER` (% de différence au-delà duquel une étape échoue).

### Keywords (session double, façon Selenium)

| Keyword | Rôle |
|---|---|
| `Open Versions` | ouvre l'URL dans les 2 Firefox |
| `Go To` | navigue vers une URL (2 versions) |
| `Click Element` | clique (`css=`, `id=`, `xpath=`…) dans les 2 |
| `Input Text` | saisit du texte dans les 2 |
| `Go Back` | page précédente dans les 2 |
| `Capture And Compare` | capture l'état courant + diff + `result.json` |
| `Close Versions` | ferme les 2 navigateurs |

### Sortie

Chaque `Capture And Compare` écrit `output/interactive/<étape>/` avec les deux
captures, l'image de diff et un `result.json` :

```json
{
  "step": "apres-clic-photographie",
  "url": "https://anathos.me/photographie",
  "firefox_a": "152.0.1",
  "firefox_b": "128.0",
  "difference_percent": 0.0,
  "first_diff_y": null,
  "image_width": 1268,
  "image_height": 3469,
  "threshold": 20,
  "screenshots": { "version_a": "version_a.png", "version_b": "version_b.png", "diff": "diff.png" }
}
```

### Limite à connaître

Le diff est **pixel-par-pixel** : un simple décalage vertical (un élément rendu
quelques px plus haut par une version) fait « déborder » tout le contenu en
dessous et gonfle le %, même si les pages se ressemblent visuellement. Le champ
`first_diff_y` aide à distinguer « vraie différence de rendu » de « simple
décalage ».

## Qualité / développement

Lint et format des suites Robot Framework avec **Robocop**, orchestrés par
**pre-commit** :

```bash
./.venv/bin/pip install -r requirements-dev.txt
./.venv/bin/pre-commit install          # active le hook git
```

Ensuite chaque `git commit` formate et vérifie automatiquement les `.robot`.
Manuellement :

```bash
./.venv/bin/robocop format    # formate les .robot (ex-robotidy)
./.venv/bin/robocop check     # lint
./.venv/bin/pre-commit run --all-files
```
