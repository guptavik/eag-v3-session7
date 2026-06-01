# Submission Video — Shot List

Target length: **3–5 minutes**. Screen-record the terminal + browser; no slides needed.
Run all commands from `Z:\eag-v3\eag-v3-session7` in **PowerShell**.

**Filming order: Shot 1 → Shot 2 → Shot 5 → Shot 3 → Shot 4 → Shot 6**
(Shot 5 uses F's FAISS index; Shot 3 clears state with `--clear`. Filming 5 before 3
means the index is safe when you need it and already gone when you don't.)

---

## ⚠️ State management — read before filming

The base queries share FAISS state across groups. **Never `--clear` inside a group.**

| Group | Queries | Clear before first? |
|-------|---------|---------------------|
| 1 | A → B → C-run1 → C-run2 → D | ✅ yes (`--clear` on A) |
| 2 | E alone | ✅ yes (`--clear` on E) |
| 3 | F-run1 → F-run2 → **G** → H | ✅ yes (`--clear` on F-run1 only) |
| Custom (no-corpus) | Q1–Q5 | ✅ yes (`--clear` on Q1) |
| Custom (with-corpus) | Q1–Q5 | ❌ no — index must be present |

**G and H piggyback on F-run1's index.** If you clear state after F, G loops to the
iteration cap and fails with "I don't have access to the research papers."

---

## Pre-filming checklist (do these before recording)

```powershell
# 1. Kill any stale gateway on port 8107
Get-NetTCPConnection -LocalPort 8107 -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

# 2. Start the gateway in a separate PowerShell window (leave it running)
cd Z:\eag-v3\eag-v3-session7\llm_gatewayV7
uv run main.py

# 3. Back in the project directory — run F-run1 so Shot 5 has the papers/ index
cd Z:\eag-v3\eag-v3-session7
uv run run_query.py --clear --out docs\traces\base\F.txt `
  "Index every .md file under papers/. Confirm how many chunks were indexed in total."
uv run run_query.py --out docs\traces\base\F_run2.txt `
  "Across the papers I have indexed, what do they say about chain-of-thought reasoning?"
#    → leave state intact (do NOT clear after this — Shot 5 needs it)

# 4. Build the corpus index for Shot 4 (~3 min; run while you set up your screen recorder)
#    Shot 4 will clear state first anyway, so do this after F-run2:
uv run python -c "import memory; memory.clear()"
uv run build_corpus_index.py corpus
#    → expect: "[build_corpus_index] 55 files, 55 chunks indexed"
```

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

## Shot 5 — Cross-run FAISS persistence (F run 2) (1:10–1:50)

> **State note:** F-run1 + F-run2 were pre-run in the checklist. The papers/ index
> is on disk. **Do not clear state before this shot.**

**Show the existing trace file** (no need to re-run):
```powershell
Get-Content docs\traces\base\F_run2.txt -TotalCount 30
```

**Point out:**
- The run ID is different from F run 1 (fresh process)
- `[memory.read] 8 hits` — FAISS index loaded from disk
- No `index_document` calls — used the persisted index
- 3 iterations total

**Say:** "Query F run 2 ran in a completely fresh Python process. The FAISS index
files on disk (`state/index.faiss` + `state/index_ids.json`) are the medium that
crosses the process boundary. The agent answered without re-indexing anything."

**Optional — live demo of G (synonym recall) while the index is still intact:**
```powershell
# G shares F's index — run without --clear
uv run run_query.py --out $env:TEMP\g_live.txt `
  "Across these papers, how do they handle the credit assignment problem?"
# → 4 iters, cites all 5 papers via vector semantics (phrase absent from chunks)
```

---

## Shot 3 — Base query E: index + extract (1:50–2:40)

> **State note:** uses `--clear`. Safe to run here because Shot 5 is already filmed.

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

## Shot 4 — Semantic recall demo (Q1 — credit assignment) (2:40–3:40)

> **State note:** self-contained. The no-corpus run clears state first; the with-corpus
> run re-indexes. Nothing earlier depends on this state.

**First — no corpus (cleared state):**
```powershell
uv run run_query.py --clear --out $env:TEMP\q1_no.txt `
  "Across these papers, how do they handle the credit assignment problem?"
# → web_search called, generic RL answer, no corpus citations
```

**Then — with corpus:**
```powershell
uv run python -c "import memory; memory.clear()"
uv run build_corpus_index.py corpus     # already cached from pre-filming; runs fast
uv run run_query.py --out $env:TEMP\q1_with.txt `
  "Across these papers, how do they handle the credit assignment problem?"
# → answers from memory hits, cites indexed papers
```

> Tip: if `build_corpus_index.py` still takes too long on camera, skip re-running it —
> use the pre-built index from the checklist and go straight to `run_query.py`.

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

- **Font size:** PowerShell → right-click title bar → Properties → Font → size 18–20
  so commands are readable on a 1080p share.
- **The gateway must stay running** throughout all shots. Start it in a separate window
  during the pre-filming checklist and leave it there.
- **Kill the gateway** between recording sessions with:
  ```powershell
  Get-NetTCPConnection -LocalPort 8107 | Select-Object -ExpandProperty OwningProcess |
    ForEach-Object { Stop-Process -Id $_ -Force }
  ```
