# Tree of Thoughts: Deliberate Problem Solving with Large Language Models (2023)

## Problem
Chain-of-thought and self-consistency commit to left-to-right reasoning and cannot
backtrack or explore alternatives. For problems that need search, planning, or
lookahead, a single forward pass of reasoning is too rigid.

## Method
Tree of Thoughts frames reasoning as search over a tree whose nodes are partial
solutions ("thoughts"). The model proposes several candidate next thoughts at each
step, evaluates how promising each partial state is (the model itself acts as a value
estimator), and uses search strategies such as breadth-first or depth-first with
backtracking to explore and prune branches. This lets the system consider multiple
paths and abandon dead ends before committing.

## Key contributions
- A general framework that turns reasoning into deliberate search over a tree of
  intermediate thoughts.
- Self-evaluation of partial states to guide exploration and pruning.
- Support for lookahead and backtracking that linear reasoning lacks.

## Results
Tree of Thoughts dramatically outperformed chain-of-thought on tasks requiring search
and planning, such as the Game of 24, creative writing with constraints, and mini
crosswords, where exploring and revising intermediate steps is essential.
