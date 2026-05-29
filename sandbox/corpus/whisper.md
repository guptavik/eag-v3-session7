# Robust Speech Recognition via Large-Scale Weak Supervision (Whisper) (2022)

## Problem
Speech recognition systems trained on limited curated data, or with unsupervised
pretraining plus dataset-specific fine-tuning, were brittle: they often needed
per-dataset adaptation and generalized poorly to new accents, domains, and noise.

## Method
Whisper trains a single encoder-decoder Transformer on a very large, diverse collection
of weakly labeled audio-transcript pairs gathered from the web — hundreds of thousands
of hours spanning many languages. Audio is converted to log-mel spectrograms for the
encoder, and the decoder predicts text. Special tokens turn one model into a multitask
system handling transcription, translation, language identification, and timestamping,
so no per-dataset fine-tuning is needed.

## Key contributions
- Large-scale weak supervision from diverse web audio instead of curated or
  fine-tuned datasets.
- A single multitask, multilingual model for transcription, translation, and language
  ID via special tokens.
- Strong zero-shot robustness across domains, accents, and noise.

## Results
Whisper approached human-level robustness on many benchmarks and generalized zero-shot
to datasets it was never tuned on, often matching or beating specialized supervised
models, and became a widely used open speech model.
