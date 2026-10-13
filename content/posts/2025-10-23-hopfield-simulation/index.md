---
title: "Monte Carlo Simulation of the Hopfield Model"
author: "Qizhi"
date: "2025-10-23"
description: "An interactive Hopfield model with two stored images: lower the temperature and watch random spins retrieve either pattern."
summary: "Explore associative memory with two stored patterns. Adjust the temperature, randomize the spins, and compare their overlap with each image."
categories:
  - Simulations
  - Physics
tags:
  - Simulations
  - Physics
  - Monte Carlo
  - Hopfield model
featured: true
cover:
  image: "cover.png"
  alt: "A random spin configuration evolving toward a stored pattern in the Hopfield model"
---

A Hopfield model stores patterns through interactions between spins. This demonstration loads two images as binary patterns and evolves a randomly initialized spin configuration with heat-bath updates. Change the temperature to see how thermal fluctuations affect pattern retrieval.[^1]

[^1]: JavaScript is required for the simulation and formula rendering.

## Interactive simulation

Move the temperature slider to adjust \(T/J\). At low temperature, the spins can align with either stored pattern or its inverted form. The random initial spins and heat-bath updates determine which memory is retrieved. At higher temperature, thermal fluctuations weaken this alignment. The two contrasting shades represent the spin states and follow the site's light or dark theme.

Use **Pause** to inspect a configuration, **Step** to advance by one Monte Carlo sweep, or **Randomize** to start from a new random configuration. The two overlaps show the alignment with each stored pattern; values near \(+1\) or \(-1\) indicate that pattern or its inverse. Try \(T/J=0.15\) and repeat **Randomize** to observe both memories. The outcomes need not occur equally often.

{{< simulation >}}

## Model and update rule

The demonstration uses a \(256\times256\) image grid, with \(N=65{,}536\) spins and \(P=2\) stored patterns, shown beside the controls. Both patterns contribute to the same coupling matrix.

The second image is derived from the supplied color portrait. Its face, hair, eyebrow, and visible ear are filled white on a black background, with sparse black contours defining the features. Shading is removed, and the resulting image contains only black and white pixels. The original color image is retained separately.

For binary patterns \(\xi_i^\mu\in\{-1,+1\}\), the couplings are

\[
J_{ij}=\frac{1}{N}\sum_{\mu=1}^{P}\xi_i^\mu\xi_j^\mu,
\qquad J_{ii}=0.
\]

The local field at spin \(i\) is \(h_i=\sum_{j\ne i}J_{ij}s_j\). A heat-bath update flips the current spin with probability

\[
P(s_i\rightarrow -s_i)=\frac{1}{1+\exp(2s_i h_i/T)}.
\]

One sweep performs \(N\) randomly selected spin-update attempts. The simulation tracks the unnormalized overlaps \(M_\mu=\sum_j\xi_j^\mu s_j\) and updates them after each accepted flip. This evaluates the local field without constructing a full \(N\times N\) coupling matrix. The displayed overlap is \(m_\mu=M_\mu/N\).

## Source

This post adapts the Hopfield model demonstration from **the 2025 open-campus event at UTokyo, Kashiwa campus**. The heat-bath update rule and incremental overlap calculation are retained, with two stored images and controls adapted to this site.

[Hopfield simulation source code](hopfield.js)

[Fig: pattern 1](pattern1.png) · [Fig: pattern 2](pattern2-binary.png) · [Fig: pattern 2 (original color)](pattern2.png)

