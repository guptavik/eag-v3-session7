# FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness (2022)

## Problem
Standard attention materializes the full N-by-N attention matrix in memory, so time and
memory grow quadratically with sequence length. The real bottleneck is not arithmetic
but the reads and writes of that large matrix to and from slow high-bandwidth memory.

## Method
FlashAttention is an IO-aware exact attention algorithm. It tiles the computation into
blocks that fit in fast on-chip SRAM and fuses the steps so the full attention matrix is
never written to main memory. Using online softmax, it computes the result block by
block in a single pass and recomputes intermediate values during the backward pass
rather than storing them. The output is mathematically identical to standard attention,
just computed with far fewer memory transfers.

## Key contributions
- An IO-aware, tiled, fused attention kernel that avoids materializing the attention
  matrix.
- Online softmax plus recomputation to keep memory roughly linear in sequence length.
- Exact (not approximate) attention with large wall-clock and memory savings.

## Results
FlashAttention sped up Transformer training and inference several-fold and enabled much
longer context windows by reducing attention's memory from quadratic to near-linear,
becoming a standard kernel in modern model training stacks.
