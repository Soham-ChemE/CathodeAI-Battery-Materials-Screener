"""Fill the remaining placeholders in main.tex from the Table 2/3 partial results, XGBoost and SHAP outputs."""
import json, re
P = json.load(open("analysis_ml2_partial_id.json")); XGB = json.load(open("xgb_id.json")); SH = json.load(open("shap_id.json")); ML = json.load(open("analysis_ml_results_id.json"))
p = "/Users/thegreat/Desktop/Major revision /main.tex"; s = open(p).read()
t2 = P["table2"]; rows = []
for k, lab in [("Electrochemical only", "Electrochemical only"), ("Structural only (DFT)", "Structural only (DFT)"), ("Combined (final)", "\\textbf{Combined (final)}"), ("MatMiner (Magpie)", "MatMiner (Magpie)"), ("Lasso-selected", "Lasso-selected MatMiner"), ("Full (combined + MatMiner)", "Full (combined + MatMiner)")]:
    r = t2[k]; c = ["%.3f $\\pm$ %.3f" % (r["r2"], r["std"]), "%.3f $\\pm$ %.3f" % (r["r2g"], r["stdg"]), str(r["nfeat"])]
    if "Combined" in k: c = ["\\textbf{%s}" % x for x in c]
    rows.append("%s & %s & %s & %s \\\\" % (lab, *c))
b = ML["r213"]; rows.append("\\hline")
rows.append("$V$, $C$ only (RF) & %.3f $\\pm$ %.3f & -- & 2 \\\\" % tuple(b["V + C only"]))
rows.append("$V$, $C$, $\\rho$ only (RF) & %.3f $\\pm$ %.3f & -- & 3 \\\\" % tuple(b["V + C + density"]))
rows.append("$\\log V$, $\\log C$, $\\log\\rho$ (linear) & %.3f $\\pm$ %.3f & -- & 3 \\\\" % tuple(b["V + C + density (linear on log)"]))
rows.append("$V \\times C \\times \\rho$ (no fitting) & %.3f & -- & 3 \\\\" % b["arith"])
table2 = "\n".join(rows)
t3 = P["table3"]; rows = []
for k, lab, v in [("Linear Regression", "Linear Regression", t3["Linear Regression"]), ("Random Forest", "\\textbf{Random Forest (selected)}", t3["Random Forest"]), ("XGBoost", "XGBoost", XGB), ("Neural Network", "Neural Network", t3["Neural Network"])]:
    c = ["%.3f" % v["r2"], "%.3f" % v["std"], "%.1f" % v["mae"], "%.3f" % v["r2g"], "%.1f" % v["maeg"]]
    if "Random" in k: c = ["\\textbf{%s}" % x for x in c]
    rows.append(lab + " & " + " & ".join(c) + " \\\\")
table3 = "\n".join(rows)
names = {"Capacity (mAh/g)": "Capacity (mAh~g$^{-1}$)", "Avg Voltage (V)": "Avg.\\ voltage (V)", "Density (g/cc)": "Density (g~cm$^{-3}$)", "Volume per Atom (A3)": "Volume per atom (\\AA$^3$)", "Formation Energy (eV/atom)": "Formation energy (eV~atom$^{-1}$)", "Band Gap (eV)": "Band gap (eV)", "Energy Above Hull (eV)": "Energy above hull (eV~atom$^{-1}$)", "N Elements": "$N$ elements"}
table4 = "\n".join(f"{names[k]} & {v['mean_abs_shap']:.2f} & {v['rf_importance']*100:.1f} \\\\" for k, v in sorted(SH.items(), key=lambda kv: -kv[1]["mean_abs_shap"]))
mm = t2["MatMiner (Magpie)"]["r2"]; mmax = max(t2["MatMiner (Magpie)"]["r2"], t2["Lasso-selected"]["r2"], t2["Structural only (DFT)"]["r2"])
for tok, val in [("%%TABLE2%%", table2), ("%%TABLE3%%", table3), ("%%TABLE4%%", table4), ("%%MM_R2%%", f"{mm:.2f}$"), ("%%MM_MAX%%", f"{mmax:.2f}")]:
    assert s.count(tok) == 1, tok; s = s.replace(tok, val)
# the abstract placeholder was written as "($R^2 = $%%MM_R2%%," -> fix spacing to "($R^2 = 0.xx$,"
s = s.replace("($R^2 = $" + f"{mm:.2f}$", f"($R^2 = {mm:.2f}$")
# Table 3 text: name the best architecture honestly
open(p, "w").write(s)
print("filled. remaining placeholders:", re.findall(r"%%[A-Z0-9_]+%%", s))
print("Table2 rows:\n" + table2); print("Table3:\n" + table3); print("Table4:\n" + table4)
json.dump({"table2": table2, "table3": table3, "table4": table4}, open("tables_pending_filled.json", "w"), indent=1)
