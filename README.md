# Symul Browser

**Symul Browser** is a planned, keyboard-first desktop browser built with **Python, PySide6, and Qt WebEngine**. Its goal is to keep the web platform and extension support of an embedded Chromium engine while replacing the usual browser chrome with a compact, custom interface.

The central idea is simple: **hide the permanent tab strip without giving up tabs**. Tabs remain available through a keyboard-driven switcher, so more screen space can be used for the page itself.

> **Project status:** Planning / early development. The architecture below describes the intended design; features are not necessarily implemented yet.

## Goals

- Use Qt WebEngine instead of maintaining a custom Chromium fork.
- Provide a minimal browser UI with no permanently visible tab bar.
- Make opening, switching, and closing tabs convenient from the keyboard.
- Support browser extensions where Qt WebEngine's extension implementation allows them.
- Keep browser UI and browser-engine code separate so the interface can evolve independently.
- Target Linux desktops, especially KDE Plasma / Kubuntu, first.

## Planned technology

| Component | Planned choice | Responsibility |
| --- | --- | --- |
| Language | Python 3 | Application logic and UI behaviour |
| Desktop UI | PySide6 / Qt Widgets | Main window, address bar, menus, tab switcher |
| Browser engine | Qt WebEngine | Chromium-based page rendering and web platform |
| Page view | `QWebEngineView` | Display an individual web page |
| Browser context | `QWebEngineProfile` | Cookies, cache, persistent storage, and profile settings |
| Extension support | `QWebEngineExtensionManager` where available | Install and load supported extensions |
| Settings | JSON initially | User preferences and browser configuration |

The extension API requires a sufficiently recent Qt WebEngine/PySide6 build (the API is available in Qt 6.10+). The exact installed Qt WebEngine version and API availability must be checked during setup.

## Architecture

The application will be divided into a few small components:

```text
Symul Browser
├── Application / Main Window
│   ├── Address and navigation controls
│   ├── Page area
│   └── Keyboard shortcut dispatcher
├── Tab Manager
│   ├── Create and close tabs
│   ├── Track the active tab
│   └── Switch between pages
├── Tab Switcher
│   ├── Open from Ctrl+T
│   ├── Show existing tabs
│   └── Offer actions to switch, create, or close tabs
├── Browser Engine
│   ├── QWebEngineView per tab
│   ├── Shared QWebEngineProfile
│   └── Navigation, loading, and page signals
├── Extension Manager
│   ├── Discover/install supported extensions
│   └── Report unsupported or failed extensions
└── Settings
    ├── Browser preferences
    └── Persistent profile and extension configuration
```

This is a logical architecture, not a promise that every component already exists as a separate source file.

### Tabs without a permanent tab bar

Each tab will own a page view. The tab manager keeps track of those views and which one is active. The main window displays the active view, while the tab switcher provides access to the other tabs.

The intended interaction is:

- **Ctrl+T:** open Symul's tab switcher rather than immediately creating a conventional visible tab.
- From the switcher, choose an existing tab or create a new one.
- Provide actions to close tabs and show useful page information, such as the title and address.
- Keep the tab switcher keyboard-navigable, with a clear way to dismiss it without changing tabs.

The exact interaction can be refined as the UI is prototyped. The key requirement is that tabs stay accessible even though the permanent tab strip is hidden.

### Keyboard shortcuts

Symul will handle its own shortcuts at the application level. This avoids relying on a regular Chrome extension to override browser-reserved shortcuts such as `Ctrl+T`.

Initial shortcut plan:

| Shortcut | Intended action |
| --- | --- |
| `Ctrl+T` | Open the tab switcher |
| `Ctrl+L` | Focus and select the address bar |
| `Esc` | Dismiss the switcher or current transient UI |
| `Enter` in the address bar | Navigate to the entered URL or search query |

Additional shortcuts can be added once the basic navigation and tab workflow works.

## Extension support

