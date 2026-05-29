# Adam: A Method for Stochastic Optimization (2014)

## Problem
Plain stochastic gradient descent uses one global learning rate and can struggle with
sparse gradients, noisy objectives, and parameters that need very different step sizes.
Earlier adaptive methods addressed parts of this but were sensitive to settings or
accumulated history in ways that stalled progress.

## Method
Adam maintains exponential moving averages of both the gradient (first moment) and the
squared gradient (second moment) for each parameter. It applies bias corrections to
these estimates, then scales each parameter's step by the first moment divided by the
square root of the second moment. This gives per-parameter adaptive learning rates that
combine the benefits of momentum and RMSProp, with little tuning required.

## Key contributions
- A per-parameter adaptive optimizer combining first- and second-moment estimates.
- Bias-correction terms that make early-training estimates reliable.
- Robust default hyperparameters that work across a wide range of problems.

## Results
Adam converged quickly and reliably across many deep-learning tasks with minimal
tuning, and it became the default optimizer for training most neural networks,
including large language models (often in its weight-decay variant, AdamW).
