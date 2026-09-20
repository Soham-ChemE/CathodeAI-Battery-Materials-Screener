# Reproduction code for the revised manuscript

All numbers in the revised manuscript, ESI and figures were produced by these scripts, run in this order
(Python 3.9; numpy 2.0, pandas 2.3, scipy 1.13, scikit-learn 1.6, xgboost 2.1, shap 0.42, matminer 0.9, umap-learn 0.5):

1. `repro_pipeline.py` reproduces the original pipeline from the cached Materials Project JSON in `mpdata/`
   (2,774 electrode documents, 16,510 Li-O structural documents, 8 LiCuO2 polymorphs) and writes `repro_state.pkl`.
   The identifier-level state (`repro_state_id.pkl`) is built from `df_id_merge.pkl` produced by `analysis_ml.py`
   (see the short snippet in the response letter or rebuild with the same train/test seed 42).
2. `analysis_novel.py` regenerates the 42 compositions and re-queries the Materials Project with the correct
   stoichiometry (needs `MP_API_KEY` in the environment; the responses are cached in `mp_novel_lookup_cache.json`).
3. `analysis_ml.py` (R1.3, R2.13, R2.14, R2.15, R2.16, R2.21), `analysis_ml2.py` (Tables 2 to 4, uncertainty, novel-composition checks)
   and `analysis_dsi.py` (DSI validation extras, per-material DSI, polymorphs, phosphate ablation, Pareto, price scenarios,
   discovery zone). Run with `STATE=repro_state_id.pkl TAG=_id` for the identifier-level dataset used in the revision.
4. `gen_tables.py` writes every LaTeX table body from the analysis outputs; `make_figures.py` and `make_umap.py` regenerate all figures.

The Materials Project API key is read from the environment variable `MP_API_KEY`; it is not stored in these files.
