"""DSI-centred reviewer points: R1.1/R1.2/R2.12 (validation-set analyses), R2.7/R2.19
(per-polymorph DSI from real MP electrode data), R2.18/R2.7 (single cycle-life method:
DSI for every material), R2.20 (phosphate ablation), R2.21 (E_hull error on rankings/Pareto),
plus recomputed Table 10, Pareto fronts, price scenarios and discovery zone."""
import pickle, json, re, itertools, warnings
import numpy as np, pandas as pd
from scipy.stats import spearmanr, pearsonr, kendalltau, ttest_ind, mannwhitneyu
warnings.filterwarnings("ignore")
import os; STATE = os.environ.get("STATE", "repro_state.pkl"); TAG = os.environ.get("TAG", ""); st = pickle.load(open(STATE, "rb"))
df_complete, df_struct_avg, df_struct, df_poly, df_cathodes = st["df_complete"], st["df_struct_avg"], st["df_struct"], st["df_poly"], st["df_cathodes"]
el = json.load(open("mpdata/electrodes_Li.json"))
res = {}
NORM_VOL, NORM_STAB, BG_OPT, BG_RANGE = 14.6, 0.190, 2.0, 4.0
W = (0.50, 0.35, 0.15); PO4B = 0.10
def dsi_score(vol, stab, bg, po4, w=W, bonus=PO4B):
    sv = max(0.0, 1 - vol / NORM_VOL); ss = max(0.0, 1 - stab / NORM_STAB); sb = max(0.0, 1 - abs(bg - BG_OPT) / BG_RANGE)
    d = w[0] * sv + w[1] * ss + w[2] * sb
    if po4: d = min(1.0, d + bonus)
    return d
def dsi_cat(d):  # relative durability category (replaces cycle-number bins)
    return "D (low)" if d < 0.35 else "C (moderate)" if d < 0.55 else "B (high)" if d < 0.75 else "A (very high)"
def dsi_bin(d): return 300 if d < 0.35 else 750 if d < 0.55 else 1500 if d < 0.75 else 2200
cat_rank = {"D (low)": 1, "C (moderate)": 2, "B (high)": 3, "A (very high)": 4}

# ================= validation set (Section 44) =================
val = {"LiCoO2": (500, 2.0, 0.02, 0.00, False, "layered"), "LiFePO4": (2000, 6.81, 0.00, 3.594, True, "olivine"), "LiMnO2": (300, 16.0, 0.05, 0.00, False, "layered"),
       "NMC111": (1000, 2.5, 0.03, 1.50, False, "layered"), "NMC622": (800, 4.0, 0.04, 1.20, False, "layered"), "NMC811": (800, 4.0, 0.06, 0.80, False, "layered"),
       "NCA": (500, 5.0, 0.08, 0.70, False, "layered"), "LNMO": (1000, 2.5, 0.02, 2.00, False, "spinel"), "LTO": (10000, 0.1, 0.00, 2.72, False, "spinel"),
       "LFMP": (1500, 5.0, 0.00, 3.50, True, "olivine"), "Li2MnO3": (200, 8.0, 0.10, 1.317, False, "layered")}
mats = list(val); exp = np.array([val[m][0] for m in mats])
def preds(w=W, bonus=PO4B, mats=mats, values=val, as_bins=True):
    d = [dsi_score(values[m][1], values[m][2], values[m][3], values[m][4], w, bonus) for m in mats]
    return np.array([dsi_bin(x) for x in d]) if as_bins else np.array(d)
