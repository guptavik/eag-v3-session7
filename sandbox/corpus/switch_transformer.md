# Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity (2021)

## Problem
Mixture-of-experts layers add capacity cheaply but are complex: top-k routing, tricky
load balancing, communication overhead, and training instability made very large sparse
models hard to use in practice.

## Method
The Switch Transformer simplifies mixture-of-experts by routing each token to exactly
one expert (top-1) instead of several. This "switch" routing cuts routing computation
and communication, and the paper adds a load-balancing loss, careful initialization, and
selective use of lower precision to stabilize training. Replacing the dense
feed-forward sublayer with a sparse switch layer lets total parameters grow into the
trillions while compute per token stays close to a dense model of normal size.

## Key contributions
- Top-1 expert routing that simplifies and speeds up sparse models.
- Stability techniques (balancing loss, precision and initialization choices) for very
  large sparse training.
- Demonstrated scaling to trillion-parameter models with fixed per-token compute.

## Results
Switch Transformers trained several times faster than dense baselines to reach the same
quality and scaled to trillions of parameters, showing that simple top-1 sparsity is an
efficient route to extreme model capacity.
