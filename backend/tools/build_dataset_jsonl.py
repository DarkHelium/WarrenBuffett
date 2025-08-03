#!/usr/bin/env python3
"""build_dataset_jsonl.py

Utility to convert raw Warren-Buffett source texts (books and transcripts)
into a single JSON-Lines file for fast downstream loading.

• Reads every *.txt file inside
  backend/agent/warren-buffett-dataset/extracted_texts
  backend/agent/warren-buffett-dataset/transcripts_raw
• Cleans whitespace, splits each file into fixed-size character chunks
• Writes each chunk as a JSON object to warren_buffett_dataset.jsonl
  with metadata: {source, chunk_id, text}

Run once after adding new raw files:
    python backend/tools/build_dataset_jsonl.py

The resulting JSONL (~6 MB) is reproducible; commit or .gitignore per team policy.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import sys

# -------- configuration --------
CHUNK_SIZE = 2000  # characters per chunk; adjust if needed
RAW_FOLDERS = ["extracted_texts", "transcripts_raw"]
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent / "agent" / "warren-buffett-dataset"
OUTPUT_PATH = BASE_DIR / "processed_knowledge.jsonl"

_whitespace_re = re.compile(r"\s+")

def clean(text: str) -> str:
    """Collapse consecutive whitespace and strip ends."""
    return _whitespace_re.sub(" ", text).strip()


def chunk_text(text: str, size: int = CHUNK_SIZE):
    """Yield successive size-limited substrings from text."""
    for i in range(0, len(text), size):
        yield text[i : i + size]


def build_jsonl() -> int:
    """Process raw txt files and write JSONL.

    Returns number of chunks written.
    """
    chunks_written = 0
    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for folder in RAW_FOLDERS:
            for txt_file in (BASE_DIR / folder).glob("*.txt"):
                try:
                    raw = txt_file.read_text(encoding="utf-8")
                except Exception as exc:
                    print(f"⚠️  Skipping {txt_file}: {exc}", file=sys.stderr)
                    continue

                cleaned = clean(raw)
                for idx, piece in enumerate(chunk_text(cleaned)):
                    json.dump({"source": txt_file.stem, "chunk_id": idx, "text": piece}, out, ensure_ascii=False)
                    out.write("\n")
                    chunks_written += 1
    return chunks_written


def main():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    count = build_jsonl()
    rel_out = OUTPUT_PATH.relative_to(Path.cwd()) if OUTPUT_PATH.is_absolute() else OUTPUT_PATH
    print(f"✔ Wrote {count} chunks to {rel_out}")


if __name__ == "__main__":
    main()