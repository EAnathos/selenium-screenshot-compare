# Authenticated sessions (storage state)

To compare pages behind a login, first capture a session (cookies +
localStorage) with your Firefox, then replay it in both versions — no need to
re-authenticate.

## 1. Capture

Run `capture_auth.robot` — it opens a visible Firefox window and gives you
time to log in manually:

```bash
robot --outputdir output/robot tests/capture_auth.robot
```

This writes `resources/env/auth.json`.

Variables: `SITE`, `FIREFOX`, `LOGIN_WAIT` (seconds to log in), `HEADLESS`.

> `resources/env/` is **gitignored**: `auth.json` contains session cookies
> (secrets) and must **never** be committed or shared.

## 2. Reuse

`interactive_navigation.robot` calls `Load Storage State ${AUTH_FILE}` right
after `Open Versions`. If `auth.json` exists, both versions start logged in;
otherwise a warning is logged and the session stays anonymous.

## Python API

```python
from selenium_screenshot_compare import DualSession
from pathlib import Path

session = DualSession("/usr/bin/firefox", "./firefoxes/firefox-128esr/firefox")
session.open("https://example.com")
session.load_storage(Path("resources/env/auth.json"))
# both browsers are now authenticated
```
