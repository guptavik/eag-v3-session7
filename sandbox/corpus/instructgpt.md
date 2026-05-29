# Training Language Models to Follow Instructions with Human Feedback (InstructGPT) (2022)

## Problem
Large language models trained only to predict the next token often produce outputs that
are untruthful, unhelpful, or not aligned with what a user actually asked. Bigger models
are not automatically better at following intent.

## Method
InstructGPT applies reinforcement learning from human feedback in three stages. First,
human-written demonstrations are used to supervise fine-tune the base model. Second,
labelers rank multiple model outputs for the same prompt, and a reward model is trained
to predict these human preferences. Third, the policy is optimized against the reward
model using Proximal Policy Optimization, with a penalty that keeps it close to the
supervised model so it does not drift or game the reward.

## Key contributions
- A concrete three-stage RLHF recipe: supervised fine-tuning, reward modeling, then
  policy optimization.
- Evidence that preference-aligned smaller models can be preferred over much larger
  unaligned ones.
- A template that shaped subsequent instruction-following assistants.

## Results
Human raters preferred InstructGPT outputs over those of the much larger base GPT-3,
and the aligned models were more truthful and produced less toxic text, establishing
RLHF as the standard alignment approach for instruction-following models.
