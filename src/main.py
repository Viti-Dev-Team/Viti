import sys
import json
import os

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar,
    QAction, QLineEdit, QTabWidget,
    QShortcut, QMenu, QMessageBox, QWidget,
    QVBoxLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEngineProfile,
    QWebEnginePage
)


BOOKMARK_FILE = "bookmarks.json"


class BrowserTab(QWebEngineView):
    def __init__(self, profile: QWebEngineProfile):
        super().__init__()

        page = QWebEnginePage(profile, self)
        self.setPage(page)

        self.setUrl(QUrl("https://www.google.com"))


class VitiBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Viti Browser")
        self.resize(1500, 900)

        self.profile = QWebEngineProfile.defaultProfile()

        self.bookmarks = []
        self.load_bookmarks()

        self.init_ui()
        self.add_new_tab()

    def init_ui(self):

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)

        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_url_bar)

        self.setCentralWidget(self.tabs)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        back = QAction("◀", self)
        back.triggered.connect(lambda: self.current_browser().back())
        toolbar.addAction(back)

        forward = QAction("▶", self)
        forward.triggered.connect(lambda: self.current_browser().forward())
        toolbar.addAction(forward)

        reload = QAction("⟳", self)
        reload.triggered.connect(lambda: self.current_browser().reload())
        toolbar.addAction(reload)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Rechercher ou entrer une URL...")
        self.url_bar.returnPressed.connect(self.navigate)
        toolbar.addWidget(self.url_bar)

        bookmark_btn = QAction("⭐", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        toolbar.addAction(bookmark_btn)

        new_tab = QAction("➕", self)
        new_tab.triggered.connect(self.add_new_tab)
        toolbar.addAction(new_tab)

        QShortcut(QKeySequence("Ctrl+T"), self, activated=self.add_new_tab)

        self.bookmarks_menu = self.menuBar().addMenu("Favoris")
        self.refresh_bookmarks_menu()

        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1f22; }

            QToolBar {
                background-color: #2a2b2f;
                padding: 6px;
            }

            QLineEdit {
                background-color: #35363a;
                border-radius: 14px;
                padding: 8px;
                color: white;
                border: 1px solid #3f4045;
            }

            QTabBar::tab {
                background: #2a2b2f;
                color: white;
                padding: 8px;
                margin: 4px;
                border-radius: 8px;
                min-width: 140px;
            }

            QTabBar::tab:selected {
                background: #35363a;
            }
        """)

    def add_new_tab(self, url=None):

        if url is None:
            url = QUrl("https://www.google.com")

        browser = BrowserTab(self.profile)
        browser.setUrl(url)

        index = self.tabs.addTab(browser, "Nouvel onglet")
        self.tabs.setCurrentIndex(index)

        browser.loadFinished.connect(
            lambda _, i=index, b=browser:
            self.tabs.setTabText(i, b.page().title())
        )

        browser.urlChanged.connect(
            lambda q, b=browser:
            self.update_url_bar(q, b)
        )

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_browser(self):
        return self.tabs.currentWidget()

    def sync_url_bar(self):
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())

    def navigate(self):

        url = self.url_bar.text()

        if "." not in url:
            url = "https://www.google.com/search?q=" + url
        elif not url.startswith("http"):
            url = "https://" + url

        self.current_browser().setUrl(QUrl(url))

    def update_url_bar(self, qurl, browser):
        if browser == self.current_browser():
            self.url_bar.setText(qurl.toString())

    def add_bookmark(self):

        browser = self.current_browser()
        title = browser.page().title()
        url = browser.url().toString()

        self.bookmarks.append({"title": title, "url": url})

        self.save_bookmarks()
        self.refresh_bookmarks_menu()

        QMessageBox.information(self, "Favori", "Ajouté ⭐")

    def delete_bookmark(self, index):

        reply = QMessageBox.question(
            self,
            "Supprimer",
            "Supprimer ce favori ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.bookmarks.pop(index)
            self.save_bookmarks()
            self.refresh_bookmarks_menu()

    def load_bookmarks(self):

        if os.path.exists(BOOKMARK_FILE):
            with open(BOOKMARK_FILE, "r", encoding="utf-8") as f:
                self.bookmarks = json.load(f)
        else:
            self.bookmarks = []

    def save_bookmarks(self):

        with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
            json.dump(self.bookmarks, f, indent=4)

    def refresh_bookmarks_menu(self):

        self.bookmarks_menu.clear()

        for index, bookmark in enumerate(self.bookmarks):

            submenu = QMenu(bookmark["title"], self)

            open_action = QAction("🌍 Ouvrir", self)
            open_action.triggered.connect(
                lambda _, url=bookmark["url"]:
                self.add_new_tab(QUrl(url))
            )

            delete_action = QAction("❌ Supprimer", self)
            delete_action.triggered.connect(
                lambda _, idx=index:
                self.delete_bookmark(idx)
            )

            submenu.addAction(open_action)
            submenu.addAction(delete_action)

            self.bookmarks_menu.addMenu(submenu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VitiBrowser()
    window.show()
    sys.exit(app.exec_())