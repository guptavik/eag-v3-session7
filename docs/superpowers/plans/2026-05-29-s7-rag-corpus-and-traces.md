# Session 7 — RAG Corpus, Traces & Architecture Proof — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pass the 8 base queries (A–H) verbatim within their iteration bounds, build a 50+ item RAG corpus, and prove 5 custom queries answer correctly with the index and fail without it — then assemble the README deliverable.

**Architecture:** No change to the agent's four-layer loop. We add data (two tracked corpora under `sandbox/`), two behavior-neutral helpers (`run_query.py` trace runner, `build_corpus_index.py` bulk ingester), captured traces under `docs/traces/`, a `.gitignore` exception, and README sections. One source edit: reword two comments in `perception.py` so the tool-blindness grep gate is clean at the file level.

**Tech Stack:** Python 3.11, `uv`, MCP (FastMCP stdio), FAISS, `llm_gatewayV7` (chat + `/v1/embed`), pytest.

**Spec:** [docs/superpowers/specs/2026-05-29-s7-rag-corpus-and-traces-design.md](../specs/2026-05-29-s7-rag-corpus-and-traces-design.md)

---

## Conventions

- Run all commands from the repo root `z:\eag-v3\eag-v3-session7`.
- Use the **Bash** tool for `grep`/pipes; `uv run` works the same in bash and PowerShell.
- The gateway must be reachable on `:8107` with an embedding provider (Ollama
  `nomic-embed-text` or `GEMINI_API_KEY`) and `TAVILY_API_KEY` set in `.env`.
- "Iteration bound" = the agent must reach `[done]` / final answer at or before the
  named iteration. The loop prints `─── iter N ───` per iteration; count the last one.

## File structure

| Path | Create/Modify | Responsibility |
|------|---------------|----------------|
| `tests/test_perception_tool_blindness.py` | Create | Gate: no MCP tool name in Perception SYSTEM or file |
| `perception.py` | Modify (2 comments) | Reword `list_dir` mentions to intent language |
| `.gitignore` | Modify | Track `sandbox/papers/` + `sandbox/corpus/` |
| `run_query.py` | Create | Run one query via `agent7.run`, tee trace to file; `--clear` |
| `build_corpus_index.py` | Create | Bulk-index a sandbox dir via the real `index_document` tool |
| `sandbox/papers/*.md` (5) | Create | Reference summaries for base E–H |
| `sandbox/corpus/*.md` (~55) | Create | 50+ item RAG corpus for custom queries |
| `sandbox/corpus/MANIFEST.md` | Create | Corpus manifest table |
| `docs/traces/base/A.txt … H.txt` | Create | Base query traces |
| `docs/traces/custom/{1..5}_with.txt`, `{1..5}_nocorpus.txt` | Create | Custom traces |
| `README.md` | Modify | Add manifest + traces + principles + reproduce sections |
| `docs/VIDEO.md` | Create | Video shot-list/script |

---

## Task 1: Tool-blindness grep gate (TDD)

**Files:**
- Create: `tests/test_perception_tool_blindness.py`
- Modify: `perception.py` (two comments near lines 201, 203)

- [ ] **Step 1: Write the failing test**

Create `tests/test_perception_tool_blindness.py`:

```python
"""Architectural gate: Perception is tool-blind.

No MCP tool name may appear in Perception's SYSTEM prompt (tool selection is
Decision's job). We also assert the whole file is clean so a literal `grep`
over perception.py — incl. comments — returns nothing.
"""
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest tests/test_perception_tool_blindness.py -v`
Expected: `test_system_prompt_names_no_tools` PASSES, `test_file_level_grep_is_clean`
FAILS with `perception.py mentions MCP tools (reword comments): ['list_dir']`.

- [ ] **Step 3: Reword the two comments in `perception.py`**

Find (around lines 200–204):

```python
    # list when a discovery action (e.g. list_dir) reveals work that wasn't
    # knowable on iter 1. NOTES_RUNS §6 (4): the previous hard-truncate to
    # `len(prior_goals)` blocked F-run-1 verbatim — list_dir revealed five
    # papers, but the goal list was locked to the three placeholders emitted
```

Replace with:

```python
    # list when a discovery action (e.g. a directory listing) reveals work
    # that wasn't knowable on iter 1. NOTES_RUNS §6 (4): the previous
    # hard-truncate to `len(prior_goals)` blocked F-run-1 verbatim — the
    # directory listing revealed five papers, but the goal list was locked to
    # the three placeholders emitted
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_perception_tool_blindness.py -v`
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_perception_tool_blindness.py perception.py
git commit -m "test: enforce Perception tool-blindness gate; reword comments"
```

---

## Task 2: Track the corpora in git

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add exceptions under the `sandbox/` ignore**

The current `.gitignore` contains `sandbox/`. Add these lines immediately after it:

```gitignore
# but keep the committed corpora (runtime scratch stays ignored)
!sandbox/papers/
!sandbox/papers/**
!sandbox/corpus/
!sandbox/corpus/**
```

- [ ] **Step 2: Verify the exception works**

```bash
mkdir -p sandbox/papers sandbox/corpus
echo "probe" > sandbox/papers/_probe.md
git check-ignore sandbox/papers/_probe.md; echo "exit=$?"
```

Expected: no path printed and `exit=1` (NOT ignored). If it prints the path
(`exit=0`), the exception is wrong — re-check ordering.

- [ ] **Step 3: Clean up the probe and commit**

```bash
rm sandbox/papers/_probe.md
git add .gitignore
git commit -m "chore: track sandbox/papers and sandbox/corpus in git"
```

---

## Task 3: `run_query.py` trace runner

**Files:**
- Create: `run_query.py`

- [ ] **Step 1: Write `run_query.py`**

```python
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
```

- [ ] **Step 2: Smoke-test it on a no-network query**

```bash
uv run run_query.py --clear --out docs/traces/_smoke.txt "What is the current time in Asia/Kolkata?"
```

Expected: prints the run trace, ends with `FINAL: ...`, and writes
`docs/traces/_smoke.txt`. Confirm the file exists and contains `─── iter 1`:

```bash
test -f docs/traces/_smoke.txt && grep -c "iter 1" docs/traces/_smoke.txt
```

Expected: prints `1` (or more).

- [ ] **Step 3: Remove the smoke file and commit**

```bash
rm docs/traces/_smoke.txt
git add run_query.py
git commit -m "feat: add run_query.py trace runner with --clear"
```

---

## Task 4: `build_corpus_index.py` bulk ingester

**Files:**
- Create: `build_corpus_index.py`

Indexing 55 files through the agent loop would exceed the iteration cap, so the
custom-query corpus is indexed directly through the real `index_document` MCP tool.

- [ ] **Step 1: Write `build_corpus_index.py`**

```python
"""build_corpus_index.py — bulk-index a sandbox directory via the index_document tool.

Spawns the MCP server (same as agent7), lists .md files under the given sandbox
subdir, and calls index_document on each. Prints the total chunk count.

Usage:
    uv run build_corpus_index.py corpus
    uv run build_corpus_index.py papers
"""
from __future__ import annotations

import asyncio
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
                print(f"[index] {subdir}/{name}: {txt[:160]}")
                # the tool returns JSON with chunks_indexed; parse leniently
                import json
                try:
                    total += int(json.loads(txt).get("chunks_indexed", 0))
                except Exception:
                    pass
    print(f"[build_corpus_index] {len(files)} files, {total} chunks indexed into memory")


if __name__ == "__main__":
    sub = sys.argv[1] if len(sys.argv) > 1 else "corpus"
    asyncio.run(run(sub))
```

- [ ] **Step 2: Commit (smoke-tested in Task 8 once the corpus exists)**

```bash
git add build_corpus_index.py
git commit -m "feat: add build_corpus_index.py bulk ingester"
```

---

## Task 5: Author the 5 reference papers (`sandbox/papers/`)

**Files:**
- Create: `sandbox/papers/attention.md`, `cot.md`, `dpo.md`, `lora.md`, `react.md`

Each file uses this exact template (the section headings matter for clean chunking
and retrieval):

```markdown
# <Paper Title> (<Year>)

## Problem
<2-4 sentences: what gap or limitation the paper addresses.>

## Method
<3-6 sentences: the core technique, in plain language.>

## Key contributions
- <contribution 1>
- <contribution 2>
- <contribution 3>

## Results
<2-4 sentences: what it achieved / why it mattered.>
```

- [ ] **Step 1: Write `sandbox/papers/attention.md` (worked example — match this depth)**

```markdown
# Attention Is All You Need (2017)

## Problem
Recurrent and convolutional sequence models process tokens in order, which limits
parallelism and makes it hard to learn dependencies between distant positions. Long
training times and weak long-range modeling were the core limitations.

## Method
The Transformer replaces recurrence entirely with self-attention. Each position
attends to every other position through scaled dot-product attention, computed in
parallel across the whole sequence. Multiple attention heads let the model attend to
different relationships at once, and because attention is order-agnostic, sinusoidal
positional encodings inject token order. The architecture stacks attention and
feed-forward sublayers with residual connections and layer normalization.

## Key contributions
- Self-attention as the sole sequence-mixing mechanism, removing recurrence.
- Multi-head attention, letting the model jointly attend to different subspaces.
- Positional encoding to represent token order without sequential computation.

## Results
The Transformer set new state-of-the-art BLEU scores on English-German and
English-French translation while training far faster than recurrent baselines, and it
became the foundation for nearly all later large language models.
```

- [ ] **Step 2: Write the other four reference files** to the same template:
  `cot.md` (Chain-of-Thought Prompting, 2022), `dpo.md` (Direct Preference
  Optimization, 2023), `lora.md` (LoRA: Low-Rank Adaptation, 2021), `react.md`
  (ReAct: Synergizing Reasoning and Acting, 2022). Keep each factually accurate; CoT
  and ReAct must clearly describe intermediate/step-by-step reasoning (base H compares
  them); DPO must describe preference optimization without a reward model (custom Q4).

- [ ] **Step 3: Verify the set**

```bash
ls -1 sandbox/papers/*.md | wc -l        # expect 5
grep -l "## Key contributions" sandbox/papers/*.md | wc -l   # expect 5
```

- [ ] **Step 4: Commit**

```bash
git add sandbox/papers/
git commit -m "data: add 5 reference paper summaries for base queries E-H"
```

---

## Task 6: Author the 50+ item corpus (`sandbox/corpus/`) + manifest

**Files:**
- Create: ~55 `sandbox/corpus/*.md` + `sandbox/corpus/MANIFEST.md`

Use the **same template** as Task 5. The authoritative list (filename · title · year ·
tags) is below — it is also the manifest source. Copy the 5 reference summaries from
`sandbox/papers/` into `sandbox/corpus/` (same filenames) so the corpus is
self-contained.

**Authoring constraints (critical for the semantic-recall gate):**
- Do **not** write the literal phrases `"credit assignment"` or `"one GPU"` /
  `"affordable"` anywhere in the corpus (those are custom semantic queries Q1/Q2 —
  the answer concepts must be present, the query words must not). Use related wording
  instead (e.g., "assigning reward to earlier steps", "fits on a single consumer card",
  "low memory footprint").
- CoT/ReAct/scratchpad/self-consistency/ToT must describe step-by-step or
  intermediate reasoning (custom Q5). DPO + PPO + InstructGPT must describe preference
  optimization (custom Q4).

The list (55 files):

| filename | title | year | tags |
|---|---|---|---|
| attention.md | Attention Is All You Need | 2017 | transformer, attention |
| bert.md | BERT: Pre-training of Deep Bidirectional Transformers | 2018 | pretraining, nlp |
| gpt3.md | Language Models are Few-Shot Learners (GPT-3) | 2020 | llm, few-shot |
| resnet.md | Deep Residual Learning (ResNet) | 2015 | vision, residual |
| word2vec.md | Efficient Estimation of Word Representations (word2vec) | 2013 | embeddings |
| seq2seq.md | Sequence to Sequence Learning with Neural Networks | 2014 | seq2seq |
| lstm.md | Long Short-Term Memory | 1997 | rnn, memory |
| dropout.md | Dropout: A Simple Way to Prevent Overfitting | 2014 | regularization |
| batchnorm.md | Batch Normalization | 2015 | training, normalization |
| layernorm.md | Layer Normalization | 2016 | training, normalization |
| adam.md | Adam: A Method for Stochastic Optimization | 2014 | optimizer |
| gan.md | Generative Adversarial Networks | 2014 | generative |
| vae.md | Auto-Encoding Variational Bayes (VAE) | 2013 | generative |
| unet.md | U-Net: Convolutional Networks for Biomedical Segmentation | 2015 | vision, segmentation |
| vit.md | An Image is Worth 16x16 Words (ViT) | 2020 | vision, transformer |
| cot.md | Chain-of-Thought Prompting | 2022 | reasoning, prompting |
| react.md | ReAct: Synergizing Reasoning and Acting | 2022 | reasoning, agents |
| scratchpad.md | Show Your Work: Scratchpads for Intermediate Computation | 2021 | reasoning |
| self_consistency.md | Self-Consistency Improves Chain-of-Thought | 2022 | reasoning |
| tot.md | Tree of Thoughts | 2023 | reasoning, search |
| least_to_most.md | Least-to-Most Prompting | 2022 | reasoning, prompting |
| toolformer.md | Toolformer: LMs Can Teach Themselves to Use Tools | 2023 | agents, tools |
| reflexion.md | Reflexion: Language Agents with Verbal RL | 2023 | agents, reasoning |
| instructgpt.md | Training LMs to Follow Instructions (InstructGPT) | 2022 | rlhf, alignment |
| dpo.md | Direct Preference Optimization | 2023 | alignment, preference |
| ppo.md | Proximal Policy Optimization | 2017 | rl, policy |
| rlhf_summarize.md | Learning to Summarize from Human Feedback | 2020 | rlhf, alignment |
| constitutional_ai.md | Constitutional AI | 2022 | alignment, safety |
| kto.md | KTO: Model Alignment as Prospect-Theoretic Optimization | 2024 | alignment, preference |
| lora.md | LoRA: Low-Rank Adaptation | 2021 | peft, efficiency |
| qlora.md | QLoRA: Efficient Finetuning of Quantized LLMs | 2023 | peft, quantization |
| adapters.md | Parameter-Efficient Transfer Learning (Adapters) | 2019 | peft |
| prefix_tuning.md | Prefix-Tuning | 2021 | peft, prompting |
| prompt_tuning.md | The Power of Scale for Prompt Tuning | 2021 | peft, prompting |
| distillation.md | Distilling the Knowledge in a Neural Network | 2015 | compression |
| llm_int8.md | LLM.int8(): 8-bit Matrix Multiplication for Transformers | 2022 | quantization |
| flashattention.md | FlashAttention | 2022 | efficiency, attention |
| moe.md | Outrageously Large Neural Networks (Mixture of Experts) | 2017 | scaling, moe |
| switch_transformer.md | Switch Transformers | 2021 | scaling, moe |
| rag.md | Retrieval-Augmented Generation | 2020 | retrieval, rag |
| dpr.md | Dense Passage Retrieval | 2020 | retrieval |
| realm.md | REALM: Retrieval-Augmented LM Pre-Training | 2020 | retrieval, rag |
| fid.md | Fusion-in-Decoder | 2020 | retrieval, rag |
| colbert.md | ColBERT: Efficient Passage Search | 2020 | retrieval |
| faiss.md | Billion-Scale Similarity Search (FAISS) | 2017 | retrieval, ann |
| scaling_laws.md | Scaling Laws for Neural Language Models | 2020 | scaling |
| chinchilla.md | Training Compute-Optimal LLMs (Chinchilla) | 2022 | scaling |
| t5.md | Exploring the Limits of Transfer Learning (T5) | 2019 | pretraining |
| palm.md | PaLM: Scaling Language Modeling with Pathways | 2022 | llm, scaling |
| llama.md | LLaMA: Open and Efficient Foundation LMs | 2023 | llm |
| clip.md | Learning Transferable Visual Models (CLIP) | 2021 | multimodal, vision |
| dalle.md | Zero-Shot Text-to-Image Generation (DALL·E) | 2021 | multimodal, generative |
| flamingo.md | Flamingo: a Visual Language Model | 2022 | multimodal |
| whisper.md | Robust Speech Recognition via Weak Supervision (Whisper) | 2022 | speech |
| ddpm.md | Denoising Diffusion Probabilistic Models | 2020 | generative, diffusion |

- [ ] **Step 1: Author all 55 files** under `sandbox/corpus/` using the Task 5
  template and the table above. Reuse the 5 reference summaries verbatim.

- [ ] **Step 2: Write `sandbox/corpus/MANIFEST.md`**

Header + the table above:

```markdown
# Corpus Manifest

55 AI/ML paper summaries indexed by the Session 7 RAG agent. Each file follows the
same template (Title/Year · Problem · Method · Key contributions · Results).

| filename | title | year | tags |
|---|---|---|---|
<...the 55 rows above...>
```

- [ ] **Step 3: Verify count and structure**

```bash
ls -1 sandbox/corpus/*.md | grep -v MANIFEST | wc -l        # expect 55 (>= 50)
grep -L "## Key contributions" sandbox/corpus/*.md          # expect: only MANIFEST.md (or empty)
```

- [ ] **Step 4: Verify the semantic-query phrases are ABSENT**

```bash
grep -ri "credit assignment" sandbox/corpus/ ; echo "Q1 phrase hits above (expect none)"
grep -riE "one gpu|affordable" sandbox/corpus/ ; echo "Q2 phrase hits above (expect none)"
```

Expected: no matches. If any appear, reword those summaries (keep the concept, drop
the literal query phrase).

- [ ] **Step 5: Commit**

```bash
git add sandbox/corpus/
git commit -m "data: add 55-item AI/ML corpus + manifest"
```

---

## Task 7: Capture the 8 base traces (A–H)

**Files:**
- Create: `docs/traces/base/A.txt … H.txt`

State plan (clear points are deliberate): clear before A; A→B→C1→C2→D share state;
clear before E; clear before F1; F1→F2→G→H share state (G/H read F's `papers/` index).
Each `run_query.py` invocation is already a fresh process, which is what makes C/F
demonstrate cross-run persistence.

- [ ] **Step 1: A — Shannon Wikipedia (bound 3)**

```bash
uv run run_query.py --clear --out docs/traces/base/A.txt "Fetch https://en.wikipedia.org/wiki/Claude_Shannon and tell me his birth date, death date, and three key contributions to information theory."
```

Expected: ends with `FINAL:` containing the dates + 3 contributions; last
`─── iter N` has N ≤ 3.

- [ ] **Step 2: B — Tokyo activities + weather (bound 8)**

```bash
uv run run_query.py --out docs/traces/base/B.txt "Find 3 family-friendly things to do in Tokyo this weekend. Check Saturday's weather forecast there and tell me which one is most appropriate."
```

Expected: final answer picks one activity given the weather; N ≤ 8.

- [ ] **Step 3: C run 1 — remember birthday (bound 4)**

```bash
uv run run_query.py --out docs/traces/base/C.txt "My mom's birthday is 15 May 2026. Remember that and create reminders for two weeks before and on the day."
```

Expected: two `create_file` calls; N ≤ 4.

- [ ] **Step 4: C run 2 — recall birthday (bound 3), appended to same trace file**

```bash
uv run run_query.py --out docs/traces/base/C_run2.txt "When is mom's birthday?"
```

Expected: zero tool calls, answers `15 May 2026` from memory; N ≤ 3.

- [ ] **Step 5: D — Asyncio research (bound 6)**

```bash
uv run run_query.py --out docs/traces/base/D.txt 'Search for "Python asyncio best practices", read the top 3 results, and give me a short numbered list of the advice they agree on.'
```

Expected: numbered list; N ≤ 6.

- [ ] **Step 6: E — Single-doc index + extract (bound 5)**

```bash
uv run run_query.py --clear --out docs/traces/base/E.txt "Index the file papers/attention.md and tell me what the three key contributions of the Transformer architecture are according to this paper."
```

Expected: `index_document` on iter 1, then `search_knowledge`/answer citing the 3
contributions; N ≤ 5.

- [ ] **Step 7: F run 1 — index papers/ (bound 11)**

```bash
uv run run_query.py --clear --out docs/traces/base/F.txt "Index every .md file under papers/. Confirm how many chunks were indexed in total."
```

Expected: a directory-listing discovery goal, then 5 index goals appended, then a
chunk-count report (~15 chunks); N ≤ 11.

- [ ] **Step 8: F run 2 — cross-run recall (bound 3)**

```bash
uv run run_query.py --out docs/traces/base/F_run2.txt "Across the papers I have indexed, what do they say about chain-of-thought reasoning?"
```

Expected: fresh process reads persisted index, answers without re-indexing; N ≤ 3.

- [ ] **Step 9: G — synonym recall (bound 4)**

```bash
uv run run_query.py --out docs/traces/base/G.txt "Across these papers, how do they handle the credit assignment problem?"
```

Expected: vector path surfaces related chunks (the phrase isn't in the papers);
answer attributes ideas to sources; N ≤ 4.

- [ ] **Step 10: H — cross-doc synthesis (bound 3)**

```bash
uv run run_query.py --out docs/traces/base/H.txt "Compare how the ReAct paper and the Chain-of-Thought paper differ in their treatment of intermediate reasoning."
```

Expected: comparison drawing on both papers; N ≤ 3.

- [ ] **Step 11: Verify every bound, then commit**

For each trace, confirm the last iteration number is within bound:

```bash
for f in docs/traces/base/*.txt; do echo "$f: $(grep -o 'iter [0-9]*' "$f" | tail -1)"; done
```

If any exceeds its bound, STOP and apply the diagnostic discipline (reconstruct what
the role saw; fix the rendering, not the SYSTEM) before re-running. Then:

```bash
git add docs/traces/base/
git commit -m "docs: capture base query traces A-H within iteration bounds"
```

---

## Task 8: Custom queries — with-corpus and no-corpus traces

**Files:**
- Create: `docs/traces/custom/{1..5}_with.txt`, `docs/traces/custom/{1..5}_nocorpus.txt`

The five queries (finalize wording only if a `_nocorpus` run unexpectedly succeeds):

1. "Across these papers, how do they handle the credit assignment problem?" *(semantic)*
2. "Which methods make adapting a huge model affordable on a single GPU?" *(semantic)*
3. "What are the three key contributions of the Transformer according to the attention paper?" *(index-only)*
4. "Compare how DPO and PPO-style RLHF approach preference optimization." *(cross-doc)*
5. "Which papers teach a model to reason before answering, and how do they differ?" *(semantic synthesis)*

- [ ] **Step 1: Phase 1 — no-corpus runs (cleared state, no index)**

Run each query from a cleared state so the vector path is empty:

```bash
uv run run_query.py --clear --out docs/traces/custom/1_nocorpus.txt "Across these papers, how do they handle the credit assignment problem?"
uv run run_query.py --clear --out docs/traces/custom/2_nocorpus.txt "Which methods make adapting a huge model affordable on a single GPU?"
uv run run_query.py --clear --out docs/traces/custom/3_nocorpus.txt "What are the three key contributions of the Transformer according to the attention paper?"
uv run run_query.py --clear --out docs/traces/custom/4_nocorpus.txt "Compare how DPO and PPO-style RLHF approach preference optimization."
uv run run_query.py --clear --out docs/traces/custom/5_nocorpus.txt "Which papers teach a model to reason before answering, and how do they differ?"
```

Expected: each declines / says it has no indexed material / answers without sources
(or loops to cap). These are the "fails without the index" traces.

- [ ] **Step 2: Phase 2 — build the corpus index once**

```bash
uv run run_query.py --clear --out docs/traces/custom/_reset.txt "What time is it in UTC?"   # clears + leaves empty index
uv run build_corpus_index.py corpus
```

Expected: `[build_corpus_index] 55 files, NN chunks indexed into memory`.

(The reset run is only to clear state cleanly before bulk indexing; delete
`_reset.txt` afterward: `rm docs/traces/custom/_reset.txt`.)

- [ ] **Step 3: Phase 2 — with-corpus runs (no clear; shared index)**

```bash
uv run run_query.py --out docs/traces/custom/1_with.txt "Across these papers, how do they handle the credit assignment problem?"
uv run run_query.py --out docs/traces/custom/2_with.txt "Which methods make adapting a huge model affordable on a single GPU?"
uv run run_query.py --out docs/traces/custom/3_with.txt "What are the three key contributions of the Transformer according to the attention paper?"
uv run run_query.py --out docs/traces/custom/4_with.txt "Compare how DPO and PPO-style RLHF approach preference optimization."
uv run run_query.py --out docs/traces/custom/5_with.txt "Which papers teach a model to reason before answering, and how do they differ?"
```

Expected: each answers correctly and cites source files via `search_knowledge`.

- [ ] **Step 4: Confirm the with/without contrast holds**

```bash
for i in 1 2 3 4 5; do
  echo "=== Q$i ===";
  echo "with:     $(grep 'FINAL:' docs/traces/custom/${i}_with.txt | head -1 | cut -c1-90)";
  echo "nocorpus: $(grep 'FINAL:' docs/traces/custom/${i}_nocorpus.txt | head -1 | cut -c1-90)";
done
```

Expected: `with` rows contain substantive cited answers; `nocorpus` rows are empty /
refusal / wrong. If a `_nocorpus` run answered correctly, the query isn't index-
dependent — sharpen it and re-run both phases for that query.

- [ ] **Step 5: Commit**

```bash
git add docs/traces/custom/
git commit -m "docs: capture 5 custom RAG queries with/without corpus"
```

---

## Task 9: Assemble the README deliverable sections

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Append the deliverable sections** to `README.md` (after the existing
  content), each as a top-level `##` section:

  1. `## Corpus manifest` — paste the manifest table from
     `sandbox/corpus/MANIFEST.md`, prefixed with the file count and the note that
     `sandbox/papers/` (5 files) backs the base queries.
  2. `## Base query traces (A–H)` — for each query: the verbatim query, the iteration
     bound, the achieved iteration count, and a fenced block with the trace (or a
     relative link to `docs/traces/base/<X>.txt` plus a short excerpt).
  3. `## Custom RAG queries` — a table (query · type · with-index result · no-index
     result), then for each: links to `docs/traces/custom/<n>_with.txt` and
     `<n>_nocorpus.txt`, and one line explaining why it fails without the index. Mark
     which two are semantic recall and show the `grep` proof that the query phrase is
     absent from the corpus.
  4. `## Architectural principles` — tool-blindness (with the grep gate command),
     the diagnostic discipline (rendering vs SYSTEM, the 5-step procedure), byte
     isolation, and the frozen 768-dim embedding model.
  5. `## Reproduce the traces` — the exact `run_query.py` / `build_corpus_index.py`
     command sequence from Tasks 7–8.

- [ ] **Step 2: Verify links resolve**

```bash
grep -oE "docs/traces/[a-z]+/[A-Za-z0-9_]+\.txt" README.md | sort -u | while read p; do test -f "$p" && echo "ok $p" || echo "MISSING $p"; done
```

Expected: every referenced trace prints `ok`.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add corpus manifest, base + custom traces, principles to README"
```

---

## Task 10: Final verification gates

**Files:** none (verification only)

- [ ] **Step 1: Tool-blindness gate**

```bash
uv run pytest tests/test_perception_tool_blindness.py -v
grep -nE "web_search|fetch_url|get_time|currency_convert|read_file|list_dir|create_file|update_file|edit_file|index_document|search_knowledge" perception.py || echo "GREP CLEAN"
```

Expected: tests pass; grep prints `GREP CLEAN`.

- [ ] **Step 2: MCP tool tests green**

```bash
uv run pytest -v test_mcp_server.py
```

Expected: all pass (network-marked tests need internet).

- [ ] **Step 3: Bounds + contrast recap** — re-run the loops from Task 7 Step 11 and
  Task 8 Step 4; confirm all bounds hold and all five contrasts hold.

- [ ] **Step 4: Commit any final tweaks**

```bash
git add -A && git commit -m "chore: final verification pass for Session 7 deliverables" || echo "nothing to commit"
```

---

## Task 11: Video shot-list (P1)

**Files:**
- Create: `docs/VIDEO.md`

- [ ] **Step 1: Write `docs/VIDEO.md`** with a 3–5 minute shot list:

```markdown
# Submission Video — Shot List

1. (0:00) Repo tour: the four layers + the tool-blindness gate (`grep` over perception.py).
2. (0:45) Corpus: show `sandbox/corpus/` (55 files) + MANIFEST.
3. (1:15) Live base query E: index attention.md and extract 3 contributions (≤5 iters).
4. (2:00) Live custom semantic query (Q1 or Q2): show the answer with sources.
5. (2:45) No-corpus comparison: same query from cleared state fails.
6. (3:30) Diagnostic discipline: one sentence on "fix the rendering, not the SYSTEM".
```

- [ ] **Step 2: Commit**

```bash
git add docs/VIDEO.md
git commit -m "docs: add submission video shot-list"
```

---

## Self-review notes (author)

- **Spec coverage:** corpus (Tasks 5–6), base traces A–H (Task 7), 5 custom + no-corpus
  (Task 8), README manifest/traces/principles/reproduce (Task 9), backlog (already
  written), video (Task 11), tool-blindness + diagnostic discipline (Tasks 1, 9, 10),
  git tracking (Task 2). All spec sections map to a task.
- **Iteration-bound risk:** Task 7 ties each query to its bound and routes a miss
  through the diagnostic procedure rather than bumping the bound.
- **Semantic-recall gate:** enforced at authoring time (Task 6 Step 4 greps for phrase
  absence) and at trace time (Task 8 Step 4 confirms no-index failure).
- **Behavior neutrality:** `run_query.py` and `build_corpus_index.py` only orchestrate
  existing entry points; no change to the cognitive loop, schemas, or retrieval.
