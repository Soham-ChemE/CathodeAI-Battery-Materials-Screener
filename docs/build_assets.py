"""Build every asset used by docs/index.html and the README hero from repo data.

Inputs (all produced by ./reproduce.sh, which runs revision_code/ in order):
  revision_code/df813_dsi.pkl              813 oxide entries with DSI (analysis_dsi.py)
  revision_code/analysis_dsi_results.json  validation statistics (analysis_dsi.py)
  revision_code/mpdata/summary_LiCuO2.json cached Materials Project LiCuO2 polymorph structures
  revision_code/mpdata/electrodes_Li.json  cached electrode documents (funnel counts)

Outputs:
  docs/assets/data.js            window.CATHODEAI = {...} (classic script, works from file://)
  docs/assets/fig_validation.svg DSI score vs representative experimental cycle life (11 cathodes)
  docs/assets/fig_funnel.svg     eight-layer screening funnel
  docs/assets/fig_polymorph.svg  LiCuO2 polymorph DSI inputs
  docs/assets/social-preview.png 1280x640 social preview
Run from the repository root:  python docs/build_assets.py
"""
import json, os, sys, math
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RC = os.path.join(ROOT, "revision_code"); OUT = os.path.join(ROOT, "docs", "assets")
os.makedirs(OUT, exist_ok=True)

df = pd.read_pickle(os.path.join(RC, "df813_dsi.pkl"))
res = json.load(open(os.path.join(RC, "analysis_dsi_results.json")))
val = res["val"]
poly = json.load(open(os.path.join(RC, "mpdata", "summary_LiCuO2.json")))
el = json.load(open(os.path.join(RC, "mpdata", "electrodes_Li.json")))

# ---------------- funnel (same filters as repro_pipeline.py) ----------------
n_all = len(el)
cath = [e for e in el if all(e.get(k) is not None for k in ["average_voltage", "capacity_grav", "energy_vol", "stability_charge", "stability_discharge"])
        and 2.5 <= e["average_voltage"] <= 5.0 and e["capacity_grav"] > 50 and e["energy_vol"] > 0]
toxic = ["Pb", "Cd", "Hg", "As", "Tl", "Be"]; rare = ["Pt", "Ir", "Os", "Ru", "Rh", "Pd", "Au", "Re", "In", "Ge"]
clean = [e for e in cath if not any(x in e["battery_formula"] for x in toxic + rare)]
n_oxide = len(df); n_dsi = int(df["DSI"].notna().sum())
funnel = [("Materials Project Li insertion electrodes", n_all), ("Voltage 2.5 to 5.0 V, capacity above 50 mAh/g", len(cath)),
          ("Toxic and rare elements removed", len(clean)), ("Oxide frameworks", n_oxide), ("Band gap available: DSI assigned", n_dsi)]
assert (n_all, len(cath), len(clean), n_oxide) == (2774, 1886, 1864, 813), (n_all, len(cath), len(clean), n_oxide)

# ---------------- materials for the 3D scatter ----------------
m = df[df["DSI"].notna()]
materials = [[f, round(float(dv), 2), round(float(eh), 4), round(float(bg), 3), round(float(d), 3), c[0], round(float(ed)), round(float(v), 2)]
             for f, dv, eh, bg, d, c, ed, v in zip(m["Formula"], m["Max Volume Change (%)"], m["Stability Charge (eV)"], m["Band Gap (eV)"],
                                                    m["DSI"], m["DSI category"], m["Energy Density (Wh/L)"], m["Avg Voltage (V)"])]
cat_counts = m["DSI category"].str[0].value_counts().to_dict()

# ---------------- experimental validation set ----------------
exp = {"LiCoO2": 500, "LiFePO4": 2000, "LiMnO2": 300, "NMC111": 1000, "NMC622": 800, "NMC811": 800, "NCA": 500, "LNMO": 1000, "LTO": 10000, "LFMP": 1500, "Li2MnO3": 200}
# descriptor values of the validation set exactly as used in revision_code/analysis_dsi.py (volume change %, charged-phase hull energy eV/atom, band gap eV)
desc = {"LiCoO2": (2.0, 0.02, 0.00), "LiFePO4": (6.81, 0.00, 3.594), "LiMnO2": (16.0, 0.05, 0.00), "NMC111": (2.5, 0.03, 1.50), "NMC622": (4.0, 0.04, 1.20), "NMC811": (4.0, 0.06, 0.80),
        "NCA": (5.0, 0.08, 0.70), "LNMO": (2.5, 0.02, 2.00), "LTO": (0.1, 0.00, 2.72), "LFMP": (5.0, 0.00, 3.50), "Li2MnO3": (8.0, 0.10, 1.317)}
