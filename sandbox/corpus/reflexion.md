# Reflexion: Language Agents with Verbal Reinforcement Learning (2023)

## Problem
Language-model agents that act in an environment usually cannot improve within a task:
when a trajectory fails, updating the model's weights from sparse success/failure
signals is slow and expensive, and the agent repeats the same mistakes.

## Method
Reflexion lets an agent learn from its own failures without changing any weights. After
an attempt, the agent receives a reward signal, then generates a written
self-reflection diagnosing what went wrong and how to do better. This verbal feedback
is stored in an episodic memory and prepended to the prompt on the next attempt, so the
agent reasons about earlier failures before acting again. Improvement is carried
entirely in natural-language memory rather than in gradients.

## Key contributions
- "Verbal reinforcement learning": converting outcome signals into written
  self-critiques that guide later attempts.
- An episodic memory of reflections that lets the agent revise its strategy across
  trials without fine-tuning.
- A general wrapper that improves reasoning, coding, and decision-making agents.

## Results
Reflexion substantially improved success rates on decision-making (ALFWorld),
reasoning (HotpotQA), and coding (HumanEval) tasks across repeated trials, showing that
reflecting on earlier errors before the next attempt is a strong, cheap form of
learning.
