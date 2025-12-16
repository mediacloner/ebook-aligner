
import zipfile
import os

books_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
out_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/temp_skyward"

en_epub = os.path.join(books_dir, "Skyward - Brandon Sanderson(EN).epub")
es_epub = os.path.join(books_dir, "Skyward - Brandon Sanderson(ES).epub")

os.makedirs(os.path.join(out_dir, "en"), exist_ok=True)
os.makedirs(os.path.join(out_dir, "es"), exist_ok=True)

try:
    with zipfile.ZipFile(en_epub, 'r') as z:
        z.extractall(os.path.join(out_dir, "en"))
    print("Extracted EN")
except Exception as e:
    print(f"Failed EN: {e}")

try:
    with zipfile.ZipFile(es_epub, 'r') as z:
        z.extractall(os.path.join(out_dir, "es"))
    print("Extracted ES")
except Exception as e:
    print(f"Failed ES: {e}")
