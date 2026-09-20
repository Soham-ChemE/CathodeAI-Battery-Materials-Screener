"""Reproduce the CathodeAI pipeline from cached Materials Project JSON.
Mirrors copy_of_cathodeai_complete_clean.py sections 4-20, 25-27, 36, 43-49.
Writes pickles for downstream reviewer analyses and prints checks vs the
original notebook outputs."""
import json, re, warnings, pickle
import numpy as np, pandas as pd
from scipy.stats import spearmanr, pearsonr
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
warnings.filterwarnings("ignore")
D = "mpdata/"
ORIG = {}  # original notebook values for comparison

el = json.load(open(D + "electrodes_Li.json"))
sm = json.load(open(D + "summary_LiO.json"))
print(f"electrodes {len(el)}  summary {len(sm)}")

# ---------------- Section 4: cathode filter ----------------
rows = []
for e in el:
    if all(e.get(k) is not None for k in ["average_voltage", "capacity_grav", "energy_vol", "stability_charge", "stability_discharge"]):
        if 2.5 <= e["average_voltage"] <= 5.0 and e["capacity_grav"] > 50 and e["energy_vol"] > 0:
            rows.append({"battery_id": e.get("battery_id"), "Formula": e["battery_formula"],
                         "id_charge": e["id_charge"], "id_discharge": e["id_discharge"],
                         "material_ids": tuple(e["material_ids"]),
                         "Avg Voltage (V)": round(e["average_voltage"], 3),
                         "Capacity (mAh/g)": round(e["capacity_grav"], 2),
                         "Energy Density (Wh/L)": round(e["energy_vol"], 2),
                         "Gravimetric Energy (Wh/kg)": round(e["energy_grav"], 2) if e.get("energy_grav") else None,
                         "Stability Charge (eV)": round(e["stability_charge"], 4),
                         "Stability Discharge (eV)": round(e["stability_discharge"], 4),
                         "Max Volume Change (%)": abs(e["max_delta_volume"]) * 100 if e.get("max_delta_volume") is not None else np.nan})
df_cathodes = pd.DataFrame(rows)
print("True cathode candidates:", len(df_cathodes), "(orig 1886)")

# ---------------- Section 5: toxicity + scoring ----------------
toxic = ["Pb", "Cd", "Hg", "As", "Tl", "Be"]; rare = ["Pt", "Ir", "Os", "Ru", "Rh", "Pd", "Au", "Re", "In", "Ge"]
def is_acceptable(f): return not any(x in f for x in toxic + rare)
df_filtered = df_cathodes[df_cathodes["Formula"].apply(is_acceptable)].copy()
print("After toxicity/cost filter:", len(df_filtered), "(orig 1864)")
def voltage_score(v):
    if 3.5 <= v <= 4.5: return 1.0
    elif 3.0 <= v < 3.5 or 4.5 < v <= 5.0: return 0.7
    return 0.4
df_filtered["capacity_score"] = df_filtered["Capacity (mAh/g)"] / df_filtered["Capacity (mAh/g)"].max()
df_filtered["energy_score"] = df_filtered["Energy Density (Wh/L)"] / df_filtered["Energy Density (Wh/L)"].max()
df_filtered["voltage_score"] = df_filtered["Avg Voltage (V)"].apply(voltage_score)
tot = df_filtered["Stability Charge (eV)"] + df_filtered["Stability Discharge (eV)"]
df_filtered["stability_score"] = 1 - tot / tot.max()
df_filtered["Overall Score"] = (0.30 * df_filtered["voltage_score"] + 0.30 * df_filtered["energy_score"]
                                + 0.25 * df_filtered["capacity_score"] + 0.15 * df_filtered["stability_score"])
df_final = df_filtered.sort_values("Overall Score", ascending=False).reset_index(drop=True)
df_final["Rank"] = df_final.index + 1

# ---------------- Sections 6-7: practical + oxide ----------------
df_practical = df_final.copy()
for h in ["ClO", "VF5", "CF"]:
    df_practical = df_practical[~df_practical["Formula"].str.contains(h)]
df_practical = df_practical.reset_index(drop=True)
def is_pure_oxide(f): return not any(a in f for a in ["F", "Cl", "Br", "S", "N"])
df_oxide = df_practical[df_practical["Formula"].apply(is_pure_oxide)].copy().reset_index(drop=True)
df_oxide["Rank"] = df_oxide.index + 1
print("Pure oxide cathode candidates:", len(df_oxide), "(orig 813)")

