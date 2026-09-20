"""Generate LaTeX table bodies from the analysis outputs (no hand transcription)."""
import json, pickle, re, os
import numpy as np, pandas as pd
R = json.load(open("analysis_dsi_results.json")); ML = json.load(open("analysis_ml_results_id.json")); MLF = json.load(open("analysis_ml_results.json"))
ML2 = json.load(open("analysis_ml2_results_id.json")) if os.path.exists("analysis_ml2_results_id.json") else None
XGB = json.load(open("xgb_id.json")); U = json.load(open("fig21_numbers.json"))
st = pickle.load(open("repro_state_id.pkl", "rb")); df = pd.read_pickle("df813_dsi.pkl"); nv = pd.read_csv("novel_compositions_recheck.csv")
T = {}
def mp(f):
    f = re.sub(r"^Li([\d\.]+)-([\d\.]+)", r"Li$_{\1\\text{--}\2}$", f)
    return re.sub(r"(?<=[A-Za-z\)])(\d+)", r"$_{\1}$", f)
def cat_short(c): return c.split(" ")[0]

# ---- Table 2 (feature sets) ----
if ML2:
    t2 = ML2["table2"]; rows = []
    for k, lab in [("Electrochemical only", "Electrochemical only"), ("Structural only (DFT)", "Structural only (DFT)"), ("Combined (final)", "\\textbf{Combined (final)}"), ("MatMiner (Magpie)", "MatMiner (Magpie)"), ("Lasso-selected", "Lasso-selected MatMiner"), ("Full (combined + MatMiner)", "Full (combined + MatMiner)")]:
        r = t2[k]; bold = "Combined" in k
        c1 = "%.3f $\\pm$ %.3f" % (r["r2"], r["std"]); c2 = "%.3f $\\pm$ %.3f" % (r["r2g"], r["stdg"]); c3 = str(r["nfeat"])
        if bold: c1, c2, c3 = ["\\textbf{%s}" % c for c in (c1, c2, c3)]
        rows.append("%s & %s & %s & %s \\\\" % (lab, c1, c2, c3))
    b = ML["r213"]
    rows.append("\\hline")
    rows.append(f"$V$, $C$ only (RF) & {b['V + C only'][0]:.3f} $\\pm$ {b['V + C only'][1]:.3f} & -- & 2 \\\\")
    rows.append(f"$V$, $C$, $\\rho$ only (RF) & {b['V + C + density'][0]:.3f} $\\pm$ {b['V + C + density'][1]:.3f} & -- & 3 \\\\")
    rows.append(f"$\\log V$, $\\log C$, $\\log\\rho$ (linear) & {b['V + C + density (linear on log)'][0]:.3f} $\\pm$ {b['V + C + density (linear on log)'][1]:.3f} & -- & 3 \\\\")
    rows.append(f"$V \\times C \\times \\rho$ (no fitting) & {b['arith']:.3f} & -- & 3 \\\\")
    T["table2"] = "\n".join(rows)
    # Table 3
    t3 = ML2["table3"]; rows = []
    for k, lab, vals in [("Linear Regression", "Linear Regression", t3["Linear Regression"]), ("Random Forest", "\\textbf{Random Forest (selected)}", t3["Random Forest"]), ("XGBoost", "XGBoost", XGB), ("Neural Network", "Neural Network", t3["Neural Network"])]:
        cells = ["%.3f" % vals["r2"], "%.3f" % vals["std"], "%.1f" % vals["mae"], "%.3f" % vals["r2g"], "%.1f" % vals["maeg"]]
        if "Random" in k: cells = ["\\textbf{%s}" % c for c in cells]
        rows.append(lab + " & " + " & ".join(cells) + " \\\\")
    T["table3"] = "\n".join(rows)
    # Table 4 SHAP
    sh = ML2["shap"]; names = {"Capacity (mAh/g)": "Capacity (mAh~g$^{-1}$)", "Avg Voltage (V)": "Avg.\\ voltage (V)", "Density (g/cc)": "Density (g~cm$^{-3}$)", "Volume per Atom (A3)": "Volume per atom (\\AA$^3$)", "Formation Energy (eV/atom)": "Formation energy (eV~atom$^{-1}$)", "Band Gap (eV)": "Band gap (eV)", "Energy Above Hull (eV)": "Energy above hull (eV~atom$^{-1}$)", "N Elements": "$N$ elements"}
    rows = [f"{names[k]} & {v['mean_abs_shap']:.2f} & {v['rf_importance']*100:.1f} \\\\" for k, v in sorted(sh.items(), key=lambda kv: -kv[1]["mean_abs_shap"])]
    T["table4"] = "\n".join(rows)

