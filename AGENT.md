# AGENT.md — Agent Onboarding: `fleet-a2a-spectral`

You are an AI agent. You have access to `evaluator.py`. Here's exactly what you need to know.

---

## What You Import

```python
from evaluator import (
    spectral_to_ternary,    # Full pipeline: eigenvalues + Fiedler + CR + Cheeger → ternary
    ternary_to_midi,        # Ternary vector → MIDI note numbers
    fiedler_to_ternary,     # Fiedler eigenvector → ternary {-1,0,+1}
    fiedler_to_voicing,     # Fiedler → MIDI in one call (convenience wrapper)
    cr_to_dissonance,       # Conservation Ratio → float [0.0, 1.0]
    cheeger_to_density,     # Cheeger constant → int onset count
    cheeger_to_ternary,     # Cheeger → ternary rhythm pattern
)
```

Zero dependencies. Pure Python. No `numpy`, no `scipy`, no MIDI libraries, no file I/O.

**The module does NOT compute eigenvalues for you.** You need to supply spectral features computed upstream (e.g., from `numpy.linalg.eigh`, or from a graph processing pipeline). The module is the **mapping function** from spectral analysis to musical structure.

---

## What You Get Back

### From `spectral_to_ternary(eigenvalues, fiedler, cr, cheeger)` → `list[int]` in {-1, 0, +1}

A fused ternary vector combining voice leading (from the Fiedler eigenvector) and rhythm (from the Cheeger constant). Length matches the longer of the base Fiedler pattern and the Cheeger rhythm pattern.

This is the core function. It packages the full spectral graph→ternary pipeline.

### From `ternary_to_midi(ternary, base=60)` → `list[int]` of MIDI note numbers

The discrete integral transform. Each note is:

```
note[0] = base
note[i] = note[i-1] + ternary[i-1] * 4
```

- `+1` → major third up (+4 semitones)
- `0` → unison (stay)
- `-1` → minor third down (−4 semitones)

### From `cr_to_dissonance(cr)` → `float` [0.0, 1.0]

| CR | Result |
|----|--------|
| 0.5 | 0.0 — fully consonant |
| 0.25 or 0.75 | 0.5 — mixed |
| 0.0 or 1.0 | 1.0 — maximally dissonant |

### From `cheeger_to_density(cheeger, max_density=16)` → `int` [1, max_density]

Round(cheeger × max_density), clamped to [1, max_density].

### From `cheeger_to_ternary(cheeger, length=8)` → `list[int]` in {0, 1}

Evenly-spaced onset pattern. Output length = `length`. Sum of pattern = density.

### From `fiedler_to_ternary(fiedler, threshold=0.0)` → `list[int]` in {-1, 0, +1}

| fiedler value | ternary |
|---------------|---------|
| v < -threshold | -1 |
| abs(v) ≤ threshold | 0 |
| v > threshold | +1 |

### From `fiedler_to_voicing(fiedler, threshold=0.0, base=60)` → `list[int]` MIDI

Equivalent to `ternary_to_midi(fiedler_to_ternary(fiedler, threshold), base)`.

---

## What the Module Does NOT Do (And What You Need To Provide)

| You need to provide... | Because the module doesn't... |
|------------------------|-------------------------------|
| Laplacian eigenvalues | Compute the graph Laplacian |
| Fiedler eigenvector | Solve the eigenproblem |
| Conservation Ratio | Compute spectral mass distribution |
| Cheeger constant | Compute the isoperimetric number |
| MIDI output device | Render audio or send to a synth |

**Typical upstream computation** (not included in this module):

```python
import numpy as np

# You have an adjacency matrix A
L = np.diag(np.sum(A, axis=1)) - A  # Laplacian
eigenvalues, eigenvectors = np.linalg.eigh(L)

# Extract spectral features for evaluator.py
fiedler_vector = eigenvectors[:, 1].tolist()  # second smallest eigenvector
cr = sum(eigenvalues[:2]) / sum(eigenvalues)   # Conservation Ratio
cheeger = eigenvalues[1] / 2                   # Cheeger inequality lower bound
```

---

## Quickstart for an Agent

```python
"""You are an agent with spectral graph data. You want MIDI."""

from evaluator import spectral_to_ternary, ternary_to_midi

# Hypothetical spectral data
eigs   = [3.618, 1.382, 0.382, 0.0]
fiedler = [-0.5, 0.5, -0.3, 0.3]
cr     = 0.6
cheeger = 0.45

# One call to get ternary
ternary = spectral_to_ternary(eigs, fiedler, cr, cheeger)

# One call to get MIDI
notes = ternary_to_midi(ternary, base=60)

# notes is ready to send to any MIDI renderer
```

---

## Error Handling

All functions are pure and deterministic. No exceptions are raised for valid input types. Edge cases:

- **Empty input lists:** `ternary_to_midi([])` returns `[base]` (a single note).
- **NaN/Inf in floats:** Not guarded — callers should pre-filter.
- **Negative Cheeger:** `cheeger_to_density` clamps to 1.
- **CR outside [0,1]:** `cr_to_dissonance` computes `abs(cr - 0.5) * 2.0` and clamps at 1.0.

---

## Contract

```
Input:  Spectral features (eigenvalues, Fiedler eigenvector, CR, Cheeger)
Output: Ternary vector {-1,0,+1} → MIDI note numbers
State:  None — pure functions, zero side effects
Self-test: 8 invariant checks on `python evaluator.py`
Size:  6.4 KB, zero external dependencies
```

You import. You call. You get MIDI. That's the contract.
