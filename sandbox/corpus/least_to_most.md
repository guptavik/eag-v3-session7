# Least-to-Most Prompting Enables Complex Reasoning in Large Language Models (2022)

## Problem
Chain-of-thought prompting often fails to generalize from easy demonstration problems
to harder test problems that require more steps than the examples showed. Models
struggle to compose solutions for problems harder than anything in the prompt.

## Method
Least-to-most prompting works in two stages. First the model decomposes a complex
problem into a sequence of simpler subproblems ordered from least to most difficult.
Then it solves the subproblems in order, feeding the answer of each solved subproblem
into the prompt for the next, so later steps build explicitly on earlier results. This
staged decomposition lets the model reach solutions that need more reasoning steps than
any single exemplar.

## Key contributions
- A decompose-then-solve prompting strategy that separates planning from execution.
- Explicit reuse of earlier subproblem answers as context for later ones.
- Strong easy-to-hard generalization, solving problems harder than the demonstrations.

## Results
Least-to-most prompting substantially outperformed standard chain-of-thought on
compositional generalization benchmarks such as SCAN and on symbolic manipulation and
math word problems that demand many sequential steps.
