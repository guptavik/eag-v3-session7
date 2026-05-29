# ReAct: Synergizing Reasoning and Acting in Language Models (2022)

## Problem
Chain-of-thought reasoning happens entirely inside the model, so it cannot gather new
facts and can drift into hallucination on knowledge-heavy tasks. Conversely, pure
action agents that call tools lack a visible reasoning trace to plan and adjust. The
two capabilities were typically studied in isolation.

## Method
ReAct interleaves free-form reasoning traces with discrete actions in a single
decision loop. At each step the model writes a thought, chooses an action (such as a
search or lookup), and then incorporates the returned observation before reasoning
again. The reasoning steps help the model decide which action to take next and how to
interpret results, while the actions ground the reasoning in external information,
reducing fabrication.

## Key contributions
- A prompting paradigm that combines step-by-step reasoning with tool-use actions in
  one interleaved trace of thought, action, and observation.
- Showed that grounding intermediate reasoning in retrieved observations reduces
  hallucination relative to reasoning alone.
- Demonstrated more interpretable, controllable agent behavior on both reasoning and
  decision-making benchmarks.

## Results
ReAct outperformed reasoning-only and action-only baselines on knowledge-intensive QA
(HotpotQA, FEVER) and on interactive decision benchmarks (ALFWorld, WebShop),
producing trajectories that are easier for humans to inspect and trust.
