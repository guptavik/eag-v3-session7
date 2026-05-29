# Learning to Summarize from Human Feedback (2020)

## Problem
Summarization models trained to imitate reference summaries and scored with metrics
like ROUGE optimize a proxy that correlates poorly with what people actually judge to
be a good summary. Maximizing the proxy does not maximize human-judged quality.

## Method
The work collects large numbers of human comparisons between pairs of candidate
summaries and trains a reward model to predict which summary people prefer. A
summarization policy is then fine-tuned with reinforcement learning (PPO) to maximize
this learned reward, with a penalty keeping it near the supervised model. Careful
collection of high-quality human preference data is emphasized as central to making the
reward model reliable.

## Key contributions
- Demonstrated that optimizing a learned human-preference reward beats optimizing
  likelihood or ROUGE for summary quality.
- An early, careful application of the reward-model-plus-RL pipeline to a real
  generation task.
- Evidence that preference-trained models generalize to new domains.

## Results
Human raters strongly preferred the feedback-optimized summaries over supervised
baselines and even over human reference summaries in some settings, and the recipe
directly informed later instruction-tuning work like InstructGPT.
