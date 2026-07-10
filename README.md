# selenium-screenshot-compare

Compare a website's rendering between **two Firefox versions** through a
**navigation scenario**: open the site in both versions in parallel, **click**
on buttons/links (Selenium-style keywords), and at each step capture both
full-page renders and measure their difference — like a plain functional test
in Robot Framework.

Distributed as an **installable Python package**; usable from plain Python or
as a Robot Framework library.

## Installation

From the repository (editable install, recommended for development):

```bash
python3 -m venv .venv
./.venv/bin/pip install -e ".[robot]"        # "robot" extra = Robot Framework
```

For plain Python usage (no Robot Framework):

```bash
./.venv/bin/pip install -e .
```

For development (lint, hooks, tests):

```bash
./.venv/bin/pip install -e ".[dev]"
./.venv/bin/pre-commit install
```

You do **not** need to install geckodriver: Selenium Manager (bundled with
selenium >= 4.6) downloads it automatically on first run.

> **Windows** — a venv places its executables under `.venv\Scripts\` (not
> `.venv/bin/`). Replace `./.venv/bin/xxx` with `.\.venv\Scripts\xxx.exe` in
> every command. Details: see the [Windows](#windows) section.

## Architecture

```
selenium_screenshot_compare/           installable Python package
├── __init__.py                        public API (plain Python)
├── capture.py                         Firefox driver + full-page capture (anti lazy-load)
├── comparison.py                      image diff (numpy) -> DiffResult
├── session.py                         dual session: 2 Firefox instances driven in lockstep
├── storage.py                         storage state (cookies + localStorage)
├── naming.py                          slugify (per-step folder name)
└── ScreenshotCompareLibrary.py        Robot Framework library (functions -> keywords)
tests/                                 example Robot Framework suites
├── interactive_navigation.robot       compares 2 versions across clicks
└── capture_auth.robot                 captures the storage state (authenticated session)
resources/env/                         auth.json (storage state) — gitignored
output/                                generated outputs (gitignored)
├── interactive/<step>/                version_a.png, version_b.png, diff.png, result.json
└── robot/                             Robot Framework reports (log.html, report.html)
pyproject.toml                         packaging (setuptools) + ruff config
```

Business logic lives in the Python package; the Robot Framework library and
the suites are just thin wrappers around it.

## Usage — Python API

```python
from selenium_screenshot_compare import DualSession, compare_images

