"""Write the revised ESI from generated table bodies."""
import json, re
T = json.load(open("tables.json")); R = json.load(open("analysis_dsi_results.json"))
# main-text reference numbers from citation order in main.tex (unsorted numeric style)
src = open("/Users/thegreat/Desktop/Major revision /main.tex").read()
lines = []
for l in src.split("\n"):
    out = ""; i = 0
    while i < len(l):
        if l[i] == "%" and (i == 0 or l[i-1] != "\\"): break
        out += l[i]; i += 1
    lines.append(out)
order = []
for m in re.finditer(r"\\cite\{([^}]*)\}", "\n".join(lines)):
    for k in m.group(1).split(","):
        k = k.strip()
        if k and k not in order: order.append(k)
num = {k: i + 1 for i, k in enumerate(order)}
json.dump(num, open("main_ref_numbers.json", "w"), indent=1)
# add main-text numbers column to S1 rows: replace trailing \cite{...} with "\cite{...} (main text refs N, M)"
s1_rows = []
for row in T["esi_s1"].split("\n"):
    m = re.search(r"\\cite\{([^}]+)\}", row); keys = [k.strip() for k in m.group(1).split(",")]
    nums = ", ".join(str(num[k]) for k in keys if k in num)
    s1_rows.append(row.replace(m.group(0), f"{m.group(0)} & {nums}"))
