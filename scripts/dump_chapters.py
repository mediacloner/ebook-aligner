
import sys
import os
import warnings
from ebooklib import epub
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

def dump_chapters(epub_path):
    book = epub.read_epub(epub_path)
    print(f"--- Dumping chapters for {os.path.basename(epub_path)} ---")
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            print(f"Item: {item.get_name()}")
            print(f"Length: {len(text)}")
            print(f"Start: {text[:200].replace(chr(10), ' ')}")
            print("-" * 20)
            if "hamburg" in text.lower():
                print("!!! Found 'hamburg' in this item !!!")

if __name__ == "__main__":
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    en_book = os.path.join(base_dir, "Artificial Intelligence - Melanie Mitchell(EN).epub")
    
    dump_chapters(en_book)
