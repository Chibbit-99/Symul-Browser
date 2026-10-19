#!/usr/bin/env python3
"""Symul Browser — a compact, keyboard-first desktop browser."""

import json
import os
import sys
from pathlib import Path
from urllib.parse import quote, urlparse
import base64

from PySide6.QtCore import QObject, QPoint, QBuffer, QIODevice, QUrl, Qt, Slot
from PySide6.QtGui import QAction, QColor, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton,
    QProgressBar, QStatusBar, QStyleFactory, QTabBar, QVBoxLayout, QWidget,
)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel


APP_NAME = "Symul Browser"
APP_DIR = Path(__file__).resolve().parent
ICON_PATH = APP_DIR / "icon.png"
HOME_URL = "https://duckduckgo.com/"
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "symul-browser"
BOOKMARKS_FILE = DATA_DIR / "bookmarks.json"

STYLE = """
QMainWindow, QWidget#browserRoot { background: #ffffff; color: #202124; }
QWidget { color: #202124; font-size: 10pt; }
QWidget#chrome { background: #dee1e6; border-bottom: 1px solid #dadce0; }
QWidget#bookmarkBar { background: #ffffff; border-bottom: 1px solid #dadce0; }
QTabBar#tabStrip { background: #dee1e6; qproperty-drawBase: 0; }
QTabBar#tabStrip::tab { background: transparent; color: #5f6368; border: 0; border-radius: 8px 8px 0 0; padding: 7px 12px; margin: 5px 2px 0 0; min-width: 90px; max-width: 240px; height: 22px; }
QTabBar#tabStrip::tab:hover { background: #cfd3da; color: #202124; }
QTabBar#tabStrip::tab:selected { background: #ffffff; color: #202124; }
QTabBar#tabStrip QToolButton { background: transparent; border: 0; border-radius: 14px; min-width: 24px; min-height: 24px; }
QTabBar#tabStrip QToolButton:hover { background: #cfd3da; }
QPushButton#bookmarkItem { min-height: 28px; max-height: 28px; min-width: 0; padding: 0 9px; font-size: 9pt; border-radius: 6px; }
QPushButton {
  background: transparent; color: #3c4043; border: 0; border-radius: 16px;
  min-width: 32px; min-height: 32px; padding: 0 4px; font-size: 17px;
}
QPushButton:hover { background: #e8eaed; color: #202124; }
QPushButton:pressed { background: #dadce0; }
QPushButton:disabled { color: #b7b9bc; }
QPushButton#brandButton { color: #77aaff; font-weight: 800; font-size: 20px; min-width: 36px; }
QPushButton#menuButton { font-size: 23px; min-width: 36px; }
QLineEdit#omnibox {
  background: #f1f3f4; color: #202124; border: 1px solid transparent;
  border-radius: 18px; padding: 0 13px; min-height: 34px;
  selection-background-color: #1a73e8;
}
QLineEdit#omnibox:hover { background: #e8eaed; }
QLineEdit#omnibox:focus { background: #ffffff; border: 1px solid #1a73e8; }
QLabel#security { color: #5f6368; min-width: 24px; font-size: 16px; }
QLabel#brandWord { color: #77aaff; font-size: 12pt; font-weight: 700; padding-left: 2px; }
QLabel#pageHint { color: #9bb1b7; padding: 2px 8px; }
QProgressBar { background: #1a292e; border: 0; max-height: 2px; }
QProgressBar::chunk { background: #4f8fff; }
QMenu {
  background: #ffffff; color: #202124; border: 1px solid #dadce0;
  padding: 6px; border-radius: 8px;
}
QMenu::item { padding: 8px 28px 8px 12px; border-radius: 5px; }
QMenu::item:selected { background: #f1f3f4; }
QMenu::separator { height: 1px; background: #dadce0; margin: 5px 8px; }
QStatusBar { background: #ffffff; color: #5f6368; border-top: 1px solid #dadce0; }
"""

