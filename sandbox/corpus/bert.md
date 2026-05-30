# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (2018)

## Problem
Earlier language representation models read text in a single direction, so a word's
representation could not draw on both its left and right context at once. This one-
directional view limited how well pretrained representations transferred to tasks like
question answering that need full-sentence understanding.

## Method
BERT pretrains a deep Transformer encoder on two self-supervised objectives. Masked
language modeling hides a fraction of input tokens and trains the model to predict them
from both directions, giving genuinely bidirectional context. Next-sentence prediction
trains the model to tell whether one sentence follows another. After pretraining on
large unlabeled text, the model is fine-tuned with a small task-specific head.

## Key contributions
- Masked language modeling, enabling deep bidirectional context in a single encoder.
- A pretrain-then-fine-tune recipe that transfers to many tasks with minimal
  task-specific architecture.
- New state-of-the-art results across a broad suite of language understanding
  benchmarks.

## Results
BERT achieved state-of-the-art scores on the GLUE benchmark, SQuAD question answering,
and other tasks at release, and established masked-language-model pretraining as the
dominant approach for language understanding.
