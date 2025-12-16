import os
import urllib.request
import tarfile
import lzma
import xml.etree.ElementTree as ET
import shutil
from io import BytesIO

# Configuration
DICTIONARY_URL = "https://download.freedict.org/dictionaries/eng-spa/2024.10.10/freedict-eng-spa-2024.10.10.src.tar.xz"
LOCAL_ARCHIVE_PATH = "freedict-eng-spa.tar.xz"
LOCAL_DICT_PATH = "freedict-eng-spa.tei"

class DictionaryLoader:
    def __init__(self, check_download=True):
        self.dictionary = {}
        if check_download:
            self.ensure_dictionary_exists()
        if os.path.exists(LOCAL_DICT_PATH):
            self.load_dictionary()

    def ensure_dictionary_exists(self):
        if os.path.exists(LOCAL_DICT_PATH):
            print(f"Dictionary found at {LOCAL_DICT_PATH}")
            return

        print("Dictionary not found. Attempting download...")
        try:
            print(f"Downloading {DICTIONARY_URL}...")
            with urllib.request.urlopen(DICTIONARY_URL) as response:
                with open(LOCAL_ARCHIVE_PATH, 'wb') as f:
                    shutil.copyfileobj(response, f)
            print("Download successful. Extracting...")
            
            with tarfile.open(LOCAL_ARCHIVE_PATH, "r:xz") as tar:
                # Find the TEI file
                tei_member = None
                for member in tar.getmembers():
                    if member.name.endswith(".tei"):
                        tei_member = member
                        break
                
                if tei_member:
                    print(f"Found TEI file: {tei_member.name}")
                    f = tar.extractfile(tei_member)
                    with open(LOCAL_DICT_PATH, 'wb') as out:
                        shutil.copyfileobj(f, out)
                    print("Extraction successful.")
                else:
                    print("Could not find .tei file in archive.")
                    
            # Cleanup archive
            if os.path.exists(LOCAL_ARCHIVE_PATH):
                os.remove(LOCAL_ARCHIVE_PATH)
                
        except Exception as e:
            print(f"Error downloading/extracting dictionary: {e}")
            if os.path.exists(LOCAL_ARCHIVE_PATH):
                os.remove(LOCAL_ARCHIVE_PATH)
        
        if not os.path.exists(LOCAL_DICT_PATH):
            print("Could not obtain dictionary. Features disabled.")

    def load_dictionary(self):
        print("Loading dictionary...")
        try:
            tree = ET.parse(LOCAL_DICT_PATH)
            root = tree.getroot()
            
            # TEI Namespace (it might change, usually standard)
            ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
            # Handle cases where namespace might be default or different
            # We can use wildcard if parsing fails or check root tag
            
            # Check namespace usage in the file
            # If root tag is {http://www.tei-c.org/ns/1.0}TEI, use ns
            
            has_ns = root.tag.startswith('{')
            
            count = 0
            entries = root.findall('.//tei:entry', ns) if has_ns else root.findall('.//entry')
            
            for entry in entries:
                orth = entry.find('.//tei:orth', ns) if has_ns else entry.find('.//orth')
                if orth is not None and orth.text:
                    word = orth.text.lower().strip()
                    translations = set()
                    
                    cits = entry.findall('.//tei:cit[@type="trans"]', ns) if has_ns else entry.findall('.//cit[@type="trans"]')
                    for cit in cits:
                        quote = cit.find('tei:quote', ns) if has_ns else cit.find('quote')
                        if quote is not None and quote.text:
                            trans_list = quote.text.lower().strip()
                            for t in trans_list.split(','): # Sometimes comma separated
                                t_clean = t.strip()
                                if t_clean:
                                    translations.add(t_clean)
                    
                    if translations:
                        if word in self.dictionary:
                            self.dictionary[word].update(translations)
                        else:
                            self.dictionary[word] = translations
                        count += 1
            
            print(f"Loaded {count} entries.")
            
        except Exception as e:
            print(f"Error parsing dictionary: {e}")
            import traceback
            traceback.print_exc()

    def get_translations(self, word):
        return self.dictionary.get(word.lower(), set())

def calculate_semantic_overlap(en_text, es_text, dict_loader):
    """
    Calculates overlap between English text and Spanish text.
    Returns a score (0.0 to 1.0) representing the fraction of English content words 
    that have a translation present in the Spanish text.
    """
    if not en_text or not es_text:
        return 0.0
        
    # Simple Tokenization
    def tokenize(text):
        return set(word.lower().strip(".,;:?!()[]'\"") for word in text.split() if len(word) > 2)

    en_tokens = tokenize(en_text)
    es_tokens = tokenize(es_text)
    
    if not en_tokens:
        return 0.0

    match_count = 0
    checked_count = 0
    
    # Common stop words to skip
    STOP_WORDS = {
        'the', 'and', 'that', 'with', 'from', 'this', 'have', 'for', 'not', 'are', 'was', 'were', 
        'but', 'all', 'can', 'your', 'has', 'one', 'his', 'her', 'they', 'our', 'abc',
        'she', 'him', 'you'
    }

    for en_word in en_tokens:
        if en_word in STOP_WORDS:
            continue
            
        checked_count += 1
        translations = dict_loader.get_translations(en_word)
        
        # Check direct match of translations
        if any(trans in es_tokens for trans in translations):
            match_count += 1
        # Fallback: check if en_word is arguably in es_text (cognates or names)
        elif en_word in es_tokens:
            match_count += 1
        # Partial match? (e.g. 'compute' in 'computadora')
        # Maybe too noisy.
            
    if checked_count == 0:
        return 0.0
        
    return match_count / checked_count

if __name__ == "__main__":
    loader = DictionaryLoader()
    print("Test: 'computer' ->", loader.get_translations('computer'))
    print("Test: 'house' ->", loader.get_translations('house'))
