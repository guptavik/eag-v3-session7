# Long Short-Term Memory (1997)

## Problem
Recurrent networks trained by backpropagation through time struggled to learn
dependencies across long gaps because error signals tend to vanish or explode as they
propagate backward through many time steps. This made it hard to assign reward or error
to events many steps earlier in a sequence.

## Method
LSTM introduces a memory cell whose state is protected by multiplicative gates. The
cell maintains a nearly constant error flow through a self-connected linear unit, while
input and output gates learn when to write information into the cell and when to expose
it. Later work added a forget gate that lets the cell reset its contents. The gating
structure keeps gradients stable over long intervals.

## Key contributions
- A gated memory-cell architecture that preserves error signals over long time lags.
- A solution to the vanishing- and exploding-gradient problem in recurrent learning.
- A building block that enabled practical learning of long-range temporal structure.

## Results
LSTMs solved synthetic long-lag tasks that plain recurrent networks could not, and for
nearly two decades became the dominant model for speech, handwriting, and language
sequence modeling before attention-based architectures.
