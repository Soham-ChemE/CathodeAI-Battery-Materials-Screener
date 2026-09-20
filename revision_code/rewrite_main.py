"""Rewrite main.tex body: abstract, intro framing paragraph, Results, Conclusions, Experimental.
Table bodies come from tables.json (generated from data). Placeholders %%TABLE2%% %%TABLE3%% %%TABLE4%% %%MM_R2%% are
filled by fill_pending.py once the MatMiner/SHAP pass completes."""
import json, re
T = json.load(open("tables.json")); R = json.load(open("analysis_dsi_results.json"))
p = "/Users/thegreat/Desktop/Major revision /main.tex"; s = open(p).read()
NS = T["novel_stats"]; r216 = T["r216"]; U = T["uncert"]; r221 = T["r221"]; r215 = T["r215"]; r13 = T["r13"]; r213 = T["r213"]
def f3(x): return f"{x:.3f}"
zone_n, zone_rows = R["zone_... & top-25% ED"][1], R["zone_... & top-25% ED"][0]
hv = R["heur_val"]; hd = R["heur_vs_dsi"]; V = R["val"]; nest = V["nested"]; sw = V["sweep"]
po_n, non_n = T["po4_n"]; rw = R["r220"]["rows"]
def pf(p): return f"$p={p:.3f}$" if p >= 1e-3 else f"$p<10^{{{int(np.floor(np.log10(p)))+1}}}$"
import numpy as np
pol = {r["Space Group"]: r for r in R["polymorph"]}; RD = R["r221"]
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f"expected {count}, found {c}: {old[:80]}"
    s = s.replace(old, new)

# ---------------- ABSTRACT ----------------
a0 = s.index("\\noindent\\normalsize{Composition-level heuristics"); a1 = s.index("} \\\\", a0)
abstract = ("\\noindent\\normalsize{Composition-level heuristics based on transition-metal identity are widely used to anticipate lithium-ion cathode durability, but their physical basis is rarely tested against structure-resolved data. "
            "Screening 2,774 Li insertion electrodes from the Materials Project, we compare a metal-identity heuristic with a transparent Degradation Screening Index (DSI) built from three structure-resolved descriptors: delithiation volume strain, charged-phase energy above hull and band gap. "
            f"Against 11 experimentally characterised cathodes the DSI ranks durability better (Spearman $\\rho = {V['rho_bins']:.2f}$, $p = {V['p_bins']:.3f}$) than the metal-identity heuristic ($\\rho = {hv['rho_nostab']:.2f}$, $p = {hv['p_nostab']:.2f}$) or a single volume-strain descriptor ($\\rho = {V['rho_single']:.2f}$, $p = {V['p_single']:.2f}$), and at database scale the heuristic correlates only weakly with the DSI ($\\rho = {hd[1]:.2f}$, $n = {hd[2]}$). "
            f"Resolving LiCuO$_2$ into its polymorph-specific electrode entries shows delithiation strain from {pol['R-3m']['dV/V (%)']:.1f} to {pol['C2/m']['dV/V (%)']:.0f}\\% and DSI values spanning three of four durability categories at fixed composition. "
            f"For energy-density prediction, neither compositional descriptors ($R^2 = $%%MM_R2%%, 132 Magpie features) nor structural descriptors alone ($R^2 = {r13['Structural only (6)']['random'][0]:.2f}$; {r13['Structural only (6)']['grouped'][0]:.2f} under grouped cross-validation) are predictive, and the accuracy of an 8-feature model ($R^2 = {r13['Combined (8)']['random'][0]:.2f}$) is fully accounted for by voltage, capacity and density, the arithmetic constituents of the target; its role is therefore confined to coverage and uncertainty estimation. "
            "Multi-objective Pareto analysis over energy density, DSI and supply-chain criticality shows that no single material is universally optimal. All durability estimates are reported as relative DSI categories rather than cycle counts, and structure-resolved descriptors, not composition alone, should anchor durability screening.")
s = s[:a0] + abstract + s[a1:]

# ---------------- INTRO framing paragraph ----------------
i0 = s.index("Here we present a screening framework organized around a single thesis"); i1 = s.index("\\section{Results and discussion}")
intro = ("Here we present a screening framework organized around a single thesis: composition-only heuristics become insufficient once structural polymorphism and multiple competing objectives are considered, and structure-resolved descriptors provide a more informative basis for durability screening. "
         "We support this with three lines of evidence and report one negative result. First, a transparent Degradation Screening Index built from structure-resolved descriptors ranks experimental durability better than a metal-identity heuristic or a single descriptor. "
         "Second, polymorph-resolved electrode data for LiCuO$_2$ show that the same composition spans three of four durability categories. Third, multi-objective Pareto analysis shows that no single material is universally optimal once durability and supply-chain criticality are considered alongside performance. "
         "The negative result concerns energy-density prediction: neither compositional nor structural descriptor sets alone are predictive, and a machine-learning model adds no accuracy beyond the arithmetic identity $E = V \\times C \\times \\rho$ once density is known, so we use it only for coverage and uncertainty estimation and say so explicitly. "
         "Every cycle-life estimate in this work derives from one method, the DSI, and is reported as a relative durability category. All scoring equations, weights and hyperparameters are given in the Experimental section; the complete codebase is publicly available.\\cite{CathodeAI_GitHub}\n\n")
s = s[:i0] + intro + s[i1:]

