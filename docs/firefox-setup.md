# Getting a second Firefox binary

To compare two **versions**, you need two distinct binaries. Grab the build
**for your OS** (a specific ESR release, for example), without touching the
system Firefox.

All versions: <https://ftp.mozilla.org/pub/firefox/releases/>

The `firefoxes/` folder is gitignored (heavy binary, ~90 MB).

## Linux

```bash
mkdir -p firefoxes && cd firefoxes
wget "https://ftp.mozilla.org/pub/firefox/releases/128.0esr/linux-x86_64/en-US/firefox-128.0esr.tar.bz2"
tar xjf firefox-128.0esr.tar.bz2 && mv firefox firefox-128esr
# -> binary: firefoxes/firefox-128esr/firefox
```

## Windows

> Do **not** grab the `.tar.bz2`: it's the Linux build. Download the
> `.exe` installer instead.

Download `Firefox Setup 128.0esr.exe` from
<https://ftp.mozilla.org/pub/firefox/releases/128.0esr/win64/en-US/>, then
install silently into a dedicated folder:

```powershell
& ".\Firefox Setup 128.0esr.exe" /S /InstallDirectoryPath="C:\ff128esr"
& "C:\ff128esr\firefox.exe" --version
```

## macOS

Mount the `.dmg` for the desired version and copy the app under another name.
The binary lives at `Firefox.app/Contents/MacOS/firefox`.