# ---- Table 5 polymorphs (static + electrode-resolved) ----
dp = st["df_poly"].sort_values("E_hull (meV/atom)"); pe = {r["polymorph_id"]: r for r in R["polymorph"]}
rows = []
for _, r in dp.iterrows():
    sg = r["Space Group"].replace("-3", "$\\bar{3}$").replace("-1", "$\\bar{1}$"); bg = f"{r['Band Gap (eV)']:.2f}"
    if r["material_id"] in pe:
        e = pe[r["material_id"]]
        rows.append(f"{sg} & {r['E_hull (meV/atom)']:.1f} & {r['Vol/atom']:.2f} & {r['Density']:.2f} & {bg} & {mp(e['battery_formula'])} & {e['dV/V (%)']:.1f} & {e['E_hull charge (eV)']*1000:.0f} & {e['DSI']:.2f} & {cat_short(e['DSI category'])} \\\\")
    else:
        rows.append(f"{sg} & {r['E_hull (meV/atom)']:.1f} & {r['Vol/atom']:.2f} & {r['Density']:.2f} & {bg} & -- & -- & -- & -- & -- \\\\")
T["table5"] = "\n".join(rows)

# ---- Table 7 validation with categories ----
val_struct = {"LiCoO2": "Layered", "LiFePO4": "Olivine", "LiMnO2": "Layered", "NMC111": "Layered", "NMC622": "Layered", "NMC811": "Layered", "NCA": "Layered", "LNMO": "Spinel", "LTO": "Spinel", "LFMP": "Olivine", "Li2MnO3": "Layered"}
val_exp = {"LiCoO2": 500, "LiFePO4": 2000, "LiMnO2": 300, "NMC111": 1000, "NMC622": 800, "NMC811": 800, "NCA": 500, "LNMO": 1000, "LTO": 10000, "LFMP": 1500, "Li2MnO3": 200}
val_vol = {"LiCoO2": 2.0, "LiFePO4": 6.81, "LiMnO2": 16.0, "NMC111": 2.5, "NMC622": 4.0, "NMC811": 4.0, "NCA": 5.0, "LNMO": 2.5, "LTO": 0.1, "LFMP": 5.0, "Li2MnO3": 8.0}
def cat(d): return "D" if d < 0.35 else "C" if d < 0.55 else "B" if d < 0.75 else "A"
def scat(v): return "A" if v < 3 else "B" if v < 7 else "C" if v < 12 else "D"
disp = {"LiCoO2": "LiCoO$_2$", "LiFePO4": "LiFePO$_4$", "LiMnO2": "LiMnO$_2$", "LFMP": "LiFe$_{0.5}$Mn$_{0.5}$PO$_4$", "Li2MnO3": "Li$_2$MnO$_3$", "LTO": "LTO$^\\ast$"}
heur = R["heur_val"]["preds"]
rows = []
for m in val_exp:
    s = R["val"]["scores"][m]; rows.append(f"{disp.get(m, m)} & {val_struct[m]} & {val_exp[m]:,} & {heur[m]:,} & {scat(val_vol[m])} & {s:.3f} & {cat(s)} \\\\")
T["table7"] = "\n".join(rows)

# ---- Table 8 PO4 ----
rw = R["r220"]["rows"]
def prow(lab, k, fmt="{:.3f}"):
    a, b, p = rw[k][0], rw[k][1], rw[k][2]; ps = f"{p:.1e}".replace("e-0", "e-").replace("e-", "\\times10^{-") + "}$" if p < 1e-3 else f"{p:.3f}$"
    return f"{lab} & {fmt.format(a)} & {fmt.format(b)} & ${'<' if False else ''}{ps} \\\\" if p < 1e-3 else f"{lab} & {fmt.format(a)} & {fmt.format(b)} & ${p:.3f}$ \\\\"
def pfmt(p):
    if p < 1e-3:
        e = int(np.floor(np.log10(p))); m = p / 10 ** e; return f"${m:.1f}\\times10^{{{e}}}$"
    return f"${p:.3f}$"
rows = []
for lab, k, fmt in [("Thermal safety score (with $+0.15$ PO$_4$ bonus)", "Thermal Safety Score", "{:.3f}"), ("Thermal safety score (bonus removed)", "Thermal Safety Score (no PO4 bonus)", "{:.3f}"),
                    ("DSI (with $+0.10$ PO$_4$ bonus)", "DSI", "{:.3f}"), ("DSI (bonus removed)", "DSI (no PO4 bonus)", "{:.3f}"),
                    ("$\\Delta V/V$ (\\%)", "Max Volume Change (%)", "{:.2f}"), ("$E_\\text{hull,charge}$ (eV~atom$^{-1}$)", "Stability Charge (eV)", "{:.3f}"),
                    ("Energy density (Wh~L$^{-1}$)", "Energy Density (Wh/L)", "{:.0f}"), ("Solid-state score", "Solid State Score", "{:.3f}")]:
    a, b, p, pu = rw[k][0], rw[k][1], rw[k][2], rw[k][3]
    rows.append(f"{lab} & {fmt.format(a)} & {fmt.format(b)} & {pfmt(p)} & {pfmt(pu)} \\\\")
