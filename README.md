# selenium-screenshot-compare

Compare a website's rendering between **two Firefox versions** through a
click-based navigation scenario. At each step, both full-page renders are
captured and their pixel difference is measured.

Usable from **plain Python** or as a **Robot Framework** library.

## Installation

```bash
pip install selenium-screenshot-compare
```

You need two Firefox binaries (your system Firefox + a second version).
See [docs/firefox-setup.md](docs/firefox-setup.md) for how to get one.

## Quick start — Python

```python
from selenium_screenshot_compare import DualSession, compare_images

session = DualSession("/usr/bin/firefox", "./firefoxes/firefox-128esr/firefox")
session.open("https://example.com")
session.click("css=a.nav-link")
session.capture_both("a.png", "b.png")
result = compare_images("a.png", "b.png", "diff.png")
print(f"{result.percent:.2f} % difference")
session.close()
```

## Quick start — Robot Framework

```bash
pip install selenium-screenshot-compare[robot]
robot --outputdir output/robot tests/interactive_navigation.robot
```

```robotframework
Open Versions    ${SITE}    ${FIREFOX_A}    ${FIREFOX_B}
Capture And Compare    home    ${CAPTURES_DIR}
Click Element    css=a[href="/photographie"]
Capture And Compare    after-click    ${CAPTURES_DIR}
[Teardown]    Close Versions
```

## Keywords

| Keyword | Role |
|---|---|
| `Open Versions` | open the URL in both Firefox instances |
| `Go To` | navigate to a URL |
| `Click Element` | click (`css=`, `id=`, `xpath=`…) |
| `Input Text` | type text |
| `Go Back` | previous page |
| `Capture And Compare` | capture + diff + `result.json` |
| `Load Storage State` | inject cookies + localStorage (authenticated session) |
| `Close Versions` | close both browsers |

## Output

Each `Capture And Compare` produces a folder with `version_a.png`,
`version_b.png`, `diff.png`, and a `result.json`:

```json
{
  "difference_percent": 0.0,
  "first_diff_y": null,
  "firefox_a": "152.0.1",
  "firefox_b": "128.0"
}
```

## Documentation

- [Firefox setup](docs/firefox-setup.md) — getting a second Firefox binary (Linux / Windows / macOS)
- [Authenticated sessions](docs/authenticated-sessions.md) — comparing pages behind a login
- [Windows notes](docs/windows.md) — venv paths, Firefox paths, running suites
- [Contributing](CONTRIBUTING.md) — development setup, linting, CI, releasing

## License

[MIT](LICENSE)
