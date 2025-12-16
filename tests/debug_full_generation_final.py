
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import create_bilingual_epub, PROFILES

# Set paths (using already extracted temp dirs to avoid re-extraction issues)
en_epub = 'temp_bilingual/en_full'
es_epub = 'temp_bilingual/es_full'
output_epub = 'debug_output_final.epub'

# Run
print("Running create_bilingual_epub...")
create_bilingual_epub(en_epub, es_epub, output_epub)
print("Alignment/Generation Complete.")

# Inspect staging
staging_dir = 'bilingual_epub_staging/OEBPS'
if os.path.exists(staging_dir):
    print("Inspecting staging...")
    files = sorted([f for f in os.listdir(staging_dir) if f.startswith('chapter_')])
    for f in files:
        fpath = os.path.join(staging_dir, f)
        size = os.path.getsize(fpath)
        print(f"  {f}: {size} bytes")
        if size < 100:
            print(f"    WARNING: {f} is suspiciously small/empty!")
    
    print(f"Result: {len(files)} OK, {[f for f in files if os.path.getsize(os.path.join(staging_dir, f)) < 100]} Empty.")
else:
    print("Error: Staging directory not found.")
