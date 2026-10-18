#!/usr/bin/env bash
set -Eeuo pipefail

APP_ID="symul-browser"
REPO="Chibbit-99/Symul-Browser"
ASSET="symul-browser-linux-x86_64.tar.gz"
# The rolling main build is updated after each successful push to main.
RELEASE_URL="https://github.com/$REPO/releases/download/main/$ASSET"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/symul-browser"
BIN_DIR="$INSTALL_DIR/app"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf -- "$TMP_DIR"' EXIT

run_with_spinner() {
    local message="$1"
    shift
    local spinner='|/-\\'
    local i=0
    "$@" &
    local pid=$!
    while kill -0 "$pid" 2>/dev/null; do
        printf '\r%s %s' "$message" "${spinner:i%4:1}"
        i=$((i + 1))
        sleep 0.12
    done
    if wait "$pid"; then
        printf '\r%s done.\n' "$message"
    else
        local status=$?
        printf '\r%s failed.\n' "$message" >&2
        return "$status"
    fi
}

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

echo "==> Downloading the prebuilt Symul Browser Linux bundle (~309 MB)"
if command -v aria2c >/dev/null 2>&1; then
    echo "Using aria2 with up to 8 parallel connections for a faster download."
    if ! aria2c \
        --max-connection-per-server=8 \
        --split=8 \
        --min-split-size=1M \
        --max-tries=5 \
        --retry-wait=2 \
        --continue=true \
        --summary-interval=1 \
        --console-log-level=warn \
        --download-result=hide \
        --dir="$TMP_DIR" \
        --out="$ASSET" \
        "$RELEASE_URL"; then
        echo >&2
        echo "Could not download the latest main-branch build." >&2
        echo "Check that the GitHub Actions build succeeded:" >&2
        echo "https://github.com/$REPO/actions" >&2
        exit 1
    fi
else
    echo "Tip: install aria2 for parallel downloads: sudo apt install aria2"
    echo "Using curl with HTTP/1.1 and automatic retries."
    if ! curl --http1.1 --fail --location --retry 5 --retry-all-errors --retry-delay 2 --connect-timeout 30 --show-error --progress-bar "$RELEASE_URL" -o "$TMP_DIR/$ASSET"; then
        echo >&2
        echo "Could not download the latest main-branch build." >&2
        echo "Check that the GitHub Actions build succeeded:" >&2
        echo "https://github.com/$REPO/actions" >&2
        exit 1
    fi
fi

echo "==> Extracting application bundle"
run_with_spinner "Extracting archive" tar -xzf "$TMP_DIR/$ASSET" -C "$TMP_DIR"
if [[ ! -x "$TMP_DIR/Symul-Browser/Symul-Browser" ]]; then
    echo "Error: downloaded archive did not contain the expected executable." >&2
    exit 1
fi

echo "==> Installing application to $INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"
# Stage the new app before replacing the current installation.
STAGING_DIR="$INSTALL_DIR/app.new"
rm -rf -- "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
run_with_spinner "Copying application files" cp -a "$TMP_DIR/Symul-Browser/." "$STAGING_DIR/"
chmod +x "$STAGING_DIR/Symul-Browser"
rm -rf -- "$BIN_DIR"
mv -- "$STAGING_DIR" "$BIN_DIR"

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
echo "To uninstall, run:"
echo "  curl -fsSL https://raw.githubusercontent.com/$REPO/main/uninstall.sh | bash"
