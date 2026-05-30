"""run_query.py — run one agent7 query and tee its trace to a file.

Usage:
    uv run run_query.py --out docs/traces/base/A.txt "Fetch https://..."
    uv run run_query.py --clear --out docs/traces/custom/1_nocorpus.txt "..."

--clear wipes persistent memory + the FAISS index before running (used for the
no-corpus comparison runs). The full stdout trace is printed AND written to --out.
"""
from __future__ import annotations

import argparse
import asyncio
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Box-drawing chars in the trace need UTF-8; the Windows console defaults to cp1252.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

import agent7
import memory


class _Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s: str) -> int:
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self) -> None:
        for st in self.streams:
            try:
                st.flush()
            except Exception:
                pass


def main() -> None:
    ap = argparse.ArgumentParser(description="Run one agent7 query and tee the trace.")
    ap.add_argument("query")
    ap.add_argument("--out", required=True, help="trace output file path")
    ap.add_argument("--clear", action="store_true", help="wipe memory + index first")
    args = ap.parse_args()

    if args.clear:
        memory.clear()
        print("[run_query] cleared persistent memory + vector index")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    real_stdout = sys.stdout
    with out_path.open("w", encoding="utf-8") as f:
        with redirect_stdout(_Tee(real_stdout, f)):
            asyncio.run(agent7.run(args.query))


if __name__ == "__main__":
    main()
