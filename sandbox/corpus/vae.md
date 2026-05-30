# Auto-Encoding Variational Bayes (Variational Autoencoder) (2013)

## Problem
Fitting latent-variable generative models to large datasets is hard because the
posterior over latents is usually intractable, which blocks efficient maximum-
likelihood learning and inference.

## Method
The variational autoencoder pairs a probabilistic decoder, which maps latent variables
to data, with an encoder network that approximates the intractable posterior over
latents. Training maximizes a variational lower bound (the ELBO) on the data
likelihood. The key trick, the reparameterization, expresses a sample from the latent
distribution as a deterministic function of the parameters plus independent noise, so
gradients can flow through the sampling step and the whole model trains with ordinary
backpropagation.

## Key contributions
- The reparameterization trick, enabling low-variance gradient estimates through random
  latent sampling.
- A scalable variational objective (the ELBO) for deep latent-variable models.
- A jointly trained encoder-decoder that supports both generation and approximate
  inference.

## Results
VAEs trained efficiently on image datasets, produced a smooth, structured latent space
useful for interpolation and representation learning, and became a foundational
deep generative model alongside GANs.
