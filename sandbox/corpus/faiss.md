# Billion-Scale Similarity Search with GPUs (FAISS) (2017)

## Problem
Nearest-neighbor search over hundreds of millions of high-dimensional vectors is the
bottleneck in large-scale retrieval and recommendation. Exact search is too slow, and
existing approximate methods did not exploit modern parallel hardware well.

## Method
FAISS is a library for efficient similarity search and clustering of dense vectors. It
combines product quantization, which compresses vectors into compact codes that can be
compared quickly, with inverted-file indexing that restricts search to a few promising
clusters. The library provides accelerator-optimized implementations of k-selection and
distance computation, trading a controllable amount of accuracy for large gains in
speed and memory, and supports both exact (flat) and approximate indexes.

## Key contributions
- Hardware-optimized approximate nearest-neighbor search scaling to billions of
  vectors.
- Product quantization plus inverted-file indexing for compact, fast similarity search.
- A widely used open-source toolkit underpinning modern vector databases.

## Results
FAISS achieved order-of-magnitude speedups over prior methods on billion-scale
benchmarks and became the de-facto engine for vector search — including the in-process
index this very agent uses for its semantic memory.
