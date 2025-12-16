import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from align_book import align_chunks

def test_issue_10():
    print("Testing Issue 10: Aggressive Phase 2 Merge causing Data Loss")
    
    # Setup: 
    # EN[1] is split into ES[1], ES[2], ES[3]
    # But EN[2] and EN[3] exist and claim ES[2] and ES[3] initially due to 1-to-1 Phase 1.
    
    english_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'I stalked my enemy carefully through the cavern.', 'es': '', 'text': 'I stalked my enemy carefully through the cavern.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'I’d taken off my boots so they wouldn’t squeak. I’d removed my socks so I wouldn’t slip. The rock under my feet was comfortably cool as I took another silent step forward.', 'es': '', 'text': 'I’d taken off my boots so they wouldn’t squeak. I’d removed my socks so I wouldn’t slip. The rock under my feet was comfortably cool as I took another silent step forward.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'This deep, the only light came from the faint glow of the worms on the ceiling, feeding off the moisture seeping through cracks. You had to sit for minutes in the darkness for your eyes to adjust to that faint light.', 'es': '', 'text': 'This deep, the only light came from the faint glow of the worms on the ceiling, feeding off the moisture seeping through cracks. You had to sit for minutes in the darkness for your eyes to adjust to that faint light.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Another quiver in the shadows. There, near those dark lumps that must be enemy fortifications. I froze in a crouch, listening to my enemy scratch the rock as he moved. I imagined a Krell: a terrible alien with red eyes and dark armor.', 'es': '', 'text': 'Another quiver in the shadows. There, near those dark lumps that must be enemy fortifications. I froze in a crouch, listening to my enemy scratch the rock as he moved. I imagined a Krell: a terrible alien with red eyes and dark armor.'},
    ]

    spanish_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Aceché a mi enemigo con sigilo por la caverna.', 'text': 'Aceché a mi enemigo con sigilo por la caverna.'},
        # Split starts here
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Me había quitado las botas para que no chirriaran.', 'text': 'Me había quitado las botas para que no chirriaran.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Me había sacado los calcetines para no resbalar.', 'text': 'Me había sacado los calcetines para no resbalar.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'La roca bajo mis pies me transmitió un cómodo frescor al dar otro silencioso paso adelante.', 'text': 'La roca bajo mis pies me transmitió un cómodo frescor al dar otro silencioso paso adelante.'},
        # Next paragraphs
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'A esa profundidad, la única luz la emitía el tenue brillo de los gusanos del techo, que se alimentaban de la humedad que se filtraba por las grietas.', 'text': 'A esa profundidad, la única luz la emitía el tenue brillo de los gusanos del techo, que se alimentaban de la humedad que se filtraba por las grietas.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Había que sentarse unos minutos en la oscuridad para que los ojos se adaptaran a esa luz tan leve.', 'text': 'Había que sentarse unos minutos en la oscuridad para que los ojos se adaptaran a esa luz tan leve.'}, 
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Otro temblor en las sombras.', 'text': 'Otro temblor en las sombras.'},
    ]
    
    aligned = align_chunks(english_chunks, spanish_chunks)
    
    print("\nResulting Alignment:")
    for idx, item in enumerate(aligned):
        en_snip = item.get('en', '')[:40].replace('\n', ' ')
        es_snip = item.get('es', '')[:40].replace('\n', ' ')
        ratio = len(item.get('es', '')) / len(item.get('en', '')) if len(item.get('en', '')) > 0 else 0
        print(f"{idx}: Ratio={ratio:.2f}\n    EN: '{en_snip}...'\n    ES: '{es_snip}...'")
        
        # Validation checks
        if "This deep" in item.get('en', '') and not item.get('en', '').strip():
             print("CRITICAL: 'This deep' paragraph is missing or empty!")

if __name__ == "__main__":
    test_issue_10()
