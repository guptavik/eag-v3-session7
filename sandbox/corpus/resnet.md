# Deep Residual Learning for Image Recognition (ResNet) (2015)

## Problem
Stacking more layers in a convolutional network was expected to help, but very deep
plain networks became harder to optimize and showed higher training error than
shallower ones. This degradation was not caused by overfitting but by the difficulty of
optimizing very deep mappings.

## Method
ResNet reformulates each block to learn a residual function relative to its input. A
shortcut (skip) connection adds the block's input to its output, so the layers only
need to learn the difference from the identity mapping. These identity shortcuts add no
extra parameters and make gradients flow more easily through very deep stacks, allowing
networks of 50, 101, and 152 layers to train successfully.

## Key contributions
- Residual learning with identity shortcut connections, easing optimization of very
  deep networks.
- Empirical evidence that depth, once trainable, yields large accuracy gains.
- A family of architectures (ResNet-50/101/152) that became standard vision backbones.

## Results
ResNet won the ILSVRC 2015 classification challenge and substantially reduced error on
ImageNet, and residual connections have since become a near-universal building block
across deep architectures, including Transformers.
