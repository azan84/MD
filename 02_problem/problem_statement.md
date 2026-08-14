# PROBLEM STATEMENT — T12 rev B
This document is attacked by both auditors at Audit 1 and becomes the manuscripts' Introduction.
Corpus citations are extraction-record IDs from `/home/azan/electrode/extraction/`
(corpus hash `9dd4b795a80ec687`).

---

## 1. The physical problem

In alkaline water electrolysis, H₂ evolves at the cathode and O₂ at the anode as discrete bubbles
that nucleate, grow and adhere before detaching. Adhering bubbles blank off catalytically active
area and displace conductive electrolyte. The blanked fraction — the **bubble coverage** Θ ∈ [0,1) —
degrades cell performance through three distinct routes.

### 1.1 Loss decomposition

Cell voltage at current density *j*:

**(1)**  `U_cell = U_rev + η_act,a + |η_act,c| + η_ohm + η_conc`

**Activation.** With a fraction Θ of the electrode screened, the same total current is driven
through the remaining area (1 − Θ), so the *local* current density rises to j/(1 − Θ). Through
Butler–Volmer,

**(2)**  `j = (1 − Θ) · j₀ · [exp(α_a n F η_act / RT) − exp(−α_c n F η_act / RT)]`

> **Kinetic convention, stated not assumed (corrected at Audit 1, A1.1).** The exponent carries `n`
> explicitly; this work uses **n = 1**, α = 0.5, so `αn = 0.5`. Inserting the overall two-electron
> HER stoichiometry into a one-step Butler–Volmer exponent is not automatically justified and is not
> done here. `j` is the **geometric** current density; `j₀` is referenced to the clean exposed area;
> the porous-electrode roughness/ECSA factor is carried explicitly, never hidden inside `j₀`.
> A single Θ is valid only because this work models the **cathode (HER)** and does not model the
> anode — it is not a claim that one Θ describes both electrodes.

and in the Tafel limit the coverage penalty is explicit:

**(3)**  `Δη_act = (RT / (α n F)) · ln[1 / (1 − Θ)]`

At α = 0.5, n = 1, T = 353 K, `RT/(αnF) = 60.84 mV`, so **Θ = 0.2 costs 13.6 mV and Θ = 0.8 costs
97.9 mV**.

> **⚠️ CORRECTED AT AUDIT 1 (A1.1).** The values previously stated here — 6 mV and 49 mV — silently
> assumed `αn = 1` (n = 2) while the printed equation omitted `n`. Equation and numbers now agree.

The penalty is strongly
non-linear in Θ, which is why an error in the closure matters more at high current density — the
behaviour E04 reports when it finds coverage the strongest-effect closure it tested.

**Ohmic.** Dispersed gas of local fraction ε lowers electrolyte conductivity. A Bruggeman-type
correction is standard in the corpus (E04, E05, E07, E13):

**(4)**  `σ_eff = σ₀ (1 − ε)^{3/2}`,  `η_ohm = j · d_gap / σ_eff`

**Concentration.** Adhering bubbles obstruct transport of OH⁻ to and from the surface and, at high
Θ, the electrode approaches a mass-transfer limit.

**(5)**  `η_conc = (RT / nF) · ln[1 / (1 − j/j_lim(Θ))]`

Equations (2)–(5) are why Θ is the closure that matters, and why deriving it is worth a study.

## 2. What the corpus establishes

**2.1 The closure in use is empirical and fitted far below where it is applied.**
E21 (Vogt & Balzer 2005) gives Θ = 0.023 (j/[A m⁻²])^0.3, anchored on a value of
(j)_Θ→1 ≈ 3 × 10⁵ A m⁻² the authors state "can roughly be estimated", fitting compiled data "more
or less satisfactorily". E20 (Eigeldinger & Vogt 2000) adds the flow correction
Θ = Θ₀/[1 + (C₄v)²]², C₄ = 8 s m⁻¹, **validated over j = 21–104 A m⁻²** and v = 0.02–0.25 m s⁻¹.

**2.2 It is applied ~60× outside that range, and it dominates the answer.**
E04 (Jacobsen 2025) applies coverage closures at **600 mA cm⁻² = 6000 A m⁻²**, reports coverage has
the **strongest effect** of the closures studied, that inter-model spread is greatest there, and
that the effect "rapidly increases with current density". The same authors state the available
models "are not tuned for porous electrodes and/or bubbles."

**2.3 Wettability is largely absent from the models despite entering every departure relation.**
**19 of 26 corpus papers (73%)** treat wettability as `absent` or `assumed-constant`. Among the
eight alkaline CFD papers, seven are `absent` or `assumed-constant`; the sole exception (E08)
sweeps θ = 90°→140° and runs in COMSOL.