single = np.array([2200 if val[m][1] < 3 else 1500 if val[m][1] < 7 else 750 if val[m][1] < 12 else 300 for m in mats])
dsi_b = preds(); dsi_c = preds(as_bins=False)
print("=" * 70); print("DSI validation reproduction")
print(f"  DSI bins   rho={spearmanr(exp, dsi_b)[0]:.4f} p={spearmanr(exp, dsi_b)[1]:.4f} (orig 0.7603/0.0066)")
print(f"  DSI cont.  rho={spearmanr(exp, dsi_c)[0]:.4f} p={spearmanr(exp, dsi_c)[1]:.4f}   (continuous score, no binning)")
print(f"  Single     rho={spearmanr(exp, single)[0]:.4f} p={spearmanr(exp, single)[1]:.4f} (orig 0.5491/0.0802)")
print(f"  Kendall tau DSI bins {kendalltau(exp, dsi_b)[0]:.3f}, single {kendalltau(exp, single)[0]:.3f}")
res["val"] = {"rho_bins": spearmanr(exp, dsi_b)[0], "p_bins": spearmanr(exp, dsi_b)[1], "rho_cont": spearmanr(exp, dsi_c)[0], "p_cont": spearmanr(exp, dsi_c)[1],
              "rho_single": spearmanr(exp, single)[0], "p_single": spearmanr(exp, single)[1], "scores": dict(zip(mats, dsi_c)), "cats": {m: dsi_cat(x) for m, x in zip(mats, dsi_c)}}
# R2.12: Li2MnO3 at 15 cycles; and NCA range; drop LTO (anode)
val15 = dict(val); val15["Li2MnO3"] = (15,) + val["Li2MnO3"][1:]
e15 = np.array([val15[m][0] for m in mats])
print(f"  R2.12 Li2MnO3=15 cycles: DSI rho={spearmanr(e15, dsi_b)[0]:.4f} p={spearmanr(e15, dsi_b)[1]:.4f}; single rho={spearmanr(e15, single)[0]:.4f}")
m10 = [m for m in mats if m != "LTO"]; i10 = [mats.index(m) for m in m10]
print(f"  R2.22 without LTO (n=10): DSI rho={spearmanr(exp[i10], dsi_b[i10])[0]:.4f} p={spearmanr(exp[i10], dsi_b[i10])[1]:.4f}; single rho={spearmanr(exp[i10], single[i10])[0]:.4f} p={spearmanr(exp[i10], single[i10])[1]:.4f}")
res["val"]["li2mno3_15"] = (spearmanr(e15, dsi_b)[0], spearmanr(e15, dsi_b)[1], spearmanr(e15, single)[0])
res["val"]["no_lto"] = (spearmanr(exp[i10], dsi_b[i10])[0], spearmanr(exp[i10], dsi_b[i10])[1], spearmanr(exp[i10], single[i10])[0], spearmanr(exp[i10], single[i10])[1])
# R1.1 chemistry-stratified
print("  R1.1 stratified:")
res["val"]["strat"] = {}
for lab, sel in [("layered oxides", [m for m in mats if val[m][5] == "layered"]), ("non-layered (olivine+spinel)", [m for m in mats if val[m][5] != "layered"])]:
    ii = [mats.index(m) for m in sel]
    r_d = spearmanr(exp[ii], dsi_b[ii]); r_s = spearmanr(exp[ii], single[ii])
    print(f"    {lab:30} n={len(ii)} DSI rho={r_d[0]:.3f} (p={r_d[1]:.3f}); single rho={r_s[0]:.3f} (p={r_s[1]:.3f})")
    res["val"]["strat"][lab] = (len(ii), r_d[0], r_d[1], r_s[0], r_s[1])
# R1.2 nested leave-one-out weight optimisation
print("  R1.2 nested LOO weight optimisation (grid step 0.05 over simplex, bonus in {0,0.05,0.10,0.15}):")
grid = [(a / 20, b / 20, 1 - a / 20 - b / 20) for a in range(0, 21) for b in range(0, 21 - a)]
bon = [0.0, 0.05, 0.10, 0.15]
chosen = []; loo_pred = np.zeros(11)
for i in range(11):
    tr = [j for j in range(11) if j != i]; best = None
    for w in grid:
        for bn in bon:
            p = preds(w, bn)[tr]; r = spearmanr(exp[tr], p)[0]
            if best is None or r > best[0] + 1e-12: best = (r, w, bn)
    chosen.append(best); loo_pred[i] = preds(best[1], best[2])[i]
