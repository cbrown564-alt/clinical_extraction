#!/usr/bin/env python3
"""Parse a two-voice audio script into merged, generation-ready blocks.

Consecutive turns by the same speaker are merged into one block so that each
becomes a single text-to-speech call. Reports the character count and credit
cost per block, and flags blocks that exceed the per-request limit.

Usage:
    python3 scripts/audio/prep_blocks.py docs/audio/scripts/flagship_the_argument.md
"""

import json
import re
import sys
from pathlib import Path

# eleven_v3 per-request character ceiling
MAX_CHARS = 3000


def parse(path: Path):
    text = path.read_text(encoding="utf-8")

    # Body starts after the episode-notes separator; turns are "### NN X" headings.
    turns = []
    pattern = re.compile(r"^### (\d+) ([NS])\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            turns.append({"n": int(m.group(1)), "speaker": m.group(2), "text": body})
    return turns


def merge(turns):
    blocks = []
    for turn in turns:
        if blocks and blocks[-1]["speaker"] == turn["speaker"]:
            blocks[-1]["text"] += "\n\n" + turn["text"]
            blocks[-1]["turns"].append(turn["n"])
        else:
            blocks.append(
                {"speaker": turn["speaker"], "text": turn["text"], "turns": [turn["n"]]}
            )
    for i, b in enumerate(blocks, 1):
        b["index"] = i
        b["chars"] = len(b["text"])
    return blocks


def main():
    path = Path(sys.argv[1])
    blocks = merge(parse(path))

    out = path.parent / (path.stem + ".blocks.json")
    out.write_text(json.dumps(blocks, indent=2), encoding="utf-8")

    total = sum(b["chars"] for b in blocks)
    narrator = sum(b["chars"] for b in blocks if b["speaker"] == "N")
    skeptic = total - narrator

    print(f"{path.name}: {len(blocks)} blocks from {sum(len(b['turns']) for b in blocks)} turns")
    print(f"  narrator {narrator:,} chars | skeptic {skeptic:,} chars | total {total:,}")
    print(f"  v3 cost: {total:,} credits | runtime ~{total / 830:.1f} min")
    print()
    for b in blocks:
        flag = "  <-- OVER LIMIT" if b["chars"] > MAX_CHARS else ""
        opener = " ".join(b["text"].split()[:4])[:34]
        print(f"  {b['index']:2d}  {b['speaker']}  {b['chars']:5,}  {opener}{flag}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
