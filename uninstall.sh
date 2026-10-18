#!/usr/bin/env bash
set -Eeuo pipefail

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
DESKTOP_DIR="$DATA_HOME/applications"
DESKTOP_FILE="$DESKTOP_DIR/symul-browser.desktop"
REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

echo "This removes Symul Browser's application launcher and local Python virtual environment."
echo "It keeps the Git checkout and personal browser profile."
if [[ ! -r /dev/tty ]]; then
    echo "No interactive terminal available; refusing to uninstall without confirmation." >&2
    exit 1
fi
read -r -p "Continue? [y/N] " answer </dev/tty
case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Cancelled."; exit 0 ;;
esac

rm -f -- "$DESKTOP_FILE"
rm -rf -- "$REPO_ROOT/.venv"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo "Symul Browser has been uninstalled."
echo "Source checkout retained at: $REPO_ROOT"
echo "Personal browser profile was not touched."
