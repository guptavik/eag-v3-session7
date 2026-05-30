# Attention Is All You Need (2017)

## Problem
Recurrent and convolutional sequence models process tokens largely in order, which
limits parallelism during training and makes it hard to learn dependencies between
distant positions. Long training times and weak long-range modeling were the core
limitations the paper set out to remove.

## Method
The Transformer replaces recurrence entirely with self-attention. Each position
attends to every other position through scaled dot-product attention, computed in
parallel across the whole sequence. Multiple attention heads let the model attend to
different relationships at once, and because attention is order-agnostic, sinusoidal
positional encodings inject token order. The architecture stacks attention and
position-wise feed-forward sublayers with residual connections and layer
normalization, in an encoder-decoder arrangement.

## Key contributions
- Self-attention as the sole sequence-mixing mechanism, removing recurrence and
  enabling full parallelism over the sequence.
- Multi-head attention, letting the model jointly attend to information from
  different representation subspaces.
- Positional encoding to represent token order without sequential computation.

## Results
The Transformer set new state-of-the-art BLEU scores on English-German and
English-French machine translation while training substantially faster than the best
recurrent and convolutional baselines. It became the architectural foundation for
nearly all subsequent large language models.