# ---------------- Section 8: 4-feature RF (used for novel compositions) ----------------
features4 = ["Avg Voltage (V)", "Capacity (mAh/g)", "Stability Charge (eV)", "Stability Discharge (eV)"]
target = "Energy Density (Wh/L)"
df_ml = df_filtered.dropna(subset=features4 + [target]).copy()
X = df_ml[features4].values; y = df_ml[target].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler4 = StandardScaler(); X_train_s = scaler4.fit_transform(X_train); X_test_s = scaler4.transform(X_test)
model4 = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train_s, y_train)
print(f"4-feature RF test R2 {r2_score(y_test, model4.predict(X_test_s)):.4f} (orig 0.8642), MAE {mean_absolute_error(y_test, model4.predict(X_test_s)):.2f} (orig 237.59)")

# ---------------- Section 11: supply chain / recyclability ----------------
criticality = {"Co": 0.95, "Ni": 0.55, "Mn": 0.30, "Fe": 0.05, "Ti": 0.20, "V": 0.45, "Cr": 0.35, "Cu": 0.25, "Li": 0.60, "P": 0.05,
               "Mg": 0.05, "Al": 0.05, "Si": 0.05, "W": 0.50, "Mo": 0.40, "Nb": 0.65}
recyclability = {"Co": 0.95, "Ni": 0.90, "Mn": 0.60, "Fe": 0.50, "Ti": 0.40, "V": 0.70, "Cr": 0.55, "Cu": 0.85, "Li": 0.75, "P": 0.30,
                 "Mg": 0.40, "Al": 0.70, "Si": 0.35, "W": 0.60, "Mo": 0.65, "Nb": 0.50}
def get_elements(f): return [e for e in re.findall("[A-Z][a-z]?", f) if e not in ("Li", "O")]
def supply_chain_score(f):
    els = get_elements(f)
    return 0.5 if not els else 1 - max(criticality.get(e, 0.5) for e in els)
def recyclability_score(f):
    els = get_elements(f)
    return 0.5 if not els else float(np.mean([recyclability.get(e, 0.5) for e in els]))
df_supply = df_oxide.copy()
df_supply["Supply Chain Score"] = df_supply["Formula"].apply(supply_chain_score)
df_supply["Recyclability Score"] = df_supply["Formula"].apply(recyclability_score)
df_supply["CathodeAI Score"] = (0.50 * df_supply["Overall Score"] / df_supply["Overall Score"].max()
                                + 0.25 * df_supply["Supply Chain Score"] + 0.25 * df_supply["Recyclability Score"])
df_supply = df_supply.sort_values("CathodeAI Score", ascending=False).reset_index(drop=True)

# ---------------- solid state, cost, thermal, heuristic cycles (Sections 12-16) ----------------
def solid_state_score(row):
    f = row["Formula"]; v = row["Avg Voltage (V)"]; s = 1.0
    if v <= 4.0: s += 0.3
    elif v <= 4.3: s += 0.15
    else: s -= 0.2
    for e in ["Mn", "Cr", "Ti"]:
        if e in f: s -= 0.15
    for e in ["V", "Cr", "Mo"]:
        if e in f: s -= 0.10
    return max(0, min(1, s))
metal_cost_per_kwh = {"Co": 45.0, "Ni": 18.0, "Mn": 8.0, "Fe": 5.0, "Cu": 12.0, "V": 35.0, "Ti": 15.0, "Cr": 12.0}
def get_realistic_cost(f):
    for m, c in metal_cost_per_kwh.items():
        if m in f: return c
    return 20.0
thermal_safety = {"Fe": 0.95, "Mn": 0.65, "Ni": 0.40, "Co": 0.45, "Cu": 0.75, "Ti": 0.90, "V": 0.60, "Cr": 0.70, "W": 0.85, "Mo": 0.82}
def thermal_score(f, phosphate_bonus=0.15):
    s = 0.5
    for m, sc in thermal_safety.items():
        if m in f: s = sc; break
    if "PO" in f or "P" in f: s = min(1.0, s + phosphate_bonus)
    if "Mn2" in f or "Mn3" in f: s = min(1.0, s + 0.05)
    return round(s, 3)
