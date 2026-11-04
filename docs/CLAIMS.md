# Claims audit: CathodeAI README and live page

Every number in `README.md` and `docs/index.html` traced to the file that produces it, with the value obtained by
re-running `./reproduce.sh` from a clean clone on 2026-11-04 (Python 3.13, numpy 2.5, pandas 3.0, scikit-learn 1.9, scipy 1.18).
Reproduced values match the committed `revision_code/*.json` outputs to the printed precision; the JSON files differ from a
fresh run only in the 16th decimal place.

| Claim | Where it is computed | Reproduced value | Status |
|---|---|---|---|
| 2,774 Li insertion electrodes from the Materials Project | `revision_code/repro_pipeline.py:17` (`len(el)` on `mpdata/electrodes_Li.json`) | 2774 | matches |
| 16,510 Li-O structural documents | `repro_pipeline.py:17` (`len(sm)`) | 16510 | matches |
| Eight-layer funnel: 1,886 after voltage and capacity filters | `repro_pipeline.py:33` | 1886 | matches |
| 1,864 after toxic and rare-element exclusion | `repro_pipeline.py` section 5 | 1864 | matches |
| 813 oxide frameworks | `repro_pipeline.py` section 6 | 813 | matches |
| 787 with a DSI (band gap of the discharged structure available) | `analysis_dsi.py` per-material block | 787 of 813 | matches |
| 26 compositions in the discovery zone | `analysis_dsi.py` discovery-zone block | 39 rows, 26 unique formulas | matches |
| DSI classes vs 11 experimental cathodes: Spearman rho 0.76, p 0.007 | `analysis_dsi.py:20-30`; `analysis_dsi_results.json` `val.rho_bins`, `val.p_bins` | rho 0.7603, p 0.0066 | matches |
| DSI continuous score rho 0.82, p 0.002 | `val.rho_cont`, `val.p_cont` | 0.8192, 0.0020 | matches |
| Volume strain alone rho 0.55, p 0.08 | `val.rho_single`, `val.p_single` | 0.5491, 0.0802 | matches |
| Metal-identity heuristic on the same 11: rho 0.55, p 0.08 | `analysis_dsi.py:138` (metal lookup + voltage + phosphate) | rho 0.545, p 0.083 | matches |
| 10 of 11 on the correct side of the durable split | criterion from `CathodeAI_complete_pipeline.py:3410` (class B or better vs >= 500 cycles) applied to `val.cats`; `docs/build_assets.py` recomputes it | 10 of 11 (Li2MnO3 is the miss) | matches; never written as a percentage |
| Bootstrap 95 % CI [0.51, 0.93] | `analysis_dsi.py:81` | [0.509, 0.934] | matches |
| Leave-one-out: DSI ahead of the single descriptor in 11 of 11 iterations | drop-one recomputation of rho for DSI bins and the single descriptor (`docs/CLAIMS.md` check script, same definitions as `analysis_dsi.py:13-29`) | 11 of 11 | matches |
| Without LTO: rho 0.77 | `val.no_lto` | 0.7678, p 0.0095 | matches |
| 24 meV/atom hull-energy noise: median rho unchanged at 0.76 | `analysis_dsi.py` R2.21 block | median 0.760 [5-95 %: 0.585, 0.797] | matches |
| Nested leave-one-out weight fit collapses to rho 0.18 | `val.nested.rho` | 0.1805, p 0.595 | matches |
| Five of six weighting schemes beat the single-descriptor baseline | `make_figures.py:161-166` (six schemes vs 0.549) | 5 of 6 (expert 0.760, equal 0.730, vol-dominant 0.638, stab-dominant 0.751, no-band-gap 0.768 beat 0.549; no-stability 0.529 does not) | matches |
| Normalisation bounds 14.6 % and 0.190 eV/atom (95th percentiles) | `repro_pipeline.py` DSI bounds | 14.64 %, 0.1899 eV | matches |
| LiCuO2 C2/m: dV/V 46.6 %, 286 meV/atom, DSI 0.09, class D | `analysis_dsi.py` R2.19 block; `tables.json` `table5` | 46.64 %, 285.6 meV, 0.089, D | matches |
| LiCuO2 R-3m: 4.7 %, 164 meV/atom, DSI 0.46, class C | same | 4.69 %, 164.5 meV, 0.464, C | matches |
| LiCuO2 Cm: 6.6 %, 25 meV/atom, DSI 0.67, class B | same | 6.57 %, 24.7 meV, 0.667, B | matches |
| Metal-identity heuristic vs structure-based strain indicator: Pearson r 0.151 | `repro_pipeline.py` section 25-27 ("Heuristic vs physics correlation") | r 0.151, n = 569 unique formulas (from the 1,702-entry formula-level merge) | matches; the CV phrase "across 1,702 materials" is stated here as 569 formulas, which is what the code computes |
| Identifier-level merge: 1,724 entries | `analysis_ml.py` R2.15; `analysis_ml_results_id.json` `r215.n_id` | 1724 | matches |
| Energy density: 8-feature RF R2 0.95 | `analysis_ml_results_id.json` `r13."Combined (8)".random` | 0.948 | matches |
| Structural descriptors alone R2 0.36 (0.27 grouped CV) | `r13."Structural only (6)"` | 0.361 random, 0.274 grouped | matches |
| Voltage, capacity, density only: R2 0.96 | `r213."V + C + density"` | 0.961 | matches |
| Unfitted V x C x rho: R2 0.999 | `r213.arith` | 0.9990 | matches |
| 132 Magpie features: R2 0.39 | `analysis_ml2.py` Table 2 block (needs matminer); `analysis_ml2_partial_id.json` `table2."MatMiner (Magpie)"` | 0.389 (132 features) | matches |
| Five of eight "database-absent" generated candidates were known compounds | `tables.json` `novel_stats.orig_absent_now_present` | 5 entries listed | matches |
| 42 generated compositions, 1,724 known in the UMAP | `make_umap.py`; `novel_stats.n_rows` | 42; 1724 | matches |
| Pareto: LiCuO2-based entries top the composite in all five price scenarios | `analysis_dsi.py` price-scenario block | rank 1 = Li0-1CuO2 in Base, Co +100 %, Ni +50 %, Li -50 %, IRA | matches |
| Copper phosphates sit in class A | `analysis_dsi.py` Table 10 block | Li0-1CuPO4 DSI 1.00 (A), Li3-5Cu(PO4)2 0.94 (A) | matches |

## Changes made to the README in this pass

| Old text | New text | Reason |
|---|---|---|
| the withdrawn-claims bullet quoted the original polymorph cycle-life ratio by name | "The polymorph cycle-life ratio of the original release (an artefact of mapping static volume onto a strain proxy) ... are gone." | the withdrawn figure must not appear anywhere, even as a withdrawal notice |
| no statement of the heuristic-vs-structure correlation | "Pearson r = 0.151 across 569 unique formulas" | added, with the n the code actually computes |
| "Eleven materials" validation described only as rho | adds "10 of 11 on the correct side of the durable split" | reproduced from the committed categories using the original criterion |
| none | hero block linking to the live page, results table, citation block with the ChemRxiv DOI | requested structure |

## Not verifiable from the repository

- The ChemRxiv DOI (10.26434/chemrxiv.15010709/v1) and the "under revision at PCCP" status come from the CV; the repository holds the manuscript source (`revision_code/rewrite_main.py`, `esi_main.tex`) but no decision letter.
- The representative experimental cycle lives of the 11 validation cathodes (500, 2000, 300, ...) are literature values hard-coded in `analysis_dsi.py`; their sources are listed in ESI Table S1 (`esi_main.tex`).
