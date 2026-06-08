# STUDENT_GUIDE.md — How Triangles Become Chords

> "I've never used spectral graph theory. Show me how triangles become chords."

This guide assumes minimal math. If you know what a graph is (dots connected by lines), you have enough. Everything else is built up from there.

---

## Step 0: What's a Graph?

A **graph** is just dots connected by lines:

```
    A ─── B
    │     │
    │     │
    C ─── D
```

The dots are **vertices** (or nodes). The lines are **edges**. That's it. A group of friends. A neural network. An agent communication channel. A musical scale. They're all graphs.

A **triangle** in a graph is three vertices all connected to each other:

```
    A ─── B
     \   /
      \ /
       C
```

That's your fundamental unit. Three friends who all know each other.

---

## Step 1: Why Triangles Matter

In spectral graph theory, the **graph Laplacian** is a matrix that encodes the graph's structure. For a graph with n vertices, it's an n×n matrix where:

- `L[i][i]` = number of edges connected to vertex i (its **degree**)
- `L[i][j]` = -1 if vertices i and j are connected, 0 otherwise

For our triangle (A, B, C all connected):

```
    A  B  C
A [ 2 -1 -1 ]     (A is connected to B and C, degree 2)
B [-1  2 -1 ]     (B is connected to A and C, degree 2)
C [-1 -1  2 ]     (C is connected to A and B, degree 2)
```

This matrix has **eigenvalues** and **eigenvectors** — special numbers and vectors that reveal deep truths about the graph.

---

## Step 2: Eigenvalues → The Graph's Fingerprint

Every graph Laplacian has eigenvalues. For our triangle:

```
λ₀ = 0.0   (always — this is the "everyone together" eigenvalue)
λ₁ = 3.0   (the Fiedler value — tells you about connectivity)
λ₂ = 3.0   (also 3.0 — this triangle is symmetric)
```

The **second eigenvalue** (λ₁) is called the **Fiedler value**. It's the most important number in this entire module. It tells you:

| Fiedler value | What it means |
|---------------|---------------|
| Close to 0 | The graph has a bottleneck — it can be split into two weakly-connected halves |
| Large | The graph is well-connected — no weak links |
| = 3 for a triangle | Three vertices, all strongly connected, no bottlenecks |

---

## Step 3: The Fiedler Vector → Voice Leading

The **Fiedler eigenvector** (the eigenvector for λ₁) assigns a number to each vertex that tells you which "side" of the graph it's on:

For our triangle:
```
fiedler(A) = maybe  0.816
fiedler(B) = maybe -0.408
fiedler(C) = maybe -0.408
```

This says: A is on one side, B and C are on the other. The exact numbers depend on the graph's structure.

**Now the magic:** We quantize these numbers to **{-1, 0, +1}**:

```python
from evaluator import fiedler_to_ternary

fiedler_vector = [0.816, -0.408, -0.408]
ternary = fiedler_to_ternary(fiedler_vector)
# → [1, -1, -1]
```

Then we turn ternary into **MIDI notes** using a cumulative sum (the discrete integral):

```python
from evaluator import ternary_to_midi

notes = ternary_to_midi([1, -1, -1], base=60)
```

Walk through it:

