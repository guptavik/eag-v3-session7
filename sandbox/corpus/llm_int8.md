# LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale (2022)

## Problem
Loading a very large language model for inference requires holding all its 16-bit
weights in accelerator memory, which is costly. Naive 8-bit quantization saves memory
but sharply degrades accuracy for the largest models, so a lossless low-precision path
was needed.

## Method
LLM.int8() performs most matrix multiplications in 8-bit integer precision to roughly
halve the memory for weights. The key insight is that a few "outlier" feature dimensions
carry disproportionate magnitude and, if quantized, wreck accuracy. The method detects
these outlier dimensions and keeps them in 16-bit while quantizing the rest to 8-bit, a
mixed-precision decomposition that preserves quality. The technique is applied so that
no retraining is required.

## Key contributions
- A mixed-precision scheme that isolates high-magnitude outlier features in 16-bit and
  quantizes the rest to 8-bit.
- Memory-halving inference for very large models with essentially no accuracy loss.
- A training-free method usable on already-trained checkpoints.

## Results
LLM.int8() ran models with up to 175 billion parameters in 8-bit with no measurable
drop in predictive performance, roughly halving inference memory and making large-model
inference feasible on more modest hardware.
