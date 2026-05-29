# Session 7 — RAG Corpus, Base/Custom Traces & Architecture Proof — Design

**Date:** 2026-05-29
**Status:** Approved (design); implementation plan to follow.
**Project:** `z:\eag-v3\eag-v3-session7` (EAGV3 Session 7 agent)

## Goal

Prove the Session 7 agent **uses RAG well** and that the **four-layer architecture is
intact**. Concretely: pass the eight base queries (A–H) verbatim within their named
iteration bounds, build a real RAG corpus of 50+ items, and design five custom
queries that answer correctly *with* the index and fail *without* it (≥2 requiring
semantic recall). Deliver a GitHub repo (README with corpus manifest + all 13 traces
and the no-corpus comparisons) and a short video.

## Context / current state

- Architecture is **intact**: four-layer loop (`memory → perception → decision →
  action`), FAISS vector memory with keyword fallback, and the `index_document` /
  `search_knowledge` tools are all present and wired.
- **Tool-blindness gate holds**: `perception.py`'s SYSTEM names no MCP tools;
  tool-selection guidance lives in `decision.py`'s SYSTEM and the tool docstrings.
  (Two incidental `list_dir` mentions remain in *code comments* — to be reworded so a
  file-level `grep` is also clean.)
- The two "fix the rendering, not the SYSTEM" corrections described in the
  assignment are already present: `_format_hits` renders `value.raw` and
  `value.chunk` in `decision.py`.
- Append-after-discovery (needed for Query F) is present in `perception.py`.
- Gateway-discovery path is fixed (`gateway.py` resolves `llm_gatewayV7/` as a
  sibling); `.venv` is present and dependencies are installed.
- **Missing**: the corpus (`sandbox/` is git-ignored and empty), all traces, the 5
  custom queries, README deliverable sections, the backlog, and the video.

## Decisions (from brainstorming)

1. **Application path**: keep `agent7.py` as the RAG application (it already needs
   retrieval to work). Add a real corpus + a small bulk-ingest helper. No browser
   extension / separate UI.
2. **Corpus**: ~55 Markdown summaries of well-known AI/ML papers. No new MCP tool
   needed (`.md` handled by `read_file` / `index_document`).
3. **Runtime**: fully ready — gateway + embeddings (Ollama `nomic-embed-text` or
   Gemini) + `TAVILY_API_KEY`. All 13 queries can be run live.

## Architecture (no changes to the agent's core)

The agent's four-layer design is unchanged. This work adds **data** (corpus),
**deliverables** (traces, README, backlog), and **behavior-neutral tooling** (a trace
runner). The only source edits are:

- Reword two comments in `perception.py` (grep-gate bulletproofing).
- Optional `run_query.py` helper that calls `agent7.run(...)` and tees stdout to a
  trace file. It must not change agent behavior.

## Components

### Corpus — two tracked directories

The base queries E–H are fixed session tests calibrated to a **5-file** set (Query F's
11-iteration bound depends on indexing exactly 5 files → ~15 chunks). The 50+ item
requirement is a separate deliverable exercised by the 5 custom queries. So the corpus
splits in two:

- **`sandbox/papers/`** — exactly 5 reference summaries (`attention.md`, `cot.md`,
  `dpo.md`, `lora.md`, `react.md`). Used **only** by base queries E–H so their traces
  and iteration bounds match the reference. These 5 are also authored to the same
  template as the big corpus.
- **`sandbox/corpus/`** — the 50+ item RAG corpus (~55 `.md` files) used **only** by
  the 5 custom queries.

Both are git-tracked (see Git tracking below). Each file is a concise,
factually-correct summary (~200–350 words) of a well-known AI/ML paper.
- **Consistent section structure** per file: `Title / Year`, `Problem`, `Method`,
  `Key contributions`, `Results`. Clean 400-word chunking; high concept density for
  semantic recall.
- Includes the five reference papers (attention, CoT, DPO, LoRA, ReAct) so the E–H
  base traces match reference behavior.
- **Manifest**: `sandbox/corpus/MANIFEST.md` — table of
  `filename · paper title · year · topic tags`. Copied into the README.
- **Git tracking**: both `sandbox/papers/` and `sandbox/corpus/` sit under `sandbox/`
  so `index_document` / `read_file` (which resolve paths under `sandbox/` via `_safe`)
  index them unchanged. Because `sandbox/` is git-ignored, add `.gitignore` exceptions
  (`!sandbox/papers/`, `!sandbox/papers/**`, `!sandbox/corpus/`, `!sandbox/corpus/**`)
  so the corpora + manifest are tracked for submission while runtime scratch and
  `state/` stay ignored.

### Base traces (A–H) — `docs/traces/base/`

Run each query verbatim via `agent7.py`; capture stdout to `A.txt … H.txt`. Verify
each lands within its named iteration bound:

| Query | Bound | Notes |
|-------|-------|-------|
| A Shannon Wikipedia | 3 | artifact attach; vector uninvolved |
| B Tokyo activities + weather | 8 | multi-goal, memory carryover |
| C Mom's birthday | 4 (run 1) + 3 (run 2) | durable memory across runs |
| D Asyncio research | 6 | multi-source synthesis |
| E Single-doc index + extract | 5 | `index_document papers/attention.md` then answer |
| F Cross-run recall | 11 (run 1) + 3 (run 2) | index `papers/` (5 files → ~15 chunks); FAISS persistence; append-after-discovery |
| G Synonym recall | 4 | vector beats keyword |
| H Cross-doc synthesis | 3 | `search_knowledge` over 2 docs |

A/B/D need web search (Tavily). C and F are two-run sequences; **state is not cleared
between run 1 and run 2** (that is the point of the test).

### Custom queries (5) — `docs/traces/custom/`

Finalized against the actual corpus once authored. Proposed set (≥2 semantic):

| # | Query (shape) | Type | Fails without index because |
|---|---|---|---|
| 1 | How do these papers handle the **credit assignment problem**? | Semantic | phrase in no chunk; vector surfaces backprop-through-steps / reward-shaping / intermediate-signal ideas |
| 2 | Which methods make **adapting a huge model affordable on one GPU**? | Semantic | no chunk says "affordable/one GPU"; vector surfaces LoRA / adapters / quantization |
| 3 | What are the **three key contributions of the Transformer** per the attention paper? | Lexical, index-only | answer lives only in an indexed chunk |
| 4 | **Compare** how DPO and PPO-style RLHF approach preference optimization. | Cross-doc synthesis | needs chunks from ≥2 docs together |
| 5 | Which papers teach a model to **reason before answering**, and how do they differ? | Semantic synthesis | wording ≠ chunk text; surfaces CoT / ReAct / scratchpad |

**No-corpus comparison:** for each query, capture a `_with.txt` (corpus indexed) and a
`_nocorpus.txt` (run from a **cleared state** — `memory.clear()` → empty FAISS, so the
vector path returns nothing). Expected no-index outcome: declines, loops to cap, or
answers incorrectly without sources.

### Deliverables

- **README** appended with: Corpus manifest, Base traces (A–H), Custom queries (5) +
  no-corpus comparison, Architectural principles, How to reproduce.
- **`BACKLOG.md`** at the project root — prioritized checkbox work-items.
- **Video**: shot-list / script provided; user records.

## Data flow (trace capture)

```
run_query.py "<query>"  ──▶  agent7.run()  ──▶  stdout  ──tee──▶  docs/traces/.../X.txt
                                   │
                                   └─ reads/writes state/ (memory.json, index.faiss, index_ids.json)
```

For no-corpus runs: `memory.clear()` first, do NOT index, then run the query.

## Principles & guidelines to enforce (acceptance gates)

1. **Tool-blindness in Perception** — `grep` over `perception.py` for MCP tool names
   returns nothing in the SYSTEM string (and, after the comment reword, nothing at the
   file level).
2. **Tool guidance home** — Decision SYSTEM + tool docstrings only; never Perception.
3. **Diagnostic discipline** — on a role-level failure, reconstruct what the role
   *saw* from the prompt-building code; fix the rendering layer when the input was the
   cause, not the SYSTEM. Documented as a 5-step procedure.
4. **Byte isolation** — raw bytes reach an LLM only via Perception's artifact attach.
5. **No regex on LLM output**; typed Pydantic contracts at every layer boundary.
6. **Iteration bounds honored** for all eight base queries.
7. **Frozen embedding model** (768-dim) — never change after an index is built.

## Error handling / risks

- **Web-query flakiness** (A/B/D): Tavily is ready; DuckDuckGo is the fallback. If a
  page changes shape, re-run; traces are "real and lightly cleaned for readability."
- **Iteration-bound misses**: if a query exceeds its bound, treat as a diagnostic
  signal (apply the discipline) rather than padding the bound.
- **Corpus factual accuracy**: summaries must be correct enough that queries answer
  correctly; the five reference papers are authored to match known E–H behavior.
- **State bleed between queries**: base RAG queries and custom queries share
  `state/`. Define explicit clear points (before A; before custom no-corpus runs) and
  document the intended state at each step.

## Testing / verification

- `grep` gate on `perception.py`.
- `uv run pytest -v test_mcp_server.py` green (list_dir test already updated).
- Each base trace reviewed against its iteration bound.
- Each custom query: `_with` answers correctly + cites sources; `_nocorpus` fails.

## Out of scope

- No changes to the agent's cognitive loop, schemas, or retrieval algorithm.
- No hybrid retrieval / RRF, no semantic chunking (future sessions).
- No browser extension or separate UI.

## Reproduce

1. Start `llm_gatewayV7` (or let `agent7.py` auto-start it); ensure embeddings +
   `TAVILY_API_KEY`.
2. Author corpus → `sandbox/corpus/`.
3. Run base A–H and custom 1–5 via `run_query.py`, capturing traces.
4. Assemble README sections from manifest + traces.
