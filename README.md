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

## Install on Linux x86_64

You can either download the prebuilt archive yourself and install it with the script below, or use the automatic installer.

### Option 1: Download manually, then install

**[Download Symul Browser for Linux (x86_64) — approximately 309 MB](https://github.com/Chibbit-99/Symul-Browser/releases/download/main/symul-browser-linux-x86_64.tar.gz)**

The archive is named `symul-browser-linux-x86_64.tar.gz`. Download it using your browser, then copy and paste the following into a terminal. The script looks for the archive in the current directory or your `~/Downloads` folder, validates it, and installs the bundled application. You do not need Python, pip, PySide6, PyInstaller, curl, or a compiler.

```bash
set -Eeuo pipefail

ARCHIVE="$PWD/symul-browser-linux-x86_64.tar.gz"
if [[ ! -f "$ARCHIVE" && -f "$HOME/Downloads/symul-browser-linux-x86_64.tar.gz" ]]; then
    ARCHIVE="$HOME/Downloads/symul-browser-linux-x86_64.tar.gz"
fi

if [[ ! -f "$ARCHIVE" ]]; then
    echo "Could not find symul-browser-linux-x86_64.tar.gz." >&2
    echo "Put the downloaded archive in ~/Downloads or run this from its folder." >&2
    exit 1
fi

case "$(uname -m)" in
    x86_64|amd64) ;;
    *)
        echo "This prebuilt bundle supports Linux x86_64 only." >&2
        exit 1
        ;;
esac

command -v tar >/dev/null 2>&1 || {
    echo "The 'tar' command is required." >&2
    exit 1
}

echo "==> Checking downloaded archive"
tar -tzf "$ARCHIVE" >/dev/null

TMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TMP_DIR"' EXIT
echo "==> Extracting application"
tar -xzf "$ARCHIVE" -C "$TMP_DIR"

SOURCE_DIR="$TMP_DIR/Symul-Browser"
if [[ ! -x "$SOURCE_DIR/Symul-Browser" ]]; then
    echo "The archive does not contain the expected Symul-Browser executable." >&2
    exit 1
fi

INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/symul-browser"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
STAGING_DIR="$INSTALL_DIR/app.new"

echo "==> Installing to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR" "$DESKTOP_DIR"
rm -rf -- "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
cp -a "$SOURCE_DIR/." "$STAGING_DIR/"
chmod +x "$STAGING_DIR/Symul-Browser"
rm -rf -- "$INSTALL_DIR/app"
mv -- "$STAGING_DIR" "$INSTALL_DIR/app"

cat > "$DESKTOP_DIR/symul-browser.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Symul Browser
GenericName=Web Browser
Comment=Experimental keyboard-first Qt WebEngine browser
Exec="$INSTALL_DIR/app/Symul-Browser" %U
Icon=web-browser
Terminal=false
Categories=Network;WebBrowser;
StartupNotify=true
EOF
chmod 644 "$DESKTOP_DIR/symul-browser.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo
echo "Symul Browser installed successfully."
echo "Launch it from the KDE application menu."
echo "Executable: $INSTALL_DIR/app/Symul-Browser"
```

### Option 2: Automatic installer

If you prefer the terminal to download the archive for you, copy and paste:

```bash
sudo apt update
sudo apt install -y curl tar
curl -fsSL 'https://raw.githubusercontent.com/Chibbit-99/Symul-Browser/main/install.sh' | bash
```

This uses curl (not aria2), retries interrupted downloads, and validates the archive before installing. If your connection repeatedly drops during the large download, use Option 1 to download the archive in your browser instead.

### Where to get other versions

The manual download above follows the rolling `main` build. For a specific published version, open the [GitHub Releases page](https://github.com/Chibbit-99/Symul-Browser/releases) and download `symul-browser-linux-x86_64.tar.gz` from the release you want.

### What gets installed?

- Application files: `~/.local/share/symul-browser/app/` (or the equivalent under `$XDG_DATA_HOME`)
- KDE application menu entry: `~/.local/share/applications/symul-browser.desktop` (or the equivalent under `$XDG_DATA_HOME`)

The prebuilt bundle is built on Ubuntu 24.04 and may still require compatible system libraries on the Linux distribution where it runs.

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
- [x] Cloud Linux build workflow and prebuilt-bundle installer
- [ ] Custom keyboard-driven tab switcher
- [ ] Settings UI and profile controls
- [ ] Investigate Qt WebEngine extension APIs
- [ ] Test packaging and runtime dependencies on clean Kubuntu installations

**Core design principle:** use Qt WebEngine for page rendering; use PySide6 to own the browser interface and tab behaviour.
