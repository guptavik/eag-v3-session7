# LLaMA: Open and Efficient Foundation Language Models (2023)

## Problem
The strongest large language models were closed and extremely large, and prevailing
practice equated capability with raw parameter count. There was a need for openly
available, smaller models that remained highly capable and cheap to run.

## Method
LLaMA is a family of foundation models from 7B to 65B parameters trained only on
publicly available datasets. Following compute-optimal insights, the models are trained
on far more tokens than typical for their size, prioritizing inference efficiency: a
smaller model trained longer is cheaper to serve than a larger one. The architecture
uses now-standard refinements such as pre-normalization, the SwiGLU activation, and
rotary positional embeddings.

## Key contributions
- A family of strong, relatively small foundation models trained only on public data.
- Emphasis on training longer to optimize for inference cost rather than just training
  cost.
- Broad release that catalyzed open research and a large ecosystem of fine-tuned
  derivatives.

## Results
LLaMA-13B outperformed the much larger GPT-3 on most benchmarks, and the 65B model was
competitive with the best closed models of the time, while remaining far cheaper to run
— spurring a wave of open instruction-tuned and parameter-efficient derivatives.
