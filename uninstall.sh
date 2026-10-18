#!/usr/bin/env bash
set -Eeuo pipefail

APP_ID="symul-browser"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/symul-browser"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"

echo "This removes the installed Symul Browser and its application-menu entry."
echo "It will not delete your source checkout or personal browser profile data."
read -r -p "Continue? [y/N] " answer
case "$answer" in
    y|Y|yes|YES) ;;
    *) echo "Cancelled."; exit 0 ;;
esac

rm -rf -- "$INSTALL_DIR"
rm -f -- "$DESKTOP_FILE"

# Also clean up build files left by older source-based installers.
rm -rf -- "$SCRIPT_DIR/.venv" "$SCRIPT_DIR/build" "$SCRIPT_DIR/dist" "$SCRIPT_DIR/__pycache__" "$SCRIPT_DIR/Symul-Browser.spec"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo "Symul Browser has been uninstalled."
