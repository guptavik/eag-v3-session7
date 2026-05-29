# Training Compute-Optimal Large Language Models (Chinchilla) (2022)

## Problem
Earlier scaling guidance led labs to grow model size aggressively while keeping
training data roughly fixed. The open question was, for a fixed compute budget, what
combination of model size and training tokens actually minimizes loss.

## Method
The authors train more than 400 models across many sizes and token counts and fit the
relationship between compute, parameters, and data. They find that most large models of
the era were significantly undertrained: parameters and training tokens should be scaled
in roughly equal proportion as compute grows. To test the prediction they train
Chinchilla, a 70-billion-parameter model, on far more tokens than a similarly-budgeted
larger model used.

## Key contributions
- The compute-optimal scaling rule: grow model size and training data together, roughly
  one-to-one.
- Empirical evidence that prior flagship models were undertrained on too little data.
- A concrete, better-balanced training recipe validated by the Chinchilla model.

## Results
Chinchilla outperformed much larger models such as Gopher and GPT-3 on a broad range of
benchmarks despite having fewer parameters, reshaping how the field allocates compute
between model size and data.
