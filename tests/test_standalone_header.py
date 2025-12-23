#!/usr/bin/env python3
"""Test script for is_standalone_numeric_header function."""

import sys
sys.path.insert(0, '/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks')

from align_book import is_standalone_numeric_header

def test_standalone_numeric_header():
    """Test the is_standalone_numeric_header detection."""
    
    # Should return True
    true_cases = [
        "4",
        "42",
        "Chapter 4",
        "CHAPTER 4",
        "Part IV",
        "4.",
        "4:",
        "IV",
        "XII",
        "Ch. 5",
        "Ch 5",
        "Pt. 3",
        "Section 10",
    ]
    
    # Should return False
    false_cases = [
        "4: The Beginning",
        "Chapter 4: Introduction",
        "The Fourth Chapter",
        "Introduction to Chapter 4",
        "A New Beginning",
        "Chapter Four: The Start",
        "",
        "4 - The Journey Begins",
    ]
    
    print("Testing TRUE cases (should be standalone):")
    for text in true_cases:
        result = is_standalone_numeric_header(text)
        status = "✓" if result else "✗ FAIL"
        print(f"  {status} '{text}' -> {result}")
    
    print("\nTesting FALSE cases (should NOT be standalone):")
    for text in false_cases:
        result = is_standalone_numeric_header(text)
        status = "✓" if not result else "✗ FAIL"
        print(f"  {status} '{text}' -> {result}")
    
    # Count failures
    failures = 0
    for text in true_cases:
        if not is_standalone_numeric_header(text):
            failures += 1
    for text in false_cases:
        if is_standalone_numeric_header(text):
            failures += 1
    
    print(f"\n{'='*50}")
    if failures == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {failures} test(s) failed")
    
    return failures == 0

if __name__ == "__main__":
    success = test_standalone_numeric_header()
    sys.exit(0 if success else 1)