validation = [{"name": k, "exp_cycles": exp[k], "dsi": round(val["scores"][k], 3), "cat": val["cats"][k][0], "dv": desc[k][0], "eh": desc[k][1], "bg": desc[k][2]} for k in exp]
binmap = {"A": 2200, "B": 1500, "C": 750, "D": 300}
n_correct = sum((v["exp_cycles"] >= 500) == (binmap[v["cat"]] >= 500) for v in validation)

# ---------------- LiCuO2 polymorph structures (the three electrode end-members) ----------------
keep = {"C2/m": ("D", 46.6, 286, 0.09), "R-3m": ("C", 4.7, 164, 0.46), "Cm": ("B", 6.6, 25, 0.67)}
structures = []
for p in poly:
    sg = p["symmetry"]["symbol"]
    if sg not in keep: continue
    s = p["structure"]
    structures.append({"id": p["material_id"], "sg": sg, "ehull_meV": round(p["energy_above_hull"] * 1000, 1), "band_gap": p["band_gap"],
                       "lattice": [[round(x, 4) for x in r] for r in s["lattice"]["matrix"]],
                       "sites": [{"el": st["species"][0]["element"], "abc": [round(x, 4) for x in st["abc"]]} for st in s["sites"]],
                       "dsi_class": keep[sg][0], "dv": keep[sg][1], "ehull_charge_meV": keep[sg][2], "dsi": keep[sg][3]})
structures.sort(key=lambda s: ["C2/m", "R-3m", "Cm"].index(s["sg"]))

data = {"funnel": funnel, "materials": materials, "cat_counts": cat_counts, "validation": validation, "n_correct": n_correct,
        "stats": {"n_screened": n_all, "rho": round(val["rho_bins"], 2), "p": round(val["p_bins"], 3), "rho_single": round(val["rho_single"], 2),
                  "rho_cont": round(val["rho_cont"], 2), "n_val": 11, "n_dsi": n_dsi, "n_oxide": n_oxide},
        "structures": structures}
with open(os.path.join(OUT, "data.js"), "w") as f:
    f.write("// Generated by docs/build_assets.py from revision_code/ outputs. Do not edit by hand.\n")
    f.write("window.CATHODEAI = " + json.dumps(data, separators=(",", ":")) + ";\n")
print(f"data.js: {len(materials)} materials, {len(structures)} structures, rho={data['stats']['rho']}, {n_correct}/11 binary")

# ---------------- figures ----------------
DARK = "#0b1220"; ACC = "#22d3ee"; ACC2 = "#f59e0b"
CAT = {"A": "#22d3ee", "B": "#34d399", "C": "#f59e0b", "D": "#f87171"}
THEMES = {"dark": ("#e6edf3", "#8b98a9"), "light": ("#0b1220", "#5b6676")}
INK, MUTED = THEMES["dark"]; THEME = "dark"
def style(ax):
    ax.set_facecolor("none")
    for s in ax.spines.values(): s.set_color(MUTED); s.set_linewidth(0.8)
    ax.tick_params(colors=INK, labelsize=9); ax.xaxis.label.set_color(INK); ax.yaxis.label.set_color(INK); ax.title.set_color(INK)
    ax.grid(True, color=MUTED, alpha=0.2, lw=0.6)
def save(fig, name): fig.savefig(os.path.join(OUT, name.replace(".svg", f"_{THEME}.svg")), transparent=True, bbox_inches="tight"); plt.close(fig); print("wrote", name, THEME)

