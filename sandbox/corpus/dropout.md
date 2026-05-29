# Dropout: A Simple Way to Prevent Neural Networks from Overfitting (2014)

## Problem
Large neural networks with many parameters overfit small training sets, and co-adapted
units learn to rely on one another in fragile ways. Combining many separately trained
networks reduces overfitting but is far too expensive at training and test time.

## Method
Dropout randomly removes units (along with their connections) from the network on each
training step, with a fixed probability. This prevents units from co-adapting because
any unit may disappear, forcing more robust, redundant features. At test time no units
are dropped; instead the weights are scaled by the keep probability, which approximates
averaging over the exponentially many thinned networks seen during training.

## Key contributions
- A cheap stochastic regularizer that approximates training and averaging a huge
  ensemble of sub-networks.
- The insight that breaking unit co-adaptation improves generalization.
- A weight-scaling rule at test time that makes the ensemble approximation practical.

## Results
Dropout reduced test error across vision, speech, and document classification
benchmarks and became one of the most widely used regularization techniques in deep
learning.
