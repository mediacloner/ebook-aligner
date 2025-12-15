import os
import sys
import shutil
# Ensure we can import from local dir
sys.path.append(os.getcwd())

from align_book import create_bilingual_epub, PROFILES

def debug_full():
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir): return
    jobs = [os.path.join(uploads_dir, d) for d in os.listdir(uploads_dir) if os.path.isdir(os.path.join(uploads_dir, d))]
    jobs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    if not jobs: return
    latest_job = jobs[0]
    print(f"Job: {latest_job}")

    def find_opf_root(d):
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith('.opf'): return root
        return None

    en_base = find_opf_root(os.path.join(latest_job, 'en_extract'))
    es_base = find_opf_root(os.path.join(latest_job, 'es_extract'))
    
    output = "debug_output.epub"
    
    # Run creation
    print("Running create_bilingual_epub...")
    try:
        # Pass generic config or auto detect? The function does auto-detect if config is None.
        create_bilingual_epub(en_base, es_base, output, config=None)
    except Exception as e:
        print(f"Creation failed: {e}")
        import traceback
        traceback.print_exc()
        
    # Inspect staging
    staging = "bilingual_epub_staging"
    if os.path.exists(staging):
        print("Inspecting staging...")
        oebps = os.path.join(staging, 'OEBPS')
        files = os.listdir(oebps)
        files.sort()
        count_empty = 0
        count_ok = 0
        for f in files:
            if f.endswith('.xhtml'):
                path = os.path.join(oebps, f)
                size = os.path.getsize(path)
                print(f"  {f}: {size} bytes")
                if size < 100: count_empty += 1
                else: count_ok += 1
        print(f"Result: {count_ok} OK, {count_empty} Empty.")
    else:
        print("Staging dir not found!")

if __name__ == "__main__":
    debug_full()