**2.4 A circularity weakens the apparent validation status of much of the corpus.**
E21's correlation is fitted to compiled sources whose table **includes Riegel**; E05, E07 and E08
each apply a Vogt-type closure **and** validate against Riegel gas-fraction data. Closure and
anchor share an experimental origin. No corpus paper remarks on it.

**2.5 Open-source alkaline CFD exists but is not bubble-resolved.**
E03 uses stock `reactingMultiphaseEulerFoam`; E04 develops `alkaWEFoam` (mixture-based, availability
unstated); E25 (openFuelCell2, GPLv3) **has no alkaline model** — listed as future work.

## 3. The claim T12 makes

> **A bubble-coverage closure whose wettability dependence is derived from interface-resolved
> simulation with a potential-aware molecular contact angle, rather than fitted to legacy
> low-current-density data, changes the predicted cell polarisation of an alkaline electrolyser at
> industrial current density by an amount that exceeds the spread between existing empirical
> closures — and it does so only within a bounded region of (j, v, θ) which this work maps.**

### Three falsifiable predictions

**P1.** Contact angle computed under electrode polarisation differs measurably from its
zero-potential value, and the difference grows with |ΔΨ|.
*Falsified if* θ(ΔΨ) is flat within the block-averaged uncertainty across the accessible window.

**P2.** Coverage measured from a resolved interface departs from Θ = 0.023 j^0.3 by more than the
inter-model spread E04 reports, with the departure increasing with j.
*Falsified if* the resolved coverage tracks the Vogt form within that spread across the campaign.

**P3.** There exists a boundary in (j, v) beyond which departure radius is insensitive to θ because
solutal Marangoni forces dominate capillary forces — so a θ-dependent closure has a finite validity
domain.
*Falsified if* the capillary:Marangoni ratio stays ≫ 1 or ≪ 1 across the whole envelope, i.e. no
boundary exists within it.

**Note P3 is written to be losable.** If Marangoni dominates everywhere in the industrial envelope,
that is a publishable negative result which redirects the field away from wettability-based closures
— and the corpus's own trend (E26 naming wettability engineering a primary management strategy)
makes that outcome interesting rather than embarrassing.

## 4. Novelty scoping

Governed entirely by `prior_art_delta.md`. In brief: MD→continuum coupling for electrolytic bubbles
is **precedented** (Zhang et al., *Soft Matter* 2024); measured coverage at industrial current
density **exists** (Kitajima 2024, Hammons 2024, Rox 2022); the θ→Fritz→coverage chain is
**precedented analytically in COMSOL** (E08). What is not precedented is a *derived, open-source,
regime-bounded* closure propagated to cell polarisation. Every gap sentence is scoped
*"within this corpus"*.

## 5. Validation anchors

| Anchor | Role | Status |
|---|---|---|
| Kitajima 2024, *Electrochim. Acta* **502** 144772 — EIS-separated bubble resistance on Ni at 1–2 A cm⁻² | **primary**, measured coverage | to retrieve |
| Hammons 2024, *Nano Lett.* `10.1021/acs.nanolett.4c03657` — GISAXS + optical coverage at high j | **primary**, measured coverage | to retrieve |
| **Rox 2022, arXiv:2209.11550 — porous Ni, j = 100–2000 A m⁻², coverage + flow** | **secondary, porous arm**; only open-access set located | ✅ retrieved, `50_validation/anchors/A1` |
| E20 Vogt — measured coverage, 21–104 A m⁻² | low-j end; **validation target, not fitting source** | in corpus |
| E04 Jacobsen — Ni-foam zero-gap polarisation, 30 wt% KOH, 91 °C | cell-scale polarisation | in corpus |
| Riegel (via E01/E05–E08) — gas-fraction profiles | **legacy comparability ONLY** | in corpus |

**Riegel's demotion is deliberate.** Cross-sectional gas fraction is constrained by Faraday's law,
so agreement confirms the mass source rather than the wall-coverage closure. Both pre-execution
auditors made this point independently. It is reported for commensurability with the five corpus
papers that use it, with that caveat stated in the figure caption.

## 6. Known threats to the claim, recorded now

1. **Marangoni dominance** may shrink the θ-controlled region to irrelevance (mitigated: P3 and the
   applicability map are designed to find that out, and it is publishable either way).
2. **Nanoscale θ is not macroscopic θ** — line tension makes it size-dependent; mandatory
   multi-size extrapolation (§4.1 of the theory document).
3. **Classical OH⁻ cannot carry Grotthuss transport**, so MD transport properties for the hydroxide
   ion are structurally limited. Stated as a limitation, never hidden.
4. **Measurand mismatch** between adhering-bubble Θ and projected-area A_cov (~4–6× at equal j,
   anchor A1). Both will be extracted from the simulations and reported separately.
5. **Axisymmetric VOF** cannot represent lateral bubble motion or coalescence; ≤3 coarse 3D
   confirmation cases bound this (measured justification in `01_env/benchmark.md`).
