import zipfile
import sys
import os

def list_epub_files(epub_path):
    print(f"--- Listing files in: {os.path.basename(epub_path)} ---")
    try:
        with zipfile.ZipFile(epub_path, 'r') as z:
            files = z.namelist()
            # print first 10 and last 10 if many
            has_ncx = any(f.endswith('.ncx') for f in files)
            has_nav = any('nav' in f.lower() and f.endswith('.xhtml') or f.endswith('.html') for f in files)
            
            print(f"Has NCX: {has_ncx}")
            print(f"Has Nav: {has_nav}")
            
            # Print file list (filtered)
            for f in files:
                if f.endswith('.ncx') or 'nav' in f or f.endswith('.opf'):
                    print(f" - {f}")

    except Exception as e:
        print(f"Error reading EPUB: {e}")
    print("\n")

if __name__ == "__main__":
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    files = [
        "Short The Will of the Many EN.epub",
        "Short The Will of the Many ES.epub",
        "Artificial Intelligence - Melanie Mitchell(EN).epub"
    ]
    
    for f in files:
        list_epub_files(os.path.join(base_dir, f))
