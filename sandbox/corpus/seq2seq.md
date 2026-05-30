# Sequence to Sequence Learning with Neural Networks (2014)

## Problem
Standard deep networks needed fixed-size inputs and outputs, but many language tasks
map a variable-length input sequence to a variable-length output sequence (for example,
translating a sentence). A general neural approach to sequence-to-sequence mapping was
missing.

## Method
The model uses two recurrent networks. An encoder LSTM reads the input sequence and
compresses it into a fixed-length context vector; a decoder LSTM then generates the
output sequence one token at a time, conditioned on that vector and its own previous
outputs. A practical trick — reversing the order of the input tokens — shortened the
effective distance between related source and target words and improved learning.

## Key contributions
- A general encoder-decoder framework for mapping one sequence to another with neural
  networks.
- Demonstrated that deep LSTMs can handle long sentences and learn sensible
  representations of phrases.
- The input-reversal trick that markedly improved translation quality.

## Results
On English-to-French translation the system reached strong BLEU scores, competitive
with phrase-based statistical machine translation of the time, and the encoder-decoder
template became the basis for later attention-based translation models.
