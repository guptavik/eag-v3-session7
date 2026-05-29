# Show Your Work: Scratchpads for Intermediate Computation with Language Models (2021)

## Problem
Language models asked to produce an answer in a single step fail at multi-step
computations such as long arithmetic or executing code, because the entire calculation
must happen implicitly with no place to store intermediate results.

## Method
The scratchpad approach trains or prompts the model to emit its intermediate work into
a buffer before the final answer. Rather than jumping straight to the result, the model
writes out each step — partial sums, intermediate program states, line-by-line
execution — into the generated text, and then reads its own earlier steps as context
for later ones. The scratchpad effectively gives the model external working memory
realized in the token stream.

## Key contributions
- Showed that letting a model write intermediate steps before answering dramatically
  improves multi-step computation.
- Framed the generated text itself as a working-memory buffer the model can reuse.
- Provided an early, general template for step-by-step computation later echoed by
  chain-of-thought prompting.

## Results
Scratchpads sharply improved accuracy on long addition, polynomial evaluation, and
program-execution tasks where direct prediction failed, demonstrating the value of
externalizing intermediate reasoning before producing an answer.
