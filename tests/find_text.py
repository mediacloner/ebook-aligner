
import os

def search():
    root = 'temp_bilingual/es_full/OEBPS'
    query = "mitad del dinero solicitado" # Subset of the user's string
    
    print(f"Searching for '{query}' in {root}...")
    
    for r, d, f in os.walk(root):
        for file in f:
            if file.endswith('.xhtml') or file.endswith('.html'):
                path = os.path.join(r, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if query in content:
                        print(f"FOUND IN: {path}")
                        # Print context
                        idx = content.find(query)
                        start = max(0, idx - 200)
                        end = min(len(content), idx + 200)
                        print(f"CONTEXT: {content[start:end]}")

if __name__ == "__main__":
    search()
