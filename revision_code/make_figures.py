"""Regenerate all manuscript figures with legible fonts and panel labels (R2.3-R2.7).
Single-column figures: figsize width 7 in; double-column (figure*): width 14 in. Fonts >= 11 pt."""
import json, pickle, os, re, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.stats import spearmanr, pearsonr, rankdata
OUT = "/Users/thegreat/Desktop/Major revision /figures_revised/"; os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12, "legend.fontsize": 10.5, "xtick.labelsize": 11, "ytick.labelsize": 11, "figure.dpi": 100, "savefig.dpi": 300})
def label(ax, s, x=-0.12, y=1.06): ax.text(x, y, s, transform=ax.transAxes, fontsize=15, fontweight="bold", va="top", ha="left")
def save(fig, name): fig.tight_layout(); fig.savefig(OUT + name, bbox_inches="tight"); plt.close(fig); print("saved", name)
def mp(f):  # Li0-1CuO2 -> Li$_{0-1}$CuO$_2$
    f = re.sub(r"^Li([\d\.]+)-([\d\.]+)", r"Li$_{\1-\2}$", f)
    f = re.sub(r"(?<=[A-Za-z\)])(\d+)", r"$_{\1}$", f); return f
st = pickle.load(open("repro_state_id.pkl", "rb")); stf = pickle.load(open("repro_state.pkl", "rb"))
df = pd.read_pickle("df813_dsi.pkl"); R = json.load(open("analysis_dsi_results.json")); ML = json.load(open("analysis_ml_results_id.json"))
ML2 = json.load(open("analysis_ml2_partial_id.json")) if os.path.exists("analysis_ml2_partial_id.json") else None
XGB = json.load(open("xgb_id.json")) if os.path.exists("xgb_id.json") else None
el = json.load(open("mpdata/electrodes_Li.json")); comb = st["combined_features"]; dfm = st["df_ml3"]; target = "Energy Density (Wh/L)"
CAT = ["D (low)", "C (moderate)", "B (high)", "A (very high)"]; CATC = {"D (low)": "#d62728", "C (moderate)": "#ff7f0e", "B (high)": "#2ca02c", "A (very high)": "#1f77b4"}
def cat(d): return "D (low)" if d < 0.35 else "C (moderate)" if d < 0.55 else "B (high)" if d < 0.75 else "A (very high)"
NORM_VOL, NORM_STAB = 14.6, 0.190
def dsi(v, s, b, p, w=(0.5, 0.35, 0.15), bonus=0.10):
    d = w[0] * max(0, 1 - v / NORM_VOL) + w[1] * max(0, 1 - s / NORM_STAB) + w[2] * max(0, 1 - abs(b - 2) / 4); return min(1, d + bonus) if p else d
val = {"LiCoO2": (500, 2.0, 0.02, 0.00, False, "Layered"), "LiFePO4": (2000, 6.81, 0.00, 3.594, True, "Olivine"), "LiMnO2": (300, 16.0, 0.05, 0.00, False, "Layered"),
       "NMC111": (1000, 2.5, 0.03, 1.50, False, "Layered"), "NMC622": (800, 4.0, 0.04, 1.20, False, "Layered"), "NMC811": (800, 4.0, 0.06, 0.80, False, "Layered"),
       "NCA": (500, 5.0, 0.08, 0.70, False, "Layered"), "LNMO": (1000, 2.5, 0.02, 2.00, False, "Spinel"), "LTO": (10000, 0.1, 0.00, 2.72, False, "Spinel"),
       "LFMP": (1500, 5.0, 0.00, 3.50, True, "Olivine"), "Li2MnO3": (200, 8.0, 0.10, 1.317, False, "Layered")}
mats = list(val); exp = np.array([val[m][0] for m in mats]); dsc = np.array([dsi(*val[m][1:5]) for m in mats])
dbin = np.array([300 if d < .35 else 750 if d < .55 else 1500 if d < .75 else 2200 for d in dsc]); single = np.array([2200 if val[m][1] < 3 else 1500 if val[m][1] < 7 else 750 if val[m][1] < 12 else 300 for m in mats])
sv_ = [max(0, 1 - val[m][1] / NORM_VOL) for m in mats]; ss_ = [max(0, 1 - val[m][2] / NORM_STAB) for m in mats]; sb_ = [max(0, 1 - abs(val[m][3] - 2) / 4) for m in mats]
which = sys.argv[1:] or ["all"]
def want(n): return "all" in which or n in which

# ---------------- Fig 1: screening funnel ----------------
if want("f1"):
    zone_n = R["zone_... & top-25% ED"][1]
    stages = [("Li insertion electrodes (Materials Project)", 2774), ("Layers 1-2: 2.5-5.0 V, >50 mAh g$^{-1}$", 1886), ("Layer 4: toxic/rare-element exclusion", 1864),
              ("Layer 3: oxide frameworks (halide, sulfide, nitride removed)", 813), ("Layers 5-8 scored; DSI computable (band gap of discharged structure)", 787), (f"Discovery zone (top-quartile composite, $E_\\mathrm{{hull}}$<50 meV atom$^{{-1}}$, top-quartile ED)", zone_n)]
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for i, (lab, n) in enumerate(stages):
        w = n / 2774; ax.barh(-i, w, left=(1 - w) / 2, height=0.72, color=plt.cm.viridis(0.15 + 0.7 * i / 5), edgecolor="black")
        if i < 5: ax.text(0.5, -i, f"{n:,}", ha="center", va="center", color="white", fontweight="bold", fontsize=13)
        else: ax.text(0.5 + w / 2 + 0.03, -i, f"{n:,}", ha="left", va="center", color="black", fontweight="bold", fontsize=13); ax.text(1.03, -i, "", va="center")
        ax.text(1.03 if i < 5 else 1.10, -i, lab, va="center", fontsize=10.5)
    ax.set_xlim(0, 2.6); ax.set_ylim(-5.6, 0.6); ax.axis("off"); ax.set_title("Screening funnel: 2,774 entries to a discovery zone of %d compositions" % zone_n, fontsize=12, loc="left")
    save(fig, "cathodeai_complete_analysis.png")