| Step | Ternary | Calculation | MIDI note | Interval |
|------|---------|-------------|-----------|----------|
| 0 | — | base = 60 | 60 (C4) | — |
| 1 | +1 | 60 + 1×4 = 64 | 64 (E4) | Major third ↑ |
| 2 | -1 | 64 + (-1)×4 = 60 | 60 (C4) | Minor third ↓ |
| 3 | -1 | 60 + (-1)×4 = 56 | 56 (G#3) | Minor third ↓ |

The triangle became a **C–E–C–G♯** arpeggio. Three vertices → three notes. That's how triangles become chords.

---

## Step 4: The Cheeger Constant → Rhythm

The **Cheeger constant** is a single number that measures how easy it is to cut the graph in half:

| Cheeger | Graph feel | Beats |
|---------|-----------|-------|
| 0.0–0.3 | Sparse, fragile, with bottlenecks | Few notes, wide spacing |
| 0.3–0.6 | Moderately connected | Moderate groove (4–8 notes) |
| 0.6–1.0 | Dense, strongly connected | Maximal onsets, driving |

A triangle has Cheeger = 0.667 (well-connected). So:

```python
from evaluator import cheeger_to_density, cheeger_to_ternary

# How many onsets?
cheeger_to_density(0.667, max_density=16)
# → 11 onsets per measure (dense rhythm!)

# Or get the full rhythm pattern
cheeger_to_ternary(0.667, length=8)
# → [1, 0, 1, 0, 1, 0, 1, 1]  (11 events spread across 8 positions)
```

---

## Step 5: Conservation Ratio → Dissonance

The **Conservation Ratio** measures how the spectral energy is distributed. Think of it like a seesaw:

- CR = 0.5: Perfectly balanced — the spectral mass is evenly split = **consonant**
- CR far from 0.5: Skewed spectrum = **dissonant**

```python
from evaluator import cr_to_dissonance

cr_to_dissonance(0.5)    # 0.0 — consonant
cr_to_dissonance(0.75)   # 0.5 — mixed
cr_to_dissonance(1.0)    # 1.0 — maximally dissonant
```

---

## Step 6: Put It All Together — Triangle → Full Music

```python
from evaluator import spectral_to_ternary, ternary_to_midi

# Your triangle gave you these spectral features:
eigenvalues = [0.0, 3.0, 3.0]    # triangle Laplacian spectrum
fiedler     = [0.816, -0.408, -0.408]
cr          = 0.5                  # perfectly balanced triangle
cheeger     = 0.667                # well-connected triangle

# Fuse everything into music
ternary = spectral_to_ternary(eigenvalues, fiedler, cr, cheeger)
notes   = ternary_to_midi(ternary, base=60)

print(f"Triangle → ternary: {ternary}")
print(f"Triangle → MIDI:   {notes}")
```

The triangle — three connected dots — becomes a melodic phrase with rhythm, voice leading, and harmonic character. That's the whole idea.

---

## Visual Summary: From Dots to Notes

```
  Three friends
  (a triangle)
       │
       ▼
  Graph Laplacian matrix
       │
       ▼
  Eigenvalues [0.0, 3.0, 3.0]  ← Fiedler value = 3.0
  Eigenvectors [0.577, 0.577, 0.577]  ← Fiedler vector
       │
       ▼
  Fiedler → ternary → [1, -1, -1]
       │
       ▼
  Ternary → MIDI → [60, 64, 64]  ← C, E, E (major)
       │
       ▼
  Cheeger (0.667) → rhythm → [1, 0, 1, 0, 1, 0, 1, 1]
       │
       ▼
  Fuse: voice × rhythm → performed music
```

---

## What About Bigger Graphs?

Everything scales linearly. A graph with 100 vertices produces a 100-dimensional Fiedler vector → 100 ternary values → 100 MIDI notes. The same math. The triangle is just the smallest interesting case.

| Graph size | Vertices | Fiedler entries | Notes produced |
|------------|----------|-----------------|----------------|
| Triangle | 3 | 3 | 4 (base + 3 steps) |
| Square | 4 | 4 | 5 |
| Hexagon | 6 | 6 | 7 |
| Complete K₅ | 5 | 5 | 6 |
| Your fleet | n | n | n+1 |

---

## The Three Key Intuitions

1. **Fiedler vector = graph's bisection signal.** Positive values are on one side, negative on the other. The music moves up and down as it crosses between graph partitions.

2. **Cheeger constant = graph's density.** More edges = more rhythm. A complete graph plays sixteenth notes. A tree plays sparse eighth notes.

3. **Conservation Ratio = graph's balance.** Evenly split spectral mass = consonant. Skewed = dissonant. The graph tells you whether it wants to be harmonious.

---

## One Final Demo

```python
# Complete graph K₆ (6 vertices, all connected)
# → high Cheeger, balanced spectral distribution
# → dense rhythm, consonant harmony
# → fast, rich, jazz-like

# Path graph P₆ (6 vertices in a line)
# → low Cheeger, simple spectrum
# → sparse rhythm, simple contour
# → slow, meditative, like a walking bass

# Star graph S₆ (1 center, 5 leaves)
# → medium Cheeger, one large partition + satellites
# → moderate rhythm, dramatic leaps
# → arpeggiated, spread-out, cinematic
```

Every graph tells a different story. Triangles became chords. Graphs became music. That's what this module does.
