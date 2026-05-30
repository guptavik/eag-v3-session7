# PaLM: Scaling Language Modeling with Pathways (2022)

## Problem
It was unclear how far few-shot performance would keep improving with scale, and
training a single dense model with hundreds of billions of parameters efficiently
across thousands of accelerators posed a major systems challenge.

## Method
PaLM is a 540-billion-parameter dense Transformer trained with the Pathways system,
which orchestrates efficient data and model parallelism across tens of thousands of
accelerator chips in two pods. The model uses standard but carefully chosen
architectural details and a large, high-quality multilingual and code dataset. The work
studies how capabilities scale and analyzes breakthrough behaviors that appear only at
the largest size.

## Key contributions
- Demonstrated efficient training of a 540B dense model via the Pathways
  infrastructure.
- Showed continued and sometimes discontinuous ("emergent") gains on reasoning tasks
  with scale.
- Evidence that chain-of-thought prompting plus scale unlocks strong multi-step
  reasoning.

## Results
PaLM achieved state-of-the-art few-shot results on many language and reasoning
benchmarks, in several cases surpassing fine-tuned prior systems and even average human
performance on a hard reasoning suite, underscoring the returns from scale combined with
better prompting.