Qt WebEngine is Chromium-based, but **it is not the same thing as running full Google Chrome**. Qt's extension implementation supports a subset of Chrome-extension behaviour and is limited to Manifest V3 in the relevant API. Some extensions may work; others may fail because they rely on Chrome APIs, browser UI, or integration points that Qt WebEngine does not provide.

Extension support will therefore be treated as a compatibility feature, not a guarantee that every Chrome Web Store extension will work.

Planned approach:

1. Check whether the installed PySide6/Qt WebEngine build exposes `QWebEngineExtensionManager`.
2. Build a minimal browser and confirm normal page loading before adding extensions.
3. Test extension installation and loading with a small, known-compatible Manifest V3 extension.
4. Surface installation/load errors rather than silently ignoring them.
5. Document tested extensions and known limitations as the project develops.

Qt WebEngine's Chromium version may lag behind the latest Chrome release. Qt integrates Chromium at its release cycle and may backport security fixes; it should not be assumed to match the newest Chrome version exactly.

## Proposed project layout

The source tree may begin with a structure like this:

```text
symul-browser/
├── README.md
├── requirements.txt
├── main.py
├── symul/
│   ├── app.py              # Application startup
│   ├── main_window.py      # Main browser window and controls
│   ├── tab_manager.py      # Tab lifecycle and active-tab state
│   ├── tab_switcher.py     # Keyboard-driven tab selection UI
│   ├── browser_page.py     # Page view and navigation signals
│   ├── shortcuts.py        # Application-level keyboard shortcuts
│   ├── extensions.py       # Qt WebEngine extension integration
│   └── settings.py         # Preferences and configuration
└── tests/
    ├── test_tab_manager.py
    └── test_settings.py
```

This layout is a starting proposal and can be adjusted to match the implementation.

## Development setup

On a Linux system with Python 3 installed:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PySide6
```

Start with a small smoke test that imports `QWebEngineView` and opens a basic window. Before implementing extension features, check whether the installed build provides the extension manager:

```bash
python - <<'PY'
import PySide6
print("PySide6:", PySide6.__version__)

try:
    from PySide6.QtWebEngineCore import QWebEngineExtensionManager
    print("Qt WebEngine extension manager: available")
except ImportError as error:
    print("Qt WebEngine extension manager: unavailable")
    print(error)
PY
```

If the extension manager is unavailable, use a PySide6/Qt WebEngine package version that includes the required API before working on extension support. Installing PySide6 alone does not make every Chrome extension compatible.

## Development milestones

- [ ] **1. Browser shell:** launch a window and render a web page.
- [ ] **2. Navigation:** address bar, back/forward, reload, loading state, and URL handling.
- [ ] **3. Tab manager:** create, select, and close multiple pages.
- [ ] **4. Tab switcher:** hide the permanent tab strip and make tabs discoverable from the keyboard.
- [ ] **5. Keyboard workflow:** implement and test application-level shortcuts.
- [ ] **6. Persistent profile:** retain cookies and browsing data between launches.
- [ ] **7. Extension proof of concept:** test the Qt WebEngine extension API with a compatible Manifest V3 extension.
- [ ] **8. Settings and polish:** configurable behaviour, error handling, and UI refinement.
- [ ] **9. Compatibility notes:** record the Qt/Chromium version and extensions tested.

## Scope and non-goals

- Symul is intended to **embed Qt WebEngine**, not compile and maintain a private Chromium fork.
- It will not initially promise full compatibility with every Chrome extension.
- It will not assume that arbitrary JavaScript injection can replace browser-level functionality; tab and shortcut management belong in the native application.
- Security updates depend on the Qt WebEngine version supplied by the chosen Qt release and distribution/package source, so the engine version should be tracked and updated deliberately.

## Contributing

The project is in its planning stage. The most useful early contributions are small, testable steps: a working web view, reliable tab lifecycle management, and a usable keyboard-driven tab switcher.

---

**Core design principle:** use Qt WebEngine for rendering pages, and use PySide6 to own the browser interface and tab behaviour.