base_cycles = {"Fe": 2500, "Mn": 1000, "Ni": 800, "Co": 1000, "Cu": 600, "Ti": 2000, "V": 700, "Cr": 900}
def estimate_cycle_life(row, phosphate_factor_on=True):
    f = row["Formula"]; v = row["Avg Voltage (V)"]; base = 1000
    for m, c in base_cycles.items():
        if m in f: base = c; break
    sf = max(0.3, 1 - (row["Stability Charge (eV)"] + row["Stability Discharge (eV)"]) * 2)
    vf = 0.75 if v > 4.3 else (0.90 if v > 4.0 else 1.0)
    pf = 1.30 if ("P" in f and phosphate_factor_on) else 1.0
    return int(base * sf * vf * pf)

df_cost = df_supply.copy()
df_cost["Solid State Score"] = df_cost.apply(solid_state_score, axis=1)
df_cost["Cost per kWh ($/kWh)"] = df_cost["Formula"].apply(get_realistic_cost)
df_cost["Cost Score"] = 1 - df_cost["Cost per kWh ($/kWh)"] / df_cost["Cost per kWh ($/kWh)"].max()
df_cost["CathodeAI Economic Score"] = (0.35 * df_cost["Overall Score"] / df_cost["Overall Score"].max() + 0.20 * df_cost["Supply Chain Score"]
                                       + 0.20 * df_cost["Recyclability Score"] + 0.15 * df_cost["Solid State Score"] + 0.10 * df_cost["Cost Score"])
df_thermal = df_cost.copy()
df_thermal["Thermal Safety Score"] = df_thermal["Formula"].apply(thermal_score)
df_thermal["Thermal Safety Score (no PO4 bonus)"] = df_thermal["Formula"].apply(lambda f: thermal_score(f, 0.0))
df_thermal["Estimated Cycles"] = df_thermal.apply(estimate_cycle_life, axis=1)
df_thermal["Estimated Cycles (no PO4 factor)"] = df_thermal.apply(lambda r: estimate_cycle_life(r, False), axis=1)
df_thermal["Cycle Life Score"] = df_thermal["Estimated Cycles"] / df_thermal["Estimated Cycles"].max()
df_thermal["CathodeAI Complete Score"] = (0.25 * df_thermal["Overall Score"] / df_thermal["Overall Score"].max() + 0.20 * df_thermal["Supply Chain Score"]
                                          + 0.15 * df_thermal["Recyclability Score"] + 0.15 * df_thermal["Solid State Score"] + 0.10 * df_thermal["Cost Score"]
                                          + 0.10 * df_thermal["Thermal Safety Score"] + 0.05 * df_thermal["Cycle Life Score"])
df_complete = df_thermal.sort_values("CathodeAI Complete Score", ascending=False).reset_index(drop=True)
df_complete["Final Rank"] = df_complete.index + 1
print("\nTop 10 complete ranking (orig: Li0-1CuO2 320 0.827093; Li0-1CuO 180 0.821300; Li0-2CuPO4 484 0.798328):")
print(df_complete[["Final Rank", "Formula", "Avg Voltage (V)", "Energy Density (Wh/L)", "Cost per kWh ($/kWh)", "Estimated Cycles", "CathodeAI Complete Score"]].head(13).to_string(index=False))

# ---------------- Sections 17-19: structural merge ----------------
srows = []
for e in sm:
    if all(e.get(k) is not None for k in ["formation_energy_per_atom", "band_gap", "volume", "nsites", "density"]):
        srows.append({"material_id": e["material_id"], "Formula": e["formula_pretty"], "Formation Energy (eV/atom)": e["formation_energy_per_atom"],
                      "Band Gap (eV)": e["band_gap"], "Volume per Atom (A3)": e["volume"] / e["nsites"] if e["nsites"] > 0 else None,
                      "N Elements": e["nelements"], "Density (g/cc)": e["density"], "Energy Above Hull (eV)": e["energy_above_hull"],
                      "Space Group": (e.get("symmetry") or {}).get("symbol")})
df_struct = pd.DataFrame(srows)
print("\nStructural descriptors available:", len(df_struct), "(orig 16510)")
def normalize_formula(f):
    f = re.sub(r"Li[\d\.]+-[\d\.]+", "Li", f.strip()); f = re.sub(r"Li[\d\.]+", "Li", f); return f.strip()
