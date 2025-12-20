import zipfile
import sys
import os
import re

def inspect_epub(epub_path):
    print(f"--- Inspecting: {os.path.basename(epub_path)} ---")
    try:
        with zipfile.ZipFile(epub_path, 'r') as z:
            # Find an HTML file that looks like a chapter
            html_files = [f for f in z.namelist() if f.endswith('.html') or f.endswith('.xhtml')]
            
            target_file = None
            # Heuristic: Pick a file that isn't cover, toc, or very small
            for f in html_files:
                info = z.getinfo(f)
                if info.file_size > 5000 and 'cover' not in f.lower() and 'toc' not in f.lower() and 'nav' not in f.lower():
                    target_file = f
                    break
            
            if not target_file and html_files:
                target_file = html_files[0]
                
            if target_file:
                print(f"Reading sample file: {target_file}")
                with z.open(target_file) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    # Print first 2000 chars
                    print(content[:2000])
                    
                    print("\n--- HTML Tags Analysis ---")
                    # Simple regex to find classes
                    classes = re.findall(r'class="([^"]+)"', content)
                    print(f"Common classes: {set(classes)}")
                    
                    tags = re.findall(r'<([a-zA-Z0-9]+)', content)
                    print(f"Common tags: {set(tags)}")
            else:
                print("No suitable HTML content found.")
                
    except Exception as e:
        print(f"Error reading EPUB: {e}")
    print("\n")

if __name__ == "__main__":
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    files = [
        "Short The Will of the Many EN.epub",
        "Short The Will of the Many ES.epub",
        "Artificial Intelligence - Melanie Mitchell(EN).epub" # Control
    ]
    
    for f in files:
        inspect_epub(os.path.join(base_dir, f))
