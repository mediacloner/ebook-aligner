from __future__ import annotations

import logging
from typing import Dict, List, Sequence

from aligner.block_builder import Block
from aligner.paragraph_aligner import AlignedPair

logger = logging.getLogger(__name__)


def attach_orphans(blocks: List[Block], pairs: Sequence[AlignedPair]) -> List[Block]:
    """Attach ES-only events from each ES orphan pair to the nearest block.

    Preference order: previous block first (so the orphan reads as commentary on
    what just happened), then next block, then drop with a warning if no blocks
    exist (unusual — chapter would have to be empty of paragraphs).
    """
    if not blocks or not pairs:
        return blocks

    pair_to_block_idx: Dict[int, List[int]] = {}
    for idx, block in enumerate(blocks):
        pair_to_block_idx.setdefault(id(block.pair), []).append(idx)

    attached = 0
    for pair_idx, pair in enumerate(pairs):
        if not pair.is_es_only:
            continue
        target_idx = None
        for prev in range(pair_idx - 1, -1, -1):
            idxs = pair_to_block_idx.get(id(pairs[prev]))
            if idxs:
                target_idx = idxs[-1]
                break
        if target_idx is None:
            for nxt in range(pair_idx + 1, len(pairs)):
                idxs = pair_to_block_idx.get(id(pairs[nxt]))
                if idxs:
                    target_idx = idxs[0]
                    break
        if target_idx is None:
            logger.warning(
                "Dropping ES orphan pair (no host block); text=%r",
                " ".join(e.text for e in pair.es_events)[:80],
            )
            continue
        blocks[target_idx].es_extras.extend(pair.es_events)
        attached += 1

    if attached:
        logger.info("Attached %d ES orphan pairs to neighbouring blocks", attached)
    return blocks
