
import sys
import os
from ebooklib import epub
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings('ignore')

def dump_chapter():
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    es_path = os.path.join(base_dir, "Babel (R. F. Kuang) (ES).epub")
    
    book = epub.read_epub(es_path)
    for item in book.get_items():
        if 'titulo.xhtml' in item.get_name():
            print(f"--- Content of {item.get_name()} ---")
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            print(soup.prettify()[:2000]) # First 2000 chars
            
            # Check for images
            imgs = soup.find_all('img')
            print(f"\n--- Images Found: {len(imgs)} ---")
            for img in imgs:
                print(img.get('src'))
            break

if __name__ == "__main__":
    dump_chapter()
