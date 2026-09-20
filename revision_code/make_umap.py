import pickle, json, numpy as np, pandas as pd, matplotlib, re
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matminer.featurizers.composition import ElementProperty
from pymatgen.core import Composition
from sklearn.preprocessing import StandardScaler
import umap
plt.rcParams.update({"font.size": 12, "axes.labelsize": 12, "legend.fontsize": 10})
st = pickle.load(open("repro_state_id.pkl", "rb")); dfm = st["df_ml3"]; nv = pd.read_csv("novel_compositions_recheck.csv")
ep = ElementProperty.from_preset("magpie"); ep.set_n_jobs(1)
Xk = pd.DataFrame(ep.featurize_many([Composition(f) for f in dfm["Formula_base"]], ignore_errors=True, pbar=False), columns=ep.feature_labels())
Xn = pd.DataFrame(ep.featurize_many([Composition(f) for f in nv["Reduced formula"]], ignore_errors=True, pbar=False), columns=ep.feature_labels())
cols = Xk.dropna(axis=1).columns; Xk, Xn = Xk[cols], Xn[cols].fillna(Xk[cols].mean())
X = StandardScaler().fit_transform(np.vstack([Xk.values, Xn.values]))
emb = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42).fit_transform(X)
k = len(Xk); ek, en = emb[:k], emb[k:]
def fam(f):
    for key, lab in [("PO", "Phosphate"), ("Co", "Cobalt oxide"), ("Ni", "Nickel oxide"), ("Mn", "Manganese oxide"), ("Fe", "Iron oxide"), ("Cu", "Copper oxide"), ("Ti", "Titanium oxide"), ("V", "Vanadium oxide")]:
        if key in f: return lab
    return "Other"
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
sc = axes[0].scatter(ek[:, 0], ek[:, 1], c=dfm["Energy Density (Wh/L)"], cmap="RdYlGn", s=12, alpha=0.6); plt.colorbar(sc, ax=axes[0], label="Energy density (Wh L$^{-1}$)")
axes[0].scatter(en[:, 0], en[:, 1], c=nv["Predicted ED 4-feature RF (Wh/L)"], cmap="RdYlGn", marker="*", s=160, edgecolors="k", label="Generated compositions (stars)")
axes[0].set_xlabel("UMAP 1"); axes[0].set_ylabel("UMAP 2"); axes[0].legend(fontsize=10); axes[0].text(-0.1, 1.05, "(a)", transform=axes[0].transAxes, fontsize=15, fontweight="bold")
cols_f = {"Phosphate": "#2ecc71", "Cobalt oxide": "#e74c3c", "Nickel oxide": "#3498db", "Manganese oxide": "#f39c12", "Iron oxide": "#27ae60", "Copper oxide": "#9b59b6", "Titanium oxide": "#1abc9c", "Vanadium oxide": "#e67e22", "Other": "#95a5a6"}
fams = np.array([fam(f) for f in dfm["Formula_base"]])
for f, c in cols_f.items():
    m = fams == f
    if m.sum(): axes[1].scatter(ek[m, 0], ek[m, 1], c=c, s=12, alpha=0.6, label=f)
axes[1].scatter(en[:, 0], en[:, 1], c="k", marker="*", s=160, edgecolors="w", label="Generated"); axes[1].set_xlabel("UMAP 1"); axes[1].set_ylabel("UMAP 2"); axes[1].legend(fontsize=9, ncol=2); axes[1].text(-0.1, 1.05, "(b)", transform=axes[1].transAxes, fontsize=15, fontweight="bold")
fig.tight_layout(); fig.savefig("/Users/thegreat/Desktop/Major revision /figures_revised/cathodeai_umap.png", dpi=300, bbox_inches="tight"); print("saved umap", Xk.shape)
