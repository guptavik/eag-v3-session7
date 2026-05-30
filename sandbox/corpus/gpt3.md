# Language Models are Few-Shot Learners (GPT-3) (2020)

## Problem
Even after large-scale pretraining, adapting a model to a new task usually required
fine-tuning on thousands of labeled examples. Collecting task-specific datasets for
every application is costly and unlike how people pick up a task from a few
demonstrations.

## Method
GPT-3 is a 175-billion-parameter autoregressive Transformer trained on a very large and
diverse text corpus. The paper studies in-context learning: instead of updating
weights, the task is described in the prompt with zero, one, or a few examples, and the
model infers the pattern and continues accordingly. No gradient updates are made at
inference time.

## Key contributions
- Demonstrated strong zero-shot, one-shot, and few-shot performance from prompting
  alone, without task-specific fine-tuning.
- Showed that in-context learning ability grows smoothly and substantially with model
  scale.
- Provided extensive evidence across dozens of language tasks that scale unlocks new
  capabilities.

## Results
With only a few in-context examples, GPT-3 reached competitive performance on many
benchmarks, sometimes approaching fine-tuned systems, and reframed scale plus prompting
as an alternative to per-task fine-tuning.
