#!/usr/bin/env bash
set -Eeuo pipefail

APP_ID="symul-browser"
APP_NAME="Symul Browser"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
BUILD_DIR="$SCRIPT_DIR/build"
DIST_DIR="$SCRIPT_DIR/dist"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/symul-browser"
BIN_DIR="$INSTALL_DIR/app"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required. Install python3 and python3-venv first." >&2
    exit 1
fi
if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "Error: Python venv support is missing. On Kubuntu/Ubuntu, install python3-venv." >&2
    exit 1
fi

echo "==> Creating/updating virtual environment"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip wheel
"$VENV_DIR/bin/python" -m pip install --upgrade PySide6 PyInstaller

echo "==> Building Symul Browser with PyInstaller"
rm -rf "$BUILD_DIR" "$DIST_DIR"
"$VENV_DIR/bin/python" -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "Symul-Browser" \
    --onedir \
    --collect-all PySide6 \
    --collect-all shiboken6 \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR" \
    "$SCRIPT_DIR/main.py"

if [[ ! -x "$DIST_DIR/Symul-Browser/Symul-Browser" ]]; then
    echo "Error: PyInstaller did not produce the expected executable." >&2
    exit 1
fi

echo "==> Installing application files to $INSTALL_DIR"
mkdir -p "$BIN_DIR" "$DESKTOP_DIR"
rm -rf "$BIN_DIR/Symul-Browser"
cp -a "$DIST_DIR/Symul-Browser/." "$BIN_DIR/"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Symul Browser
GenericName=Web Browser
Comment=Experimental keyboard-first Qt WebEngine browser
Exec="$BIN_DIR/Symul-Browser" %U
Icon=web-browser
Terminal=false
Categories=Network;WebBrowser;
StartupNotify=true
EOF
chmod 644 "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo
echo "Installed successfully."
echo "Launch it from the application menu by searching for: Symul Browser"
echo "Executable: $BIN_DIR/Symul-Browser"
echo "To uninstall: run ./uninstall.sh from this repository checkout."
