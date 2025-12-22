
import sys
import os
import warnings
from ebooklib import epub
import xml.etree.ElementTree as ET

warnings.filterwarnings('ignore')

def parse_toc(ncx_path):
    tree = ET.parse(ncx_path)
    root = tree.getroot()
    ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
    
    def parse_navpoint(node, level, ns):
        items = []
        try:
            label = node.find('./ncx:navLabel/ncx:text', ns).text
        except:
            label = "Unknown"
        
        try:
            content = node.find('./ncx:content', ns).get('src')
        except:
            content = ""
            
        items.append({'label': label.strip(), 'src': content, 'level': level})
        for child in node.findall('./ncx:navPoint', ns):
            items.extend(parse_navpoint(child, level + 1, ns))
        return items

    nav_points = []
    for nav_point in root.findall('./ncx:navMap/ncx:navPoint', ns):
         nav_points.extend(parse_navpoint(nav_point, 0, ns))
    return nav_points

def dump_toc(epub_path):
    book = epub.read_epub(epub_path)
    print(f"--- TOC for {os.path.basename(epub_path)} ---")
    
    # Find NCX
    ncx_item = None
    for item in book.get_items():
        if item.get_type() == 4: # EPUB_NCX usually
             # But ebooklib might not set type 4 consistently?
             pass
        if 'ncx' in item.get_name().lower() and item.get_name().endswith('.ncx'):
             ncx_item = item
             break
             
    if not ncx_item:
        # Fallback to verify logic
        print("No NCX item found explicitly. Searching all items...")
        for item in book.get_items():
             if item.get_media_type() == 'application/x-dtbncx+xml':
                 ncx_item = item
                 break
                 
    if not ncx_item:
        print("CRITICAL: No NCX file found in EPUB!")
        return

    # Extract NCX content to temp file to parse with ElementTree (lazy way)
    temp_ncx = "temp_toc.ncx"
    with open(temp_ncx, 'wb') as f:
        f.write(ncx_item.get_content())
        
    toc = parse_toc(temp_ncx)
    for i, item in enumerate(toc):
        print(f"[{i}] {item['label']}  (Src: {item['src']})")
        
    if os.path.exists(temp_ncx): os.remove(temp_ncx)

if __name__ == "__main__":
    base_dir = "/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/books"
    en_book = os.path.join(base_dir, "Babel (R. F. Kuang) (EN).epub")
    es_book = os.path.join(base_dir, "Babel (R. F. Kuang) (ES).epub")
    
    dump_toc(en_book)
    print("\n" + "="*40 + "\n")
    dump_toc(es_book)
