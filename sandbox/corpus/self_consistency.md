# Self-Consistency Improves Chain-of-Thought Reasoning in Language Models (2022)

## Problem
Chain-of-thought prompting decodes a single reasoning path greedily, so one wrong step
derails the whole answer. A single sampled chain is brittle and underuses the model's
ability to reach the same answer by different routes.

## Method
Self-consistency replaces greedy decoding with sampling many diverse reasoning paths
for the same question, then taking the final answer that the most paths agree on
(a majority vote over answers, marginalizing over the differing intermediate steps).
The intuition is that a correct answer can be reached through several valid lines of
thought, so agreement across independent samples is a strong signal of correctness.

## Key contributions
- A simple decoding strategy: sample multiple reasoning chains and marginalize to the
  most consistent answer.
- Showed large accuracy gains over single-path chain-of-thought with no extra training.
- Demonstrated that answer agreement across diverse reasoning paths correlates with
  correctness.

## Results
Self-consistency produced substantial improvements on arithmetic and commonsense
reasoning benchmarks such as GSM8K and SVAMP over standard chain-of-thought prompting,
becoming a standard inference-time technique for reasoning tasks.
