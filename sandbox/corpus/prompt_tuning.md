# The Power of Scale for Parameter-Efficient Prompt Tuning (2021)

## Problem
Adapting frozen models with discrete text prompts is fiddly and limited, while full
fine-tuning is costly to store per task. The question was how simple a learnable
conditioning could be while still matching full fine-tuning.

## Method
Prompt tuning prepends a small set of trainable "soft prompt" embeddings to the input
of an otherwise frozen model, and learns only those embeddings by backpropagation. It
is a simplification of prefix-tuning: rather than injecting prefixes at every layer, it
adds tunable vectors only at the input embedding layer. Each task is represented by its
own learned soft prompt, while one frozen model is shared across all tasks.

## Key contributions
- Input-only soft prompts as an extremely compact, task-specific conditioning.
- The finding that prompt tuning closes the gap to full fine-tuning as model scale
  grows.
- "Prompt ensembling" by learning multiple soft prompts for the same task.

## Results
At large model scale, prompt tuning matched full fine-tuning on the SuperGLUE benchmark
while storing only a few thousand parameters per task, and it transferred more robustly
to out-of-domain data than fine-tuning.