# ---------------- Fig 2: feature sets ----------------
if want("f2") and ML2:
    T2 = ML2["table2"]; names = ["Electrochemical only", "Structural only (DFT)", "Combined (final)", "MatMiner (Magpie)", "Lasso-selected", "Full (combined + MatMiner)"]
    short = ["Electro-\nchemical (4)", "Structural (6)", "Combined (8)", f"MatMiner ({T2['MatMiner (Magpie)']['nfeat']})", f"Lasso ({T2['Lasso-selected']['nfeat']})", f"Full ({T2['Full (combined + MatMiner)']['nfeat']})"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    x = np.arange(len(names)); w = 0.38
    axes[0].bar(x - w / 2, [T2[n]["r2"] for n in names], w, yerr=[T2[n]["std"] for n in names], capsize=4, color="#1f77b4", label="Random 5-fold CV")
    axes[0].bar(x + w / 2, [T2[n]["r2g"] for n in names], w, yerr=[T2[n]["stdg"] for n in names], capsize=4, color="#ff7f0e", label="Grouped 5-fold CV (base formula)")
    axes[0].axhline(ML["r213"]["V + C + density"][0], color="k", ls="--", lw=1.5, label=f"V + C + $\\rho$ only (RF): {ML['r213']['V + C + density'][0]:.3f}")
    axes[0].set_xticks(x); axes[0].set_xticklabels(short, fontsize=9.5); axes[0].set_ylabel("Cross-validated $R^2$"); axes[0].set_ylim(0, 1.08); axes[0].legend(loc="lower right", fontsize=9); label(axes[0], "(a)")
    rf = st["rf_combined"]; imp = sorted(zip(comb, rf.feature_importances_), key=lambda t: t[1])
    axes[1].barh([f.replace(" (A3)", " (Å$^3$)").replace("Avg ", "") for f, _ in imp], [i for _, i in imp], color=["#e74c3c" if ("Voltage" in f or "Capacity" in f) else "#2ecc71" for f, _ in imp], edgecolor="black")
    for j, (_, i) in enumerate(imp): axes[1].text(i + 0.005, j, f"{i:.3f}", va="center", fontsize=10)
    axes[1].set_xlabel("Random Forest impurity importance"); axes[1].set_xlim(0, 0.95); axes[1].legend(handles=[Patch(color="#e74c3c", label="Electrochemical"), Patch(color="#2ecc71", label="Structural (DFT)")], fontsize=9.5); label(axes[1], "(b)", x=-0.55)
    yp = rf.predict(st["X3_test"]); yt = st["y3_test"]; from sklearn.metrics import r2_score, mean_absolute_error
    axes[2].scatter(yt, yp, s=18, alpha=0.6, color="#2ecc71", edgecolors="k", linewidths=0.3); m = max(yt.max(), yp.max()); axes[2].plot([0, m], [0, m], "r--", lw=1.5)
    axes[2].set_xlabel("Actual energy density (Wh L$^{-1}$)"); axes[2].set_ylabel("Predicted (Wh L$^{-1}$)"); axes[2].set_title(f"Held-out test (n={len(yt)}): $R^2$={r2_score(yt, yp):.3f}, MAE={mean_absolute_error(yt, yp):.0f} Wh L$^{{-1}}$", fontsize=11.5); label(axes[2], "(c)")
    save(fig, "cathodeai_feature_engineering.png")

# ---------------- Fig 3: ML vs arithmetic ----------------
if want("f3"):
    from sklearn.metrics import r2_score
    y = dfm[target].values; arith = dfm["Avg Voltage (V)"] * dfm["Capacity (mAh/g)"] * dfm["Density (g/cc)"]
    Xs = st["X3scaler"].transform(dfm[comb].values); yml = st["rf_combined"].predict(Xs)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].scatter(y, arith, s=14, alpha=0.5, color="#3498db", label=f"$V\\times C\\times\\rho$: $R^2$={r2_score(y, arith):.3f}"); axes[0].scatter(y, yml, s=14, alpha=0.5, color="#2ecc71", label=f"Random Forest (8 features): $R^2$={r2_score(y, yml):.3f}")
    m = y.max(); axes[0].plot([0, m], [0, m], "k--", lw=1); axes[0].set_xlabel("Materials Project energy density (Wh L$^{-1}$)"); axes[0].set_ylabel("Estimate (Wh L$^{-1}$)"); axes[0].legend(fontsize=9.5); axes[0].set_title("Complete inputs (n=%d, ID-level structures)" % len(y), fontsize=11.5); label(axes[0], "(a)")
    r = ML["r216"]
    labs = ["Complete\nrows\n(n=%d)" % r["n_test_complete"], "Imputed\nrows\n(n=%d)" % r["n_test_imp"]]
    axes[1].bar(labs, [r["test_complete"], r["test_imputed"]], color=["#2ecc71", "#e74c3c"], edgecolor="k", width=0.55)
    for i, v in enumerate([r["test_complete"], r["test_imputed"]]): axes[1].text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Held-out $R^2$ of the 8-feature model"); axes[1].set_ylim(0, 1.1); axes[1].set_title("30% of capacity values removed\n(mean-imputed at prediction time)", fontsize=11.5); label(axes[1], "(b)")
    meth = ["ML\nmean-imp. C", "Arithmetic\nmean-imp. C", "Arithmetic\nRF-imp. C", "ML\nRF-imp. C"]; vals = [r["test_imputed"], r["arith_mean_imp"], r["arith_rf_imp"], r["ml_rf_imp"]]
    axes[2].bar(meth, vals, color=["#e74c3c", "#3498db", "#3498db", "#e74c3c"], edgecolor="k", width=0.6)
    for i, v in enumerate(vals): axes[2].text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=12, fontweight="bold")
    axes[2].set_ylabel("Held-out $R^2$ on imputed rows (n=%d)" % r["n_test_imp"]); axes[2].set_ylim(0, 0.6); axes[2].set_xticks(range(4)); axes[2].set_xticklabels(meth, fontsize=9, rotation=12); axes[2].set_title("Imputation baselines on the same rows", fontsize=11.5); label(axes[2], "(c)")
    save(fig, "cathodeai_ml_vs_arithmetic.png")

