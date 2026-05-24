"""
Local LLM-based alignment verification using Ollama.

This module provides optional post-alignment verification to flag
potentially misaligned translation pairs using a local LLM.

Requirements:
    - Ollama installed and running: brew install ollama && ollama serve
    - A multilingual model pulled: ollama pull qwen2.5:7b

Usage:
    from llm_verifier import AlignmentVerifier
    verifier = AlignmentVerifier()
    result = verifier.verify_pair("Hello world", "Hola mundo")
"""

import subprocess
import sys
import time
import re


def is_valid_spanish(text: str) -> bool:
    """
    Check if text is valid Spanish (no Chinese/Japanese/Korean characters).
    
    Detects when the LLM outputs metadata or non-Spanish text instead of translation.
    """
    if not text:
        return False
    # Chinese characters
    if re.search(r'[\u4e00-\u9fff]', text):
        return False
    # Japanese hiragana and katakana
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return False
    # Korean hangul
    if re.search(r'[\uac00-\ud7af]', text):
        return False
    return True


# Check if ollama is available
def check_ollama_installed():
    """Check if Ollama is installed and accessible."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                               capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_ollama_running():
    """Check if Ollama server is running by trying to connect."""
    try:
        import urllib.request
        req = urllib.request.urlopen('http://localhost:11434/api/tags', timeout=2)
        return req.status == 200
    except:
        return False


def start_ollama():
    """Try to start Ollama server in background."""
    try:
        print("Starting Ollama server...")
        # Start ollama serve in background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        start_new_session=True)
        # Wait a bit for it to start
        for _ in range(10):
            time.sleep(1)
            if check_ollama_running():
                print("Ollama server started successfully")
                return True
        print("Ollama server started but not responding yet")
        return False
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False


def install_ollama_package():
    """Install the ollama Python package if not present."""
    try:
        import ollama
        return True
    except ImportError:
        print("Installing ollama Python package...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ollama', '-q'])
        return True
        return True


class AlignmentVerifier:
    """Verifies bilingual alignment pairs using a local Ollama model."""
    
    # Class-level cache to prevent repeated checks across instances/threads
    _class_available = None
    _class_ollama = None
    _class_model_checked = set()  # Track which models have been verified
    
    def __init__(self, model: str = 'qwen2.5:7b'):
        """
        Initialize the verifier.
        
        Args:
            model: Ollama model to use. Recommended multilingual models:
                   - qwen2.5:7b (best for EN/ES)
                   - llama3.2:8b
                   - command-r
        """
        self.model = model
        self._ollama = None
        self._available = None
    
    def _ensure_ollama(self):
        """Lazy-load ollama and check availability. Auto-starts server and installs model if needed."""
        # Check class-level cache first (shared across all instances/threads)
        if AlignmentVerifier._class_available is not None and self.model in AlignmentVerifier._class_model_checked:
            self._available = AlignmentVerifier._class_available
            self._ollama = AlignmentVerifier._class_ollama
            return self._available
        
        if not check_ollama_installed():
            print("WARNING: Ollama not installed. Install with: brew install ollama")
            print("         Download from: https://ollama.com/download")
            self._available = False
            AlignmentVerifier._class_available = False
            return False
        
        # Check if Ollama server is running, start if needed
        if not check_ollama_running():
            print("Ollama server not running. Attempting to start...")
            if not start_ollama():
                print("WARNING: Could not start Ollama server. Please run: ollama serve")
                self._available = False
                AlignmentVerifier._class_available = False
                return False
        
        try:
            install_ollama_package()
            import ollama
            self._ollama = ollama
            AlignmentVerifier._class_ollama = ollama
            
            # Check if model is available, if not try to pull it
            if self.model not in AlignmentVerifier._class_model_checked:
                try:
                    models = ollama.list()
                    model_names = [m.get('name', '') for m in models.get('models', [])]
                    if not any(self.model in name for name in model_names):
                        print(f"Model {self.model} not found. Downloading...")
                        # Pull the model (this may take a while)
                        ollama.pull(self.model)
                        print(f"Model {self.model} downloaded successfully.")
                    AlignmentVerifier._class_model_checked.add(self.model)
                except Exception as pull_err:
                    print(f"Warning: Could not verify/pull model: {pull_err}")
            
            self._available = True
            AlignmentVerifier._class_available = True
        except Exception as e:
            print(f"WARNING: Failed to load ollama: {e}")
            self._available = False
            AlignmentVerifier._class_available = False
        
        return self._available
    
    def verify_pair(self, en_text: str, es_text: str) -> dict:
        """
        Verify if an EN-ES pair is semantically aligned.
        
        Args:
            en_text: English text
            es_text: Spanish text
        
        Returns:
            dict with keys:
                - is_match: bool - whether texts are aligned
                - confidence: float - confidence score (0.0-1.0)
                - raw: str - raw LLM response
        """
        if not self._ensure_ollama():
            return {'is_match': True, 'confidence': 0.5, 'raw': 'Ollama not available'}
        
        # Truncate long texts
        en_truncated = en_text[:300] if len(en_text) > 300 else en_text
        es_truncated = es_text[:300] if len(es_text) > 300 else es_text
        
        try:
            response = self._ollama.chat(model=self.model, messages=[{
                'role': 'user',
                'content': f"""Is this a correct English-Spanish translation pair?

