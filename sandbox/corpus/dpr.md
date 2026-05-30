# Dense Passage Retrieval for Open-Domain Question Answering (DPR) (2020)

## Problem
Open-domain question answering long relied on sparse keyword retrieval (TF-IDF, BM25),
which matches on exact terms and misses passages that answer a question using different
words. Lexical mismatch capped retrieval quality.

## Method
DPR learns dense vector representations for questions and passages with two BERT-based
encoders trained so that a question embedding lands close to the embeddings of passages
that answer it. Training uses a contrastive objective with in-batch negatives, pushing
correct question-passage pairs together and incorrect ones apart. At inference, passages
are embedded offline and indexed for fast nearest-neighbor search, so retrieval becomes
a similarity lookup in vector space rather than term matching.

## Key contributions
- Learned dual-encoder dense retrieval that matches on meaning, not just shared words.
- Efficient contrastive training with in-batch negatives.
- A practical pipeline pairing dense retrieval with a reader for open-domain QA.

## Results
DPR substantially outperformed BM25 on passage retrieval and lifted end-to-end
open-domain QA accuracy, popularizing dense retrieval as the backbone for
retrieval-augmented systems and modern semantic search.
