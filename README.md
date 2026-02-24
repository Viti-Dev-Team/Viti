# 🚀 Viti Browser

**Viti Browser** is a lightweight and modern web browser built with **Python + PyQt5 + Chromium (QtWebEngine)**.

This project is a personal development experiment focused on building a customizable browser with tab support, bookmarks, and automatic updates — packaged as a standalone desktop application.

---

## ✨ Features

✅ Full web browsing support  
✅ Multiple tabs (Ctrl + T, close, and move tabs)  
✅ Smart address bar (URL detection + automatic search)  
✅ Persistent bookmarks system (stored locally in JSON)  
✅ Add & delete bookmarks  
✅ Integrated bookmarks menu  
✅ Modern Chrome-style interface  
✅ Automatic update system  
✅ Buildable as a standalone `.exe` with custom icon  

---

## 🛠 Technologies Used

- Python 3  
- PyQt5  
- PyQtWebEngine (Chromium-based engine)  
- JSON for local data storage  
- PyInstaller for executable packaging  

---

## 📦 Build as Executable

To compile the project into a standalone `.exe` file:

```bash
pyinstaller --windowed --icon=icon.ico viti.py
