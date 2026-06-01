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
- [Corpus manifest](#corpus-manifest)
- [Base query traces (A–H)](#base-query-traces-ah)
- [Custom RAG queries](#custom-rag-queries)
- [Architectural principles](#architectural-principles)
- [Reproduce the traces](#reproduce-the-traces)

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

---

## Corpus manifest

Two tracked directories back the assignment deliverables:

- **`sandbox/papers/`** (5 files) — reference summaries for **base queries E–H**.
  These 5 are also included in the big corpus.
- **`sandbox/corpus/`** (55 files) — the full RAG corpus for the **5 custom queries**.

Each file: ~200–350 words, template `Title/Year · Problem · Method · Key contributions · Results`.
Full manifest: [sandbox/corpus/MANIFEST.md](sandbox/corpus/MANIFEST.md)

| # | filename | title | year | tags |
|---|----------|-------|------|------|
| 1 | attention.md | Attention Is All You Need | 2017 | transformer, attention |
| 2 | bert.md | BERT: Pre-training of Deep Bidirectional Transformers | 2018 | pretraining, nlp |
| 3 | gpt3.md | Language Models are Few-Shot Learners (GPT-3) | 2020 | llm, few-shot |
| 4 | resnet.md | Deep Residual Learning (ResNet) | 2015 | vision, residual |
| 5 | word2vec.md | Efficient Estimation of Word Representations (word2vec) | 2013 | embeddings |
| 6 | seq2seq.md | Sequence to Sequence Learning with Neural Networks | 2014 | seq2seq |
| 7 | lstm.md | Long Short-Term Memory | 1997 | rnn, memory |
| 8 | dropout.md | Dropout: Preventing Overfitting | 2014 | regularization |
| 9 | batchnorm.md | Batch Normalization | 2015 | training, normalization |
| 10 | layernorm.md | Layer Normalization | 2016 | training, normalization |
| 11 | adam.md | Adam: A Method for Stochastic Optimization | 2014 | optimizer |
| 12 | gan.md | Generative Adversarial Networks | 2014 | generative |
| 13 | vae.md | Auto-Encoding Variational Bayes (VAE) | 2013 | generative |
| 14 | unet.md | U-Net: Biomedical Image Segmentation | 2015 | vision, segmentation |
| 15 | vit.md | An Image is Worth 16x16 Words (ViT) | 2020 | vision, transformer |
| 16 | cot.md | Chain-of-Thought Prompting | 2022 | reasoning, prompting |
| 17 | react.md | ReAct: Synergizing Reasoning and Acting | 2022 | reasoning, agents |
| 18 | scratchpad.md | Show Your Work: Scratchpads | 2021 | reasoning |
| 19 | self_consistency.md | Self-Consistency Improves Chain-of-Thought | 2022 | reasoning |
| 20 | tot.md | Tree of Thoughts | 2023 | reasoning, search |
| 21 | least_to_most.md | Least-to-Most Prompting | 2022 | reasoning, prompting |
| 22 | toolformer.md | Toolformer: LMs Can Use Tools | 2023 | agents, tools |
| 23 | reflexion.md | Reflexion: Verbal Reinforcement Learning | 2023 | agents, reasoning |
| 24 | instructgpt.md | InstructGPT: Following Instructions with Human Feedback | 2022 | rlhf, alignment |
| 25 | dpo.md | Direct Preference Optimization | 2023 | alignment, preference |
| 26 | ppo.md | Proximal Policy Optimization | 2017 | rl, policy |
| 27 | rlhf_summarize.md | Learning to Summarize from Human Feedback | 2020 | rlhf, alignment |
| 28 | constitutional_ai.md | Constitutional AI | 2022 | alignment, safety |
| 29 | kto.md | KTO: Prospect-Theoretic Optimization | 2024 | alignment, preference |
| 30 | lora.md | LoRA: Low-Rank Adaptation | 2021 | peft, efficiency |
| 31 | qlora.md | QLoRA: Finetuning of Quantized LLMs | 2023 | peft, quantization |
| 32 | adapters.md | Parameter-Efficient Transfer Learning (Adapters) | 2019 | peft |
| 33 | prefix_tuning.md | Prefix-Tuning | 2021 | peft, prompting |
| 34 | prompt_tuning.md | The Power of Scale for Prompt Tuning | 2021 | peft, prompting |
| 35 | distillation.md | Distilling the Knowledge in a Neural Network | 2015 | compression |
| 36 | llm_int8.md | LLM.int8(): 8-bit Matrix Multiplication | 2022 | quantization |
| 37 | flashattention.md | FlashAttention | 2022 | efficiency, attention |
| 38 | moe.md | Sparsely-Gated Mixture-of-Experts | 2017 | scaling, moe |
| 39 | switch_transformer.md | Switch Transformers | 2021 | scaling, moe |
| 40 | rag.md | Retrieval-Augmented Generation | 2020 | retrieval, rag |
| 41 | dpr.md | Dense Passage Retrieval | 2020 | retrieval |
| 42 | realm.md | REALM: Retrieval-Augmented Pre-Training | 2020 | retrieval, rag |
| 43 | fid.md | Fusion-in-Decoder | 2020 | retrieval, rag |
| 44 | colbert.md | ColBERT: Late Interaction Passage Search | 2020 | retrieval |
| 45 | faiss.md | Billion-Scale Similarity Search (FAISS) | 2017 | retrieval, ann |
| 46 | scaling_laws.md | Scaling Laws for Neural Language Models | 2020 | scaling |
| 47 | chinchilla.md | Training Compute-Optimal LLMs (Chinchilla) | 2022 | scaling |
| 48 | t5.md | Unified Text-to-Text Transformer (T5) | 2019 | pretraining |
| 49 | palm.md | PaLM: Scaling with Pathways | 2022 | llm, scaling |
| 50 | llama.md | LLaMA: Open Foundation Models | 2023 | llm |
| 51 | clip.md | Learning Transferable Visual Models (CLIP) | 2021 | multimodal, vision |
| 52 | dalle.md | Zero-Shot Text-to-Image Generation (DALL-E) | 2021 | multimodal, generative |
| 53 | flamingo.md | Flamingo: a Visual Language Model | 2022 | multimodal |
| 54 | whisper.md | Robust Speech Recognition (Whisper) | 2022 | speech |
| 55 | ddpm.md | Denoising Diffusion Probabilistic Models | 2020 | generative, diffusion |

---

## Base query traces (A–H)

All eight queries run verbatim against `agent7.py`. Traces: [docs/traces/base/](docs/traces/base/)

| Query | Iters | Bound | Trace |
|-------|-------|-------|-------|
| A — Shannon Wikipedia | 3 | ≤3 | [A.txt](docs/traces/base/A.txt) |
| B — Tokyo activities + weather | 4 | ≤8 | [B.txt](docs/traces/base/B.txt) |
| C run 1 — remember birthday | 4 | ≤4 | [C.txt](docs/traces/base/C.txt) |
| C run 2 — recall birthday | 3 | ≤3 | [C_run2.txt](docs/traces/base/C_run2.txt) |
| D — asyncio best practices | 6 | ≤6 | [D.txt](docs/traces/base/D.txt) |
| E — index attention.md + extract | 4 | ≤5 | [E.txt](docs/traces/base/E.txt) |
| F run 1 — index papers/ | 9 | ≤11 | [F.txt](docs/traces/base/F.txt) |
| F run 2 — cross-run recall | 3 | ≤3 | [F_run2.txt](docs/traces/base/F_run2.txt) |
| G — synonym recall (credit assignment) | 3 | ≤4 | [G.txt](docs/traces/base/G.txt) |
| H — ReAct vs CoT comparison | 3 | ≤3 | [H.txt](docs/traces/base/H.txt) |

### Trace excerpts

**A — Shannon Wikipedia** (3 iters · `fetch_url` → 262 KB artifact → attach → answer):
> Claude Shannon was born on April 30, 1916, and passed away on February 24, 2001.
> Key contributions: (1) the Mathematical Theory of Communication, (2) the Source Coding
> Theorem, (3) the Shannon-Hartley Channel Capacity theorem.

**C run 2 — cross-run birthday recall** (3 iters · zero tool calls · FAISS):
> Mom's birthday is on 15 May 2026. Reminders have been set for 1 May 2026 and 15 May 2026.

**F run 2 — cross-run FAISS persistence** (3 iters · fresh process · no re-indexing):
> Based on the indexed papers, chain-of-thought (CoT) reasoning is a technique designed
> to improve LLM performance on multi-step tasks by including intermediate reasoning steps
> in few-shot exemplars…

**G — synonym recall** (3 iters · "credit assignment" absent from all 5 papers):
> Each paper addresses credit assignment through its own mechanism: Attention via
> global self-attention weights; CoT via explicit step-by-step decomposition; DPO via
> direct policy optimization removing the explicit reward; LoRA via low-rank parameter
> constraints; ReAct via linking internal reasoning to external action feedback.

**H — cross-doc synthesis** (3 iters · `search_knowledge` → cot.md + react.md chunks):
> CoT treats intermediate reasoning as a static internal cognitive process (purely within
> the model). ReAct treats it as a dynamic interactive loop — interleaving thoughts with
> tool actions so reasoning is grounded in external facts.

### Diagnostic note: G iteration history and state dependency

**State dependency:** G must run in the same state chain as F-run1 (no `--clear`
between them). If state is cleared before G, the FAISS index is empty, the model
correctly reports "I don't have access to the research papers", and the query loops
to the 20-iteration cap. Always run F-run1 → F-run2 → G → H as one uninterrupted group.

**Model size lesson:** An early run of G produced 17 iters (exceeded ≤4 bound) when
a small model was used. The model looped on `search_knowledge` because it correctly
judged the chunks as indirect and kept searching for something more specific. The fix
was not a SYSTEM rule — it was ensuring the router selects a sufficiently capable
model tier for the Decision layer. With the right model, G completes in 4 iters
without any SYSTEM patch. **Lesson: when an agent loops, check the model tier before
adding SYSTEM rules.**

---

## Custom RAG queries

Five queries against the 55-paper corpus. At least two require **semantic recall** —
the query words do not appear in any chunk that answers them.

Traces: [docs/traces/custom/](docs/traces/custom/)

| # | Query | Type | With-corpus | No-corpus |
|---|-------|------|-------------|-----------|
| Q1 | Across these papers, how do they handle the credit assignment problem? | **Semantic** | [1_with.txt](docs/traces/custom/1_with.txt) | [1_nocorpus.txt](docs/traces/custom/1_nocorpus.txt) |
| Q2 | Which methods make adapting a huge model affordable on a single GPU? | **Semantic** | [2_with.txt](docs/traces/custom/2_with.txt) | [2_nocorpus.txt](docs/traces/custom/2_nocorpus.txt) |
| Q3 | What are the three key contributions of the Transformer according to the attention paper? | Index-only | [3_with.txt](docs/traces/custom/3_with.txt) | [3_nocorpus.txt](docs/traces/custom/3_nocorpus.txt) |
| Q4 | Compare how DPO and PPO-style RLHF approach preference optimization. | Cross-doc synthesis | [4_with.txt](docs/traces/custom/4_with.txt) | [4_nocorpus.txt](docs/traces/custom/4_nocorpus.txt) |
| Q5 | Which papers teach a model to reason before answering, and how do they differ? | Semantic synthesis | [5_with.txt](docs/traces/custom/5_with.txt) | [5_nocorpus.txt](docs/traces/custom/5_nocorpus.txt) |

### Semantic recall proof (Q1 and Q2)

The phrases `credit assignment`, `single GPU`, `one GPU`, and `affordable` are **absent** from every corpus chunk:

```powershell
# run from repo root — all should print nothing
Select-String -Pattern "credit assignment" sandbox\corpus\*.md
Select-String -Pattern "single gpu|one gpu" sandbox\corpus\*.md -CaseSensitive:$false
Select-String -Pattern "affordable" sandbox\corpus\*.md
```

Vector search surfaces the right papers by concept, not by keyword:

- **Q1** → seq2seq (temporal flow), attention (global weights), layernorm (gradient
  stability), flashattention (sequence length), constitutional\_ai (feedback loop),
  KTO (value assignment), ReAct (action feedback) — all relate to "how does the system
  know which part deserves credit?" without ever using those words.

- **Q2** → LoRA (low-rank updates), QLoRA (4-bit quantized base + adapters), Adapters
  (bottleneck modules), Prompt Tuning (soft prompts), GPT-3 (no-weight in-context),
  Distillation (student from teacher) — all reduce the cost of adapting a large model
  without the corpus mentioning "affordable" or "single GPU."

### With vs without: contrast summary

| Q | With-corpus (iters) | No-corpus outcome |
|---|--------------------|--------------------|
| Q1 | 3 — cites 7 indexed papers, no web search | 4 — generic RL-theory answer from web search, no corpus citations |
| Q2 | 3 — cites LoRA/QLoRA/Adapters/etc. | 3 — generic answer, no provenance |
| Q3 | 3 — quotes from attention.md chunk | 4 — correct from parametric knowledge only |
| Q4 | 3 — synthesises dpo.md + ppo.md + instructgpt.md | 3 — parametric answer, no chunk sources |
| Q5 | 4 — cites ReAct, Reflexion, Constitutional AI | 7 — web search needed, less specific |

---

## Architectural principles

### 1. Tool-blindness in Perception

Perception's SYSTEM prompt names **zero MCP tools**. Tool-selection guidance lives in
Decision's SYSTEM and in the docstrings on the MCP tools themselves.

**The gate (run after any edit to perception.py):**

```bash
uv run pytest -v test_perception_tool_blindness.py
grep -E "web_search|fetch_url|get_time|currency_convert|read_file|list_dir|create_file|update_file|edit_file|index_document|search_knowledge" perception.py && echo FAIL || echo PASS
```

**Why this matters:** if Perception names tools, it performs tool selection by emitting
goal text like "use `index_document` on this file." This seems harmless but is
architecturally wrong. Tool guidance pushed into Perception's SYSTEM becomes context
bloat as the tool set grows, and it breaks the clean boundary that lets Decision
independently reason about which tool fits each goal. The guidance belongs in the tool's
docstring, where it co-locates with the tool definition and the model sees it precisely
when it is selecting a tool.

### 2. Diagnostic discipline: fix the rendering, not the SYSTEM

When a role misbehaves, the reflex is to add a rule to its SYSTEM prompt. The right
procedure is to first reconstruct what the role **actually saw** on the failing turn:

1. **Capture** the trace from the failing iteration.
2. **Identify** which role produced the wrong output.
3. **Reconstruct** the exact prompt it received by reading the source code that builds it.
   Pay attention to truncation and fields that may be dropped.
4. **Ask:** given that input, was the output rational?
   - **Yes** → the bug is in the rendering layer. Fix `_format_hits`, `_format_history`,
     or similar. Do **not** add a SYSTEM rule.
   - **No** → the bug is in the role's SYSTEM or the model tier.
5. **Apply** the fix at the right boundary only.

**Session 7 examples:**

*Mom's birthday query (C run 2):* First fix attempt added a SYSTEM rule to Decision
saying "answer from memory when memory contains the date." Actual cause: `_format_hits`
rendered the descriptor ("mom's birthday remembered") but dropped `value.raw` which
contained "15 May 2026." Fix: render the `raw` field. SYSTEM addition removed.

*Synonym recall loop (G):* An early run produced 17 iters when a small model was used.
The model correctly judged the retrieved chunks as only indirectly related and kept
searching for something more specific. Root cause: model capability, not a rendering
or architecture bug. Fix: ensure the router selects a sufficiently capable model tier
for Decision. With the right tier, G completes in 4 iters without any SYSTEM patch.

### 3. Byte isolation

Raw bytes reach an LLM **only** when Perception explicitly attaches an artifact to a
goal. The artifact store holds bytes; Memory holds handles + one-line descriptors.
A 262 KB Wikipedia page touches exactly one LLM call per run — the extraction turn
where Perception sets `attach_artifact_id`.

### 4. Frozen embedding model (768-dim)

The embedding model is pinned at the gateway level (Ollama `nomic-embed-text` →
768-dim; Gemini `gemini-embedding-001` → `outputDimensionality=768`). Changing either
model or the dimension **silently invalidates** every vector in the FAISS index. The
index raises on dimension mismatch as a guard rail, but the invalidation itself is
silent. Treat the model as a project-level constant for the lifetime of an index.

---

## Reproduce the traces

### Prerequisites

- `uv sync` (installs `tzdata`, `faiss-cpu`, `numpy`, etc.)
- Gateway running: `cd llm_gatewayV7 && uv run main.py` (or let `agent7` auto-start it)
- `.env` with `GEMINI_API_KEY`, `GROQ_API_KEY`, and optionally `TAVILY_API_KEY`

### ⚠️ State management

The base queries share FAISS state across groups. **Never `--clear` inside a group.**

| Group | Queries | Rule |
|-------|---------|------|
| 1 | A → B → C → C_run2 → D | `--clear` on A only |
| 2 | E | `--clear` on E |
| 3 | F-run1 → F-run2 → **G** → H | `--clear` on F-run1 only — G and H **require** F's index |

If you clear state before G, the FAISS index is empty and G loops to the 20-iter cap.

### Base traces (A–H)

```powershell
# Group 1 — web + memory
uv run run_query.py --clear --out docs\traces\base\A.txt `
  "Fetch https://en.wikipedia.org/wiki/Claude_Shannon and tell me his birth date, death date, and three key contributions to information theory."

uv run run_query.py --out docs\traces\base\B.txt `
  "Find 3 family-friendly things to do in Tokyo this weekend. Check Saturday's weather forecast there and tell me which one is most appropriate."

uv run run_query.py --out docs\traces\base\C.txt `
  "My mom's birthday is 15 May 2026. Remember that and create reminders for two weeks before and on the day."

uv run run_query.py --out docs\traces\base\C_run2.txt `
  "When is mom's birthday?"

uv run run_query.py --out docs\traces\base\D.txt `
  'Search for "Python asyncio best practices", read the top 3 results, and give me a short numbered list of the advice they agree on.'

# Group 2 — single-doc RAG
uv run run_query.py --clear --out docs\traces\base\E.txt `
  "Index the file papers/attention.md and tell me what the three key contributions of the Transformer architecture are according to this paper."

# Group 3 — RAG + cross-run + semantic (must run in sequence, no clear after F)
uv run run_query.py --clear --out docs\traces\base\F.txt `
  "Index every .md file under papers/. Confirm how many chunks were indexed in total."

uv run run_query.py --out docs\traces\base\F_run2.txt `
  "Across the papers I have indexed, what do they say about chain-of-thought reasoning?"

uv run run_query.py --out docs\traces\base\G.txt `
  "Across these papers, how do they handle the credit assignment problem?"

uv run run_query.py --out docs\traces\base\H.txt `
  "Compare how the ReAct paper and the Chain-of-Thought paper differ in their treatment of intermediate reasoning."
```

**Verify bounds:**
```powershell
foreach ($f in Get-ChildItem docs\traces\base\*.txt) {
    $n = (Select-String "── iter" $f.FullName).Count
    Write-Host "$($f.Name): $n iters"
}
# A:3 B:≤8 C:4 C_run2:3 D:≤6 E:≤5 F:≤11 F_run2:3 G:≤4 H:3
```

### Custom queries (5 × with-corpus + 5 × no-corpus)

```powershell
# --- no-corpus runs (cleared state, no index) ---
uv run run_query.py --clear --out docs\traces\custom\1_nocorpus.txt `
  "Across these papers, how do they handle the credit assignment problem?"
uv run run_query.py --out docs\traces\custom\2_nocorpus.txt `
  "Which methods make adapting a huge model affordable on a single GPU?"
uv run run_query.py --out docs\traces\custom\3_nocorpus.txt `
  "What are the three key contributions of the Transformer according to the attention paper?"
uv run run_query.py --out docs\traces\custom\4_nocorpus.txt `
  "Compare how DPO and PPO-style RLHF approach preference optimization."
uv run run_query.py --out docs\traces\custom\5_nocorpus.txt `
  "Which papers teach a model to reason before answering, and how do they differ?"

# --- build the full corpus index (~3 min) ---
uv run python -c "import memory; memory.clear()"
uv run build_corpus_index.py corpus   # 55 files → 55 chunks

# --- with-corpus runs (shared index, no clear) ---
uv run run_query.py --out docs\traces\custom\1_with.txt `
  "Across these papers, how do they handle the credit assignment problem?"
uv run run_query.py --out docs\traces\custom\2_with.txt `
  "Which methods make adapting a huge model affordable on a single GPU?"
uv run run_query.py --out docs\traces\custom\3_with.txt `
  "What are the three key contributions of the Transformer according to the attention paper?"
uv run run_query.py --out docs\traces\custom\4_with.txt `
  "Compare how DPO and PPO-style RLHF approach preference optimization."
uv run run_query.py --out docs\traces\custom\5_with.txt `
  "Which papers teach a model to reason before answering, and how do they differ?"
```