r_nested = spearmanr(exp, loo_pred)
print(f"    nested-LOO rho (each held-out material predicted with weights optimised on the other 10) = {r_nested[0]:.3f} (p={r_nested[1]:.3f})")
ws = np.array([c[1] for c in chosen]); print(f"    chosen weights per fold: vol {ws[:,0].min():.2f}-{ws[:,0].max():.2f}, stab {ws[:,1].min():.2f}-{ws[:,1].max():.2f}, bg {ws[:,2].min():.2f}-{ws[:,2].max():.2f}; bonus {sorted(set(c[2] for c in chosen))}")
full_best = max(((spearmanr(exp, preds(w, bn))[0], w, bn) for w in grid for bn in bon), key=lambda t: t[0])
print(f"    in-sample optimum over full n=11: rho={full_best[0]:.3f} at weights {full_best[1]} bonus {full_best[2]} (optimistic; compare fixed expert weights 0.760)")
res["val"]["nested"] = {"rho": r_nested[0], "p": r_nested[1], "w_ranges": ws.min(0).tolist() + ws.max(0).tolist(), "insample_best": full_best}
# exhaustive weight sweep summary (how much of the simplex beats single)
allr = np.array([spearmanr(exp, preds(w, PO4B))[0] for w in grid])
print(f"    over all {len(grid)} weight triplets (bonus 0.10): rho median {np.median(allr):.3f}, range [{allr.min():.3f},{allr.max():.3f}], fraction > single (0.549): {np.mean(allr>0.5491)*100:.0f}%")
res["val"]["sweep"] = (float(np.median(allr)), float(allr.min()), float(allr.max()), float(np.mean(allr > 0.5491)))
# bootstrap + LOO re-run for completeness (fast)
rng = np.random.RandomState(42); from scipy.stats import rankdata
def sp(x, y):
    rx, ry = rankdata(x), rankdata(y)
    return 0.0 if np.std(ry) == 0 else 1 - 6 * np.sum((rx - ry) ** 2) / (11 * 120)
bd = [sp(exp[i], dsi_b[i]) for i in (rng.choice(11, 11) for _ in range(10000))]
print(f"  bootstrap DSI 95% CI [{np.percentile(bd,2.5):.3f},{np.percentile(bd,97.5):.3f}] (orig [0.509,0.934])")

# ================= per-material DSI for the 813-material set =================
print("=" * 70); print("Per-material DSI for the 813 oxide set (single method for every reported cycle-life value)")
sid = df_struct.set_index("material_id")
df = df_complete.copy()
df["Band Gap (eV)"] = df["id_discharge"].map(sid["Band Gap (eV)"])   # band gap of the electrode's own discharged structure (ID-level)
df["E_hull struct (meV)"] = df["Stability Discharge (eV)"] * 1000       # hull energy of the discharged phase from the electrode document
print(f"  band gap available (ID-level, discharge structure) for {df['Band Gap (eV)'].notna().sum()} of {len(df)}; volume change available for {df['Max Volume Change (%)'].notna().sum()}")
df["Has P"] = df["Formula"].str.contains("P")
def row_dsi(r, bonus=PO4B, w=W):
    return dsi_score(r["Max Volume Change (%)"], max(0, r["Stability Charge (eV)"]), r["Band Gap (eV)"], r["Has P"], w, bonus) if pd.notna(r["Band Gap (eV)"]) else np.nan
