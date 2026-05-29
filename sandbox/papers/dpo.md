# Direct Preference Optimization: Your Language Model is Secretly a Reward Model (2023)

## Problem
Aligning language models to human preferences was usually done with reinforcement
learning from human feedback (RLHF): first fit a separate reward model to preference
data, then optimize the policy against it with an RL algorithm such as PPO. That
pipeline is complex, unstable, and sensitive to many hyperparameters, and it requires
sampling from the model during training.

## Method
Direct Preference Optimization removes the explicit reward model and the RL loop. It
shows that the RLHF objective has a closed-form relationship between the optimal policy
and the reference policy, which lets preference learning be rewritten as a simple
classification loss over pairs of preferred and dispreferred responses. The model is
trained directly on this loss to raise the relative likelihood of preferred responses,
with a term that keeps it close to the reference model.

## Key contributions
- Reframed RLHF as a single supervised-style classification objective on preference
  pairs, eliminating the separate reward model.
- Removed the need for online sampling and unstable RL optimization during alignment.
- Provided the theoretical link showing the language model itself implicitly defines
  the reward.

## Results
DPO matched or exceeded PPO-based RLHF on sentiment control, summarization, and
single-turn dialogue while being markedly simpler and more stable to train, and it has
become a widely used alignment recipe.
