import os
import shutil
import time

UPLOADS_DIR = 'uploads'
STAGING_DIR = 'bilingual_epub_staging'

def cleanup():
    print("Cleaning up...")
    
    # 1. Clean uploads
    if os.path.exists(UPLOADS_DIR):
        print(f"Removing contents of {UPLOADS_DIR}...")
        for item in os.listdir(UPLOADS_DIR):
            path = os.path.join(UPLOADS_DIR, item)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"  Removed {item}")
            except Exception as e:
                print(f"  Failed to remove {item}: {e}")
    else:
        print(f"{UPLOADS_DIR} does not exist.")
        os.makedirs(UPLOADS_DIR)
        
    # 2. Clean staging
    if os.path.exists(STAGING_DIR):
        print(f"Removing {STAGING_DIR}...")
        try:
            shutil.rmtree(STAGING_DIR)
        except Exception as e:
            print(f"Failed to remove {STAGING_DIR}: {e}")
            
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup()
