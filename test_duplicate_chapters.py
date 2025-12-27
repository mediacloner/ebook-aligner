#!/usr/bin/env python3
"""
Test case to verify that align_tocs prevents duplicate chapter mapping.
Reproduces the scenario where Spanish Chapter 9 was reused for EN Chapters 9, 10, and footer.
"""

import sys
sys.path.insert(0, '/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks')

from align_book import align_tocs

def test_no_duplicate_mapping():
    """
    Scenario: EN has chapters 1-10 + footer
             ES has chapters 1-9 (missing 10)
    Expected: Each ES chapter used only ONCE
    """
    # Simulate English TOC
    en_toc = []
    for i in range(1, 11):
        en_toc.append({
            'label': f'Chapter {i}',
            'src': f'chapter{i:02d}.xhtml',
            'level': 1
        })
    en_toc.append({
        'label': 'Footer',
        'src': 'footer.xhtml',
        'level': 1
    })
    
    # Simulate Spanish TOC (missing Chapter 10)
    es_toc = []
    for i in range(1, 10):  # Only 1-9
        es_toc.append({
            'label': f'Capítulo {i}',
            'src': f'Sec{i:04d}.xhtml',
            'level': 1
        })
    
    print("EN TOC:")
    for item in en_toc:
        print(f"  {item['label']} -> {item['src']}")
    
    print("\nES TOC:")
    for item in es_toc:
        print(f"  {item['label']} -> {item['src']}")
    
    # Run alignment
    result = align_tocs(en_toc, es_toc)
    
    print(f"\n=== ALIGNMENT RESULT ({len(result)} pairs) ===")
    
    # Track used Spanish sources
    used_es = {}
    duplicates_found = False
    
    for label, en_src, es_src, level in result:
        print(f"{label:20s} | EN: {en_src or 'None':20s} | ES: {es_src or 'None':20s}")
        
        if es_src:
            if es_src in used_es:
                print(f"  ❌ DUPLICATE! '{es_src}' was already used for '{used_es[es_src]}'")
                duplicates_found = True
            else:
                used_es[es_src] = label
    
    print("\n=== TEST RESULT ===")
    if duplicates_found:
        print("❌ FAILED: Duplicates detected!")
        return False
    else:
        print("✅ PASSED: No duplicates, strict 1-to-1 mapping enforced!")
        return True

if __name__ == '__main__':
    success = test_no_duplicate_mapping()
    sys.exit(0 if success else 1)