df_cathodes["Formula_base"] = df_cathodes["Formula"].apply(normalize_formula)
df_struct["Formula_base"] = df_struct["Formula"].apply(normalize_formula)
print("Unique cathode base formulas:", df_cathodes["Formula_base"].nunique(), "(orig 1036); struct:", df_struct["Formula_base"].nunique(), "(orig 4898); overlap:",
      len(set(df_cathodes["Formula_base"]) & set(df_struct["Formula_base"])), "(orig 931)")
structural_features = ["Formation Energy (eV/atom)", "Band Gap (eV)", "Volume per Atom (A3)", "N Elements", "Density (g/cc)", "Energy Above Hull (eV)"]
df_struct_avg = df_struct.groupby("Formula_base").agg({"Formation Energy (eV/atom)": "mean", "Band Gap (eV)": "mean", "Volume per Atom (A3)": "mean",
                                                        "N Elements": "first", "Density (g/cc)": "mean", "Energy Above Hull (eV)": "mean"}).reset_index()
df_struct_avg["n_polymorphs"] = df_struct.groupby("Formula_base").size().values
df_merged = df_cathodes.merge(df_struct_avg, on="Formula_base", how="inner")
print("Merged dataset:", len(df_merged), f"(orig 1702) match rate {len(df_merged)/len(df_cathodes)*100:.1f}%")

# ---------------- Section 20: feature set comparison ----------------
electro_features = ["Avg Voltage (V)", "Capacity (mAh/g)", "Stability Charge (eV)", "Stability Discharge (eV)"]
combined_features = ["Avg Voltage (V)", "Capacity (mAh/g)", "Formation Energy (eV/atom)", "Band Gap (eV)", "Volume per Atom (A3)", "N Elements", "Density (g/cc)", "Energy Above Hull (eV)"]
df_ml3 = df_merged.dropna(subset=combined_features + [target]).copy().reset_index(drop=True)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
def cv_r2(feats, df=df_ml3):
    Xs = StandardScaler().fit_transform(df[feats].values)
    sc = cross_val_score(RandomForestRegressor(n_estimators=100, random_state=42), Xs, df[target].values, cv=kf, scoring="r2")
    return sc.mean(), sc.std()
print("\nFEATURE SET COMPARISON (orig: electro 0.8578/0.0338, struct 0.3366/0.0851, combined 0.9392/0.0575)")
for name, feats in [("Electrochemical only", electro_features), ("Structural only", structural_features), ("Combined 8", combined_features)]:
    m, s = cv_r2(feats); print(f"  {name:22} R2 {m:.4f} +/- {s:.4f}")
X3 = StandardScaler().fit(df_ml3[combined_features].values); X3s = X3.transform(df_ml3[combined_features].values); y3 = df_ml3[target].values
X3_train, X3_test, y3_train, y3_test = train_test_split(X3s, y3, test_size=0.2, random_state=42)
rf_combined = RandomForestRegressor(n_estimators=100, random_state=42).fit(X3_train, y3_train)
print(f"Combined held-out test R2 {r2_score(y3_test, rf_combined.predict(X3_test)):.4f} (paper 0.966), MAE {mean_absolute_error(y3_test, rf_combined.predict(X3_test)):.1f} (paper 92.9)")
print("importances:", {f: round(i, 4) for f, i in zip(combined_features, rf_combined.feature_importances_)})

# ---------------- Sections 25-27: physics cycle life, heuristic vs physics r ----------------
def physics_cycle_life(vc, v, po4=False):
    b = 2200 if vc < 3 else 1500 if vc < 7 else 750 if vc < 12 else 300
    if v > 4.3: b = int(b * 0.75)
    elif v > 4.0: b = int(b * 0.90)
    if po4: b = int(b * 1.20)
    return b
vol_rows = [{"Formula": e["battery_formula"], "battery_id": e.get("battery_id"), "Max Volume Change (%)": abs(e["max_delta_volume"]) * 100,
             "Avg Voltage (V)": e["average_voltage"]} for e in el if e.get("max_delta_volume") is not None and e.get("battery_formula")]
