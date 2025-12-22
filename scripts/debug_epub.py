
import sys
import os
import warnings
from ebooklib import epub

warnings.filterwarnings('ignore')

def debug_epub_structure(epub_path):
    print(f"Reading {epub_path}...")
    try:
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"Error reading EPUB: {e}")
        return

    print("Listing ALL items:")
    count = 0
    for item in book.get_items():
        print(f"Id: {item.get_id()}, Type: {item.get_type()}, Name: {item.get_name()}")
        count += 1
        if count > 20:
            print("... (stopping after 20 items)")
            break
            
    if count == 0:
        print("No items found in the book!")

if __name__ == "__main__":
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    en_book = os.path.join(base_dir, "Artificial Intelligence - Melanie Mitchell(EN).epub")
    debug_epub_structure(en_book)