ENGLISH: {en_truncated}
SPANISH: {es_truncated}

Reply with ONLY "YES" or "NO" followed by a confidence percentage (0-100%)."""
            }])
            
            text = response['message']['content'].upper()
            is_match = 'YES' in text[:10]  # Check first 10 chars
            
            # Try to extract confidence
            import re
            conf_match = re.search(r'(\d+)\s*%', text)
            confidence = int(conf_match.group(1)) / 100.0 if conf_match else (0.9 if is_match else 0.3)
            
            return {
                'is_match': is_match,
                'confidence': confidence,
                'raw': response['message']['content']
            }
        except Exception as e:
            print(f"LLM verification failed: {e}")
            return {'is_match': True, 'confidence': 0.5, 'raw': str(e)}
    
    def repair_translation(self, en_text: str) -> str:
        """
        Generate a fresh translation for a misaligned English text.
        
        Args:
            en_text: English text to translate
            
        Returns:
            str: Corrected Spanish translation with ± marker
        """
        if not self._ensure_ollama():
            return "[Error: LLM not available for repair]"
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Progressive prompting strategy
                if attempt == 0:
                    messages = [{
                        'role': 'user',
                        'content': f"""Translate the following English text to Spanish. 
Maintain the tone and style of a literary book.
Do not add any notes, just provide the translation.

ENGLISH: {en_text}

SPANISH:"""
                    }]
                elif attempt == 1:
                    # Stricter prompt with system message
                    messages = [
                        {
                            'role': 'system',
                            'content': 'You are a professional translator. You ONLY output Spanish text. Never output Chinese, Japanese, or any other language.'
                        },
                        {
                            'role': 'user',
                            'content': f"""Translate to Spanish ONLY:

{en_text}"""
                        }
                    ]
                else:
                    # Last resort: most explicit prompt
                    messages = [
                        {
                            'role': 'system',
                            'content': 'Eres un traductor profesional de inglés a español. Solo respondes en español.'
                        },
                        {
                            'role': 'user',
                            'content': f"""Traduce este texto al español:

"{en_text}"

