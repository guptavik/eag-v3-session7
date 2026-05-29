# ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction (2020)

## Problem
Single-vector dense retrievers compress a whole passage into one embedding, losing
fine-grained term-level signal, while cross-encoders that jointly read query and passage
are accurate but far too slow to run over millions of documents at query time.

## Method
ColBERT introduces "late interaction." Query and passage are each encoded into a bag of
per-token contextual embeddings independently and offline for passages. At query time,
relevance is scored by summing, for each query token, its maximum similarity to any
passage token (a MaxSim operation). Because passage embeddings are precomputed and the
interaction is cheap, ColBERT keeps much of a cross-encoder's fine-grained matching
while remaining fast enough for large-scale search, and it supports vector-index
pruning to find candidates.

## Key contributions
- Late interaction with per-token embeddings and MaxSim scoring, balancing accuracy and
  speed.
- Offline passage encoding so expensive matching is deferred to a cheap query-time step.
- Index-based candidate generation for scalable retrieval.

## Results
ColBERT matched the accuracy of much slower cross-encoder rerankers while retrieving
orders of magnitude faster, and its late-interaction design influenced many later
high-recall, high-efficiency retrieval systems.
