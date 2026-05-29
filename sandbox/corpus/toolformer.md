# Toolformer: Language Models Can Teach Themselves to Use Tools (2023)

## Problem
Language models are weak at tasks that external tools handle well — exact arithmetic,
up-to-date facts, translation — yet teaching tool use usually needs large amounts of
human annotation specifying when and how to call each tool.

## Method
Toolformer learns tool use in a self-supervised way. Starting from a few examples, the
model samples candidate API calls (calculator, search engine, calendar, translation,
question answering) at many positions in ordinary text. It then keeps only the calls
whose returned results actually reduce the model's loss on predicting the following
tokens — that is, calls that demonstrably help. The model is then fine-tuned on this
filtered, self-generated dataset, learning where calling a tool pays off.

## Key contributions
- A self-supervised method to decide when and how to call external tools, with minimal
  human supervision.
- A usefulness filter that keeps only API calls that improve next-token prediction.
- Retention of general language ability while adding tool-use skills.

## Results
Toolformer improved zero-shot performance on math, factual QA, and other tasks,
sometimes letting a smaller model match much larger ones, without sacrificing its core
language modeling capabilities.
