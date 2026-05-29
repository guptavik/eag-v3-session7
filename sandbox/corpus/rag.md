# Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (RAG) (2020)

## Problem
A language model's knowledge is frozen in its weights at training time, so it cannot
easily cite sources, stay current, or be updated without retraining, and it tends to
hallucinate on knowledge-heavy questions.

## Method
RAG couples a parametric generator with a non-parametric retriever over an external
document index. Given a query, a dense retriever fetches the most relevant passages from
a corpus (such as Wikipedia); the generator then conditions on both the query and the
retrieved passages to produce its answer. The retriever and generator are trained
together end-to-end, and the model can marginalize over several retrieved documents per
output. Updating knowledge means swapping the index, not retraining the model.

## Key contributions
- An end-to-end trainable architecture combining dense retrieval with sequence
  generation.
- Grounding generation in retrieved evidence, improving factuality and enabling
  citations.
- A hot-swappable knowledge store: update the corpus without retraining the generator.

## Results
RAG set state-of-the-art results on open-domain question answering and produced more
specific, factual, and verifiable generations than comparable closed-book models,
establishing the retrieval-augmented paradigm that this agent's vector memory follows.
