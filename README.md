# fleet-a2a-spectral: Spectral Graph → MIDI Evaluator 🌀

**evaluator.py** — Pure Python, zero deps. Maps spectral properties of any graph to ternary {-1,0,+1} vectors, then to MIDI pitch sequences.

```
spectral graph  →  Laplacian eigenvalues  →  Fiedler vector  →  ternary {-1,0,+1}  →  MIDI notes
```

This is the **spectral engine** of the SuperInstance A2A fleet: the module that turns the algebraic topology of an agent communication graph into audible structure.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    evaluator.py (6.4 KB)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  eigenvalues, fiedler, cr, cheeger                         │
│       │                                                      │
│       ▼                                                      │
│  spectral_to_ternary(eigenvalues, fiedler, cr, cheeger)     │
│       │                                                      │
│       ├── fiedler_to_ternary(fiedler)   ──→ ternary voice    │
│       ├── cheeger_to_ternary(cheeger)   ──→ ternary rhythm   │
│       └── fuse: voice × rhythm                              │
│               │                                              │
│               ▼                                              │
│       ternary_to_midi(ternary)          ──→ [60, 64, 64...]  │
│                                                             │
│  Also directly:                                             │
│       fiedler_to_voicing(fiedler)       ──→ MIDI in one go  │
│       cr_to_dissonance(cr)              ──→ [0.0, 1.0]      │
│       cheeger_to_density(cheeger)       ──→ onset count     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
     ↑ agent imports evaluator
     ↑ no UI, no plots, no DOM
```

### The pipeline, step by step

1. **Input:** A graph's Laplacian eigenvalues, Fiedler eigenvector, Conservation Ratio (CR), and Cheeger constant — computed upstream (e.g., by `numpy.linalg.eigh` or a graph processing pipeline).

2. **Fiedler → voice leading:** The Fiedler eigenvector (eigenvector of the second-smallest eigenvalue) captures the graph's natural bisection. Each entry is quantized to {-1, 0, +1}, then integrated (cumulative sum × 4 semitones) into a MIDI pitch contour. This is the **voice** — the melodic line the graph wants to sing.

3. **Cheeger → rhythm:** The Cheeger constant is the graph's isoperimetric ratio — a measure of connectivity. Higher Cheeger → more connected → more rhythmic onsets. Lower Cheeger → sparser graph → sparser note density. This becomes a ternary rhythm pattern.

4. **Fusion:** Voice × Rhythm. Where the rhythm has a rest (0), the output goes silent. Where it has an event (1), the voice sounds.

5. **Output:** A sequence of MIDI note numbers, ready for any synthesizer or sequencer.

---

## Theorems That Make This Work

### Cheeger Inequality — Why the Fiedler Value Matters

The Cheeger inequality is the foundational bound of spectral graph theory:

```
h(G) ≥ λ₂ / 2
```

where `h(G)` is the **Cheeger constant** (isoperimetric number) of the graph and `λ₂` is the second-smallest Laplacian eigenvalue (the **Fiedler value**).

**Intuition:** The Fiedler value tells you how easy it is to cut the graph into two balanced pieces. A small Fiedler value means there's a narrow bottleneck — the graph can be split with few edge cuts. A large Fiedler value means the graph is well-connected, no bottlenecks.

**In this module:**
- The Fiedler value `λ₂` is computed upstream and propagated as the Cheeger constant
- `cheeger_to_density(cheeger)` maps it linearly: more connectivity → more onsets
- A graph that's one big cluster (high Cheeger) plays dense rhythm. A graph with bottlenecks (low Cheeger) plays sparse, punctuated rhythm.

### Cheeger → Rhythm

| Cheeger | Graph feel | Onset density | Musical feel |
|---------|-----------|---------------|-------------|
| 0.0–0.2 | Fragmented, bottlenecks | 1–3 onsets/measure | Sparse, pointillist |
| 0.2–0.5 | Moderately connected | 4–8 onsets/measure | Groove, syncopation |
| 0.5–0.8 | Well-connected | 8–13 onsets/measure | Dense, active |
| 0.8–1.0 | Nearly complete | 13–16 onsets/measure | Maximal, driving |

### Courant-Fischer & CR → Dissonance

The Courant-Fischer min-max theorem characterizes eigenvalues as:

```
λₖ = min_{dim(S)=k} max_{x∈S, x≠0} (xᵀLx) / (xᵀx)
```

The **Conservation Ratio** (CR) measures where the spectral mass concentrates:

```python
cr = sum of selected eigenvalues / total spectral mass
```

A CR of 0.5 means the spectral mass is evenly split — balanced, harmonic. Deviation from 0.5 means the spectrum is skewed:

```python
dissonance = min(1.0, abs(cr - 0.5) * 2.0)
```

| CR | Meaning | Dissonance |
|----|---------|-----------|
| 0.5 | Perfect spectral balance | 0.0 — consonant |
| 0.75 | Moderate skew | 0.5 — mixed |
| 0.0 or 1.0 | Maximum skew | 1.0 — maximally dissonant |

This is a direct application of Courant-Fischer: the eigenvalue spacing tells you how "spread out" the graph's energy is. Spread-out eigenvalues = balanced = consonant. Clustered eigenvalues = skewed = dissonant.

---

## "Wait, show me" — Python One-Liner

```python
# From nothing to MIDI in one import
from evaluator import spectral_to_midi  # (this module wraps spectral_to_ternary → ternary_to_midi)

