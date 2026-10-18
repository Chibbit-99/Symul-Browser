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

## Quick start: fork, clone, and install

**Git can clone repositories, but it cannot create a GitHub fork by itself.** To make your own fork, first open the repository on GitHub and click **Fork**:

`https://github.com/Chibbit-99/Symul-Browser`

Then copy-paste this script into a terminal, replacing `YOUR_GITHUB_USERNAME` with your GitHub username. It uses plain Git to clone your fork and runs the installer:

```bash
set -e
git clone https://github.com/YOUR_GITHUB_USERNAME/Symul-Browser.git
cd Symul-Browser
chmod +x install.sh uninstall.sh
./install.sh
```

If you **don't need your own fork**, you can clone the original repository directly instead:

```bash
set -e
git clone https://github.com/Chibbit-99/Symul-Browser.git
cd Symul-Browser
chmod +x install.sh uninstall.sh
./install.sh
```

## Install manually

Requirements: Linux desktop, Python 3, `python3-venv`, and an internet connection for downloading Python packages.

```bash
sudo apt update
sudo apt install git python3 python3-venv
git clone https://github.com/Chibbit-99/Symul-Browser.git
cd Symul-Browser
chmod +x install.sh uninstall.sh
./install.sh
```

The installer:
1. Creates a `.venv` in the repository.
2. Installs PySide6 and PyInstaller into that environment.
3. Builds a **PyInstaller onedir bundle**.
4. Installs the bundle under `~/.local/share/symul-browser/app/`.
5. Adds a `.desktop` launcher to `~/.local/share/applications/`, so **Symul Browser** appears in the application menu.

On Linux, PyInstaller produces a Linux executable, not a Windows `.exe`. The build is intended for the Linux machine and architecture on which it is created; it is not a cross-platform package. The bundled Qt WebEngine may still rely on system libraries provided by the Linux distribution.

Launch Symul Browser from the desktop application menu, or run:

```bash
~/.local/share/symul-browser/app/Symul-Browser
```

## Uninstall

From the same source checkout:

```bash
./uninstall.sh
```

The uninstaller asks for confirmation, removes the installed app and application-menu entry, and deletes generated build/virtual-environment files (`.venv`, `build/`, and `dist/`) from that checkout. It **does not delete your source checkout**. It also does not remove your personal browser profile or browsing data.

## Development

To run directly without packaging:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PySide6
python main.py
```

Build manually (the installer does this for you):

```bash
.venv/bin/python -m pip install PyInstaller
.venv/bin/python -m PyInstaller --clean --noconfirm --windowed --onedir --name Symul-Browser --collect-all PySide6 --collect-all shiboken6 main.py
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
- [x] PyInstaller build and desktop-menu installer
- [ ] Custom keyboard-driven tab switcher
- [ ] Settings UI and profile controls
- [ ] Investigate Qt WebEngine extension APIs
- [ ] Test packaging and runtime dependencies on clean Kubuntu installations

**Core design principle:** use Qt WebEngine for page rendering; use PySide6 to own the browser interface and tab behaviour.
