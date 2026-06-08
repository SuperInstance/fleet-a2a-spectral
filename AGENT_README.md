# A2A Spectral→MIDI Module

Spectral graph analysis → ternary vector → MIDI notes — all agent-side, no UI.

Maps spectral-spreadsheet eigenvalues and Fiedler vectors into the fleet's core ternary {-1,0,+1} domain, then applies the accumulator algorithm for MIDI output.

## Exports

| Function | Signature | Purpose |
|----------|-----------|---------|
| `fiedler_to_ternary(fiedler, threshold=0.0)` | `list[float], float → list[int]` | Fiedler eigenvector → {-1,0,+1} |
| `fiedler_to_voicing(fiedler, threshold=0.0)` | `list[float], float → list[int]` | Fiedler → ternary → MIDI notes (+60) |
| `cr_to_dissonance(cr)` | `float → float` | Conservation Ratio → dissonance (0.0–1.0) |
| `cheeger_to_density(cheeger, max_density=16)` | `float, int → int` | Cheeger constant → rhythm onset density |
| `cheeger_to_ternary(cheeger, length=8)` | `float, int → list[int]` | Cheeger → ternary rhythm pattern |
| `spectral_to_ternary(eigenvals, fiedler, cr, cheeger)` | `→ list[int]` | Full spectral → ternary fusion |
| `ternary_to_midi(ternary)` | `list[int] → list[int]` | Core fleet invariant (accumulator) |

## Agent Usage

```python
from evaluator import fiedler_to_ternary, ternary_to_midi

# Agent A has a Fiedler vector from a graph Laplacian
fiedler = [-0.5, -0.1, 0.2, 0.6]
ternary = fiedler_to_ternary(fiedler)
# → [-1, -1, 0, 1]

# Agent B needs MIDI notes
midi = ternary_to_midi(ternary)
# → [60, 56, 56, 56, 60]
```

```python
from evaluator import spectral_to_ternary, cr_to_dissonance

# Single call: eigenvalues, Fiedler vector, CR, Cheeger → ternary vector
result = spectral_to_ternary(
    eigenvalues=[3.618, 1.382, 0.382, 0.0],
    fiedler=[-0.5, 0.5, 0.5, -0.5],
    cr=0.375,
    cheeger=0.667
)
# → [-1, 1, 1, -1, 1, 0, 1, 1]

dissonance = cr_to_dissonance(0.375)
# → 0.25 (0 = consonant, 1 = maximally dissonant)
```

## Tests

```bash
python3 -m pytest test_spectral.py -v
```

16 tests, all passing. Zero deps beyond Python stdlib.

## Dual Architecture Mapping

| Spectral Concept | Ternary Equivalent | MIDI Output |
|-----------------|-------------------|-------------|
| λ₁ (Fiedler value) | Voicing spread | Chord width |
| Fiedler vector | Ternary sequence | Voice leading |
| Conservation Ratio | Z₃ balance | Dissonance level |
| Cheeger constant | Rhythm density | Attack count |
