
import sys
import os
import warnings
from ebooklib import epub
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')

def get_chapter_text(item):
    soup = BeautifulSoup(item.get_content(), 'html.parser')
    return soup.get_text()

def find_chapter(epub_path, search_terms):
    book = epub.read_epub(epub_path)
    count = 0
    found = False
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            text = get_chapter_text(item)
            # Check if ALL terms are present
            if all(term in text for term in search_terms):
                print(f"Found {search_terms} in item: {item.get_name()} (id: {item.get_id()})")
                idx = text.find(search_terms[0])
                start = max(0, idx - 50)
                end = min(len(text), idx + 200)
                print(f"Snippet: {text[start:end]}...")
                found = True
                # Don't return immediately, find all occurrences
    
    if not found:
        print(f"Terms {search_terms} not found in {epub_path}")

if __name__ == "__main__":
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    en_book = os.path.join(base_dir, "Artificial Intelligence - Melanie Mitchell(EN).epub")
    es_book = os.path.join(base_dir, "Artificial Intelligence - Melanie Mitchell(ES).epub")

    print(f"Searching English book: {en_book}")
    find_chapter(en_book, ["hamburger", "ordered"])
    
    print(f"\nSearching Spanish book: {es_book}")
    find_chapter(es_book, ["hamburguesa", "pidió"])