T["table8"] = "\n".join(rows); T["po4_n"] = (R["r220"]["n_po4"], R["r220"]["n_non"])

# ---- Table 9 novel (database-absent, correct stoichiometry) ----
ab = nv[~nv["in_db_correct"]].drop_duplicates("Reduced formula").sort_values("Predicted ED 4-feature RF (Wh/L)", ascending=False)
sc = {"Fe": 0.05, "Mn": 0.30, "Ni": 0.55, "Co": 0.95, "Cu": 0.25, "Ti": 0.20, "V": 0.45}
rows = []
for _, r in ab.iterrows():
    ox = int(r["Oxidation State"]); rows.append(f"{mp(r['Reduced formula'])} & {r['Metal']}$^{{{ox}+}}$ & {r['Avg Voltage (V)']:.2f} & {r['Capacity (mAh/g)']:.0f} & {r['Predicted ED 4-feature RF (Wh/L)']:.0f} & {1-sc[r['Metal']]:.2f} \\\\")
T["table9"] = "\n".join(rows); T["n_absent"] = len(ab)
pres = nv[nv["in_db_correct"]].drop_duplicates("Reduced formula")
T["novel_stats"] = {"n_rows": len(nv), "n_unique": int(nv["Reduced formula"].nunique()), "n_present_unique": len(pres), "n_present_rows": int(nv["in_db_correct"].sum()), "lt50_unique": int((pres.ehull_meV_correct < 50).sum()),
                    "onhull_unique": int((pres.ehull_meV_correct < 1e-6).sum()), "mid_unique": int(((pres.ehull_meV_correct >= 50) & (pres.ehull_meV_correct < 100)).sum()), "lt50_rows": int((nv.ehull_meV_correct < 50).sum()),
                    "absent": sorted(ab["Reduced formula"]), "ed_min": float(nv["Predicted ED 4-feature RF (Wh/L)"].min()), "ed_max": float(nv["Predicted ED 4-feature RF (Wh/L)"].max()),
                    "orig_absent_now_present": [(o, c, round(e, 1)) for o, c, e in zip(nv["Original query formula"], nv["Reduced formula"], nv["ehull_meV_correct"]) if o in ["LiCu2O3", "LiTi2O5", "LiVO4", "LiTiO3", "LiMn2O5", "LiCoO3", "LiNi2O5", "LiV2O6"] and not np.isnan(e)]}

# ---- Table 10 ----
rows = []
for i, r in enumerate(R["table10"], 1):
    rows.append(f"{i} & {mp(r['Formula'])} & {r['Avg Voltage (V)']:.3f} & {r['Energy Density (Wh/L)']:.0f} & {r['Cost per kWh ($/kWh)']:.0f} & {r['Max Volume Change (%)']:.1f} & {r['Stability Charge (eV)']:.3f} & {r['DSI']:.2f} & {cat_short(r['DSI category'])} & {r['Composite (DSI term)']:.3f} \\\\")
T["table10"] = "\n".join(rows)

