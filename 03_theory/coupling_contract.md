# COUPLING CONTRACT
One row per coupling arrow. This file is the evidence that parameter *passing* occurred rather than
scales being juxtaposed — the distinction the scoring rubric rewards and the one the pre-execution
audit specifically challenged.

**Direction is strictly one-way: MD → bridge → VOF → regression → CELL.**
**No two-way feedback is claimed anywhere.** Where a quantity appears to flow backwards (e.g. local
current density depends on coverage, which depends on current density), it is resolved *within* a
single solver, not across the chain — see §3.

---

## 1. The arrows

| # | From | To | Quantity | Symbol | Units | Format | Interp / extrapolation rule | Validity box | Uncertainty carried |
|---|---|---|---|---|---|---|---|---|---|
| **C1** | **[MD]** LAMMPS | bridge **[AN]** | macroscopic contact angle, line-tension extrapolated | θ_∞(ΔΨ, c, T) | degrees | `10_md/results/theta_table.csv` | linear in ΔΨ within measured range; **no extrapolation beyond ±1.0 V** | ΔΨ ∈ [0, 1.0] V; c ∈ {20, 30} wt%; T ∈ {298, 333, 353} K | ± SE from block averaging **and** the spread between circular-fit and COM estimators, propagated as a θ band |
| **C2** | **[MD]** LAMMPS | **[VOF]** | liquid–vapour surface tension | γ_lv(c, T) | N m⁻¹ | same CSV | linear in T | as C1 | ± Kirkwood–Buff block SE |
| **C3** | **[MD]** LAMMPS | **[VOF]** / **[CELL]** | dissolved-H₂ diffusivity | D_H₂(c, T) | m² s⁻¹ | same CSV | Arrhenius in T | as C1 | ± Yeh–Hummer-corrected MSD fit SE |
| **C4** | bridge **[AN]** | **[VOF]** | wall contact-angle boundary condition | θ (static) or θ_A/θ_R (dynamic) | degrees | `constant.../alphaContactAngle` entry | **none** — set per case, not interpolated | as C1 | propagated by running the campaign at θ_∞ ± σ_θ at 3 corners |
| **C5** | **[CT]** Cantera | **[VOF]** and **[CELL]** | exchange current density | j₀(T, c_KOH) | A m⁻² | `foamFile` lookup table, pre-tabulated | bilinear in (T, c); **clamped at table edges, never extrapolated** | T ∈ [298, 353] K; c ∈ [20, 30] wt% | mechanism-parameter uncertainty stated, not propagated (algebraic evaluation) |
| **C6** | **[VOF]** campaign | regression **[AN]** | resolved coverage, **both measurands** | Θ_adh, A_cov,proj | – | `20_vof/results/coverage_campaign.csv` | n/a — raw campaign output | j ∈ [10², 10⁴] A m⁻²; v ∈ [0, 0.2] m s⁻¹; θ ∈ [30°, 150°] | ± time-averaging SE over the quasi-steady window |
| **C7** | regression **[AN]** | **[CELL]** | the closure itself | Θ(j, v, θ); params {C, a, b, C₄} | – | `40_closure/closure_library/T12_closure.H` (OpenFOAM-includable) | evaluated pointwise; **refuses to evaluate outside the validity box — returns an error, not a silent clamp** | the C6 box, intersected with the θ-controlled region Λ > 1 | 95% CI on {C, a, b, C₄} from the NLS covariance; held-out RMSE reported |
| **C8** | **[AN]** applicability map | **[CELL]** | validity gate | Λ(j, v) = \|F_cap\|/\|F_Mar\| | – | `40_closure/results/applicability_map.csv` | boolean gate on C7 | as C6 | boundary located to the campaign's (j, v) resolution |

## 2. Why C7's refusal matters

The study exists because a closure fitted at 21–104 A m⁻² (corpus E20) is applied at 6000 A m⁻²
(corpus E04). **Reproducing that error with a new closure would be self-defeating.** The
implementation therefore raises a `FatalError` outside its validity box rather than silently
extrapolating. Any cell-scale result reported in the manuscripts is, by construction, inside the box.

## 3. Apparent circularity, and how it is resolved without a two-way claim

Coverage reduces active area, which raises local current density, which increases gas production,
which raises coverage. This is a genuine feedback — but it is closed **inside** a single solver:

- **[VOF]**: the Faradaic wall flux uses the *local, instantaneous, resolved* interface state. There
  is no closure in the loop — coverage is an *output*, measured from the resolved interface, never
  an input. **No circularity exists here.**
- **[CELL]**: the closure Θ(j, v, θ) is evaluated with the *local* j from the previous outer
  iteration and converged as part of the normal segregated solution. This is a fixed-point iteration
  within one solver, and convergence of Θ is a reported QC metric.

**What is explicitly NOT done:** the cell-scale result never feeds back to the VOF campaign or the
MD. The chain runs once, forward. Claiming otherwise would be false.

## 4. Double-counting guard

Bubble gas appears in two distinct populations and must be counted once each:

| Population | Symbol | Where it acts | Equation |
|---|---|---|---|
| **Adhering** at the electrode | Θ | reduces **active area** | (33), (39) |
| **Dispersed** in the bulk electrolyte | ε_g | reduces **conductivity** | (36), (37), (40) |

A bubble that departs **leaves Θ and joins ε_g**. The implementation must conserve that transfer and
the QC script asserts it. *Raised for Audit 1 Q1 precisely because it is the easiest way for this
study to be quietly wrong.*

## 5. What crosses the chain, and what does not

**Crosses:** θ_∞, γ_lv, D_H₂ (MD → continuum); Θ closure (VOF → cell); Λ gate (analysis → cell).

**Does NOT cross, and must not be claimed to:**
- Molecular structure of the double layer — informs interpretation only, never a continuum input.
- MD-derived viscosity — the continuum uses experimental KOH viscosity, because the classical OH⁻
  model lacks Grotthuss transport and its transport coefficients are structurally limited.
  **Using an MD viscosity here would import a known model deficiency into the continuum for no
  gain.** MD viscosity is reported as a force-field validation check only.
- Any cell-scale quantity backwards to any smaller scale.

## 6. Traceability

Each arrow's payload file carries a header stamping: source case IDs, git commit of the generating
script, date, and the validity box. A manuscript number without a traceable payload file is written
`[UNVERIFIED — trace pending]` and listed in `OPEN_ITEMS.md`.
