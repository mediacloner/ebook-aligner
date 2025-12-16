
import re

def split_sentences_debug(text):
    print(f"Text: '{text[:50]}...'")
    # Original Regex
    pattern = r'(?<=[.!?])(?:[”\"’\'\)\\]»]*)\s+(?=[A-Z¿¡\"\'\-])'
    parts = re.split(pattern, text)
    print(f"Parts (Original): {len(parts)}")
    for i, p in enumerate(parts):
        print(f"  {i}: '{p[:20]}...'")

    print("\nAttempting Capturing Group Strategy:")
    # Split keeping the delimiter
    parts_v2 = re.split(r'([.!?]+(?:[”\"’\'\)\\]»]*)\s+)(?=[A-Z¿¡\"\'\-])', text)
    # Note: I kept lookahead for Capital just to ensure we don't split "Dr. Smith".
    # But lookbehind is removed. We capture punctuation + space.
    
    print(f"Parts (V2 Raw): {len(parts_v2)}")
    reconstructed = []
    current = ""
    for p in parts_v2:
        if not p: continue
        # If p is a delimiter (matches regex), append to previous?
        # Capturing group makes delimiter appear as SEPARATE item.
        # But here delimiter is at END of sentence logic.
        # "Igneous" + ". " + "My"
        # We want "Igneous."
        # So we append p to current, UNLESS p is start of new?
        # Actually identifying delimiter is hard if text chunks look same.
        pass
    
    # Better Strategy:
    # re.findall?
    
    # Strategy 3: Compile regex and iterate matches?
    
    # Let's try your simpler suggestion: 
    # Use split with capturing group for ". "
    parts_simple = re.split(r'([.!?]+(?:[”\"’\'\)\\]»]*)\s+)', text)
    final_sents = []
    current_sent = ""
    for i, p in enumerate(parts_simple):
        if i % 2 == 0:
            current_sent += p
        else:
            # This is separator. Check if next starts with Capital?
            # We can't check next here easily without lookahead.
            # But normally we assume split is correct.
            sep = p
            # Check if sep looks like end of sentence? "." is good. "Mr." is bad.
            # Assuming robust split, we append sep to current_sent.
            current_sent += sep
            final_sents.append(current_sent.strip())
            current_sent = ""
            
    if current_sent: final_sents.append(current_sent.strip())
    
    print(f"Final Sents (Simple): {len(final_sents)}")
    for i, s in enumerate(final_sents):
         print(f"  {i}: '{s[:50]}...'")

    print("\nAttempting Brute Force Trivial Split:")
    print(f"Text Repr: {repr(text)}")
    parts_trivial = re.split(r'(\. )', text)
    print(f"Parts (Trivial): {len(parts_trivial)}")
    for i, p in enumerate(parts_trivial):
        print(f"  {i}: '{p}'")



if __name__ == "__main__":
    t_en = "I stepped up to the hole and looked out on Igneous. My home cavern and the largest of the underground cities that made up the Defiant League. My perch was high, providing me with a stunning view of a large cave filled with boxy apartments built like cubes splitting off one another."
    split_sentences_debug(t_en)
