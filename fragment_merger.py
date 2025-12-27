"""
Sentence Fragment Merger

Detects and merges sentence fragments that were incorrectly split by
formatting symbols (e.g., ⁂, *, ---).

Example Issue:
  EN: ["...where Mrs. ⁂", "Jones was already snoring."]
  ES: ["...donde ya roncaba la señora Jones. ⁂"]
  
Without merge: Misalignment
With merge: Correct alignment
"""

import re


def is_sentence_fragment(chunk):
    """
    Detect if a chunk is likely a sentence fragment.
    
    A fragment is a chunk that:
    - Ends with a scene break symbol (⁂, *, ---)
    - AND doesn't end with sentence-ending punctuation
    - OR is very short (< 20 chars) and doesn't start with capital
    """
    text = chunk['text'].strip()
    
    if not text:
        return False
    
    # Check if ends with scene break without proper sentence ending
    # Pattern: text ⁂ (without .!? before ⁂)
    if re.search(r'[^.!?]\s*[⁂*\-—]{1,3}$', text):
        return True
    
    # Check if very short and doesn't start with capital (continuation)
    if len(text) < 20 and not text[0].isupper():
        return True
    
    return False


def should_merge_with_next(current_chunk, next_chunk):
    """
    Determine if current chunk should merge with next chunk.
    
    Merge if:
    - Current ends with fragment marker (Mrs. ⁂)
    - Next likely continues the sentence
    """
    if not current_chunk or not next_chunk:
        return False
    
    current_text = current_chunk['text'].strip()
    next_text = next_chunk['text'].strip()
    
    # Pattern 1: Current ends with "Name ⁂" and next starts with "Name"
    # Example: "Mrs. ⁂" + "Jones was..."
    if re.search(r'\b[A-Z][a-z]+\.?\s*⁂$', current_text):
        # Check if next starts with likely continuation
        if next_text and next_text[0].isupper():
            # Could be continuation (Jones) or new sentence
            # Heuristic: if short (< 30 chars), likely continuation
            if len(next_text) < 30:
                return True
    
    # Pattern 2: Current ends with incomplete clause
    # Keywords: "where", "when", "and", "but", "or"
    incomplete_endings = r'\b(where|when|and|but|or|while|as|that|which)\s+[A-Z][a-z]*\.?\s*⁂$'
    if re.search(incomplete_endings, current_text, re.IGNORECASE):
        return True
    
    return False


def merge_sentence_fragments(chunks):
    """
    Pre-process chunks to merge sentence fragments.
    
    Args:
        chunks: List of chunk dictionaries
        
    Returns:
        Merged list of chunks
    """
    if len(chunks) <= 1:
        return chunks
    
    merged = []
    i = 0
    
    while i < len(chunks):
        current = chunks[i]
        
        # Look ahead to see if we should merge
        if i + 1 < len(chunks):
            next_chunk = chunks[i + 1]
            
            if should_merge_with_next(current, next_chunk):
                # Merge current and next
                merged_text = current['text'].rstrip() + ' ' + next_chunk['text'].lstrip()
                merged_chunk = {
                    **current,  # Copy all fields from current
                    'text': merged_text,
                    'merged_from': [current.get('raw_html', ''), next_chunk.get('raw_html', '')]
                }
                merged.append(merged_chunk)
                i += 2  # Skip next chunk (already merged)
                continue
        
        # No merge, keep as-is
        merged.append(current)
        i += 1
    
    return merged
