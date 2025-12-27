import re
import math

class Splitter:
    def __init__(self, aligner=None, trigger_length=280):
        """
        Initialize Splitter.
        :param aligner: Optional instance of NeuralAligner for semantic matching of splits.
        :param trigger_length: Threshold in characters to trigger splitting (default 280).
        """
        self.aligner = aligner
        self.trigger_length = trigger_length 

    def split_sentences(self, text):
        """
        Splits text into sentences using pySBD for better accuracy with abbreviations.
        """
        if not text:
            return []
        
        try:
            import pysbd
            seg = pysbd.Segmenter(language="en", clean=False)
            sentences = seg.segment(text)
            return [s.strip() for s in sentences if s.strip()]
        except ImportError:
            print("Warning: pySBD not found, falling back to regex splitting")
            # Fallback: End punctuation + optional quotes + whitespace + Next is Upper/Start
            pattern = r'([.!?…]+(?:[”"’\'\)\]»]*)\s+(?=[A-Z¿¡"\'\-]))'
            
            parts = re.split(pattern, text)
            sentences = []
            current_sent = ""
            
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    current_sent += part
                else:
                    current_sent += part
                    sentences.append(current_sent.strip())
                    current_sent = ""
                    
            if current_sent and current_sent.strip():
                sentences.append(current_sent.strip())
                
            return sentences

    def process_pair(self, en_text, es_text, debug=False):
        """
        Splits a single aligned pair if english text represents > 3 lines.
        Returns a list of dicts [{'en': ..., 'es': ...}, ...]
        """
        original_pair = [{'en': en_text, 'es': es_text}]
        
        if not en_text or len(en_text) < self.trigger_length:
            return original_pair
        
        print(f"Splitter: Triggered for text length {len(en_text)}") 
            
        en_sents = self.split_sentences(en_text)
        if len(en_sents) <= 1:
            return original_pair
            
        # We need to group EN sentences into chunks of approx trigger_length
        # but only split at logical sentence boundaries.
        
        en_chunks_text = []
        en_chunks_tails = []
        current_chunk = ""
        current_tail = ""
        
        for sent in en_sents:
            if len(current_chunk) + len(sent) > self.trigger_length and len(current_chunk) > 50:
                # Close current chunk
                en_chunks_text.append(current_chunk.strip())
                en_chunks_tails.append(current_tail)
                
                current_chunk = sent
                current_tail = sent
            else:
                current_chunk += (" " + sent) if current_chunk else sent
                current_tail = sent
        
        if current_chunk:
            en_chunks_text.append(current_chunk.strip())
            en_chunks_tails.append(current_tail)
            
        if len(en_chunks_text) == 1:
            return original_pair
            
        # Now we have EN partitions. We need to partitions ES to match.
        es_sents = self.split_sentences(es_text)
        
        # If we have the aligner, we can do this semantically.
        # Otherwise, we fallback to length ratio.
        
        final_splits = []
        
        if self.aligner and es_sents:
             # Neural Split Mapping
             # We want to map groups of ES sents to the EN chunks.
             # Approach: 
             # 1. Embed all EN chunks.
             # 2. Embed all ES sentences.
             # 3. For each ES sentence, assign it to the EN chunk it matches best?
             #    No, ES sentences must remain ordered. This is a segmentation problem.
             #    We want to find cut points in ES_sents that maximize similarity to EN_chunks.
             
             # Simpler: Accumulate ES sentences until they "fill" the first EN chunk semantically.
             
             en_embs = self.aligner.embed_chunks([{'text': t} for t in en_chunks_text])
             # Also embed tails for boundary refinement
             en_tail_embs = self.aligner.embed_chunks([{'text': t} for t in en_chunks_tails])
             
             es_embs = self.aligner.embed_chunks([{'text': t} for t in es_sents])
             
             import numpy as np
             from scipy.spatial.distance import cosine
             
             es_idx = 0
             
             for i, en_chunk in enumerate(en_chunks_text):
                 if es_idx >= len(es_sents):
                     final_splits.append({'en': en_chunk, 'es': ""})
                     continue
                     
                 if i == len(en_chunks_text) - 1:
                     remainder = " ".join(es_sents[es_idx:])
                     final_splits.append({'en': en_chunk, 'es': remainder})
                     break
                 
                 # Greedy search using vector math
                 best_cut = es_idx + 1
                 best_score = float('inf') # using distance (lower is better)
                 
                 en_vec = en_embs[i]
                 en_len = len(en_chunk)
                 
                 current_es_str = ""
                 
                 # Limit search window
                 max_lookahead = min(len(es_sents) - es_idx, 20)
                 
                 for k in range(max_lookahead):
                     idx = es_idx + k
                     sent = es_sents[idx]
                     current_es_str += (" " + sent) if current_es_str else sent
                     
                     # Ratio Check
                     # Fast fail based on length
                     ratio = len(current_es_str) / en_len
                     if ratio < 0.4: continue 
                     if ratio > 2.2: break 
                     
                     # Vector Aggregation (Mean Pooling)
                     # es_embs[es_idx : idx+1]
                     # We want the mean of these vectors to compare with en_vec
                     # Check shapes
                     relevant_vecs = es_embs[es_idx : idx+1]
                     # If using standard list of arrays from embed_chunks?
                     # Ideally embed_chunks returns a numpy matrix. 
                     # If it returns list of arrays, we stack.
                     
                     if not isinstance(relevant_vecs, np.ndarray):
                         relevant_vecs = np.vstack(relevant_vecs)
                         
                     # Mean vector
                     cand_vec = np.mean(relevant_vecs, axis=0)
                     
                     dist = cosine(en_vec, cand_vec)
                     
                     # --- TAIL BONUS ---
                     # Check if the cut point allows the last ES sentence to match the last EN sentence
                     # idx is the index of the last included ES sentence
                     es_tail_vec = es_embs[idx]
                     en_tail_vec = en_tail_embs[i]
                     tail_sim = 1 - cosine(en_tail_vec, es_tail_vec)
                     
                     if tail_sim > 0.4:
                         # Apply bonus (reduce distance)
                         dist -= 0.25
                     
                     if dist < best_score:
                         best_score = dist
                         best_cut = idx + 1
                         
                 # Construct best match text
                 # Note: we need to reconstruct the string for the best cut
                 best_es_text = " ".join(es_sents[es_idx:best_cut])
                 final_splits.append({'en': en_chunk, 'es': best_es_text})
                 es_idx = best_cut

        else:
            # Fallback: Ratio based splitting
            total_en_len = len(en_text)
            total_es_len = len(es_text)
            
            es_sents = self.split_sentences(es_text)
            es_idx = 0
            
            for i, en_chunk in enumerate(en_chunks_text):
                if i == len(en_chunks_text) - 1:
                    rem = " ".join(es_sents[es_idx:])
                    final_splits.append({'en': en_chunk, 'es': rem})
                    break
                    
                target_ratio = len(en_chunk) / total_en_len
                target_len = target_ratio * total_es_len
                
                accum_len = 0
                chunk_sents = []
                while es_idx < len(es_sents):
                    s = es_sents[es_idx]
                    accum_len += len(s)
                    chunk_sents.append(s)
                    es_idx += 1
                    if accum_len >= target_len:
                        break
                
                final_splits.append({'en': en_chunk, 'es': " ".join(chunk_sents)})

        # Post-Processing: Add asterism signs
        for i in range(len(final_splits)):
            if i < len(final_splits) - 1:
                final_splits[i]['en'] += " ⁂"
                if final_splits[i]['es']:
                     # Check if it ends with punctuation?
                     final_splits[i]['es'] += " ⁂"
        
        return final_splits

    def process_all(self, aligned_pairs):
        """
        Process the entire list of aligned chunks.
        """
        new_aligned = []
        for item in aligned_pairs:
            en = item['en']
            es = item['es']
            tag = item['tag']
            classes = item.get('classes', [])
            
            # Only split paragraphs
            if tag == 'p' and en and es:
                splits = self.process_pair(en, es)
                if len(splits) == 1:
                     # No split (or single chunk result). Preserve original structure including raw_html.
                     # We update text just in case process_pair did some cleanup, but usually it's same.
                     combined = item.copy()
                     combined['en'] = splits[0]['en']
                     combined['es'] = splits[0]['es']
                     new_aligned.append(combined)
                else:
                    for split in splits:
                        # Construct new item preserving original props (classes, tag, node, etc.)
                        new_item = item.copy()
                        new_item['en'] = split['en']
                        new_item['es'] = split['es']
                        # raw_html is invalid for splits, clear it
                        new_item['raw_html'] = None 
                        new_aligned.append(new_item)
            else:
                new_aligned.append(item)
                
        return new_aligned
