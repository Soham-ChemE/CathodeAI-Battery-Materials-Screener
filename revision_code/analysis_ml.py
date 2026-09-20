"""ML reviewer points: R1.3 (GroupKFold leakage), R2.13 (fair V/C/rho baseline),
R2.14 (arithmetic identity), R2.15 (ID-level merge), R2.16 (missing-capacity split),
R2.21 (DFT error sensitivity: synthesizability labels + discovery-zone membership)."""
import pickle, json, warnings, re
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, GroupKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
warnings.filterwarnings("ignore")
import os; STATE = os.environ.get("STATE", "repro_state.pkl"); TAG = os.environ.get("TAG", ""); st = pickle.load(open(STATE, "rb"))
df_ml3, df_cathodes, df_struct, df_merged = st["df_ml3"], st["df_cathodes"], st["df_struct"], st["df_merged"]
combined, electro, structural = st["combined_features"], st["electro_features"], st["structural_features"]
target = "Energy Density (Wh/L)"
y = df_ml3[target].values
out = {}
def rf(): return RandomForestRegressor(n_estimators=100, random_state=42)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
def cv(feats, cvobj, groups=None, df=df_ml3, model=None):
    Xs = StandardScaler().fit_transform(df[feats].values)
    m = model if model is not None else rf()
    s = cross_val_score(m, Xs, df[target].values, cv=cvobj, groups=groups, scoring="r2")
    return s.mean(), s.std()

# ---------------- R1.3 grouped CV ----------------
print("=" * 70); print("R1.3  Random KFold vs GroupKFold (groups = base formula)")
groups = df_ml3["Formula_base"].values
gkf = GroupKFold(n_splits=5)
n_groups = df_ml3["Formula_base"].nunique()
dup = df_ml3.groupby("Formula_base").size()
print(f"  {len(df_ml3)} rows, {n_groups} unique base formulas; {int((dup>1).sum())} formulas appear >1 time; max multiplicity {dup.max()}; rows in multi-entry groups {int(dup[dup>1].sum())}")
out["r13"] = {}
for name, feats in [("Electrochemical only (4)", electro), ("Structural only (6)", structural), ("Combined (8)", combined)]:
    m1, s1 = cv(feats, kf); m2, s2 = cv(feats, gkf, groups)
    out["r13"][name] = {"random": (m1, s1), "grouped": (m2, s2)}
    print(f"  {name:26} random {m1:.3f}+/-{s1:.3f}   grouped {m2:.3f}+/-{s2:.3f}")
# grouped also for the framework (element set) as a stricter grouping
df_ml3["framework"] = df_ml3["Formula_base"].apply(lambda f: "".join(sorted(set(re.findall("[A-Z][a-z]?", f)) - {"Li"})))
gkf2 = GroupKFold(n_splits=5)
for name, feats in [("Combined (8)", combined)]:
    m3, s3 = cv(feats, gkf2, df_ml3["framework"].values)
    out["r13"][name]["grouped_framework"] = (m3, s3)
    print(f"  {name:26} grouped by element set ({df_ml3['framework'].nunique()} groups): {m3:.3f}+/-{s3:.3f}")

# ---------------- R2.13 fair baselines ----------------
print("=" * 70); print("R2.13 equivalent-information baselines (5-fold random KFold, RF unless noted)")
out["r213"] = {}
for name, feats, model in [("V + C only", ["Avg Voltage (V)", "Capacity (mAh/g)"], None),
                           ("V + C + density", ["Avg Voltage (V)", "Capacity (mAh/g)", "Density (g/cc)"], None),
                           ("V + C + density (linear on log)", None, None),
                           ("Combined 8", combined, None),
                           ("Combined 8 minus density (7)", [f for f in combined if f != "Density (g/cc)"], None),
                           ("Structural 6 + density already in", structural, None)]:
    if feats is None:
        Xl = np.log(df_ml3[["Avg Voltage (V)", "Capacity (mAh/g)", "Density (g/cc)"]].values); yl = np.log(y)
        s = cross_val_score(LinearRegression(), Xl, yl, cv=kf, scoring="r2")
        # back-transform R2 on original scale via manual CV
        r2s = []
        for tr, te in kf.split(Xl):
            lr = LinearRegression().fit(Xl[tr], yl[tr]); r2s.append(r2_score(y[te], np.exp(lr.predict(Xl[te]))))
        m, sd = np.mean(r2s), np.std(r2s)
    else:
        m, sd = cv(feats, kf, model=model)
    out["r213"][name] = (m, sd); print(f"  {name:36} R2 {m:.3f}+/-{sd:.3f}")
