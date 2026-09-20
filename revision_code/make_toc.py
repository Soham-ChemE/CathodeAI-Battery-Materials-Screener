"""Table-of-contents graphic: 8 cm x 4 cm at 600 dpi (1890 x 945 px), two panels."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import spearmanr
R = json.load(open("analysis_dsi_results.json")); V = R["val"]; hv = R["heur_val"]
val_exp = {"LiCoO2": 500, "LiFePO4": 2000, "LiMnO2": 300, "NMC111": 1000, "NMC622": 800, "NMC811": 800, "NCA": 500, "LNMO": 1000, "LTO": 10000, "LFMP": 1500, "Li2MnO3": 200}
mats = list(val_exp); exp = np.array([val_exp[m] for m in mats]); dsi = np.array([V["scores"][m] for m in mats]); heur = np.array([hv["preds"][m] for m in mats], float)
CATC = {"D": "#d62728", "C": "#ff7f0e", "B": "#2ca02c", "A": "#1f77b4"}
cm = 1 / 2.54
fig, axes = plt.subplots(1, 2, figsize=(8 * cm, 4 * cm), dpi=600, gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.55})
plt.rcParams.update({"font.size": 5})
ax = axes[0]
for lo, hi, c in [(0, .35, "D"), (.35, .55, "C"), (.55, .75, "B"), (.75, 1.0, "A")]: ax.axhspan(lo, hi, color=CATC[c], alpha=0.10, lw=0)
ax.scatter(exp, heur / heur.max(), s=9, marker="s", color="#999999", edgecolors="k", linewidths=0.3, label=f"metal-identity heuristic (scaled), $\\rho$={hv['rho_nostab']:.2f}", zorder=3)
ax.scatter(exp, dsi, s=11, color="#2ecc71", edgecolors="k", linewidths=0.3, label=f"structure-resolved DSI  $\\rho$={V['rho_bins']:.2f}", zorder=4)
ax.set_xscale("log"); ax.set_ylim(-0.26, 1.02); ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); ax.set_xlabel("experimental cycle life (rank only)", fontsize=5, labelpad=1); ax.set_ylabel("normalised durability score", fontsize=5, labelpad=1)
ax.tick_params(labelsize=4.5, length=1.5, pad=1, width=0.4); [sp.set_linewidth(0.4) for sp in ax.spines.values()]
ax.legend(fontsize=3.8, loc="lower right", frameon=True, framealpha=0.95, handlelength=1, borderpad=0.25, labelspacing=0.2)
for yv, t in [(0.45, "C"), (0.65, "B"), (0.87, "A")]: ax.text(12000, yv, t, fontsize=5, fontweight="bold", color="grey", va="center")
ax.text(12000, 0.17, "D", fontsize=5, fontweight="bold", color="grey", va="center")
ax.set_xlim(120, 16000)
ax.set_title("Structure-resolved index beats\nmetal-identity heuristic (11 cathodes)", fontsize=4.8, pad=2)
ax = axes[1]; pol = sorted(R["polymorph"], key=lambda r: r["E_hull polymorph (meV)"])
names = [p["Space Group"] for p in pol]; vals = [p["DSI"] for p in pol]; cats = [p["DSI category"][0] for p in pol]
ax.bar(range(3), vals, color=[CATC[c] for c in cats], edgecolor="k", linewidth=0.4, width=0.6)
for i, (v, c, p) in enumerate(zip(vals, cats, pol)): ax.text(i, v + 0.03, f"{c}\n$\\Delta V/V$ {p['dV/V (%)']:.0f}%", ha="center", fontsize=4.5, fontweight="bold")
for c in [0.35, 0.55, 0.75]: ax.axhline(c, color="grey", ls=":", lw=0.4)
ax.set_xticks(range(3)); ax.set_xticklabels(names, fontsize=5); ax.set_ylim(0, 1.0); ax.set_ylabel("DSI", fontsize=5, labelpad=1); ax.tick_params(labelsize=4.5, length=1.5, pad=1, width=0.4); [sp.set_linewidth(0.4) for sp in ax.spines.values()]
ax.set_title("One composition, LiCuO$_2$:\nthree durability classes", fontsize=4.8, pad=2)
fig.subplots_adjust(left=0.10, right=0.99, bottom=0.17, top=0.80)
out = "/Users/thegreat/Desktop/Major revision /TOC_graphic"
fig.savefig(out + ".png", dpi=600); fig.savefig(out + ".tif", dpi=600, pil_kwargs={"compression": "tiff_lzw"}); fig.savefig(out + ".pdf")
txt = ("A structure-resolved Degradation Screening Index ranks cathode durability better than the metal-identity heuristic (Spearman 0.76 vs 0.55), and one composition, LiCuO2, spans three durability classes across its polymorphs.")
print(len(txt), "chars"); open("/Users/thegreat/Desktop/Major revision /TOC_text.txt", "w").write(txt + "\n")
from PIL import Image; im = Image.open(out + ".png"); print("px", im.size, "-> cm", im.size[0] / 600 * 2.54, im.size[1] / 600 * 2.54)
