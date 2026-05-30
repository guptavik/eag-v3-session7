# Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer (2017)

## Problem
Model capacity tends to scale with parameter count, but making every parameter active
for every input multiplies compute proportionally. The goal was to grow capacity by
orders of magnitude without a matching increase in per-example computation.

## Method
A sparsely-gated mixture-of-experts layer contains many expert sub-networks and a
trainable gating network that, for each input, selects only a small number of experts
to run (top-k routing). Because only a few experts activate per token, the parameter
count can be enormous while the compute per token stays modest — conditional
computation. An auxiliary load-balancing loss discourages the gate from collapsing onto
a few experts, keeping utilization spread across the pool.

## Key contributions
- A sparsely-gated MoE layer enabling conditional computation: huge capacity, low
  per-token compute.
- Top-k expert routing with a learned gating network.
- Load-balancing techniques to keep experts evenly used.

## Results
MoE models reached thousands of experts and billions of parameters with large quality
gains on language modeling and translation at manageable compute, laying the groundwork
for later sparse architectures such as Switch Transformers.
