# Windows notes

Three differences compared to Linux:

## 1. venv executables

Executables live in `.venv\Scripts\` (not `.venv/bin/`):

```powershell
python -m venv .venv
.\.venv\Scripts\pip.exe install selenium-screenshot-compare[robot]
```

Or activate the venv once:

```powershell
.\.venv\Scripts\Activate.ps1   # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 2. Firefox paths

Use forward slashes `/` in Robot Framework (`\` is an escape character):

```powershell
# System Firefox (via the registry)
(Get-ItemProperty "HKLM:\SOFTWARE\Mozilla\Mozilla Firefox\*\Main")."PathToExe"

# Second Firefox: install a specific version into a separate folder
& ".\Firefox Setup 128.0esr.exe" /S /InstallDirectoryPath="C:\ff128esr"
```

## 3. Running the suite

```powershell
.\.venv\Scripts\robot.exe `
  --variable "FIREFOX_A:C:/Program Files/Mozilla Firefox/firefox.exe" `
  --variable "FIREFOX_B:C:/ff128esr/firefox.exe" `
  --outputdir output/robot `
  tests/interactive_navigation.robot
```

> If you get `NoSuchDriverException: Unable to obtain driver for firefox`,
> check that `& "<path>" --version` responds for each Firefox path — the
> defaults are Linux paths.