# ---------------- RESULTS ... EXPERIMENTAL (full replacement) ----------------
r0 = s.index("\\section{Results and discussion}"); r1 = s.index("\\section*{Author contributions}")
body = r"""\section{Results and discussion}\label{sec:results}

\subsection{Multi-layer screening funnel}\label{sec:funnel}

Starting from 2,774 Li insertion-electrode entries queried from the Materials Project database,\cite{Jain2013} an eight-layer sequential pipeline is applied to identify viable cathode candidates (Fig.~\ref{fig:funnel}). Layers 1 and 2 enforce electrochemical viability (voltage window 2.5--5.0~V, gravimetric capacity above 50~mAh~g$^{-1}$), reducing the dataset to 1,886 entries; Layer 4 removes toxic and rare elements (1,864 entries) and Layer 3 retains oxide frameworks (813 entries). Layers 5 to 8 score, rather than filter, these 813 entries for supply-chain criticality and recyclability (Section~\ref{sec:pipeline}), thermal safety and the DSI described in Section~\ref{sec:dsi}; the DSI is computable for 787 of the 813 entries (the remainder are hydrogen-containing compositions absent from the structural query). For machine learning, the 1,886 electrode entries are matched to the structural descriptors of their own discharged structure through the Materials Project identifier of the discharge end-member, giving 1,724 entries (91.4\%) with complete features (Section~\ref{sec:data}). A discovery zone defined explicitly as top-quartile composite score, energy above hull of the discharged phase below 50~meV~atom$^{-1}$ and top-quartile energy density contains %d entries corresponding to %d unique compositions (Fig.~\ref{fig:discovery}).

\begin{figure}[h]
\centering
\includegraphics[width=0.48\textwidth]{cathodeai_complete_analysis.png}
\caption{Eight-layer screening funnel. Bar widths are proportional to the number of Materials Project insertion-electrode entries retained after each filtering layer; Layers 5 to 8 score rather than filter. The final bar is the discovery zone defined in Section~\ref{sec:funnel}.}
\label{fig:funnel}
\end{figure}

\subsection{Machine learning feature comparison and model selection}\label{sec:ml}

We evaluated six feature sets and four model architectures for volumetric energy-density (Wh~L$^{-1}$) prediction using 5-fold cross-validation (Fig.~\ref{fig:features}, Tables~\ref{tbl:features} and \ref{tbl:models}). Because several electrode entries share a base formula (232 base formulas account for 1,004 of the 1,724 entries), random fold assignment can place near-duplicate compounds in both training and test folds.\cite{Kapoor2023,Meredig2018} We therefore report, alongside random 5-fold cross-validation, a grouped 5-fold cross-validation in which all entries sharing a base formula are assigned to the same fold.

\begin{table}[h]
\small
\caption{\ Five-fold cross-validated $R^2$ (mean $\pm$ standard deviation across folds) for six feature sets with a Random Forest, under random and grouped (by base formula) fold assignment, followed by equivalent-information baselines built only from the arithmetic constituents of the target}
\label{tbl:features}
\begin{tabular*}{0.48\textwidth}{@{\extracolsep{\fill}}llll}
\hline
Feature set & Random CV & Grouped CV & $N$ features \\
\hline
%%TABLE2%%
\hline
\end{tabular*}
\end{table}

The combined 8-feature model (voltage, capacity, formation energy, band gap, energy above hull, volume per atom, density, number of elements) achieves $R^2 = %s$ under random and $%s$ under grouped cross-validation, against $%s$ and $%s$ for the electrochemical-only set. Grouping affects the structural-only set most strongly ($%s$ random against $%s$ grouped), showing that part of its apparent accuracy came from same-formula leakage. High-dimensional compositional descriptors (MatMiner Magpie,\cite{Ward2018} with or without Lasso selection) perform no better than the structural-only set and adding them to the combined set does not improve it.

The equivalent-information baselines in Table~\ref{tbl:features} settle how this result should be read. Volumetric energy density is defined as $E = V \times C \times \rho$, and a Random Forest given only voltage, capacity and density reaches $R^2 = %s$, indistinguishable from the 8-feature model, while a linear fit in the logarithms of the same three quantities and the unfitted product itself both reach $R^2 = %s$. The gain from the electrochemical-only to the combined set is therefore attributable to a single structural quantity, density, which completes the arithmetic identity; the remaining five DFT descriptors contribute nothing measurable. Consequently, this comparison does not show that structural descriptors are more predictive than compositional ones for energy density. Both families alone are poor predictors ($R^2 \le %s$), and the combined model succeeds because it contains the constituents of the target. We retain the model for the coverage and uncertainty roles described in Section~\ref{sec:arith}, and the structure-over-composition claims of this work rest on the durability analyses of Sections~\ref{sec:dsi} and \ref{sec:po4}, not on energy-density prediction.

\begin{table}[h]
\small
\caption{\ Five-fold cross-validated performance of four architectures on the combined 8-feature set (1,724 entries). Random and grouped fold assignment as in Table~\ref{tbl:features}; MAE in Wh~L$^{-1}$}
\label{tbl:models}
\begin{tabular*}{0.48\textwidth}{@{\extracolsep{\fill}}llllll}
\hline
Model & $R^2$ & std & MAE & $R^2$ (grouped) & MAE (grouped) \\
\hline
%%TABLE3%%
\hline
\end{tabular*}
\end{table}

Across the four architectures the differences are small relative to the fold-to-fold standard deviation (Table~\ref{tbl:models}). Random Forest was retained as the production model because its impurity-based feature importances and compatibility with exact TreeSHAP attribution\cite{Lundberg2020} support the interpretability analysis of Section~\ref{sec:shap}. Hyperparameter tuning via grid search did not improve cross-validated performance over default parameters; default parameters were retained, consistent with known risks of over-fitting a hyperparameter search to a finite cross-validation sample.\cite{Cawley2010} On a single held-out 20\% split the final model gives MAE $= 89$~Wh~L$^{-1}$ with $R^2 = 0.865$; the lower $R^2$ of this particular split relative to cross-validation reflects a small number of high-energy-density entries with large residuals, and we regard the cross-validated values as the representative estimate.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_feature_engineering.png}
\caption{Machine learning feature-set comparison. (a) Cross-validated $R^2$ for the six feature sets of Table~\ref{tbl:features} under random (blue) and grouped (orange) fold assignment; the dashed line is the Random Forest trained on voltage, capacity and density only. (b) Random Forest feature importances for the combined model. (c) Predicted against Materials Project energy density on the held-out test split.}
\label{fig:features}
\end{figure*}

\subsection{Machine learning versus the arithmetic relation}\label{sec:arith}

Since volumetric energy density is defined as $E = V \times C \times \rho$, we tested explicitly when a learned model adds anything beyond direct evaluation of this relation (Fig.~\ref{fig:mlvsarith}). With every electrode matched to the density of its own discharged structure, the unfitted product reproduces the Materials Project energy density with $R^2 = %s$ and a best-fit proportionality constant of %s (median ratio %s). In the original submission this relation gave $R^2 = 0.985$; the deviation arose because densities were then averaged over all structural entries sharing a base formula (Section~\ref{sec:data}). Restricting that earlier dataset to entries whose base formula has a single structural entry recovers $R^2 = %s$, while entries with polymorph-averaged density give $R^2 = %s$, which identifies the averaging as the sole source of the discrepancy. Machine learning is therefore not needed, and adds nothing, when voltage, capacity and density are all known.

\textbf{Missing-data behaviour.} We removed 30\% of the capacity values at random and mean-imputed them at prediction time, evaluating the 8-feature model only on held-out test entries, separately for entries with observed and with imputed capacity (Table~\ref{tbl:missing}). On entries with observed capacity the model retains $R^2 = %s$; on entries with imputed capacity it falls to $R^2 = %s$. Imputing capacity from the seven remaining features with a second Random Forest and then evaluating the arithmetic relation gives $R^2 = %s$ on the same entries, and feeding that imputed capacity to the 8-feature model gives $R^2 = %s$. The model thus retains coverage when an input is missing, but no approach recovers useful accuracy without the capacity value, because the remaining descriptors carry little information about it (imputation $R^2 = %s$). The original submission reported $R^2 = 0.986$ at 100\% coverage for this experiment; that figure was produced by a coding error in which the capacity mask was created but never applied, so no values were actually removed. We withdraw it.

\begin{table}[h]
\small
\caption{\ Held-out performance ($R^2$) when 30\% of capacity values are removed, split by whether the test entry's capacity was observed or imputed}
\label{tbl:missing}
\begin{tabular*}{0.48\textwidth}{@{\extracolsep{\fill}}lll}
\hline
Method & Observed capacity & Imputed capacity \\
\hline
%s
\hline
\end{tabular*}
\end{table}

\textbf{Novel-composition prediction.} For the generated compositions of Section~\ref{sec:novel} the inputs are not measured but assigned (voltage from a lookup by metal and oxidation state, capacity from Faraday's law, hull energies assumed), and the model used is the 4-feature electrochemical Random Forest rather than the 8-feature model, because the structural descriptors of a hypothetical composition are unknown. The resulting values are screening-level priors, not predictions.

\textbf{Uncertainty quantification.} The arithmetic relation produces a single deterministic value. The Random Forest ensemble provides prediction intervals whose empirical coverage and width are reported in Section~\ref{sec:uq}; this, together with coverage of incomplete records, is the role we assign to the learned model.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_ml_vs_arithmetic.png}
\caption{Machine learning against the arithmetic relation. (a) Complete inputs: the unfitted product $V \times C \times \rho$ (blue) and the 8-feature Random Forest (green) against the Materials Project energy density for all 1,724 entries. (b) Held-out $R^2$ of the Random Forest on test entries whose capacity was observed and on entries whose capacity was removed and mean-imputed. (c) Held-out $R^2$ on the imputed entries for four strategies: Random Forest with mean-imputed capacity, arithmetic relation with mean-imputed capacity, arithmetic relation with capacity imputed from the other seven features by a second Random Forest and the 8-feature model fed with that imputed capacity.}
\label{fig:mlvsarith}
\end{figure*}

\subsection{SHAP analysis and physical interpretation}\label{sec:shap}

SHapley Additive exPlanations (SHAP) analysis\cite{Lundberg2017} was applied to the final Random Forest model to quantify per-feature contributions (Table~\ref{tbl:shap}, Fig.~\ref{fig:shap}).

\begin{table}[h]
\small
\caption{\ Mean absolute SHAP values and Random Forest feature importances for the combined model (1,724 entries)}
\label{tbl:shap}
\begin{tabular*}{0.48\textwidth}{@{\extracolsep{\fill}}lll}
\hline
Feature & Mean $|$SHAP$|$ (Wh~L$^{-1}$) & RF importance (\%) \\
\hline
%%TABLE4%%
\hline
\end{tabular*}
\end{table}

Capacity, voltage and density account for essentially the whole attribution, in that order, which is the expected signature of a model that has learned the product $V \times C \times \rho$ and is a useful sanity check rather than a discovery. Formation energy, band gap, energy above hull and the number of elements make small contributions; the mild dependence of the formation-energy SHAP value on formation energy (Fig.~\ref{fig:shap}c) is consistent with more negative formation energies co-occurring with denser, higher-capacity oxides in this dataset and should not be read as a causal stability threshold.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_shap_analysis.png}
\caption{SHAP interpretability analysis. (a) Mean $|$SHAP$|$ for the 8 features. (b) SHAP value of capacity against capacity. (c) SHAP value of formation energy against formation energy, coloured by energy density.}
\label{fig:shap}
\end{figure*}

\subsection{Metal-identity heuristics and the Degradation Screening Index}\label{sec:dsi}

We developed a transparent, structure-grounded Degradation Screening Index (DSI) combining three descriptors, each tied to a distinct degradation pathway:
\begin{equation}
\text{DSI} = 0.50\,S_\text{vol} + 0.35\,S_\text{stab} + 0.15\,S_\text{bg} + 0.10\,\mathbb{1}_\text{PO$_4$}
\label{eq:dsi}
\end{equation}
capped at unity (the phosphate bonus therefore has full effect only when the base score is below 0.90), where
\begin{align}
S_\text{vol} &= \max(0,\, 1 - (\Delta V/V)/14.6\%) \\
S_\text{stab} &= \max(0,\, 1 - E_\text{hull,charge}/0.190~\text{eV~atom}^{-1}) \\
S_\text{bg} &= \max(0,\, 1 - |E_g - 2.0~\text{eV}|/4.0~\text{eV})
\end{align}
with normalization bounds fixed at the 95th percentile of the 2,774-entry training distribution (volumetric strain and charged-phase hull energy from the Materials Project \texttt{InsertionElectrode} documents, accessed via \texttt{pymatgen}\cite{Jain2013,Ong2013}), independent of the 11-material validation set. Descriptor weights are expert-assigned rather than learned, for reasons quantified below; band gap was included not as an optimal mechanistic descriptor of interfacial degradation, but because it is available at database scale, contributes information statistically independent of the other two descriptors (Table~\ref{tbl:dsicorr}, Fig.~\ref{fig:dsi}a; full-dataset $\Delta V/V$ against $E_\text{hull,charge}$: $r=-0.005$, $n=2{,}035$, Fig.~\ref{fig:fulldataset}) and empirically improves rank-order agreement with experiment. The DSI is a ranking heuristic: rather than mapping scores to cycle numbers, we report four relative durability categories, D (DSI $<0.35$), C ($0.35$--$0.55$), B ($0.55$--$0.75$) and A ($\geq 0.75$), which are used for every durability statement in this paper (Section~\ref{sec:dsimethod}).

\begin{table}[h]
\small
\caption{\ Pearson correlation matrix for the three normalized DSI descriptor scores ($S_\text{vol}$, $S_\text{stab}$, $S_\text{bg}$) across the 11-material validation set}
\label{tbl:dsicorr}
\begin{tabular*}{0.48\textwidth}{@{\extracolsep{\fill}}llll}
\hline
Score & $S_\text{vol}$ & $S_\text{stab}$ & $S_\text{bg}$ \\
\hline
$S_\text{vol}$ & 1.000 & 0.392 & 0.480 \\
$S_\text{stab}$ & 0.392 & 1.000 & $-0.074$ \\
$S_\text{bg}$ & 0.480 & $-0.074$ & 1.000 \\
\hline
\end{tabular*}
\end{table}

\textbf{Validation against experiment.} Against 11 experimentally characterized electrodes spanning layered oxides, olivines, spinels and a Li-rich compound (Table~\ref{tbl:validation}; literature sources per material in ESI, Table~S1$^\dag$), the DSI categories achieve Spearman $\rho = %s$ ($p=%s$) with the representative experimental cycle-life ranking and the continuous DSI score $\rho = %s$ ($p=%s$), compared with $\rho = %s$ ($p=%s$, not significant) for the single volume-strain descriptor with the same four-level binning (Fig.~\ref{fig:dsi}c). The metal-identity heuristic used in Layer 8 of the original pipeline (base cycle count by dominant transition metal with voltage and phosphate factors; Section~\ref{sec:dsimethod}) gives $\rho = %s$ ($p=%s$) on the same 11 materials, statistically indistinguishable from the single descriptor; adding a charged-phase stability factor to it raises this to $\rho = %s$ ($p=%s$). The heuristic is therefore not invalidated by these data, it is outperformed, and the improvement comes from structure-resolved information. Ten of eleven materials fall on the correct side of a binary durable/non-durable split (category B or better against a representative cycle life of at least 500). Bootstrap 95\% CIs (10,000 resamples) are [0.509, 0.934] for the DSI and [0.018, 0.923] for the single descriptor (Fig.~\ref{fig:bootstrap}); given $n=11$, wide CIs are expected. Leave-one-out analysis shows the DSI ahead of the single descriptor in all 11 iterations ($\rho \in [0.680, 0.848]$ against $[0.396, 0.706]$).

\begin{table*}[t]
\small
\caption{\ Validation of the DSI across 11 cathode materials. Representative experimental cycle life is used only to establish a rank order (Section~\ref{sec:dsimethod}). The metal-identity heuristic column is the original Layer 8 estimate. Categories: A (very high, DSI $\geq 0.75$), B (high), C (moderate), D (low, DSI $< 0.35$); the single-descriptor category uses the same four-level binning of $\Delta V/V$ alone}
\label{tbl:validation}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lllllll}
\hline
Material & Structure & Representative exp.\ cycles & Metal-identity heuristic (cycles) & Single-descriptor category & DSI score & DSI category \\
\hline
%s
\hline
\multicolumn{7}{l}{\footnotesize $^\ast$LTO (Li$_4$Ti$_5$O$_{12}$) is an anode and lies outside the cathode applicability domain; it is retained as a zero-strain reference. Excluding it leaves the conclusion unchanged (DSI $\rho=%s$, $p=%s$; single descriptor $\rho=%s$, $p=%s$).}
\end{tabular*}
\end{table*}

\textbf{Weights, sample size and stratification.} With only 11 materials, weights cannot be learned reliably: a nested leave-one-out procedure that optimizes the three weights and the phosphate bonus on 10 materials (grid step 0.05) and predicts the eleventh yields $\rho = %s$ ($p=%s$), whereas the in-sample optimum over all 11 reaches $\rho = %s$, an optimistic value that would not generalize. Fixed expert weights are therefore the defensible choice, and their adequacy is assessed by robustness rather than optimization: across six alternative schemes $\rho \in [0.529, 0.768]$ with five of six exceeding the single-descriptor baseline (Fig.~\ref{fig:robustness}), and across all %d weight triplets on a 0.05 grid the median is $\rho = %s$ (range $[%s, %s]$), with %d\%% exceeding the baseline. Stratifying by chemistry, the seven layered oxides alone give $\rho = %s$ (categories, $p=%s$) or $\rho = %s$ (continuous score, $p=%s$) against $\rho = %s$ for the single descriptor; the four non-layered materials all fall in category A, so no rank correlation is defined within that stratum. Replacing the tabulated 200 cycles for Li$_2$MnO$_3$ with the approximately 15 cycles reported by Kalyani \textit{et al.}\cite{Kalyani1999} leaves every rank, and therefore $\rho$, unchanged. We stress that this validation supports the DSI as a ranking tool within the chemistries represented; it does not establish generalization to unrepresented families, which requires a larger validation set.

\textbf{Sensitivity to DFT error.} Materials Project hull energies carry a mean absolute error of approximately 24~meV~atom$^{-1}$ against experiment.\cite{Hautier2012} Adding independent $N(0,\,24~\text{meV~atom}^{-1})$ noise to $E_\text{hull,charge}$ of the 11 validation materials (2,000 draws) gives a median $\rho = %s$ with a 5--95\% range of $[%s, %s]$, so the validation conclusion is robust; across the 787 scored candidates, however, %s\%% of DSI categories change per draw, and the same perturbation changes the Pareto fronts of Section~\ref{sec:po4} (mean Jaccard overlap %s for the EV front and %s for the grid front). Individual category assignments near a boundary should therefore be read with this uncertainty in mind, and we do not claim that DFT error leaves relative rankings unaffected.

\textbf{Heuristic against DSI at database scale.} Across the 787 oxide candidates for which the DSI is computable, the metal-identity heuristic correlates only weakly with it (Spearman $\rho = %s$, Pearson $r = %s$; Fig.~\ref{fig:volume}a). This is not by itself evidence against the heuristic, since both are unvalidated at this scale; the evidence is the direct comparison against experiment above, in which the structure-resolved index ranks better.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_volume_change.png}
\caption{Metal-identity heuristic against the DSI. (a) Heuristic cycle-life estimate against DSI score for the 787 oxide candidates with computable DSI; dotted lines mark the category boundaries. (b) Distribution of maximum delithiation volume change across the 813 oxide candidates (clipped at 50\%), with the $S_\text{vol}$ normalization bound. (c) Volume change against energy density, coloured by DSI category.}
\label{fig:volume}
\end{figure*}

\textbf{Polymorph-resolved durability at fixed composition.} Table~\ref{tbl:polymorph} lists the eight LiCuO$_2$ polymorphs in the Materials Project. Three of them are the end-member of an insertion-electrode entry, which supplies the delithiation strain, charged-phase hull energy and, through the polymorph's own band gap, a complete DSI (Fig.~\ref{fig:polymorph}). The ground-state C2/m polymorph delithiates with a volume change of %s\%% and a charged-phase hull energy of %s~meV~atom$^{-1}$, giving DSI $= %s$ (category D); the R$\bar{3}$m polymorph changes volume by %s\%% with $E_\text{hull,charge} = %s$~meV~atom$^{-1}$, giving DSI $= %s$ (category C); and the Cm polymorph, whose electrode entry covers lithiation from Li$_1$ to Li$_{1.5}$ at 2.9~V, gives DSI $= %s$ (category B). A single composition therefore spans three of the four durability categories, driven by delithiation strain and charged-phase stability rather than by composition. The original submission reported a seven-fold cycle-life variation across all eight polymorphs; that figure was obtained by mapping the static volume per atom linearly onto a 0--15\% strain proxy, which spans the full four-bin range by construction, and we withdraw it in favour of the electrode-resolved values here. The five polymorphs without an electrode entry cannot be assigned a DSI. The finding is consistent with the general principle that mechanical and structural factors govern degradation independently of bulk composition,\cite{Xu2017,Zheng2013} though the polymorph result is specific to fixed-composition structural variation.

\begin{table*}[t]
\small
\caption{\ The eight LiCuO$_2$ polymorphs in the Materials Project (static properties, left) and, for the three that are end-members of an insertion-electrode entry, the electrode-resolved descriptors and DSI (right). $E_\text{hull}$ of the polymorph and of the charged phase in meV~atom$^{-1}$; Li$_{a\text{--}b}$ denotes the lithium range spanned by the electrode entry}
\label{tbl:polymorph}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllllllll}
\hline
Space group & $E_\text{hull}$ & Vol./atom (\AA$^3$) & $\rho$ (g~cm$^{-3}$) & $E_g$ (eV) & Electrode entry & $\Delta V/V$ (\%) & $E_\text{hull,charge}$ & DSI & Category \\
\hline
%s
\hline
\end{tabular*}
\end{table*}

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_polymorph_analysis.png}
\caption{LiCuO$_2$ polymorph analysis. (a) Volume per atom against energy above hull for all eight polymorphs, coloured by density. (b) Delithiation volume change (blue, left axis) and charged-phase hull energy (orange, right axis) for the three polymorphs with an insertion-electrode entry. (c) DSI of the same three polymorphs; dotted lines mark the category boundaries.}
\label{fig:polymorph}
\end{figure*}

The single binary misclassification, Li$_2$MnO$_3$, reflects an activation mechanism beyond the three DSI descriptors, consistent with the two-phase structural complexity documented for Li-rich layered oxides:\cite{Yu2014} it exhibits low volumetric strain but high thermodynamic instability of the delithiated phase.\cite{Koyama2009} Rank disagreements are largest for the layered oxides, whose degradation is governed additionally by phase transformation and surface reactivity (for example the first-cycle irreversibility and local structural collapse documented for Li$_x$NiO$_2$\cite{Delmas1997}); these mechanisms lie outside the descriptor set and define the boundary of the DSI applicability domain (Fig.~\ref{fig:expanded}).

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_dsi_model.png}
\caption{DSI validation. (a) Pearson correlations among the normalized descriptor scores for the 11 validation materials. (b) $S_\text{vol}$ against $S_\text{stab}$, coloured by DSI score. (c) DSI score (circles) and single-descriptor score $S_\text{vol}$ (squares) against representative experimental cycle life on a logarithmic axis; shaded bands are the four DSI categories.}
\label{fig:dsi}
\end{figure*}

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_bootstrap_ci.png}
\caption{Bootstrap validation (10,000 resamples of the 11 materials). (a) Bootstrap distributions of Spearman $\rho$ for the single descriptor and the DSI. (b) Point estimates with 95\% percentile intervals.}
\label{fig:bootstrap}
\end{figure*}

\begin{figure}[h]
\centering
\includegraphics[width=0.48\textwidth]{cathodeai_weight_robustness.png}
\caption{DSI weight robustness across six weighting schemes (bars). The dashed line is the single-descriptor baseline and the dotted line the nested leave-one-out result obtained when weights are optimized on 10 materials and applied to the eleventh.}
\label{fig:robustness}
\end{figure}

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_full_dataset_correlation.png}
\caption{Full-dataset descriptor independence ($n=2{,}035$ entries in the 2.5--5.0~V window with both descriptors). (a) Distribution of $\Delta V/V$ and (b) of $E_\text{hull,charge}$, with the 95th-percentile normalization bounds. (c) Normalized $S_\text{vol}$ against $S_\text{stab}$, Pearson $r=-0.005$.}
\label{fig:fulldataset}
\end{figure*}

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_expanded_validation.png}
\caption{Mechanism-resolved validation across the 11 materials, coloured by dominant degradation mechanism. (a) DSI score against representative experimental cycle life. (b) Absolute difference between experimental and DSI rank by mechanism. (c) Rank difference against delithiation volume change.}
\label{fig:expanded}
\end{figure*}

\subsection{Supply-chain criticality}\label{sec:supply}

Supply-chain criticality is contextualized via the Herfindahl-Hirschman Index (HHI),\cite{DOJ2010} computed as the sum of squared national market shares (Fig.~\ref{fig:hhi}). Cobalt reaches HHI $= 5{,}162$ due to 70\% DRC supply concentration, classified as highly concentrated (HHI $>2{,}500$) and IRA-designated. Cu- and P-based top candidates avoid all IRA-designated critical minerals; although Cu and P show moderate-to-high HHI (2,674 and 3,030), they are substantially cheaper than Co (\$8.5 and \$0.8 against \$33 per kg), a 74\% and 98\% cost reduction respectively. The HHI is not the Layer 5 screening criterion, which uses the expert-assigned element criticality values listed in Section~\ref{sec:pipeline}.

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_supply_chain_hhi.png}
\caption{Supply-chain criticality via HHI. (a) HHI by element with concentration thresholds; red bars are IRA-designated critical minerals. (b) Element supply-chain score ($1-$criticality, Section~\ref{sec:pipeline}) against raw-material price; bubble area is proportional to HHI.}
\label{fig:hhi}
\end{figure*}

\subsection{Phosphate frameworks and multi-objective screening}\label{sec:po4}

Two-sample comparisons between phosphate-containing ($n=%d$) and other ($n=%d$) entries in the 813-entry oxide set are given in Table~\ref{tbl:po4} and Fig.~\ref{fig:po4}. With the scoring functions as designed, phosphates show a higher thermal-safety score ($\Delta=+%s$) and a higher DSI ($\Delta=+%s$), both with Welch $p<10^{-13}$. These differences are, however, largely built in: the thermal-safety score carries a $+0.15$ phosphate bonus and the DSI a $+0.10$ bonus (eqn~(\ref{eq:dsi})). Removing both bonuses leaves a thermal-safety difference of $+%s$ (Welch $p=%s$) and a DSI difference of $+%s$ (Welch $p=%s$; Mann-Whitney $p=%s$), and the two descriptors that enter the DSI without any phosphate term do not differ between the groups ($\Delta V/V$: %s against %s\%%, $p=%s$; $E_\text{hull,charge}$: %s against %s~eV~atom$^{-1}$, Welch $p=%s$). The phosphate advantage reported in the original submission was therefore a consequence of the design bonuses, which encode the well-documented thermal and structural stabilization by covalent P--O bonds,\cite{Padhi1997} not an independent discovery of the screen; we retain the bonuses as a deliberate design preference and state their effect explicitly. The energy-density penalty of phosphates ($\Delta=-%s$~Wh~L$^{-1}$, $p<10^{-4}$) involves no bonus and is a genuine feature of the dataset. This trade-off motivates explicit multi-objective treatment (Fig.~\ref{fig:pareto}). Pareto analysis over the 100 highest-composite entries, with the DSI as the durability axis, gives seven non-dominated entries for energy density against DSI (%s), two for energy density against cost (%s) and two for thermal safety against DSI (%s); no single material is optimal across the three application pairs. LiCuO$_2$-based compositions retain the top composite ranking in all five commodity-price scenarios owing to zero cobalt and nickel content (Fig.~\ref{fig:price}).

\begin{table*}[t]
\small
\caption{\ Mean property comparison between phosphate-containing ($n=%d$) and other ($n=%d$) entries in the 813-entry oxide set, with the phosphate design bonuses present and removed. $p$-values from Welch's $t$-test and the Mann-Whitney $U$ test}
\label{tbl:po4}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lllll}
\hline
Metric & Phosphate mean & Other mean & Welch $p$ & Mann-Whitney $p$ \\
\hline
%s
\hline
\end{tabular*}
\end{table*}

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_po4_comparison.png}
\caption{Phosphate against other oxide frameworks in the 813-entry set (boxes: quartiles; whiskers: 1.5 IQR; outliers omitted). (a) Thermal-safety score as designed and (b) with the phosphate bonus removed. (c) DSI as designed and (d) with the phosphate bonus removed. (e) Energy density. (f) Solid-state compatibility score.}
\label{fig:po4}
\end{figure*}

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{cathodeai_pareto_frontier.png}
\caption{Pareto fronts over the 100 highest-composite entries. (a) EV: energy density against DSI. (b) Consumer electronics: raw-material cost against energy density. (c) Grid storage: thermal-safety score against DSI. Coloured points are non-dominated; grey points are dominated.}
\label{fig:pareto}
\end{figure*}

\begin{figure}[h]
\centering
\includegraphics[width=0.48\textwidth]{cathodeai_price_sensitivity.png}
\caption{Composite rank of the eight highest-ranked base-case compositions under five commodity-price scenarios (Section~\ref{sec:pareto}). Li$_{0\text{--}1}$CuO$_2$ retains rank 1 in all scenarios.}
\label{fig:price}
\end{figure}

\subsection{Novel composition generation}\label{sec:novel}

As a separate, exploratory extension distinct from the supervised model above, 42 charge-balanced Li--M--O compositions (M = Fe, Mn, Ni, Co, Cu, Ti, V) were generated by enumerating oxidation states, lithium and metal counts and three structure-family templates (Section~\ref{sec:pareto}); they reduce to %d unique compositions. For each, the inputs to the 4-feature electrochemical Random Forest were assigned as follows and are listed item by item in ESI, Table~S3$^\dag$: voltage from a lookup by metal and oxidation state, clipped to the template's range; capacity from Faraday's law for the lithium content, clipped to the template's range (200--300~mAh~g$^{-1}$ for the layered template); and hull energies of 0.02~eV~atom$^{-1}$ assumed. The predicted energy densities of %d--%d~Wh~L$^{-1}$ follow directly from these assigned inputs (a clipped capacity of 300~mAh~g$^{-1}$ at 3.5--4.2~V), are theoretical values for full lithium extraction and exceed the training-set median of 1,722~Wh~L$^{-1}$ because the generator assigns high capacities, not because the model extrapolates: all 42 input vectors lie inside the training distribution of the 4-feature space (maximum $|Z| = 2.06$, on capacity; maximum leverage 0.0038 against a warning threshold of 0.0080; Fig.~\ref{fig:domain}). Independent first-principles verification of capacity, voltage, density and accessible lithium content, which these estimates do not provide, is required before any of them can be called a prediction.

Novelty and synthesizability were checked against the Materials Project using the compositions as generated. In the original submission this check was performed on formulas from which the lithium index had been stripped (Li$_2$Cu$_2$O$_3$ was queried as LiCu$_2$O$_3$, for example), which produced charge-imbalanced formulas that are absent from the database for that reason alone; five of the eight compositions originally reported as database-absent are in fact known compounds when written correctly (Li$_3$CoO$_3$, Li$_2$TiO$_3$, Li$_3$VO$_4$, LiVO$_3$ and Li$_2$Ti$_2$O$_5$; ESI, Table~S3$^\dag$). With the corrected query, %d of the %d unique compositions have Materials Project entries, of which %d lie below 50~meV~atom$^{-1}$ (%d on the convex hull) and %d between 50 and 100~meV~atom$^{-1}$ (Fig.~\ref{fig:synth}); recovery of LiCoO$_2$, LiNiO$_2$, LiMnO$_2$, LiFePO$_4$-type and Li$_x$V$_2$O$_5$-type chemistries\cite{Delmas1994} as on-hull entries is a positive control on the generator. The remaining %d compositions are absent from the database and constitute the exploratory candidate set (Table~\ref{tbl:novel}). Several of them (Li$_2$M$_2$O$_3$, formal M$^{2+}$; Li$_3$MO$_3$, formal M$^{3+}$) have unusual stoichiometries for which no structural prototype was assigned, so a low hull energy cannot be inferred and the low hull energy of the database-present compositions does not imply synthesizability of these. They are screening-level priors requiring future structural and first-principles evaluation, not validated discoveries.

\begin{table*}[t]
\small
\caption{\ Generated compositions absent from the Materials Project when queried with their correct stoichiometry. Voltage and capacity are assigned inputs (Section~\ref{sec:pareto}), not measurements; predicted energy density is from the 4-feature electrochemical Random Forest; supply-chain score follows Section~\ref{sec:pipeline}. All have solid-state score 1.00 by the voltage rule}
\label{tbl:novel}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllll}
\hline
Composition & Formal M state & Assigned $V$ (V) & Assigned $C$ (mAh~g$^{-1}$) & Pred.\ ED (Wh~L$^{-1}$) & Supply-chain score \\
\hline
%s
\hline
\end{tabular*}
\end{table*}

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_novel_compositions.png}
\caption{Generated compositions. (a) Assigned voltage against predicted energy density for the 42 generated compositions (stars; green present in the Materials Project, red absent) over the 1,724 known electrodes. (b) Predicted energy density of the database-absent compositions.}
\label{fig:novel}
\end{figure*}

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_synthesizability.png}
\caption{Synthesizability of the 42 generated compositions queried with their correct stoichiometry. (a) Share of compositions by minimum hull energy of matching Materials Project entries, or absent. (b) Minimum hull energy for each database-present unique composition.}
\label{fig:synth}
\end{figure*}

Chemical-space mapping via UMAP\cite{McInnes2018} over 132 MatMiner compositional features across the 1,724 known and 42 generated compositions shows the generated compositions lying within or adjacent to the known Li--M--O families rather than in unpopulated regions (Fig.~\ref{fig:umap}), as expected for compositions built from the same seven metals. The discovery zone defined in Section~\ref{sec:funnel} identifies %d known compositions combining top-quartile composite score, discharged-phase hull energy below 50~meV~atom$^{-1}$ and top-quartile energy density (Fig.~\ref{fig:discovery}).

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_applicability_domain.png}
\caption{Applicability domain in the 4-feature space of the model used for generated compositions. (a) Leverage distribution of the 1,864 training entries (log count) with the generated compositions as vertical lines and the warning threshold $3p/n$. (b) $|Z|$-scores of each generated composition's four inputs relative to the training set.}
\label{fig:domain}
\end{figure*}

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_umap.png}
\caption{UMAP embedding of 132 MatMiner compositional features for 1,724 known and 42 generated compositions. (a) Coloured by energy density (known) and predicted energy density (generated, stars). (b) Coloured by material family.}
\label{fig:umap}
\end{figure*}

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_discovery_sweetspot.png}
\caption{Discovery zone. (a) Composite score against hull energy of the discharged phase for the 787 scored entries, coloured by energy density; circled points satisfy all three zone criteria. (b) Energy density against DSI for the zone members, coloured by DSI category.}
\label{fig:discovery}
\end{figure*}

\subsection{Uncertainty quantification}\label{sec:uq}

Ensemble variance across the 100 Random Forest estimators generates 95\% prediction intervals (Fig.~\ref{fig:uncertainty}). Empirical coverage on the %d held-out test entries is %s\%%, above the nominal 95\%, so the intervals are conservative rather than sharply calibrated. Mean interval half-width is $\pm %s$~Wh~L$^{-1}$ and half-width rises with capacity ($r=%s$), reflecting sparser training coverage in the high-capacity regime.

\begin{figure*}[t]
\centering
\includegraphics[width=0.85\textwidth]{cathodeai_uncertainty.png}
\caption{Prediction uncertainty. (a) Predicted energy density with 95\% intervals for the held-out test entries, sorted by prediction, with the Materials Project values overlaid. (b) Interval half-width against capacity.}
\label{fig:uncertainty}
\end{figure*}

\subsection{Top-ranked candidates}\label{sec:top}

Table~\ref{tbl:top10} presents the ten highest-ranked unique compositions from the composite score integrating all eight scoring layers, with the DSI as the Layer 8 durability term (Section~\ref{sec:pipeline}). Compositions are written in Materials Project insertion-electrode notation, Li$_{a\text{--}b}$ denoting the lithium range spanned by the electrode entry. LiCuO$_2$-based compositions retain the top composite ranking, driven substantially by supply-chain and recyclability terms (a combined 35\% of the composite weight, ESI Table~S2$^\dag$) rather than electrochemical performance or durability: the two highest-ranked entries fall in DSI category C (moderate), and the highest-durability entries in the table are copper phosphates in category A. We note that lithium extraction from LiCuO$_2$ has been reported to irreversibly release oxygen above 4.0~V,\cite{Arai1998} a practical stability caveat not captured by the composite score and relevant to interpreting its top ranking.

\begin{table*}[t]
\small
\caption{\ Ten highest-ranked unique compositions from the complete eight-layer composite score (Section~\ref{sec:pipeline}); duplicate electrode entries of the same composition are omitted. Cost is the raw-material estimate by dominant metal (US\$~kWh$^{-1}$); $\Delta V/V$ and $E_\text{hull,charge}$ (eV~atom$^{-1}$) are the DSI inputs; DSI categories as in Table~\ref{tbl:validation}}
\label{tbl:top10}
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llllllllll}
\hline
Rank & Composition & $V$ (V) & ED (Wh~L$^{-1}$) & Cost & $\Delta V/V$ (\%) & $E_\text{hull,charge}$ & DSI & Category & Composite score \\
\hline
%s
\hline
\end{tabular*}
\end{table*}

\section{Conclusions}

Structure-resolved descriptors outperform composition-only heuristics for lithium-ion cathode durability screening in the three tests we could perform. A transparent Degradation Screening Index ranks the durability of 11 experimentally characterized cathodes better ($\rho=%s$) than a metal-identity heuristic ($\rho=%s$) or a single strain descriptor ($\rho=%s$); the same composition, LiCuO$_2$, spans three of four durability categories across its polymorph-resolved electrode entries; and once durability and supply-chain criticality are considered alongside performance, no single material is Pareto-optimal for all applications. For energy-density prediction the picture is different and we state it plainly: neither compositional nor structural descriptor sets alone are predictive, a learned model adds nothing to the arithmetic identity once density is known, and its usefulness is limited to coverage of incomplete records and interval estimation. The phosphate advantage in our composite scores follows from design bonuses rather than from the data. The principal limitations, a small ($n=11$) validation set that cannot support learned weights, a %s\%% category reassignment rate under realistic DFT error and exploratory generated compositions lacking resolved crystal structures, define the natural next steps: a larger and chemistry-stratified validation set, and first-principles evaluation of the highest-ranked candidates to close the loop between screening and experiment.

\section{Experimental}\label{sec:exp}

\subsection{Data source}\label{sec:data}

All materials data were obtained from the Materials Project database\cite{Jain2013} through its REST API (2,774 Li insertion-electrode documents and 16,510 Li- and O-containing structural documents; the counts were identical at the original query and at the revision query, September 2026). Each insertion-electrode document names the Materials Project identifiers of its charged and discharged end-members; structural descriptors (formation energy, band gap, volume per atom, number of elements, density, energy above hull) were taken from the structural document of the discharged end-member, giving 1,724 of the 1,886 filtered entries (91.4\%) with complete features. The original submission instead merged on base chemical formula after averaging structural descriptors over every entry sharing that formula; 1,415 of the resulting 1,702 entries received such averaged descriptors, the averaging mixed polymorphs and, because the lithium index was stripped before matching, also mixed distinct lithium stoichiometries (Li$_2$CuO$_2$ entries were averaged into LiCuO$_2$, for example). The identifier-level merge removes both problems and the conclusions are unchanged (ESI, Table~S5$^\dag$). All DFT-derived properties use the \texttt{MaterialsProject2020Compatibility} correction scheme for GGA/GGA+U mixing errors, which builds on the GGA+U parameter-fitting methodology of Wang \textit{et al.}\cite{Wang2006,Cococcioni2005} and the high-throughput DFT infrastructure of Jain \textit{et al.}\cite{Jain2011} Materials Project reaction energies relevant to phase stability carry a mean absolute error of approximately 24~meV~atom$^{-1}$ against experiment;\cite{Hautier2012} the sensitivity of our rankings to an error of this size is quantified in Section~\ref{sec:dsi}.

\subsection{Eight-layer screening pipeline}\label{sec:pipeline}

Layer 1, voltage window (2.5--5.0~V), intentionally extends beyond the $\sim$4.3~V stability limit of standard carbonate electrolytes to capture candidates for emerging solid-state and water-in-salt systems.\cite{Suo2015,Kato2016} Layer 2 enforces capacity $>50$~mAh~g$^{-1}$. Layer 3 restricts to oxide frameworks (entries containing F, Cl, Br, S or N are removed, as are ClO-, VF$_5$- and CF-based entries). Layer 4 excludes Pb, Cd, Hg, As, Tl and Be (RoHS/REACH) and the rare or precious elements Pt, Ir, Os, Ru, Rh, Pd, Au, Re, In and Ge. %s Layer 6 scores recyclability analogously, as the mean of expert-assigned per-element hydrometallurgical recovery values over the same element set (range 0.30--0.95, e.g.\ Co 0.95, Fe 0.50).\cite{Gaines2018} Layer 7 scores thermal safety from an expert-assigned per-metal base score informed by oxygen-release onset temperature (e.g.\ Fe 0.95 at 600~$^\circ$C onset, Ni 0.40 at 220~$^\circ$C, Co 0.45 at 250~$^\circ$C), with a $+0.15$ bonus for phosphorus-containing frameworks and $+0.05$ for Mn$_2$- or Mn$_3$-type spinel formulas, capped at 1.0. Layer 8 is the DSI (Section~\ref{sec:dsi}); it is the only cycle-life estimate used anywhere in this paper. The original submission used three different cycle-life estimators in different places (a metal-identity lookup in the composite score and Table~\ref{tbl:top10}, a volume-strain binning with voltage and phosphate factors in the heuristic comparison, and the DSI in the validation); all have been replaced by the DSI, and the metal-identity lookup is retained only as the heuristic being tested (base cycles Fe 2500, Ti 2000, Mn 1000, Co 1000, Cr 900, Ni 800, V 700, Cu 600 by first-listed dominant metal, multiplied by $\max(0.3,\,1-2(E_\text{hull,charge}+E_\text{hull,discharge}))$, by 0.75 above 4.3~V or 0.90 above 4.0~V, and by 1.30 for phosphorus-containing formulas). The composite score used to rank candidates in Table~\ref{tbl:top10} and Fig.~\ref{fig:pareto} is $0.25\,P/P_\text{max} + 0.20\,S_\text{supply} + 0.15\,S_\text{recyc} + 0.15\,S_\text{solid} + 0.10\,S_\text{cost} + 0.10\,S_\text{thermal} + 0.05\,\text{DSI}$, where $P$ is the Performance Score defined in ESI, Table~S2$^\dag$ together with the other composite scores; entries without a computable DSI receive the median DSI in the last term.

The market-share-derived Herfindahl-Hirschman Index reported in Section~\ref{sec:supply} ($\sum_i s_i^2$ over national production shares, e.g.\ cobalt HHI $=5{,}162$) is a separate, downstream analysis applied to the top-ranked candidates for supply-chain risk contextualization; it is not the criterion used to screen the dataset in Layer 5 above.

\subsection{Machine learning methodology}\label{sec:mlmethod}

Six feature sets (Table~\ref{tbl:features}) and four architectures, Linear Regression, Random Forest (100 estimators, default scikit-learn 1.6 parameters), XGBoost (100 estimators, default parameters, \texttt{xgboost} 2.1) and a two-hidden-layer (64, 32 units, ReLU) Neural Network, were evaluated by 5-fold cross-validation with shuffled random folds (seed 42) and, additionally, with \texttt{GroupKFold} using the base formula (lithium index stripped) as the group; MatMiner Magpie descriptors\cite{Ward2018} (\texttt{matminer} 0.9) were computed from the base formula and the Lasso-selected subset used $\alpha=0.01$. Features were standardized within each analysis. Because structural descriptors are taken from the electrode's own discharged structure, electrode entries of different polymorphs of one composition receive different structural features; the original formula-level merge did not have this property. SHAP values used \texttt{TreeExplainer} on a 200-estimator Random Forest fitted to all 1,724 entries (\texttt{shap} 0.42).\cite{Lundberg2020} Prediction intervals used $\pm1.96$ standard deviations of the per-tree predictions of the production model on the held-out 20\% split (seed 42). In the missing-data experiment, 30\% of capacity values were masked at random (seed 42) after training and replaced by the training-set mean, or by the prediction of a Random Forest trained on the seven remaining features of unmasked training entries.

\subsection{Degradation Screening Index}\label{sec:dsimethod}

The DSI (eqn~(\ref{eq:dsi})) is a screening heuristic for durability \emph{ranking}, not a mechanistic cycle-life model; it does not capture kinetic effects, electrolyte reaction specifics or exact cycle numbers. DSI scores are reported as relative durability categories, A (DSI $\geq0.75$), B ($0.55$--$0.75$), C ($0.35$--$0.55$) and D ($<0.35$); the Spearman correlations of Section~\ref{sec:dsi} are computed on these four levels unless the continuous score is stated, and no cycle numbers are inferred from them. For the 813 screened entries the DSI uses the entry's own maximum delithiation volume change and charged-phase hull energy from the insertion-electrode document, the band gap of its discharged structure and a phosphate indicator for phosphorus-containing formulas. Representative experimental cycle-life figures and volumetric strain values for the 11 validation materials are compiled from the literature,\cite{Reimers1992,Padhi1997,Armstrong1996,Jung2017,Liu2015,Zhong1997,Ohzuku1995,Bramnik2007,Mizushima1980,Watanabe2014,Kalyani1999} while delithiated-phase energy above hull and band gap are taken from Materials Project GGA+U calculations (Section~\ref{sec:data}), consistent with ESI, Table~S1$^\dag$. The experimental figures are representative order-of-magnitude values for each chemistry that vary with electrode loading, voltage window and depth of discharge; they are used solely to establish a rank order, and the sources for NCA and Li$_2$MnO$_3$ in particular do not report a single cycles-to-failure figure (ESI, Table~S1$^\dag$).

\subsection{Pareto, novel composition and applicability domain}\label{sec:pareto}

A material is Pareto-optimal if no other material dominates it on both objectives; non-dominated sorting was applied to the 100 highest-composite entries for three application pairs (EV: energy density and DSI; consumer: cost and energy density; grid: thermal-safety score and DSI). Price sensitivity re-scored all entries under five commodity scenarios (base 2024 prices; Co $+100$\%; Ni $+50$\%; Li $-50$\%; Fe and Mn halved) with the raw-material cost term weighted 0.15 in place of the DSI and cost terms above. Generated compositions Li$_a$M$_b$O$_c$ were enumerated for $a \in \{1,2,3\}$, $b \in \{1,2\}$ and the oxidation states Fe$^{2+,3+}$, Mn$^{2+,3+,4+}$, Ni$^{2+,3+,4+}$, Co$^{2+,3+}$, Cu$^{+,2+}$, Ti$^{3+,4+}$ and V$^{3+,4+,5+}$, keeping integer oxygen counts, with voltage from a per-state lookup and capacity from Faraday's law, each clipped to the range of a layered (3.5--4.5~V, 200--300~mAh~g$^{-1}$), spinel (3.8--4.8~V, 100--150~mAh~g$^{-1}$) or olivine (3.0--3.8~V, 150--200~mAh~g$^{-1}$) template; duplicates by formula string were removed, leaving 42. Database presence and minimum hull energy were queried for each composition reduced to its smallest integer formula; the synthesizability threshold is $E_\text{hull}<50$~meV~atom$^{-1}$.\cite{Sun2016} The applicability domain was assessed in the 4-feature space of the model actually applied to these compositions, by $|Z|$-scores and leverage relative to the 1,864 training entries with a warning threshold of $3p/n$.

\subsection{Statistical analysis}\label{sec:stats}

Welch's $t$-test and the Mann-Whitney $U$ test for the phosphate comparison ($n=%d$ against $%d$); Spearman correlation for experimental validation ($n=11$) and for the heuristic against the DSI ($n=787$); Pearson correlation for DSI descriptor independence ($n=2{,}035$); bootstrap CIs (10,000 resamples, rank-based); leave-one-out and nested leave-one-out over the 11 validation materials; Monte Carlo perturbation of hull energies with $N(0,\,24~\text{meV~atom}^{-1})$ noise (2,000 draws for the validation set, 1,000 for the Pareto fronts, 500 for the 813-entry category assignments). All tests two-tailed, $\alpha=0.05$, performed in Python 3.9 using \texttt{scipy.stats} 1.13 and \texttt{scikit-learn} 1.6.

"""
body = body.replace("\\%%", "@@PP@@").replace("\\%", "\\%%").replace("@@PP@@", "\\%%")
body = body % (
    zone_rows, zone_n,
    # ML section
    f3(r13["Combined (8)"]["random"][0]), f3(r13["Combined (8)"]["grouped"][0]), f3(r13["Electrochemical only (4)"]["random"][0]), f3(r13["Electrochemical only (4)"]["grouped"][0]),
    f3(r13["Structural only (6)"]["random"][0]), f3(r13["Structural only (6)"]["grouped"][0]),
    f3(r213["V + C + density"][0]), f3(r213["arith"]), "%%MM_MAX%%",
    # arith section
    f3(T["r214_id"]["k"] and r213["arith"]), f"{T['r214_id']['k']:.4f}", f"{T['r214_id']['median_ratio']:.4f}", f"{T['r214_f']['r2_single']:.4f}", f"{T['r214_f']['r2_multi']:.4f}",
    f3(r216["test_complete"]), f3(r216["test_imputed"]), f3(r216["arith_rf_imp"]), f3(r216["ml_rf_imp"]), f3(r216["cap_imp_r2"]),
    T["table_missing"],
    # DSI validation
    f3(V["rho_bins"]), f3(V["p_bins"]), f3(V["rho_cont"]), f3(V["p_cont"]), f3(V["rho_single"]), f3(V["p_single"]),
    f3(hv["rho_nostab"]), f3(hv["p_nostab"]), f3(hv["rho_stab"]), f3(hv["p_stab"]),
    T["table7"], f3(V["no_lto"][0]), f3(V["no_lto"][1]), f3(V["no_lto"][2]), f3(V["no_lto"][3]),
    # weights
    f"{nest['rho']:.2f}", f"{nest['p']:.2f}", f3(nest["insample_best"][0]), 231, f3(sw[0]), f3(sw[1]), f3(sw[2]), int(round(sw[3] * 100)),
    f3(V["strat"]["layered oxides"][1]), f3(V["strat"]["layered oxides"][2]), f3(V["strat"]["layered oxides cont"][1]), f3(V["strat"]["layered oxides cont"][2]), f3(V["strat"]["layered oxides"][3]),
    # DFT error
    f3(RD["val_rho_med"]), f3(RD["val_rho_5"]), f3(RD["val_rho_95"]), f"{RD['cat_flip_813']*100:.0f}", f"{RD['jac_ev']:.2f}", f"{RD['jac_grid']:.2f}",
    # heuristic vs DSI
    f"{hd[1]:.2f}", f"{hd[0]:.2f}",
    # polymorph
    f"{pol['C2/m']['dV/V (%)']:.1f}", f"{pol['C2/m']['E_hull charge (eV)']*1000:.0f}", f"{pol['C2/m']['DSI']:.2f}", f"{pol['R-3m']['dV/V (%)']:.1f}", f"{pol['R-3m']['E_hull charge (eV)']*1000:.0f}", f"{pol['R-3m']['DSI']:.2f}", f"{pol['Cm']['DSI']:.2f}",
    T["table5"],
    # PO4
    po_n, non_n, f3(rw["Thermal Safety Score"][0] - rw["Thermal Safety Score"][1]), f3(rw["DSI"][0] - rw["DSI"][1]),
    f3(rw["Thermal Safety Score (no PO4 bonus)"][0] - rw["Thermal Safety Score (no PO4 bonus)"][1]), f3(rw["Thermal Safety Score (no PO4 bonus)"][2]),
    f3(rw["DSI (no PO4 bonus)"][0] - rw["DSI (no PO4 bonus)"][1]), f3(rw["DSI (no PO4 bonus)"][2]), f3(rw["DSI (no PO4 bonus)"][3]),
    f"{rw['Max Volume Change (%)'][0]:.2f}", f"{rw['Max Volume Change (%)'][1]:.2f}", f"{rw['Max Volume Change (%)'][2]:.2f}", f"{rw['Stability Charge (eV)'][0]:.3f}", f"{rw['Stability Charge (eV)'][1]:.3f}", f"{rw['Stability Charge (eV)'][2]:.2f}",
    f"{abs(rw['Energy Density (Wh/L)'][0] - rw['Energy Density (Wh/L)'][1]):.0f}",
    ", ".join(re.sub(r"^Li([\d\.]+)-([\d\.]+)", r"Li$_{\1\\text{--}\2}$", re.sub(r"(?<=[A-Za-z\)])(\d+)", r"$_{\1}$", x["Formula"])) for x in R["pareto"]["EV: ED vs DSI"]),
    ", ".join(re.sub(r"^Li([\d\.]+)-([\d\.]+)", r"Li$_{\1\\text{--}\2}$", re.sub(r"(?<=[A-Za-z\)])(\d+)", r"$_{\1}$", x["Formula"])) for x in R["pareto"]["Consumer: ED vs cost"]),
    ", ".join(re.sub(r"^Li([\d\.]+)-([\d\.]+)", r"Li$_{\1\\text{--}\2}$", re.sub(r"(?<=[A-Za-z\)])(\d+)", r"$_{\1}$", x["Formula"])) for x in R["pareto"]["Grid: thermal vs DSI"]),
    po_n, non_n, T["table8"],
    # novel
    NS["n_unique"], int(round(NS["ed_min"])), int(round(NS["ed_max"])), NS["n_present_unique"], NS["n_unique"], NS["lt50_unique"], NS["onhull_unique"], NS["mid_unique"], T["n_absent"], T["table9"], zone_n,
    # UQ
    U["n"], f"{U['coverage']:.1f}", f"{U['mean_hw']:.0f}", f"{U['r']:.3f}",
    T["table10"],
    # conclusions
    f"{V['rho_bins']:.2f}", f"{hv['rho_nostab']:.2f}", f"{V['rho_single']:.2f}", f"{RD['cat_flip_813']*100:.0f}",
    # experimental: layer 5 text (already written earlier in file; re-insert)
    "%%LAYER5%%",
    po_n, non_n)
