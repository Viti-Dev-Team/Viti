import sys
import json
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QAction,
    QLineEdit,
    QTabWidget,
    QShortcut,
    QMenu,
    QMessageBox,
    QListWidget,
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEngineProfile,
    QWebEnginePage,
)

BOOKMARK_FILE = "bookmarks.json"
HISTORY_FILE = "history.json"


class BrowserTab(QWebEngineView):
    def __init__(self, profile, url=None):
        super().__init__()
        page = QWebEnginePage(profile, self)
        self.setPage(page)
        if not url:
            url = "https://www.google.com"
        self.setUrl(QUrl(str(url)))


class VitiBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Viti Browser")
        self.resize(1400, 800)
        self.profile = QWebEngineProfile.defaultProfile()
        self.bookmarks = []
        self.history = []
        self.load_bookmarks()
        self.load_history()
        self.init_ui()
        self.add_new_tab("https://www.google.com")

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

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        toolbar.addAction(reload_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter URL")
        self.url_bar.returnPressed.connect(self.navigate)
        toolbar.addWidget(self.url_bar)

        bookmark_btn = QAction("⭐", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        toolbar.addAction(bookmark_btn)

        download_btn = QAction("⬇", self)
        download_btn.triggered.connect(self.show_download_manager)
        toolbar.addAction(download_btn)

        new_tab_btn = QAction("➕", self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab("https://www.google.com"))
        toolbar.addAction(new_tab_btn)

        QShortcut(QKeySequence("Ctrl+T"), self,
                  activated=lambda: self.add_new_tab("https://www.google.com"))

        self.bookmarks_menu = self.menuBar().addMenu("Bookmarks")
        self.history_menu = self.menuBar().addMenu("History")

        self.refresh_bookmarks_menu()
        self.refresh_history_menu()

        self.profile.downloadRequested.connect(self.handle_download)

        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1f22; }
            QToolBar { background-color: #2a2b2f; padding: 6px; }
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
            QTabBar::tab:selected { background: #35363a; }
        """)

    def add_new_tab(self, url=None):
        if not url:
            url = "https://www.google.com"
        browser = BrowserTab(self.profile, url)
        index = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentIndex(index)

        browser.loadFinished.connect(
            lambda _, i=index, b=browser:
            self.tabs.setTabText(i, b.page().title())
        )

        browser.urlChanged.connect(
            lambda q, b=browser:
            self.update_url_bar(q)
        )

        browser.loadFinished.connect(
            lambda _, b=browser:
            self.add_to_history(b.page().title(), b.url().toString())
        )

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_browser(self):
        return self.tabs.currentWidget()

    def navigate(self):
        text = self.url_bar.text()
        if "." not in text:
            url = "https://www.google.com/search?q=" + text
        elif not text.startswith("http"):
            url = "https://" + text
        else:
            url = text
        self.current_browser().setUrl(QUrl(url))

    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())

    def add_bookmark(self):
        browser = self.current_browser()
        if not browser:
            return
        self.bookmarks.append({
            "title": browser.page().title(),
            "url": browser.url().toString()
        })
        self.save_bookmarks()
        self.refresh_bookmarks_menu()
        QMessageBox.information(self, "Bookmark", "Added")

    def delete_bookmark(self, index):
        reply = QMessageBox.question(
            self,
            "Delete",
            "Delete bookmark?",
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
            open_action = QAction("Open", self)
            open_action.triggered.connect(
                lambda _, url=bookmark["url"]:
                self.add_new_tab(url)
            )
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(
                lambda _, idx=index:
                self.delete_bookmark(idx)
            )
            submenu.addAction(open_action)
            submenu.addAction(delete_action)
            self.bookmarks_menu.addMenu(submenu)

    def add_to_history(self, title, url):
        self.history.append({
            "title": title,
            "url": url,
            "date": str(QUrl(url))
        })
        self.save_history()
        self.refresh_history_menu()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        else:
            self.history = []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

    def refresh_history_menu(self):
        self.history_menu.clear()
        for index, item in enumerate(self.history):
            submenu = QMenu(item["title"], self)
            open_action = QAction("Open", self)
            open_action.triggered.connect(
                lambda _, url=item["url"]:
                self.add_new_tab(url)
            )
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(
                lambda _, idx=index:
                self.delete_history_item(idx)
            )
            submenu.addAction(open_action)
            submenu.addAction(delete_action)
            self.history_menu.addMenu(submenu)

    def delete_history_item(self, index):
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self.save_history()
            self.refresh_history_menu()

    def handle_download(self, download):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        file_path = os.path.join(downloads_path, download.suggestedFileName())
        download.setPath(file_path)
        download.accept()
        download.finished.connect(self.refresh_downloads)

    def show_download_manager(self):
        self.download_window = QMainWindow(self)
        self.download_window.setWindowTitle("Downloads")
        self.download_window.resize(500, 400)
        self.download_list = QListWidget()
        self.download_window.setCentralWidget(self.download_list)
        self.refresh_downloads()
        self.download_window.show()

    def refresh_downloads(self):
        if hasattr(self, "download_list"):
            self.download_list.clear()
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(downloads_path):
                for file in os.listdir(downloads_path):
                    self.download_list.addItem(file)

    def sync_url_bar(self):
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VitiBrowser()
    window.show()
    sys.exit(app.exec_())