df["DSI"] = df.apply(row_dsi, axis=1); df["DSI (no PO4 bonus)"] = df.apply(lambda r: row_dsi(r, 0.0), axis=1)
df["DSI category"] = df["DSI"].apply(lambda d: dsi_cat(d) if pd.notna(d) else "n/a")
print("  DSI category distribution:", df["DSI category"].value_counts().to_dict())
# composite with the heuristic cycle-life term replaced by the DSI (single method): 5% weight, DSI on [0,1]
df["DSI norm"] = df["DSI"].fillna(df["DSI"].median())
df["Composite (DSI term)"] = (0.25 * df["Overall Score"] / df["Overall Score"].max() + 0.20 * df["Supply Chain Score"] + 0.15 * df["Recyclability Score"]
                              + 0.15 * df["Solid State Score"] + 0.10 * df["Cost Score"] + 0.10 * df["Thermal Safety Score"] + 0.05 * df["DSI norm"])
df = df.sort_values("Composite (DSI term)", ascending=False).reset_index(drop=True); df["Rank (DSI composite)"] = df.index + 1
cols10 = ["Rank (DSI composite)", "Final Rank", "Formula", "Avg Voltage (V)", "Energy Density (Wh/L)", "Cost per kWh ($/kWh)", "Max Volume Change (%)", "Stability Charge (eV)", "Band Gap (eV)", "DSI", "DSI category", "Estimated Cycles", "CathodeAI Complete Score", "Composite (DSI term)", "Supply Chain Score", "Recyclability Score", "Solid State Score", "Thermal Safety Score"]
print("\n  TABLE 10 candidates: original composite order (dedup by formula):")
top_orig_df = df.sort_values("CathodeAI Complete Score", ascending=False).drop_duplicates("Formula").head(10)
print(top_orig_df[cols10].to_string(index=False))
print("\n  TABLE 10 candidates: composite with DSI term (dedup by formula):")
top = df.drop_duplicates("Formula").head(10)
print(top[cols10].to_string(index=False))
top_orig = list(top_orig_df["Formula"]); top_alt = list(top["Formula"])
print(f"  overlap of top-10 sets: {len(set(top_orig)&set(top_alt))}/10; rank-1 unchanged: {top_orig[0]==top_alt[0]}")
res["table10_orig"] = top_orig_df[cols10].to_dict("records"); res["table10"] = top[cols10].to_dict("records"); res["table10_overlap"] = len(set(top_orig) & set(top_alt))
# heuristic (metal lookup) vs DSI across the 813 set: replaces the heuristic-vs-volume-strain r = 0.151
ok = df["DSI"].notna()
print(f"  heuristic Estimated Cycles vs DSI (n={ok.sum()}): Pearson r={pearsonr(df.loc[ok,'Estimated Cycles'], df.loc[ok,'DSI'])[0]:.3f}, Spearman rho={spearmanr(df.loc[ok,'Estimated Cycles'], df.loc[ok,'DSI'])[0]:.3f}")
res["heur_vs_dsi"] = (pearsonr(df.loc[ok, "Estimated Cycles"], df.loc[ok, "DSI"])[0], spearmanr(df.loc[ok, "Estimated Cycles"], df.loc[ok, "DSI"])[0], int(ok.sum()))
# per-formula best (as the original figure did): heuristic first vs DSI max
bf = df[ok].groupby("Formula").agg({"Estimated Cycles": "first", "DSI": "max"})
print(f"  per unique formula (n={len(bf)}): Pearson r={pearsonr(bf['Estimated Cycles'], bf['DSI'])[0]:.3f}, Spearman rho={spearmanr(bf['Estimated Cycles'], bf['DSI'])[0]:.3f}")
res["heur_vs_dsi_formula"] = (pearsonr(bf["Estimated Cycles"], bf["DSI"])[0], spearmanr(bf["Estimated Cycles"], bf["DSI"])[0], len(bf))
# R2.19: metal-identity heuristic tested directly against the 11 experimental materials
base_cycles = {"Fe": 2500, "Mn": 1000, "Ni": 800, "Co": 1000, "Cu": 600, "Ti": 2000, "V": 700, "Cr": 900}
vform = {"LiCoO2": "LiCoO2", "LiFePO4": "LiFePO4", "LiMnO2": "LiMnO2", "NMC111": "LiNi0.33Mn0.33Co0.33O2", "NMC622": "LiNi0.6Mn0.2Co0.2O2", "NMC811": "LiNi0.8Mn0.1Co0.1O2",
         "NCA": "LiNi0.8Co0.15Al0.05O2", "LNMO": "LiNi0.5Mn1.5O4", "LTO": "Li4Ti5O12", "LFMP": "LiFe0.5Mn0.5PO4", "Li2MnO3": "Li2MnO3"}
