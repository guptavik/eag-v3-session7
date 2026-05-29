"""build_corpus_index.py — bulk-index a sandbox directory via the index_document tool.

Indexing 50+ files through the agent loop would exceed the iteration cap, so the
custom-query corpus is indexed directly through the real `index_document` MCP tool
(same chunking + embedding path the agent uses). Prints the total chunk count.

Usage:
    uv run build_corpus_index.py corpus
    uv run build_corpus_index.py papers
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MCP_SERVER = Path(__file__).parent / "mcp_server.py"
SANDBOX = Path(__file__).parent / "sandbox"


def _result_text(res) -> str:
    parts = []
    for c in getattr(res, "content", None) or []:
        t = getattr(c, "text", None)
        parts.append(t if t is not None else str(c))
    return "\n".join(parts)


async def run(subdir: str) -> None:
    target = SANDBOX / subdir
    files = sorted(p.name for p in target.glob("*.md") if p.name != "MANIFEST.md")
    if not files:
        raise SystemExit(f"no .md files under {target}")
    params = StdioServerParameters(command=sys.executable, args=[str(MCP_SERVER)])
    total = 0
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for name in files:
                res = await session.call_tool(
                    "index_document", arguments={"path": f"{subdir}/{name}"}
                )
                txt = _result_text(res)
                try:
                    n = int(json.loads(txt).get("chunks_indexed", 0))
                except Exception:
                    n = 0
                total += n
                print(f"[index] {subdir}/{name}: {n} chunks")
    print(f"[build_corpus_index] {len(files)} files, {total} chunks indexed into memory")


if __name__ == "__main__":
    sub = sys.argv[1] if len(sys.argv) > 1 else "corpus"
    asyncio.run(run(sub))
