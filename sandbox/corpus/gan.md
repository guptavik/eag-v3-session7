# Generative Adversarial Networks (2014)

## Problem
Generative models trained by maximum likelihood often required intractable
probabilistic computations or produced blurry samples. A way to learn to generate
realistic data without explicitly modeling the data likelihood was desirable.

## Method
GANs set up a two-player game between a generator and a discriminator. The generator
maps random noise to synthetic samples; the discriminator tries to tell real data from
generated data. The generator is trained to fool the discriminator while the
discriminator is trained to catch it, so the two networks improve together. At the game's
equilibrium the generator's distribution matches the data distribution, and no explicit
likelihood is ever computed.

## Key contributions
- An adversarial training framework that learns a generator through competition rather
  than likelihood maximization.
- A theoretical analysis showing the optimum recovers the true data distribution.
- A new paradigm that spurred large families of image-generation models.

## Results
GANs produced sharp, realistic image samples and launched an influential research line
(DCGAN, StyleGAN, conditional GANs), though training stability and mode collapse
remained active challenges.