session = DualSession("/usr/bin/firefox", "./firefoxes/firefox-128esr/firefox")
session.open("https://anathos.me/")
session.click("css=a[href='/photographie']")
session.capture_both("a.png", "b.png")
result = compare_images("a.png", "b.png", "diff.png")
print(f"{result.percent:.2f} % difference")
session.close()
```

## Usage — Robot Framework

Once the package is installed with the `robot` extra, import the library by
name:

```robotframework
Library    selenium_screenshot_compare.ScreenshotCompareLibrary
```

Run the example suite:

```bash
./.venv/bin/robot --outputdir output/robot tests/interactive_navigation.robot
```

The test reads like a plain Selenium test:

```robotframework
Open Versions    ${SITE}    ${FIREFOX_A}    ${FIREFOX_B}
Capture And Compare    home    ${CAPTURES_DIR}
Click Element    css=a[href="/photographie"]
Capture And Compare    after-click-photography    ${CAPTURES_DIR}
Go Back
Click Element    css=a[href="/en"]
Capture And Compare    after-click-language-button    ${CAPTURES_DIR}
[Teardown]    Close Versions
```

Variables overridable with `--variable`: `SITE`, `FIREFOX_A`, `FIREFOX_B`,
`CAPTURES_DIR`, `FAIL_OVER` (% difference above which a step fails).

### Keywords (dual session, Selenium-style)

| Keyword | Role |
|---|---|
| `Open Versions` | opens the URL in both Firefox instances |
| `Go To` | navigate to a URL (both versions) |
| `Click Element` | click (`css=`, `id=`, `xpath=`…) in both |
| `Input Text` | type text in both |
| `Go Back` | previous page in both |
| `Load Storage State` | inject cookies + localStorage (authenticated session) into both |
| `Capture And Compare` | capture current state + diff + `result.json` |
| `Close Versions` | close both browsers |

### Authenticated session (storage state)

To compare pages behind a login, first capture a session (cookies +
localStorage) with your Firefox, then replay it in both versions — no need to
re-authenticate.

**1. Capture** (visible window: log in manually during the wait):

```bash
./.venv/bin/robot --outputdir output/robot tests/capture_auth.robot
```

→ writes `resources/env/auth.json`. Variables: `SITE`, `FIREFOX`, `LOGIN_WAIT`
(seconds to log in), `HEADLESS`.

**2. Reuse**: `interactive_navigation.robot` already calls
`Load Storage State ${AUTH_FILE}` right after `Open Versions`. If `auth.json`
exists, both versions start logged in; otherwise a warning is logged and the
session stays anonymous.

> 🔒 `resources/env/` is **gitignored**: `auth.json` contains session cookies
> (secrets) and must **never** be committed or shared.

### Output

Each `Capture And Compare` writes `output/interactive/<step>/` with both
captures, the diff image, and a `result.json`:

```json
{
  "step": "after-click-photography",
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

### Known limitation

The diff is **pixel-by-pixel**: a small vertical offset (an element rendered
a few px higher by one version) makes everything below it "spill over" and
inflates the percentage even if the pages look visually the same. The
`first_diff_y` field helps distinguish a "real rendering difference" from a
"simple offset".

## Getting a second Firefox binary

To compare two **versions**, you need two distinct binaries. Grab the build
**for your OS** (a specific ESR release, for example), without touching the
system Firefox.

> ⚠️ On Windows, do **not** grab the `.tar.bz2`: it's the Linux build, it has
> no `firefox.exe` and won't run on Windows.

### Linux

```bash
mkdir -p firefoxes && cd firefoxes
wget "https://ftp.mozilla.org/pub/firefox/releases/128.0esr/linux-x86_64/en-US/firefox-128.0esr.tar.bz2"
tar xjf firefox-128.0esr.tar.bz2 && mv firefox firefox-128esr
# -> binary: firefoxes/firefox-128esr/firefox
```

### Windows

Download the `Firefox Setup 128.0esr.exe` installer from
<https://ftp.mozilla.org/pub/firefox/releases/128.0esr/win64/en-US/>, then
install it silently into a dedicated folder (PowerShell):

```powershell
& ".\Firefox Setup 128.0esr.exe" /S /InstallDirectoryPath="C:\ff128esr"
& "C:\ff128esr\firefox.exe" --version   # should respond -> binary: C:\ff128esr\firefox.exe
```

### macOS

Mount the `.dmg` for the desired version and copy the app under another name;
the binary lives at `Firefox.app/Contents/MacOS/firefox`.

All versions: <https://ftp.mozilla.org/pub/firefox/releases/>. The `firefoxes/`
folder is gitignored (heavy binary, ~90 MB).

## Windows

Three differences compared to the Linux commands elsewhere in the README:

1. **venv executables** live in `.venv\Scripts\`:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\pip.exe install -e ".[robot]"
   ```

   Or activate the venv once, then call `robot`, `pip`… directly:

   ```powershell
   .\.venv\Scripts\Activate.ps1   # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

2. **Firefox paths**: find the system binary, install the second one in a
   dedicated folder, and use forward slashes `/` (`\` is an escape character
   in Robot Framework):

   ```powershell
   # System Firefox (via the registry)
   (Get-ItemProperty "HKLM:\SOFTWARE\Mozilla\Mozilla Firefox\*\Main")."PathToExe"

   # Second Firefox: install a specific version into a separate folder
   & ".\Firefox Setup 128.0esr.exe" /S /InstallDirectoryPath="C:\ff128esr"
   ```

3. **Run the suite** overriding both Firefox paths:

   ```powershell
   .\.venv\Scripts\robot.exe `
     --variable "FIREFOX_A:C:/Program Files/Mozilla Firefox/firefox.exe" `
     --variable "FIREFOX_B:C:/ff128esr/firefox.exe" `
     --outputdir output/robot `
     tests/interactive_navigation.robot
   ```

> If you get `NoSuchDriverException: Unable to obtain driver for firefox`,
> it's almost always an invalid `FIREFOX_A`/`FIREFOX_B` path (the defaults
> are Linux paths): check that `& "<path>" --version` responds for each.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development setup, linting, and CI
details.
