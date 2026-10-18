# Symul Browser

**Symul Browser** is an experimental, keyboard-first desktop browser built with **Python, PySide6, and Qt WebEngine**. The prototype focuses on page loading and navigation, with a hidden tab strip and keyboard controls.

> **Status:** Early prototype, not yet a polished daily-driver replacement. Chrome extension support and the planned custom tab switcher are not implemented yet.

## Features

- Qt WebEngine page rendering
- Address bar with URL navigation and DuckDuckGo search
- Back, forward, reload, and page title
- Multiple tabs without a permanent visible tab strip
- Persistent browser profile for cookies/site storage
- Keyboard shortcuts: `Ctrl+T` new tab · `Ctrl+W` close tab · `Ctrl+L` focus address bar · `Ctrl+Tab` / `Ctrl+Shift+Tab` switch tabs · `Ctrl+Q` quit

## Install on Linux x86_64

### 1. Download the archive

Open the **[GitHub Releases page](https://github.com/Chibbit-99/Symul-Browser/releases)** and download `symul-browser-linux-x86_64.tar.gz`. Save it in your **Downloads** folder. The archive is approximately 309 MB.

### 2. Copy and paste this into a terminal

This installs the archive you downloaded; it does **not** download the archive again. No Python, pip, PySide6, PyInstaller, curl, or compiler is required.

```bash
set -e
A="$HOME/Downloads/symul-browser-linux-x86_64.tar.gz"
test -f "$A" || { echo "Archive not found: $A"; exit 1; }
case "$(uname -m)" in x86_64|amd64) ;; *) echo "Linux x86_64 is required."; exit 1 ;; esac
tar -tzf "$A" >/dev/null
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
tar -xzf "$A" -C "$T"
S="$T/Symul-Browser"; test -x "$S/Symul-Browser" || { echo "Invalid archive contents."; exit 1; }
I="${XDG_DATA_HOME:-$HOME/.local/share}/symul-browser"
D="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$I/app.new" "$D"
cp -a "$S/." "$I/app.new/"
chmod +x "$I/app.new/Symul-Browser"
rm -rf "$I/app"; mv "$I/app.new" "$I/app"
printf '[Desktop Entry]\nVersion=1.0\nType=Application\nName=Symul Browser\nGenericName=Web Browser\nComment=Experimental keyboard-first Qt WebEngine browser\nExec="%s" %%U\nIcon=web-browser\nTerminal=false\nCategories=Network;WebBrowser;\nStartupNotify=true\n' "$I/app/Symul-Browser" > "$D/symul-browser.desktop"
chmod 644 "$D/symul-browser.desktop"
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$D" >/dev/null 2>&1 || true
command -v kbuildsycoca6 >/dev/null 2>&1 && kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
echo "Installed! Launch Symul Browser from the KDE application menu."
```

The script checks the archive, extracts the application, installs it to `~/.local/share/symul-browser/app/`, and creates a KDE application-menu entry. If you saved the archive somewhere other than Downloads, change the `A=` path in the script.

The prebuilt bundle is built on Ubuntu 24.04 and may require compatible system libraries on other Linux distributions.

## Uninstall

Copy and paste this command into a terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/Chibbit-99/Symul-Browser/main/uninstall.sh | bash
```

The uninstaller asks for confirmation and removes the installed application and menu entry. It **does not delete your personal browser profile data**.

## Development

Run from source:

```bash
sudo apt install python3 python3-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PySide6
python main.py
```

Optional local build:

```bash
python -m pip install PyInstaller
python -m PyInstaller --clean --noconfirm --windowed --onedir --name Symul-Browser --collect-all PySide6 --collect-all shiboken6 --distpath dist --workpath build --specpath build main.py
```

## Planned architecture

The long-term goal is to keep the permanent tab bar hidden while providing a custom, keyboard-driven tab switcher.

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

Qt WebEngine is Chromium-based, but it is **not full Google Chrome**. Extension support is not implemented in this prototype, and not every Chrome Web Store extension should be assumed to work.

## Roadmap

- [x] Basic browser window and web page rendering
- [x] Address bar, back/forward, and reload
- [x] Hidden tab strip and keyboard tab controls
- [x] Prebuilt Linux bundle
- [ ] Custom keyboard-driven tab switcher
- [ ] Settings UI and profile controls
- [ ] Investigate Qt WebEngine extension APIs
- [ ] Test on clean Kubuntu installations

**Core design principle:** use Qt WebEngine for page rendering; use PySide6 to own the browser interface and tab behaviour.