Traducción:"""
                        }
                    ]
                
                response = self._ollama.chat(model=self.model, messages=messages)
                translation = response['message']['content'].strip()
                
                # Clean up common issues
                # Remove "Traducción:" prefix if present
                if translation.lower().startswith('traducción:'):
                    translation = translation[11:].strip()
                
                # Validate the output
                if is_valid_spanish(translation):
                    return f"{translation} ±"  # Mark as LLM-generated
                else:
                    print(f"Invalid translation detected (attempt {attempt + 1}/{max_retries}): contains non-Spanish characters")
                    if attempt < max_retries - 1:
                        continue  # Retry with stricter prompt
                    else:
                        # Last attempt failed, return partial translation with error note
                        # Try to extract any valid Spanish portion
                        clean = ''.join(c for c in translation if ord(c) < 0x3000 or ord(c) > 0xFFFF)
                        if clean.strip():
                            return f"{clean.strip()} [partial] ±"
                        return f"[Translation Error: {en_text[:50]}...] ±"
                        
            except Exception as e:
                print(f"Repair failed: {e}")
                return f"[Repair Failed: {en_text[:50]}...] ±"
        
        return f"[Translation Error] ±"

    def batch_verify(self, pairs: list, threshold: float = 0.6) -> list:
        """
        Verify multiple alignment pairs, flagging suspicious ones.
        
        Args:
            pairs: List of dicts with 'en' and 'es' keys
            threshold: Minimum similarity to consider aligned
        
        Returns:
            The same list with added 'llm_verified' and 'llm_confidence' keys
        """
        if not self._ensure_ollama():
            return pairs
        
        flagged_count = 0
        previous_es = None  # Track previous Spanish text for duplicate detection
        
        for i, pair in enumerate(pairs):
            en = pair.get('en', '')
            es = pair.get('es', '')
            
            # Skip if English is too short or empty
            if not en or len(en) < 20:
                previous_es = es
                continue
            
            # DUPLICATE DETECTION: Flag if Spanish is identical to previous row
            if previous_es and es and len(es) > 50:
                # Check for exact match
                if es == previous_es:
                    print(f"Flagging DUPLICATE translation: {en[:40]}...")
                    pair['llm_verified'] = False
                    pair['llm_confidence'] = 0.05  # Very low confidence
                    pair['_duplicate_translation'] = True
                    flagged_count += 1
                    previous_es = es
                    continue
                # Also check if current ES is a substring of previous (partial duplicate)
                elif len(es) > 100 and (previous_es.startswith(es[:100]) or es.startswith(previous_es[:100])):
                    print(f"Flagging OVERLAPPING translation: {en[:40]}...")
                    pair['llm_verified'] = False
                    pair['llm_confidence'] = 0.10
                    pair['_overlapping_translation'] = True
                    flagged_count += 1
                    previous_es = es
                    continue
            
            previous_es = es  # Update tracking for next iteration
            
            # CRITICAL CHECK: If English is present but Spanish is missing/empty, FLAG IT!
            if not es or len(es) < 5:  # Allow very short Spanish if it's just "Sí" but usually < 5 is suspicious for a >20 char English sentence
                 print(f"Flagging empty/missing translation for: {en[:30]}...")
                 pair['llm_verified'] = False
                 pair['llm_confidence'] = 1.0 # High confidence it's wrong
                 flagged_count += 1
                 continue

            # Only verify pairs that might be problematic
            # (e.g., very different lengths, no shared words)
            len_ratio = len(es) / len(en)
            
            # GAP FIX: Detect OVER-LONG translations (ES is much longer than EN)
            if len_ratio > 4.0:
                print(f"Flagging over-long translation (ratio={len_ratio:.1f}): {en[:30]}...")
                pair['llm_verified'] = False
                pair['llm_confidence'] = 0.15
                pair['_overlong_translation'] = True
                flagged_count += 1
                continue
            
            if len_ratio < 0.3 or len_ratio > 3.0:
                result = self.verify_pair(en, es)
                pair['llm_verified'] = result['is_match']
                pair['llm_confidence'] = result['confidence']
                if not result['is_match']:
                    flagged_count += 1
                    # print(f"Flagged pair {i}: EN='{en[:30]}...' ES='{es[:30]}...'")
        
        if flagged_count:
            print(f"LLM verification flagged {flagged_count} suspicious pairs")
        
        return pairs


# Convenience function for standalone verification
def verify_translation(en_text: str, es_text: str, model: str = 'qwen2.5:7b') -> bool:
    """Quick verification of a single translation pair."""
    verifier = AlignmentVerifier(model=model)
    result = verifier.verify_pair(en_text, es_text)
    return result['is_match']


def generate_report(output_path: str, flagged_pairs: list, total_pairs: int, alignment_mode: str = None, stats: dict = None) -> str:
    """
    Generate a verification report and save it next to the output EPUB.
    
    Args:
        output_path: Path to the output EPUB file
        flagged_pairs: List of flagged pairs with 'en', 'es', 'llm_confidence' keys
        total_pairs: Total number of pairs processed
        alignment_mode: Optional alignment mode indicator ('split' or 'preserve')
        stats: Optional dictionary with 'en_chars', 'es_chars', 'count' for metrics
    
    Returns:
        Path to the generated report file
    """
    import os
    from datetime import datetime
    
    # Create report path next to the EPUB
    base_path = output_path.rsplit('.', 1)[0]
    report_path = f"{base_path}_verification_report.md"
    
    # Build report content
    # Build report content
    fixed_count = sum(1 for p in flagged_pairs if p.get('_was_fixed'))
    
    # Breakdown by method
    fixed_vector = sum(1 for p in flagged_pairs if 'Vector Search' in p.get('_repair_method', ''))
    fixed_llm = sum(1 for p in flagged_pairs if 'LLM Repair' in p.get('_repair_method', ''))
    
    pass_rate = "N/A"
    if total_pairs > 0:
        pass_rate = f"{((total_pairs - len(flagged_pairs)) / total_pairs * 100):.1f}%"
    
    # Calculate pass rate with vector search (naturally passing + vector search fixes)
    vector_search_rate = "N/A"
    if total_pairs > 0:
        # Pairs that passed naturally + pairs fixed via vector search
        passed_naturally = total_pairs - len(flagged_pairs)
        vector_search_rate = f"{((passed_naturally + fixed_vector) / total_pairs * 100):.1f}%"
    
    report_lines = [
        "# Bilingual Alignment Verification Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Output File:** `{os.path.basename(output_path)}`",
        f"**Alignment Mode:** {'📝 Preserve Paragraphs' if alignment_mode == 'preserve' else '✂️ Split into Sentences'}",
        "",
        "## Summary",
        "",
        f"- **Total pairs analyzed:** {total_pairs}",
        f"- **Flagged as suspicious:** {len(flagged_pairs)}",
        f"- **Automatically Fixed:** {fixed_count}",
        f"  - 🔍 Vector Search: {fixed_vector}",
        f"  - ✨ LLM Repair: {fixed_llm}",
        f"- **Pass rate:** {pass_rate}",
        f"- **Pass rate with Vector Search:** {vector_search_rate}",
        "",
    ]
    
    if stats and stats.get('count', 0) > 0:
        avg_en = stats.get('en_chars', 0) / stats.get('count', 1)
        avg_es = stats.get('es_chars', 0) / stats.get('count', 1)
        # Check alignment balance (ratio of chars)
        ratio = avg_es / avg_en if avg_en > 0 else 0
        report_lines.insert(14, f"- **Avg Chunk Length:** EN: {avg_en:.1f} chars | ES: {avg_es:.1f} chars (Ratio: {ratio:.2f})")

    
    if flagged_pairs:
        report_lines.extend([
            "## Flagged & Fixed Pairs",
            "",
            "The following translation pairs were identified as misaligned:",
            "",
        ])
        
        for i, pair in enumerate(flagged_pairs, 1):
            en = pair.get('en', '')[:200]
            es_current = pair.get('es', '')[:200]
            
            # If fixed, we want to show the ORIGINAL Spanish that was replaced
            es_original = pair.get('_original_es', es_current)[:200]
            was_fixed = pair.get('_was_fixed', False)
            conf = pair.get('llm_confidence', 'N/A')
            
            status_icon = "✅ FIXED" if was_fixed else "⚠️ FLAGGED"
            
            # Special labeling for duplicate issues
            if pair.get('_duplicate_translation'):
                status_icon = "🔁 DUPLICATE" if not was_fixed else "🔁 DUPLICATE (FIXED)"
            elif pair.get('_overlapping_translation'):
                status_icon = "🔀 OVERLAPPING" if not was_fixed else "🔀 OVERLAPPING (FIXED)"
            elif pair.get('_overlong_translation'):
                status_icon = "📏 OVER-LONG" if not was_fixed else "📏 OVER-LONG (FIXED)"
            elif pair.get('_multi_paragraph_es'):
                status_icon = "🔀 MULTI-PARA" if not was_fixed else "🔀 MULTI-PARA (FIXED)"
            
            report_lines.extend([
                f"### Issue {i} {status_icon}",
                "",
                f"**English:** {en}{'...' if len(pair.get('en', '')) > 200 else ''}",
                "",
                f"**Original Spanish:** {es_original}{'...' if len(pair.get('_original_es', '')) > 200 else ''}",
                ""
            ])
            
            if was_fixed:
                method_label = pair.get('_repair_method', '✨ LLM Repair')
                
                # For LLM repairs, show what the vector search found (for threshold analysis)
                vector_score = pair.get('_vector_score')
                if vector_score is not None and 'LLM Repair' in method_label:
                    report_lines.extend([
                         f"**🔍 Vector Search ({vector_score:.2f}):** {es_original}{'...' if len(pair.get('_original_es', '')) > 200 else ''}",
                         ""
                    ])
                
                report_lines.extend([
                     f"**{method_label}:** {es_current}{'...' if len(pair.get('es', '')) > 200 else ''}",
                     ""
                ])
                
            report_lines.extend([
                f"**Confidence:** {conf}",
                "",
                "---",
                "",
            ])
    else:
        report_lines.extend([
            "## Result",
            "",
            "✅ **All pairs passed verification.** No issues detected.",
            "",
        ])
    
    report_lines.extend([
        "## How to Fix Issues",
        "",
        "If you see flagged pairs above:",
        "",
        "1. Open the EPUB in Calibre or Sigil",
        "2. Search for the English text shown above", 
        "3. Check if the Spanish translation below it is correct",
        "4. Manually edit the Spanish text if needed",
        "",
        "---",
        "*Report generated by llm_verifier.py using Ollama*",
    ])
    
    # Write report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Verification report saved to: {report_path}")
    return report_path


if __name__ == "__main__":
    # Test the verifier
    print("Testing LLM Verifier...")
    
    verifier = AlignmentVerifier()
    
    # Good pair
    result = verifier.verify_pair(
        "The quick brown fox jumps over the lazy dog.",
        "El rápido zorro marrón salta sobre el perro perezoso."
    )
    print(f"Good pair: is_match={result['is_match']}, confidence={result['confidence']}")
    
    # Bad pair (mismatched)
    result = verifier.verify_pair(
        "I went to the store yesterday.",
        "El gato está durmiendo en el sofá."
    )
    print(f"Bad pair: is_match={result['is_match']}, confidence={result['confidence']}")
