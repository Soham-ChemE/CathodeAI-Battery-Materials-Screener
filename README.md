# CathodeAI: A Structure-Aware Screening Framework for Li-ion Battery Cathodes

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Data: Materials Project](https://img.shields.io/badge/Data-Materials%20Project-green)](https://materialsproject.org)
[![ML: scikit-learn](https://img.shields.io/badge/ML-scikit--learn%20%7C%20SHAP-orange)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

**Author:** Soham Kavathekar, MS Chemical & Biomolecular Engineering, University of Pennsylvania
**Contact:** stg3719@seas.upenn.edu · [LinkedIn](https://www.linkedin.com/in/soham-kavathekar-72a22b246)

---

## What this project is

CathodeAI is a reproducible computational pipeline that screens **2,774 lithium-ion insertion-electrode entries** from the Materials Project database and ranks cathode candidates on three simultaneous axes: energy density, structural durability and supply-chain criticality.

Its central finding is a scientific one, not a software one:

> **Composition-level heuristics (rules of thumb based on which transition metal a cathode contains) become unreliable once crystal structure and multiple competing objectives are taken into account. Structure-derived descriptors provide a consistently more informative basis for screening.**

Everything in this repository is built to support, test and quantify that claim. The framework is deliberately scoped as a **screening and prioritization tool**, not a first-principles predictor. See [Scope & Limitations](#scope--limitations), which is the most important section to read before drawing conclusions from any number here.

![Feature set comparison](cathodeai_feature_engineering.png)

*Structure-informed features (8) reach R² = 0.942 for energy-density prediction, outperforming 83 purely compositional descriptors (R² = 0.413).*

---

## The four lines of evidence

| # | Finding | Evidence |
|---|---------|----------|
| 1 | **Composition heuristics reach a predictive limit.** | Metal-identity cycle-life heuristics show essentially no correlation with structure-based degradation indicators (Pearson **r = 0.151**). Identical LiCuO₂ compositions vary **~7-fold** in predicted durability across crystal polymorphs (a 28% spread in volume per atom). |
| 2 | **Structure improves property prediction.** | Eight physics-informed structural features reach **R² = 0.942** (5-fold CV) for volumetric energy density, versus **R² = 0.413** for 83 Lasso-selected compositional descriptors. Compositional feature spaces saturate; structure-grounded ones do not. |
| 3 | **Structure improves degradation ranking.** | A transparent, structurally-grounded Degradation Screening Index (DSI) ranks experimental durability at **Spearman ρ = 0.760** (p = 0.007) vs **ρ = 0.549** (p = 0.080, not significant) for a single volume-strain descriptor, across 11 well-characterized cathodes. |
| 4 | **Multi-objective screening changes outcomes.** | Pareto analysis over energy density, stability and supply-chain criticality shows **no single material is universally optimal**; each application has a distinct frontier. |

The conclusion is model-agnostic: it is about *which descriptors carry the signal*, not about a specific machine-learning algorithm.

---

## Headline reproducible results

All values below are produced by running the notebook end-to-end (see [Reproducing the results](#reproducing-the-results)).

**Machine learning: volumetric energy density (Wh/L)**

Feature-set comparison (5-fold CV, Random Forest):

| Feature set | R² (mean) | R² (std) | # features |
|---|---|---|---|
| Electrochemical only | 0.857 | 0.019 | 4 |
| Structural only (DFT) | 0.364 | 0.024 | 6 |
| **Combined (final)** | **0.942** | **0.056** | **8** |
| MatMiner (Magpie) | 0.413 | 0.016 | 132 |
| Lasso-selected | 0.413 | 0.017 | 83 |
| Full (combined + MatMiner) | 0.937 | 0.055 | 140 |

Model comparison on the combined 8-feature set (5-fold CV):

| Model | R² (mean) | R² (std) | MAE (Wh/L) |
|---|---|---|---|
| Linear Regression | 0.930 | 0.015 | 153.99 |
| **Random Forest (selected)** | **0.942** | **0.056** | **101.97** |
| XGBoost | 0.945 | 0.046 | 104.28 |
| Neural Network | 0.976 | 0.010 | 84.46 |

> **Note on model choice (this is deliberate, not an oversight).** The neural network attains the highest cross-validation R². Random Forest was nonetheless selected as the production model because its native, well-calibrated impurity importances and exact TreeSHAP attribution are essential to the interpretability analysis at the core of this work, and the accuracy gap (0.034 in R²) is small relative to prediction uncertainty. Held-out test-set performance for the final model: **R² = 0.966, MAE = 92.9 Wh/L (single held-out split)**.

**Interpretability (SHAP, final model)**

Capacity dominates energy-density prediction (mean |SHAP| = 602 Wh/L; Random Forest impurity importance ≈ **78.5%**), consistent with the thermodynamic definition of volumetric energy density, a useful sanity check that the model has learned the physics rather than a spurious correlation.

**Degradation Screening Index (DSI)**

- Spearman ρ = **0.760** (p = 0.007); single-descriptor baseline ρ = 0.549 (p = 0.080, not significant)
- Binary screening accuracy **90.9%** (10/11 materials correctly classified)
- Robust across six weighting schemes (ρ ∈ [0.529, 0.768]) and all 11 leave-one-out iterations
- Descriptor independence confirmed on the full dataset (ΔV/V vs delithiated-phase E_hull: r = −0.005, n = 2,035)

**Uncertainty quantification (RF ensemble, held-out test set)**

- Empirical 95% prediction-interval coverage: **95.6%** (well-calibrated; ideal 95%)
- Mean uncertainty ±308 Wh/L; uncertainty rises with capacity (r = 0.555), reflecting sparser training data in the high-capacity regime

**Screening & discovery**

- 2,774 entries → an 8-layer pipeline → **12-15** high-value discovery-zone candidates
- **42** charge-balanced hypothetical compositions generated; **27/42** pass the synthesizability screen; **8** are genuinely absent from the Materials Project database (verified via API) and constitute the exploratory candidate set
- LiCuO₂-based compositions retain top composite ranking across all **5** commodity-price scenarios

---

## Methodology

### Data
2,774 Li insertion-electrode entries + 16,510 Li-containing structural entries, queried from the Materials Project via `mp-api`. All DFT thermodynamic/electrochemical properties use the `MaterialsProject2020Compatibility` correction scheme.

### Eight-layer screening pipeline

| Layer | Criterion | Industrial relevance |
|---|---|---|
| 1 | Voltage window (2.5-5.0 V) | Electrolyte stability / high-voltage solid-state |
| 2 | Capacity ≥ 50 mAh/g | Minimum practical performance |
| 3 | Oxide framework | Reversible intercalation redox |
| 4 | Toxicity exclusion (Pb, Cd, Hg) | RoHS / REACH compliance |
| 5 | Supply-chain criticality (HHI + IRA) | Sourcing risk |
| 6 | Recyclability | Hydrometallurgical recovery |
| 7 | Thermal safety | Oxygen-release onset proxy |
| 8 | Degradation Screening Index | Structure-aware durability ranking |

### The Degradation Screening Index (DSI)

A transparent composite of three structure-derived descriptors, each tied to an independent degradation pathway:
DSI = 0.50·S_strain + 0.35·S_stability + 0.15·S_bandgap + 0.10·1_phosphate   (capped at 1.0)


The descriptor **weights are expert-assigned, not learned**. The DSI is presented honestly as a structurally-grounded *screening heuristic*, whose advantage over composition-based heuristics is that it operates on structure-resolved state variables. Its value is demonstrated empirically (improved rank-order agreement with experiment), not asserted mechanistically. Normalization bounds are fixed on the 2,774-material training distribution, independent of the 11-material validation set.

![DSI validation](cathodeai_expanded_validation.png)

*The multi-descriptor DSI (Spearman ρ = 0.760) ranks experimental cycle life across 11 cathodes better than a single volume-strain descriptor (ρ = 0.549).*

### Novel-composition generator (exploratory)

A charge-balance enumeration over transition metals, oxidation states and Li content, with energy density estimated from empirical voltage/capacity relations. **This is methodologically separate from the supervised ML model**, which is applied only to structure-resolved database materials. Generated compositions are screening-level priors for future first-principles evaluation, not validated discoveries.

---

## Repository structure
CathodeAI-Battery-Materials-Screener/
├── README.md
├── LICENSE
├── requirements.txt
├── CathodeAI_complete_pipeline.py      # Full 53-section pipeline (Colab-ready)
├── CathodeAI_complete_clean.ipynb      # Notebook with rendered outputs
└── cathodeai_*.png                     # Generated figures

---

## Reproducing the results

```bash
git clone https://github.com/Soham-ChemE/CathodeAI-Battery-Materials-Screener.git
cd CathodeAI-Battery-Materials-Screener
pip install -r requirements.txt
```

1. Obtain a free Materials Project API key: https://materialsproject.org/api
2. Set it as an environment variable: `export MP_API_KEY="your_key_here"`
3. Run the pipeline sections in order (designed as sequential Colab cells).

The pipeline is organized into 53 numbered sections (setup → screening layers → ML → interpretability → DSI validation). Each is self-contained and runs in order.

---

## Scope & limitations

This section is intentionally prominent. The framework is useful precisely because its boundaries are stated clearly.

- **The DSI is a screening heuristic, not a mechanistic model.** Its weights are expert-assigned. It is validated on *rank order* across major structural classes, not on absolute cycle counts. It is most reliable in the volume-change-dominated regime (olivines, polyanionic frameworks; prediction error 10-47%) and is treated as outside its applicability domain for layered oxides, where phase transformation and surface reactivity dominate.
- **The experimental validation set is small (n = 11).** Leave-one-out and bootstrap analyses show the result is internally stable and not driven by any single material, but a set this size cannot establish generalization to chemistries outside it. Expanding the experimental validation set is the primary next step.
- **Generated "novel" compositions are exploratory.** They have no resolved crystal structure; their energy densities are empirical screening estimates, not first-principles predictions. They identify *where to look next* and require DFT relaxation and convex-hull placement before any claim of viability.
- **All energy-density values are theoretical** (100% depth of discharge, active material only); practical cell-level values are lower.
- **DFT inputs inherit GGA+U systematic errors** (~0.1-0.3 V in redox potentials). These are approximately uniform shifts and do not affect the relative rankings that drive the conclusions.

---

## Related work

A manuscript describing this framework in full, including the complete Degradation Screening Index validation, bootstrap and leave-one-out analyses and the heuristic-invalidation result, is in preparation. This repository contains the complete, runnable pipeline behind it.

---

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Built on the open-access [Materials Project](https://materialsproject.org) DFT database (Lawrence Berkeley National Laboratory). Descriptor generation uses [matminer](https://hackingmaterials.lbl.gov/matminer/); interpretability uses [SHAP](https://github.com/shap/shap).









