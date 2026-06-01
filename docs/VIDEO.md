# Submission Video — Shot List

Target length: **3–5 minutes**. Screen-record the terminal + browser; no slides needed.
Run all commands from `Z:\eag-v3\eag-v3-session7` in **PowerShell**.

---

## Shot 1 — Repo tour (0:00–0:40)

**What to show:**
```powershell
Get-ChildItem *.py | Select-Object Name
# agent7.py, memory.py, perception.py, decision.py,
# action.py, artifacts.py, mcp_server.py, schemas.py,
# vector_index.py, gateway.py

(Get-ChildItem sandbox\corpus\).Count    # 56 (55 md + MANIFEST)
Get-ChildItem sandbox\papers\            # 5 reference papers
```

**Say:** "This is the Session 7 agent — a four-layer cognitive loop: memory reads,
perception sets goals, decision picks a tool or answers, action dispatches. Session 7
adds FAISS-backed vector memory and two new tools: `index_document` and `search_knowledge`.
The corpus is 55 AI/ML paper summaries; the 5 files under `papers/` back the base queries."

---

## Shot 2 — Architectural gate: tool-blindness (0:40–1:10)

**What to show:**
```powershell
uv run pytest test_perception_tool_blindness.py -v
# → 2 passed

$hits = Select-String -Pattern "web_search|fetch_url|index_document|search_knowledge" perception.py
if ($hits) { "FAIL" } else { "PASS" }
# → PASS
```

**Say:** "The gate: Perception's SYSTEM prompt names zero MCP tools. Tool selection
is Decision's job. This is tested automatically — if anyone adds a tool name to
Perception's prompt, the test fails."

---

## Shot 3 — Base query E: index + extract (1:10–2:00)

Run live (takes ~30s):
```powershell
uv run run_query.py --clear --out $env:TEMP\e_live.txt `
  "Index the file papers/attention.md and tell me what the three key contributions of the Transformer architecture are according to this paper."
```

**Show the terminal as it runs.** Point out:
- iter 1: `TOOL_CALL: index_document({"path": "papers/attention.md"})` — chunk embedded into FAISS
- iter 2: Decision answers directly from the memory hit (no second tool call)
- Final answer: the 3 contributions cited from the indexed chunk

**Say:** "This is the core RAG loop: index once, retrieve by semantic similarity,
answer from the chunk. Two iterations — fast because the indexed content surfaces
in the very next memory read."

---

## Shot 4 — Semantic recall demo (Q1 — credit assignment) (2:00–3:00)

**First — no corpus (cleared state):**
```powershell
uv run run_query.py --clear --out $env:TEMP\q1_no.txt `
  "Across these papers, how do they handle the credit assignment problem?"
# → web_search called, generic RL answer, no corpus citations
```

**Then — with corpus (index first):**
```powershell
uv run python -c "import memory; memory.clear()"
uv run build_corpus_index.py corpus     # 55 chunks indexed (~3 min, run beforehand)
uv run run_query.py --out $env:TEMP\q1_with.txt `
  "Across these papers, how do they handle the credit assignment problem?"
# → answers from memory hits, cites seq2seq/attention/layernorm/etc.
```

**Show the contrast — print the two FINAL lines:**
```powershell
Select-String "^FINAL:" $env:TEMP\q1_no.txt   | Select-Object -First 1
Select-String "^FINAL:" $env:TEMP\q1_with.txt | Select-Object -First 1
```

**Say:** "The phrase 'credit assignment' does not appear in a single corpus chunk.
Vector search surfaces papers that relate to it conceptually — LSTM's gradient
preservation, attention's global weighting, LoRA's parameter constraints. Without
the index, the agent uses web search and gives a generic answer. With the index,
it answers in 3 iterations from the indexed corpus."

---

## Shot 5 — Cross-run FAISS persistence (F run 2) (3:00–3:40)

**Show the existing trace file** (no need to re-run):
```powershell
Get-Content docs\traces\base\F_run2.txt -TotalCount 30
```

**Point out:**
- The run ID is different from F run 1 (a fresh process)
- `[memory.read] 8 hits` — the FAISS index loaded from disk
- No `index_document` calls — the agent used the persisted index
- 3 iterations total

**Say:** "Query F run 2 ran in a completely fresh Python process. The FAISS index
files on disk (`state/index.faiss` + `state/index_ids.json`) are the medium that
crosses the process boundary. The agent answered without re-indexing anything."

---

## Shot 6 — One-line close (3:40–4:00)

```powershell
git log --oneline | Select-Object -First 8
```

**Say:** "The architecture is intact: tool-blind Perception, byte isolation through
the artifact store, one LLM call per Decision turn with native function-calling, and
durable FAISS-backed memory that survives across runs. 8 base queries all within their
iteration bounds, 5 custom queries — 2 with proven semantic recall."

---

## Notes for recording

- The gateway must be running before filming — start it in a separate PowerShell window:
  ```powershell
  cd Z:\eag-v3\eag-v3-session7\llm_gatewayV7
  uv run main.py
  ```
  Or just run the first query and let `ensure_gateway()` auto-start it (takes ~15s).
- Kill any existing gateway first if port 8107 is in use:
  ```powershell
  Get-NetTCPConnection -LocalPort 8107 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
  ```
- **Pre-run `build_corpus_index.py` before filming Shot 4** — it takes ~3 min.
  Have the index ready so the with-corpus query runs immediately.
- Keep the terminal font size large enough to read on a 1080p share (PowerShell:
  right-click title bar → Properties → Font → size 18–20).