arith = df_ml3["Avg Voltage (V)"] * df_ml3["Capacity (mAh/g)"] * df_ml3["Density (g/cc)"]
print(f"  Arithmetic V*C*rho (no fitting)          R2 {r2_score(y, arith):.4f}")
out["r213"]["arith"] = r2_score(y, arith)
# Fraction of combined-model gain attributable to density
print(f"  Combined-8 minus V+C+rho = {out['r213']['Combined 8'][0]-out['r213']['V + C + density'][0]:+.3f}")

# ---------------- R2.14 arithmetic identity residual ----------------
print("=" * 70); print("R2.14 arithmetic identity check")
k = np.sum(arith * y) / np.sum(arith * arith)
ratio = y / arith
print(f"  best-fit k = {k:.4f}, median ratio {np.median(ratio):.4f}, mean {ratio.mean():.4f}, IQR [{np.percentile(ratio,25):.3f},{np.percentile(ratio,75):.3f}]")
multi = df_ml3["n_polymorphs"] > 1
print(f"  rows whose base formula has >1 structural entry: {multi.sum()} ({multi.mean()*100:.1f}%)")
for lab, mask in [("single-polymorph rows", ~multi), ("multi-polymorph rows", multi)]:
    if mask.sum() < 2: continue
    print(f"    {lab:24} n={mask.sum():4d}  R2(arith)={r2_score(y[mask], arith[mask]):.4f}  median |ratio-1| = {np.median(np.abs(ratio[mask]-1)):.4f}")
out["r214"] = {"k": k, "median_ratio": float(np.median(ratio)), "multi_frac": float(multi.mean()),
               "r2_single": r2_score(y[~multi], arith[~multi]) if (~multi).sum()>1 else None, "r2_multi": r2_score(y[multi], arith[multi]) if multi.sum()>1 else None}

# ---------------- R2.15 ID-level merge ----------------
print("=" * 70); print("R2.15 ID-level merge (electrode id_discharge -> structural material_id)")
sid = df_struct.set_index("material_id")
dc = df_cathodes.copy()
for end in ["id_discharge", "id_charge"]:
    dc[f"{end}_in_struct"] = dc[end].isin(sid.index)
print(f"  of {len(dc)} cathode entries: discharge-ID found in structural set {dc['id_discharge_in_struct'].sum()}, charge-ID found {dc['id_charge_in_struct'].sum()}")
df_id = dc[dc["id_discharge_in_struct"]].copy()
for f in structural:
    df_id[f] = sid.loc[df_id["id_discharge"], f].values
