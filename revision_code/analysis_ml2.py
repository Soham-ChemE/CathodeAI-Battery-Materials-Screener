"""Second ML pass: Table 3 (models), MatMiner rows of Table 2 (random + grouped CV),
Table 4 SHAP, uncertainty (Section 2.9), arithmetic check + applicability domain for the
42 generated compositions (R1.5, R2.17, Fig. 18)."""
import pickle, json, warnings, re
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.neural_network import MLPRegressor
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import KFold, GroupKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
warnings.filterwarnings("ignore")
import os; STATE = os.environ.get("STATE", "repro_state.pkl"); TAG = os.environ.get("TAG", ""); st = pickle.load(open(STATE, "rb"))
df_ml3, df_filtered = st["df_ml3"], st["df_filtered"]
combined, electro, structural = st["combined_features"], st["electro_features"], st["structural_features"]
target = "Energy Density (Wh/L)"; y = df_ml3[target].values
kf = KFold(n_splits=5, shuffle=True, random_state=42); gkf = GroupKFold(n_splits=5); groups = df_ml3["Formula_base"].values
out = {}
X3s = StandardScaler().fit_transform(df_ml3[combined].values)

# ---------- Table 3 ----------
print("=" * 70); print("TABLE 3 models on combined 8 (5-fold random KFold; grouped in brackets)  [notebook: LR 0.9286/0.0193/153.60, RF 0.9392/0.0575/101.10, XGB 0.9362/0.0517/104.87, NN 0.9736/0.0134/83.64]")
models = {"Linear Regression": LinearRegression(), "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
          "Neural Network": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)}
out["table3"] = {}
for n, m in models.items():
    r2 = cross_val_score(m, X3s, y, cv=kf, scoring="r2"); mae = -cross_val_score(m, X3s, y, cv=kf, scoring="neg_mean_absolute_error")
    r2g = cross_val_score(m, X3s, y, cv=gkf, groups=groups, scoring="r2"); maeg = -cross_val_score(m, X3s, y, cv=gkf, groups=groups, scoring="neg_mean_absolute_error")
    out["table3"][n] = {"r2": r2.mean(), "std": r2.std(), "mae": mae.mean(), "r2g": r2g.mean(), "stdg": r2g.std(), "maeg": maeg.mean()}
    print(f"  {n:18} R2 {r2.mean():.4f}+/-{r2.std():.4f} MAE {mae.mean():.2f}   [grouped R2 {r2g.mean():.4f}+/-{r2g.std():.4f} MAE {maeg.mean():.2f}]")

# ---------- MatMiner ----------
print("=" * 70); print("MatMiner Magpie descriptors (Table 2 rows)")
from matminer.featurizers.composition import ElementProperty
from pymatgen.core import Composition
ep = ElementProperty.from_preset("magpie"); ep.set_n_jobs(1)
comps = [Composition(f) for f in df_ml3["Formula_base"]]
mm = pd.DataFrame(ep.featurize_many(comps, ignore_errors=True, pbar=False), columns=ep.feature_labels()).dropna(axis=1)
print(f"  Magpie features: {mm.shape[1]} (orig 132) for {len(mm)} rows")
Xmm = StandardScaler().fit_transform(mm.values)
Xfull = StandardScaler().fit_transform(np.hstack([df_ml3[combined].values, mm.values]))
lasso = Lasso(alpha=0.01, max_iter=10000); sfm = SelectFromModel(lasso).fit(Xmm, y); sel = sfm.get_support(); print(f"  Lasso-selected: {sel.sum()} (orig 83)")
out["table2"] = {}
for n, X in [("Electrochemical only", StandardScaler().fit_transform(df_ml3[electro].values)), ("Structural only (DFT)", StandardScaler().fit_transform(df_ml3[structural].values)),
             ("Combined (final)", X3s), ("MatMiner (Magpie)", Xmm), ("Lasso-selected", Xmm[:, sel]), ("Full (combined + MatMiner)", Xfull)]:
    r = cross_val_score(RandomForestRegressor(n_estimators=100, random_state=42), X, y, cv=kf, scoring="r2")
    g = cross_val_score(RandomForestRegressor(n_estimators=100, random_state=42), X, y, cv=gkf, groups=groups, scoring="r2")
    out["table2"][n] = {"r2": r.mean(), "std": r.std(), "r2g": g.mean(), "stdg": g.std(), "nfeat": X.shape[1]}
    print(f"  {n:28} n={X.shape[1]:3d}  random {r.mean():.4f}+/-{r.std():.4f}   grouped {g.mean():.4f}+/-{g.std():.4f}")