esi = r"""\documentclass[10pt]{article}
\usepackage[a4paper,margin=2cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{longtable}
\usepackage[super,sort&compress,comma]{natbib}
\renewcommand{\thetable}{S\arabic{table}}

\title{Electronic Supplementary Information\\
\large Beyond heuristics: structure-aware screening reveals the limits of
composition-based cathode design}
\author{Soham Kavathekar}
\date{}

\begin{document}
\maketitle

\noindent This Electronic Supplementary Information (ESI) accompanies the main manuscript and provides: (S1) literature sources, descriptor values and DSI scores for the 11-material validation set; (S2) definitions of the composite scoring functions; (S3) item-by-item inputs and database status for the 42 generated compositions; (S4) the Materials Project insertion-electrode entries of the LiCuO$_2$ composition; and (S5) a comparison of the formula-level structural merge used in the original submission with the identifier-level merge used in the revised manuscript. Citation numbers in the ESI reference list are ESI-internal; the corresponding main-text reference numbers are given in Table~\ref{tab:s1_sources}.

\vspace{1em}

\begin{table}[htbp]
\centering
\caption{DSI descriptor values, DSI scores and literature sources for the 11 validation materials. $\Delta V/V$ is the volumetric change upon delithiation; $E_\mathrm{hull}$ is the energy above hull of the charged (delithiated) phase from Materials Project GGA+U calculations; $E_g$ is the electronic band gap. Representative cycle-life figures are order-of-magnitude values for each chemistry under typical cycling conditions that vary with electrode loading, voltage window, depth of discharge and temperature; the DSI is validated against the \emph{rank ordering} of these values (Spearman $\rho$), never their magnitudes. DSI categories: A ($\geq 0.75$), B ($0.55$--$0.75$), C ($0.35$--$0.55$), D ($<0.35$). Band-gap and hull-energy values for the NMC compositions reflect Materials Project GGA+U trends for representative ordered structures rather than specific experimental measurements.}
\label{tab:s1_sources}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.25}
\footnotesize
\begin{tabular}{l c c c c c c c l c c}
\hline
\textbf{Material} & \textbf{Rep.\ cycles} & \textbf{$\Delta V/V$ (\%%)} & \textbf{$E_\mathrm{hull}$ (eV~atom$^{-1}$)} & \textbf{$E_g$ (eV)} & \textbf{PO\textsubscript{4}} & \textbf{DSI} & \textbf{Cat.} & \textbf{Source} & \textbf{ESI ref.} & \textbf{Main-text ref.} \\
\hline
%s
\hline
\end{tabular}

\vspace{0.5em}
\noindent\footnotesize
Cited sources are the canonical primary or characterization references for each chemistry. For NCA, Watanabe \textit{et al.} report capacity retention under calendar and cycling storage tests rather than a single cycles-to-failure figure; for Li$_2$MnO$_3$, Kalyani \textit{et al.} report stable cycling for approximately 15 cycles, well below the tabulated 200. Both entries are retained as the closest identified primary characterization sources; replacing 200 by 15 for Li$_2$MnO$_3$ changes no rank and therefore no reported correlation (main text, Section~2.5). The experimental figures serve only to fix a rank order, and the manuscript makes no claim of absolute cycle-count prediction.
\normalsize
\end{table}

\begin{table}[htbp]
\centering
\caption{Composite scoring functions used in the screening pipeline, in addition to the Degradation Screening Index (DSI) defined in the main text (eqn~(1)). Within each composite score the component weights sum to unity. The Complete Score is the ranking used for Table~10 and the Pareto analysis of the main text; the Economic Score and the CathodeAI Score are intermediate rankings retained in the released code.}
\label{tab:s2_scores}
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.3}
\begin{tabular}{p{3.0cm} p{5.0cm} p{6.6cm}}
\hline
\textbf{Composite Score} & \textbf{Components (Weights)} & \textbf{Definition} \\
\hline
Performance Score &
Voltage (0.30), Energy density (0.30), Capacity (0.25), Stability (0.15) &
Initial electrochemical ranking; voltage scored 1.0 in 3.5--4.5~V, 0.7 in 3.0--3.5 and 4.5--5.0~V, 0.4 otherwise; capacity and energy density normalized to their maxima; stability $= 1 - (E_\mathrm{hull,charge}+E_\mathrm{hull,discharge})/\max$ \\[4pt]
CathodeAI Score &
Performance (0.50), Supply chain (0.25), Recyclability (0.25) &
Performance normalized to its maximum; supply chain and recyclability scored on $[0,1]$ (main text, Section~4.2) \\[4pt]
CathodeAI Economic Score &
Performance (0.35), Supply chain (0.20), Recyclability (0.20), Solid state (0.15), Cost (0.10) &
Intermediate ranking including raw-material cost; cost score $= 1 - \mathrm{cost}/\max(\mathrm{cost})$ with cost by dominant metal (Co 45, Ni 18, Mn 8, Fe 5, Cu 12, V 35, Ti 15, Cr 12, default 20~US\$~kWh$^{-1}$) \\[4pt]
Complete Score (Table~10) &
Performance (0.25), Supply chain (0.20), Recyclability (0.15), Solid state (0.15), Cost (0.10), Thermal safety (0.10), DSI (0.05) &
Full eight-layer ranking used for Table~10 and the Pareto analysis; the DSI term replaces the metal-identity cycle-life estimate used in the original submission; entries without a computable DSI receive the median DSI \\[4pt]
Price-scenario Score &
Performance (0.25), Supply chain (0.20), Recyclability (0.15), Solid state (0.15), Scenario cost (0.15), Thermal safety (0.10) &
Re-scored under five commodity-price scenarios (main text, Section~4.5) \\[4pt]
Novel Score &
Predicted energy density (0.40), Supply chain (0.20), Recyclability (0.20), Solid state (0.20) &
Applied to the 42 generated compositions; predicted energy density from the 4-feature electrochemical Random Forest (voltage, capacity, charged- and discharged-phase hull energy), not the 8-feature model, because structural descriptors of hypothetical compositions are unavailable; normalized to its maximum \\
\hline
\end{tabular}
\end{table}

\clearpage
\begin{center}
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\renewcommand{\arraystretch}{1.15}
\begin{longtable}{l l l c c c c c l c}
\caption{Item-by-item inputs and Materials Project status for the 42 generated compositions. Generated formula and structure-family template as enumerated; ``reduced'' is the smallest-integer formula used for the corrected database query; formal M state is the metal oxidation state implied by charge balance; assigned voltage (lookup by metal and oxidation state, clipped to the template range) and capacity (Faraday's law for the lithium content, clipped to the template range) are the model inputs, together with assumed hull energies of 0.02~eV~atom$^{-1}$; predicted energy density from the 4-feature Random Forest; $E_\mathrm{hull}$ is the minimum energy above hull (meV~atom$^{-1}$) among Materials Project entries of the reduced formula, or ``absent''. The last two columns show the lithium-index-stripped formula used in the original submission's query and its outcome, which differed from the correct one for many compositions.}\label{tab:s3_novel}\\
\hline
Generated & Reduced & Template & M state & $V$ (V) & $C$ (mAh~g$^{-1}$) & Pred.\ ED & $E_\mathrm{hull}$ (correct) & Original query & $E_\mathrm{hull}$ (original) \\
\hline
\endfirsthead
\hline
Generated & Reduced & Template & M state & $V$ (V) & $C$ (mAh~g$^{-1}$) & Pred.\ ED & $E_\mathrm{hull}$ (correct) & Original query & $E_\mathrm{hull}$ (original) \\
\hline
\endhead
%s
\hline
\end{longtable}
\end{center}

\begin{table}[htbp]
\centering
\caption{Materials Project insertion-electrode entries whose base formula is LiCuO$_2$. Li$_{a\text{--}b}$ denotes the lithium range spanned by the entry; $E_\mathrm{hull}$ in meV~atom$^{-1}$. The discharge and charge identifiers are the Materials Project material identifiers of the end-members; three of the discharge or charge end-members coincide with the eight LiCuO$_2$ polymorph entries and provide the polymorph-resolved DSI values of Table~5 in the main text.}
\label{tab:s4_licuo2}
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.25}
\footnotesize
\begin{tabular}{l c c c c l l}
\hline
Entry & $V$ (V) & $\Delta V/V$ (\%%) & $E_\mathrm{hull,charge}$ & $E_\mathrm{hull,discharge}$ & Discharge end-member & Charge end-member \\
\hline
%s
\hline
\end{tabular}
\end{table}

\begin{table}[htbp]
\centering
\caption{Five-fold cross-validated $R^2$ (Random Forest, mean $\pm$ standard deviation across folds) for the formula-level structural merge of the original submission (1,702 entries, descriptors averaged over all structural entries sharing a base formula) and the identifier-level merge of the revised manuscript (1,724 entries, descriptors of each electrode's own discharged structure), under random and grouped (by base formula) fold assignment. The last row is the unfitted arithmetic relation $V\times C\times\rho$.}
\label{tab:s5_merge}
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.25}
\small
\begin{tabular}{l c c c c}
\hline
 & \multicolumn{2}{c}{Formula-level merge (original)} & \multicolumn{2}{c}{Identifier-level merge (revised)} \\
Feature set & Random CV & Grouped CV & Random CV & Grouped CV \\
\hline
%s
\hline
\end{tabular}
\end{table}

\bibliographystyle{rsc}
\bibliography{rsc}
\end{document}
""" % ("\n".join(s1_rows), T["esi_s3"], T["esi_s4"], T["esi_s5"])
open("/Users/thegreat/Desktop/Major revision /esi main.tex", "w").write(esi)
print("ESI written; main-text ref numbers used:", {k: num.get(k) for k in ["Mizushima1980", "Reimers1992", "Padhi1997", "Armstrong1996", "Jung2017", "Liu2015", "Watanabe2014", "Zhong1997", "Ohzuku1995", "Bramnik2007", "Kalyani1999"]})