df_id["Space Group"] = sid.loc[df_id["id_discharge"], "Space Group"].values
df_id = df_id.dropna(subset=combined + [target]).reset_index(drop=True)
print(f"  ID-level merged rows: {len(df_id)} (formula-level merge: {len(df_ml3)})")
# how many base formulas map to >1 structural entry (polymorph ambiguity) in the formula-level merge
print(f"  formula-level merge: {multi.sum()} of {len(df_ml3)} rows received polymorph-AVERAGED descriptors (base formula with >1 structural entry)")
# electrodes sharing the same base formula but different discharge structures
g = df_id.groupby("Formula_base")["id_discharge"].nunique()
print(f"  base formulas with >1 distinct discharge structure among matched electrodes: {(g>1).sum()} (covering {int(df_id['Formula_base'].isin(g[g>1].index).sum())} rows)")
out["r215"] = {"n_id": len(df_id), "n_formula": len(df_ml3), "multi_rows": int(multi.sum()), "n_disch_found": int(dc["id_discharge_in_struct"].sum())}
gid = GroupKFold(n_splits=5)
for name, feats in [("Electrochemical only (4)", electro), ("Structural only (6)", structural), ("Combined (8)", combined)]:
    m1, s1 = cv(feats, kf, df=df_id); m2, s2 = cv(feats, gid, df_id["Formula_base"].values, df=df_id)
    out["r215"][name] = {"random": (m1, s1), "grouped": (m2, s2)}
    print(f"  ID-merge {name:26} random {m1:.3f}+/-{s1:.3f}  grouped {m2:.3f}+/-{s2:.3f}")
arith_id = df_id["Avg Voltage (V)"] * df_id["Capacity (mAh/g)"] * df_id["Density (g/cc)"]
print(f"  ID-merge arithmetic V*C*rho R2 = {r2_score(df_id[target], arith_id):.4f} (formula-level {out['r213']['arith']:.4f})")
out["r215"]["arith"] = r2_score(df_id[target], arith_id)
# same-composition, different structure: do structural features differ within a base formula?
sub = df_id[df_id["Formula_base"].isin(g[g>1].index)]
print(f"  within-formula spread of density for multi-structure formulas: median range {sub.groupby('Formula_base')['Density (g/cc)'].agg(lambda s: s.max()-s.min()).median():.3f} g/cc")
df_id.to_pickle(f"df_id_merge{TAG}.pkl")

# ---------------- R2.16 missing-capacity experiment ----------------
print("=" * 70); print("R2.16 missing-capacity experiment (30% of capacity values removed, test rows only vs all rows)")
Xsc = st["X3scaler"]; rf_c = st["rf_combined"]
Xall = df_ml3[combined].values.copy()
idx = np.arange(len(df_ml3)); tr, te = train_test_split(idx, test_size=0.2, random_state=42)
rng = np.random.RandomState(42); miss = rng.rand(len(df_ml3)) < 0.30
cap_i = combined.index("Capacity (mAh/g)")
cap_mean_train = df_ml3["Capacity (mAh/g)"].values[tr].mean()
# (a) as in the notebook: model trained on complete training data; capacity mean-imputed at prediction time; evaluated on ALL rows incl. training rows
Xm = Xall.copy(); Xm[miss, cap_i] = cap_mean_train
pred_all = rf_c.predict(Xsc.transform(Xm))
print(f"  [notebook protocol] R2 all 1702 rows (incl. train rows): {r2_score(y, pred_all):.3f}; complete rows {r2_score(y[~miss], pred_all[~miss]):.3f}; imputed rows {r2_score(y[miss], pred_all[miss]):.3f}")
# (b) proper protocol: evaluate on held-out test rows only
te_mask = np.zeros(len(y), bool); te_mask[te] = True
for lab, m in [("test complete", te_mask & ~miss), ("test imputed", te_mask & miss), ("test all", te_mask)]:
    print(f"  [held-out] {lab:14} n={m.sum():3d} ML R2 {r2_score(y[m], pred_all[m]):.3f}  MAE {mean_absolute_error(y[m], pred_all[m]):.0f}")