# Your graph gave you these (e.g., from numpy.linalg.eigh of the Laplacian):
eigenvalues = [3.618, 1.382, 0.382, 0.0]
fiedler     = [-0.5, 0.5, 0.5, -0.5]
cr          = 0.375
cheeger     = 0.667

# Full pipeline in one call
ternary = spectral_to_ternary(eigenvalues, fiedler, cr, cheeger)
midi    = ternary_to_midi(ternary, base=60)

print(ternary)  # → [-1, 0, 1, 1]  (voice + rhythm fused)
print(midi)     # → [60, 56, 56, 60, 64, ...]  (actual MIDI numbers)
```

**Or, piece by piece:**

```python
from evaluator import fiedler_to_voicing, cr_to_dissonance, cheeger_to_density

# Just the melodic line
notes = fiedler_to_voicing([-0.5, -0.1, 0.2, 0.6], base=60)
# → [60, 56, 56, 60, 64]  (descending then ascending fourths)

# Just the dissonance
d = cr_to_dissonance(0.5)   # 0.0 → perfectly consonant
d = cr_to_dissonance(0.0)   # 1.0 → maximally dissonant

# Just the rhythm density
onsets = cheeger_to_density(0.5)  # 8 onsets per measure
```

---

## API Reference

### Core Functions

| Function | Input | Output | What It Does |
|----------|-------|--------|-------------|
| `spectral_to_ternary(eigs, fiedler, cr, cheeger)` | Lists + floats | `list[int]` in {-1,0,+1} | Full spectral analysis → fused ternary |
| `fiedler_to_ternary(fiedler, threshold=0.0)` | List of floats | `list[int]` in {-1,0,+1} | Quantize Fiedler eigenvector to ternary |
| `ternary_to_midi(ternary, base=60)` | List of ints | `list[int]` MIDI notes | Discrete integral: `note[n] = note[n-1] + v*4` |
| `fiedler_to_voicing(fiedler, threshold=0.0, base=60)` | List of floats | `list[int]` MIDI notes | One-call Fiedler → MIDI |

### Spectral Feature Extractors

| Function | Input | Output | What It Does |
|----------|-------|--------|-------------|
| `cr_to_dissonance(cr)` | Float | `float` [0.0, 1.0] | Conservation Ratio → dissonance score |
| `cheeger_to_density(cheeger, max_density=16)` | Float | `int` | Cheeger constant → onset count |
| `cheeger_to_ternary(cheeger, length=8)` | Float | `list[int]` in {0,1} | Cheeger → ternary rhythm pattern |

### Threshold Semantics

The `threshold` parameter in `fiedler_to_ternary` controls quantization strictness:

| threshold | fiedler=[-0.5, -0.1, 0.0, 0.2, 0.6] | Effect |
|-----------|------|--------|
| 0.0 | `[-1, -1, 0, 1, 1]` | Every nonzero value quantized |
| 0.15 | `[-1, 0, 0, 1, 1]` | Near-zero values become rest |
| 0.5 | `[-1, 0, 0, 0, 1]` | Only strong values pass through |

---

## Cross-Fleet Integration

This module is a node in the SuperInstance A2A fleet. It interoperates with:

| Repo | Role |
|------|------|
| [fleet-a2a-wasm](https://github.com/SuperInstance/fleet-a2a-wasm) | The 514-byte WASM kernel implementing the same ternary→MIDI invariant — same cumulative sum, same ⊕4 semitone rule. The spectral module is the **high-level orchestration**; the WASM module is the **drop-in binary** for agents that can't run Python. |
| [ternary-invariants](https://github.com/SuperInstance/ternary-invariants) | The formal theory of ternary {-1,0,+1} over ℤ₃. The conservation property (`+1 + (-1) = 0`) that makes the discrete integral meaningful. |
| [constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core) | Exact Pythagorean manifold snapping — the lattice of exact rational points on the unit circle. Spectral analysis of the constraint graph produces the eigenvalues/vectors this module consumes. |
| [fleet-a2a-pipeline](https://github.com/SuperInstance/fleet-a2a-pipeline) | Orchestrates the full A2A pipeline: graph construction → spectral analysis → MIDI. `evaluator.py` is the spectral→MIDI step. |
| [fleet-a2a-bridge](https://github.com/SuperInstance/fleet-a2a-bridge) | Bridges spectral output to downstream MIDI processing (velocity, articulation, CC). |

---

## Agent Usage

```python
# Standard import — the module is self-contained
from evaluator import (
    spectral_to_ternary,
    ternary_to_midi,
    fiedler_to_voicing,
    cr_to_dissonance,
    cheeger_to_density,
    cheeger_to_ternary,
)

# Full spectral pipeline
ternary = spectral_to_ternary(eigenvalues, fiedler_vector, cr, cheeger_constant)
midi_notes = ternary_to_midi(ternary, base=72)
```

See [AGENT.md](./AGENT.md) for the complete agent onboarding guide.

---

## Quality

| Check | Status |
|-------|--------|
| Self-test on import | 8 invariant tests pass |
| Dependencies | Zero — pure Python |
| Agent interface | Pure function calls, no side effects |
| Input validation | Explicit in docstrings |
