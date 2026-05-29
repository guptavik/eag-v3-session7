# Session 7 — Backlog

Actionable work to deliver the RAG assignment: pass the 8 base queries (A–H) within
their iteration bounds, build a 50+ item corpus, design 5 custom queries (≥2 semantic
recall) that work with the index and fail without it, and ship the README + video.

Design spec: [docs/superpowers/specs/2026-05-29-s7-rag-corpus-and-traces-design.md](docs/superpowers/specs/2026-05-29-s7-rag-corpus-and-traces-design.md)

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · **P0** must-have · **P1**
important · **P2** nice-to-have.

---

## Epic 1 — Corpus (two tracked dirs)

- [ ] **P0** Author the 5 reference summaries under `sandbox/papers/` (`attention.md`, `cot.md`, `dpo.md`, `lora.md`, `react.md`) — used by base queries E–H (keeps F at ~15 chunks / 11 iters).
- [ ] **P0** Curate a list of ~55 well-known AI/ML papers (incl. the 5 above) for the big corpus.
- [ ] **P0** Author ~55 `.md` summaries under `sandbox/corpus/` (~200–350 words; sections: Title/Year, Problem, Method, Key contributions, Results).
- [ ] **P0** Write `sandbox/corpus/MANIFEST.md` (filename · title · year · topic tags).
- [ ] **P1** Sanity-check factual accuracy of the 5 reference papers (E–H depend on them).
- [ ] **P2** Spot-check chunk counts (≈400-word windows, 80 overlap) per file.

## Epic 2 — Tooling / hardening (behavior-neutral)

- [ ] **P1** Add `run_query.py` helper: runs a query via `agent7.run()` and tees stdout to a trace file.
- [ ] **P1** Reword the two `list_dir` comments in `perception.py` so a file-level `grep` for tool names is clean.
- [ ] **P2** Add a `clear_state` convenience (wraps `memory.clear()`) for no-corpus runs.
- [x] **P0** Fix gateway-discovery path in `gateway.py` (sibling resolution).
- [x] **P1** Fix stale `test_list_dir` + `requirements.txt` drift.

## Epic 3 — Base traces (A–H), within iteration bounds

- [ ] **P0** A — Shannon Wikipedia (≤3 iters; artifact attach).
- [ ] **P0** B — Tokyo activities + Saturday weather (≤8; multi-goal carryover). *Needs Tavily.*
- [ ] **P0** C — Mom's birthday run1 (≤4) + run2 (≤3); durable memory across runs (no clear between).
- [ ] **P0** D — Asyncio best practices, top 3 synthesis (≤6). *Needs Tavily.*
- [ ] **P0** E — Index `papers/attention.md`, extract 3 Transformer contributions (≤5).
- [ ] **P0** F — Index `papers/` (5 files) run1 (≤11) + cross-run recall run2 (≤3); FAISS persistence.
- [ ] **P0** G — Synonym recall: "credit assignment problem" (≤4); vector beats keyword.
- [ ] **P0** H — Compare ReAct vs CoT intermediate reasoning (≤3).
- [ ] **P0** Capture each to `docs/traces/base/<X>.txt`; verify bound; note any miss as a diagnostic.

## Epic 4 — Custom queries (5; ≥2 semantic recall)

- [ ] **P0** Finalize the 5 queries against the authored corpus (proposed set in the spec).
- [ ] **P0** Q1 (semantic) — credit-assignment across papers; `_with` + `_nocorpus` traces.
- [ ] **P0** Q2 (semantic) — "adapt a huge model affordably on one GPU"; `_with` + `_nocorpus`.
- [ ] **P0** Q3 (index-only) — three Transformer contributions; `_with` + `_nocorpus`.
- [ ] **P0** Q4 (cross-doc) — DPO vs PPO-style RLHF; `_with` + `_nocorpus`.
- [ ] **P0** Q5 (semantic synthesis) — "reason before answering" papers; `_with` + `_nocorpus`.
- [ ] **P0** Confirm ≥2 are true semantic recall (answer words absent from answering chunks; verify via `grep`).
- [ ] **P0** Confirm each `_nocorpus` run fails (declines / loops / wrong) from cleared state.

## Epic 5 — Deliverables (README + repo)

- [ ] **P0** README: Corpus manifest section.
- [ ] **P0** README: Base traces (A–H).
- [ ] **P0** README: Custom queries (5) + no-corpus comparison.
- [ ] **P0** README: Architectural principles (tool-blindness, diagnostic discipline, byte isolation, frozen embed model).
- [ ] **P1** README: How to reproduce.
- [ ] **P1** Add `.gitignore` exceptions (`!sandbox/papers/`, `!sandbox/papers/**`, `!sandbox/corpus/`, `!sandbox/corpus/**`) so both corpora + manifest are tracked while `state/` and scratch `sandbox/` stay ignored.
- [ ] **P1** Commit corpus + traces + docs to git.

## Epic 6 — Verification gates

- [ ] **P0** `grep` over `perception.py` returns zero MCP tool names.
- [ ] **P0** `uv run pytest -v test_mcp_server.py` green.
- [ ] **P0** All 8 base traces within bounds.
- [ ] **P0** All 5 custom queries: with-index correct + cited; no-index fails.

## Epic 7 — Video

- [ ] **P1** Write shot-list / script (architecture tour → live base query → live semantic custom query → no-corpus comparison).
- [ ] **P1** Record + link in README (user records).

---

### Notes

- Corpus lives at `sandbox/corpus/` (so `index_document`/`read_file` index it
  unchanged) and is git-tracked via a `.gitignore` exception. Resolved in spec.
- Iteration bounds are hard gates; a miss triggers the diagnostic procedure, not a
  bound bump.
