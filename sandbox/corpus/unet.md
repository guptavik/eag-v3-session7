# U-Net: Convolutional Networks for Biomedical Image Segmentation (2015)

## Problem
Biomedical segmentation needs a label for every pixel, yet annotated medical images are
scarce. Classification-style convolutional networks lose spatial detail through
pooling, making precise, localized segmentation from few examples difficult.

## Method
U-Net uses a symmetric encoder-decoder shape. A contracting path of convolutions and
pooling captures context while downsampling; an expanding path upsamples back to full
resolution. Crucially, skip connections copy high-resolution feature maps from the
encoder directly to the matching decoder level, so fine spatial detail lost during
downsampling is restored. Heavy data augmentation, especially elastic deformations,
lets the network learn from very few annotated images.

## Key contributions
- A U-shaped encoder-decoder with skip connections that fuse context and precise
  localization.
- A training recipe that achieves strong segmentation from very small annotated
  datasets via augmentation.
- An architecture that generalizes well beyond biomedical imaging.

## Results
U-Net won biomedical segmentation challenges with limited training data and became a
default architecture for dense prediction tasks, later underpinning the denoising
networks used in diffusion image models.
