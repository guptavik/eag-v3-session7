# EAGV3 — Session 7 Agent

A small, typed, tool-using agent built around a **four-layer cognitive loop**
(`memory → perception → decision → action`). Session 7 keeps the Session 6
architecture intact and adds two things on top:

1. **Vector memory (RAG).** Memory writes now compute an embedding and append
   it to a FAISS index; reads do semantic similarity first and fall back to
   keyword overlap only when the vector path is empty.
2. **Document indexing.** Two new MCP tools — `index_document` and
   `search_knowledge` — let the agent ingest sandbox files / fetched pages
   into searchable memory and query that knowledge base on demand.

Everything else (the loop, the artifact store, the typed contracts between
layers) is unchanged from Session 6.

```bash
# from this folder, after the gateway is running (see "Running"):
uv run agent7.py "What is the current time in Asia/Tokyo and Asia/Kolkata? Tell me the difference in hours."
```

---

## Table of contents

- [Mental model](#mental-model)
- [The cognitive loop](#the-cognitive-loop)
- [Module map](#module-map)
- [Deep dive: each layer](#deep-dive-each-layer)
  - [Schemas — the typed contracts](#schemas--the-typed-contracts)
  - [Memory — vector + keyword retrieval](#memory--vector--keyword-retrieval)
  - [Vector index — FAISS wrapper](#vector-index--faiss-wrapper)
  - [Perception — the orchestrator](#perception--the-orchestrator)
  - [Decision — one LLM call per turn](#decision--one-llm-call-per-turn)
  - [Action — the MCP dispatcher](#action--the-mcp-dispatcher)
  - [Artifacts — byte isolation](#artifacts--byte-isolation)
  - [MCP server — the 11 tools](#mcp-server--the-11-tools)
  - [Gateway — the LLM + embedding bridge](#gateway--the-llm--embedding-bridge)
- [Retrieval-augmented generation (RAG) flow](#retrieval-augmented-generation-rag-flow)
- [State & data layout](#state--data-layout)
- [Setup & running](#setup--running)
- [Configuration](#configuration)
- [Testing](#testing)
- [Design principles & invariants](#design-principles--invariants)
- [Known limitations & caveats](#known-limitations--caveats)

---

## Mental model

The agent thinks in **four typed layers**, each with a single responsibility,
talking to each other only through Pydantic models defined in [schemas.py](schemas.py):

```
        ┌──────────────────────────────────────────────────────────────┐
        │                       agent7.py  (the loop)                    │
        └──────────────────────────────────────────────────────────────┘
                                     │  per iteration
   ┌─────────────┐   hits   ┌──────────────┐  goal  ┌────────────┐  tool_call  ┌──────────┐
   │  memory.read│ ───────▶ │ perception   │ ─────▶ │  decision  │ ──────────▶ │  action  │
   │ (vec→kw)    │          │ .observe()   │        │.next_step()│             │ .execute │
   └─────────────┘          └──────────────┘        └────────────┘             └────┬─────┘
          ▲                        │                       │                        │
          │                        │ attach_artifact_id    │ answer (plain text)    │ (descriptor, art_id)
          │                        ▼                       ▼                        │
          │                  ┌──────────────┐         final answer                  │
          └──────────────────│  artifacts   │◀───────────────────────────────── memory.record_outcome
        memory.record_outcome│ (raw bytes)  │
                             └──────────────┘
```

Key separation-of-concerns rules that the whole design hangs on:

- **Perception is the only layer that holds goal state across iterations.**
  It decomposes the query into goals once, then refreshes `done` flags every
  turn and decides whether the next goal needs raw bytes attached.
- **Bytes never travel through Memory or Perception.** Large tool outputs go
  to the content-addressable **artifact store**; Memory keeps only a handle +
  a one-line descriptor. Decision sees raw bytes *only* when Perception
  explicitly attaches an artifact to the current goal. (One 50 KB page touches
  exactly one LLM call per run instead of every call.)
- **Decision does the "thinking."** There is no taxonomy of operation kinds —
  Decision either answers in plain text (which may itself be summarisation,
  extraction, comparison, translation…) or calls exactly one MCP tool.
- **Memory is a typed service**, not a layer in the loop's critical path. It
  is read at the top of each iteration and written after each action.

---

## The cognitive loop

[agent7.py](agent7.py) runs up to `MAX_ITERATIONS = 20` iterations. Each one:

1. **`memory.read(query, history)`** — pull relevant memory items (vector search
   first, keyword fallback).
2. **`perception.observe(...)`** — (re)build the goal list, mark done goals, and
   set `attach_artifact_id` on the next unfinished goal if it needs bytes.
   - If all goals are done → stop.
3. **Attach** — if the chosen goal references an artifact, load its bytes from
   the artifact store.
4. **`decision.next_step(goal, hits, attached, history, tools)`** — one LLM call.
   Returns either an `answer` (closes the goal) or a `tool_call`.
5. **`action.execute(session, tool_call)`** — dispatch to the MCP server; large
   results get offloaded to the artifact store.
6. **`memory.record_outcome(...)`** — write the tool outcome back to memory
   (zero LLM; kind is `tool_outcome` by construction, embedded for later recall).

Before iteration 1, the loop also calls **`memory.remember(query)`** once so any
durable facts/preferences stated in the user's query survive into future runs.

---

## Module map

| File | Lines | Role |
|------|-------|------|
| [agent7.py](agent7.py) | ~170 | The loop; wires the four layers + MCP session |
| [schemas.py](schemas.py) | ~97 | Pydantic contracts every layer talks in |
| [memory.py](memory.py) | ~383 | Typed memory service: vector + keyword retrieval, classified writes |
| [vector_index.py](vector_index.py) | ~119 | FAISS `IndexFlatIP` wrapper with disk persistence |
| [perception.py](perception.py) | ~265 | Goal decomposition + per-iter refresh + force-attach |
| [decision.py](decision.py) | ~193 | One LLM call → answer or tool_call (native tool-calling) |
| [action.py](action.py) | ~79 | MCP dispatcher + large-result → artifact offload |
| [artifacts.py](artifacts.py) | ~53 | Content-addressable byte store (sha256 handles) |
| [gateway.py](gateway.py) | ~87 | Bridge to `llm_gatewayV7` (chat + embed), auto-starts it |
| [mcp_server.py](mcp_server.py) | ~392 | FastMCP stdio server: 11 tools |
| [test_mcp_server.py](test_mcp_server.py) | ~204 | pytest suite for the MCP tools |

---

## Deep dive: each layer

### Schemas — the typed contracts

[schemas.py](schemas.py) is the boundary between layers — every other module
imports from here, so there is no free-form dict passing between roles.

- **`MemoryItem`** — one record. Kinds: `fact`, `preference`, `tool_outcome`,
  `scratchpad`. The S7 addition is the optional **`embedding: list[float]`**
  field, set by Memory at write time for the first three kinds (scratchpad is
  run-scoped and skips embedding). Bytes never live here — only a `descriptor`,
  structured `value`, and an optional `artifact_id` handle.
- **`Artifact`** — metadata for a content-addressed blob (id, content_type,
  size, source, descriptor). The bytes live in `state/artifacts/`.
- **`Goal`** — `id`, `text`, `done`, and `attach_artifact_id` (set by Perception
  when the goal needs raw bytes).
- **`Observation`** — the list of goals + `all_done` / `next_unfinished()` helpers.
- **`ToolCall`** — `name` + `arguments`.
- **`DecisionOutput`** — exactly one of `answer` / `tool_call`; `is_answer`
  helper distinguishes them.

`new_id(prefix)` mints typed ids (`mem:…`, `g:…`, `art:…`) so the kind is
visible at a glance in traces and on disk.

### Memory — vector + keyword retrieval

[memory.py](memory.py) is the centrepiece of Session 7. It is a module-level
service persisting to `state/memory.json` and a FAISS index under `state/`.

**Reads** (`read()`):

```
read(query)  ──▶  _vector_search()  ──┐ hits?  yes ──▶ return vector hits
                                       └──────  no  ──▶ _keyword_search()  (S6 fallback)
```

- `_vector_search` embeds the query (`task_type="retrieval_query"`), searches
  FAISS by cosine similarity, then maps integer positions back to `MemoryItem`s
  and applies any `kinds` filter.
- `_keyword_search` is the Session 6 path: token-overlap scoring over keywords
  + descriptor, with the last few history events folded into the query tokens.

**Writes** — three entry points, all of which embed the descriptor (except
scratchpad):

- **`remember(raw_text)`** — for ambiguous free-form content (the user's query).
  One **LLM classifier** call (routed `auto_route="memory"`) decides `kind`,
  `descriptor`, `keywords`, and structured `value`. Has a deterministic
  `_fallback_remember` for when the classifier is unavailable, and guards
  against the classifier returning an empty `value` (falls back to
  `{"raw": raw_text}` so the original text is always retrievable).
- **`record_outcome(tool_call, result_text, …)`** — zero-LLM write for a
  deterministic tool result. Kind is always `tool_outcome`.
- **`add_fact(descriptor, value, …)`** — direct fact write used by
  `index_document` (kind is known, so it skips the classifier but still embeds).

`_persist_item` is the single write path: append to JSON, and if the item has an
embedding of an embeddable kind, add it to the FAISS index and persist.

`clear()` wipes both `memory.json` and the vector index — the clean-slate story
between assignment attempts.

### Vector index — FAISS wrapper

[vector_index.py](vector_index.py) wraps `faiss.IndexFlatIP` (inner product on
**L2-normalized** vectors, which equals cosine similarity) with a parallel
`list[str]` of `MemoryItem` ids (FAISS stores by integer position; the ids list
maps position → application id).

- Persists to `state/index.faiss` (binary) + `state/index_ids.json` (the ids).
- The index dimension is fixed on first `add`; a later `add` with a different
  dimension **raises** — this is the guard rail that protects you from silently
  mixing embedding models. The dimension is pinned to **768** at the gateway
  level (see below).
- On cold start, Memory rebuilds the index from any already-embedded items in
  `memory.json` (`_index()` in [memory.py](memory.py)).

### Perception — the orchestrator

[perception.py](perception.py) runs every iteration. It sees the query, memory
hits (descriptors only — **never** bytes), the run history, and the prior goals,
and returns the current `Observation`.

Notable design choices, encoded in the system prompt and the post-processing:

- **Goals are identified by position**, not by an id the LLM controls — the LLM
  literally has no id field to drift across iterations.
- **Append-only goal growth.** Prior goals are copied verbatim into the same
  slot; Perception may *append* new goals at the end when a discovery action
  (e.g. `list_dir` revealing 5 papers) exposes work that wasn't knowable at
  decomposition time. Duplicate appended goals are dropped.
- **Intent, not tools.** Goals are written as imperatives ("fetch", "summarise",
  "make searchable") — naming a specific tool is left to Decision.
- **Knowledge-base awareness.** If memory already contains indexed chunks
  (`fact` items whose descriptors start with `[sandbox:` / `[art:`), the prompt
  steers the next goal toward *querying the knowledge base* rather than
  re-fetching the source.
- **Synthesis-done guard.** A synthesis-shaped goal (extract/compare/summarise/…)
  is only allowed to flip to `done` once history actually contains a substantive
  answer for it — a tool call alone can't close it.
- **Force-attach safety net.** If the first unfinished goal is synthesis-shaped
  and there are artifacts available but the LLM forgot to attach one, Perception
  attaches the most recent artifact itself (the model at `temperature=1.0` is
  otherwise unreliable about this).

### Decision — one LLM call per turn

[decision.py](decision.py) makes exactly one gateway call per turn and returns a
`DecisionOutput`. It uses **native tool-calling**: the MCP tool catalogue is
passed as `tools=` with `tool_choice="auto"`, and the reply's `tool_calls` are
read directly — no hand-parsing of JSON out of free-form text.

- `temperature=0` and `cache_system=True` (the long system prompt is cached).
- Attached artifact bytes are windowed (`ATTACH_HEAD=20_000` / `ATTACH_TAIL=10_000`)
  so very large pages still fit a turn as head+tail.
- The system prompt encodes the hard rules: never narrate; never invent tools;
  `art:…` handles are **not** file paths/URLs (answer from the attached bytes);
  use `index_document` when content must be searchable later vs `read_file` for
  one-shot inspection; use `search_knowledge` instead of re-fetching when chunks
  already exist.
- `_format_hits` surfaces a chunk preview inline for indexed-chunk facts so
  Decision can synthesise directly from the hit list instead of looping on
  `search_knowledge`.

### Action — the MCP dispatcher

[action.py](action.py) is pure dispatch — no LLM. It calls the tool over the
live MCP session and returns `(descriptor, artifact_id_or_None)`.

- **Artifact offload.** Results larger than `ARTIFACT_THRESHOLD_BYTES` (4 KB)
  are written to the artifact store; the returned descriptor is a short preview
  + the handle. Smaller results pass through inline.
- **`art:` guard.** If Decision hallucinates that an `art:…` handle is a `path`
  or `url` argument, Action returns an error string instead of making the bad
  call — saving a wasted iteration.

### Artifacts — byte isolation

[artifacts.py](artifacts.py) is a content-addressable blob store keyed by
`sha256(content)[:16]`. Identical content dedupes to the same handle. Memory
holds the handle + descriptor; this module owns the bytes. This is what keeps
large pages out of the LLM context except on the one turn that needs them.

### MCP server — the 11 tools

[mcp_server.py](mcp_server.py) is a FastMCP **stdio** server. Tools:

| Tool | Purpose |
|------|---------|
| `web_search` | Tavily primary, DuckDuckGo fallback; hard-capped at 5 results |
| `fetch_url` | Clean markdown via crawl4ai (headless Chromium) |
| `get_time` | Current time in an IANA timezone (with UTC offset) |
| `currency_convert` | ISO-3 conversion via frankfurter.dev |
| `read_file` | Read a UTF-8 file from the sandbox |
| `list_dir` | List a sandbox dir — returns `{count, names, entries}` |
| `create_file` | Create a new sandbox file (errors if it exists) |
| `update_file` | Overwrite an existing sandbox file |
| `edit_file` | Find-and-replace inside a sandbox file |
| **`index_document`** | Chunk a file/artifact and write chunks into Memory as searchable `fact`s |
| **`search_knowledge`** | Vector search over indexed `fact` chunks (same backend as `memory.read`) |

Hardening worth knowing about:

- **Sandboxing.** `_safe()` resolves every path under `sandbox/` and rejects
  anything that escapes it (`../…`).
- **Usage metering.** Tavily/DDG call counts roll over monthly in `usage.json`
  with a soft cap of 950/1000 on Tavily.
- **stdio hygiene.** `fetch_url` redirects crawl4ai's banner output at the
  file-descriptor level so it can't corrupt the JSON-RPC stream, and unwraps
  crawl4ai's `StringCompatibleMarkdown` into a plain string.
- **`list_dir` shape.** Returns a single dict with an explicit `count` + flat
  `names` list so cardinality survives downstream prompt truncation (a bare
  list could get clipped to a few entries and look "complete").
- **`index_document`** chunks by a sliding word window (`size=400`, `overlap=80`)
  — heuristic by design (semantic chunking is a later session).

### Gateway — the LLM + embedding bridge

[gateway.py](gateway.py) is the single place the agent talks to the LLM. It:

- Auto-starts `llm_gatewayV7` on **port 8107** if it isn't already up
  (`ensure_gateway()`), idempotently.
- Loads V7's `client.py` without polluting `sys.path` (the gateway has its own
  `schemas.py` that would shadow the agent's).
- Re-exports `LLM` (chat) and an `embed()` helper.

**V7 = V3 + one endpoint: `POST /v1/embed`.** The embedding subsystem
([llm_gatewayV7/embedders.py](llm_gatewayV7/embedders.py)) produces **768-dim**
vectors via a failover ring: **Ollama `nomic-embed-text`** (local, default) →
**Gemini `gemini-embedding-001`** (`outputDimensionality=768`). Both pinned to
768 so failover doesn't invalidate the FAISS index. `task_type`
(`retrieval_document` vs `retrieval_query`) is passed through natively.

`auto_route` tells the gateway which routing role a chat call is for —
`perception`, `decision`, `memory` — so it can pick an appropriate model tier.

---

## Retrieval-augmented generation (RAG) flow

The S7 headline feature is ingest-then-query over documents:

```
1. INGEST    Goal: "make attention.md searchable"
             Decision → index_document("papers/attention.md")
             → _chunk_text() → memory.add_fact() per chunk (each embedded)
             → chunks land in memory.json + FAISS index, descriptor "[sandbox:… chunk i/N] …"

2. QUERY     Goal: "answer: what problem does attention solve?"
             Perception sees [sandbox:…] facts → steers to "query the knowledge base"
             Decision → search_knowledge("what problem does attention solve")
             → memory.read(kinds=["fact"]) → FAISS cosine search → top-k chunks

3. SYNTHESISE
             chunk previews are surfaced inline in the next Decision prompt
             → Decision answers directly from the retrieved chunks
```

`sandbox/papers/` ships with five sample markdown docs (`attention.md`,
`cot.md`, `dpo.md`, `lora.md`, `react.md`) to exercise this path.

---

## State & data layout

```
.
├── agent7.py, schemas.py, memory.py, vector_index.py,
│   perception.py, decision.py, action.py, artifacts.py,
│   gateway.py, mcp_server.py, test_mcp_server.py
├── sandbox/                # file-tool working dir (git-ignored)
│   └── papers/*.md         # sample corpus for indexing/RAG
├── state/                  # runtime state (git-ignored)
│   ├── memory.json         # the MemoryItem store
│   ├── index.faiss         # binary FAISS index
│   └── index_ids.json      # parallel ids list (position → MemoryItem id)
├── usage.json              # Tavily/DDG monthly usage counters (git-ignored)
├── llm_gatewayV7/          # the LLM + embedding gateway (separate service)
├── pyproject.toml          # dependency source of truth (uv)
└── .env                    # secrets (git-ignored; copy from .env.example)
```

`state/`, `sandbox/`, `usage.json`, and `.env` are git-ignored. The clean-slate
story is `rm -rf state/` (or `memory.clear()`).

---

## Setup & running

**Prerequisites**

- Python ≥ 3.11 and [uv](https://docs.astral.sh/uv/).
- The **`llm_gatewayV7`** service (see [llm_gatewayV7/README.md](llm_gatewayV7/README.md)).
- For embeddings: a local **Ollama** with `nomic-embed-text` pulled, *or* a
  `GEMINI_API_KEY` for the Gemini fallback.
- A `TAVILY_API_KEY` for `web_search` (DuckDuckGo is used if absent).

**Install & run**

```bash
# 1. secrets
cp .env.example .env        # then fill in TAVILY_API_KEY (and GEMINI_API_KEY if used)

# 2. dependencies
uv sync                     # uses pyproject.toml

# 3. (optional) start the gateway yourself, else agent7 auto-starts it
cd llm_gatewayV7 && ./run.sh   # serves on :8107

# 4. run the agent
uv run agent7.py "Index sandbox/papers/attention.md, then tell me what problem attention solves."
```

If no query is passed, `agent7.py` runs a default Tokyo/Kolkata time-difference
query.

---

## Configuration

| Variable | Used by | Purpose |
|----------|---------|---------|
| `TAVILY_API_KEY` | mcp_server | Primary web search (DDG fallback if unset) |
| `GEMINI_API_KEY` | gateway | Chat + embedding fallback provider |
| `LLM_GATEWAY_V7_URL` | gateway client | Override gateway URL (default `http://localhost:8107`) |
| `OLLAMA_URL` | gateway embedders | Ollama base URL (default `http://localhost:11434`) |
| `EMBED_OLLAMA_MODEL` | gateway embedders | Default `nomic-embed-text` — **do not change after building an index** |
| `EMBED_FALLBACK_MODEL` | gateway embedders | Default `gemini-embedding-001` (768-dim) |
| `EMBED_ORDER` | gateway embedders | Comma-separated failover order |

Agent-side constants worth knowing: `MAX_ITERATIONS=20` ([agent7.py](agent7.py)),
`ARTIFACT_THRESHOLD_BYTES=4096` ([action.py](action.py)), embedding dim **768**
([llm_gatewayV7/embedders.py](llm_gatewayV7/embedders.py)).

---

## Testing

```bash
uv run pytest -v test_mcp_server.py          # all tool tests
uv run pytest -v -m "not network" test_mcp_server.py   # skip internet-bound tests
```

Markers: `network` (needs internet), `embed` (needs gateway V7's embed endpoint).

---

## Design principles & invariants

- **Typed boundaries.** Layers exchange Pydantic models from [schemas.py](schemas.py),
  never free-form dicts.
- **Bytes are isolated.** Only the artifact store holds raw bytes; they reach an
  LLM only when Perception attaches them to a goal.
- **One classifier call for ambiguous writes; zero for deterministic ones.**
  Tool outcomes and indexed chunks are written without an LLM.
- **The embedding model is a project-level constant.** Changing it (or its dim)
  silently invalidates every vector already in the FAISS index. The index guards
  against dimension drift by raising.
- **Goal identity is positional**, so the LLM can't drift it across iterations.

---

## Known limitations & caveats

These are documented honestly so they aren't mistaken for bugs:

1. **Vector-only retrieval.** No hybrid retrieval / reciprocal-rank-fusion yet —
   keyword search is only a fallback, not blended in.
2. **Heuristic chunking.** `index_document` uses a fixed sliding word window;
   semantic chunking is a later session.
3. **Append-only memory.** There is no superseding of stale facts — re-stating a
   preference adds a second item, and memory grows unbounded.
4. **Non-atomic writes.** `memory.json` and the FAISS index are written with
   plain `write_text` / `faiss.write_index` and updated independently — an
   interrupted write can leave them inconsistent.
5. **No persistent run tracing.** The loop prints to stdout but does not write a
   per-run JSONL trace.

> **Resolved in this revision:** the gateway-discovery path in
> [gateway.py](gateway.py) now resolves `llm_gatewayV7/` as a sibling of the
> agent (`Path(__file__).resolve().parent`), the `requirements.txt` drift vs
> `pyproject.toml` is fixed, and `test_list_dir` is updated to the S7 dict shape.
