# AUDIT REQUEST 1 — end of Phase 1 (problem definition)

You are an **independent auditor**. You have not seen the other auditor's response and must not
guess it. Be blunt. An audit that changes nothing and explains nothing is a failed audit.

## Context

A study is being executed on a strictly open-source stack: **LAMMPS** (MD), **Cantera/Python**
(kinetics), **OpenFOAM v2406** (CFD). WSL2, 16 physical cores, **23 GB RAM**, **no GPU**
(`nvidia-smi` absent). Topic: derive a bubble-coverage closure Θ(j, v, θ) for alkaline water
electrolysis in which the wettability dependence comes from potential-aware molecular dynamics
rather than from a fitted legacy correlation, then propagate it to cell-scale polarisation.

Read these files before answering:
- `/home/azan/research/T12_MD_wettability_closure/02_problem/problem_statement.md`
- `/home/azan/research/T12_MD_wettability_closure/02_problem/prior_art_delta.md`
- `/home/azan/research/T12_MD_wettability_closure/02_problem/design_spec.md`
- `/home/azan/research/T12_MD_wettability_closure/02_problem/parameter_matrix.csv`
- `/home/azan/research/T12_MD_wettability_closure/01_env/benchmark.md`
- `/home/azan/research/T12_MD_wettability_closure/50_validation/anchors/A1_rox2022_porous_ni_coverage.md`
- `/home/azan/research/T12_MD_wettability_closure/00_admin/DECISIONS.md`

## Established facts — do not re-litigate

- Environment is provisioned. LAMMPS built with **ELECTRODE**; `electrode/conp` reproduces the
  shipped reference log **bitwise** (proof in `01_env/electrode_proof/`).
- Water model is **SPC/E, not mW/Stillinger–Weber** — coarse-grained water was ruled out
  pre-execution as unable to represent an electrochemical interface.
- 3D parametric VOF is infeasible on this hardware (measured: ~15 days/case, 15.6M cells vs ~5M
  practical ceiling). The parametric campaign is **axisymmetric**; one coarsened 3D corner confirms.
- Riegel is a **legacy comparability benchmark only**, not a coverage validation, because channel
  gas fraction is Faraday-constrained.

## Specific questions

**Q1 — Is the physics right?**
Check the loss decomposition (eqs 1–5 of `problem_statement.md`), the Butler–Volmer coverage
factor (1 − Θ), the Bruggeman exponent, and the claim that Θ = 0.8 costs ≈49 mV at α = 0.5, 353 K.
Are the equations dimensionally consistent and is the coverage entering in the right places?
Is anything double-counted — in particular, is bubble blockage counted both in active area **and**
in effective conductivity?

**Q2 — Are the three predictions P1–P3 actually falsifiable, and is P3 well-posed?**
P3 asserts a boundary exists in (j, v) beyond which departure is Marangoni-controlled and θ-
insensitive. Is that boundary reachable within the stated envelope (j = 10²–10⁴ A m⁻²,
v = 0–0.2 m s⁻¹)? If Marangoni dominates the *entire* industrial envelope, does the study still
have a result?

**Q3 — The Vogt/Rox discrepancy.**
Vogt predicts Θ ≈ 0.15 at 500 A m⁻²; Rox et al. (anchor A1) report the electrode "nearly fully
covered" above 50 mA cm⁻². I have attributed this to a **measurand mismatch** (adhering-bubble
surface coverage vs projected-area coverage on a *porous* electrode, including detached rising
bubbles in the field of view). **Is that attribution correct, or am I explaining away a real
physical disagreement?** What specific analysis would settle it?

**Q4 — Is the MD plan capable of delivering a usable contact angle?**
Consider: SPC/E water with classical K⁺/OH⁻ (no Grotthuss transport); a nanoscale cylindrical cap
with line-tension extrapolation from 3 base radii (R = 3, 5, 8 nm); ΔΨ = 0–1.0 V via
`fix electrode/conp`. **Will the extrapolated θ_∞ be meaningful for a continuum contact-angle
boundary condition on a 50–100 µm bubble?** If not, what is the minimum change that makes it so?
Note the continuum model needs *underwater gas-bubble advancing and receding* angles under flow,
not an equilibrium droplet angle in a static cell.

**Q5 — Budget realism.**
The active matrix is 96 cases, 1742 h total, 1230 h critical path (51 days), assuming
`fix electrode` costs 2–4× over plain PPPM (unmeasured — OI-1). Where is this most likely to be
wrong, and which cases would you cut first?

**Q6 — Standing questions.**
(a) What would a hostile Reviewer 2 attack first in this problem definition?
(b) Which planned result is most likely to be an artefact of a numerical choice rather than physics?
(c) What is claimed more strongly than the evidence supports?

Write your response as markdown. Be specific and numeric wherever possible.
