# Parameter-Efficient Transfer Learning for NLP (Adapters) (2019)

## Problem
Fine-tuning a full pretrained Transformer for every downstream task stores a complete
copy of the model per task, which scales badly when many tasks must be served. A way to
adapt to new tasks while sharing almost all parameters was needed.

## Method
Adapter tuning inserts small bottleneck modules between the existing layers of a frozen
pretrained Transformer. Each adapter projects the hidden representation down to a small
dimension, applies a non-linearity, and projects back up, with a residual connection so
it starts near the identity. Only the adapters and layer-norm parameters are trained;
the original weights stay fixed and shared across tasks. Adding a new task means adding
a few new adapter parameters rather than a whole model.

## Key contributions
- Compact bottleneck adapter modules that make most parameters shareable across tasks.
- Near-identity initialization so adapters can be added without destabilizing the base
  model.
- Strong task performance while training only a few percent of the parameters per task.

## Results
On a suite of text classification tasks, adapters came within a fraction of a point of
full fine-tuning while adding only a few percent of new parameters per task, pioneering
the parameter-efficient tuning family that LoRA and prompt tuning later extended.
