# Symul Browser

**Symul Browser** is an experimental, keyboard-first desktop browser built with **Python, PySide6, and Qt WebEngine**. The first prototype focuses on page loading and navigation, with a hidden tab strip and keyboard controls.

> **Status:** Early prototype. It is an experimental test browser, not yet a polished daily-driver replacement. Chrome extension support and the planned custom tab switcher are not implemented yet.

## Current prototype

- Qt WebEngine page rendering
- Address bar with URL navigation and DuckDuckGo search
- Back, forward, reload, and page title
- Multiple tabs without a permanent visible tab strip
- Persistent browser profile for cookies/site storage
- Keyboard shortcuts:
  - `Ctrl+T` — new tab
  - `Ctrl+W` — close current tab
  - `Ctrl+L` — focus the address bar
  - `Ctrl+Tab` / `Ctrl+Shift+Tab` — switch tabs
  - `Ctrl+Q` — quit

Because the tab strip is hidden, use the keyboard shortcuts to navigate between tabs.

## Quick install (Linux x86_64)

GitHub Actions builds the application and uploads the finished bundle to a GitHub Release. The installer downloads that prebuilt bundle; it does **not** install Python, PySide6, or PyInstaller or compile the app on your computer.

Copy and paste this command to install without cloning the repository:

```bash
sudo apt update
sudo apt install -y curl tar
curl -fsSL 'https://raw.githubusercontent.com/Chibbit-99/Symul-Browser/main/install.sh?cache=1' | bash
```

The installer uses **curl only**—it does not use `aria2`. It downloads over HTTP/1.1 and retries transient failures automatically. Before installing, it checks that the downloaded archive is valid, so a truncated or corrupt download is rejected. The approximately 309 MB bundle is followed by spinner indicators while extracting and copying the application files.

### When is the downloadable build updated?

- **Push to `main`:** GitHub Actions builds the app and updates the rolling `main` release.
- **Publish a GitHub Release:** GitHub Actions builds the release tag and attaches the archive to that versioned release.

The installer downloads the rolling `main` build. To install a specific published version instead, download `symul-browser-linux-x86_64.tar.gz` from that version's GitHub Release and extract it manually.

### What the installer does

1. Checks that the machine is Linux x86_64 and that `curl` and `tar` are available.
2. Downloads `symul-browser-linux-x86_64.tar.gz` from the project's rolling `main` GitHub Release with curl retries and visible progress.
3. Verifies the downloaded archive before extracting it.
4. Installs the prebuilt application to `~/.local/share/symul-browser/app/` (or the equivalent under `$XDG_DATA_HOME`).
5. Creates `~/.local/share/applications/symul-browser.desktop`, so **Symul Browser** appears in the KDE application menu.

No Python, pip, virtual environment, or PyInstaller build is needed on the target computer. The bundle is built on Ubuntu 24.04 and may still require compatible system libraries on the Linux distribution where it runs.

**If installation says the build cannot be downloaded**, the first successful GitHub Actions build must finish before the rolling `main` release exists. Check the [Actions page](https://github.com/Chibbit-99/Symul-Browser/actions).

## Uninstall

Copy and paste this command to uninstall without cloning the repository:

```bash
curl -fsSL https://raw.githubusercontent.com/Chibbit-99/Symul-Browser/main/uninstall.sh | bash
```

The uninstaller asks for confirmation and removes the installed application and application-menu entry. It **does not delete your source checkout or personal browser profile data**.

## Development

To run from source:

```bash
sudo apt install python3 python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PySide6
python main.py
```

To build locally (optional):

```bash
python -m pip install PyInstaller
python -m PyInstaller --clean --noconfirm --windowed --onedir --name Symul-Browser --collect-all PySide6 --collect-all shiboken6 --distpath dist --workpath build --specpath build main.py
```

## Planned architecture

The long-term goal is to keep the permanent tab bar hidden while providing a custom, keyboard-driven tab switcher. The prototype currently uses keyboard shortcuts for tab creation and switching; the switcher UI is a future step.

```text
Symul Browser
├── PySide6 / Qt Widgets
│   ├── Main window and navigation controls
│   ├── Keyboard shortcuts
│   └── Future custom tab switcher
├── Tab management
│   └── One QWebEngineView per tab
├── Qt WebEngine
│   └── Shared QWebEngineProfile
└── Future settings and extension integration
```

Qt WebEngine is Chromium-based, but it is **not full Google Chrome**. Extension support is not implemented in this prototype, and future support will depend on the Qt WebEngine APIs and the extensions being tested. Do not assume that every Chrome Web Store extension will work.

## Roadmap

- [x] Basic browser window and web page rendering
- [x] Address bar, back/forward, and reload
- [x] Hidden tab strip and keyboard tab controls
- [x] Cloud Linux build workflow and prebuilt-bundle installer (first successful build still needs verification)
- [ ] Custom keyboard-driven tab switcher
- [ ] Settings UI and profile controls
- [ ] Investigate Qt WebEngine extension APIs
- [ ] Test packaging and runtime dependencies on clean Kubuntu installations

**Core design principle:** use Qt WebEngine for page rendering; use PySide6 to own the browser interface and tab behaviour.
