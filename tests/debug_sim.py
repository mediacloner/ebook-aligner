
from difflib import SequenceMatcher

def debug_sim():
    s1 = "I carefully picked my way through the debris, keeping my head low."
    s2 = "Avancé con cuidado por entre los escombros, manteniendo la cabeza baja."
    # Case 2: Split Spanish (Good Match)
    s3 = "I'm offering you a job. I need a new assistant, and you're the only one I can trust."
    s4 = "Lo que te ofrezco es un trabajo. Necesito un nuevo ayudante, y eres la única en quien puedo confiar."
    
    # Case 3: N-to-1 Merge (Bad Match - Noise) -- EN1 vs ES2
    s5 = "My father’s dream had come true. In defeating the Krell that day over nine years ago, those fledgling starfighter pilots had inspired a nation."
    s6 = "Todos juntos, nos hacíamos llamar los Desafiantes, por el nombre de nuestra nave insignia original."
    
    # Case 4: True Match (EN1 vs ES1)
    s7 = "My father’s dream had come true."
    s8 = "El sueño de mi padre se había hecho realidad."
    
    print(f"Sim 1 (Random): {SequenceMatcher(None, s1, s2).ratio():.3f}")
    print(f"Sim 2 (Split Good): {SequenceMatcher(None, s3, s4).ratio():.3f}")
    print(f"Sim 3 (Merge Bad): {SequenceMatcher(None, s5, s6).ratio():.3f}")
    print(f"Sim 4 (True Match): {SequenceMatcher(None, s7, s8).ratio():.3f}")
    
    s9 = "“She doesn’t approve,” I whispered."
    s10 = "—No lo aprueba —susurré."
    print(f"Sim 5 (Pull Down): {SequenceMatcher(None, s9, s10).ratio():.3f}")


if __name__ == "__main__":
    debug_sim()
