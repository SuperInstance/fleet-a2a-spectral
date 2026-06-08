"""A2A Spectral→MIDI Evaluator — Agent module.

Maps spectral graph analysis (Fiedler vectors, Conservation Ratio,
Cheeger constants) into ternary {-1,0,+1} vectors, then to MIDI notes.

Agent-consumable: no UI, no plots, no DOM. Pure function calls.
"""

def ternary_to_midi(ternary, base=60):
    """Core fleet invariant: cumulative sum (discrete integral).
    
    Each note = previous_note + v * 4.
    +1 → major third up, 0 → unison, -1 → minor third down.
    
    Example:
        [1,0,-1,1,0,-1,1,1] → [60,64,64,60,64,64,60,64,68]
    """
    notes = [base]
    for v in ternary:
        notes.append(notes[-1] + v * 4)
    return notes


def fiedler_to_ternary(fiedler, threshold=0.0):
    """Quantize Fiedler eigenvector values to {-1, 0, +1}.
    
    Args:
        fiedler: List of Fiedler eigenvector entries (float)
        threshold: Values within ±threshold become 0
        
    Returns:
        Ternary vector in {-1, 0, +1}
    """
    result = []
    for v in fiedler:
        if abs(v) <= threshold:
            result.append(0)
        elif v > threshold:
            result.append(1)
        else:
            result.append(-1)
    return result


def fiedler_to_voicing(fiedler, threshold=0.0, base=60):
    """Fiedler eigenvector → MIDI voicing in one call."""
    return ternary_to_midi(fiedler_to_ternary(fiedler, threshold), base)


def cr_to_dissonance(cr):
    """Conservation Ratio → dissonance score.
    
    Conservation Ratio measures spectral gap deviation from 0.5.
    
    Args:
        cr: Conservation ratio (float, expected ≈0.5 for balanced)
        
    Returns:
        Dissonance score (0.0 = consonant, 1.0 = maximally dissonant)
    """
    return min(1.0, abs(cr - 0.5) * 2.0)


def cheeger_to_density(cheeger, max_density=16):
    """Cheeger constant → rhythm onset density.
    
    Higher Cheeger = more connected = more onsets per measure.
    
    Args:
        cheeger: Cheeger constant (0.0 to 1.0 typically)
        max_density: Maximum number of onsets
        
    Returns:
        Number of onsets in the rhythm pattern
    """
    return max(1, min(max_density, round(cheeger * max_density)))


def cheeger_to_ternary(cheeger, length=8):
    """Cheeger constant → ternary rhythm pattern.
    
    Creates a pattern where '1's = events (rests = '0' or '-1').
    Higher Cheeger = more events.
    
    Args:
        cheeger: Cheeger constant
        length: Length of ternary pattern
        
    Returns:
        Ternary rhythm pattern
    """
    density = cheeger_to_density(cheeger, max_density=length)
    positions = set()
    step = max(1, length // max(density, 1))
    for i in range(min(density, length)):
        pos = (i * step) % length
        positions.add(pos)
    
    pattern = []
    for i in range(length):
        if i in positions:
            pattern.append(1)
        else:
            pattern.append(0)
    return pattern


def spectral_to_ternary(eigenvalues, fiedler, cr, cheeger):
    """Full spectral analysis → ternary vector.
    
    Fuses multiple spectral features into a single ternary vector.
    
    Args:
        eigenvalues: List of Laplacian eigenvalues
        fiedler: Fiedler eigenvector values
        cr: Conservation Ratio
        cheeger: Cheeger constant
        
    Returns:
        Combined ternary vector
    """
    # Fiedler → base ternary pattern (voice leading)
    base = fiedler_to_ternary(fiedler)
    
    # Cheeger → rhythm pattern
    rhythm = cheeger_to_ternary(cheeger, length=len(base))
    
    # Fuse: multiply active rhythm by base, keep steady state for rests
    fused = []
    for i in range(max(len(base), len(rhythm))):
        b = base[i % len(base)] if i < len(base) else 0
        r = rhythm[i % len(rhythm)] if i < len(rhythm) else 0
        if r == 0:
            fused.append(0)  # rest
        else:
            fused.append(b)  # active voice
    
    return fused


# === Self-test on load ===
if __name__ == "__main__":
    import sys
    
    errors = 0
    
    # Test invariant
    result = ternary_to_midi([1,0,-1,1,0,-1,1,1])
    expected = [60,64,64,60,64,64,60,64,68]
    if result == expected:
        print(f"✅ INVARIANT: {result}")
    else:
        print(f"❌ INVARIANT: got {result}, expected {expected}")
        errors += 1
    
    # Test fiedler_to_ternary
    f = [-0.5, -0.1, 0.2, 0.6]
    t = fiedler_to_ternary(f)
    if t == [-1, -1, 1, 1]:
        print(f"✅ FIEDLER: {f} → {t}")
    else:
        print(f"❌ FIEDLER: got {t}, expected [-1, -1, 1, 1]")
        errors += 1
    
    # Test fiedler_to_ternary with threshold
    t = fiedler_to_ternary(f, threshold=0.15)
    if t == [-1, 0, 1, 1]:
        print(f"✅ FIEDLER_THRESHOLD: {t}")
    else:
        print(f"❌ FIEDLER_THRESHOLD: got {t}, expected [-1, 0, 1, 1]")
        errors += 1
    
    # Test cr_to_dissonance
    d = cr_to_dissonance(0.5)
    if d == 0.0:
        print(f"✅ CR_CONSONANT: {d}")
    else:
        print(f"❌ CR_CONSONANT: got {d}, expected 0.0")
        errors += 1
    
    d = cr_to_dissonance(0.0)
    if d == 1.0:
        print(f"✅ CR_DISSONANT: {d}")
    else:
        print(f"❌ CR_DISSONANT: got {d}, expected 1.0")
        errors += 1
    
    d = cr_to_dissonance(0.75)
    if abs(d - 0.5) < 0.001:
        print(f"✅ CR_MID: {d}")
    else:
        print(f"❌ CR_MID: got {d}, expected 0.5")
        errors += 1
    
    # Test cheeger_to_density
    den = cheeger_to_density(0.5, max_density=16)
    if den == 8:
        print(f"✅ CHEEGER_DENSITY: {den}")
    else:
        print(f"❌ CHEEGER_DENSITY: got {den}, expected 8")
        errors += 1
    
    # Test cheeger_to_ternary
    pat = cheeger_to_ternary(0.5, length=8)
    if len(pat) == 8 and sum(pat) == 4 and all(v in (0, 1) for v in pat):
        print(f"✅ CHEEGER_PATTERN: {pat}")
    else:
        print(f"❌ CHEEGER_PATTERN: got {pat}")
        errors += 1
    
    # Test spectral_to_ternary fusion
    fused = spectral_to_ternary(
        [3.618, 1.382, 0.382, 0.0],
        [-0.5, 0.5, 0.5, -0.5],
        0.375,
        0.667
    )
    if len(fused) > 0 and all(v in (-1, 0, 1) for v in fused):
        print(f"✅ SPECTRAL_FUSION: {fused}")
    else:
        print(f"❌ SPECTRAL_FUSION: got {fused}")
        errors += 1
    
    # Summary
    if errors == 0:
        print(f"\n✅ ALL 8 TESTS PASS")
        sys.exit(0)
    else:
        print(f"\n❌ {errors} TEST(S) FAILED")
        sys.exit(1)
