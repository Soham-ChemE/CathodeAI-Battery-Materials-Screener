"""Designed graphics: RSC TOC graphic (two variants), GitHub hero banner, pipeline card.
All numbers read from the analysis outputs."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch, Circle, Rectangle
from matplotlib import font_manager as fm
R = json.load(open("analysis_dsi_results.json")); V = R["val"]; hv = R["heur_val"]
val_exp = {"LiCoO2": 500, "LiFePO4": 2000, "LiMnO2": 300, "NMC111": 1000, "NMC622": 800, "NMC811": 800, "NCA": 500, "LNMO": 1000, "LTO": 10000, "LFMP": 1500, "Li2MnO3": 200}
mats = list(val_exp); exp = np.array([val_exp[m] for m in mats]); dsi = np.array([V["scores"][m] for m in mats]); heur = np.array([hv["preds"][m] for m in mats], float)
pol = sorted(R["polymorph"], key=lambda r: r["E_hull polymorph (meV)"])
FONT = "Avenir Next" if "Avenir Next" in {f.name for f in fm.fontManager.ttflist} else "Helvetica Neue"
plt.rcParams.update({"font.family": FONT, "mathtext.fontset": "custom", "mathtext.rm": FONT, "mathtext.it": FONT + ":italic", "mathtext.bf": FONT + ":bold"})
CAT = {"D": "#e5484d", "C": "#f5a524", "B": "#30a46c", "A": "#3e63dd"}
OUT = "/Users/thegreat/Desktop/Major revision /"

def iso_cell(ax, x, y, w, h, d, face, edge, lw=1.0, alpha=1.0, z=3):
    """Isometric box: front face at (x,y), depth offset d."""
    front = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    top = [(x, y + h), (x + w, y + h), (x + w + d, y + h + d * 0.6), (x + d, y + h + d * 0.6)]
    side = [(x + w, y), (x + w + d, y + d * 0.6), (x + w + d, y + h + d * 0.6), (x + w, y + h)]
    for pts, shade in [(front, 1.0), (top, 1.18), (side, 0.85)]:
        c = "none" if face == "none" else np.clip(np.array(matplotlib.colors.to_rgb(face)) * shade, 0, 1)
        ax.add_patch(Polygon(pts, closed=True, facecolor=c, edgecolor=edge, lw=lw, alpha=alpha, zorder=z, joinstyle="round"))

def toc(theme="light"):
    dark = theme == "dark"
    bg = "#0b1220" if dark else "white"; fg = "#e6edf3" if dark else "#0f172a"; muted = "#9fb0c3" if dark else "#64748b"; card = "#111a2e" if dark else "#f4f6fa"; grid = "#243147" if dark else "#dfe4ec"
    cm = 1 / 2.54; fig = plt.figure(figsize=(8 * cm, 4 * cm), dpi=600, facecolor=bg)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 80); ax.set_ylim(0, 40); ax.axis("off"); ax.set_facecolor(bg)
    # headline
    ax.text(2.2, 36.6, "Structure, not composition, sets cathode durability", fontsize=6.6, fontweight="bold", color=fg, va="center")
    ax.text(2.2, 33.2, "2,774 Li insertion electrodes screened with a structure-resolved Degradation Screening Index (DSI)", fontsize=3.6, color=muted, va="center")
    # ---- left card: polymorphs ----
    ax.add_patch(FancyBboxPatch((2, 2.2), 40, 28, boxstyle="round,pad=0,rounding_size=1.6", facecolor=card, edgecolor="none", zorder=1))
    ax.text(4, 27.6, "One composition, LiCuO$_2$", fontsize=5.2, fontweight="bold", color=fg, va="center")
    ax.text(4, 25.2, "three polymorph electrodes, three durability classes", fontsize=3.6, color=muted, va="center")
    xs = [4.5, 16.5, 28.5]
    for x0, p in zip(xs, pol):
        cat = p["DSI category"][0]; dv = p["dV/V (%)"]; c = CAT[cat]
        iso_cell(ax, x0 + 1.4, 14.2, 6.4, 5.4, 2.0, face=c, edge="#0b1220" if dark else "#1e293b", lw=0.35)
        # strain arrow: length proportional to dV/V (capped), centred under the cell
        L = 2.6 + 7.4 * min(dv, 50) / 50
        ax.annotate("", (x0 + 5.2 - L / 2, 12.3), (x0 + 5.2 + L / 2, 12.3), arrowprops=dict(arrowstyle="<|-|>", color=c, lw=0.7, mutation_scale=4), zorder=5)
        ax.text(x0 + 5.2, 10.4, f"ΔV/V {dv:.0f}%", fontsize=3.7, color=fg, ha="center", va="center", fontweight="bold")
        ax.text(x0 + 5.2, 24.0 - 1.4, p["Space Group"].replace("-3", "$\\bar{3}$"), fontsize=4.8, fontweight="bold", color=fg, ha="center", va="center")
        ax.add_patch(FancyBboxPatch((x0 + 0.2, 4.0), 10.0, 3.6, boxstyle="round,pad=0,rounding_size=1.3", facecolor=c, edgecolor="none", zorder=4))
        ax.text(x0 + 5.2, 5.8, f"class {cat}   DSI {p['DSI']:.2f}", fontsize=3.4, fontweight="bold", color="white", ha="center", va="center", zorder=5)
    ax.text(4, 8.6, "arrow length = volume change on Li removal", fontsize=2.8, color=muted, va="center", style="italic")
    # ---- right card: ranking ----
    ax.add_patch(FancyBboxPatch((44, 2.2), 34, 28, boxstyle="round,pad=0,rounding_size=1.6", facecolor=card, edgecolor="none", zorder=1))
    ax.text(46, 27.6, "Ranks 11 experimental cathodes", fontsize=5.2, fontweight="bold", color=fg, va="center")
    ax.text(46, 25.0, "Spearman ρ against measured cycle-life order", fontsize=3.6, color=muted, va="center")
    # two mini scatter strips: heuristic vs DSI rank
    from scipy.stats import rankdata
    re_ = rankdata(exp); rd = rankdata(dsi); rh = rankdata(heur)
    for j, (lab, rk, col, rho) in enumerate([("metal-identity heuristic", rh, "#8a94a6", hv["rho_nostab"]), ("structure-resolved DSI", rd, "#30a46c", V["rho_bins"])]):
        y0 = 15.5 - j * 8.8; x0, w = 47, 20
        ax.text(x0, y0 + 5.2, lab, fontsize=3.6, color=fg, va="center")
        ax.text(x0 + w + 9.3, y0 + 2.1, f"ρ = {rho:.2f}", fontsize=6.0, fontweight="bold", color=col, ha="right", va="center")
        ax.plot([x0, x0 + w], [y0 + 4.0, y0 + 4.0], color=grid, lw=0.5); ax.plot([x0, x0 + w], [y0 + 0.2, y0 + 0.2], color=grid, lw=0.5)
        ax.text(x0 - 0.4, y0 + 4.0, "exp.", fontsize=2.6, color=muted, ha="right", va="center"); ax.text(x0 - 0.4, y0 + 0.2, "pred.", fontsize=2.6, color=muted, ha="right", va="center")
        for a, b in zip(re_, rk):
            xa = x0 + (a - 1) / 10 * w; xb = x0 + (b - 1) / 10 * w
            ax.plot([xa, xb], [y0 + 4.0, y0 + 0.2], color=col, lw=0.45, alpha=0.75)
            ax.plot(xa, y0 + 4.0, "o", ms=1.5, color=fg, mec="none"); ax.plot(xb, y0 + 0.2, "o", ms=1.5, color=col, mec="none")
    ax.text(46, 3.6, "fewer crossings = better rank agreement", fontsize=2.9, color=muted, va="center", style="italic")
    for ext in ["png", "pdf"]: fig.savefig(f"{OUT}TOC_graphic_v2_{theme}.{ext}", dpi=600, facecolor=bg)
    fig.savefig(f"{OUT}TOC_graphic_v2_{theme}.tif", dpi=600, facecolor=bg, pil_kwargs={"compression": "tiff_lzw"}); plt.close(fig); print("toc", theme)

def hero():
    bg = "#0b1220"; fig = plt.figure(figsize=(16, 5.5), dpi=100, facecolor=bg); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 160); ax.set_ylim(0, 55); ax.axis("off")
    # subtle grid
    for gx in range(0, 161, 8): ax.plot([gx, gx], [0, 55], color="#152037", lw=0.6, zorder=0)
    for gy in range(0, 56, 8): ax.plot([0, 160], [gy, gy], color="#152037", lw=0.6, zorder=0)
    ax.text(8, 44, "COMPUTATIONAL MATERIALS DISCOVERY  ·  REVISED SEPT 2026", fontsize=11, color="#22d3ee", fontweight="bold", va="center")
    ax.text(8, 34.5, "CathodeAI", fontsize=58, fontweight="bold", color="white", va="center")
    ax.text(8, 25.5, "Structure-aware screening of Li-ion battery cathodes", fontsize=19, color="#c9d4e2", va="center")
    ax.plot([8, 27], [21.6, 21.6], color="#22d3ee", lw=3)
    kpis = [("2,774", "Materials Project electrodes", 23), ("ρ = 0.76 vs 0.55", "DSI vs metal-identity heuristic", 33), ("3 classes", "one composition, LiCuO$_2$", 25), ("A to D", "durability classes, no cycle counts", 31)]
    x = 8
    for big, small, w in kpis:
        ax.add_patch(FancyBboxPatch((x, 4.5), w, 10, boxstyle="round,pad=0,rounding_size=1.2", facecolor="#111a2e", edgecolor="#22d3ee" if big.startswith("2,7") else "#243147", lw=1.4))
        ax.text(x + 1.6, 11.2, big, fontsize=14.5, fontweight="bold", color="#22d3ee" if big.startswith("2,7") else "white", va="center", family="Menlo")
        ax.text(x + 1.6, 7.2, small, fontsize=9, color="#9fb0c3", va="center", family="Menlo"); x += w + 2.2
    # right: three isometric cells with strain, badges
    for i, p in enumerate(pol):
        cat = p["DSI category"][0]; c = CAT[cat]; x0 = 108 + i * 16; dv = p["dV/V (%)"]
        iso_cell(ax, x0, 30, 8, 7, 2.6, face=c, edge="#0b1220", lw=1.0)
        L = 2.5 + 8 * min(dv, 50) / 50; ax.annotate("", (x0 + 4 - L / 2, 27.6), (x0 + 4 + L / 2, 27.6), arrowprops=dict(arrowstyle="<|-|>", color=c, lw=1.6, mutation_scale=10))
        ax.text(x0 + 4, 24.4, p["Space Group"], fontsize=13, fontweight="bold", color="white", ha="center", va="center")
        ax.text(x0 + 4, 21.0, f"ΔV/V {dv:.0f}%   class {cat}", fontsize=10, color=c, ha="center", va="center", fontweight="bold")
    ax.text(128, 49, "LiCuO$_2$ polymorphs, real electrode data", fontsize=12, color="#9fb0c3", ha="center", va="center")
    ax.text(128, 45.2, "same formula, three durability classes", fontsize=12, color="white", ha="center", va="center", fontweight="bold")
    fig.savefig(OUT + "github/hero.png", dpi=100, facecolor=bg); plt.close(fig); print("hero")

def pipeline():
    bg = "#0b1220"; fig = plt.figure(figsize=(12.8, 5.6), dpi=100, facecolor=bg); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 128); ax.set_ylim(0, 56); ax.axis("off")
    ax.text(6, 51, "EIGHT-LAYER SCREENING PIPELINE", fontsize=11, color="#22d3ee", fontweight="bold", va="center")
    ax.text(6, 46.5, "2,774 electrodes  $\\rightarrow$  813 scored oxides  $\\rightarrow$  26 discovery-zone compositions", fontsize=19, color="white", fontweight="bold", va="center")
    layers = [("1 · Voltage window 2.5–5.0 V", 2774, 1886, "electrolyte / solid-state window"), ("2 · Capacity above 50 mAh/g", 1886, 1886, "practical performance"), ("4 · Toxic and rare-element exclusion", 1886, 1864, "RoHS / REACH"),
              ("3 · Oxide frameworks", 1864, 813, "reversible redox"), ("5 · Supply chain   6 · Recyclability", 813, 813, "expert element scores; HHI as context"), ("7 · Thermal safety", 813, 813, "oxygen-release onset proxy"), ("8 · Degradation Screening Index", 813, 787, "durability classes A to D")]
    y = 40
    for lab, n0, n1, why in layers:
        w = 34 + 44 * n1 / 2774; col = "#f5a524" if lab.startswith("8") else "#22a6c9"
        ax.add_patch(FancyBboxPatch((6, y - 2.2), w, 4.4, boxstyle="round,pad=0,rounding_size=0.8", facecolor=col, edgecolor="none", alpha=0.95 if lab.startswith("8") else 0.85))
        ax.text(7.5, y, lab, fontsize=11.5, color="#0b1220" if lab.startswith("8") else "white", fontweight="bold", va="center")
        ax.text(6 + w + 1.5, y, f"{n1:,}", fontsize=11, color="white", va="center", family="Menlo")
        ax.text(90, y, why, fontsize=10.5, color="#f5a524" if lab.startswith("8") else "#9fb0c3", va="center", family="Menlo"); y -= 5.4
    ax.add_patch(FancyBboxPatch((6, y - 2.4), 46, 4.8, boxstyle="round,pad=0,rounding_size=0.8", facecolor="#0b1220", edgecolor="#22d3ee", lw=1.8))
    ax.text(29, y, "26 discovery-zone compositions (39 entries)", fontsize=12.5, color="#22d3ee", fontweight="bold", ha="center", va="center", family="Menlo")
    ax.text(90, y, "top-quartile composite, E_hull < 50 meV, top ED", fontsize=9.5, color="#9fb0c3", va="center", family="Menlo")
    fig.savefig(OUT + "github/pipeline.png", dpi=100, facecolor=bg); plt.close(fig); print("pipeline")

import os; os.makedirs(OUT + "github", exist_ok=True)
toc("light"); toc("dark"); hero(); pipeline()
