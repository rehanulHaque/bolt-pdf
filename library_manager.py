import json
import os
import uuid
import shutil
from pathlib import Path
import fitz  # PyMuPDF


class LibraryManager:
    """Handles JSON storage and PDF management for the library."""
    
    def __init__(self):
        self.base_path = Path("LibraryData")
        self.covers_path = self.base_path / "covers"
        self.books_file = self.base_path / "books.json"
        self._init_storage()

    def _init_storage(self):
        """Initialize storage directories and files."""
        self.covers_path.mkdir(parents=True, exist_ok=True)
        if not self.books_file.exists():
            with open(self.books_file, 'w', encoding='utf-8') as f:
                json.dump({"books": []}, f)

    def load_books(self):
        """Load all books from the JSON file."""
        with open(self.books_file, 'r', encoding='utf-8') as f:
            return json.load(f).get("books", [])

    def add_book(self, pdf_path):
        doc = fitz.open(pdf_path)
        book_id = f"book_{uuid.uuid4().hex[:8]}"
        title = doc.metadata.get("title") or os.path.basename(pdf_path)
        total_pages = doc.page_count
        
        # Generate and save ONLY the cover image
        cover_path = self.covers_path / f"{book_id}.png"
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
        pix.save(str(cover_path))
        doc.close()

        # REMOVED shutil.copy()!
        # We now just store the absolute path to where the file originally lives.
        original_path = str(Path(pdf_path).resolve())

        book_data = {
            "id": book_id,
            "title": title,
            "file_path": original_path, # <-- Points to your original file
            "cover": str(cover_path),
            "page_count": total_pages,
            "last_page": 0,
            "progress": 0.0
        }

        books = self.load_books()
        books.append(book_data)
        with open(self.books_file, 'w', encoding='utf-8') as f:
            json.dump({"books": books}, f, indent=4)
        
        return book_data
    def update_book_progress(self, book_id, current_page):
        """Updates the last read page and progress percentage in JSON."""
        books = self.load_books()
        for book in books:
            if book["id"] == book_id:
                book["last_page"] = current_page
                # Calculate progress percentage (0.0 to 1.0)
                book["progress"] = current_page / max(1, book.get("page_count", 1) - 1)
                break
        
        # Save back to JSON
        with open(self.books_file, 'w', encoding='utf-8') as f:
            json.dump({"books": books}, f, indent=4)
    def update_book_genre(self, book_id, new_genre):
        """Updates the genre/collection of a specific book."""
        books = self.load_books()
        for book in books:
            if book["id"] == book_id:
                book["genre"] = new_genre
                break
        
        with open(self.books_file, 'w', encoding='utf-8') as f:
            json.dump({"books": books}, f, indent=4)

    def get_all_genres(self):
        """Scans the library and returns a sorted list of unique genres."""
        books = self.load_books()
        genres = set()
        for book in books:
            genres.add(book.get("genre", "Uncategorized"))
        
        # Sort alphabetically, but keep "Uncategorized" at the bottom if it exists
        sorted_genres = sorted(list(genres))
        if "Uncategorized" in sorted_genres:
            sorted_genres.remove("Uncategorized")
            sorted_genres.append("Uncategorized")
            
        return sorted_genres
    def delete_book(self, book_id):
        """Removes a book from JSON and deletes its cover image."""
        books = self.load_books()
        for i, book in enumerate(books):
            if book["id"] == book_id:
                # Delete the cover image to save disk space
                cover_path = Path(book.get("cover", ""))
                if cover_path.exists() and cover_path.is_file():
                    try:
                        cover_path.unlink()
                    except Exception as e:
                        print(f"Could not delete cover: {e}")
                
                # Remove from list
                del books[i]
                break
                
        # Save updated list back to JSON
        with open(self.books_file, 'w', encoding='utf-8') as f:
            json.dump({"books": books}, f, indent=4)