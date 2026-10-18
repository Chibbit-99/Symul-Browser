#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
DESKTOP_DIR="$DATA_HOME/applications"
DESKTOP_FILE="$DESKTOP_DIR/symul-browser.desktop"
VENV="$REPO_ROOT/.venv"
PYTHON="${PYTHON:-python3}"

if [[ ! -f "$REPO_ROOT/main.py" || ! -f "$REPO_ROOT/requirements.txt" ]]; then
    echo "Error: run this script from a valid Symul Browser checkout." >&2
    exit 1
fi

for command_name in git "$PYTHON"; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Error: required command not found: $command_name" >&2
        exit 1
    fi
done

if ! "$PYTHON" -m venv --help >/dev/null 2>&1; then
    echo "Python venv support is missing. On Kubuntu/Ubuntu, run:" >&2
    echo "  sudo apt install python3-venv" >&2
    exit 1
fi

echo "==> Creating/updating the virtual environment"
if [[ ! -x "$VENV/bin/python" ]]; then
    "$PYTHON" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$REPO_ROOT/requirements.txt"

echo "==> Creating KDE application launcher"
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Symul Browser
GenericName=Web Browser
Comment=Experimental keyboard-first Qt WebEngine browser
Exec="$VENV/bin/python" "$REPO_ROOT/main.py" %U
Path=$REPO_ROOT
Icon=$REPO_ROOT/icon.png
Terminal=false
Categories=Network;WebBrowser;
StartupNotify=true
StartupWMClass=symul-browser
EOF
chmod 644 "$DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo
echo "Symul Browser is installed."
echo "Source:   $REPO_ROOT"
echo "Python:   $VENV/bin/python"
echo "Launcher: $DESKTOP_FILE"
echo "Launch Symul Browser from your application menu."
echo "To update later, close the browser and run: $REPO_ROOT/update.sh"
