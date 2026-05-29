# Flamingo: a Visual Language Model for Few-Shot Learning (2022)

## Problem
Aligning vision and language usually meant task-specific fine-tuning on large labeled
datasets. A model that could handle interleaved images and text and adapt to new
multimodal tasks from just a few examples was missing.

## Method
Flamingo bridges a powerful frozen vision encoder and a frozen large language model with
trainable components. A Perceiver-style resampler converts variable numbers of visual
features into a fixed set of tokens, and gated cross-attention layers inserted into the
frozen language model let text attend to those visual tokens. Only the new bridging
parameters are trained, on large web corpora of interleaved images and text, so the
model can ingest sequences mixing pictures and words and respond in text.

## Key contributions
- An architecture connecting frozen vision and language models via a resampler and
  gated cross-attention.
- Native handling of arbitrarily interleaved image-and-text sequences.
- Strong few-shot, in-context learning on multimodal tasks without task-specific
  fine-tuning.

## Results
Flamingo set few-shot state-of-the-art results across many vision-language benchmarks
(captioning, visual question answering), sometimes beating systems fine-tuned on far
more data, and shaped later multimodal assistants that fuse pretrained vision and
language backbones.