# ---------------- Fig 4: SHAP ----------------
if want("f4") and os.path.exists("shap_values_id.npz"):
    z = np.load("shap_values_id.npz", allow_pickle=True); sv, X, feats = z["sv"], z["X"], list(z["features"])
    fig, axes = plt.subplots(1, 3, figsize=(15, 5)); msv = np.abs(sv).mean(0); o = np.argsort(msv)
    axes[0].barh([feats[i].replace(" (A3)", " (Å$^3$)").replace("Avg ", "") for i in o], msv[o], color=["#e74c3c" if ("Voltage" in feats[i] or "Capacity" in feats[i]) else "#2ecc71" for i in o], edgecolor="k")
    for j, i in enumerate(o): axes[0].text(msv[i] + 5, j, f"{msv[i]:.1f}", va="center", fontsize=10)
    axes[0].set_xlabel("Mean |SHAP| (Wh L$^{-1}$)"); axes[0].set_xlim(0, msv.max() * 1.18); label(axes[0], "(a)", x=-0.55)
    ci = feats.index("Capacity (mAh/g)"); sc = axes[1].scatter(X[:, ci], sv[:, ci], c=X[:, ci], cmap="viridis", s=10, alpha=0.6); axes[1].axhline(0, color="r", ls="--"); axes[1].set_xlabel("Capacity (mAh g$^{-1}$)"); axes[1].set_ylabel("SHAP value (Wh L$^{-1}$)"); plt.colorbar(sc, ax=axes[1], label="Capacity (mAh g$^{-1}$)"); label(axes[1], "(b)")
    fi = feats.index("Formation Energy (eV/atom)"); sc = axes[2].scatter(X[:, fi], sv[:, fi], c=z["y"], cmap="RdYlGn", s=10, alpha=0.6); axes[2].axhline(0, color="r", ls="--"); axes[2].set_xlabel("Formation energy (eV atom$^{-1}$)"); axes[2].set_ylabel("SHAP value (Wh L$^{-1}$)"); plt.colorbar(sc, ax=axes[2], label="Energy density (Wh L$^{-1}$)"); label(axes[2], "(c)")
    save(fig, "cathodeai_shap_analysis.png")

# ---------------- Fig 5: heuristic vs DSI ----------------
if want("f5"):
    d = df.dropna(subset=["DSI"]); fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    rho = spearmanr(d["Estimated Cycles"], d["DSI"])[0]; r = pearsonr(d["Estimated Cycles"], d["DSI"])[0]
    axes[0].scatter(d["Estimated Cycles"], d["DSI"], s=16, alpha=0.5, color="steelblue", edgecolors="k", linewidths=0.3)
    for c in [0.35, 0.55, 0.75]: axes[0].axhline(c, color="grey", ls=":", lw=1)
    axes[0].set_xlabel("Metal-identity heuristic (cycles)"); axes[0].set_ylabel("DSI score"); axes[0].set_title(f"n={len(d)}: Spearman $\\rho$={rho:.2f}, Pearson $r$={r:.2f}", fontsize=11.5); label(axes[0], "(a)")
    axes[1].hist(df["Max Volume Change (%)"].clip(upper=50), bins=40, color="#e74c3c", edgecolor="k", alpha=0.85); axes[1].axvline(14.6, color="k", ls="--", lw=1.5, label="$S_\\mathrm{vol}$ normalisation bound (14.6%)"); axes[1].set_xlabel("Maximum delithiation volume change $\\Delta V/V$ (%)"); axes[1].set_ylabel("Count (813 oxide candidates)"); axes[1].legend(fontsize=9.5); label(axes[1], "(b)")
    for c in CAT: s = d[d["DSI category"] == c]; axes[2].scatter(s["Max Volume Change (%)"].clip(upper=50), s["Energy Density (Wh/L)"], s=18, alpha=0.7, color=CATC[c], label=f"DSI {c}", edgecolors="k", linewidths=0.3)
    axes[2].set_xlabel("$\\Delta V/V$ (%)"); axes[2].set_ylabel("Energy density (Wh L$^{-1}$)"); axes[2].legend(fontsize=9.5); label(axes[2], "(c)")
    save(fig, "cathodeai_volume_change.png")

# ---------------- Fig 6: LiCuO2 polymorphs ----------------
if want("f6"):
    dp = st["df_poly"].sort_values("E_hull (meV/atom)"); pe = pd.DataFrame(R["polymorph"]); fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    sc = axes[0].scatter(dp["Vol/atom"], dp["E_hull (meV/atom)"], c=dp["Density"], cmap="RdYlGn_r", s=160, edgecolors="k")
    for _, r_ in dp.iterrows(): axes[0].annotate(r_["Space Group"], (r_["Vol/atom"], r_["E_hull (meV/atom)"]), xytext=(6, 4), textcoords="offset points", fontsize=10.5, fontweight="bold")
    axes[0].axhline(50, color="orange", ls="--", label="50 meV atom$^{-1}$"); plt.colorbar(sc, ax=axes[0], label="Density (g cm$^{-3}$)"); axes[0].set_xlabel("Volume per atom (Å$^3$)"); axes[0].set_ylabel("$E_\\mathrm{hull}$ (meV atom$^{-1}$)"); axes[0].legend(fontsize=9.5); axes[0].set_title("      Eight LiCuO$_2$ polymorphs (static properties)", fontsize=11.5, loc="left"); label(axes[0], "(a)")
    pe = pe.sort_values("E_hull polymorph (meV)"); x = np.arange(len(pe)); w = 0.38
    ax2 = axes[1]; ax2.bar(x - w / 2, pe["dV/V (%)"], w, color="#3498db", edgecolor="k", label="$\\Delta V/V$ (%)"); ax2.set_ylabel("$\\Delta V/V$ (%)", color="#3498db")
    ax2b = ax2.twinx(); ax2b.bar(x + w / 2, pe["E_hull charge (eV)"] * 1000, w, color="#e67e22", edgecolor="k", label="$E_\\mathrm{hull,charge}$"); ax2b.set_ylabel("$E_\\mathrm{hull,charge}$ (meV atom$^{-1}$)", color="#e67e22")
    ax2.set_xticks(x); ax2.set_xticklabels([f"{r_['Space Group']}\n{mp(r_['battery_formula'])}" for _, r_ in pe.iterrows()], fontsize=10); ax2.set_title("Polymorph-resolved electrode entries (3 of 8)", fontsize=11.5); label(ax2, "(b)")
    ax3 = axes[2]; cols = [CATC[c] for c in pe["DSI category"]]; ax3.bar(x, pe["DSI"], color=cols, edgecolor="k", width=0.6)
    for c in [0.35, 0.55, 0.75]: ax3.axhline(c, color="grey", ls=":", lw=1)
    for i, (_, r_) in enumerate(pe.iterrows()): ax3.text(i, r_["DSI"] + 0.02, f"{r_['DSI']:.2f}\n{r_['DSI category'].split(' ')[0]}", ha="center", fontsize=10.5, fontweight="bold")
    ax3.set_xticks(x); ax3.set_xticklabels(pe["Space Group"], fontsize=11); ax3.set_ylim(0, 1.0); ax3.set_ylabel("DSI score"); ax3.set_title("DSI at fixed composition LiCuO$_2$", fontsize=11.5); label(ax3, "(c)")
    save(fig, "cathodeai_polymorph_analysis.png")

