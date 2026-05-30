# Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift (2015)

## Problem
As a deep network trains, the distribution of each layer's inputs shifts because the
parameters of preceding layers keep changing. This internal covariate shift forces
small learning rates and careful initialization, slowing training and making very deep
networks hard to optimize.

## Method
Batch normalization normalizes each layer's pre-activations using the mean and variance
computed over the current mini-batch, then applies a learned scale and shift so the
layer can recover any needed representation. The normalization is part of the
computation graph, so its statistics are accounted for during backpropagation. At
inference, running averages of the statistics are used instead of batch statistics.

## Key contributions
- A normalization layer that stabilizes the distribution of layer inputs during
  training.
- Enabled much higher learning rates and reduced sensitivity to initialization.
- A mild regularizing effect from the noise of batch statistics.

## Results
Batch normalization let deep image classifiers train several times faster and reach
higher accuracy, and it became a standard component of convolutional architectures,
inspiring related schemes such as layer and group normalization.
