# Learning Transferable Visual Models From Natural Language Supervision (CLIP) (2021)

## Problem
Vision models were trained to predict a fixed set of labeled categories, which is
costly to annotate and limits a model to those predefined classes. Recognizing new
concepts required new labeled data and retraining.

## Method
CLIP learns from a very large set of image-text pairs scraped from the web. An image
encoder and a text encoder are trained jointly with a contrastive objective: for a
batch of pairs, the model learns to match each image with its correct caption and push
away mismatched ones, aligning both into a shared embedding space. At test time,
classification is done zero-shot by embedding candidate label descriptions as text and
picking the one whose embedding is closest to the image.

## Key contributions
- Contrastive image-text pretraining at web scale that aligns vision and language in
  one embedding space.
- Zero-shot transfer to new visual tasks by writing label names as text prompts.
- Strong robustness to distribution shift compared with supervised classifiers.

## Results
CLIP matched a fully supervised ResNet-50 on ImageNet zero-shot, without using any of
its labeled training images, and transferred across dozens of datasets — becoming a
foundation for text-to-image generation, retrieval, and multimodal models.
