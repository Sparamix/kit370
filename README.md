[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![IEEE 370](https://img.shields.io/badge/IEEE-370--2020-green.svg)](https://standards.ieee.org/standard/370-2020.html)

# openSNPKit370: Virtual IEEE P370 De-embedding Kit

**A free, open-source training kit for learning fixture de-embedding.**

This library provides synthesized S-parameter files demonstrating de-embedding concepts, pitfalls, and best practices..

Part of the [OpenSNPTools](https://github.com/OpenSNPTools) ecosystem.

---

## 🎯 Who Is This For?

- **Signal integrity engineers** learning de-embedding for the first time
- **Students** in RF/microwave or high-speed digital courses  
- **Practitioners** who want hands-on examples without buying expensive test fixtures

---

## 📦 What's Included

### Virtual P370 Kit (`kit/`)

| File | Description | Equivalent P370 Board |
|------|-------------|----------------------|
| `dut_microstrip_6cm.s2p` | 6cm bare microstrip (ground truth) | Board #1 |
| `dut_microstrip_3cm.s2p` | 3cm bare microstrip | Board #1a |
| `2xthru_50ohm_6cm.s2p` | 6cm 2x-THRU, 50Ω nominal | Board #2 |
| `2xthru_52ohm_6cm.s2p` | 6cm 2x-THRU, 52.5Ω (105% Z₀) | Board #3 |
| `fixture_with_vias.s2p` | Fixture with via transitions | Board #4 |
| `beatty_50_25_50.s2p` | Beatty impedance standard | Board #5 |

### Pitfall Examples (`examples/`)

| # | Pitfall | What Goes Wrong |
|---|---------|-----------------|
| 01 | Good Reference | Baseline: what "correct" looks like |
| 02 | Impedance Mismatch | ±5% Z₀ causes 1-2 dB ripple |
| 03 | Poor Return Loss | RL < IL violates 5 dB rule → noise amplification |
| 04 | Non-Causal | Phase error → "ghost limbs" in TDR |
| 05 | Mode Conversion | Differential asymmetry → Scd/Sdc artifacts |
| 06 | Port Ordering | (1,3)/(2,4) vs (1,2)/(3,4) confusion |
| 07 | Calibration Drift | Thermal drift → passivity violations |
| 08 | Bandwidth Truncation | Measuring to 28 GHz for 25 Gbps → ringing |
| 09 | Wrong Algorithm | Symmetric method on asymmetric fixture |
| 10 | Microprobing | De-embed GSG probes (alt to $15K ISS cal) |
| 11 | Measured Striplines | Real-world data for correlation. We hope to build up a dataset over time! |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/OpenSNPTools/openSNPKit370.git
cd openSNPKit370

# Install dependencies
pip install -r requirements.txt

# Run your first example
cd examples/01_good_reference
python example_01.py
```

---

## 📁 Repository Structure

```
openSNPKit370/
├── README.md
├── LICENSE                      # BSD-3-Clause
├── requirements.txt
├── CHANGELOG.md
│
├── kit/                         # Virtual P370 S-parameter files
│   ├── README.md
│   ├── dut_microstrip_6cm.s2p
│   ├── dut_microstrip_3cm.s2p
│   ├── 2xthru_50ohm_6cm.s2p
│   ├── 2xthru_52ohm_6cm.s2p
│   ├── fixture_with_vias.s2p
│   └── beatty_50_25_50.s2p
│
├── examples/                    # Pitfall demonstrations
│   ├── 01_good_reference/
│   ├── 02_impedance_mismatch/
│   ├── 03_poor_return_loss/
│   ├── 04_noncausal/
│   ├── 05_mode_conversion/
│   ├── 06_port_ordering/
│   ├── 07_calibration_drift/
│   ├── 08_bandwidth_truncation/
│   ├── 09_wrong_algorithm/
│   ├── 10_microprobing/
│   └── 11_measured_striplines/
│
├── synthesis/                   # Scripts that generate the kit
│   └── generate_kit.py
│
└── docs/
    ├── pitfall_guide.md
    ├── theory_review.md
    └── figures/
```

---

## 🔧 Technical Specifications

### PCB Parameters (P370-equivalent)

| Parameter | Value |
|-----------|-------|
| **Material** | Rogers RO4350B-equivalent (Dk=3.48, Df=0.0037) |
| **Frequency** | 10 MHz – 67 GHz |
| **Trace geometry** | ~22 mil width on 10 mil dielectric → 50Ω |
| **Copper** | 1 oz (35 µm) with surface roughness |
| **Via model** | Pi-network (L ≈ 80 pH, C ≈ 35 fF) --> TBD!! |
| **Connector** | 1.85mm end-launch model |

### Realism Features --> ALL THIS TBD!!

- ✅ Frequency-dependent conductor loss (skin effect)
- ✅ Dielectric loss (Djordjevic-Sarkar model)
- ✅ Surface roughness (Huray model)
- ✅ Via resonances and parasitics
- ✅ Connector discontinuities
- ✅ Measurement noise floor (~-60 dB)

---

## 📊 The 10 Pitfalls — Detailed

### 01. Good Reference (Baseline)
**Purpose:** Establish what "correct" looks like  
**Expected results:**
- IL: -0.5 dB @ 10 GHz, -1.5 dB @ 50 GHz
- RL: < -25 dB across band
- Self-deembed residual: < 0.05 dB

### 02. Impedance Mismatch
**Purpose:** Show ripple from ±5% manufacturing tolerance  
**Setup:** 50Ω 2x-THRU with 52.5Ω fixture  
**Symptom:** 1-2 dB ripple, standing waves  
**Lesson:** Match your 2x-THRU impedance to your fixture

### 03. Poor Return Loss
**Purpose:** "Cannot see through a wall" failure  
**Setup:** Fixture with RL = -8 dB, IL = -10 dB  
**Symptom:** Noise amplification, passivity violations  
**Lesson:** Maintain RL - IL ≥ 5 dB headroom

### 04. Non-Causal
**Purpose:** Show "ghost limbs" from phase error  
**Setup:** Add 15° phase error (simulates connector mismatch)  
**Symptom:** Pre-cursor energy in TDR (t < 0)  
**Lesson:** Verify causality before trusting magnitude

### 05. Mode Conversion
**Purpose:** Show Scd/Sdc artifacts from asymmetry  
**Setup:** One trace 0.5mm longer in differential pair  
**Symptom:** Scd, Sdc rise from -40 dB to -25 dB  
**Lesson:** Balance your differential fixtures

### 06. Port Ordering
**Purpose:** Convention confusion  
**Setup:** Same fixture, different port numbering  
**Symptom:** Sdd21 shows zero, signal in wrong S-param  
**Lesson:** Document and verify port conventions

### 07. Calibration Drift
**Purpose:** Show thermal degradation  
**Setup:** T=0 (fresh cal) vs T=60 min (drifted)  
**Symptom:** Directivity drops 50→35 dB, RL degrades  
**Lesson:** Re-calibrate, especially for sensitive measurements

### 08. Bandwidth Truncation
**Purpose:** Show artifacts from insufficient frequency range  
**Setup:** Measured to 28 GHz vs 40 GHz for 25 Gbps  
**Symptom:** Time-domain ringing, causality issues  
**Lesson:** Measure 10% beyond your target frequency

### 09. Wrong Algorithm
**Purpose:** Symmetric method on asymmetric fixture  
**Setup:** Via fixture with different left/right lengths  
**Symptom:** > 1 dB self-deembed residual  
**Lesson:** Use NZC (non-zero-centered) for asymmetric fixtures

### 10. Microprobing
**Purpose:** De-embed as alternative to expensive ISS cal substrates  
**Setup:** GSG probe-to-probe THRU + probe-DUT-probe  
**Result:** Removes pad parasitics, reveals structure
**Lesson:** de-embedding could be an easier path than ISS 

---

## 🔗 Related Tools

| Tool | Description |
|------|-------------|
| [openSNPQual](https://github.com/OpenSNPTools/openSNPQual) | S-parameter quality checker (passivity, reciprocity, causality) |
| [openSNPlot](https://github.com/OpenSNPTools/openSNPlot) | S-parameter visualization |
| [scikit-rf](https://scikit-rf.org/) | Python RF/microwave library |
| [IEEE 370 Reference Code](https://opensource.ieee.org/elec-char/ieee-370/) | Official MATLAB implementation |

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ideas for contributions:
- Add measured S-parameters (anonymized) for comparison
- Improve synthesis models
- Add more pitfall examples
- Create interactive Jupyter notebooks
- Translate documentation

---

## 📄 License

BSD 3-Clause License — see [LICENSE](LICENSE).

Free to use, modify, and distribute. Attribution appreciated.

---

## 📚 References

- IEEE 370-2020: "Electrical Characterization of Printed Circuit Board and Related Interconnects up to 50 GHz"
- IPC-2141A: "Design Guide for High-Speed Controlled Impedance Circuit Boards"
- Keysight App Note 5989-5765EN: "The ABCs of De-Embedding"
- [scikit-rf documentation](https://scikit-rf.readthedocs.io/)

---

## 📧 Contact

**Author:** Giorgi Maghlakelidze  
**Email:** giorgi.snp [at] pm.me  
**LinkedIn:** [linkedin.com/in/giorgim](https://linkedin.com/in/giorgim)  
**Issues:** [GitHub Issues](https://github.com/OpenSNPTools/openSNPKit370/issues)

---

Made with ❤️ for the Signal Integrity Community