# ---------------- Fig 7: DSI validation ----------------
if want("f7"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5)); corr = pd.DataFrame({"$S_\\mathrm{vol}$": sv_, "$S_\\mathrm{stab}$": ss_, "$S_\\mathrm{bg}$": sb_}).corr()
    im = axes[0].imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1); axes[0].set_xticks(range(3)); axes[0].set_yticks(range(3)); axes[0].set_xticklabels(corr.columns); axes[0].set_yticklabels(corr.columns)
    for i in range(3):
        for j in range(3): axes[0].text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=13, color="white" if abs(corr.values[i, j]) > 0.5 else "black")
    plt.colorbar(im, ax=axes[0], fraction=0.046); axes[0].set_title("Descriptor correlations (n=11)", fontsize=11.5); label(axes[0], "(a)")
    sc = axes[1].scatter(sv_, ss_, c=dsc, cmap="viridis", s=170, edgecolors="k", vmin=0, vmax=1)
    for i, m in enumerate(mats): axes[1].annotate(m, (sv_[i], ss_[i]), xytext=(6, 4), textcoords="offset points", fontsize=10)
    plt.colorbar(sc, ax=axes[1], label="DSI score"); axes[1].set_xlabel("$S_\\mathrm{vol}$"); axes[1].set_ylabel("$S_\\mathrm{stab}$"); label(axes[1], "(b)")
    for lo, hi, c in [(0, .35, "D (low)"), (.35, .55, "C (moderate)"), (.55, .75, "B (high)"), (.75, 1.0, "A (very high)")]: axes[2].axhspan(lo, hi, color=CATC[c], alpha=0.12)
    axes[2].scatter(exp, dsc, s=140, color="#2ecc71", edgecolors="k", zorder=5, label=f"DSI: $\\rho$={spearmanr(exp, dbin)[0]:.2f} (categories), {spearmanr(exp, dsc)[0]:.2f} (score)")
    axes[2].scatter(exp, [max(0, 1 - val[m][1] / NORM_VOL) for m in mats], s=90, marker="s", color="#e74c3c", edgecolors="k", zorder=4, label=f"Single $S_\\mathrm{{vol}}$: $\\rho$={spearmanr(exp, single)[0]:.2f}")
    for i, m in enumerate(mats): axes[2].annotate(m, (exp[i], dsc[i]), xytext=(5, 5), textcoords="offset points", fontsize=9.5)
    axes[2].set_xscale("log"); axes[2].set_xlabel("Representative experimental cycle life (log scale)"); axes[2].set_ylabel("Normalised score"); axes[2].legend(fontsize=9, loc="lower right"); axes[2].set_ylim(0, 1.05)
    for yv, t in [(0.17, "D"), (0.45, "C"), (0.65, "B"), (0.87, "A")]: axes[2].text(150, yv, t, fontsize=12, fontweight="bold", color="grey")
    label(axes[2], "(c)"); save(fig, "cathodeai_dsi_model.png")

# ---------------- Fig 8: bootstrap ----------------
if want("f8"):
    rng = np.random.RandomState(42); n = 11
    def sp(x, y):
        rx, ry = rankdata(x), rankdata(y); return 0.0 if np.std(ry) == 0 else 1 - 6 * np.sum((rx - ry) ** 2) / (n * (n * n - 1))
    bd, bs = [], []
    for _ in range(10000): i = rng.choice(n, n); bd.append(sp(exp[i], dbin[i])); bs.append(sp(exp[i], single[i]))
    bd, bs = np.array(bd), np.array(bs); fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    axes[0].hist(bs, bins=50, alpha=0.6, color="#e74c3c", label="Single descriptor"); axes[0].hist(bd, bins=50, alpha=0.6, color="#2ecc71", label="DSI"); axes[0].set_xlabel("Bootstrap Spearman $\\rho$"); axes[0].set_ylabel("Count (10,000 resamples)"); axes[0].legend(); label(axes[0], "(a)")
    for k, (lab, arr, pt, c) in enumerate([("Single", bs, spearmanr(exp, single)[0], "#e74c3c"), ("DSI", bd, spearmanr(exp, dbin)[0], "#2ecc71")]):
        lo, hi = np.percentile(arr, [2.5, 97.5]); axes[1].errorbar(k, pt, yerr=[[pt - lo], [hi - pt]], fmt="o", ms=10, capsize=8, color=c, lw=2); axes[1].text(k + 0.08, pt, f"{pt:.3f}\n[{lo:.2f}, {hi:.2f}]", va="center", fontsize=10.5)
    axes[1].set_xticks([0, 1]); axes[1].set_xticklabels(["Single descriptor", "DSI"]); axes[1].set_xlim(-0.5, 1.8); axes[1].set_ylabel("Spearman $\\rho$ (point estimate, 95% CI)"); axes[1].axhline(0, color="k", lw=0.8); label(axes[1], "(b)")
    save(fig, "cathodeai_bootstrap_ci.png")

# ---------------- Fig 9: weight robustness + nested LOO ----------------
if want("f9"):
    schemes = {"Expert\n(50/35/15)": (0.5, 0.35, 0.15), "Equal\n(33/33/33)": (1/3, 1/3, 1/3), "Vol-dominant\n(70/20/10)": (0.7, 0.2, 0.1), "Stab-dominant\n(20/70/10)": (0.2, 0.7, 0.1), "No band gap\n(50/50/0)": (0.5, 0.5, 0), "No stability\n(50/0/50)": (0.5, 0, 0.5)}
    rh = [spearmanr(exp, [300 if d < .35 else 750 if d < .55 else 1500 if d < .75 else 2200 for d in [dsi(*val[m][1:5], w=w) for m in mats]])[0] for w in schemes.values()]
    base = spearmanr(exp, single)[0]; nest = R["val"]["nested"]["rho"]
    fig, ax = plt.subplots(figsize=(9, 5)); ax.bar(range(6), rh, color=["#2ecc71" if v > base else "#e74c3c" for v in rh], edgecolor="k", width=0.65)
    for i, v in enumerate(rh): ax.text(i, v + 0.012, f"{v:.3f}", ha="center", fontweight="bold")
    ax.axhline(base, color="navy", ls="--", lw=2, label=f"Single-descriptor baseline ($\\rho$={base:.3f})"); ax.axhline(nest, color="purple", ls=":", lw=2, label=f"Nested leave-one-out weight optimisation ($\\rho$={nest:.2f})")
    ax.set_xticks(range(6)); ax.set_xticklabels(list(schemes), fontsize=10); ax.set_ylabel("Spearman $\\rho$ vs experimental rank"); ax.set_ylim(0, 0.9); ax.legend(fontsize=10, loc="upper right"); save(fig, "cathodeai_weight_robustness.png")

