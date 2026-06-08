# fleet-a2a-spectral

Turn the algebraic topology of a graph into music. Laplacian eigenvalues, Fiedler eigenvectors, Cheeger constants, and conservation ratios become ternary vectors, then MIDI notes.

## The Problem

A fleet of agents forms a communication graph. You can compute its spectral properties — Laplacian eigenvalues, eigenvectors, isoperimetric ratios — but these are abstract numbers. How do you *hear* the structure of a graph? And how do you do it in a way that's mathematically grounded rather than arbitrary?

More concretely: you have a graph. You've computed its spectral decomposition. Now you need a ternary vector (the fleet's lingua franca) that captures the graph's harmonic content, and you need it in a form that other fleet modules can process.

## The Insight

Three spectral features map to three musical dimensions:

| Spectral Feature | Musical Dimension | Why |
|-----------------|-------------------|-----|
| **Fiedler eigenvector** | Voice leading (melody) | The second eigenvector captures the graph's natural bipartition — which nodes cluster together and which pull apart. Quantized to {-1, 0, +1}, it becomes a sequence of rising and falling intervals: a melody the graph wants to sing. |
| **Cheeger constant** | Rhythm density | The isoperimetric ratio measures how hard it is to cut the graph in two. High Cheeger = dense connections = many onsets. Low Cheeger = sparse, bottlenecked = few onsets. Connectivity maps directly to rhythmic activity. |
| **Conservation Ratio (CR)** | Dissonance | CR measures how the spectral mass distributes across eigenvalues. CR ≈ 0.5 means balanced energy = consonance. CR near 0 or 1 means skewed energy = dissonance. |

The fusion algorithm: the Fiedler vector provides pitch content, the Cheeger constant gates it with rhythm (silencing notes where the rhythm pattern is 0), and the CR tells you how tense the result should feel.

This works because of the **Cheeger inequality**: `h(G) ≥ λ₂/2`, where `h(G)` is the Cheeger constant and `λ₂` is the Fiedler value. The Fiedler value and Cheeger constant are not independent — they're bound together by this inequality. The voice leading and rhythm density of the output are thus mathematically coupled, not independently chosen.

## How It Works

### Step 1: Fiedler → ternary (voice leading)

```python
fiedler_to_ternary([-0.5, -0.1, 0.2, 0.6])
# → [-1, -1, 1, 1]
```

Each Fiedler entry is quantized to {-1, 0, +1} based on sign. The optional `threshold` parameter sends near-zero values to 0:

```python
fiedler_to_ternary([-0.5, -0.1, 0.2, 0.6], threshold=0.15)
# → [-1, 0, 1, 1]  # -0.1 is within ±0.15, becomes rest
```

The ternary vector then passes through the fleet's standard discrete integral to produce MIDI notes:

```python
ternary_to_midi([-1, -1, 1, 1])
# → [60, 56, 52, 56, 60]  # descending then ascending
```

### Step 2: Cheeger → rhythm pattern

```python
cheeger_to_ternary(0.5, length=8)
# → [1, 0, 1, 0, 1, 0, 1, 0]  (4 onsets out of 8 positions)
```

Higher Cheeger → more `1`s → more active rhythm. The onsets are distributed evenly across the pattern length.

### Step 3: Fusion

```python
spectral_to_ternary(
    eigenvalues=[3.618, 1.382, 0.382, 0.0],
    fiedler=[-0.5, 0.5, 0.5, -0.5],
    cr=0.375,
    cheeger=0.667
)
```

The Fiedler provides the base ternary pattern. The Cheeger provides a rhythm mask. Where the mask is 0, the output is silenced (set to 0). Where the mask is 1, the Fiedler value passes through. The result is a single fused ternary vector carrying both pitch and rhythm information.

### Step 4: CR → dissonance score

```python
cr_to_dissonance(0.5)   # → 0.0 (consonant: balanced spectral energy)
cr_to_dissonance(0.75)  # → 0.5 (moderate tension)
cr_to_dissonance(0.0)   # → 1.0 (maximum dissonance: all energy at one extreme)
```

The formula is `min(1.0, abs(cr - 0.5) × 2.0)`. This is a linear mapping from CR deviation to a [0, 1] dissonance score. It's grounded in the Courant-Fischer min-max theorem: eigenvalue spacing reflects how "spread out" the graph's energy is.

## Code Example

### Full spectral pipeline

```python
from evaluator import spectral_to_ternary, ternary_to_midi

# Your graph analysis produced these:
eigenvalues = [3.618, 1.382, 0.382, 0.0]
fiedler     = [-0.5, 0.5, 0.5, -0.5]
cr          = 0.375
cheeger     = 0.667

# One call: spectral features → fused ternary → MIDI
ternary = spectral_to_ternary(eigenvalues, fiedler, cr, cheeger)
midi    = ternary_to_midi(ternary, base=60)
```

### Individual features

