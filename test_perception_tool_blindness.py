"""Architectural gate: Perception is tool-blind.

No MCP tool name may appear in Perception's SYSTEM prompt — tool selection is
Decision's job (guidance lives in Decision's SYSTEM and the tool docstrings).
We also assert the whole file is clean, so a literal `grep` over perception.py
(comments included) returns nothing.

Run: uv run pytest -v test_perception_tool_blindness.py
"""
from __future__ import annotations

from pathlib import Path

import perception

TOOL_NAMES = [
    "web_search", "fetch_url", "get_time", "currency_convert",
    "read_file", "list_dir", "create_file", "update_file", "edit_file",
    "index_document", "search_knowledge",
]


def test_system_prompt_names_no_tools():
    sys_text = perception.SYSTEM.lower()
    found = [t for t in TOOL_NAMES if t in sys_text]
    assert not found, f"Perception SYSTEM names MCP tools: {found}"


def test_file_level_grep_is_clean():
    src = Path(perception.__file__).read_text(encoding="utf-8").lower()
    found = [t for t in TOOL_NAMES if t in src]
    assert not found, f"perception.py mentions MCP tools (reword comments): {found}"