vvolt = {"LiCoO2": 3.9, "LiFePO4": 3.4, "LiMnO2": 3.3, "NMC111": 3.7, "NMC622": 3.8, "NMC811": 3.87, "NCA": 3.86, "LNMO": 4.7, "LTO": 1.55, "LFMP": 3.6, "Li2MnO3": 3.8}
def heur(m, use_stab=True):
    f = vform[m]; b = 1000
    for k, c in base_cycles.items():
        if k in f: b = c; break
    sf = max(0.3, 1 - val[m][2] * 2) if use_stab else 1.0
    v = vvolt[m]; vf = 0.75 if v > 4.3 else 0.9 if v > 4.0 else 1.0
    return int(b * sf * vf * (1.3 if "P" in f else 1.0))
h1 = np.array([heur(m) for m in mats]); h0 = np.array([heur(m, False) for m in mats])
print(f"  metal-identity heuristic vs experiment (n=11): rho={spearmanr(exp, h1)[0]:.3f} p={spearmanr(exp, h1)[1]:.3f} (with E_hull,charge stability factor); rho={spearmanr(exp, h0)[0]:.3f} p={spearmanr(exp, h0)[1]:.3f} (metal lookup + voltage + phosphate only)")
print("   heuristic preds:", dict(zip(mats, h1)))
res["heur_val"] = {"rho_stab": spearmanr(exp, h1)[0], "p_stab": spearmanr(exp, h1)[1], "rho_nostab": spearmanr(exp, h0)[0], "p_nostab": spearmanr(exp, h0)[1], "preds": dict(zip(mats, h1.tolist()))}
# stratified with continuous DSI
for lab, sel in [("layered oxides", [m for m in mats if val[m][5] == "layered"]), ("non-layered", [m for m in mats if val[m][5] != "layered"])]:
    ii = [mats.index(m) for m in sel]; r_c = spearmanr(exp[ii], dsi_c[ii])
    print(f"  stratified continuous DSI {lab:16} n={len(ii)} rho={r_c[0]:.3f} p={r_c[1]:.3f}"); res["val"]["strat"][lab + " cont"] = (len(ii), r_c[0], r_c[1])
df.to_pickle("df813_dsi.pkl")

# ================= R2.20 phosphate comparison with and without design bonuses =================
print("=" * 70); print("R2.20 phosphate vs non-phosphate (813 oxide set; Welch t-test and Mann-Whitney)")
po4 = df["Formula"].str.contains("PO"); print(f"  n(PO-containing)={po4.sum()}, n(other)={(~po4).sum()}  [manuscript stated 312/1390]")
res["r220"] = {"n_po4": int(po4.sum()), "n_non": int((~po4).sum()), "rows": {}}
for col in ["Thermal Safety Score", "Thermal Safety Score (no PO4 bonus)", "DSI", "DSI (no PO4 bonus)", "Estimated Cycles", "Estimated Cycles (no PO4 factor)",
            "Energy Density (Wh/L)", "Solid State Score", "Max Volume Change (%)", "Stability Charge (eV)"]:
    a = df.loc[po4, col].dropna(); b = df.loc[~po4, col].dropna()
    t, p = ttest_ind(a, b, equal_var=False); u, pu = mannwhitneyu(a, b)
    print(f"  {col:38} PO {a.mean():8.3f}  non {b.mean():8.3f}  diff {a.mean()-b.mean():+8.3f}  Welch p={p:.2e}  MWU p={pu:.2e}")
    res["r220"]["rows"][col] = (a.mean(), b.mean(), p, pu, len(a), len(b))

