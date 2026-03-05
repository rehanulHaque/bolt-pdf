from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                               QListWidget, QListWidgetItem, QProgressBar, QLineEdit, QMessageBox, QHBoxLayout, QMenu, QInputDialog)

from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtCore import Qt, QSize

# 1. Create a custom widget for the Book Card
class BookCardWidget(QWidget):
    def __init__(self, book_data):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Cover Image
        self.cover = QLabel()
        pixmap = QPixmap(book_data["cover"]).scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.cover.setPixmap(pixmap)
        self.cover.setAlignment(Qt.AlignCenter)
        
        # Title
        self.title = QLabel(book_data["title"])
        self.title.setWordWrap(True)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 12px; font-weight: bold;")
        self.title.setMaximumWidth(120)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { border: 1px solid #ccc; border-radius: 4px; background: #eee; }
            QProgressBar::chunk { background-color: #4CAF50; border-radius: 4px; }
        """)
        
        # Calculate percentage (e.g., 0.5 becomes 50)
        pct = int(book_data.get("progress", 0.0) * 100)
        self.progress.setValue(pct)
        
        layout.addWidget(self.cover)
        layout.addWidget(self.title)
        layout.addWidget(self.progress)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize


class LibraryView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.current_genre_filter = "All Books"
        
        self.main_layout = QHBoxLayout(self)
        
        # --- LEFT SIDEBAR (Genres) ---
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget { background-color: #f7f7f7; border-right: 1px solid #ddd; border: none; font-size: 14px; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background-color: #007AFF; color: white; border-radius: 5px; }
        """)
        self.sidebar.itemClicked.connect(self.on_genre_clicked)
        
        # --- RIGHT AREA (Bookshelf) ---
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        
        # Top Bar (Header + Search)
        self.top_right_layout = QHBoxLayout()
        self.header = QLabel("Your Library")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search books by title...")
        self.search_bar.setMaximumWidth(300)
        self.search_bar.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        self.search_bar.textChanged.connect(self.populate) # Update grid as you type!
        
        self.top_right_layout.addWidget(self.header)
        self.top_right_layout.addStretch()
        self.top_right_layout.addWidget(self.search_bar)
        
        # Book Grid
        self.book_list = QListWidget()
        self.book_list.setViewMode(QListWidget.IconMode)
        self.book_list.setIconSize(QSize(150, 240))
        self.book_list.setSpacing(20)
        self.book_list.setResizeMode(QListWidget.Adjust)
        self.book_list.itemDoubleClicked.connect(self.on_book_clicked)
        
        # Enable Right-Click Menu
        self.book_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.book_list.customContextMenuRequested.connect(self.show_context_menu)
        
        self.right_layout.addLayout(self.top_right_layout)
        self.right_layout.addWidget(self.book_list)
        
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.right_widget, 1)

    def populate(self):
        """Refreshes the sidebar and the book grid with filtering & searching."""
        # 1. Update Sidebar
        self.sidebar.clear()
        self.sidebar.addItem("All Books")
        
        genres = self.main_window.lib_manager.get_all_genres()
        for genre in genres:
            self.sidebar.addItem(genre)

        # 2. Update Book Grid
        self.book_list.clear()
        books = self.main_window.lib_manager.load_books()
        search_text = self.search_bar.text().lower()
        
        for book in books:
            book_genre = book.get("genre", "Uncategorized")
            
            # Filter by Genre
            if self.current_genre_filter != "All Books" and book_genre != self.current_genre_filter:
                continue 
                
            # Filter by Search Text
            if search_text and search_text not in book["title"].lower():
                continue
                
            item = QListWidgetItem(self.book_list)
            item.setSizeHint(QSize(150, 240))
            item.setData(Qt.UserRole, book)
            
            card = BookCardWidget(book)
            self.book_list.setItemWidget(item, card)

    def on_genre_clicked(self, item):
        self.current_genre_filter = item.text()
        self.header.setText(self.current_genre_filter)
        self.populate()

    def show_context_menu(self, position):
        item = self.book_list.itemAt(position)
        if not item:
            return
            
        book_data = item.data(Qt.UserRole)
        
        menu = QMenu()
        set_genre_action = menu.addAction("Set Genre / Collection")
        remove_genre_action = menu.addAction("Remove from Genre")
        menu.addSeparator() # Adds a nice visual line
        delete_action = menu.addAction("Delete Book from Library")
        
        action = menu.exec(QCursor.pos())
        
        if action == set_genre_action:
            new_genre, ok = QInputDialog.getText(self, "Set Genre", 
                                                 f"Enter genre for '{book_data['title']}':",
                                                 text=book_data.get("genre", ""))
            if ok and new_genre.strip():
                self.main_window.lib_manager.update_book_genre(book_data["id"], new_genre.strip())
                self.populate()
                
        elif action == remove_genre_action:
            # Resets the genre to "Uncategorized"
            self.main_window.lib_manager.update_book_genre(book_data["id"], "Uncategorized")
            self.populate()
            
        elif action == delete_action:
            # Confirm before deleting
            reply = QMessageBox.question(self, "Confirm Delete", 
                                         f"Are you sure you want to remove '{book_data['title']}' from your library?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.main_window.lib_manager.delete_book(book_data["id"])
                self.populate()
    def on_book_clicked(self, item):
        """Handle double-click on a book."""
        book_data = item.data(Qt.UserRole)
        self.main_window.switch_to_reader(book_data)

    # Drag and Drop functionality
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event for PDF files."""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.main_window.lib_manager.add_book(file_path)
        self.populate()
