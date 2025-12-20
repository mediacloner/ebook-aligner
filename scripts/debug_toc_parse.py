import sys
import os
import xml.etree.ElementTree as ET

# Re-implement parse_toc here to avoid importing the whole app
def parse_toc(ncx_path):
    print(f"Parsing: {ncx_path}")
    tree = ET.parse(ncx_path)
    root = tree.getroot()
    
    # Handle namespaces
    ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
    
    # Robust finder
    def find_text(node, xpath):
        found = node.find(xpath, ns)
        if found is not None and found.text:
            return found.text
        return ""

    nav_points = []
    
    # Find all navPoints recursively (flattened)
    for nav_point in root.findall('.//ncx:navPoint', ns):
        label = find_text(nav_point, './ncx:navLabel/ncx:text')
        content_node = nav_point.find('./ncx:content', ns)
        content = content_node.get('src') if content_node is not None else ""
        
        nav_points.append({'label': label.strip(), 'src': content})
    return nav_points

def main():
    en_toc = parse_toc('temp_debug_toc/en/toc.ncx')
    es_toc = parse_toc('temp_debug_toc/es/toc.ncx')
    
    print("\n--- EN TOC ---")
    for item in en_toc:
        print(f"{item['label']} -> {item['src']}")

    print("\n--- ES TOC ---")
    for item in es_toc:
        print(f"{item['label']} -> {item['src']}")

if __name__ == "__main__":
    main()
