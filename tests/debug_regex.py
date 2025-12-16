import re

def test_regex():
    text = "¿Cuándo has llegado? —A mitad de la charla. ¿No me has visto entrar?"
    
    # Current Regex in align_book.py
    pattern = r'([.!?]+(?:[”"’\'\)\]»]*)\s+(?=[A-Z¿¡"\'\-—–]))'
    
    parts = re.split(pattern, text)
    print(f"Text: '{text}'")
    print(f"Pattern: {pattern}")
    print(f"Parts: {parts}")
    
    # Test Char Codes
    print("\nChar Codes:")
    for i, c in enumerate(text):
         print(f"{i}: '{c}' ({ord(c)})")
         if c == '—': print("  ^-- EM DASH detected")
         if c == '?': print("  ^-- QUESTION MARK")

if __name__ == "__main__":
    test_regex()
