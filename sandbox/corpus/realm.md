# REALM: Retrieval-Augmented Language Model Pre-Training (2020)

## Problem
Language models store world knowledge implicitly in their parameters, which is opaque,
hard to update, and grows costly as more facts must be memorized. Making knowledge
explicit and retrievable during pretraining was the aim.

## Method
REALM augments masked-language-model pretraining with a learned neural retriever over a
large textual knowledge corpus. To predict masked tokens, the model first retrieves
relevant documents and conditions on them, so the retriever is trained by the signal of
whether retrieved text helps fill the masks. Because back-propagating through retrieval
over millions of documents is expensive, REALM periodically re-embeds and re-indexes the
corpus asynchronously and uses maximum-inner-product search to fetch candidates.

## Key contributions
- The first approach to train a knowledge retriever jointly with language-model
  pretraining, end-to-end.
- Asynchronous index refresh plus MIPS to make latent retrieval over a huge corpus
  tractable.
- Explicit, updatable knowledge access instead of purely parametric memorization.

## Results
REALM improved open-domain question answering over much larger closed-book models while
using fewer parameters, and it showed that learning to retrieve during pretraining
yields more interpretable and updatable knowledge access.