# ---------------- Fig 10: full dataset ----------------
if want("f10"):
    vv, ss = [], []
    for e in el:
        if e.get("max_delta_volume") is not None and e.get("stability_charge") is not None and e["stability_charge"] >= 0 and e.get("average_voltage") is not None and 2.5 <= e["average_voltage"] <= 5.0:
            vv.append(abs(e["max_delta_volume"]) * 100); ss.append(e["stability_charge"])
    vv, ss = np.array(vv), np.array(ss); svn = np.maximum(0, 1 - vv / NORM_VOL); ssn = np.maximum(0, 1 - ss / NORM_STAB)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    axes[0].hist(np.clip(vv, 0, 40), bins=50, color="#3498db", edgecolor="k"); axes[0].axvline(14.6, color="k", ls="--", label="95th percentile = 14.6%"); axes[0].set_xlabel("$\\Delta V/V$ (%) (clipped at 40%)"); axes[0].set_ylabel("Count"); axes[0].legend(fontsize=9.5); axes[0].set_title(f"Distribution of $\\Delta V/V$ (n={len(vv)})", fontsize=11.5); label(axes[0], "(a)")
    axes[1].hist(np.clip(ss * 1000, 0, 400), bins=50, color="#e67e22", edgecolor="k"); axes[1].axvline(190, color="k", ls="--", label="95th percentile = 190 meV atom$^{-1}$"); axes[1].set_xlabel("$E_\\mathrm{hull,charge}$ (meV atom$^{-1}$) (clipped at 400)"); axes[1].set_ylabel("Count"); axes[1].legend(fontsize=9.5); axes[1].set_title("Distribution of $E_\\mathrm{hull,charge}$", fontsize=11.5); label(axes[1], "(b)")
    r = pearsonr(svn, ssn)[0]; axes[2].scatter(svn, ssn, s=8, alpha=0.35, color="purple"); axes[2].set_xlabel("$S_\\mathrm{vol}$"); axes[2].set_ylabel("$S_\\mathrm{stab}$"); axes[2].set_title(f"Normalised scores: Pearson $r$={r:.3f}", fontsize=11.5); label(axes[2], "(c)")
    save(fig, "cathodeai_full_dataset_correlation.png")

# ---------------- Fig 11: mechanism-resolved ----------------
if want("f11"):
    mech = {"LiCoO2": "Phase transformation/surface", "LiFePO4": "Volume-change dominated", "LiMnO2": "Phase transformation/surface", "NMC111": "Phase transformation/surface", "NMC622": "Phase transformation/surface", "NMC811": "Phase transformation/surface", "NCA": "Phase transformation/surface", "LNMO": "Mixed", "LTO": "Mixed", "LFMP": "Volume-change dominated", "Li2MnO3": "Phase transformation/surface"}
    mc = {"Volume-change dominated": "#2ecc71", "Phase transformation/surface": "#e74c3c", "Mixed": "#f39c12"}
    re_, rd_ = rankdata(exp), rankdata(dsc); dr = np.abs(re_ - rd_)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].scatter(exp, dsc, c=[mc[mech[m]] for m in mats], s=150, edgecolors="k", zorder=5)
    for i, m in enumerate(mats): axes[0].annotate(m, (exp[i], dsc[i]), xytext=(5, 4), textcoords="offset points", fontsize=9.5)
    axes[0].set_xscale("log"); axes[0].set_xlabel("Representative experimental cycle life (log)"); axes[0].set_ylabel("DSI score"); axes[0].legend(handles=[Patch(color=c, label=k) for k, c in mc.items()], fontsize=9); axes[0].set_title(f"Spearman $\\rho$={spearmanr(exp, dsc)[0]:.2f} (n=11)", fontsize=11.5); label(axes[0], "(a)")
    order = list(mc); axes[1].boxplot([dr[[mech[m] == k for m in mats]] for k in order], labels=["Volume\nchange", "Phase transf./\nsurface", "Mixed"], patch_artist=True, medianprops=dict(color="k"))
    for p, k in zip(axes[1].patches, order): p.set_facecolor(mc[k]); p.set_alpha(0.7)
    axes[1].set_ylabel("|rank(experiment) $-$ rank(DSI)|"); axes[1].set_title("Rank disagreement by degradation mechanism", fontsize=11.5); label(axes[1], "(b)")
    axes[2].scatter([val[m][1] for m in mats], dr, c=[mc[mech[m]] for m in mats], s=150, edgecolors="k", zorder=5)
    for i, m in enumerate(mats): axes[2].annotate(m, (val[m][1], dr[i]), xytext=(5, 4), textcoords="offset points", fontsize=9.5)
    axes[2].set_xlabel("$\\Delta V/V$ (%)"); axes[2].set_ylabel("|rank(experiment) $-$ rank(DSI)|"); label(axes[2], "(c)"); save(fig, "cathodeai_expanded_validation.png")

