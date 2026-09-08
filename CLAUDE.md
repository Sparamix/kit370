# CLAUDE.md — kit370

Working context for Claude Code. Not user-facing; the public description is in
`README.md`.

---

## How to work on this project

**Plan, get approval, then implement incrementally.** Propose structure and naming
before writing code. Do not build ten examples because one was approved. Do not
refactor beyond what was asked. When a task could be interpreted broadly, ask.

This is a correction from prior sessions where the assistant over-built. It is the
single most important instruction in this file.

**Do not reinvent tools that already exist.** Quality checking belongs to
SQualCheck. Plotting helpers belong in `shared/`. If a capability seems missing,
ask before writing a replacement.

---

## Hard dependencies

`scikit-rf` is the only required library, plus numpy, scipy, matplotlib, jupyter.

Do **not** import `py370` or `octave-rf`. Both exist in the SParamix org, neither is
released or integrated. They are future cross-checks, not current dependencies.
Keep `shared/deembed.py` a thin wrapper over scikit-rf's IEEE 370 classes so a
second implementation can be swapped in later as a one-file change — do not reach
into scikit-rf internals.

`SQualCheck` is used for quality gates but has open issues against its metrics. If a
gate behaves inconsistently, fall back to the IEEE P370 reference code and note it
rather than silently working around it.

---

## Invariants

These are settled decisions. Do not change them without asking.

### File naming, per example

```
data/<tier>/
├── DUT.s2p
├── FIX_L.s2p
├── FIX_R.s2p
├── 2xTHRU.s2p            # FIX_L ** FIX_R
├── FIX_DUT_FIX.s2p       # FIX_L ** DUT ** FIX_R
└── DUT_deembedded.s2p    # written by process.py
```

Tier is `analytic`, `fullwave` or `measured`. Same filenames in every tier so
`process.py` takes a `--tier` flag and there is one code path.

Asymmetric examples use `FIX1`/`FIX2` and `2xTHRU_PCB1`/`2xTHRU_PCB2`.

### Impedance naming

- `Z_REF` — port/reference impedance for S-parameters and TDR. Always 50 Ω.
- `Z0_line` — characteristic impedance computed from geometry. Not 50 Ω.

A prior version used a single global `Z0` for both. That was a bug. Never
reintroduce it.

### Network cascade preserves metadata

The `**` operator returns a new Network and drops custom attributes:

```python
params = ntwk.params          # save first
ntwk = conn ** ntwk ** conn
ntwk.name = name
ntwk.params = params          # restore
```

### Frequency grids

| Tier | Range | Step |
|---|---|---|
| analytic | 10 MHz – 67 GHz | 10 MHz |
| fullwave | 100 MHz – 50 GHz | 100 MHz |

When comparing tiers, **resample analytic down onto the full-wave grid.** Never
interpolate full-wave data up to a denser grid — that invents points between solved
ones.

### Material

Rogers RO4003C class, NiAu plated, 17.3 mil design trace width, 4 layers.

An earlier draft used RO4350B at 22 mil. That was a guess made before the real
coupon specifications were available. It is wrong. Do not revert to it.

### Plot conventions

Magnitude solid, phase dashed. S11 magnitude y-limits `[-40, 0]` dB. TDR uses a
Kaiser window, β = 6, with 4× zero padding, x-limits `[-1, 1]` ns and y-limits
`[40, 60]` Ω.

---

## Example organisation

Two axes, deliberately.

**Spine:** the M1–M19 measurement set and E1–E8 de-embedding computations defined by
the physical kit's user guide. Following that numbering makes results directly
comparable with published committee work.

**Cross-cutting layer:** the pitfall taxonomy.

| Category | Nature | Demonstrable with |
|---|---|---|
| A — Design for de-embedding | Baked in at layout | analytic, full-wave |
| B — Measurement practice | Bench-time | measured, or injected artifacts |
| C — Processing and algorithm | Post-processing | any tier, wrong flags |

Category B mostly **cannot** be shown with clean simulation. Either use measured
data or inject the artifact — and if injecting, state the assumption explicitly in
the example's README. This makes the measured-data example load-bearing.

---

## External datasets

The IEEE P370 TG2 verification library (≈500 Touchstone files, ~374 MB) covers
impedance mismatch, via/stub variants and port reordering better than we would
build them.

**Do not vendor it into this repository.** Redistribution terms are unstated. Use a
fetch script with SHA-256 checksums and document the directory structure so the
description survives link rot.

Likewise: no vendor PDFs, no vendor DXF files, ever. Dimensions and material
properties are facts and may be used. The documents are not ours to redistribute.

---

## Current state

`synthesis/generate_kit.py` works — builds 3 cm and 6 cm microstrip DUTs with
Wheeler impedance, skin-effect and Huray roughness, Djordjevic-Sarkar dielectric
loss, a lumped connector model, and Kaiser-windowed TDR. Passes passivity and
reciprocity.

Not yet done: `synthesis/utils.py` has not been extracted from `generate_kit.py`;
`shared/` does not exist; no examples are built.

---

## Task order

1. Extract `synthesis/utils.py` from `generate_kit.py` — the geometry and network
   primitives that each example's `synthesize.py` will import.
2. Create `shared/plotting.py`, `shared/deembed.py`, `shared/quality.py`.
3. Example 01, symmetric good reference — establishes the pattern for all others.
4. Example 02, asymmetric two-PCB mezzanine, with its own 2x-thru per board.
5. Remaining examples, in taxonomy order.
6. Fetch script and documentation for the P370 TG2 library.

Stop after each numbered step and check in.

---

## Environment

Linux, Spyder and VS Code. Repository root is the working directory for scripts
unless a script states otherwise.

Committed `data/` files are the product, not build artifacts — they belong in git.
Keep individual files reasonable; a 67 GHz sweep at 10 MHz steps is roughly 1.2 MB
per `.s2p`.
