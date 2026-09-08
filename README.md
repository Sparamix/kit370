[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Follows IEEE 370-2020](https://img.shields.io/badge/follows-IEEE%20370--2020-green.svg)](https://standards.ieee.org/standard/370-2020.html)

# kit370: A Virtual De-embedding Kit

**A free, open-source training kit for learning fixture de-embedding.**

kit370 provides S-parameter files and worked examples that demonstrate de-embedding
concepts, pitfalls, and best practices — with no hardware purchase required.

---

> ### Not affiliated with IEEE
>
> This is an independent, unaffiliated project. It is **not** part of, produced by,
> or connected to the IEEE, the IEEE Standards Association, or the IEEE 370-2020
> working group or committee, and it has **not** been reviewed, approved, or
> endorsed by any of them. References to IEEE 370-2020 describe which published
> standard the methods here follow. They do not imply any relationship with, or
> endorsement by, IEEE or its committees.
>
> IEEE 370-2020 is a copyrighted standard and is not distributed here. Obtain it
> from IEEE. "IEEE" is a registered trademark of the Institute of Electrical and
> Electronics Engineers, Incorporated.

---

## Who is this for?

- Signal integrity engineers learning de-embedding for the first time
- Students in RF/microwave or high-speed digital courses
- Practitioners who want hands-on examples without buying a physical fixture kit

## What you get

Every structure exists at up to three levels of fidelity, and the *disagreement
between them* is part of the lesson. When an algorithm scores 0.01 dB against an
analytic model and 0.3 dB against a full-wave model of the same geometry, that gap
is the thing worth understanding.

| Tier | Source | Ground truth |
|---|---|---|
| **analytic** | Circuit models via scikit-rf | Exact by construction |
| **fullwave** | 3D FEM | Known geometry, no closed form |
| **measured** | VNA measurements | Unknown |

Generated data is committed, so you can start immediately. Every `synthesize.py` is
also runnable, so you can change the physics and watch what happens.

## Quick start

```bash
git clone https://github.com/Sparamix/kit370.git
cd kit370
pip install -r requirements.txt

cd examples/01_symmetric_good
python process.py
```

## Layout

```
kit370/
├── kit/              # Core S-parameter library, by tier
├── synthesis/        # Scripts that build the analytic tier
├── shared/           # Plotting, de-embedding and quality helpers
└── examples/         # Worked examples, one directory each
```

Each example holds a `README.md` explaining what it teaches, a `synthesize.py` to
regenerate its data, a `process.py` that de-embeds as a practitioner would, an
`analyze.ipynb` for interactive comparison, and a `data/` directory:

```
data/<tier>/
├── DUT.s2p              # Bare device, the reference
├── FIX_L.s2p            # Left fixture
├── FIX_R.s2p            # Right fixture
├── 2xTHRU.s2p           # FIX_L ** FIX_R
├── FIX_DUT_FIX.s2p      # What you would measure
└── DUT_deembedded.s2p   # Produced by process.py
```

## Pitfalls

Examples are organised around three kinds of failure, because they call for
different responses:

| Category | Nature | Example |
|---|---|---|
| **A — Design for de-embedding** | Baked in at layout; needs a respin | Fixture impedance ≠ DUT impedance |
| **B — Measurement practice** | Bench-time; fixed by re-measuring | Calibration drift, insufficient bandwidth |
| **C — Processing and algorithm** | Free to fix, if you notice | Symmetric method on an asymmetric fixture |

## Specifications

| Parameter | Value |
|---|---|
| Material | Rogers RO4003C class, NiAu plated |
| Design trace width | 17.3 mil |
| Layers | 4 |
| Analytic frequency range | 10 MHz – 67 GHz, 10 MHz steps |
| Full-wave frequency range | 100 MHz – 50 GHz, 100 MHz steps |
| Reference impedance | 50 Ω |

Analytic models include Wheeler/Hammerstad-Jensen microstrip impedance,
skin-effect conductor loss with Huray roughness correction, Djordjevic-Sarkar
causal dielectric loss, and a lumped connector launch model.

## Quality

No file enters the kit until it passes passivity, reciprocity and causality checks;
full-wave files additionally require a documented mesh-convergence study.

## Related

| Tool | Role |
|---|---|
| [scikit-rf](https://scikit-rf.org/) | Synthesis, network algebra, IEEE 370 de-embedding |
| [SQualCheck](https://github.com/Sparamix/SQualCheck) | S-parameter quality checking |
| [IEEE P370 reference code](https://gitlab.com/IEEE-SA/ElecChar/P370) | Reference implementation |
| kit370-emerge | Full-wave FEM models (GPLv2, separate repository) |

## Attribution and scope

This project distributes only its own models, scripts and results. No vendor
drawings, CAD files or documentation are redistributed, and no part of the IEEE
370-2020 standard is reproduced here. Figures are original.

The structures modelled here follow the design intent of published verification
coupons. Naming a commercial kit or a standard is descriptive only and implies no
affiliation with, sponsorship by, or endorsement from any vendor, standards body or
committee. All trademarks belong to their respective owners.

## Contributing

Contributions welcome — measured S-parameters for correlation, improved models,
additional examples, interactive notebooks.

## License

BSD 3-Clause. See [LICENSE](LICENSE).

## Contact

**Giorgi Maghlakelidze**
giorgi.snp [at] pm.me · [linkedin.com/in/giorgim](https://linkedin.com/in/giorgim)
