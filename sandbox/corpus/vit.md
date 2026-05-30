# An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (ViT) (2020)

## Problem
Convolutional networks dominated computer vision through built-in assumptions like
locality and translation equivariance. Whether the pure Transformer, so successful in
language, could match them on images without convolutional priors was an open question.

## Method
The Vision Transformer splits an image into fixed-size patches, flattens and linearly
embeds each patch as if it were a token, adds positional embeddings, and feeds the
sequence to a standard Transformer encoder. A special classification token aggregates
information for the final prediction. With little vision-specific inductive bias, ViT
relies on large-scale pretraining to learn the structure that convolutions otherwise
build in.

## Key contributions
- Showed a standard Transformer applied to image patches can match or beat
  convolutional networks.
- Demonstrated that sufficient pretraining data compensates for the missing
  convolutional inductive biases.
- Unified the architecture across language and vision around the Transformer.

## Results
When pretrained on very large image datasets, ViT matched or exceeded strong
convolutional baselines on ImageNet and other benchmarks at lower pretraining compute,
and it became the backbone for much of modern vision and multimodal modeling.