# (c) baselines: impute then arithmetic
arith_mean = df_ml3["Avg Voltage (V)"].values * np.where(miss, cap_mean_train, df_ml3["Capacity (mAh/g)"].values) * df_ml3["Density (g/cc)"].values
# structural-imputation baseline: RF predicts capacity from the 7 other features (trained on training rows with observed capacity)
others = [f for f in combined if f != "Capacity (mAh/g)"]
imp_rf = rf().fit(df_ml3.loc[tr][~miss[tr]][others].values, df_ml3.loc[tr][~miss[tr]]["Capacity (mAh/g)"].values)
cap_imp = df_ml3["Capacity (mAh/g)"].values.copy(); cap_imp[miss] = imp_rf.predict(df_ml3[others].values[miss])
arith_rfimp = df_ml3["Avg Voltage (V)"].values * cap_imp * df_ml3["Density (g/cc)"].values
# ML with RF-imputed capacity
Xm2 = Xall.copy(); Xm2[miss, cap_i] = cap_imp[miss]; pred_rfimp = rf_c.predict(Xsc.transform(Xm2))
m = te_mask & miss
print(f"  [held-out imputed rows, n={m.sum()}]  ML(mean-imputed) R2 {r2_score(y[m], pred_all[m]):.3f} | arithmetic(mean-imputed C) R2 {r2_score(y[m], arith_mean[m]):.3f} | arithmetic(RF-imputed C) R2 {r2_score(y[m], arith_rfimp[m]):.3f} | ML(RF-imputed C) R2 {r2_score(y[m], pred_rfimp[m]):.3f}")
print(f"  capacity imputation quality on held-out imputed rows: RF-from-structure R2 {r2_score(df_ml3['Capacity (mAh/g)'].values[m], cap_imp[m]):.3f}")
out["r216"] = {"all_incl_train": r2_score(y, pred_all), "test_complete": r2_score(y[te_mask & ~miss], pred_all[te_mask & ~miss]), "test_imputed": r2_score(y[m], pred_all[m]),
               "arith_mean_imp": r2_score(y[m], arith_mean[m]), "arith_rf_imp": r2_score(y[m], arith_rfimp[m]), "ml_rf_imp": r2_score(y[m], pred_rfimp[m]), "n_test_imp": int(m.sum()),
               "n_test_complete": int((te_mask & ~miss).sum()), "cap_imp_r2": r2_score(df_ml3['Capacity (mAh/g)'].values[m], cap_imp[m])}

# ---------------- R2.21 DFT error sensitivity (E_hull) ----------------
print("=" * 70); print("R2.21 Monte Carlo sensitivity to DFT hull-energy error (sigma = 24 meV/atom, 2000 draws)")
rng = np.random.RandomState(0); N = 2000; sig = 0.024
eh = df_ml3["Energy Above Hull (eV)"].values
# discovery zone (as in notebook): top-quartile composite AND E_hull < 50 meV. Use Overall Score (performance) available in df_merged? df_ml3 lacks composite; use energy density top quartile + E_hull<50 as stated in text.
ed = df_ml3[target].values
q75 = np.percentile(ed, 75)
zone0 = (eh < 0.05) & (ed >= q75)
flips = []
for _ in range(N):
    z = ((eh + rng.normal(0, sig, len(eh))) < 0.05) & (ed >= q75)
    flips.append(np.mean(z != zone0))
print(f"  materials in (E_hull<50 meV & top-quartile ED) zone: {zone0.sum()}; mean fraction of 1702 rows whose zone membership flips per draw: {np.mean(flips)*100:.1f}%; among zone members, mean retained {np.mean([1-np.mean(((eh[zone0]+rng.normal(0,sig,zone0.sum()))>=0.05)) for _ in range(500)])*100:.1f}%")
# how many of the 1702 lie within +/-24 meV of the 50 meV threshold
near = np.abs(eh - 0.05) < sig
print(f"  rows within +/-24 meV of the 50 meV threshold: {near.sum()} of {len(eh)} ({near.mean()*100:.1f}%)")
out["r221"] = {"zone_n": int(zone0.sum()), "flip_frac": float(np.mean(flips)), "near_thresh": int(near.sum())}
json.dump({k: (v if not isinstance(v, dict) else {kk: (list(vv) if isinstance(vv, tuple) else vv) for kk, vv in v.items()}) for k, v in out.items()},
          open(f"analysis_ml_results{TAG}.json", "w"), indent=1, default=lambda o: float(o) if hasattr(o, "__float__") else str(o))
print("saved analysis_ml_results.json")
