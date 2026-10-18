# Symul Browser

**Symul Browser** is an experimental, keyboard-first desktop browser built with **Python, PySide6, and Qt WebEngine**. The first prototype focuses on reliable page loading and navigation, with a hidden tab strip and keyboard controls.

> **Status:** Early prototype. It is a test browser, not yet a polished daily-driver replacement. Chrome extension support and the planned custom tab switcher are not implemented yet.

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

The Linux bundle is built in the cloud by GitHub Actions. Installing does **not** create a Python virtual environment or install PySide6/PyInstaller on your computer; it downloads the prebuilt bundle and adds a KDE application-menu entry.

Copy and paste:

```bash
set -e
sudo apt update
sudo apt install -y git curl tar
git clone https://github.com/Chibbit-99/Symul-Browser.git
cd Symul-Browser
chmod +x install.sh uninstall.sh
./install.sh
```

You can make a fork on GitHub first and clone your fork instead. The installer currently downloads the published upstream nightly binary. A fork's own source changes will only be included in its binary after its GitHub Actions workflow has run and published that fork's nightly release.

### What the installer does

1. Checks that the machine is Linux x86_64 and that `curl` and `tar` are available.
2. Downloads `symul-browser-linux-x86_64.tar.gz` from the project's GitHub nightly release.
3. Extracts the prebuilt application to `~/.local/share/symul-browser/app/` (or the equivalent under `$XDG_DATA_HOME`).
4. Creates `~/.local/share/applications/symul-browser.desktop`, so **Symul Browser** appears in the application menu.

No Python, pip, virtual environment, or PyInstaller build is needed on the target computer. The bundle is built on Ubuntu 24.04 and may still require compatible system libraries on the Linux distribution where it runs.

**If installation says the nightly build cannot be downloaded**, the GitHub Actions workflow may not have run successfully yet. Check the [Actions page](https://github.com/Chibbit-99/Symul-Browser/actions) and wait for a successful build/release.

## Uninstall

From the source checkout:

```bash
./uninstall.sh
```

The uninstaller asks for confirmation, removes the installed application and application-menu entry, and cleans up any old build files left by previous versions of the installer. It **does not delete your source checkout or personal browser profile data**.

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
- [x] Cloud Linux build workflow and prebuilt-bundle installer (pending first successful release)
- [ ] Custom keyboard-driven tab switcher
- [ ] Settings UI and profile controls
- [ ] Investigate Qt WebEngine extension APIs
- [ ] Test packaging and runtime dependencies on clean Kubuntu installations

**Core design principle:** use Qt WebEngine for page rendering; use PySide6 to own the browser interface and tab behaviour.