# ---------- SHAP (Table 4) ----------
print("=" * 70); print("SHAP (RF 200 trees on full 1702)  [notebook: 603.36, 203.91, 191.36, 31.05, 23.61, 5.09, 4.09, 1.84]")
import shap
rf_shap = RandomForestRegressor(n_estimators=200, random_state=42).fit(X3s, y)
sv = shap.TreeExplainer(rf_shap).shap_values(X3s)
msv = np.abs(sv).mean(axis=0)
out["shap"] = {f: {"mean_abs_shap": float(v), "rf_importance": float(i)} for f, v, i in zip(combined, msv, rf_shap.feature_importances_)}
for f, v, i in sorted(zip(combined, msv, rf_shap.feature_importances_), key=lambda t: -t[1]): print(f"  {f:28} |SHAP| {v:7.2f}  importance {i*100:5.1f}%")
np.savez(f"shap_values{TAG}.npz", sv=sv, X=df_ml3[combined].values, y=y, features=np.array(combined))
# threshold for formation energy: where does the SHAP contribution cross zero?
fe = df_ml3["Formation Energy (eV/atom)"].values; fs = sv[:, combined.index("Formation Energy (eV/atom)")]
bins = np.linspace(fe.min(), fe.max(), 25); mids = 0.5 * (bins[1:] + bins[:-1]); bm = [fs[(fe >= a) & (fe < b)].mean() if ((fe >= a) & (fe < b)).sum() > 5 else np.nan for a, b in zip(bins[:-1], bins[1:])]
print("  formation-energy SHAP by bin:", [(round(m, 2), round(v, 1)) for m, v in zip(mids, bm) if not np.isnan(v)])
# uncertainty
rf_c, X3_test, y3_test = st["rf_combined"], st["X3_test"], st["y3_test"]
pt = np.stack([t.predict(X3_test) for t in rf_c.estimators_]); mean_p, std_p = pt.mean(0), pt.std(0); hw = 1.96 * std_p
cov = np.mean((y3_test >= mean_p - hw) & (y3_test <= mean_p + hw)) * 100
idx = np.arange(len(y)); tr, te = train_test_split(idx, test_size=0.2, random_state=42); cap_te = df_ml3["Capacity (mAh/g)"].values[te]
r_uc = np.corrcoef(cap_te, hw)[0, 1]
print(f"  UNCERTAINTY: coverage {cov:.1f}% (paper 95.6), mean half-width {hw.mean():.1f} (paper 308; notebook 323.6), max {hw.max():.0f}, r(unc,cap) {r_uc:.3f} (paper 0.555; notebook 0.620)")
out["uncertainty"] = {"coverage": cov, "mean_hw": hw.mean(), "max_hw": hw.max(), "r_cap": r_uc, "n_test": len(y3_test)}
np.savez(f"uncertainty{TAG}.npz", mean_p=mean_p, hw=hw, y=y3_test, cap=cap_te)

# ---------- Novel compositions: arithmetic check with MP density (R1.5) and AD in the 4-feature space (Fig. 18) ----------
print("=" * 70); print("Novel compositions: arithmetic V*C*rho check and 4-feature applicability domain")
nv = pd.read_csv("novel_compositions_recheck.csv")
sm = json.load(open("mpdata/summary_LiO.json"))
dens = {}
for d in sm:
    f = d["formula_pretty"]
    if d.get("density") is not None and (f not in dens or d["energy_above_hull"] < dens[f][1]): dens[f] = (d["density"], d["energy_above_hull"], d["material_id"])
