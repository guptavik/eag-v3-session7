# Layer Normalization (2016)

## Problem
Batch normalization depends on mini-batch statistics, which makes it awkward for
recurrent networks, where the natural unit is a single time step, and unreliable when
the batch is very small or the sequence length varies. A normalization that does not
depend on the batch was needed.

## Method
Layer normalization computes the normalization statistics — mean and variance — across
all the units within a single layer for one training example, rather than across the
batch. Each example is normalized independently using its own feature statistics, then
a learned gain and bias are applied. Because it is independent of other examples, the
same computation is used at training and test time and applies naturally to recurrent
and sequence models.

## Key contributions
- A batch-independent normalization computed over a layer's features per example.
- Consistent behavior between training and inference, with no running statistics.
- A normalization well suited to recurrent networks and, later, Transformers.

## Results
Layer normalization stabilized and sped up training of recurrent models, and it became
the default normalization inside Transformer architectures, where it is applied around
the attention and feed-forward sublayers.
