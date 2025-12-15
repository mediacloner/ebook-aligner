import re
import html

content = """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es">
<head><title></title><link rel="stylesheet" type="text/css" href="0.css"/></head>
<body><h2><img src="3.png" alt="Imagen"/></h2>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p class="c">CAPÍTULO 1</p><p>&nbsp;</p><p>Cuando llegó la luz, estuvo a punto de partirle el cerebro.</p>
"""

print(f"Content length: {len(content)}")

def check(content):
    p_matches = re.findall(r'<p(?:\s+[^>]*)?>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
    print(f"Found {len(p_matches)} p tags.")
    for i, p_text in enumerate(p_matches):
        clean = re.sub(r'<[^>]+>', '', p_text).strip()
        clean = html.unescape(clean)
        if not clean: 
            print(f"[{i}] Skipping empty.")
            continue
        
        print(f"[{i}] checking '{clean}'")
        
        if len(clean) > 80: 
            print("  -> too long")
            continue
        
        norm = clean.lower().replace('í', 'i').replace('á', 'a').replace('é', 'e').replace('ó', 'o').replace('ú', 'u')
        print(f"  -> norm: '{norm}'")
        
        if 'capitulo' in norm or 'parte' in norm or 'prologo' in norm or 'epilogo' in norm or 'chapter' in norm:
             print("  -> MATCH KEYWORD")
             return clean
             
        if any(c.isdigit() for c in clean) and len(clean) < 30:
             print("  -> MATCH DIGIT")
             return clean
    return "NO MATCH"

res = check(content)
print(f"Result: {res}")
