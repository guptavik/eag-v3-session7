# LoRA: Low-Rank Adaptation of Large Language Models (2021)

## Problem
Full fine-tuning of a large pretrained model updates every weight and produces a fresh
full-size copy of the model for each downstream task. That is expensive in memory and
storage and becomes impractical when serving many task-specific variants of a very
large model.

## Method
LoRA freezes the pretrained weights and injects a pair of small trainable low-rank
matrices into each targeted layer; only those low-rank updates are learned. Because the
update is constrained to a low-rank decomposition, the number of trainable parameters
drops by several orders of magnitude. At inference the learned low-rank matrices can be
merged back into the original weights, so there is no added latency, and a single
frozen base model can host many swappable task adapters.

## Key contributions
- Reduced the count of trainable parameters by thousands of times while keeping
  quality close to full fine-tuning.
- Showed the merged adapter adds no inference latency, unlike adapter layers.
- Made it practical to maintain many task-specific variants from one frozen base model
  on modest hardware.

## Results
On GPT-3-scale models LoRA matched full fine-tuning quality on several benchmarks while
training a tiny fraction of the parameters and shrinking the per-task checkpoint from
gigabytes to megabytes. It is now a standard parameter-efficient tuning method.
