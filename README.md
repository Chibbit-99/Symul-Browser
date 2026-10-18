# Symul Browser

**Symul Browser** is an experimental, keyboard-first desktop web browser built with Python, PySide6, and Qt WebEngine. Its tab strip stays hidden so the browser can keep its interface compact and let keyboard shortcuts handle tab navigation.

> **Status:** Early prototype. It is not yet intended as a polished daily-driver replacement. Chrome extension support and a custom tab switcher are not implemented.

## Features

- Chromium-based page rendering through Qt WebEngine
- Address bar that opens URLs or searches DuckDuckGo
- Back, forward, and reload controls
- Multiple tabs with no permanent visible tab strip
- Persistent browser profile for cookies and site storage
- Keyboard shortcuts:
  - `Ctrl+T` — new tab
  - `Ctrl+W` — close tab
  - `Ctrl+L` — focus the address bar
  - `Ctrl+Tab` — next tab
  - `Ctrl+Shift+Tab` — previous tab
  - `Ctrl+Q` — quit

## Install on Linux

Symul is installed directly from its Git repository. There is no large prebuilt archive to download, no separate copy of the application to keep in sync, and no GitHub Actions build required. The repository you clone is the application installation.

### 1. Install system prerequisites

On Kubuntu or Ubuntu:

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip
```

### 2. Clone the repository and install

```bash
mkdir -p ~/Applications
git clone https://github.com/Chibbit-99/Symul-Browser.git ~/Applications/Symul-Browser
cd ~/Applications/Symul-Browser
bash install.sh
```

The installer creates a local `.venv`, installs Python dependencies into it, and creates a desktop entry in `~/.local/share/applications/` (or the equivalent under `$XDG_DATA_HOME`). The desktop entry points directly to `main.py` in this checkout.

Launch **Symul Browser** from your KDE application launcher. You can also run it from the repository with:

```bash
.venv/bin/python main.py
```

The first installation downloads PySide6 and its Qt components, so it may take a while and use several hundred megabytes of disk space. No `sudo` is needed for the installer.

## Update

Close Symul Browser before updating, then run:

```bash
cd ~/Applications/Symul-Browser
bash update.sh
```

The updater fetches and fast-forwards the current Git branch, then refreshes the virtual environment's dependencies. You can also run `git pull --ff-only` yourself, but `update.sh` additionally updates dependencies.

If you edited tracked files locally, commit or stash those changes before updating. Git will refuse to fast-forward if the checkout has diverged; the updater will not force-reset or overwrite your local work.

## Uninstall

From the repository:

```bash
./uninstall.sh
```

The uninstaller asks for confirmation and removes Symul's desktop launcher and virtual environment. It **keeps the Git checkout and your personal browser profile**. To remove the source code as well, delete the checkout manually after uninstalling, for example:

```bash
rm -rf ~/Applications/Symul-Browser
```

Your personal browser profile is separate from the repository and is not removed by these commands.

## Development

The application uses Python 3 and PySide6. To run from source without installing a desktop launcher:

```bash
sudo apt install python3 python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

To check Python syntax without launching the browser:

```bash
.venv/bin/python -m py_compile main.py
```

## Project structure

```text
Symul-Browser/
├── main.py          # Browser window, navigation, and tab handling
├── requirements.txt # Python runtime dependencies
├── install.sh       # Creates the virtual environment and desktop entry
├── update.sh        # Fast-forward Git update and dependency refresh
├── uninstall.sh     # Removes the launcher and virtual environment
└── README.md
```

## Roadmap

- [x] Basic browser window and page rendering
- [x] Address bar, back/forward, and reload
- [x] Hidden tab strip and keyboard tab controls
- [x] Git-based installation and updates
- [ ] Custom keyboard-driven tab switcher
- [ ] Settings UI and profile controls
- [ ] Investigate Qt WebEngine extension APIs
- [ ] Test on clean Kubuntu installations

## Notes

Qt WebEngine is Chromium-based, but it is not the full Google Chrome browser. Extension support is not implemented, and Chrome Web Store extensions should not be assumed to work.

**Design principle:** Qt WebEngine renders pages; PySide6 owns the browser interface and tab behaviour.
