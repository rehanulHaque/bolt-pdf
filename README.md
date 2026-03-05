# 📚 Bolt PDF

A fast, fully offline, and privacy-focused digital library and PDF reader built with Python and PySide6. 

Unlike modern e-readers that rely on cloud syncing and complex databases, **Bolt PDF** uses a transparent, 100% JSON-based local storage system. It allows you to organize your PDFs like a real bookshelf, sort them by genre, and read them in a beautiful two-page spread without ever needing an internet connection.

![Screenshot-1](/3.png)
![Screenshot-2](/1.png)
![Screenshot-2](/2.png)

## ✨ Features

* **100% Offline & Local:** No databases (SQLite/SQL), no cloud syncing, no accounts. All metadata is saved transparently in simple `.json` files.
* **Visual Bookshelf:** See your books as real covers, complete with reading progress bars.
* **Drag & Drop Import:** Easily add new PDFs by dragging them directly into the application window.
* **Smart Organization:** Group books by custom genres/collections, and use the real-time search bar to find books instantly.
* **Book-Style Reader:** A high-DPI, crystal-clear 2-page spread view that automatically scales to your window size.
* **Progress Tracking:** Automatically remembers the last page you were reading and calculates your completion percentage.
* **CPU-Friendly:** Runs smoothly on normal computers without requiring dedicated GPU acceleration.

## 🛠️ Technology Stack

* **Language:** Python 3.11+
* **UI Framework:** PySide6 (Qt for Python)
* **PDF Engine:** PyMuPDF (`fitz`)