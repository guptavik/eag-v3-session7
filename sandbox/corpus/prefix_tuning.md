# Prefix-Tuning: Optimizing Continuous Prompts for Generation (2021)

## Problem
Fine-tuning a full language model for each generation task is storage-heavy, and
discrete prompt engineering is brittle and hard to optimize. A lightweight, learnable
way to steer a frozen model toward a task was wanted.

## Method
Prefix-tuning prepends a short sequence of continuous, trainable vectors — a "prefix" —
to the keys and values at every Transformer layer, while the model's own weights stay
frozen. These prefix vectors are free parameters optimized by gradient descent; they
are not real tokens but act like virtual context that conditions the model's attention.
Only the prefix is stored per task, so adapting to a new task costs a tiny fraction of
the full model size.

## Key contributions
- Continuous, layer-wise trainable prefixes that condition a frozen model without
  changing its weights.
- Task adaptation that stores only the small prefix rather than a full model copy.
- Competitive generation quality, especially in low-data settings.

## Results
On table-to-text and summarization, prefix-tuning matched or approached full
fine-tuning while training roughly 0.1% of the parameters, and it worked particularly
well when training data was limited, influencing later prompt- and adapter-based methods.
