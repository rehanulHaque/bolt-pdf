from PySide6.QtWidgets import QMainWindow, QStackedWidget

from library_manager import LibraryManager
from library_view import LibraryView
from reader_view import ReaderView


class MainWindow(QMainWindow):
    """Main application window - routes between library and reader views."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bolt PDF")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #ffffff; color: #333333;")
        
        self.lib_manager = LibraryManager()
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.library_view = LibraryView(self)
        self.reader_view = ReaderView(self)
        
        self.stack.addWidget(self.library_view)
        self.stack.addWidget(self.reader_view)
        
        self.library_view.populate()

    def switch_to_reader(self, book_data):
        """Switch to the reader view with the selected book."""
        self.reader_view.open_book(book_data)
        self.stack.setCurrentWidget(self.reader_view)

    def switch_to_library(self):
        """Switch back to the library view."""
        self.stack.setCurrentWidget(self.library_view)
        self.library_view.populate()
