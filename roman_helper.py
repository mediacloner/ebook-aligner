
def roman_to_int(s):
    """
    Convert Roman numeral string to integer.
    """
    s = s.upper().strip().rstrip('.')
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
            int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
        else:
            int_val += rom_val[s[i]]
    return int_val

def extract_roman(text):
    """
    Extract first valid Roman numeral from header-like text.
    Handles 'Chapter IV', 'Part XI', 'IX'
    """
    import re
    # Look for Roman numeral at end or standalone
    # "Chapter IV" -> IV
    # "IV." -> IV
    # "The Age of Innocence" -> None
    # "Start of XIX Century" -> XIX (maybe)
    
    match = re.search(r'\b([IVXLCDM]+)\.?', text, re.IGNORECASE)
    if match:
        # Verify it's not just a word like 'I' or 'A' (A not roman here) 
        # But 'I' is valid. 'MIX' is valid. 'CIVIL' is valid? No, too generic.
        # Restrict to strictly standard structural Romans if inside text
        # Or simple check if the text is SHORT (< 20 chars).
        if len(text) < 30:
            return match.group(1)
    return None
