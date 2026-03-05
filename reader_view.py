import fitz  # PyMuPDF
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QPixmap, QImage, QColor
from PySide6.QtCore import Qt


class ReaderView(QWidget):
    """PDF reader view with page navigation and two-page spread display."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.doc = None
        self.current_page = 0
        self.book_data = None
        
        # Set focus policy so we can easily add keyboard shortcuts later
        self.setFocusPolicy(Qt.StrongFocus)
        self.layout = QVBoxLayout(self)
        
        # Top Bar
        self.top_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Library")
        self.back_btn.clicked.connect(self.close_book)
        self.title_label = QLabel("Book Title")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.top_bar.addWidget(self.back_btn)
        self.top_bar.addWidget(self.title_label, 1)
        
        # Pages Area
        self.pages_layout = QHBoxLayout()
        self.left_page = QLabel()
        self.right_page = QLabel()
        self.left_page.setAlignment(Qt.AlignCenter)
        self.right_page.setAlignment(Qt.AlignCenter)
        
        page_style = "background-color: white; border: 1px solid #ccc;"
        self.left_page.setStyleSheet(page_style)
        self.right_page.setStyleSheet(page_style)

        self.pages_layout.addWidget(self.left_page)
        self.pages_layout.addWidget(self.right_page)
        
        # Bottom Navigation (UPDATED: Added page info label)
        self.nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        
        self.page_info_label = QLabel("Page - of -")
        self.page_info_label.setAlignment(Qt.AlignCenter)
        self.page_info_label.setStyleSheet("color: #555; font-size: 14px;")

        self.prev_btn.clicked.connect(self.page_prev)
        self.next_btn.clicked.connect(self.page_next)
        
        self.nav_layout.addWidget(self.prev_btn)
        self.nav_layout.addWidget(self.page_info_label, 1) # '1' makes it take the middle space
        self.nav_layout.addWidget(self.next_btn)
        
        self.layout.addLayout(self.top_bar)
        self.layout.addLayout(self.pages_layout, 1)
        self.layout.addLayout(self.nav_layout)

    def open_book(self, book_data):
        """Open a book for reading."""
        self.book_data = book_data
        self.title_label.setText(book_data["title"])
        self.doc = fitz.open(book_data["file_path"])
        self.current_page = book_data.get("last_page", 0)
        
        # Ensure we start on an even page for 2-page spread
        if self.current_page % 2 != 0:
            self.current_page -= 1
            
        self.render_pages()

    def close_book(self):
        """Close the currently open book."""
        if self.doc:
            self.doc.close()
            self.doc = None
        self.main_window.switch_to_library()

    def resizeEvent(self, event):
        """Automatically called when the window is resized."""
        super().resizeEvent(event)
        if self.doc:
            self.render_pages()

    def render_pages(self):
        # Calculate available space for ONE page
        available_width = (self.width() / 2) - 40
        available_height = self.height() - 150 
        
        if available_width <= 0 or available_height <= 0:
            return

        left_pix = self._get_scaled_page_pixmap(self.current_page, available_width, available_height)
        right_pix = self._get_scaled_page_pixmap(self.current_page + 1, available_width, available_height)
        
        self.left_page.setPixmap(left_pix)
        self.right_page.setPixmap(right_pix)
        
        total_pages = self.book_data["page_count"]
        
        # Hide right page if we are at the end of the book (odd number of pages)
        if self.current_page + 1 < total_pages:
            self.right_page.setVisible(True)
            # Display "Pages 2 - 3 of 100"
            self.page_info_label.setText(f"Pages {self.current_page + 1} - {self.current_page + 2} of {total_pages}")
        else:
            self.right_page.setVisible(False)
            # Display "Page 100 of 100"
            self.page_info_label.setText(f"Page {self.current_page + 1} of {total_pages}")

        # Update button states
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 2)
    def _get_scaled_page_pixmap(self, page_num, max_width, max_height):
        """Generate a scaled pixmap for a specific page."""
        if not self.doc or page_num < 0 or page_num >= len(self.doc):
            empty = QPixmap(int(max_width), int(max_height))
            empty.fill(QColor("#f0f0f0"))
            return empty
            
        page = self.doc.load_page(page_num)
        
        # Render at a high resolution multiplier for clarity
        zoom = 2.5 
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        
        # Convert to QImage
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        high_res_pixmap = QPixmap.fromImage(img)
        
        # Smoothly scale it down to exactly fit our window size
        return high_res_pixmap.scaled(
            int(max_width), 
            int(max_height), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )

    def page_next(self):
        """Navigate to the next page spread."""
        if self.current_page < self.book_data["page_count"] - 2:
            self.current_page += 2
            self.render_pages()

    def page_prev(self):
        """Navigate to the previous page spread."""
        if self.current_page > 0:
            self.current_page -= 2
            self.render_pages()

    # 1. Add this to your __init__ method to ensure the widget catches keystrokes
    # self.setFocusPolicy(Qt.StrongFocus) 
    
    def keyPressEvent(self, event):
        """Handle keyboard navigation."""
        if event.key() == Qt.Key_Right or event.key() == Qt.Key_Space or event.key() == Qt.Key_PageDown:
            self.page_next()
        elif event.key() == Qt.Key_Left or event.key() == Qt.Key_PageUp:
            self.page_prev()
        elif event.key() == Qt.Key_Escape:
            self.close_book()

    def close_book(self):
        """Saves progress before closing the document."""
        if self.doc and self.book_data:
            # Save the current page to JSON via LibraryManager
            book_id = self.book_data["id"]
            self.main_window.lib_manager.update_book_progress(book_id, self.current_page)
            
            self.doc.close()
            self.doc = None
            
        self.main_window.switch_to_library()

    def showEvent(self, event):
        """Ensures the reader grabs keyboard focus when opened."""
        super().showEvent(event)
        self.setFocus()