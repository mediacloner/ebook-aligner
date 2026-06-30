#!/usr/bin/env python3
"""Re-lay-out the keep-together strategy of an already-generated bilingual EN/ES
EPUB, without re-running alignment. Two target strategies:

``--mode merge`` (recommended for Onyx Boox NeoReader, Moon+ Reader, and other
custom-paginating readers): fold each English paragraph and its Spanish
translation(s) into a SINGLE block — the English text, a ``<br/>``, and a
``<span class="es-tandem">`` per Spanish part. A single block has no between-
block break point, so these readers — which implement little or no CSS
fragmentation and split a wrapper ``<div>`` freely between its children — can no
longer separate the English from its translation across a page. It also unwraps
any leftover ``keeptogether`` ``<div>`` and strips the now-redundant break/margin
hints, so it cleanly upgrades a flat- or wrap-strategy EPUB.

``--mode wrap`` (default, back-compatible): enclose each pair in a single
``<div class="keeptogether" style="page-break-inside:avoid;break-inside:avoid">``.
``break-inside:avoid`` is the most reliably honored break hint among
fragmentation-aware engines (Calibre, ADE), so the pair is pushed whole to the
next page instead of splitting. Readers that fake pagination with CSS
multi-columns ignore it — use ``--mode merge`` for those.

Pairs are detected purely from the ``es-tandem`` markers already in the markup,
so the tool is fast and deterministic. The same logic runs in the live emitter
(``aligner.keep_together.merge_pairs`` / ``wrap_pairs``); this is the post-hoc
path for EPUBs that were already generated.

Usage:
    python scripts/wrap_keep_together.py "Book (bilingual).epub" [--mode merge] [-o out.epub]

By default writes "<name> (<mode>).epub" next to the input; the original is left
untouched.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from typing import Optional, Tuple

from bs4 import BeautifulSoup

# Make the aligner package importable when run as a standalone script. We import
# from aligner.keep_together (BeautifulSoup only) rather than aligner.inline_emitter
# so this tool runs with just bs4 installed — no numpy / ML stack required.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aligner.keep_together import merge_pairs, wrap_pairs  # noqa: E402

_HTML_SUFFIXES = (".xhtml", ".html", ".htm")


def _process_html(path: str, mode: str) -> int:
    """Re-lay-out pairs in a single (X)HTML file in place. Returns pairs changed."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    had_xml_decl = content.lstrip().startswith("<?xml")
    soup = BeautifulSoup(content, "html.parser")
    n = merge_pairs(soup) if mode == "merge" else wrap_pairs(soup, strip_flat=True)
    if n == 0:
        return 0
    out = str(soup)
    # html.parser drops the XML declaration; restore it so the file stays valid
    # XHTML inside the EPUB.
    if had_xml_decl and not out.lstrip().startswith("<?xml"):
        out = "<?xml version='1.0' encoding='utf-8'?>\n" + out
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return n


def _repack(src_dir: str, out_path: str) -> None:
    """Zip src_dir into an EPUB: 'mimetype' first and stored, rest deflated."""
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w") as zf:
        mimetype = os.path.join(src_dir, "mimetype")
        if os.path.isfile(mimetype):
            zf.write(mimetype, "mimetype", compress_type=zipfile.ZIP_STORED)
        for root, _dirs, files in os.walk(src_dir):
            for name in sorted(files):
                full = os.path.join(root, name)
                arc = os.path.relpath(full, src_dir)
                if arc == "mimetype":
                    continue
                zf.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)


def process_epub(
    epub_path: str, out_path: Optional[str] = None, mode: str = "wrap"
) -> Tuple[str, int, int]:
    """Extract, re-lay-out pairs in every (X)HTML file, repack.

    Returns (out_path, files_changed, pairs_changed). The input is untouched.
    """
    if out_path is None:
        base, ext = os.path.splitext(epub_path)
        out_path = f"{base} ({mode}){ext}"
    tmp = tempfile.mkdtemp(prefix=f"epub_{mode}_")
    try:
        with zipfile.ZipFile(epub_path) as zf:
            zf.extractall(tmp)
        files_changed = 0
        pairs = 0
        for root, _dirs, files in os.walk(tmp):
            for name in sorted(files):
                if name.lower().endswith(_HTML_SUFFIXES):
                    n = _process_html(os.path.join(root, name), mode)
                    if n:
                        files_changed += 1
                        pairs += n
                        verb = "merged" if mode == "merge" else "wrapped"
                        print(
                            f"  {os.path.relpath(os.path.join(root, name), tmp)}: "
                            f"{verb} {n} pair(s)"
                        )
        _repack(tmp, out_path)
        return out_path, files_changed, pairs
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("epub", help="Path to the bilingual EPUB to re-lay-out.")
    ap.add_argument(
        "--mode",
        choices=("merge", "wrap"),
        default="wrap",
        help="merge: fold each pair into one block (survives readers with no CSS "
        "break support, e.g. Boox NeoReader / Moon+ Reader). wrap (default): "
        "enclose each pair in a break-inside:avoid <div>.",
    )
    ap.add_argument("-o", "--output", help="Output path (default: '<name> (<mode>).epub').")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.epub):
        print(f"error: not a file: {args.epub}", file=sys.stderr)
        return 2

    out_path, files_changed, pairs = process_epub(args.epub, args.output, args.mode)
    if pairs == 0:
        print(
            "No EN/ES pairs found (no `es-tandem` markers). "
            "Is this a bilingual EPUB from this project's inline mode?",
            file=sys.stderr,
        )
    verb = "Merged" if args.mode == "merge" else "Wrapped"
    print(f"\n{verb} {pairs} pair(s) across {files_changed} file(s).")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
