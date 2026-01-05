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
            str: Corrected Spanish translation
        """
        if not self._ensure_ollama():
            return "[Error: LLM not available for repair]"
            
        try:
            response = self._ollama.chat(model=self.model, messages=[{
                'role': 'user',
                'content': f"""Translate the following English text to Spanish. 
Maintain the tone and style of a literary book.
Do not add any notes, just provide the translation.

ENGLISH: {en_text}

SPANISH:"""
            }])
            
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Repair failed: {e}")
            return f"[Repair Failed: {en_text[:50]}...]"

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
        for i, pair in enumerate(pairs):
            en = pair.get('en', '')
            es = pair.get('es', '')
            
            # Skip if English is too short or empty
            if not en or len(en) < 20:
                continue
            
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


def generate_report(output_path: str, flagged_pairs: list, total_pairs: int) -> str:
    """
    Generate a verification report and save it next to the output EPUB.
    
    Args:
        output_path: Path to the output EPUB file
        flagged_pairs: List of flagged pairs with 'en', 'es', 'llm_confidence' keys
        total_pairs: Total number of pairs processed
    
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
    
    report_lines = [
        "# Bilingual Alignment Verification Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Output File:** `{os.path.basename(output_path)}`",
        "",
        "## Summary",
        "",
        f"- **Total pairs analyzed:** {total_pairs}",
        f"- **Flagged as suspicious:** {len(flagged_pairs)}",
        f"- **Automatically Fixed:** {fixed_count}",
        f"  - 🔍 Vector Search: {fixed_vector}",
        f"  - ✨ LLM Repair: {fixed_llm}",
        f"- **Pass rate:** {pass_rate}",
        "",
    ]
    
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
