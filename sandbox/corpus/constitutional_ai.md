# Constitutional AI: Harmlessness from AI Feedback (2022)

## Problem
Making models harmless usually depends on large amounts of human-labeled data flagging
harmful outputs. That labeling is costly, exposes humans to disturbing content, and is
hard to scale or audit as a transparent statement of values.

## Method
Constitutional AI reduces reliance on human harm labels by guiding the model with a
written set of principles (a "constitution"). In a supervised phase the model critiques
and revises its own responses against the principles. In a reinforcement-learning phase
("RL from AI Feedback"), the model generates preference comparisons by judging which of
two responses better follows the constitution, and a reward model trained on these
AI-generated preferences is optimized against — replacing human harm labels with AI
feedback grounded in explicit rules.

## Key contributions
- Self-critique and revision guided by an explicit written set of principles.
- RL from AI Feedback (RLAIF), generating preference labels for harmlessness without
  human harm annotation.
- More transparent, steerable control over model behavior via a stated constitution.

## Results
Constitutional AI produced models that were both helpful and markedly more harmless,
with less reliance on human-labeled harmful examples, and it offered a more scalable and
auditable route to alignment than purely human-feedback approaches.