# ---------------- Fig 12: HHI ----------------
if want("f12"):
    supply = {"Co": ({"DRC": 70, "Russia": 5, "Australia": 4, "Philippines": 4, "Cuba": 3, "Other": 14}, 33, True), "Ni": ({"Indonesia": 37, "Philippines": 13, "Russia": 9, "NewCal": 8, "Australia": 6, "Other": 27}, 14, True),
              "Li": ({"Australia": 46, "Chile": 30, "China": 15, "Argentina": 6, "Other": 3}, 22, True), "Mn": ({"SouthAfrica": 36, "Gabon": 20, "Australia": 15, "China": 13, "Ghana": 7, "Other": 9}, 2, False),
              "Fe": ({"Australia": 38, "Brazil": 20, "China": 15, "India": 8, "Russia": 5, "Other": 14}, 0.1, False), "P": ({"China": 44, "Morocco": 14, "Egypt": 5, "Algeria": 4, "Russia": 4, "Other": 29}, 0.8, False),
              "Cu": ({"Chile": 27, "Peru": 10, "China": 8, "DRC": 8, "USA": 6, "Other": 41}, 8.5, False), "Ti": ({"China": 45, "Japan": 18, "Russia": 12, "Kazakhstan": 8, "Ukraine": 6, "Other": 11}, 11, False)}
    hhi = {k: sum(s ** 2 for s in v[0].values()) for k, v in supply.items()}; fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ks = sorted(hhi, key=hhi.get, reverse=True); axes[0].bar(ks, [hhi[k] for k in ks], color=["#e74c3c" if supply[k][2] else "#3498db" for k in ks], edgecolor="k")
    axes[0].axhline(2500, color="k", ls="--", label="Highly concentrated (>2,500)"); axes[0].axhline(1500, color="grey", ls=":", label="Moderately concentrated (>1,500)"); axes[0].set_ylabel("HHI (national production shares)"); axes[0].legend(handles=axes[0].get_legend_handles_labels()[0] + [Patch(color="#e74c3c", label="IRA-designated critical mineral"), Patch(color="#3498db", label="Not IRA-designated")], fontsize=9.5); label(axes[0], "(a)")
    crit = {"Co": 0.95, "Ni": 0.55, "Li": 0.60, "Mn": 0.30, "Fe": 0.05, "P": 0.05, "Cu": 0.25, "Ti": 0.20}
    for k in ks: axes[1].scatter(supply[k][1], 1 - crit[k], s=hhi[k] / 12, color="#e74c3c" if supply[k][2] else "#3498db", edgecolors="k", alpha=0.8); axes[1].annotate(k, (supply[k][1], 1 - crit[k]), xytext=(8, 4), textcoords="offset points", fontsize=11)
    axes[1].set_xscale("log"); axes[1].set_xlabel("Raw-material price (US$ kg$^{-1}$, log)"); axes[1].set_ylabel("Element supply-chain score $1-$criticality"); axes[1].set_title("Bubble size $\\propto$ HHI", fontsize=11.5); label(axes[1], "(b)")
    save(fig, "cathodeai_supply_chain_hhi.png")

# ---------------- Fig 13: PO4 comparison with and without design bonuses ----------------
if want("f13"):
    po = df["Formula"].str.contains("PO"); fig, axes = plt.subplots(2, 3, figsize=(15, 8.5)); rows = R["r220"]["rows"]
    panels = [("Thermal Safety Score", "Thermal safety (with +0.15 PO$_4$ bonus)"), ("Thermal Safety Score (no PO4 bonus)", "Thermal safety (bonus removed)"), ("DSI", "DSI (with +0.10 PO$_4$ bonus)"), ("DSI (no PO4 bonus)", "DSI (bonus removed)"), ("Energy Density (Wh/L)", "Energy density (Wh L$^{-1}$)"), ("Solid State Score", "Solid-state compatibility score")]
    for ax, (col, ttl), lab in zip(axes.flat, panels, "abcdef"):
        a, b = df.loc[~po, col].dropna(), df.loc[po, col].dropna(); bp = ax.boxplot([a, b], labels=[f"Other\n(n={len(a)})", f"P-containing\n(n={len(b)})"], patch_artist=True, medianprops=dict(color="k", lw=2), showfliers=False)
        bp["boxes"][0].set_facecolor("lightcoral"); bp["boxes"][1].set_facecolor("#2ecc71"); p = rows[col][2]
        ax.set_title(f"{ttl}\nWelch $p$ = {p:.1e}" if p < 1e-3 else f"{ttl}\nWelch $p$ = {p:.2f}", fontsize=11.5); label(ax, f"({lab})")
    save(fig, "cathodeai_po4_comparison.png")

# ---------------- Fig 14: Pareto ----------------
if want("f14"):
    top100 = df.head(100).dropna(subset=["DSI"]).copy()
    def pareto(dfp, c1, c2, m1=True, m2=True):
        v1 = dfp[c1].values * (1 if m1 else -1); v2 = dfp[c2].values * (1 if m2 else -1); keep = np.ones(len(dfp), bool)
        for i in range(len(dfp)):
            for j in range(len(dfp)):
                if i != j and v1[j] >= v1[i] and v2[j] >= v2[i] and (v1[j] > v1[i] or v2[j] > v2[i]): keep[i] = False; break
        return keep
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    for ax, (ttl, c1, c2, m1, m2, col, lab) in zip(axes, [("EV: energy density vs DSI", "Energy Density (Wh/L)", "DSI", True, True, "#e74c3c", "(a)"), ("Consumer: cost vs energy density", "Cost per kWh ($/kWh)", "Energy Density (Wh/L)", False, True, "#3498db", "(b)"), ("Grid: thermal safety vs DSI", "Thermal Safety Score", "DSI", True, True, "#2ecc71", "(c)")]):
        k = pareto(top100, c1, c2, m1, m2); ax.scatter(top100[~k][c1], top100[~k][c2], color="lightgrey", edgecolors="k", linewidths=0.3, s=45, label="Dominated (top-100 composite)")
        fr = top100[k].sort_values(c1); ax.plot(fr[c1], fr[c2], "--", color=col, lw=1.5); ax.scatter(fr[c1], fr[c2], color=col, edgecolors="k", s=120, zorder=5, label="Non-dominated")
        for _, r_ in fr.drop_duplicates("Formula").iterrows(): ax.annotate(mp(r_["Formula"]), (r_[c1], r_[c2]), xytext=(6, 4), textcoords="offset points", fontsize=9.5, fontweight="bold")
        ax.set_xlabel({"Energy Density (Wh/L)": "Energy density (Wh L$^{-1}$)", "Cost per kWh ($/kWh)": "Raw-material cost (US\\$ kWh$^{-1}$)", "Thermal Safety Score": "Thermal safety score"}[c1]); ax.set_ylabel({"DSI": "DSI score", "Energy Density (Wh/L)": "Energy density (Wh L$^{-1}$)"}[c2]); ax.set_title(ttl, fontsize=11.5); ax.legend(fontsize=9.5); label(ax, lab)
    save(fig, "cathodeai_pareto_frontier.png")

