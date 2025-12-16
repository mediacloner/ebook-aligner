
import difflib
import re

def calculate_quality_score(aligned_data):
    """
    Calculates a quality score (0.0 to 1.0) for an alignment.
    Higher is better.
    """
    if not aligned_data:
        return {'score': 0.0, 'issues': ['No data']}
        
    total_items = len(aligned_data)
    empty_count = 0
    low_sim_count = 0
    dialogue_mismatch_count = 0
    
    total_sim = 0
    valid_pairs = 0
    
    issues = []
    
    for i, item in enumerate(aligned_data):
        en = item.get('en', '').strip()
        es = item.get('es', '').strip()
        
        # 1. Empty Check
        if not en or not es:
            # Ignore structural deletes/inserts if tagged properly?
            # For now, treat as penalty unless explicitly 'delete' tag (which we don't have in final output usually)
            empty_count += 1
            if i < 5: # Debug start
                 issues.append(f"Empty at {i}")
            continue
            
        # 2. Similarity Check
        sim = difflib.SequenceMatcher(None, en, es).ratio()
        total_sim += sim
        valid_pairs += 1
        
        if sim < 0.2:
            low_sim_count += 1
            if len(issues) < 10:
                issues.append(f"Low Sim at {i}: {sim:.2f} ({en[:20]}...)")
            
        # 3. Dialogue Check
        # If EN starts with quote and ES doesn't (or vice versa)
        en_is_dialog = en.startswith(('“', '"', '—', '-'))
        es_is_dialog = es.startswith(('—', '-', '–', '“', '"', '«'))
        
        if en_is_dialog != es_is_dialog:
             # Check if it's just a missing marker or completely different text type
             # Heuristic: Short texts (<50 chars) matching Long text (>200) often signals mismatch
             if abs(len(en) - len(es)) > 100:
                 dialogue_mismatch_count += 1
                 
    # Scoring Formula
    # Base: Average Sim (0-1)
    # Penalties:
    # - Empty Rate (> 10% is bad)
    # - Low Sim Rate (> 10% is bad)
    
    avg_sim = total_sim / valid_pairs if valid_pairs > 0 else 0
    
    empty_rate = empty_count / total_items
    low_sim_rate = low_sim_count / valid_pairs if valid_pairs > 0 else 0
    
    score = avg_sim
    
    # Penalize empty
    score -= (empty_rate * 0.5)
    
    # Penalize low sim (extra penalty on top of average)
    score -= (low_sim_rate * 0.3)
    
    # Normalize
    score = max(0.0, min(1.0, score))
    
    return {
        'score': score,
        'avg_sim': avg_sim,
        'empty_rate': empty_rate,
        'low_sim_rate': low_sim_rate,
        'dialogue_mismatches': dialogue_mismatch_count,
        'total_items': total_items,
        'issues': issues
    }
