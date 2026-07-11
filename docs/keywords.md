# Keyword reference

All keywords exposed by the `ScreenshotCompareLibrary`.

```robotframework
Library    selenium_screenshot_compare.ScreenshotCompareLibrary
```

---

## Dual-session keywords

These keywords drive **two Firefox instances** in lockstep: every action is
replayed identically in both browsers so you can compare the rendering at any
point.

### Open Versions

Opens a URL in both Firefox versions and creates the dual session.

| Argument | Type | Default | Description |
|---|---|---|---|
| `url` | str | *required* | URL to open in both browsers |
| `firefox_a` | str | *required* | Path to the first Firefox binary |
| `firefox_b` | str | *required* | Path to the second Firefox binary |
| `width` | int | `1280` | Browser window width (px) |
| `height` | int | `900` | Browser window height (px) |
| `wait` | float | `2.0` | Default wait time (seconds) before each capture |

Both browsers run **headless** with a fixed viewport so the captures are
pixel-comparable. Image lazy-loading is disabled automatically.

```robotframework
Open Versions    https://example.com    /usr/bin/firefox    ./firefoxes/firefox-128esr/firefox
Open Versions    https://example.com    ${FIREFOX_A}    ${FIREFOX_B}    width=1920    height=1080    wait=3.0
```

---

### Go To

Navigates to a new URL in both browsers.

| Argument | Type | Default | Description |
|---|---|---|---|
| `url` | str | *required* | URL to navigate to |

Requires a session opened with `Open Versions`.

```robotframework
Go To    https://example.com/about
```

---

### Click Element

Clicks an element in both browsers.

| Argument | Type | Default | Description |
|---|---|---|---|
| `locator` | str | *required* | Selenium-style locator |

Supported locator strategies:

| Prefix | Strategy | Example |
|---|---|---|
| `css=` | CSS selector | `css=a.nav-link` |
| `xpath=` | XPath | `xpath=//button[@id="submit"]` |
| `id=` | Element ID | `id=submit` |
| `name=` | Element name | `name=email` |
| `link=` | Link text | `link=Contact` |
| `partial link=` | Partial link text | `partial link=Cont` |
| `tag=` | Tag name | `tag=h1` |
| `class=` | Class name | `class=active` |

If no prefix is given, the locator defaults to **XPath** when it starts with
`//`, otherwise **CSS selector**.

```robotframework
Click Element    css=a[href="/about"]
Click Element    id=menu-toggle
Click Element    //button[contains(text(), "OK")]
```

---

### Input Text

Types text into a form field in both browsers. The field is cleared first.

| Argument | Type | Default | Description |
|---|---|---|---|
| `locator` | str | *required* | Selenium-style locator (same as `Click Element`) |
| `text` | str | *required* | Text to type |

```robotframework
Input Text    id=search    robot framework
Input Text    css=input[name="email"]    user@example.com
```

---

### Go Back

Navigates to the previous page in both browsers (equivalent to pressing the
browser back button).

No arguments.

```robotframework
Click Element    css=a.detail-link
Capture And Compare    detail-page    ${OUTPUT}
Go Back
Capture And Compare    back-to-list    ${OUTPUT}
```

---

### Capture And Compare

Captures full-page screenshots of both browsers, generates a diff image, writes
a `result.json`, and returns the percentage of differing pixels.

| Argument | Type | Default | Description |
|---|---|---|---|
| `name` | str | *required* | Step name (used as subfolder name) |
| `output_dir` | str | *required* | Root output directory |
| `wait` | float | session default | Seconds to wait before capturing (overrides the value set in `Open Versions`) |
| `threshold` | int | `20` | Colour delta (0–255) below which a pixel is considered identical, to absorb anti-aliasing noise |

**Output structure** — for each call, a folder `<output_dir>/<name>/` is
created containing:

| File | Description |
|---|---|
| `version_a.png` | Full-page screenshot from Firefox A |
| `version_b.png` | Full-page screenshot from Firefox B |
| `diff.png` | Amplified diff image (differences highlighted) |
| `result.json` | Structured comparison result |

**result.json fields:**