# fix the arithmetic-section first placeholder (R2 arith id)
body = body.replace(f"with $R^2 = {f3(T['r214_id']['k'] and r213['arith'])}$ and a best-fit", f"with $R^2 = {f3(r213['arith'])}$ and a best-fit")
# Layer 5 text: reuse the disclosure paragraph inserted earlier
m = re.search(r"Layer 5 scores supply-chain criticality.*?Co-containing compositions: \$1-0\.95=0\.05\$\)\.", s, flags=re.S)
assert m, "layer5 text not found"; body = body.replace("%LAYER5%", m.group(0))
body = body.replace("%TABLE2%", "%%TABLE2%%").replace("%TABLE3%", "%%TABLE3%%").replace("%TABLE4%", "%%TABLE4%%").replace("%MM_MAX%", "%%MM_MAX%%")
s = s[:r0] + body + s[r1:]
# figure path and footnote update
rep("\\usepackage{epstopdf}", "\\usepackage{epstopdf}\n\\graphicspath{{figures_revised/}}")
rep("Electronic Supplementary Information (ESI) available: complete literature sources for the Degradation Screening Index validation set, and definitions of the auxiliary composite scoring functions.",
    "Electronic Supplementary Information (ESI) available: literature sources and DSI values for the validation set, definitions of the composite scoring functions, item-by-item inputs for the 42 generated compositions, LiCuO$_2$ electrode entries and a comparison of the formula-level and identifier-level structural merges.")
open(p, "w").write(s)
print("rewritten; placeholders remaining:", re.findall(r"%%[A-Z0-9_]+%%", s))
print("em-dashes:", s.count("\u2014"), "| 'Oxford' check ', and ':", len(re.findall(r", and ", s)))
