import os
import xml.etree.ElementTree as ET
from align_book import read_opf_data

# Create a dummy OPF with Calibre metadata
dummy_opf = 'test_calibre.opf'
opf_content = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid_id" version="2.0">
  <metadata xmlns:calibre="http://calibre.kovidgoyal.net/2009/metadata" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>Test Book</dc:title>
    <dc:creator opf:role="aut">Test Author</dc:creator>
    <dc:identifier id="uuid_id" opf:scheme="uuid">57e76550-6a75-476c-8208-8df09f78317d</dc:identifier>
    <meta name="calibre:series" content="The Testing Series"/>
    <meta name="calibre:series_index" content="1"/>
    <meta name="cover" content="cover"/>
  </metadata>
  <manifest>
    <item href="cover.jpg" id="cover" media-type="image/jpeg"/>
  </manifest>
</package>
"""

with open(dummy_opf, 'w') as f:
    f.write(opf_content)

print(f"Created {dummy_opf}")

# Test read_opf_data
try:
    data = read_opf_data(dummy_opf)
    print("Read Data Successfully.")
    
    # Check Namespaces
    print("Namespaces:", data.get('namespaces'))
    if 'calibre' in data.get('namespaces', {}):
        print("PASS: Calibre namespace detected.")
    else:
        print("FAIL: Calibre namespace NOT detected.")

    # Check Metadata Items
    found_series = False
    for item in data['metadata_items']:
        print(f"Item: {item['tag']} -> {item['attrib']}")
        if 'calibre:series' in str(item): # Naive string check or check tag/attrib
             found_series = True
        if item.get('attrib', {}).get('name') == 'calibre:series':
             found_series = True
             print("Found series via attrib name")

    if found_series:
        print("PASS: Calibre series metadata found.")
    else:
        print("FAIL: Calibre series metadata NOT found.")
        
except Exception as e:
    print(f"FAIL: Exception during read: {e}")
    import traceback
    traceback.print_exc()

# Clean up
if os.path.exists(dummy_opf):
    os.remove(dummy_opf)
