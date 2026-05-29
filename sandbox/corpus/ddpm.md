# Denoising Diffusion Probabilistic Models (DDPM) (2020)

## Problem
GANs generate sharp images but train unstably and can collapse to limited variety,
while likelihood-based models often produced blurrier samples. A stable generative model
with high sample quality and good mode coverage was wanted.

## Method
Diffusion models define a fixed forward process that gradually adds Gaussian noise to
data over many steps until it becomes pure noise. A neural network is trained to reverse
this process step by step, learning to denoise. The paper shows the training objective
simplifies to predicting the noise added at each step with a plain mean-squared-error
loss, making optimization stable. Generation starts from random noise and iteratively
denoises through the learned reverse steps to produce a sample.

## Key contributions
- A simple noise-prediction objective that makes diffusion training stable and
  effective.
- A principled connection between denoising score matching and diffusion processes.
- High-quality, diverse image generation rivaling GANs without adversarial training.

## Results
DDPM produced image samples competitive with or better than leading GANs on standard
benchmarks while training stably, and it launched the diffusion-model wave that now
underpins state-of-the-art text-to-image and other generative systems.
