#!/usr/bin/env bash
# One-command reproduction of every number in README.md, docs/CLAIMS.md and docs/index.html.
# Needs: pip install -r requirements.txt   (no Materials Project API key; responses are cached in revision_code/mpdata/)
# Runtime: about 2 minutes for the pipeline and DSI analysis; analysis_ml2.py (Magpie, SHAP) adds ~10 minutes and is optional.
set -euo pipefail
cd "$(dirname "$0")/revision_code"
python repro_pipeline.py                                  # cached MP JSON -> repro_state.pkl (2,774 / 1,886 / 1,864 / 813 counts)
python analysis_ml.py                                     # formula-level ML checks; writes df_id_merge.pkl
python build_state_id.py                                  # identifier-level state -> repro_state_id.pkl
STATE=repro_state_id.pkl TAG=_id python analysis_ml.py    # identifier-level ML results (analysis_ml_results_id.json)
python analysis_dsi.py                                    # DSI validation, polymorphs, Pareto, price scenarios, discovery zone
if [ "${FULL:-0}" = "1" ]; then
  STATE=repro_state_id.pkl TAG=_id python analysis_ml2.py # Magpie / Lasso / SHAP / uncertainty (needs matminer, shap, xgboost)
  python gen_tables.py && python make_figures.py && python make_umap.py
fi
cd ..
python docs/build_assets.py                               # docs/assets/data.js, SVG figures, social preview
echo "Done. Compare the printed values with docs/CLAIMS.md."
