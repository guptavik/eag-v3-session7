# Leveraging Passage Retrieval with Generative Models for Open Domain QA (Fusion-in-Decoder) (2020)

## Problem
Retrieval-augmented generators that concatenate many retrieved passages into one input
hit the Transformer's quadratic attention cost and a context-length wall, limiting how
much evidence the model can actually use to answer a question.

## Method
Fusion-in-Decoder (FiD) encodes each retrieved passage independently with the encoder,
so cost grows linearly in the number of passages rather than quadratically with their
combined length. The decoder then attends jointly over the concatenation of all the
encoded passage representations, "fusing" evidence from many passages when generating
the answer. This separation lets the model condition on a large set of passages while
keeping computation manageable.

## Key contributions
- Encode passages separately, then fuse them only in the decoder's attention.
- Linear scaling in the number of retrieved passages, enabling many more evidence
  sources.
- A simple generative reader that strongly exploits retrieval.

## Results
FiD set state-of-the-art results on open-domain QA benchmarks such as Natural Questions
and TriviaQA, and showed that answer quality keeps improving as more retrieved passages
are fused, making it a standard reader design for retrieval-augmented QA.