# ================= R2.7 / R2.19 per-polymorph DSI from real electrode data =================
print("=" * 70); print("R2.19 LiCuO2 polymorphs: electrode entries whose material_ids include each polymorph")
poly_ids = set(df_poly["material_id"])
sid = df_struct.set_index("material_id")
rows = []
for e in el:
    hit = poly_ids & set(e["material_ids"])
    if hit:
        for mid in hit:
            rows.append({"polymorph_id": mid, "Space Group": df_poly.set_index("material_id").loc[mid, "Space Group"], "battery_formula": e["battery_formula"],
                         "id_charge": e["id_charge"], "id_discharge": e["id_discharge"], "role": "discharge" if e["id_discharge"] == mid else ("charge" if e["id_charge"] == mid else "intermediate"),
                         "dV/V (%)": abs(e["max_delta_volume"]) * 100, "E_hull charge (eV)": e["stability_charge"], "E_hull discharge (eV)": e["stability_discharge"],
                         "V (V)": e["average_voltage"], "n_steps": e["num_steps"], "all_ids": e["material_ids"]})
pe = pd.DataFrame(rows)
if len(pe):
    pe["Band Gap (eV)"] = pe["polymorph_id"].map(df_poly.set_index("material_id")["Band Gap (eV)"])
    pe["E_hull polymorph (meV)"] = pe["polymorph_id"].map(df_poly.set_index("material_id")["E_hull (meV/atom)"])
    pe["Vol/atom"] = pe["polymorph_id"].map(df_poly.set_index("material_id")["Vol/atom"])
    pe["DSI"] = pe.apply(lambda r: dsi_score(r["dV/V (%)"], max(0, r["E_hull charge (eV)"]), r["Band Gap (eV)"], False), axis=1)
    pe["DSI category"] = pe["DSI"].apply(dsi_cat)
    pd.set_option("display.width", 250)
    print(pe.drop(columns=["all_ids"]).sort_values("E_hull polymorph (meV)").to_string(index=False))
    print(f"  polymorphs with an electrode entry: {pe['polymorph_id'].nunique()} of 8; DSI range {pe['DSI'].min():.3f}-{pe['DSI'].max():.3f}; categories {sorted(set(pe['DSI category']))}")
    print(f"  dV/V range across LiCuO2 polymorph electrodes: {pe['dV/V (%)'].min():.2f}-{pe['dV/V (%)'].max():.2f}%")
    res["polymorph"] = pe.drop(columns=["all_ids"]).to_dict("records")
else:
    print("  no electrode entries reference the LiCuO2 polymorph ids"); res["polymorph"] = []
# all LiCuO2-formula electrodes (any Li range) for context
lic = [e for e in el if re.sub(r"Li[\d\.]+-[\d\.]+", "Li", e["battery_formula"]) == "LiCuO2"]
print(f"  electrode entries with base formula LiCuO2: {len(lic)}: " + "; ".join(f"{e['battery_formula']} dV={abs(e['max_delta_volume'])*100:.2f}% Ehc={e['stability_charge']:.3f} V={e['average_voltage']:.2f} disch={e['id_discharge']}" for e in lic))
res["licuo2_electrodes"] = [{"f": e["battery_formula"], "dV": abs(e["max_delta_volume"]) * 100, "Ehc": e["stability_charge"], "Ehd": e["stability_discharge"], "V": e["average_voltage"], "disch": e["id_discharge"], "charge": e["id_charge"], "ids": e["material_ids"]} for e in lic]
# is the 7-fold artefact: what proxy gives
print(f"  original proxy: min-vol polymorph -> 0% strain -> bin 2200; max-vol -> 15% -> bin 300; ratio {2200/300:.2f} by construction")