```python
from evaluator import fiedler_to_voicing, cr_to_dissonance, cheeger_to_density

# Just the melodic contour from the Fiedler vector
notes = fiedler_to_voicing([-0.5, -0.1, 0.2, 0.6], base=60)
# → [60, 56, 56, 60, 64]

# Just the tension from the conservation ratio
tension = cr_to_dissonance(0.375)  # → 0.25

# Just the rhythm density from the Cheeger constant
onsets = cheeger_to_density(0.667, max_density=16)  # → 11
```

### Run the self-test

```bash
python evaluator.py
```

```
✅ INVARIANT: [60, 64, 64, 60, 64, 64, 60, 64, 68]
✅ FIEDLER: [-0.5, -0.1, 0.2, 0.6] → [-1, -1, 1, 1]
✅ FIEDLER_THRESHOLD: [-1, 0, 1, 1]
✅ CR_CONSONANT: 0.0
✅ CR_DISSONANT: 1.0
✅ CR_MID: 0.5
✅ CHEEGER_DENSITY: 8
✅ CHEEGER_PATTERN: [1, 0, 1, 0, 1, 0, 1, 0]
✅ SPECTRAL_FUSION: [-1, 0, 1, 1]
✅ ALL 8 TESTS PASS
```

## Module Map

```
evaluator.py — single file, zero dependencies
├── spectral_to_ternary(eigs, fiedler, cr, cheeger)  # full fusion
├── fiedler_to_ternary(fiedler, threshold)            # eigenvector → ternary
├── fiedler_to_voicing(fiedler, threshold, base)      # one-call → MIDI
├── cr_to_dissonance(cr)                              # conservation ratio → tension
├── cheeger_to_density(cheeger, max_density)           # connectivity → onset count
├── cheeger_to_ternary(cheeger, length)                # connectivity → rhythm pattern
└── ternary_to_midi(ternary, base)                     # discrete integral (fleet invariant)
```

### The theorems behind each function

| Function | Mathematical Foundation |
|----------|----------------------|
| `fiedler_to_ternary` | Fiedler's theorem: the second eigenvector gives the optimal relaxation of the graph bipartition problem |
| `cheeger_to_density` | Cheeger inequality: `h(G) ≥ λ₂/2` binds connectivity to spectral gap |
| `cr_to_dissonance` | Courant-Fischer min-max: eigenvalue distribution reflects energy concentration |
| `spectral_to_ternary` | All three: the fusion is valid because Fiedler, Cheeger, and CR are not independent — they're bound by the same Laplacian |

## Design Decisions

**Why quantize the Fiedler vector instead of using it directly?** The Fiedler eigenvector is real-valued. Direct use would require a continuous-to-MIDI mapping with arbitrary scaling. Quantizing to {-1, 0, +1} produces a ternary vector — the fleet's shared representation — that any other module (WASM kernel, pipeline, bridge) can process without knowing where it came from. The threshold parameter lets you control how aggressively the quantization happens.

**Why linear mapping for Cheeger → density?** The Cheeger constant already ranges from 0 to ~1 (for normalized cuts). A linear map to onset count is the simplest bijection that preserves ordering. More connected → more onsets. The `max_density` parameter caps the upper bound so you don't get unreasonable density values.

**Why is CR dissonance centered at 0.5?** CR measures what fraction of spectral mass is in the selected eigenvalues. At exactly 0.5, the mass is evenly split between "selected" and "unselected" portions — this is the balanced state. Deviation in either direction means concentration, which maps to harmonic tension. The `abs(cr - 0.5) × 2.0` formula produces a [0, 1] range where 0 = perfect balance and 1 = maximum skew.

**Why does `spectral_to_ternary` fuse voice and rhythm instead of keeping them separate?** The fleet's downstream consumers (WASM kernel, pipeline) operate on single ternary vectors. Fusing at the source means every downstream module gets both pitch and rhythm information in one pass. If you need them separate, call `fiedler_to_ternary` and `cheeger_to_ternary` individually.

**Why doesn't this module compute eigenvalues?** Eigenvalue computation is a separate concern that depends on the graph representation (adjacency matrix, edge list, etc.) and the numerical library available (numpy, scipy, eigen, etc.). This module consumes the *results* of spectral analysis, not the analysis itself. It's a pure function of four numbers: eigenvalues, Fiedler vector, CR, and Cheeger.

## Status

8/8 tests pass. Single file (`evaluator.py`), zero dependencies, pure Python 3.

### Fleet

| Module | Role |
|--------|------|
| [fleet-a2a-bridge](https://github.com/SuperInstance/fleet-a2a-bridge) | I2I bottle ↔ spreadsheet formula translation |
| [fleet-a2a-wasm](https://github.com/SuperInstance/fleet-a2a-wasm) | 514-byte WASM ternary→MIDI kernel (same accumulator) |
| **fleet-a2a-spectral** | You are here — spectral graph → ternary → MIDI |
| [fleet-a2a-pipeline](https://github.com/SuperInstance/fleet-a2a-pipeline) | ESM pipeline: CSV → ternary → MIDI → analysis |

MIT.
