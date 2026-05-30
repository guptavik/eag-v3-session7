# Proximal Policy Optimization Algorithms (PPO) (2017)

## Problem
Policy-gradient reinforcement learning is unstable: a single large update can collapse
performance. Trust-region methods like TRPO control update size but are complicated to
implement and compute, needing second-order information.

## Method
PPO is a first-order policy-gradient method that keeps each update close to the current
policy without a hard trust region. It optimizes a clipped surrogate objective: the
ratio between the new and old policy probabilities is clipped to a small range, which
removes the incentive to move the policy too far in one step. Multiple epochs of
minibatch updates are run on each batch of collected experience, balancing sample
efficiency and stability. Reward is assigned to actions using an advantage estimate
that distributes credit over the trajectory.

## Key contributions
- A clipped surrogate objective that limits destructive large policy updates using only
  first-order gradients.
- A simple, robust algorithm that reuses sampled data over several update epochs.
- Strong, stable performance with little tuning across many control tasks.

## Results
PPO became the default policy-optimization algorithm in reinforcement learning,
performing reliably across continuous-control and game benchmarks, and it is the RL
optimizer used in the RLHF pipelines that align language models.