# ================= Pareto fronts with the DSI (top 100 by composite, as in the notebook) =================
print("=" * 70); print("Pareto fronts (top-100 by composite score, as originally), cycle-life axis = DSI score")
def pareto(dfp, c1, c2, max1=True, max2=True):
    v1 = dfp[c1].values * (1 if max1 else -1); v2 = dfp[c2].values * (1 if max2 else -1); keep = np.ones(len(dfp), bool)
    for i in range(len(dfp)):
        for j in range(len(dfp)):
            if i != j and v1[j] >= v1[i] and v2[j] >= v2[i] and (v1[j] > v1[i] or v2[j] > v2[i]): keep[i] = False; break
    return keep
top100 = df.head(100).dropna(subset=["DSI"]).copy()
res["pareto"] = {}
for lab, c1, c2, m1, m2 in [("EV: ED vs DSI", "Energy Density (Wh/L)", "DSI", True, True), ("Consumer: ED vs cost", "Energy Density (Wh/L)", "Cost per kWh ($/kWh)", True, False), ("Grid: thermal vs DSI", "Thermal Safety Score", "DSI", True, True)]:
    k = pareto(top100, c1, c2, m1, m2); front = top100[k].drop_duplicates("Formula")
    print(f"  {lab}: {len(front)} non-dominated -> " + "; ".join(f"{r['Formula']} ({r[c1]:.3g}, {r[c2]:.3g})" for _, r in front.iterrows()))
    res["pareto"][lab] = front[["Formula", c1, c2, "DSI category"]].to_dict("records")
# R2.21 Pareto/ranking stability under E_hull noise (sigma 24 meV on stability_charge)
rng = np.random.RandomState(1); N = 1000
def fronts_and_top(dfx):
    fr = {}
    for lab, c1, c2, m1, m2 in [("EV", "Energy Density (Wh/L)", "DSI", True, True), ("Grid", "Thermal Safety Score", "DSI", True, True)]:
        fr[lab] = set(dfx[pareto(dfx, c1, c2, m1, m2)]["Formula"])
    return fr
base_fr = fronts_and_top(top100)
jac = {"EV": [], "Grid": []}; cat_flip = []; top10_same = []
for _ in range(N):
    d2 = top100.copy(); noisy = np.clip(d2["Stability Charge (eV)"].values + rng.normal(0, 0.024, len(d2)), 0, None)
    d2["DSI"] = [dsi_score(v, s, b, p) for v, s, b, p in zip(d2["Max Volume Change (%)"], noisy, d2["Band Gap (eV)"], d2["Has P"])]
    fr = fronts_and_top(d2)
    for lab in jac: jac[lab].append(len(fr[lab] & base_fr[lab]) / len(fr[lab] | base_fr[lab]))
    cat_flip.append(np.mean(d2["DSI"].apply(dsi_cat).values != top100["DSI"].apply(dsi_cat).values))
print(f"  R2.21 under N(0,24 meV) noise on E_hull,charge: mean Jaccard overlap of Pareto fronts EV {np.mean(jac['EV']):.2f}, Grid {np.mean(jac['Grid']):.2f}; mean fraction of top-100 whose DSI category changes {np.mean(cat_flip)*100:.1f}%")
# category flips over the whole 813 set
d3 = df.dropna(subset=["DSI"]); fl = []
for _ in range(500):
    noisy = np.clip(d3["Stability Charge (eV)"].values + rng.normal(0, 0.024, len(d3)), 0, None)
    nd = np.array([dsi_score(v, s, b, p) for v, s, b, p in zip(d3["Max Volume Change (%)"], noisy, d3["Band Gap (eV)"], d3["Has P"])])
    fl.append(np.mean([dsi_cat(x) for x in nd] != d3["DSI"].apply(dsi_cat).values))
print(f"  whole 813 set: mean fraction of DSI category changes under 24 meV noise = {np.mean(fl)*100:.1f}%")
# validation set: same perturbation on the 11
fl11 = []; rhos = []
for _ in range(2000):
    noisy = {m: (val[m][0], val[m][1], max(0, val[m][2] + rng.normal(0, 0.024)), val[m][3], val[m][4]) for m in mats}
    p = np.array([dsi_bin(dsi_score(noisy[m][1], noisy[m][2], noisy[m][3], noisy[m][4])) for m in mats]); rhos.append(spearmanr(exp, p)[0]); fl11.append(np.mean(p != dsi_b))
