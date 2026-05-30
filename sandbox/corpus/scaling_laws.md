# Scaling Laws for Neural Language Models (2020)

## Problem
Practitioners had little principled guidance on how model size, dataset size, and
training compute trade off, so decisions about how big a model to train and on how much
data were largely guesswork.

## Method
The study trains many Transformer language models across wide ranges of parameter
count, dataset size, and compute budget, and measures how test loss varies. It fits the
results to simple functional forms and finds that loss falls as a smooth power law in
each of the three quantities when the others are not bottlenecking. From these fits the
authors derive how, for a fixed compute budget, model size and data should be scaled,
concluding that very large models are relatively sample-efficient.

## Key contributions
- Empirical power-law relationships between loss and model size, data, and compute.
- Predictable extrapolation of performance, enabling planning of large training runs.
- Compute-allocation guidance for trading off model size against dataset size.

## Results
The power laws held across several orders of magnitude and made large-model
performance forecastable, directly motivating the race to scale; later work (Chinchilla)
revised the precise size-versus-data trade-off the original analysis suggested.