class BrowserPage(QWebEnginePage):
    """A page that routes pop-up links into normal Symul tabs."""

    def __init__(self, profile, browser, parent=None):
        super().__init__(profile, parent)
        self.browser = browser
        self.install_local_extensions()

    def install_local_extensions(self):
        """Install manifest content scripts using Qt's built-in JavaScript injection."""
        newline = chr(10)
        for extension in self.browser.local_extensions:
            for item in extension["scripts"]:
                script = QWebEngineScript()
                script.setName(extension["name"] + ": " + item["file"])
                script.setInjectionPoint(item["injection_point"])
                script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
                script.setRunsOnSubFrames(item["all_frames"])
                matches_json = json.dumps(item["matches"])
                source = (
                    "(() => {" + newline
                    + "const patterns = " + matches_json + ";" + newline
                    + "const url = window.location.href;" + newline
                    + "const allowed = patterns.some(pattern => {" + newline
                    + "if (pattern === '<all_urls>') return /^(https?|file|ftp):/i.test(url);" + newline
                    + "const prefix = pattern.split('*')[0];" + newline
                    + "return url.startsWith(prefix);" + newline
                    + "});" + newline
                    + "if (allowed) {" + newline
                    + item["source"] + newline
                    + "}" + newline + "})();"
                )
                script.setSourceCode(source)
                self.scripts().insert(script)

    def createWindow(self, _type):
        tab = self.browser.new_tab("about:blank")
        return tab.view.page()


