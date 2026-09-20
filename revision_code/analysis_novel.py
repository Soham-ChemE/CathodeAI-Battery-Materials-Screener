"""R1.4/R1.5/R2.17: regenerate the 42 hypothetical compositions exactly as Section 13,
recompute predicted ED with the reproduced 4-feature RF, then check MP novelty and
E_hull with the formulas AS GENERATED (reduced), not with the Li-index-stripped
formulas used originally."""
import json, pickle, re, time, requests, math
import numpy as np, pandas as pd
from math import gcd
from functools import reduce
st = pickle.load(open("repro_state.pkl", "rb"))
scaler4, model4 = st["scaler4"], st["model4"]
import os
key = os.environ["MP_API_KEY"]  # set your Materials Project API key in the environment
H = {"X-API-KEY": key, "accept": "application/json"}
base = "https://api.materialsproject.org"

transition_metals = {"Fe": [2, 3], "Mn": [2, 3, 4], "Ni": [2, 3, 4], "Co": [2, 3], "Cu": [1, 2], "Ti": [3, 4], "V": [3, 4, 5]}
structure_families = {"layered": {"voltage_range": (3.5, 4.5), "capacity_range": (200, 300)},
                      "spinel": {"voltage_range": (3.8, 4.8), "capacity_range": (100, 150)},
                      "olivine": {"voltage_range": (3.0, 3.8), "capacity_range": (150, 200)}}
voltage_map = {("Fe", 2): 3.45, ("Fe", 3): 3.80, ("Mn", 2): 3.30, ("Mn", 3): 3.50, ("Mn", 4): 4.00, ("Ni", 2): 3.60, ("Ni", 3): 3.90, ("Ni", 4): 4.20,
               ("Co", 2): 3.70, ("Co", 3): 4.00, ("Cu", 1): 3.40, ("Cu", 2): 3.90, ("Ti", 3): 2.80, ("Ti", 4): 3.20, ("V", 3): 3.00, ("V", 4): 3.40, ("V", 5): 3.80}
aw = {"Li": 6.94, "O": 16.00, "Fe": 55.85, "Mn": 54.94, "Ni": 58.69, "Co": 58.93, "Cu": 63.55, "Ti": 47.87, "V": 50.94}
hyp = []
for metal, oxs in transition_metals.items():
    for ox in oxs:
        for structure, params in structure_families.items():
            for n_li in [1, 2, 3]:
                for n_metal in [1, 2]:
                    n_O = (n_li + n_metal * ox) / 2
                    if n_O != int(n_O): continue
                    n_O = int(n_O)
                    fw = n_li * aw["Li"] + n_metal * aw[metal] + n_O * aw["O"]
                    v = max(params["voltage_range"][0], min(params["voltage_range"][1], voltage_map.get((metal, ox), 3.5)))
                    cap = (n_li * 26801) / fw
                    cap = max(params["capacity_range"][0], min(params["capacity_range"][1], cap))
                    formula = f"{'Li' if n_li == 1 else 'Li' + str(n_li)}{metal if n_metal == 1 else metal + str(n_metal)}O{n_O}"
                    hyp.append({"Formula": formula, "Structure Family": structure, "Metal": metal, "Oxidation State": ox, "n_Li": n_li, "n_M": n_metal, "n_O": n_O,
                                "Avg Voltage (V)": round(v, 3), "Capacity (mAh/g)": round(cap, 2), "Empirical ED (Wh/L)": round(v * cap * 3.0, 2),
                                "Stability Charge (eV)": 0.02, "Stability Discharge (eV)": 0.02})
df_hyp = pd.DataFrame(hyp).drop_duplicates(subset=["Formula"]).reset_index(drop=True)
print("Generated hypothetical compositions:", len(df_hyp), "(orig 42)")
X = scaler4.transform(df_hyp[["Avg Voltage (V)", "Capacity (mAh/g)", "Stability Charge (eV)", "Stability Discharge (eV)"]].values)
df_hyp["Predicted ED 4-feature RF (Wh/L)"] = model4.predict(X)

def reduced(n_li, n_m, n_o, metal):
    g = reduce(gcd, [n_li, n_m, n_o])
    a, b, c = n_li // g, n_m // g, n_o // g
    return f"Li{'' if a == 1 else a}{metal}{'' if b == 1 else b}O{'' if c == 1 else c}"
