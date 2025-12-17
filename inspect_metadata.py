import os
import zipfile
import xml.etree.ElementTree as ET

def find_opf(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith('.opf'):
                return os.path.join(root, f)
    return None

def read_metadata(opf_path):
    print(f"--- Reading {opf_path} ---")
    try:
        tree = ET.parse(opf_path)
        root = tree.getroot()
        ns = {'opf': 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/'}
        
        metadata = root.find('opf:metadata', ns)
        if metadata is None:
            # Try without namespace for metadata tag if partial match
             metadata = root.find('{http://www.idpf.org/2007/opf}metadata')
        
        if metadata is not None:
            for child in metadata:
                tag = child.tag
                text = child.text
                attrib = child.attrib
                print(f"Tag: {tag}")
                print(f"  Text: {text}")
                print(f"  Attr: {attrib}")
        else:
            print("No metadata tag found.")
    except Exception as e:
        print(f"Error: {e}")

print("=== Source OPF (English) ===")
source_dir = 'temp_analysis/en_book'
source_opf = find_opf(source_dir)
if source_opf:
    read_metadata(source_opf)
else:
    print("Source OPF not found.")

print("\n=== Output EPUB (Bilingual) ===")
output_epub = 'bilingual_book.epub'
if os.path.exists(output_epub):
    with zipfile.ZipFile(output_epub, 'r') as z:
        # Find OPF in zip
        opf_name = None
        for n in z.namelist():
            if n.endswith('.opf'):
                opf_name = n
                break
        
        if opf_name:
            print(f"Found OPF in generated EPUB: {opf_name}")
            with z.open(opf_name) as f:
                # Parse directly from file object? ET.parse needs seekable usually, but verify
                # Better to read str
                content = f.read()
                # writes to temp to parse easily or parse string
                root = ET.fromstring(content)
                ns = {'opf': 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/'} 
                # Note: our output might use proper namespaces or not, let's just dump children of metadata
                # The output code sets xmlns:opf and xmlns:dc.
                
                metadata = root.find('{http://www.idpf.org/2007/opf}metadata')
                if metadata is not None:
                    for child in metadata:
                         print(f"Tag: {child.tag}")
                         print(f"  Text: {child.text}")
                         print(f"  Attr: {child.attrib}")
                else:
                    print("No metadata tag in output.")

        else:
            print("No OPF found in output EPUB.")
else:
    print("Output EPUB not found.")
