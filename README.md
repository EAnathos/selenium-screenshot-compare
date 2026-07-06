# selenium-screenshot-compare

Compare le rendu d'un site entre **deux versions de Firefox** : capture chaque
page en entier (pleine hauteur) avec les deux binaires, produit une image de diff
et un pourcentage de pixels différents.

Deux façons de l'utiliser :

- **CLI page unique** (`compare.py`) — comparer une seule URL, rapidement.
- **Suite Robot Framework** (`tests/firefox_versions.robot`) — crawler tout un
  site et comparer chaque page, avec un fichier résultat par page.

## Architecture

```
src/                           package cœur (Python pur, sans Robot Framework)
├── capture.py                 capture Selenium + scroll anti lazy-loading
├── comparison.py              diff d'images (numpy) -> DiffResult
└── crawl.py                   découverte des pages (crawl same-domain)
ScreenshotCompareLibrary.py    librairie Robot Framework (les fonctions -> keywords)
PerPageModifier.py             pre-run modifier RF : 1 test distinct par page
tests/firefox_versions.robot   suite RF
compare.py                     CLI page unique (utilise le package)
output/                        toutes les sorties (gitignore)
├── single/                    captures de la CLI page unique
├── crawl/<slug>/              captures + result.json par page crawlée
└── robot/                     rapports Robot Framework (log.html, report.html)
```

La logique métier vit dans `src/` ; Robot Framework et la CLI n'en sont que deux
enveloppes. Aucune duplication.

## Installation

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

geckodriver n'a **pas** besoin d'être installé : Selenium Manager (inclus dans
selenium >= 4.6) le télécharge automatiquement au premier lancement.

## Usage — CLI page unique

```bash
./.venv/bin/python compare.py https://anathos.me/ \
    --firefox-a /usr/bin/firefox \
    --firefox-b "$(pwd)/firefoxes/firefox-128esr/firefox" \
    --width 1280 --height 900 --wait 2
```

> `--firefox-b` doit pointer vers un binaire **qui existe** sur ta machine. Ici
> on utilise le Firefox 128 ESR installé dans `firefoxes/` (voir plus bas). Un
> chemin inexistant comme `/opt/firefox-esr/firefox` provoque une erreur.

Résultats dans `output/` :

- `version_a.png` — capture avec le 1er binaire
- `version_b.png` — capture avec le 2e binaire
- `diff.png` — différences surlignées (clair sur fond noir)

Sortie console : le **% de pixels différents** et la **première ligne de
divergence substantielle** (y en px), qui localise le point où le layout
commence à se décaler.

### Options utiles

- `--threshold N` (défaut 20) : écart de couleur (0-255) sous lequel un pixel est
  considéré identique. Monte-le pour ignorer davantage l'anti-aliasing, baisse-le
  pour un diff strict.

### Limite à connaître

Le diff est **pixel-par-pixel** : un simple décalage vertical (une image ou un
tableau rendu 3px plus haut par une version) fait « déborder » tout le contenu
en dessous et gonfle le %, même si les pages se ressemblent visuellement. C'est
le comportement de tous les diffs naïfs. La ligne de première divergence aide à
distinguer « vraie différence de rendu » de « simple décalage ».

## Obtenir un second binaire Firefox

Pour comparer deux **versions**, il faut deux binaires distincts. Quelques
options, sans toucher au Firefox système :

### Firefox ESR / Developer Edition / une release précise (portable)

```bash
# Exemple : une version archivée précise, décompressée dans /opt
cd /opt
sudo wget "https://ftp.mozilla.org/pub/firefox/releases/128.0esr/linux-x86_64/en-US/firefox-128.0esr.tar.bz2"
sudo tar xjf firefox-128.0esr.tar.bz2   # -> /opt/firefox/firefox
```

Toutes les versions sont sur <https://ftp.mozilla.org/pub/firefox/releases/>.
Puis pointe `--firefox-b /opt/firefox/firefox`.

> Astuce : lance chaque version avec un profil séparé si tu veux éviter les
> conflits (`options.add_argument("-profile <dir>")`).

## Usage — site entier (Robot Framework)

La suite crawle le site, compare **chaque page** (un **test RF distinct par
page**) et écrit un fichier `result.json` par page. Le crawl est fait par le
pre-run modifier `PerPageModifier.py`, qui génère un test par URL découverte :

```bash
./.venv/bin/robot \
    --prerunmodifier "PerPageModifier.py;https://anathos.me/;20" \
    --outputdir output/robot \
    tests/firefox_versions.robot
```

Arguments du modifier : `PerPageModifier.py;<START_URL>;<MAX_PAGES>;<MAX_DEPTH>`.

> **Séparateur `;` et non `:`** — comme l'URL contient déjà `:` (`https://`),
> il faut utiliser le point-virgule comme séparateur d'arguments de Robot
> Framework, sinon le `:` de `https://` est mal découpé.

La librairie est référencée par chemin relatif dans le `.robot`, donc **pas
besoin de `--pythonpath`** ni d'être dans un répertoire précis.

Les paramètres de comparaison se surchargent avec `--variable` :

```bash
./.venv/bin/robot \
    --prerunmodifier "PerPageModifier.py;https://exemple.com/;50" \
    --variable FIREFOX_B:/opt/firefox/firefox \
    --variable FAIL_OVER:2.0 \
    --outputdir output/robot \
    tests/firefox_versions.robot
```

Variables de comparaison : `FIREFOX_A`, `FIREFOX_B`, `OUTPUT_DIR`, `WIDTH`,
`HEIGHT`, `WAIT`, `THRESHOLD`, `FAIL_OVER` (% de différence au-delà duquel le
test d'une page échoue). Les paramètres de crawl (`START_URL`, `MAX_PAGES`,
`MAX_DEPTH`) sont passés au modifier.

### Sortie du crawl

```
output/
├── crawl/
│   ├── index/
│   │   ├── version_a.png  version_b.png  diff.png
│   │   └── result.json        <-- fichier résultat de la page
│   ├── photographie/…
│   └── en/…
└── robot/                     <-- log.html / report.html (1 test par page)
```

Exemple de `result.json` :

```json
{
  "url": "https://anathos.me/en",
  "firefox_a": "152.0.1",
  "firefox_b": "128.0",
  "difference_percent": 0.0005,
  "first_diff_y": null,
  "image_width": 1268,
  "image_height": 3425,
  "threshold": 20,
  "screenshots": { "version_a": "version_a.png", "version_b": "version_b.png", "diff": "diff.png" },
  "generated_at": "2026-07-06T11:26:59+00:00"
}
```

### Keywords exposés

La librairie `ScreenshotCompareLibrary` transforme les fonctions Python en
keywords Robot Framework :

| Keyword | Rôle |
|---|---|
| `Crawl Site` | découvre les pages same-domain |
| `Capture Page` | capture une URL avec un binaire Firefox |
| `Compare Screenshots` | diffe deux images |
| `Write Page Result` | écrit le `result.json` d'une page |
| `Compare Page Across Versions` | enchaîne tout pour une page (capture A + B, diff, result.json) |

### Découverte statique — limite

Le crawl lit le HTML brut (`urllib`) : les liens injectés en **JavaScript**
(SPA, menus dynamiques) ne sont pas vus. Pour un site à liens en dur c'est
parfait ; sinon il faudra faire la découverte via Selenium.