def stripped(f):  # original (buggy) normalisation used for the MP query
    return re.sub(r"Li[\d\.]+", "Li", f)
df_hyp["Reduced formula"] = df_hyp.apply(lambda r: reduced(r["n_Li"], r["n_M"], r["n_O"], r["Metal"]), axis=1)
df_hyp["Original query formula"] = df_hyp["Formula"].apply(stripped)

cache = {}
def mp_lookup(formula):
    if formula in cache: return cache[formula]
    for attempt in range(4):
        try:
            r = requests.get(f"{base}/materials/summary/", headers=H, params={"formula": formula, "_fields": "material_id,formula_pretty,energy_above_hull,is_stable", "_limit": 200}, timeout=60)
            r.raise_for_status(); d = r.json()["data"]; break
        except Exception as e:
            print("retry", formula, e); time.sleep(3); d = None
    if d:
        best = min(d, key=lambda x: x["energy_above_hull"] if x["energy_above_hull"] is not None else 9)
        res = {"in_db": True, "n_entries": len(d), "min_ehull_meV": best["energy_above_hull"] * 1000, "mp_formula": best["formula_pretty"], "mp_id": best["material_id"]}
    else:
        res = {"in_db": False, "n_entries": 0, "min_ehull_meV": np.nan, "mp_formula": None, "mp_id": None}
    cache[formula] = res; return res
for col, tag in [("Reduced formula", "correct"), ("Original query formula", "orig")]:
    res = df_hyp[col].apply(mp_lookup)
    df_hyp[f"in_db_{tag}"] = [x["in_db"] for x in res]; df_hyp[f"ehull_meV_{tag}"] = [x["min_ehull_meV"] for x in res]
    df_hyp[f"n_entries_{tag}"] = [x["n_entries"] for x in res]; df_hyp[f"mp_id_{tag}"] = [x["mp_id"] for x in res]
df_hyp["Formal M oxidation state as queried (orig)"] = df_hyp.apply(lambda r: (2 * r["n_O"] - 1) / r["n_M"], axis=1)
pd.set_option("display.width", 250)
cols = ["Formula", "Reduced formula", "Original query formula", "Formal M oxidation state as queried (orig)", "in_db_orig", "ehull_meV_orig", "in_db_correct", "ehull_meV_correct", "Predicted ED 4-feature RF (Wh/L)"]
print(df_hyp[cols].to_string(index=False))
def synth(e):
    if pd.isna(e): return "absent"
    return "synth(<50)" if e < 50 else ("maybe(50-100)" if e < 100 else "unlikely(>100)")
print("\nORIGINAL (stripped) classification:", df_hyp["ehull_meV_orig"].apply(synth).value_counts().to_dict(), "| unique absent:", sorted(set(df_hyp.loc[~df_hyp["in_db_orig"], "Original query formula"])))
print("CORRECT (reduced) classification:", df_hyp["ehull_meV_correct"].apply(synth).value_counts().to_dict(), "| unique absent:", sorted(set(df_hyp.loc[~df_hyp["in_db_correct"], "Reduced formula"])))
print("unique reduced formulas:", df_hyp["Reduced formula"].nunique())
# Which of the reduced formulas exist in the 2,774 electrode set or the 16,510 structural set?
el = json.load(open("mpdata/electrodes_Li.json")); sm = json.load(open("mpdata/summary_LiO.json"))
struct_formulas = set(d["formula_pretty"] for d in sm)
def normalize_formula(f):
    f = re.sub(r"Li[\d\.]+-[\d\.]+", "Li", f.strip()); f = re.sub(r"Li[\d\.]+", "Li", f); return f.strip()
el_bases = set(normalize_formula(e["battery_formula"]) for e in el)
df_hyp["in_16510_struct_set"] = df_hyp["Reduced formula"].isin(struct_formulas)
print("\nreduced formulas present in 16,510 structural set:", df_hyp["in_16510_struct_set"].sum(), "of", len(df_hyp))
df_hyp.to_csv("novel_compositions_recheck.csv", index=False)
json.dump(cache, open("mp_novel_lookup_cache.json", "w"), indent=1)
print("saved novel_compositions_recheck.csv")
