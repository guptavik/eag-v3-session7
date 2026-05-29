# Efficient Estimation of Word Representations in Vector Space (word2vec) (2013)

## Problem
Earlier neural language models learned useful word vectors but were expensive to train,
which limited the size of the vocabulary and corpus they could handle. A cheaper way to
learn high-quality distributed word representations from very large corpora was needed.

## Method
word2vec introduces two shallow, log-linear models. The continuous bag-of-words (CBOW)
model predicts a target word from the average of its surrounding context words, while
the skip-gram model predicts the surrounding context words from a target word. By
removing the hidden non-linear layer and using efficient training tricks such as
hierarchical softmax and negative sampling, the models scale to billions of words.

## Key contributions
- Two efficient architectures (CBOW and skip-gram) for learning word embeddings at
  large scale.
- Showed the learned vectors capture syntactic and semantic regularities, including
  linear analogy relationships (king − man + woman ≈ queen).
- Training methods (negative sampling, hierarchical softmax) that made web-scale
  embedding training practical.

## Results
word2vec produced high-quality word vectors orders of magnitude faster than prior
neural approaches and popularized pretrained embeddings as a standard input
representation across natural language processing.