# ---- ESI S1 (validation descriptors + DSI) ----
srcs = {"LiCoO2": "Mizushima1980,Reimers1992", "LiFePO4": "Padhi1997", "LiMnO2": "Armstrong1996", "NMC111": "Jung2017", "NMC622": "Jung2017,Liu2015", "NMC811": "Liu2015", "NCA": "Watanabe2014", "LNMO": "Zhong1997", "LTO": "Ohzuku1995", "LFMP": "Padhi1997,Bramnik2007", "Li2MnO3": "Kalyani1999"}
authyr = {"LiCoO2": "Mizushima 1980; Reimers 1992", "LiFePO4": "Padhi 1997", "LiMnO2": "Armstrong 1996", "NMC111": "Jung 2017", "NMC622": "Jung 2017; Liu 2015", "NMC811": "Liu 2015", "NCA": "Watanabe 2014", "LNMO": "Zhong 1997", "LTO": "Ohzuku 1995", "LFMP": "Padhi 1997; Bramnik 2007", "Li2MnO3": "Kalyani 1999"}
vst = {"LiCoO2": (0.02, 0.00, "No"), "LiFePO4": (0.00, 3.59, "Yes"), "LiMnO2": (0.05, 0.00, "No"), "NMC111": (0.03, 1.50, "No"), "NMC622": (0.04, 1.20, "No"), "NMC811": (0.06, 0.80, "No"), "NCA": (0.08, 0.70, "No"), "LNMO": (0.02, 2.00, "No"), "LTO": (0.00, 2.72, "No"), "LFMP": (0.00, 3.50, "Yes"), "Li2MnO3": (0.10, 1.32, "No")}
dispE = {"LiCoO2": "LiCoO\\textsubscript{2}", "LiFePO4": "LiFePO\\textsubscript{4}", "LiMnO2": "LiMnO\\textsubscript{2}", "LFMP": "LiFe\\textsubscript{0.5}Mn\\textsubscript{0.5}PO\\textsubscript{4}", "Li2MnO3": "Li\\textsubscript{2}MnO\\textsubscript{3}"}
rows = []
for m in val_exp:
    s = R["val"]["scores"][m]; rows.append(f"{dispE.get(m, m)} & {val_exp[m]:,} & {val_vol[m]} & {vst[m][0]:.2f} & {vst[m][1]:.2f} & {vst[m][2]} & {s:.3f} & {cat(s)} & {authyr[m]} & \\cite{{{srcs[m]}}} \\\\")
T["esi_s1"] = "\n".join(rows)

# ---- ESI S3: all 42 generated compositions, item-by-item ----
rows = []
for _, r in nv.sort_values(["Metal", "Formula"]).iterrows():
    st_ = "absent" if not r["in_db_correct"] else f"{r['ehull_meV_correct']:.1f}"
    st_o = "absent" if not r["in_db_orig"] else f"{r['ehull_meV_orig']:.1f}"
    rows.append(f"{mp(r['Formula'])} & {mp(r['Reduced formula'])} & {r['Structure Family']} & {int(r['Oxidation State'])} & {r['Avg Voltage (V)']:.2f} & {r['Capacity (mAh/g)']:.0f} & {r['Predicted ED 4-feature RF (Wh/L)']:.0f} & {st_} & {mp(r['Original query formula'])} & {st_o} \\\\")
T["esi_s3"] = "\n".join(rows)

# ---- ESI S4: LiCuO2 electrode entries ----
rows = []
for e in R["licuo2_electrodes"]:
    rows.append(f"{mp(e['f'])} & {e['V']:.2f} & {e['dV']:.2f} & {e['Ehc']*1000:.0f} & {e['Ehd']*1000:.0f} & \\texttt{{{e['disch']}}} & \\texttt{{{e['charge']}}} \\\\")
T["esi_s4"] = "\n".join(rows)

# ---- ESI S5: merge comparison ----
rows = []
for k in ["Electrochemical only (4)", "Structural only (6)", "Combined (8)"]:
    a = MLF["r13"][k]; b = ML["r13"][k]
    rows.append(f"{k} & {a['random'][0]:.3f} $\\pm$ {a['random'][1]:.3f} & {a['grouped'][0]:.3f} $\\pm$ {a['grouped'][1]:.3f} & {b['random'][0]:.3f} $\\pm$ {b['random'][1]:.3f} & {b['grouped'][0]:.3f} $\\pm$ {b['grouped'][1]:.3f} \\\\")
rows.append(f"$V\\times C\\times\\rho$ (no fitting) & {MLF['r213']['arith']:.4f} & -- & {ML['r213']['arith']:.4f} & -- \\\\")
T["esi_s5"] = "\n".join(rows)

# ---- Table (main) missing data ----
r = ML["r216"]
T["table_missing"] = "\n".join([
    f"Random Forest, mean-imputed capacity & {r['test_complete']:.3f} ($n={r['n_test_complete']}$) & {r['test_imputed']:.3f} ($n={r['n_test_imp']}$) \\\\",
    f"$V\\times C\\times\\rho$, mean-imputed capacity & -- & {r['arith_mean_imp']:.3f} \\\\",
    f"$V\\times C\\times\\rho$, RF-imputed capacity & -- & {r['arith_rf_imp']:.3f} \\\\",
    f"Random Forest, RF-imputed capacity & -- & {r['ml_rf_imp']:.3f} \\\\"])
T["r216"] = r; T["uncert"] = U; T["r221"] = ML["r221"]; T["r215"] = ML["r215"]; T["r13"] = ML["r13"]; T["r213"] = ML["r213"]; T["r214_id"] = ML["r214"]; T["r214_f"] = MLF["r214"]
json.dump(T, open("tables.json", "w"), indent=1, default=str)
print("tables written:", list(T))
print(T["table10"]); print(T["table5"]); print(T["table7"])