df_vol = pd.DataFrame(vol_rows); print("\nEntries with volume change data:", len(df_vol), "(orig 2774)")
df_vol["Has Phosphate"] = df_vol["Formula"].str.contains("P")
df_vol_f = df_vol[df_vol["Max Volume Change (%)"] <= 50].copy(); print("After <50% filter:", len(df_vol_f), "(orig 2760)")
df_vol_f["Physics Cycle Life"] = df_vol_f.apply(lambda r: physics_cycle_life(r["Max Volume Change (%)"], r["Avg Voltage (V)"] if r["Avg Voltage (V)"] else 3.5, r["Has Phosphate"]), axis=1)
df_vol_f["Formula_base"] = df_vol_f["Formula"].apply(normalize_formula)
df_complete["Formula_base"] = df_complete["Formula"].apply(normalize_formula)
df_wp = df_complete.merge(df_vol_f[["Formula_base", "Max Volume Change (%)", "Physics Cycle Life"]].rename(columns={"Max Volume Change (%)": "MVC_merge"}), on="Formula_base", how="left")
df_wp["Physics Cycle Life"] = df_wp["Physics Cycle Life"].fillna(df_wp["Estimated Cycles"])
print("Rows after many-to-many merge:", len(df_wp), "(orig 5228)")
best = df_wp.groupby("Formula").agg({"Physics Cycle Life": "max", "Estimated Cycles": "first", "MVC_merge": "min", "Energy Density (Wh/L)": "first"}).reset_index().dropna()
r_hp = best["Estimated Cycles"].corr(best["Physics Cycle Life"])
print(f"Heuristic vs physics correlation r = {r_hp:.3f} (orig 0.151), n formulas = {len(best)}")
licuo2 = df_wp[df_wp["Formula"] == "Li0-1CuO2"][["Formula", "MVC_merge", "Physics Cycle Life", "Estimated Cycles"]]
print(licuo2.to_string(index=False))

# ---------------- Sections 43, 49: DSI normalisation + full-dataset correlation ----------------
vc_all = np.array([abs(e["max_delta_volume"]) * 100 for e in el if e.get("max_delta_volume") is not None])
sc_all = np.array([e["stability_charge"] for e in el if e.get("stability_charge") is not None and e["stability_charge"] >= 0])
print(f"\nDSI bounds: vol 95th {np.percentile(vc_all,95):.2f}% (orig 14.64), stab 95th {np.percentile(sc_all,95):.4f} eV (orig 0.1899)")
NORM_VOL, NORM_STAB = 14.6, 0.190
vn, sn = [], []
for e in el:
    if (e.get("max_delta_volume") is not None and e.get("stability_charge") is not None and e["stability_charge"] >= 0
            and e.get("average_voltage") is not None and 2.5 <= e["average_voltage"] <= 5.0):
        vn.append(max(0, 1 - abs(e["max_delta_volume"]) * 100 / NORM_VOL)); sn.append(max(0, 1 - e["stability_charge"] / NORM_STAB))
r, p = pearsonr(vn, sn); print(f"Full dataset n={len(vn)} (orig 2035): r={r:.4f} (orig -0.0050) p={p:.4f}")

# ---------------- Section 36: LiCuO2 polymorphs ----------------
lc = json.load(open(D + "summary_LiCuO2.json"))
df_poly = pd.DataFrame([{"material_id": d["material_id"], "E_hull (meV/atom)": d["energy_above_hull"] * 1000, "Band Gap (eV)": d["band_gap"],
                         "Vol/atom": d["volume"] / d["nsites"], "Density": d["density"], "Space Group": d["symmetry"]["symbol"]} for d in lc]).sort_values("E_hull (meV/atom)")
print("\nLiCuO2 polymorphs:\n", df_poly.to_string(index=False))

pickle.dump({"df_cathodes": df_cathodes, "df_filtered": df_filtered, "df_oxide": df_oxide, "df_complete": df_complete, "df_struct": df_struct,
             "df_struct_avg": df_struct_avg, "df_merged": df_merged, "df_ml3": df_ml3, "df_vol": df_vol, "df_vol_f": df_vol_f, "df_poly": df_poly,
             "combined_features": combined_features, "electro_features": electro_features, "structural_features": structural_features,
             "scaler4": scaler4, "model4": model4, "X3scaler": X3, "rf_combined": rf_combined, "y3_test": y3_test, "X3_test": X3_test},
            open("repro_state.pkl", "wb"))
print("\nSaved repro_state.pkl")
