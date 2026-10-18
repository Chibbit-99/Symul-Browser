#!/usr/bin/env python3
"""Symul Browser — an early PySide6 / Qt WebEngine browser prototype."""

import sys
from pathlib import Path
from urllib.parse import quote, urlparse

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView


APP_NAME = "Symul Browser"
APP_DIR = Path(__file__).resolve().parent
ICON_PATH = APP_DIR / "icon.png"
HOME_URL = "https://duckduckgo.com/"


class BrowserTab(QWidget):
    """A single page and its navigation controls."""

    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(parent)
        self.view = QWebEngineView(self)
        self.page = QWebEnginePage(profile, self.view)
        self.view.setPage(self.page)

        self.address = QLineEdit(self)
        self.address.setPlaceholderText("Search or enter address")
        self.address.setClearButtonEnabled(True)
        self.address.returnPressed.connect(self.navigate)
        self.view.urlChanged.connect(self.update_address)

        back = QPushButton("←", self)
        back.setToolTip("Back")
        back.clicked.connect(self.view.back)
        forward = QPushButton("→", self)
        forward.setToolTip("Forward")
        forward.clicked.connect(self.view.forward)
        reload_button = QPushButton("⟳", self)
        reload_button.setToolTip("Reload")
        reload_button.clicked.connect(self.view.reload)
        go = QPushButton("Go", self)
        go.clicked.connect(self.navigate)

        controls = QHBoxLayout()
        controls.setContentsMargins(8, 8, 8, 4)
        controls.setSpacing(6)
        controls.addWidget(back)
        controls.addWidget(forward)
        controls.addWidget(reload_button)
        controls.addWidget(self.address, 1)
        controls.addWidget(go)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(controls)
        layout.addWidget(self.view, 1)

        self.view.setUrl(QUrl(HOME_URL))

    def navigate(self):
        text = self.address.text().strip()
        if not text:
            return

        # Explicit URLs are opened directly; other text is sent to DuckDuckGo.
        parsed = urlparse(text)
        if parsed.scheme in ("http", "https"):
            target = text
        elif " " not in text and "." in text:
            target = "https://" + text
        else:
            target = "https://duckduckgo.com/?q=" + quote(text)

        self.view.setUrl(QUrl(target))

    def update_address(self, url: QUrl):
        self.address.setText(url.toString())


class SymulBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        if ICON_PATH.is_file():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.resize(1200, 800)

        # A persistent profile keeps cookies and site storage between launches.
        self.profile = QWebEngineProfile("SymulBrowser", self)
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )

        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabBar().hide()  # Prototype: no permanent tab strip.
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_window_title)
        self.setCentralWidget(self.tabs)

        self._build_menu()
        self.new_tab()

    def _build_menu(self):
        toolbar = QToolBar("Browser", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        new_tab_action = QAction("New tab", self)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.triggered.connect(self.new_tab)
        self.addAction(new_tab_action)

        close_tab_action = QAction("Close tab", self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(
            lambda: self.close_tab(self.tabs.currentIndex())
        )
        self.addAction(close_tab_action)

        focus_address_action = QAction("Focus address", self)
        focus_address_action.setShortcut(QKeySequence("Ctrl+L"))
        focus_address_action.triggered.connect(self.focus_address)
        self.addAction(focus_address_action)

        next_tab_action = QAction("Next tab", self)
        next_tab_action.setShortcut(QKeySequence("Ctrl+Tab"))
        next_tab_action.triggered.connect(self.next_tab)
        self.addAction(next_tab_action)

        previous_tab_action = QAction("Previous tab", self)
        previous_tab_action.setShortcut(QKeySequence("Ctrl+Shift+Tab"))
        previous_tab_action.triggered.connect(self.previous_tab)
        self.addAction(previous_tab_action)

        menu = self.menuBar().addMenu("File")
        menu.addAction(new_tab_action)
        menu.addAction(close_tab_action)
        menu.addSeparator()
        menu.addAction("Quit", self.close, QKeySequence("Ctrl+Q"))

        view_menu = self.menuBar().addMenu("Navigate")
        view_menu.addAction(focus_address_action)
        view_menu.addAction(next_tab_action)
        view_menu.addAction(previous_tab_action)

    def new_tab(self, url: str = HOME_URL):
        tab = BrowserTab(self.profile, self.tabs)
        index = self.tabs.addTab(tab, "New tab")
        self.tabs.setCurrentIndex(index)
        tab.view.titleChanged.connect(
            lambda title, page_tab=tab: self.update_tab_title(page_tab, title)
        )
        if url != HOME_URL:
            tab.view.setUrl(QUrl(url))
        tab.address.setFocus()
        tab.address.selectAll()
        return tab

    def close_tab(self, index: int):
        if index < 0 or index >= self.tabs.count():
            return
        tab = self.tabs.widget(index)
        self.tabs.removeTab(index)
        tab.deleteLater()
        if self.tabs.count() == 0:
            self.new_tab()
        self.update_window_title()

    def update_tab_title(self, tab: BrowserTab, title: str):
        index = self.tabs.indexOf(tab)
        if index >= 0:
            self.tabs.setTabText(index, title or "New tab")
        if tab is self.tabs.currentWidget():
            self.update_window_title()

    def update_window_title(self, *_):
        tab = self.tabs.currentWidget()
        title = tab.view.title() if isinstance(tab, BrowserTab) else ""
        self.setWindowTitle(f"{title or 'New tab'} — {APP_NAME}")

    def focus_address(self):
        tab = self.tabs.currentWidget()
        if isinstance(tab, BrowserTab):
            tab.address.setFocus()
            tab.address.selectAll()

    def next_tab(self):
        count = self.tabs.count()
        if count > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % count)

    def previous_tab(self):
        count = self.tabs.count()
        if count > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % count)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Symul")
    # Match the KDE launcher filename so the taskbar can group/pin this app,
    # rather than identifying the running process as Python.
    app.setDesktopFileName("symul-browser")
    if ICON_PATH.is_file():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    window = SymulBrowser()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
