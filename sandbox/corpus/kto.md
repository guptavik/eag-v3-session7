# KTO: Model Alignment as Prospect-Theoretic Optimization (2024)

## Problem
Preference-based alignment methods such as DPO need paired data: two responses to the
same prompt with a label saying which is better. Collecting matched pairs is expensive,
and much real feedback is unpaired — a single response simply marked good or bad.

## Method
KTO (Kahneman-Tversky Optimization) draws on prospect theory, which describes how people
weigh gains and losses asymmetrically around a reference point. Instead of pairwise
preferences, KTO trains on individual examples each labeled only as desirable or
undesirable, defining a human-aware loss that increases the utility of good outputs and
decreases that of bad ones relative to a reference point. This removes the requirement
for matched pairs.

## Key contributions
- An alignment objective that learns from unpaired binary (good/bad) feedback rather
  than preference pairs.
- A loss grounded in prospect-theoretic, asymmetric weighting of gains and losses.
- Practical robustness to imbalanced and abundant real-world feedback signals.

## Results
KTO matched or exceeded DPO across a range of model sizes while using cheaper, more
plentiful unpaired feedback, broadening the kinds of human signal that can be used to
align models.