| Field | Type | Description |
|---|---|---|
| `step` | str | Step name |
| `url` | str | URL at capture time |
| `firefox_a` | str | Version string of Firefox A |
| `firefox_b` | str | Version string of Firefox B |
| `difference_percent` | float | Percentage of differing pixels (0.0 = identical) |
| `first_diff_y` | int \| null | First row (px) where >10 % of pixels differ — helps distinguish a layout shift from scattered noise |
| `image_width` | int | Compared image width (px) |
| `image_height` | int | Compared image height (px) |
| `threshold` | int | Threshold used |
| `screenshots` | object | Filenames of the three images |
| `generated_at` | str | ISO 8601 timestamp (UTC) |

**Return value:** the `difference_percent` as a float, usable directly in Robot
Framework assertions.

```robotframework
${diff}=    Capture And Compare    home    ${OUTPUT}
Should Be True    ${diff} < 1.0    Home page differs by ${diff}%

Capture And Compare    hero-section    ${OUTPUT}    wait=5.0    threshold=30
```

---

### Load Storage State

Injects cookies and localStorage from a JSON file into both browsers, then
reloads the pages. Use this to compare authenticated pages without logging in
interactively.

| Argument | Type | Default | Description |
|---|---|---|---|
| `path` | str | *required* | Path to the storage state JSON file (produced by `Save Storage State`) |

**Return value:** `True` if the file was loaded, `False` if the file was
missing (anonymous session — a warning is logged, execution continues).

Call **after** `Open Versions`, once the browsers are on the target domain.

```robotframework
Open Versions    https://example.com    ${FIREFOX_A}    ${FIREFOX_B}
Load Storage State    resources/env/auth.json
Capture And Compare    authenticated-home    ${OUTPUT}
```

See [authenticated-sessions.md](authenticated-sessions.md) for the full
capture-and-replay workflow.

---

### Close Versions

Closes both browsers and ends the dual session. Safe to call even if no session
is open.

No arguments.

```robotframework
[Teardown]    Close Versions
```

---

## Auth capture keywords

These keywords open a **single** Firefox window (visible by default) so you can
log in manually, then save the storage state for later replay with
`Load Storage State`.

### Open Auth Browser

Opens one Firefox browser on a URL.

| Argument | Type | Default | Description |
|---|---|---|---|
| `url` | str | *required* | URL to open |
| `firefox_binary` | str | *required* | Path to the Firefox binary |
| `headless` | bool | `False` | Run headless (set to `False` to log in manually) |
| `width` | int | `1280` | Window width (px) |
| `height` | int | `900` | Window height (px) |

```robotframework
Open Auth Browser    https://example.com/login    /usr/bin/firefox
Open Auth Browser    ${SITE}    ${FIREFOX}    headless=False
```

---

### Save Storage State

Saves the auth browser's cookies and localStorage to a JSON file.

| Argument | Type | Default | Description |
|---|---|---|---|
| `path` | str | *required* | Output path for the JSON file |

Requires `Open Auth Browser` to be called first.

```robotframework
Save Storage State    resources/env/auth.json
```

> **Security:** the output file contains session cookies. It is gitignored by
> default (`resources/env/`). Never commit or share it.

---

### Close Auth Browser

Closes the auth browser. Safe to call even if no auth browser is open.

No arguments.

```robotframework
[Teardown]    Close Auth Browser
```

---

## Full example

```robotframework
*** Settings ***
Library     selenium_screenshot_compare.ScreenshotCompareLibrary

*** Variables ***
${SITE}             https://example.com
${FIREFOX_A}        /usr/bin/firefox
${FIREFOX_B}        ./firefoxes/firefox-128esr/firefox
${AUTH_FILE}        resources/env/auth.json
${OUTPUT}           output/captures

*** Test Cases ***
Compare Homepage Rendering
    Open Versions    ${SITE}    ${FIREFOX_A}    ${FIREFOX_B}
    Load Storage State    ${AUTH_FILE}
    ${diff}=    Capture And Compare    home    ${OUTPUT}
    Should Be True    ${diff} < 1.0
    Click Element    css=a[href="/about"]
    ${diff}=    Capture And Compare    about    ${OUTPUT}
    Should Be True    ${diff} < 1.0
    [Teardown]    Close Versions
```
