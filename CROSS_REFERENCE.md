# CROSS_REFERENCE.md — Fleet Ecosystem Map

This document maps every known SuperInstance fleet repo and its relationship to `fleet-a2a-spectral`. Use it to navigate the ecosystem.

---

## Direct Integrations

These repos share data, invariants, or pipeline stages with this module.

| Repo | Language | Relationship |
|------|----------|-------------|
| [fleet-a2a-wasm](https://github.com/SuperInstance/fleet-a2a-wasm) | WASM / WAT | **Same invariant, different substrate.** The 514-byte WASM kernel implements the identical ternary→MIDI mapping (cumulative sum, ±4 semitones). This spectral module is the Python orchestration layer; the WASM module is the drop-in binary for agents in constrained environments. They produce identical MIDI from identical ternary input. |
| [fleet-a2a-pipeline](https://github.com/SuperInstance/fleet-a2a-pipeline) | JavaScript | Orchestrates the full A2A pipeline: graph extraction → spectral computation → MIDI output. `evaluator.py` is the spectral→MIDI step. The pipeline feeds eigenvalues/Fiedler/CR/Cheeger into this module. |
| [fleet-a2a-bridge](https://github.com/SuperInstance/fleet-a2a-bridge) | Python | Bridges spectral MIDI output to downstream MIDI processing modules (velocity, articulation, CC, tempo). Takes the raw note sequence from `ternary_to_midi` and routes it to the expressive fleet. |
| [constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core) | Rust | Exact Pythagorean manifold snapping produces a constraint graph. Spectral analysis of that constraint graph generates the eigenvalues and eigenvectors that `evaluator.py` consumes. **constraint-theory-core → spectral analysis → evaluator.py → MIDI.** |

---

## Ternary Invariants & Core Math

| Repo | Language | Relationship |
|------|----------|-------------|
| [ternary-invariants](https://github.com/SuperInstance/ternary-invariants) | — | The formal theory of ternary {-1,0,+1} over ℤ₃. The conservation property (`+1 + (-1) = 0`) is the bedrock invariant that makes the discrete integral meaningful. The `spectral_to_ternary` fusion function depends on this. |
| [constraint-theory-core](https://github.com/SuperInstance/constraint-theory-core) | Rust | See above. Also provides `PythagoreanQuantizer` with Ternary mode — an alternative path to {-1,0,+1} quantization of continuous vectors. |
| [grove-ast](https://github.com/SuperInstance/grove-ast) | — | AST types and ternary primitives for the Grove compiler ecosystem. The ternary type system used across the fleet originates here. |
| [renormalization-agent](https://github.com/SuperInstance/renormalization-agent) | — | Renormalization group for multi-scale agent behavior. Spectral graph features can feed into RG flow analysis. |

---

## Fleet MIDI Modules

These consume MIDI note sequences produced by `evaluator.py` (or the WASM kernel) and add expressive rendering.

| Repo | Adds |
|------|------|
| [fleet-midi-velocity](https://github.com/SuperInstance/fleet-midi-velocity) | Per-note velocity from agent state intensity |
| [fleet-midi-dynamics](https://github.com/SuperInstance/fleet-midi-dynamics) | Dynamics envelope from agent dispatch rate |
| [fleet-midi-articulation](https://github.com/SuperInstance/fleet-midi-articulation) | Staccato/legato from agent persistence |
| [fleet-midi-expression](https://github.com/SuperInstance/fleet-midi-expression) | Expressive CC curves from agent modulation |
| [fleet-midi-tempo](https://github.com/SuperInstance/fleet-midi-tempo) | Tempo from agent dispatch rate |
| [fleet-midi-scale](https://github.com/SuperInstance/fleet-midi-scale) | Scale quantization from agent state distribution |
| [fleet-midi-mode](https://github.com/SuperInstance/fleet-midi-mode) | Mode detection from agent state patterns |
| [fleet-midi-chord](https://github.com/SuperInstance/fleet-midi-chord) | Chord spelling from ternary vector balance |
| [fleet-midi-voicing](https://github.com/SuperInstance/fleet-midi-voicing) | Chord voicing optimization from agent state balance |
| [fleet-midi-inversion](https://github.com/SuperInstance/fleet-midi-inversion) | Chord inversion from agent state position |
| [fleet-midi-substitution](https://github.com/SuperInstance/fleet-midi-substitution) | Chord substitution from agent state tension |
| [fleet-midi-modulation](https://github.com/SuperInstance/fleet-midi-modulation) | Key modulation from agent state transitions |
| [fleet-midi-cc](https://github.com/SuperInstance/fleet-midi-cc) | Continuous controller MIDI from agent modulation |
| [fleet-midi-pan](https://github.com/SuperInstance/fleet-midi-pan) | Spatialization from agent state position |
| [fleet-midi-echo](https://github.com/SuperInstance/fleet-midi-echo) | Acoustic echo for spatialization |
| [fleet-midi-script](https://github.com/SuperInstance/fleet-midi-script) | Scripting language for fleet MIDI composition |

---

## Spreadsheet & Spectral Ecosystem

| Repo | Relationship |
|------|-------------|
| [spectral-spreadsheet](https://github.com/SuperInstance/spectral-spreadsheet) | "The Second Moment" — a spreadsheet where formulas compute spectral graph quantities. Cells evaluate Laplacian eigenvalues, Fiedler vectors, CR, Cheeger. The output feeds directly into `evaluator.py`. |
| [ternary-spreadsheet-python](https://github.com/SuperInstance/ternary-spreadsheet-python) | Ternary spreadsheet engine in Python. Cells hold {-1,0,+1}. The ternary vectors produced by `evaluator.py` can flow into these spreadsheets for further transformation. |
| [spreadsheet-plr-bridge](https://github.com/SuperInstance/spreadsheet-plr-bridge) | Bridge between spreadsheet cells and PLR voice leading. Connects the spectral→ternary pipeline to the PLR group algebra. |
| [spreadsheet-engine](https://github.com/SuperInstance/spreadsheet-engine) | Core engine for living AI spreadsheets. Every cell can be an agent. `evaluator.py` provides the spectral→MIDI cell type. |
| [spreadsheet-formulas](https://github.com/SuperInstance/spreadsheet-formulas) | Formula language for spreadsheets — includes spectral formula primitives. |
| [superinstance-spreadsheet](https://github.com/SuperInstance/superinstance-spreadsheet) | "Excel, but alive." The flagship spreadsheet product. `evaluator.py` is one of its cell intelligence modules. |

---

## Music & Interaction

| Repo | Relationship |
|------|-------------|
| [lotka-beats](https://github.com/SuperInstance/lotka-beats) | Generative music via Lotka-Volterra dynamics. Complements spectral→MIDI with population-dynamics rhythm generation. |
| [groovemesh-plr](https://github.com/SuperInstance/groovemesh-plr) | PLR group algebra for collaborative counterpoint. The ternary voice-leading patterns from `evaluator.py` are PLR objects. |
| [tropical-synth](https://github.com/SuperInstance/tropical-synth) | Sound design via tropical geometry. Spectral graph features can drive tropical synthesis parameters. |
| [noether-guard](https://github.com/SuperInstance/noether-guard) | Physics linter — verifies conservation laws via Noether's theorem. Validates that the Conservation Ratio integrity holds across the spectral pipeline. |
| [fleet-science](https://github.com/SuperInstance/fleet-science) | Scientific research hub — papers, experiments, proofs for the SuperInstance ternary ecosystem. Contains the spectral graph→music proofs. |
| [decomp-agents](https://github.com/SuperInstance/decomp-agents) | Agent decomposition framework. Spectral graph analysis of agent networks uses this module for sonification. |

---

## Infrastructure

| Repo | Relationship |
|------|-------------|
| [construct-coordination](https://github.com/SuperInstance/construct-coordination) | Shared coordination surface between OpenClaw instances. Spectral analysis of the coordination graph feeds `evaluator.py`. |
| [fleet-arm-compat](https://github.com/SuperInstance/fleet-arm-compat) | ARM64 compatibility. `evaluator.py` is pure Python — no arch issues. The WASM kernel needs ARM-compatible WASM runtime. |

---

## Data Flow Diagram

```
Upstream                            This Module                    Downstream
═══════════                         ════════════                   ══════════

[constraint-theory-core]            [fleet-a2a-spectral]           [fleet-midi-velocity]
        │                                   │                             │
[spectral-spreadsheet]                      │                    [fleet-midi-dynamics]
        │                                   │                             │
[decomp-agents]                             │                    [fleet-midi-articulation]
        │                                   │                             │
        ▼                                   ▼                             ▼
Graph → spectral features ──→ evaluator.py ──→ MIDI notes ──→ Expressive MIDI modules
                                  │
                                  ├──→ [ternary-spreadsheet-python]
                                  ├──→ [fleet-a2a-wasm] (same invariant)
                                  └──→ [groovemesh-plr]
```

---

## Quick Links

| Purpose | Link |
|---------|------|
| All SuperInstance repos | https://github.com/SuperInstance?tab=repositories |
| This module | https://github.com/SuperInstance/fleet-a2a-spectral |
| WASM kernel (same invariant) | https://github.com/SuperInstance/fleet-a2a-wasm |
| Pipeline orchestrator | https://github.com/SuperInstance/fleet-a2a-pipeline |
| Bridge to MIDI modules | https://github.com/SuperInstance/fleet-a2a-bridge |
| Pythagorean manifold | https://github.com/SuperInstance/constraint-theory-core |
| Ternary invariants theory | https://github.com/SuperInstance/ternary-invariants |
| Spectral spreadsheet | https://github.com/SuperInstance/spectral-spreadsheet |
| Ternary spreadsheet | https://github.com/SuperInstance/ternary-spreadsheet-python |
| Fleet science (papers) | https://github.com/SuperInstance/fleet-science |
| Coordination surface | https://github.com/SuperInstance/construct-coordination |