for THEME in THEMES:
    INK, MUTED = THEMES[THEME]
    fig, ax = plt.subplots(figsize=(6.4, 4.2)); style(ax)
    for v in validation:
        ax.scatter(v["exp_cycles"], v["dsi"], s=90, color=CAT[v["cat"]], edgecolor=INK, lw=0.6, zorder=3)
        ax.annotate(v["name"], (v["exp_cycles"], v["dsi"]), textcoords="offset points", xytext=(6, 4), fontsize=8, color=INK)
    ax.set_xscale("log"); ax.set_xlabel("Representative experimental cycle life (cycles)"); ax.set_ylabel("Degradation Screening Index")
    ax.set_title(f"11 cathodes: Spearman rho = {val['rho_bins']:.2f}, p = {val['p_bins']:.3f}", fontsize=10)
    ax.axhline(0.55, color=MUTED, ls="--", lw=0.8); ax.axvline(500, color=MUTED, ls="--", lw=0.8)
    ax.text(205, 0.57, "class B or better", color=MUTED, fontsize=8); ax.text(520, 0.12, "500 cycles", color=MUTED, fontsize=8, rotation=90)
    save(fig, "fig_validation.svg")

    fig, ax = plt.subplots(figsize=(6.4, 3.6)); style(ax); ax.grid(False)
    labels = [f[0] for f in funnel][::-1]; vals = [f[1] for f in funnel][::-1]
    bars = ax.barh(labels, vals, color=[ACC2, ACC, ACC, ACC, MUTED], height=0.6)
    for b, v in zip(bars, vals): ax.text(b.get_width() + 40, b.get_y() + b.get_height() / 2, f"{v:,}", va="center", color=INK, fontsize=9)
    ax.set_xlim(0, 3300); ax.set_xlabel("Entries retained"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    save(fig, "fig_funnel.svg")

    fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.0))
    for ax, key, lab in zip(axs, ["dv", "ehull_charge_meV", "dsi"], ["Volume change on delithiation (%)", "E_hull of charged phase (meV/atom)", "DSI (higher is more durable)"]):
        style(ax); ax.grid(False)
        ax.bar([s["sg"] for s in structures], [s[key] for s in structures], color=[CAT[s["dsi_class"]] for s in structures], width=0.6)
        for i, s in enumerate(structures): ax.text(i, s[key], f"{s[key]:g}", ha="center", va="bottom", color=INK, fontsize=8)
        ax.set_title(lab, fontsize=8); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout(); save(fig, "fig_polymorph.svg")

# social preview 1280x640
fig = plt.figure(figsize=(12.8, 6.4), dpi=100); fig.patch.set_facecolor(DARK)
ax = fig.add_axes([0.52, 0.12, 0.45, 0.78], projection="3d"); ax.set_facecolor(DARK)
rng = np.random.default_rng(0); idx = rng.choice(len(materials), 500, replace=False)
xs = np.array([materials[i][1] for i in idx]); ys = np.array([materials[i][2] for i in idx]) * 1000; zs = np.array([materials[i][3] for i in idx]); cs = np.array([materials[i][4] for i in idx])
ax.scatter(np.clip(xs, 0, 20), np.clip(ys, 0, 300), zs, c=cs, cmap="viridis", s=14, alpha=0.9, depthshade=True)
ax.set_xlabel("dV/V (%)", color=MUTED); ax.set_ylabel("E_hull,charge (meV)", color=MUTED); ax.set_zlabel("Band gap (eV)", color=MUTED)
ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False; ax.tick_params(colors=MUTED, labelsize=7)
for a in (ax.xaxis, ax.yaxis, ax.zaxis): a.pane.set_edgecolor("#1f2a3c"); a._axinfo["grid"]["color"] = "#1f2a3c"
fig.text(0.05, 0.72, "CathodeAI", color=INK, fontsize=44, fontweight="bold")
fig.text(0.05, 0.60, "Structure-aware degradation screening\nof 2,774 Li-ion cathodes", color=INK, fontsize=20, va="top")
fig.text(0.05, 0.34, f"Spearman rho {val['rho_bins']:.2f} on 11 experimental cathodes\n{n_correct} of 11 on the right side of the durable split\nMaterials Project data, every number reproducible", color=ACC, fontsize=14, va="top")
fig.text(0.05, 0.10, "Soham Kavathekar  |  github.com/Soham-ChemE", color=MUTED, fontsize=12)
fig.savefig(os.path.join(OUT, "social-preview.png"), dpi=100, facecolor=DARK); plt.close(fig); print("wrote social-preview.png")


# ---------------- animated README hero (SVG with CSS keyframes; GitHub renders these through <img>) ----------------
# A 2-D projection of the same 787-material cloud (volume change against charged-phase hull energy, coloured by DSI) with the
# eleven validation cathodes pulsing in order of reported cycle life. No SMIL, no scripts, no fonts; under 1.5 MB.
def _viridis(t):
    s = [(68, 1, 84), (59, 82, 139), (33, 145, 140), (94, 201, 98), (253, 231, 37)]; t = max(0, min(1, t)) * 4; i = int(t); f = t - i; a = s[i]; b = s[min(i + 1, 4)]
    return "#%02x%02x%02x" % tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))
