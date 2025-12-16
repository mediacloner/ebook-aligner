
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import split_sentences

text = "The dream of creating an intelligent machine—one that is as smart as or smarter than humans—is centuries old but became part of modern science with the rise of digital computers. In fact, the ideas that led to the first programmable computers came out of mathematicians’ attempts to understand human thought—particularly logic—as a mechanical process of “symbol manipulation.” Digital computers are essentially symbol manipulators, pushing around combinations of the symbols 0 and 1. To pioneers of computing like Alan Turing and John von Neumann, there were strong analogies between computers and the human brain, and it seemed obvious to them that human intelligence could be replicated in computer programs."

sents = split_sentences(text)
print(f"Original Length: {len(text)}")
print(f"Split into {len(sents)} sentences.")
for i, s in enumerate(sents):
    print(f"[{i}] {s[:50]}...")