# ---------------- Fig 15: price scenarios ----------------
if want("f15"):
    scen = {"Base": {"Co": 33.0, "Ni": 14.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 23.0}, "Co +100%": {"Co": 66.0, "Ni": 14.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 23.0}, "Ni +50%": {"Co": 33.0, "Ni": 21.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 23.0}, "Li -50%": {"Co": 33.0, "Ni": 14.0, "Mn": 1.8, "Fe": 0.1, "Cu": 8.5, "Li": 11.5}, "IRA reshoring": {"Co": 33.0, "Ni": 14.0, "Mn": 0.9, "Fe": 0.05, "Cu": 8.5, "Li": 23.0}}
    def cost_s(f, pr):
        for m, c in pr.items():
            if m in f and m != "Li": return c
        return 20.0
    ranks = {}
    for s, pr in scen.items():
        d2 = df.copy(); d2["sc"] = d2["Formula"].apply(lambda f: cost_s(f, pr)); d2["scs"] = 1 - d2["sc"] / d2["sc"].max()
        d2["S"] = 0.25 * d2["Overall Score"] / d2["Overall Score"].max() + 0.20 * d2["Supply Chain Score"] + 0.15 * d2["Recyclability Score"] + 0.15 * d2["Solid State Score"] + 0.15 * d2["scs"] + 0.10 * d2["Thermal Safety Score"]
        d2 = d2.sort_values("S", ascending=False).drop_duplicates("Formula").reset_index(drop=True); ranks[s] = {f: i + 1 for i, f in enumerate(d2["Formula"])}
    top = list(ranks["Base"])[:8]; M = np.array([[ranks[s][f] for s in scen] for f in top])
    fig, ax = plt.subplots(figsize=(8.5, 5)); im = ax.imshow(M, cmap="RdYlGn_r", vmin=1, vmax=12); plt.colorbar(im, ax=ax, label="Rank (1 = best)")
    ax.set_xticks(range(5)); ax.set_xticklabels(list(scen), rotation=15); ax.set_yticks(range(len(top))); ax.set_yticklabels([mp(f) for f in top])
    for i in range(len(top)):
        for j in range(5): ax.text(j, i, M[i, j], ha="center", va="center", fontweight="bold")
    ax.set_title("Composite rank of the base-case top 8 under five commodity-price scenarios", fontsize=11.5); save(fig, "cathodeai_price_sensitivity.png")

# ---------------- Fig 16: novel compositions ----------------
nv = pd.read_csv("novel_compositions_recheck.csv")
if want("f16"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5)); axes[0].scatter(dfm["Avg Voltage (V)"], dfm[target], s=10, alpha=0.3, color="steelblue", label="Known electrodes (n=%d)" % len(dfm))
    for m, c, lab in [(nv["in_db_correct"], "#2ecc71", "Generated, present in MP"), (~nv["in_db_correct"], "#e74c3c", "Generated, absent from MP")]:
        axes[0].scatter(nv.loc[m, "Avg Voltage (V)"], nv.loc[m, "Predicted ED 4-feature RF (Wh/L)"], marker="*", s=180, color=c, edgecolors="k", label=lab, zorder=5)
    axes[0].set_xlabel("Average voltage (V)"); axes[0].set_ylabel("Energy density (Wh L$^{-1}$)"); axes[0].legend(fontsize=9.5); axes[0].set_title("Generated compositions vs known electrodes", fontsize=11.5); label(axes[0], "(a)")
    ab = nv[~nv["in_db_correct"]].drop_duplicates("Reduced formula").sort_values("Predicted ED 4-feature RF (Wh/L)", ascending=False)
    axes[1].barh([mp(f) for f in ab["Reduced formula"]][::-1], ab["Predicted ED 4-feature RF (Wh/L)"].values[::-1], color="#e74c3c", edgecolor="k")
    for i, v in enumerate(ab["Predicted ED 4-feature RF (Wh/L)"].values[::-1]): axes[1].text(v + 20, i, f"{v:.0f}", va="center", fontsize=10)
    axes[1].set_xlabel("Predicted energy density, 4-feature RF (Wh L$^{-1}$)"); axes[1].set_title("Database-absent generated compositions (n=%d)" % len(ab), fontsize=11.5); axes[1].set_xlim(0, ab["Predicted ED 4-feature RF (Wh/L)"].max() * 1.15); label(axes[1], "(b)", x=-0.3)
    save(fig, "cathodeai_novel_compositions.png")

# ---------------- Fig 17: synthesizability (corrected stoichiometry) ----------------
if want("f17"):
    def cls(e): return "Absent from MP" if pd.isna(e) else "$E_\\mathrm{hull}$ < 50" if e < 50 else "50-100" if e < 100 else "> 100"
    fig, axes = plt.subplots(1, 2, figsize=(13, 5)); c = nv["ehull_meV_correct"].apply(cls).value_counts(); order = [k for k in ["$E_\\mathrm{hull}$ < 50", "50-100", "> 100", "Absent from MP"] if k in c]
    axes[0].pie([c[k] for k in order], labels=[f"{k}\n({c[k]})" for k in order], colors=["#2ecc71", "#f39c12", "#e74c3c", "#3498db"][:len(order)], autopct="%1.0f%%", startangle=90, textprops={"fontsize": 11}); axes[0].set_title("42 generated compositions (as generated)", fontsize=11.5); label(axes[0], "(a)")
    pres = nv[nv["in_db_correct"]].drop_duplicates("Reduced formula").sort_values("ehull_meV_correct"); cols = ["#2ecc71" if v < 50 else "#f39c12" if v < 100 else "#e74c3c" for v in pres["ehull_meV_correct"]]
    axes[1].bar(range(len(pres)), pres["ehull_meV_correct"], color=cols, edgecolor="k"); axes[1].axhline(50, color="orange", ls="--", label="50 meV atom$^{-1}$"); axes[1].axhline(100, color="red", ls="--", label="100 meV atom$^{-1}$")
    axes[1].set_xticks(range(len(pres))); axes[1].set_xticklabels([mp(f) for f in pres["Reduced formula"]], rotation=90, fontsize=9); axes[1].set_ylabel("Minimum $E_\\mathrm{hull}$ of MP entries (meV atom$^{-1}$)"); axes[1].legend(fontsize=9.5); axes[1].set_title("Database-present compositions (%d unique)" % len(pres), fontsize=11.5); label(axes[1], "(b)")
    save(fig, "cathodeai_synthesizability.png")

