# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models (2022)

## Problem
Large language models struggled with multi-step arithmetic, commonsense, and symbolic
reasoning when asked to produce an answer directly. Standard few-shot prompting gave
only the final answer in its examples, so the model never learned to work through the
intermediate steps a hard problem requires.

## Method
Chain-of-thought prompting adds a series of intermediate reasoning steps to each
few-shot exemplar, so the model is shown not just the answer but the worked path to
it. At inference the model then generates its own step-by-step reasoning before
committing to a final answer. The technique needs no fine-tuning or extra training; it
is purely a change in how exemplars are written, and it works best on sufficiently
large models where the reasoning ability emerges with scale.

## Key contributions
- Showed that prompting a model to emit explicit intermediate reasoning steps sharply
  improves performance on arithmetic and reasoning benchmarks.
- Demonstrated that this reasoning ability is emergent — it appears only once models
  pass a scale threshold.
- Established a simple, training-free prompting pattern that later reasoning methods
  (self-consistency, least-to-most, tree-of-thoughts) build on.

## Results
On the GSM8K math word-problem benchmark, chain-of-thought prompting with a large
model produced large absolute accuracy gains over direct-answer prompting, and similar
improvements held across commonsense and symbolic reasoning tasks.
