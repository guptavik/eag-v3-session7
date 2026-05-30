# Distilling the Knowledge in a Neural Network (2015)

## Problem
The most accurate models are often large ensembles or very big networks that are slow
and memory-hungry to deploy. The knowledge they contain needs to be transferred into a
smaller, cheaper model without losing much accuracy.

## Method
Knowledge distillation trains a compact "student" network to mimic the outputs of a
large "teacher". Instead of learning only from hard labels, the student is trained on
the teacher's full softened probability distribution, produced by raising the softmax
temperature. These soft targets carry "dark knowledge" — the relative probabilities the
teacher assigns to wrong classes — which conveys how the teacher generalizes and gives
the student a much richer training signal than one-hot labels.

## Key contributions
- Training small students on softened teacher probabilities to transfer generalization
  behavior.
- The temperature-scaling technique that exposes the teacher's "dark knowledge".
- A practical route from expensive ensembles to a single deployable model.

## Results
Distilled students recovered much of a large teacher or ensemble's accuracy at a
fraction of the size and inference cost, and distillation became a core technique for
model compression, including shrinking large language models.
