
import sys
import os
import warnings
from ebooklib import epub
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

def find_chapter(epub_path, search_term):
    book = epub.read_epub(epub_path)
    print(f"Searching for '{search_term}' in {os.path.basename(epub_path)}...")
    
    for item in book.get_items():
        if item.get_type() == 9: # EpubHtml
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            
            if search_term.lower() in text.lower():
                print(f"!!! FOUND match in Item: {item.get_name()} (ID: {item.get_id()})")
                # find index
                idx = text.lower().find(search_term.lower())
                print(f"Context: ...{text[max(0, idx-50):min(len(text), idx+100)]}...")
                print("-" * 40)

if __name__ == "__main__":
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    en_book = os.path.join(base_dir, "Artificial Intelligence - Melanie Mitchell(EN).epub")
    
    find_chapter(en_book, "word2vec")