# ---------------- Fig 18: applicability domain in the 4-feature space ----------------
if want("f18"):
    f4 = ["Avg Voltage (V)", "Capacity (mAh/g)", "Stability Charge (eV)", "Stability Discharge (eV)"]; Xtr = stf["df_filtered"][f4].values; mu, sd = Xtr.mean(0), Xtr.std(0)
    Zt = (Xtr - mu) / sd; Zn = (nv[f4].values - mu) / sd; X1 = np.hstack([np.ones((len(Zt), 1)), Zt]); H = np.linalg.inv(X1.T @ X1)
    lt = np.einsum("ij,jk,ik->i", X1, H, X1); Xn1 = np.hstack([np.ones((len(Zn), 1)), Zn]); ln = np.einsum("ij,jk,ik->i", Xn1, H, Xn1); thr = 3 * X1.shape[1] / len(X1)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5)); axes[0].hist(lt, bins=60, color="steelblue", alpha=0.7, label="Training set (n=%d)" % len(lt), log=True); axes[0].axvline(thr, color="k", ls="--", label=f"Warning leverage 3p/n = {thr:.4f}")
    for v in ln: axes[0].axvline(v, color="#e74c3c", alpha=0.5, lw=1)
    axes[0].plot([], [], color="#e74c3c", label="Generated compositions (n=42)"); axes[0].set_xlabel("Leverage in the 4-feature space of the novel-composition model"); axes[0].set_ylabel("Count (log)"); axes[0].legend(fontsize=9.5); label(axes[0], "(a)")
    im = axes[1].imshow(np.abs(Zn).T, cmap="viridis", aspect="auto", vmin=0, vmax=3); plt.colorbar(im, ax=axes[1], label="|Z| relative to training set"); axes[1].set_yticks(range(4)); axes[1].set_yticklabels(["Voltage", "Capacity", "$E_\\mathrm{hull,charge}$", "$E_\\mathrm{hull,discharge}$"]); axes[1].set_xticks(range(len(nv))); axes[1].set_xticklabels([mp(f) for f in nv["Reduced formula"]], rotation=90, fontsize=7.5); axes[1].set_title(f"max |Z| over all 42 compositions = {np.abs(Zn).max():.2f}", fontsize=11.5); label(axes[1], "(b)")
    save(fig, "cathodeai_applicability_domain.png")

# ---------------- Fig 20: discovery zone ----------------
if want("f20"):
    d = df.dropna(subset=["DSI"]); q = d["Composite (DSI term)"].quantile(.75); qe = d["Energy Density (Wh/L)"].quantile(.75)
    zone = (d["Composite (DSI term)"] >= q) & (d["E_hull struct (meV)"] < 50) & (d["Energy Density (Wh/L)"] >= qe)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2)); sc = axes[0].scatter(d["E_hull struct (meV)"].clip(upper=200), d["Composite (DSI term)"], c=d["Energy Density (Wh/L)"], cmap="RdYlGn", s=22, alpha=0.7, edgecolors="none"); plt.colorbar(sc, ax=axes[0], label="Energy density (Wh L$^{-1}$)")
    axes[0].axvline(50, color="green", ls="--", label="$E_\\mathrm{hull}$(discharged) = 50 meV atom$^{-1}$"); axes[0].axhline(q, color="blue", ls="--", label=f"Top-quartile composite ({q:.3f})"); axes[0].scatter(d[zone]["E_hull struct (meV)"], d[zone]["Composite (DSI term)"], facecolors="none", edgecolors="k", s=90, lw=1.5, label="Discovery zone (%d compositions)" % d[zone]["Formula"].nunique())
    axes[0].set_xlabel("$E_\\mathrm{hull}$ of discharged phase (meV atom$^{-1}$, clipped at 200)"); axes[0].set_ylabel("Composite score (DSI term)"); axes[0].legend(fontsize=9, loc="lower right"); label(axes[0], "(a)")
    z = d[zone].drop_duplicates("Formula")
    for c in CAT: s = z[z["DSI category"] == c]; axes[1].scatter(s["Energy Density (Wh/L)"], s["DSI"], color=CATC[c], s=110, edgecolors="k", label=f"DSI {c}", zorder=5)
    for _, r_ in z.iterrows(): axes[1].annotate(mp(r_["Formula"]), (r_["Energy Density (Wh/L)"], r_["DSI"]), xytext=(5, 3), textcoords="offset points", fontsize=8.5)
    axes[1].set_xlabel("Energy density (Wh L$^{-1}$)"); axes[1].set_ylabel("DSI score"); axes[1].legend(fontsize=9); axes[1].set_title("Discovery-zone members", fontsize=11.5); label(axes[1], "(b)"); save(fig, "cathodeai_discovery_sweetspot.png")

# ---------------- Fig 21: uncertainty ----------------
if want("f21"):
    rf = st["rf_combined"]; Xt, yt = st["X3_test"], st["y3_test"]; pt = np.stack([t.predict(Xt) for t in rf.estimators_]); mpred, hw = pt.mean(0), 1.96 * pt.std(0)
    cov = np.mean((yt >= mpred - hw) & (yt <= mpred + hw)) * 100; from sklearn.model_selection import train_test_split
    idx = np.arange(len(dfm)); _, te = train_test_split(idx, test_size=0.2, random_state=42); cap = dfm["Capacity (mAh/g)"].values[te]; rr = np.corrcoef(cap, hw)[0, 1]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5)); o = np.argsort(mpred); x = np.arange(len(o))
    axes[0].errorbar(x, mpred[o], yerr=hw[o], fmt="o", ms=3, color="#2ecc71", ecolor="#bdc3c7", elinewidth=1, label="Predicted (95% interval)"); axes[0].scatter(x, yt[o], color="#e74c3c", s=10, zorder=3, label="Materials Project value")
    axes[0].set_xlabel("Test material (sorted by prediction)"); axes[0].set_ylabel("Energy density (Wh L$^{-1}$)"); axes[0].set_title(f"Empirical 95% coverage: {cov:.1f}% (n={len(yt)})", fontsize=11.5); axes[0].legend(fontsize=9.5); label(axes[0], "(a)")
    axes[1].scatter(cap, hw, s=18, color="#3498db", edgecolors="k", linewidths=0.3); axes[1].set_xlabel("Capacity (mAh g$^{-1}$)"); axes[1].set_ylabel("Interval half-width (Wh L$^{-1}$)"); axes[1].set_title(f"Pearson $r$ = {rr:.3f}; mean half-width {hw.mean():.0f} Wh L$^{{-1}}$", fontsize=11.5); label(axes[1], "(b)")
    save(fig, "cathodeai_uncertainty.png"); json.dump({"coverage": cov, "mean_hw": float(hw.mean()), "r": float(rr), "n": int(len(yt))}, open("fig21_numbers.json", "w"))
print("done")