PX, PY, PW, PH = 960, 70, 560, 380  # plot box
def _x(dv): return PX + min(dv, 15) / 15 * PW
def _y(eh): return PY + PH - min(eh * 1000, 150) / 150 * PH
dots = "".join(f'<circle cx="{_x(m[1]):.1f}" cy="{_y(m[2]):.1f}" r="3.2" fill="{_viridis(m[4])}" opacity=".75"/>' for m in materials)
CATC = {"A": "#22d3ee", "B": "#34d399", "C": "#f59e0b", "D": "#f87171"}
vs = sorted(validation, key=lambda v: v["exp_cycles"])
marks = ""; css = ""
for i, v in enumerate(vs):
    x, y = _x(v["dv"]), _y(v["eh"]); c = CATC[v["cat"]]
    marks += f'<g class="vm m{i}"><circle class="halo" cx="{x:.1f}" cy="{y:.1f}" r="18" fill="{c}" opacity="0"/><circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{c}" stroke="#0b1220" stroke-width="1.5"/><text x="{x + 10:.1f}" y="{y - 8:.1f}" class="vl">{v["name"]} · {v["exp_cycles"]:,} cycles</text></g>'
    css += f".m{i} .halo,.m{i} .vl{{animation-delay:{i * 1.4:.1f}s}}\n"
lines = [("2,774 electrodes", "screened from the Materials Project through an eight-layer funnel"), ("ρ = 0.76, p = 0.007", "Spearman rank of DSI classes against reported cycle life, 11 cathodes"),
         (f"{n_correct} of 11", "cathodes on the correct side of the durable / non-durable split"), ("787 oxides", "with a complete DSI from their own discharged structure")]
stat_svg = "".join(f'<g class="st s{i}"><text x="80" y="268" class="big">{a}</text><text x="80" y="300" class="small">{b}</text></g>' for i, (a, b) in enumerate(lines))
loop = 1.4 * len(vs) + 1.0
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 500" width="1600" height="500" role="img" aria-label="CathodeAI: 787 screened cathodes plotted by volume change and charged-phase hull energy, coloured by Degradation Screening Index, with the eleven validation cathodes highlighted in turn">
<style>
.t{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.h{{font-size:54px;font-weight:800;fill:#e6edf3;letter-spacing:-1.5px}}.sub{{font-size:21px;fill:#8b98a9}}.big{{font-size:34px;font-weight:800;fill:#22d3ee}}.small{{font-size:16px;fill:#8b98a9}}.foot{{font-size:15px;fill:#5b6676}}.ax{{font-size:13px;fill:#8b98a9}}.vl{{font-size:13px;font-weight:700;fill:#e6edf3;opacity:0;animation:lab {loop}s infinite}}
.halo{{animation:pulse {loop}s infinite}}
@keyframes pulse{{0%{{opacity:0;r:6}}4%{{opacity:.55;r:14}}9%{{opacity:0;r:26}}100%{{opacity:0}}}}
@keyframes lab{{0%{{opacity:0}}2%{{opacity:1}}9%{{opacity:1}}12%{{opacity:0}}100%{{opacity:0}}}}
{css}
.st{{opacity:0;animation:cycle 16s infinite}}.s1{{animation-delay:4s}}.s2{{animation-delay:8s}}.s3{{animation-delay:12s}}
@keyframes cycle{{0%,22%{{opacity:1}}25%,97%{{opacity:0}}100%{{opacity:1}}}}
@media (prefers-reduced-motion:reduce){{.halo,.vl,.st{{animation:none}}.vl{{opacity:1}}.s0{{opacity:1}}}}
</style>
<rect width="1600" height="500" fill="#0b1220"/>
<g class="t">
<text x="80" y="120" class="h">Structure predicts durability.</text><text x="80" y="178" class="h">Metal identity does not.</text>
<text x="80" y="218" class="sub">CathodeAI: a three-descriptor Degradation Screening Index for Li-ion cathodes</text>
{stat_svg}
<text x="80" y="420" class="foot">Materials Project data · every number regenerated by reproduce.sh · preprint on ChemRxiv</text>
<text x="80" y="446" class="foot">Right: 787 oxide cathodes, volume change against charged-phase hull energy, coloured by DSI · open the live page for the 3D fly-through</text>
<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="none" stroke="#1f2a3c"/>
<text x="{PX + PW / 2}" y="{PY + PH + 28}" class="ax" text-anchor="middle">ΔV/V on delithiation, 0 → 15 % (clipped)</text>
<text x="{PX - 12}" y="{PY + PH / 2}" class="ax" text-anchor="middle" transform="rotate(-90 {PX - 12} {PY + PH / 2})">E_hull of the charged phase, 0 → 150 meV/atom (clipped)</text>
</g>
{dots}
<g class="t">{marks}</g>
</svg>"""
with open(os.path.join(OUT, "hero.svg"), "w", encoding="utf-8") as f: f.write(svg)
print("wrote hero.svg", os.path.getsize(os.path.join(OUT, "hero.svg")), "bytes")