aw = {"Li": 6.94, "O": 16.00, "Fe": 55.85, "Mn": 54.94, "Ni": 58.69, "Co": 58.93, "Cu": 63.55, "Ti": 47.87, "V": 50.94}
nv["FW"] = nv["n_Li"] * aw["Li"] + nv["n_M"] * nv["Metal"].map(aw) + nv["n_O"] * aw["O"]
nv["C_faraday_unclipped"] = nv["n_Li"] * 26801 / nv["FW"]
nv["rho_MP (g/cc)"] = nv["Reduced formula"].map(lambda f: dens.get(f, (np.nan,))[0])
nv["ED_arith (V*C_clipped*rho_MP)"] = nv["Avg Voltage (V)"] * nv["Capacity (mAh/g)"] * nv["rho_MP (g/cc)"]
nv["ED_arith_unclipped"] = nv["Avg Voltage (V)"] * nv["C_faraday_unclipped"] * nv["rho_MP (g/cc)"]
ok = nv["rho_MP (g/cc)"].notna()
print(f"  MP density available for {ok.sum()} of 42 (database-present reduced formulas)")
print(f"  RF prediction vs V*C*rho (clipped C): Pearson r = {np.corrcoef(nv.loc[ok,'Predicted ED 4-feature RF (Wh/L)'], nv.loc[ok,'ED_arith (V*C_clipped*rho_MP)'])[0,1]:.3f}; median ratio RF/arith = {np.median(nv.loc[ok,'Predicted ED 4-feature RF (Wh/L)']/nv.loc[ok,'ED_arith (V*C_clipped*rho_MP)']):.2f}")
print(f"  capacity clipping: {(nv['C_faraday_unclipped']>nv['Capacity (mAh/g)']+0.5).sum()} of 42 had Faraday capacity clipped DOWN to the family maximum; {(nv['C_faraday_unclipped']<nv['Capacity (mAh/g)']-0.5).sum()} clipped UP to the family minimum")
print(f"  predicted ED range: RF {nv['Predicted ED 4-feature RF (Wh/L)'].min():.0f}-{nv['Predicted ED 4-feature RF (Wh/L)'].max():.0f}; arith(clipped) {nv.loc[ok,'ED_arith (V*C_clipped*rho_MP)'].min():.0f}-{nv.loc[ok,'ED_arith (V*C_clipped*rho_MP)'].max():.0f}; arith(unclipped) {nv.loc[ok,'ED_arith_unclipped'].min():.0f}-{nv.loc[ok,'ED_arith_unclipped'].max():.0f}")
# training-set context for R1.5: distribution of ED in the 1864 set
ed_tr = df_filtered[target]; print(f"  training ED distribution (n={len(ed_tr)}): median {ed_tr.median():.0f}, 90th pct {ed_tr.quantile(.9):.0f}, max {ed_tr.max():.0f}; fraction > 3500 Wh/L: {(ed_tr>3500).mean()*100:.1f}%")
# AD in the 4-feature space actually used by the novel-composition model
f4 = ["Avg Voltage (V)", "Capacity (mAh/g)", "Stability Charge (eV)", "Stability Discharge (eV)"]
Xtr = df_filtered[f4].values; mu, sd = Xtr.mean(0), Xtr.std(0)
Xn = nv[f4].values; Z = (Xn - mu) / sd
Xtr_s = (Xtr - mu) / sd; Xtr_s1 = np.hstack([np.ones((len(Xtr_s), 1)), Xtr_s]); H = np.linalg.inv(Xtr_s1.T @ Xtr_s1)
lev = np.array([np.r_[1, z] @ H @ np.r_[1, z] for z in Z]); thr = 3 * Xtr_s1.shape[1] / len(Xtr_s1)
nv["maxZ_4feat"] = np.abs(Z).max(1); nv["leverage_4feat"] = lev
print(f"  4-feature AD: max|Z| range {nv['maxZ_4feat'].min():.2f}-{nv['maxZ_4feat'].max():.2f} (all < 3: {(nv['maxZ_4feat']<3).all()}); leverage range {lev.min():.4f}-{lev.max():.4f}, warning threshold 3p/n = {thr:.4f}; n above threshold: {(lev>thr).sum()}")
print(f"  per-feature Z (max over 42): V {np.abs(Z[:,0]).max():.2f}, C {np.abs(Z[:,1]).max():.2f}, stab_c {np.abs(Z[:,2]).max():.2f}, stab_d {np.abs(Z[:,3]).max():.2f}; training C range {Xtr[:,1].min():.0f}-{Xtr[:,1].max():.0f}, generated C range {Xn[:,1].min():.0f}-{Xn[:,1].max():.0f}")
np.savez(f"ad_4feat{TAG}.npz", Ztrain=Xtr_s, Znovel=Z, lev_train=np.array([np.r_[1, z] @ H @ np.r_[1, z] for z in Xtr_s]), lev_novel=lev, thr=thr)
out["novel"] = {"n_density": int(ok.sum()), "r_rf_arith": float(np.corrcoef(nv.loc[ok, 'Predicted ED 4-feature RF (Wh/L)'], nv.loc[ok, 'ED_arith (V*C_clipped*rho_MP)'])[0, 1]),
                "median_ratio": float(np.median(nv.loc[ok, 'Predicted ED 4-feature RF (Wh/L)'] / nv.loc[ok, 'ED_arith (V*C_clipped*rho_MP)'])), "n_clipped_down": int((nv['C_faraday_unclipped'] > nv['Capacity (mAh/g)'] + 0.5).sum()),
                "n_clipped_up": int((nv['C_faraday_unclipped'] < nv['Capacity (mAh/g)'] - 0.5).sum()), "maxZ": float(nv['maxZ_4feat'].max()), "lev_max": float(lev.max()), "thr": float(thr), "n_above": int((lev > thr).sum()),
                "ed_train_median": float(ed_tr.median()), "ed_train_p90": float(ed_tr.quantile(.9)), "frac_gt_3500": float((ed_tr > 3500).mean())}
nv.to_csv("novel_compositions_recheck.csv", index=False)
absent = nv[~nv["in_db_correct"]].drop_duplicates("Reduced formula")
print("\n  DATABASE-ABSENT (correct stoichiometry) for Table 9:")
print(absent[["Formula", "Reduced formula", "Structure Family", "Metal", "Oxidation State", "Avg Voltage (V)", "Capacity (mAh/g)", "C_faraday_unclipped", "Predicted ED 4-feature RF (Wh/L)"]].to_string(index=False))
json.dump(out, open(f"analysis_ml2_results{TAG}.json", "w"), indent=1, default=lambda o: float(o))
print("saved analysis_ml2_results.json")
