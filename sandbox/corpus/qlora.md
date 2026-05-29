# QLoRA: Efficient Finetuning of Quantized LLMs (2023)

## Problem
Fine-tuning very large language models normally demands enormous amounts of accelerator
memory to hold the weights, gradients, and optimizer state, putting it out of reach for
anyone without a large cluster. Reducing that memory cost without hurting quality was
the goal.

## Method
QLoRA freezes the base model in a new 4-bit quantized format (NormalFloat4) and trains
only small low-rank adapter matrices on top, so gradients flow only through the tiny
adapters while the bulk of the weights stay quantized in memory. Two further tricks —
double quantization, which compresses the quantization constants, and paged optimizers,
which offload optimizer state to host memory during spikes — cut peak memory further.
The combination lets a multi-billion-parameter model be tuned on a single commodity
graphics card with limited memory.

## Key contributions
- 4-bit NormalFloat quantization of the frozen base weights with low-rank adapters
  trained on top.
- Double quantization and paged optimizers to slash peak memory use.
- Showed massive models can be tuned on modest, widely available hardware.

## Results
QLoRA fine-tuned models with billions of parameters on a single consumer-grade card
while retaining the quality of 16-bit full fine-tuning, making customization of large
models broadly accessible.
