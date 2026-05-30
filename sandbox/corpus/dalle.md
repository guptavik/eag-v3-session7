# Zero-Shot Text-to-Image Generation (DALL-E) (2021)

## Problem
Generating images from arbitrary text descriptions had been limited to narrow domains
and required specialized, dataset-specific models. A single model that could generate
plausible images for open-ended prompts was lacking.

## Method
DALL-E treats text-to-image generation as autoregressive sequence modeling over a single
stream of tokens. A discrete variational autoencoder first compresses images into a grid
of discrete image tokens drawn from a learned codebook. A large Transformer is then
trained to model the concatenated sequence of text tokens followed by image tokens, so
at generation time it continues from a text prompt to produce image tokens, which the
decoder turns back into pixels. Samples can be ranked by a CLIP-style model to pick the
best.

## Key contributions
- A unified autoregressive Transformer over text and discrete image tokens for
  open-ended generation.
- A discrete VAE tokenizer that makes images tractable as sequences.
- Demonstrated zero-shot generation, composition of concepts, and attribute binding
  from free-form prompts.

## Results
DALL-E produced coherent, often imaginative images for a wide variety of novel prompts,
including unusual concept combinations, and helped launch the modern text-to-image
generation field later advanced by diffusion models.