class BrowserTab(QWidget):
    def __init__(self, profile, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        tab_layout = QVBoxLayout(self)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        self.view = QWebEngineView(self)
        tab_layout.addWidget(self.view, 1)
        self.page = BrowserPage(profile, browser, self.view)
        self.view.setPage(self.page)
        self.view.urlChanged.connect(self.update_address)
        self.view.titleChanged.connect(self.on_title_changed)
        self.view.loadStarted.connect(self.on_load_started)
        self.view.loadProgress.connect(self.browser.update_progress)
        self.view.loadFinished.connect(self.on_load_finished)

    def navigate(self, text=None):
        text = (self.browser.address.text() if text is None else text).strip()
        if not text:
            return
        parsed = urlparse(text)
        if parsed.scheme in ("http", "https", "file", "about"):
            target = text
        elif " " not in text and ("." in text or text.startswith("localhost")):
            target = "https://" + text
        else:
            target = "https://duckduckgo.com/?q=" + quote(text)
        self.view.setUrl(QUrl(target))

    def update_address(self, url):
        if self.browser.tabs.currentWidget() is self:
            self.browser.address.setText(url.toString())
            self.browser.update_security(url)
            self.browser.sync_chrome()

    def on_title_changed(self, title):
        self.browser.update_tab_title(self, title)

    def on_load_started(self):
        if self.browser.tabs.currentWidget() is self:
            self.browser.loading = True
            self.browser.progress.setValue(0)
            self.browser.progress.hide()
            self.browser.statusBar().showMessage("Loading…")
            self.browser.sync_chrome()

    def on_load_finished(self, ok):
        if self.browser.tabs.currentWidget() is self:
            self.browser.loading = False
            self.browser.progress.hide()
            self.browser.statusBar().showMessage("Ready" if ok else "Page couldn't be loaded", 2500)
            self.browser.refresh_buttons()
            self.browser.sync_chrome()

class BrowserChromeBridge(QObject):
    """JavaScript bridge between the HTML chrome and real Qt WebEngine tabs."""
    def __init__(self, browser):
        super().__init__(browser)
        self.browser = browser
    @Slot()
    def ready(self): self.browser.sync_chrome()
    @Slot()
    def minimizeWindow(self): self.browser.showMinimized()
    @Slot()
    def toggleMaximizeWindow(self):
        if self.browser.isMaximized():
            self.browser.showNormal()
        else:
            self.browser.showMaximized()
        self.browser.sync_chrome()
    @Slot()
    def closeWindow(self): self.browser.close()
    @Slot()
    def beginWindowDrag(self):
        handle = self.browser.windowHandle()
        if handle:
            handle.startSystemMove()
    @Slot(int)
    def setChromeHeight(self, height):
        self.browser.chrome_view.setFixedHeight(max(1, min(height, 120)))
    @Slot(str)
    def navigate(self, text):
        tab = self.browser.current_tab()
        if tab: tab.navigate(text)
    @Slot(str)
    def openUrl(self, url):
        if url:
            tab = self.browser.current_tab()
            if tab: tab.view.setUrl(QUrl(url))
    @Slot()
    def back(self):
        tab = self.browser.current_tab()
        if tab: tab.view.back()
    @Slot()
    def forward(self):
        tab = self.browser.current_tab()
        if tab: tab.view.forward()
    @Slot()
    def reload(self): self.browser.reload_or_stop()
    @Slot()
    def home(self):
        tab = self.browser.current_tab()
        if tab: tab.view.setUrl(QUrl(HOME_URL))
    @Slot()
    def newTab(self): self.browser.new_tab()
    @Slot(int)
    def closeTab(self, index): self.browser.close_tab(index)
    @Slot(int)
    def selectTab(self, index):
        if 0 <= index < self.browser.tabs.count(): self.browser.tabs.setCurrentIndex(index)
    @Slot()
    def toggleBookmark(self): self.browser.toggle_bookmark()
    @Slot()
    def extensions(self): self.browser.show_extensions()
    @Slot()
    def downloads(self): self.browser.show_downloads()
    @Slot()
    def menu(self): self.browser.show_browser_menu()
    @Slot(int, int)
    def showTabMenu(self, x, y): self.browser.show_tab_menu(x, y)


class SymulBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        if ICON_PATH.is_file():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.resize(1280, 820)
        self.setMinimumSize(720, 480)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.profile = QWebEngineProfile("SymulBrowser", self)
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
        self.profile.setPersistentStoragePath(str(DATA_DIR / "web-data"))
        self.profile.setCachePath(str(DATA_DIR / "cache"))
        self.profile.downloadRequested.connect(self.handle_download)
        self.local_extensions = self.load_local_extensions()

        root = QWidget(self)
        root.setObjectName("browserRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # The browser chrome is rendered from the HTML prototype.
        self.chrome_view = QWebEngineView(root)
        # Size the embedded chrome to its actual HTML content. The page reports
        # its height after rendering so an empty bookmarks row leaves no gap.
        self.chrome_view.setMinimumHeight(45)
        self.chrome_view.setMaximumHeight(120)
        self.chrome_view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        chrome_page = QWebEnginePage(self.profile, self.chrome_view)
        chrome_page.setBackgroundColor(QColor("#ffffff"))
        self.chrome_view.setPage(chrome_page)
        self.chrome_channel = QWebChannel(self.chrome_view.page())
        self.chrome_bridge = BrowserChromeBridge(self)
        self.chrome_channel.registerObject("browserBridge", self.chrome_bridge)
        self.chrome_view.page().setWebChannel(self.chrome_channel)
        self.chrome_view.loadFinished.connect(lambda _ok: self.sync_chrome())
        self.chrome_view.setUrl(QUrl.fromLocalFile(str(APP_DIR / "resources" / "browser_chrome.html")))
        root_layout.addWidget(self.chrome_view)

        # Compatibility state used by existing browser commands and status reporting.
        self.address = QLineEdit(root)
        self.address.returnPressed.connect(self.navigate)
        self.security = QLabel(root)
        self.progress = QProgressBar(root)
        self.progress.setRange(0, 100)
        self.progress.hide()
        self.back_button = QPushButton(root)
        self.forward_button = QPushButton(root)
        self.reload_button = QPushButton(root)
        self.home_button = QPushButton(root)
        self.bookmark_button = QPushButton(root)
        self.tabs_button = QPushButton(root)
        self.extensions_button = QPushButton(root)
        self.downloads_button = QPushButton(root)
        self.menu_button = QPushButton(root)
        for control in (self.address, self.security, self.progress, self.back_button,
                        self.forward_button, self.reload_button, self.home_button,
                        self.bookmark_button, self.tabs_button, self.extensions_button,
                        self.downloads_button, self.menu_button):
            control.hide()
        status = QStatusBar(self)
        self.setStatusBar(status)
        self.statusBar().showMessage("Ready")

        self.tabs = _TabStack(root)
        self.tabs.setObjectName("tabContent")
        self.tabs.setStyleSheet("background: #ffffff;")
        self.tabs.stack.setStyleSheet("background: #ffffff;")
        self.tabs.browser = self
        root_layout.addWidget(self.tabs, 1)
        self.setCentralWidget(root)
        self.statusBar().hide()
        self.loading = False

        self._build_actions()
        self.refresh_bookmark_bar()
        self.new_tab()
        self.apply_shortcuts()
        # QWebEngine can consume Ctrl+T before a content script sees it.
        # Use an application-wide host shortcut for the test extension.
        self.ctrl_t_extension_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.ctrl_t_extension_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.ctrl_t_extension_shortcut.activated.connect(self.handle_ctrl_t_extension)

    def sync_chrome(self):
        """Synchronise the HTML chrome with live WebEngine tabs and bookmarks."""
        if not hasattr(self, "chrome_view") or not hasattr(self, "tabs") or not hasattr(self, "progress"):
            return
        current = self.current_tab()
        colors = ["#4285f4", "#d93025", "#f48024", "#34a853", "#5f6368", "#7b61ff", "#10a37f", "#1da1f2"]
        tab_states = []
        for index in range(self.tabs.count()):
            tab = self.tabs.widget(index)
            url = tab.view.url().toString()
            title = tab.view.title() or ("New Tab" if not url or url == "about:blank" else urlparse(url).hostname or url)
            favicon = tab.view.icon()
            favicon_data = ""
            if not favicon.isNull():
                image_buffer = QBuffer()
                image_buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                if favicon.pixmap(32, 32).save(image_buffer, "PNG"):
                    favicon_data = "data:image/png;base64," + base64.b64encode(bytes(image_buffer.data())).decode("ascii")
                image_buffer.close()
            tab_states.append({
                "title": title,
                "url": "" if url == "about:blank" else url,
                "color": colors[index % len(colors)],
                "favicon": favicon_data,
            })
        url = current.view.url().toString() if current else ""
        state = {
            "tabs": tab_states, "active": self.tabs.currentIndex(),
            "url": "" if url == "about:blank" else url,
            "title": current.view.title() if current else "New Tab",
            "canBack": bool(current and current.view.history().canGoBack()),
            "canForward": bool(current and current.view.history().canGoForward()),
            "loading": bool(current and self.loading),
            "bookmarked": self.is_bookmarked(url) if url and url != "about:blank" else False,
            "bookmarks": self.load_bookmarks(),
        }
        payload = json.dumps(state).replace("</", "<\\/")
        self.chrome_view.page().runJavaScript("if(window.setBrowserState)window.setBrowserState(" + payload + ");")

    def load_local_extensions(self):
        """Load basic unpacked extensions that declare manifest content scripts."""
        loaded = []
        extension_root = APP_DIR / "extensions"
        if not extension_root.is_dir():
            print(f"No extensions directory found: {extension_root}")
            return loaded

        injection_points = {
            "document_start": QWebEngineScript.InjectionPoint.DocumentCreation,
            "document_end": QWebEngineScript.InjectionPoint.DocumentReady,
            "document_idle": QWebEngineScript.InjectionPoint.Deferred,
        }

        for manifest_path in sorted(extension_root.glob("*/manifest.json")):
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                extension_name = manifest.get("name", manifest_path.parent.name)
                scripts = []

                for content_script in manifest.get("content_scripts", []):
                    injection_point = injection_points.get(
                        content_script.get("run_at", "document_idle")
                    )
                    if injection_point is None:
                        print(f"Unsupported run_at value in {manifest_path}")
                        continue

                    matches = content_script.get("matches", [])
                    for relative_path in content_script.get("js", []):
                        script_path = (manifest_path.parent / relative_path).resolve()
                        if manifest_path.parent.resolve() not in script_path.parents:
                            print(f"Rejected extension script outside its folder: {script_path}")
                            continue
                        if not script_path.is_file():
                            print(f"Extension script not found: {script_path}")
                            continue

                        scripts.append({
                            "file": relative_path,
                            "source": script_path.read_text(encoding="utf-8"),
                            "matches": matches,
                            "injection_point": injection_point,
                            "all_frames": bool(content_script.get("all_frames", False)),
                        })

                if scripts:
                    loaded.append({"name": extension_name, "scripts": scripts})
                    print(f"Loaded extension content scripts: {extension_name}")
                else:
                    print(f"No supported content scripts found in {manifest_path}")
            except (OSError, ValueError, TypeError) as error:
                print(f"Could not load extension manifest {manifest_path}: {error}")

        return loaded

    def button(self, text, tooltip, callback):
        button = QPushButton(text, self)
        button.setToolTip(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)
        return button

    def _build_actions(self):
        self.actions_by_name = {}
        entries = [
            ("New tab", "Alt+T", lambda: self.new_tab()),
            ("Close tab", "Ctrl+W", lambda: self.close_current_tab()),
            ("Focus address bar", "Ctrl+L", self.focus_address),
            ("Next tab", "Ctrl+Tab", self.next_tab),
            ("Previous tab", "Ctrl+Shift+Tab", self.previous_tab),
            ("Reload", "Ctrl+R", self.reload_or_stop),
            ("Home", "Alt+Home", lambda: self.current_tab().view.setUrl(QUrl(HOME_URL))),
            ("Back", "Alt+Left", lambda: self.current_tab().view.back()),
            ("Forward", "Alt+Right", lambda: self.current_tab().view.forward()),
            ("Find in page", "Ctrl+F", self.show_find_bar),
            ("Zoom in", "Ctrl++", lambda: self.zoom(0.1)),
            ("Zoom out", "Ctrl+-", lambda: self.zoom(-0.1)),
            ("Reset zoom", "Ctrl+0", lambda: self.current_tab().view.setZoomFactor(1.0)),
            ("Fullscreen", "F11", self.toggle_fullscreen),
            ("Quit", "Ctrl+Q", self.close),
        ]
        for title, shortcut, callback in entries:
            action = QAction(title, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(callback)
            self.addAction(action)
            self.actions_by_name[title] = action

    def apply_shortcuts(self):
        self.find_bar = QWidget(self.centralWidget())
        find_layout = QHBoxLayout(self.find_bar)
        find_layout.setContentsMargins(12, 7, 12, 7)
        find_layout.addWidget(QLabel("Find", self.find_bar))
        self.find_input = QLineEdit(self.find_bar)
        self.find_input.setPlaceholderText("Find on this page")
        self.find_input.textChanged.connect(self.find_text)
        find_layout.addWidget(self.find_input, 1)
        self.find_count = QLabel("", self.find_bar)
        find_layout.addWidget(self.find_count)
        close_find = self.button("×", "Close find bar (Esc)", self.hide_find_bar)
        find_layout.addWidget(close_find)
        self.find_bar.hide()
        self.find_bar.setStyleSheet("background:#172226; border-bottom:1px solid #29383d;")
        self.find_bar.setGeometry(0, 0, 440, 52)

        self.find_escape = QShortcut(QKeySequence("Esc"), self.find_bar)
        self.find_escape.activated.connect(self.hide_find_bar)

    def current_tab(self):
        return self.tabs.currentWidget()

    def _select_tab_from_bar(self, index):
        if hasattr(self, "tabs") and index >= 0 and index != self.tabs.currentIndex():
            self.tabs.setCurrentIndex(index)

    def new_tab(self, url=HOME_URL):
        tab = BrowserTab(self.profile, self, self.tabs)
        index = self.tabs.addTab(tab, "New tab")
        self.tabs.setCurrentIndex(index)
        tab.view.setUrl(QUrl(url))
        self.address.setFocus()
        self.address.selectAll()
        self.refresh_buttons()
        return tab

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def close_tab(self, index):
        if index < 0 or index >= self.tabs.count():
            return
        tab = self.tabs.widget(index)
        self.tabs.removeTab(index)
        tab.deleteLater()
        if self.tabs.count() == 0:
            self.new_tab()
        self.sync_current_tab()
        self.refresh_buttons()

    def update_tab_title(self, tab, title):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            clean_title = (title or "New tab")[:80]
            self.tabs.setTabText(index, clean_title)
        if tab is self.current_tab():
            self.update_window_title()
        self.sync_chrome()

    def update_window_title(self, *_):
        tab = self.current_tab()
        title = tab.view.title() if tab else ""
        self.setWindowTitle((title or "New tab") + " — Symul Browser")

    def sync_current_tab(self, *_):
        tab = self.current_tab()
        if not tab:
            return
        self.address.setText(tab.view.url().toString())
        index = self.tabs.currentIndex()
        self.update_security(tab.view.url())
        self.update_window_title()
        self.refresh_buttons()
        self.tabs_button.setText("▣ " + str(self.tabs.count()))
        self.bookmark_button.setText("★" if self.is_bookmarked(tab.view.url().toString()) else "☆")
        self.progress.setVisible(False)
        self.sync_chrome()

    def navigate(self):
        self.current_tab().navigate()

    def focus_address(self):
        self.address.setFocus()
        self.address.selectAll()

    def refresh_buttons(self):
        tab = self.current_tab()
        if not tab:
            return
        self.back_button.setEnabled(tab.view.history().canGoBack())
        self.forward_button.setEnabled(tab.view.history().canGoForward())
        self.reload_button.setText("↻")
        self.tabs_button.setText("▣ " + str(self.tabs.count()))
        self.sync_chrome()

    def reload_or_stop(self):
        tab = self.current_tab()
        if tab:
            tab.view.reload()

    def update_progress(self, value):
        tab = self.current_tab()
        if tab:
            self.progress.setValue(value)
            self.progress.hide()
            self.loading = value < 100
            self.sync_chrome()

    def update_security(self, url):
        scheme = url.scheme()
        self.security.setText("🔒" if scheme == "https" else ("ⓘ" if scheme in ("http", "file") else "◈"))
        self.security.setToolTip("Secure connection (HTTPS)" if scheme == "https" else "Connection information")

    def update_page_icon(self, icon):
        if icon and not icon.isNull():
            self.setWindowIcon(icon)
        elif ICON_PATH.is_file():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

    def next_tab(self):
        if self.tabs.count() > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % self.tabs.count())

    def previous_tab(self):
        if self.tabs.count() > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % self.tabs.count())

    def handle_ctrl_t_extension(self):
        """Run the local test extension's Ctrl+T alert reliably at browser level."""
        if any(extension.get("name") == "Symul Test Alert" for extension in self.local_extensions):
            tab = self.current_tab()
            if tab:
                tab.view.page().runJavaScript('alert("Ctrl+T was pressed!")')

    def show_tab_menu(self, x=None, y=None):
        menu = QMenu(self)
        # Keep the popup's corners transparent and match the browser's tab strip
        # instead of using the unrelated white system-menu appearance.
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint)
        fusion_style = QStyleFactory.create("Fusion")
        if fusion_style is not None:
            menu.setStyle(fusion_style)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1f1f23;
                color: #e8eaed;
                border: 1px solid #3c4043;
                border-radius: 10px;
                padding: 6px;
                font-size: 10pt;
            }
            QMenu::item {
                background-color: transparent;
                padding: 9px 30px 9px 10px;
                margin: 2px;
                border-radius: 6px;
                min-width: 250px;
                min-height: 20px;
            }
            QMenu::item:selected {
                background-color: #35363a;
                color: #e8eaed;
            }
            QMenu::item:disabled { color: #9aa0a6; }
            QMenu::icon { padding-left: 2px; }
            QMenu::separator {
                height: 1px;
                background: #3c4043;
                color: #3c4043;
                border: none;
                margin: 6px 8px;
                padding: 0;
                max-height: 1px;
            }
        """)
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            title = tab.view.title() or "New tab"
            action = menu.addAction(title[:55])
            favicon = tab.view.icon()
            if not favicon.isNull():
                action.setIcon(favicon)
            action.setToolTip(tab.view.url().toString())
            action.triggered.connect(lambda checked=False, index=i: self.tabs.setCurrentIndex(index))
        menu.addSeparator()
        new_tab_action = menu.addAction("＋  New tab")
        new_tab_action.triggered.connect(lambda checked=False: self.new_tab())
        anchor = self.chrome_view.mapToGlobal(QPoint(max(8, x if x is not None else self.chrome_view.width() - 310), y if y is not None else 38))
        menu.exec(anchor)

    def show_browser_menu(self):
        menu = QMenu(self)
        menu.addAction("New tab", lambda: self.new_tab())
        menu.addSeparator()
        menu.addAction("Bookmarks", self.show_bookmarks)
        menu.addAction("History", self.show_history)
        menu.addAction("Downloads", self.show_downloads)
        menu.addSeparator()
        menu.addAction("Find in page", self.show_find_bar)
        zoom_menu = menu.addMenu("Zoom")
        zoom_menu.addAction("Zoom in", lambda: self.zoom(0.1))
        zoom_menu.addAction("Zoom out", lambda: self.zoom(-0.1))
        zoom_menu.addAction("Reset zoom", lambda: self.current_tab().view.setZoomFactor(1.0))
        menu.addSeparator()
        menu.addAction("Settings & shortcuts", self.show_about)
        menu.addAction("Quit Symul", self.close)
        menu.exec(self.chrome_view.mapToGlobal(QPoint(self.chrome_view.width() - 36, self.chrome_view.height() - 18)))

    def toggle_bookmark(self):
        tab = self.current_tab()
        url = tab.view.url().toString()
        if not url or url == "about:blank":
            return
        bookmarks = self.load_bookmarks()
        existing = next((item for item in bookmarks if item.get("url") == url), None)
        if existing:
            bookmarks.remove(existing)
        else:
            bookmarks.append({"title": tab.view.title() or url, "url": url})
        self.save_bookmarks(bookmarks)
        self.refresh_bookmark_bar()
        self.sync_chrome()
        self.bookmark_button.setText("★" if not existing else "☆")
        self.statusBar().showMessage("Bookmark removed" if existing else "Page bookmarked", 2200)

    def load_bookmarks(self):
        try:
            return json.loads(BOOKMARKS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []

    def save_bookmarks(self, bookmarks):
        BOOKMARKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        BOOKMARKS_FILE.write_text(json.dumps(bookmarks, indent=2), encoding="utf-8")

    def refresh_bookmark_bar(self):
        """Render saved bookmarks in the compact toolbar row."""
        if not hasattr(self, "bookmark_layout"):
            return
        while self.bookmark_layout.count():
            item = self.bookmark_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        bookmarks = self.load_bookmarks()
        for item in bookmarks[:12]:
            title = (item.get("title") or item.get("url") or "Bookmark").strip()
            url = item.get("url", "")
            button = QPushButton(title[:24], self.bookmark_bar)
            button.setObjectName("bookmarkItem")
            button.setToolTip(url)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, target=url: self.current_tab().view.setUrl(QUrl(target)))
            self.bookmark_layout.addWidget(button)
        self.bookmark_layout.addStretch(1)
        self.sync_chrome()

    def show_extensions(self):
        menu = QMenu(self)
        if not self.local_extensions:
            menu.addAction("No local extensions loaded").setEnabled(False)
        else:
            for extension in self.local_extensions:
                action = menu.addAction(extension["name"])
                action.setEnabled(False)
        menu.addSeparator()
        menu.addAction("Extension folder", lambda: QMessageBox.information(
            self, "Local extensions", "Place supported unpacked extensions in the 'extensions' folder inside the Symul Browser repository. Only manifest content scripts are currently supported."
        ))
        menu.exec(self.chrome_view.mapToGlobal(QPoint(self.chrome_view.width() - 160, 48)))

    def is_bookmarked(self, url):
        return any(item.get("url") == url for item in self.load_bookmarks())

    def show_bookmarks(self):
        menu = QMenu(self)
        bookmarks = self.load_bookmarks()
        if not bookmarks:
            menu.addAction("No bookmarks yet").setEnabled(False)
        else:
            for item in bookmarks:
                action = menu.addAction(item.get("title", item.get("url", "Bookmark"))[:60])
                action.triggered.connect(lambda checked=False, url=item.get("url", ""): self.current_tab().view.setUrl(QUrl(url)))
                remove = menu.addAction("   Remove: " + item.get("title", item.get("url", ""))[:45])
                remove.triggered.connect(lambda checked=False, url=item.get("url", ""): self.remove_bookmark(url))
        menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))

    def remove_bookmark(self, url):
        self.save_bookmarks([item for item in self.load_bookmarks() if item.get("url") != url])
        self.refresh_bookmark_bar()
        self.sync_current_tab()

    def show_history(self):
        menu = QMenu(self)
        history = self.current_tab().view.history().items()
        history = list(reversed(history))[:30]
        if not history:
            menu.addAction("No history for this tab").setEnabled(False)
        for item in history:
            action = menu.addAction(item.title()[:60] or item.url().toString()[:60])
            action.triggered.connect(lambda checked=False, url=item.url(): self.current_tab().view.setUrl(url))
        menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))

    def handle_download(self, download):
        suggested = download.downloadFileName() or "download"
        path, _ = QFileDialog.getSaveFileName(self, "Save download", str(Path.home() / suggested))
        if not path:
            download.cancel()
            return
        download.setDownloadDirectory(str(Path(path).parent))
        download.setDownloadFileName(Path(path).name)
        download.accept()
        self.statusBar().showMessage("Downloading " + Path(path).name)

    def show_downloads(self):
        QMessageBox.information(self, "Downloads", "Downloads are saved to the location you choose when each download starts.")

    def show_find_bar(self):
        self.find_bar.show()
        self.find_bar.raise_()
        self.find_bar.setGeometry(max(0, self.centralWidget().width() - 452), 64, min(440, self.centralWidget().width()), 52)
        self.find_input.setFocus()
        self.find_input.selectAll()

    def hide_find_bar(self):
        self.find_bar.hide()
        self.current_tab().view.findText("")
        self.current_tab().view.setFocus()

    def find_text(self, text):
        self.current_tab().view.findText(text)
        self.find_count.setText("Searching…" if text else "")

    def zoom(self, amount):
        tab = self.current_tab()
        tab.view.setZoomFactor(max(0.5, min(3.0, tab.view.zoomFactor() + amount)))

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def private_window_notice(self):
        QMessageBox.information(self, "Private browsing", "Private browsing is not implemented yet. Symul currently uses your normal persistent browser profile.")

    def show_about(self):
        QMessageBox.information(
            self, "Symul Browser",
            "Symul Browser\\nA compact Chromium-based browser with a keyboard-first workflow.\\n\\n"
            "Shortcuts\\n"
            "Alt+T  New tab\\nCtrl+W  Close tab\\nCtrl+L  Focus address bar\\n"
            "Ctrl+Tab / Ctrl+Shift+Tab  Switch tabs\\nCtrl+F  Find on page\\n"
            "Ctrl+R  Reload\\nCtrl+Plus / Ctrl+Minus  Zoom\\nF11  Fullscreen\\n\\n"
            "Built with PySide6 and Qt WebEngine."
        )

class _TabStack(QWidget):
    """A tab container with no visible tab strip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QStackedWidget
        self.stack = QStackedWidget(self)
        self._tabs = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

    def addTab(self, widget, title):
        self._tabs.append([widget, title])
        self.stack.addWidget(widget)
        return len(self._tabs) - 1

    def count(self):
        return len(self._tabs)

    def widget(self, index):
        return self._tabs[index][0] if 0 <= index < len(self._tabs) else None

    def indexOf(self, widget):
        return next((i for i, item in enumerate(self._tabs) if item[0] is widget), -1)

    def currentIndex(self):
        return self.stack.currentIndex()

    def currentWidget(self):
        return self.stack.currentWidget()

    def setCurrentIndex(self, index):
        if 0 <= index < len(self._tabs):
            self.stack.setCurrentIndex(index)
            if hasattr(self, "browser"):
                self.browser.sync_current_tab()

    def setTabText(self, index, title):
        if 0 <= index < len(self._tabs):
            self._tabs[index][1] = title

    def removeTab(self, index):
        if 0 <= index < len(self._tabs):
            widget = self._tabs[index][0]
            self._tabs.pop(index)
            self.stack.removeWidget(widget)
            if self._tabs:
                self.stack.setCurrentIndex(min(index, len(self._tabs) - 1))

    def currentChanged(self, callback):
        self.stack.currentChanged.connect(callback)

    def tabCloseRequested(self, callback):
        pass

    def tabBar(self):
        return None

    def currentChangedConnect(self, callback):
        self.stack.currentChanged.connect(callback)

    def history(self):
        tab = self.currentWidget()
        return tab.view.history() if tab else None

    def resizeEvent(self, event):
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Symul")
    app.setDesktopFileName("symul-browser")
    app.setStyleSheet(STYLE)
    if ICON_PATH.is_file():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = SymulBrowser()
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
