# Symul Browser

**Symul Browser** is a compact desktop web browser built with Python, PySide6 and Qt WebEngine. The browser chrome is based directly on `resources/Browser UI.html`, with its SVG icons, CSS geometry, adaptive light/dark colours, rounded omnibox, tab-switcher popup and bookmarks row.

The HTML prototype is rendered as the live browser chrome and connected to real Qt WebEngine tabs using Qt WebChannel. The web page itself remains a real browser view, not the prototype’s placeholder content.

## Features

- Chromium-based rendering through Qt WebEngine
- Rounded address/search bar: enter a URL or search DuckDuckGo
- Back, forward, reload and home controls
- HTML tab-switcher popup with close buttons and new-tab action
- Tabs can also be switched from the tab switcher or keyboard shortcuts
- Pop-up links routed into a new Symul tab
- Persistent cookies, cache and site storage between launches
- Save-page downloads with a save-location prompt
- Bookmarks saved locally, shown in the toolbar bookmark row, and accessible from the browser menu
- Toolbar shortcuts for loaded local extensions and downloads
- Current-tab browsing history menu
- Find-in-page bar, page zoom controls and fullscreen
- Native desktop launcher and window identity for KDE taskbar pinning

## Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Alt+T` | New tab |
| `Ctrl+W` | Close current tab |
| `Ctrl+L` | Focus and select the address bar |
| `Ctrl+Tab` | Next tab |
| `Ctrl+Shift+Tab` | Previous tab |
| `Ctrl+R` | Reload |
| `Alt+Left` / `Alt+Right` | Back / forward |
| `Alt+Home` | Open home page |
| `Ctrl+F` | Find in page |
| `Ctrl++` / `Ctrl+-` | Zoom in / out |
| `Ctrl+0` | Reset zoom |
| `F11` | Toggle fullscreen |
| `Ctrl+Q` | Quit |

## Install on Kubuntu / Ubuntu

Install prerequisites:

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip
```

Clone and install:

```bash
mkdir -p ~/Applications
git clone https://github.com/Chibbit-99/Symul-Browser.git ~/Applications/Symul-Browser
cd ~/Applications/Symul-Browser
bash install.sh
```

The installer creates a local `.venv`, installs PySide6, and writes a launcher to `~/.local/share/applications/`. Launch **Symul Browser** from the application menu or run:

```bash
.venv/bin/python main.py
```

The first install downloads Qt/PySide6 components and may take a while. The installer does not need `sudo`.

## Update

Close Symul first, then:

```bash
cd ~/Applications/Symul-Browser
bash update.sh
```

The updater fast-forwards the Git checkout and refreshes dependencies. If you have local edits, commit or stash them before updating; it will not force-reset your work.

## Uninstall

```bash
cd ~/Applications/Symul-Browser
bash uninstall.sh
```

The uninstaller removes the desktop launcher and virtual environment, but keeps the repository and personal browser data. Delete the repository manually if you also want to remove the source.

## Browser data

Symul stores its persistent profile, cache and bookmarks in the application-data directory chosen by Qt (normally under `~/.local/share/`). Cookies and site storage persist across launches. Bookmarks are stored in `bookmarks.json`.

## Current limitations

- Symul uses Qt WebEngine, which is Chromium-based but is not Google Chrome itself.
- Chrome Web Store extensions are not supported by this app at present.
- Private browsing, sync, a persistent global history page, and a dedicated downloads manager are not implemented.
- Some websites may behave differently from Chrome because Qt WebEngine and its bundled Chromium version differ.

## Development

```bash
sudo apt install python3 python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m py_compile main.py
.venv/bin/python main.py
```

**Design principle:** the page renderer is Qt WebEngine; Symul owns the browser chrome, navigation and tab workflow.