print(f"  validation set: DSI rho under 24 meV noise median {np.median(rhos):.3f} [5-95%: {np.percentile(rhos,5):.3f},{np.percentile(rhos,95):.3f}]; bin flips {np.mean(fl11)*100:.0f}% of materials per draw")
res["r221"] = {"jac_ev": float(np.mean(jac["EV"])), "jac_grid": float(np.mean(jac["Grid"])), "cat_flip_top100": float(np.mean(cat_flip)), "cat_flip_813": float(np.mean(fl)),
               "val_rho_med": float(np.median(rhos)), "val_rho_5": float(np.percentile(rhos, 5)), "val_rho_95": float(np.percentile(rhos, 95)), "val_flip": float(np.mean(fl11))}

# ================= price scenarios (Section 32 protocol) =================
print("=" * 70); print("Price scenarios (Section 32 protocol, re-scored composite)")
scen = {"Base": {"Co": 33.0, "Ni": 14.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 23.0}, "Co +100%": {"Co": 66.0, "Ni": 14.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 23.0},
        "Ni +50%": {"Co": 33.0, "Ni": 21.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 23.0}, "Li -50%": {"Co": 33.0, "Ni": 14.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 11.5},
        "IRA reshoring": {"Co": 33.0, "Ni": 14.0, "Mn": 0.9, "Fe": 0.05, "Cu": 8.5, "Li": 23.0}}
def cost_s(f, pr):
    for m, c in pr.items():
        if m in f and m != "Li": return c
    return 20.0
res["price"] = {}
for s, pr in scen.items():
    d2 = df.copy(); d2["sc"] = d2["Formula"].apply(lambda f: cost_s(f, pr)); d2["scs"] = 1 - d2["sc"] / d2["sc"].max()
    d2["S"] = 0.25 * d2["Overall Score"] / d2["Overall Score"].max() + 0.20 * d2["Supply Chain Score"] + 0.15 * d2["Recyclability Score"] + 0.15 * d2["Solid State Score"] + 0.15 * d2["scs"] + 0.10 * d2["Thermal Safety Score"]
    t5 = d2.nlargest(8, "S").drop_duplicates("Formula")["Formula"].tolist()[:5]; res["price"][s] = t5; print(f"  {s:14} top5: {t5}")

# ================= discovery zone =================
print("=" * 70); print("Discovery zone (composite top quartile AND formula-level E_hull < 50 meV/atom AND predicted/actual ED top quartile)")
q = df["Composite (DSI term)"].quantile(0.75); qe = df["Energy Density (Wh/L)"].quantile(0.75)
for lab, mask in [("top-25% composite & E_hull(discharge)<50", (df["Composite (DSI term)"] >= q) & (df["E_hull struct (meV)"] < 50)),
                  ("... & top-25% ED", (df["Composite (DSI term)"] >= q) & (df["E_hull struct (meV)"] < 50) & (df["Energy Density (Wh/L)"] >= qe))]:
    print(f"  {lab}: {mask.sum()} rows, {df[mask]['Formula'].nunique()} unique formulas")
    res["zone_" + lab] = (int(mask.sum()), int(df[mask]["Formula"].nunique()), df[mask].drop_duplicates("Formula")["Formula"].tolist())
print(f"  thresholds: composite {q:.3f}, ED {qe:.0f} Wh/L")
df.to_pickle("df813_dsi.pkl")

pickle.dump(res, open("analysis_dsi_results.pkl", "wb"))
def conv(o):
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, (np.ndarray,)): return o.tolist()
    return str(o)
json.dump(res, open("analysis_dsi_results.json", "w"), indent=1, default=conv)
print("saved analysis_dsi_results.json")
