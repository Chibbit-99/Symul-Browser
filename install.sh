#!/usr/bin/env bash
set -Eeuo pipefail

APP_ID="symul-browser"
REPO="Chibbit-99/Symul-Browser"
ASSET="symul-browser-linux-x86_64.tar.gz"
RELEASE_URL="https://github.com/$REPO/releases/download/nightly/$ASSET"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/symul-browser"
BIN_DIR="$INSTALL_DIR/app"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TMP_DIR"' EXIT

case "$(uname -m)" in
    x86_64|amd64) ;;
    *)
        echo "Error: the prebuilt release currently supports Linux x86_64 only." >&2
        echo "Detected architecture: $(uname -m)" >&2
        exit 1
        ;;
esac

for command_name in curl tar; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Error: '$command_name' is required. On Kubuntu/Ubuntu, run:" >&2
        echo "  sudo apt install curl tar" >&2
        exit 1
    fi
done

echo "==> Downloading the prebuilt Symul Browser Linux bundle"
if ! curl --fail --location --retry 3 --silent --show-error "$RELEASE_URL" -o "$TMP_DIR/$ASSET"; then
    echo >&2
    echo "Could not download the nightly build." >&2
    echo "The GitHub Actions build may not have finished yet:" >&2
    echo "https://github.com/$REPO/actions" >&2
    exit 1
fi

echo "==> Extracting application bundle"
tar -xzf "$TMP_DIR/$ASSET" -C "$TMP_DIR"
if [[ ! -x "$TMP_DIR/Symul-Browser/Symul-Browser" ]]; then
    echo "Error: downloaded archive did not contain the expected executable." >&2
    exit 1
fi

echo "==> Installing application to $INSTALL_DIR"
mkdir -p "$BIN_DIR" "$DESKTOP_DIR"
rm -rf -- "$BIN_DIR"
mkdir -p "$BIN_DIR"
cp -a "$TMP_DIR/Symul-Browser/." "$BIN_DIR/"
chmod +x "$BIN_DIR/Symul-Browser"

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
echo "Launch Symul Browser from the KDE application menu."
echo "Executable: $BIN_DIR/Symul-Browser"
echo "To uninstall, run ./uninstall.sh from this source checkout."
