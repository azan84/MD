# A wettability-dependent bubble-coverage closure for open-source alkaline water electrolyser CFD, derived from potential-aware molecular dynamics and interface-resolved simulation

Authors: [TO BE COMPLETED]
Affiliations: [TO BE COMPLETED]
Corresponding author: [TO BE COMPLETED]

**Target journal:** International Journal of Hydrogen Energy (primary) · Chemical Engineering Science (fallback) · Chemical Engineering Journal (stretch). See `journal_note.md`.

**Draft status:** Sections 1–3 (Introduction, Theory, Methods) are drafted. Section 4 (Results) is a
structural placeholder — **the simulations are still running and no results exist yet.** Every
placeholder is marked `[PENDING]`. No number appears in this manuscript that is not traceable to a
file under `results/` or to a corpus extraction record.

---

## Abstract

`[PENDING — to be written once results exist. Structure fixed now so it cannot be retrofitted:
(i) coverage closures used in alkaline water electrolyser CFD are empirical correlations fitted at
low current density; (ii) we derive the wettability dependence of coverage from constant-potential
MD and interface-resolved VOF; (iii) quantified effect on cell polarisation vs the legacy closure;
(iv) validity envelope.]`

**Keywords:** alkaline water electrolysis; bubble coverage; wettability; contact angle; constant-potential molecular dynamics; volume of fluid; OpenFOAM; multiscale modelling

---

## 1. Introduction

### 1.1 Bubble coverage is the dominant closure in alkaline electrolyser models

Alkaline water electrolysis (AWE) remains the most mature technology for large-scale hydrogen
production, and its efficiency at industrially relevant current density is limited in large part by
the gas bubbles it generates. Hydrogen evolves at the cathode and oxygen at the anode as discrete
bubbles that nucleate, grow, adhere and eventually detach. While attached, a bubble blanks off
catalytically active area and displaces conductive electrolyte. The blanked fraction — the bubble
coverage Θ — degrades performance through three distinct routes: it reduces the active area
available for charge transfer, it lowers the effective conductivity of the electrolyte, and it
obstructs species transport to and from the surface.

The activation penalty is the most direct. If a fraction Θ of the electrode is screened, the same
total current must pass through the remaining fraction, so the local current density rises to
j/(1 − Θ). In the Tafel limit this costs

  Δη_act = (RT / α n F) · ln[1 / (1 − Θ)]                                          (1)

At α = 0.5, n = 1 and T = 353 K, the prefactor RT/(αnF) is 60.84 mV, so a coverage of Θ = 0.2 costs
13.6 mV while Θ = 0.8 costs 97.9 mV. The penalty is strongly non-linear, which is why an error in Θ
matters disproportionately at high current density.

**Kinetic convention.** Equation (1) carries n explicitly. This work assumes a Volmer-limited
cathodic reaction with a one-electron rate-determining step, α_app = αn = 0.5, implying a Tafel
slope of 140.1 mV dec⁻¹ at 353 K. This is stated because the choice matters: were the Heyrovsky
step rate-determining (α_app ≈ 1.5, 46.7 mV dec⁻¹), the same coverage would cost only 32.7 mV. The
headline quantity of this study depends on the assumed elementary step by a factor of three, and
both values are reported in Section 4.

### 1.2 The closure in use was fitted far below where it is applied

Cell-scale AWE models close Θ with empirical correlations, overwhelmingly of the form introduced by
Vogt and co-workers. Vogt and Balzer [1] give

  Θ = (j / 3×10⁵ A m⁻²)^0.3 = 0.023 (j / [A m⁻²])^0.3                              (2)

for stagnant electrolyte, and Eigeldinger and Vogt [2] supply the flow correction

  Θ = Θ₀ / [1 + (C₄ v)²]²,  C₄ = 8 s m⁻¹                                           (3)

Two features of these correlations are material and are rarely carried forward by the models that
use them. First, the scaling constant in Eq. (2) rests on a value of the current density at which
coverage would reach unity, (j)_Θ→1 ≈ 3×10⁵ A m⁻², which the authors state "can roughly be
estimated"; the correlation is described as fitting the compiled data "more or less
satisfactorily". Second, the flow correction of Eq. (3) was validated over j = 21–104 A m⁻² and
v = 0.02–0.25 m s⁻¹.

Contemporary open-source AWE simulations apply these correlations at current densities two orders of
magnitude above that validated range. Jacobsen et al. [3], developing a mixture-based OpenFOAM
solver for zero-gap AWE cells, run at 600 mA cm⁻² (6000 A m⁻²) and report that of all the two-phase
closures they examine — bubble coverage, interfacial mass transfer, bubble dispersion and hindrance
— **bubble coverage has the strongest effect on predicted cell performance**, that the spread
between coverage sub-models is largest at that current density, and that the effect "rapidly
increases with current density". The same authors note that the available closure models "are not
tuned for porous electrodes and/or bubbles".

So the closure that dominates the answer is an empirical correlation applied roughly 60× beyond the
range over which its flow dependence was validated, whose absolute scaling rests on a rough
estimate, and which its own users describe as untuned for the electrodes they are modelling.

### 1.3 Wettability is largely absent from these models, despite entering every departure relation

A structured analysis of a 26-paper corpus of multiscale electrolysis modelling literature
(corpus hash `9dd4b795a80ec687`; see Data Availability) found that **19 of 26 papers treat
wettability as absent or as a fixed constant**. Restricting to the eight alkaline CFD papers in that
corpus, seven treat it as absent or constant. The single exception, Li et al. [4], sweeps contact
angle from 90° to 140° and reports a measurable change in current density at fixed cell voltage —
but does so in commercial software, and constructs coverage analytically by combining a Fritz
departure-diameter relation with Faraday-law bubble counting rather than resolving it.

This is a curious gap. Contact angle enters every departure-diameter relation in use, and the
experimental community treats wettability engineering — aerophobic and superaerophobic electrode
design — as a primary bubble-management strategy [5]. Yet the closures that carry bubble effects
into cell-scale models are functions of current density alone.

### 1.4 What is and is not new here

Coupling molecular simulation to continuum descriptions of electrolytic bubbles is **not** new.
Zhang et al. [6] combine molecular dynamics with continuum fluid dynamics for electrolytic gas
bubbles, obtaining consistent solutal Marangoni forces of order 0.01 nN from both descriptions. That
work addresses lateral bubble motion and self-pinning; it derives no coverage closure and addresses
no electrode- or cell-scale model.

Direct measurement of bubble coverage at industrially relevant current density is **not** absent
either. Kitajima et al. [7] separate reaction and bubble-coating resistance by impedance
spectroscopy on nickel at 1–2 A cm⁻²; Hammons et al. [8] resolve nanobubble size and surface
coverage with synchronised small-angle X-ray scattering and optical microscopy at high current
density; Rox et al. [9] report coverage on porous expanded-nickel electrodes over
j = 100–2000 A m⁻². The gap is therefore not in the measurements. It is that **no open-source
continuum coverage closure has been re-derived from resolved interface simulation and validated
against modern coverage data, and no cell-scale model propagates a wettability-dependent closure to
a polarisation prediction.**

Accordingly, this work claims the following and nothing broader:

1. A coverage closure whose **wettability dependence** is derived from interface-resolved simulation
   with a contact angle computed under electrode polarisation, rather than assumed or fitted to
   legacy low-current data.
2. A quantitative bound on the region of (j, v, θ) over which that closure is valid, obtained by
   comparing capillary and solutal-Marangoni contributions to the departure force balance.
3. The consequence at cell scale: the difference in predicted polarisation between the legacy
   correlation and the derived closure, in a fully open-source stack.
4. A quantitative account of why optically measured projected coverage and electrochemically
   relevant adhering-bubble coverage differ by several fold at the same current density.

**The word "wettability dependence" in claim 1 is load-bearing.** A single-bubble simulation cannot
derive coverage outright: coverage is an ensemble property that also requires the density of active
nucleation sites, their activation statistics, cycle frequency and coalescence. This work derives
the wettability-dependent factors and treats the nucleation-site density as a declared external
input (Section 3.5). Claiming to derive coverage itself would not be defensible.

### 1.5 Structure

Section 2 states the governing equations at each scale and the coupling contract between them.
Section 3 gives the numerical methods, including the verification cases that gate production.
Section 4 reports results `[PENDING]`. Section 5 discusses limitations, of which several are
structural rather than incidental.

---

## 2. Theory

Symbols are defined in the Nomenclature. Equation numbers follow `03_theory/governing_equations.md`
in the accompanying repository so that every equation in this manuscript is traceable to an
implemented form.

### 2.1 Loss decomposition

The cell voltage decomposes as

  U_cell = U_rev + η_act,a + |η_act,c| + η_ohm + η_conc                             (4)

with the coverage-modified Butler–Volmer relation at the electrode

  j = (1 − Θ) j₀ [ exp(α_a n F η_act / RT) − exp(−α_c n F η_act / RT) ]             (5)

Here j is the **geometric** current density, j₀ is referenced to the corresponding clean exposed
area, and for porous electrodes the roughness (ECSA) factor is carried explicitly rather than
absorbed into j₀. This work models the cathode; the anode is not modelled, so a single Θ suffices
and no claim is made that one coverage describes both electrodes.

The ohmic contribution follows a Bruggeman-corrected effective conductivity,

  σ_eff = σ₀ (1 − ε_g)^{3/2},  η_ohm from ∇·(σ_eff ∇φ) = 0                          (6)

The exponent 3/2 is the standard baseline for dispersed gas in a continuous conducting phase and is
retained for comparability with the corpus, but it is not validated for a wall-attached bubble layer
or for porous nickel; it is therefore carried as a sensitivity parameter.

Two distinct concentration effects exist and are not summed without justification: the OH⁻
mass-transfer limitation,

  η_conc = (RT / nF) ln[ 1 / (1 − j / j_lim(Θ)) ]                                   (7)

and the Nernstian shift arising from local dissolved-hydrogen supersaturation beneath adhering
bubbles,

  ΔE_rev = (RT / 2F) ln( c_H₂,surf / c_H₂,sat )                                     (7a)

which can reach several tens of millivolts at high current density. Section 4 states which is
reported.

**Avoiding double counting.** Bubble gas enters the model in two physically distinct populations.
Adhering gas at the electrode contributes to Θ and acts only on active area, Eqs. (1) and (5).
Dispersed gas in the bulk contributes to ε_g and acts only on conductivity, Eq. (6). A bubble that
departs leaves Θ and joins ε_g. The implementation conserves that transfer and the conservation is
asserted in the automated checks (Section 3.7), because counting the same gas in both places is the
most plausible way for a model of this type to be quietly wrong.

### 2.2 Departure force balance

Departure is not imposed. It is detected in the resolved simulation when the net force on the bubble
changes sign,

  F_buoy + F_cap + F_drag + F_lift + F_Mar + F_el = 0                               (8)

with the capillary retention term

  F_cap = −π R_base γ_lv sin θ_c · f(θ_A, θ_R)                                      (9)

and the Marangoni term

  F_Mar = ∮_S ∇_s γ_lv dS,  ∇_s γ_lv = (∂γ_lv/∂T) ∇_s T + (∂γ_lv/∂c) ∇_s c          (10)

Equation (10) is identically zero unless surface tension is made an explicit function of
composition. The constitutive law used is

  γ_lv(c_H₂, c_KOH, T) = γ₀(c_KOH, T) + (∂γ/∂c_H₂)(c_H₂ − c_sat)                    (10a)

**The legacy Fritz relation is implemented as a baseline for comparison only**, not as the
mechanism. Fritz is a quasi-static balance of buoyancy against capillarity for an isolated bubble in
a stagnant pool, and is not valid under forced convection at high gas-generation rate. Its role in
this work is to appear in a figure showing where it departs from the resolved result.

### 2.3 Regime bound

The competition between capillary retention and Marangoni forcing is characterised by

  Λ = |F_cap| / |F_Mar|                                                             (11)

Order-of-magnitude estimates for a 50 µm bubble give F_cap ≈ 3.9 µN, against F_Mar ≈ 0.05 nN if
driven by dissolved-hydrogen gradients and ≈ 12.5 nN if driven by electrolyte concentration
gradients, i.e. Λ of order 10²–10⁵. The expectation, pre-registered before the campaign, is
therefore that Λ ≫ 1 throughout the industrial envelope and that departure is
capillary/wettability-controlled. Section 4 tests this rather than assuming it.

This expectation appears to conflict with a body of work reporting that the solutal Marangoni effect
governs electrolytic bubble dynamics. It does not: that work is predominantly conducted on
**microelectrodes**, with bubbles of tens of micrometres and below and very high local
supersaturation, where capillary retention is correspondingly small. The present study addresses
macroscopic bubbles on planar and porous electrodes at industrial current density. Locating the
crossover between these regimes is one of the outcomes reported here.

### 2.4 Coupling contract

Coupling is strictly one-way: MD → bridge → VOF → regression → cell. No two-way feedback across
scales is claimed. The quantities that cross, their validity ranges, and the uncertainty carried
with each are tabulated in Table 1.

**Table 1.** Cross-scale coupling contract. `[Full version in the repository as
`03_theory/coupling_contract.md`.]`

| From | To | Quantity | Validity range | Uncertainty carried |
|---|---|---|---|---|
| MD | bridge | contact angle θ(ΔΨ, c, T) | ΔΨ ≤ 1.0 V; 20–30 wt%; 298–353 K | replica spread |
| MD | VOF | surface tension γ_lv(c, T) | as above | Kirkwood–Buff block SE |
| MD | VOF/cell | diffusivity D_H₂(c, T) | as above | finite-size-corrected fit SE |
| bridge | VOF | wall contact-angle BC | per case | campaign repeated at θ ± σ_θ at three corners |
| Cantera | VOF/cell | j₀(T, c) | tabulated, clamped at edges | mechanism uncertainty stated |
| VOF | regression | Θ_adh and A_cov,proj | j 10²–10⁴ A m⁻²; v 0–0.2 m s⁻¹; θ 30–150° | time-averaging SE |
| regression | cell | closure Θ(j, v, θ) | the above box ∩ Λ > 1 | 95% CI on fitted parameters |

The closure implementation **raises an error rather than extrapolating** outside its stated validity
box. This is deliberate: the study exists because a closure was extrapolated far beyond its
validated range, and reproducing that error with a new closure would be self-defeating.

Quantities that deliberately do **not** cross scales are also worth stating. Electrolyte viscosity
is taken from experiment rather than from MD, because the classical hydroxide model used here cannot
represent structural (Grotthuss) transport and its transport coefficients are correspondingly
limited; MD viscosity is used only as a force-field validation check. Double-layer structure informs
interpretation but is not a continuum input.

---

## 3. Methods

All simulations use open-source software on a single Linux workstation (16 physical cores, 23 GB
RAM, no GPU). Versions, build configurations and hardware benchmarks are recorded in
`01_env/versions.json` and `01_env/benchmark.md`.

### 3.1 Molecular dynamics

**Code and electrostatics.** LAMMPS (22 Jul 2025 stable) built from source with the ELECTRODE
package, MPI and FFTW3. Long-range electrostatics use `pppm/electrode` with slab correction for the
2D-periodic geometry.

**Constant-potential electrodes.** Electrode atoms carry Gaussian charges solved each timestep so
that every electrode atom sits at its imposed potential, via `fix electrode/conp`. Writing the
electrode charge vector **q** and the elastance matrix **A**,

  A q = b(Ψ, {r_electrolyte}),  Σ_i q_i = 0,  ΔΨ = Ψ_anode − Ψ_cathode              (12)

The implementation was verified against the reference case distributed with the ELECTRODE package,
reproducing the published induced electrode charges to all printed digits across the full potential
ramp. In the production geometry the constraint Σ q_i = 0 is satisfied exactly at every timestep,
with induced charges equal and opposite on the two slabs and growing as the double layer forms.

**System.** Ni(111) slabs of five layers (a = 3.524 Å) bound an aqueous KOH film. Water is SPC/E
with SHAKE constraints. Potassium uses Joung–Cheatham parameters optimised for SPC/E
`[UNVERIFIED — citation to be confirmed]`. Hydroxide is represented as a **single Lennard-Jones site
carrying unit negative charge, with LJ parameters taken identical to SPC/E oxygen**, following
established practice for hydroxide in SPC/E-based simulations `[UNVERIFIED — citation to be
confirmed]`. This model cannot carry Grotthuss transport; the consequences are stated in Section 5
and the model is admitted only because it must first pass the bulk validation gate of Section 3.2.

**Ensemble and initialisation.** Production runs are NVT with a Nosé–Hoover thermostat. Lattice
initial configurations are relaxed by a displacement-capped `nve/limit` push under a strong Langevin
thermostat rather than by energy minimisation, because SHAKE constraints are ignored during
minimisation in LAMMPS and a minimised configuration is therefore not consistent with the
constrained dynamics that follow.

**Contact-angle protocol.** A **cylindrical (quasi-2D) hydrogen bubble**, periodic along its
cylinder axis, rests on the cathode. The interface is located as the isochore of the time-averaged
density field at ρ = ½(ρ_l + ρ_g) and the angle is measured **through the liquid**, matching the
convention used by the continuum wall boundary condition, Eq. (16).

**No line-tension extrapolation is performed, and none is possible in this geometry.** A periodic
cylindrical cap has straight contact lines with zero in-plane geodesic curvature, so the modified
Young relation cos θ(R) = cos θ_∞ − τ/(γ_lv R), which is derived for a circular contact line, does
not apply. Cylindrical geometry is used precisely because it *suppresses* the line-tension
contribution. Size dependence is instead addressed by **box-size convergence**: the angle is
measured at lateral box widths of 8, 12 and 16 nm (19k, 30k and 41k atoms respectively) and required
to be invariant within replica scatter. This is a convergence check on periodic-image and
opposing-wall artefacts, not a physical extrapolation.

**Statistics.** Each state point is run with at least three independent seeds. Reported uncertainty
is the **spread across replicas**, because block averages taken from a single trajectory are not
independent realisations.

**Potential referencing.** The control variable is the electrode potential relative to the potential
of zero charge, determined in a separate calculation. The raw inter-slab potential difference is a
cell voltage, not an electrode potential, and is not used as the abscissa for the reported
electrowetting response.

**Expected response.** The Lippmann relation predicts

  cos θ(ΔΨ) = cos θ_pzc + C_dl (ΔΨ − Ψ_pzc)² / (2 γ_lv)                             (13)

For C_dl in the range 0.1–0.3 F m⁻² and a 0.5 V excursion this corresponds to a shift of roughly
10°–31°. The quadratic form saturates unphysically at larger excursions; contact-angle saturation is
a documented electrowetting phenomenon, and its observation would be a result rather than a failure.

### 3.2 Force-field validation gate

The molecular model is validated against bulk KOH(aq) properties **before** any interface
calculation is performed. Systems of 20 and 30 wt% KOH are equilibrated at 298 and 333 K with three
seeds each, and density, water and potassium self-diffusivities are compared with experiment.
Diffusivities are obtained from the Einstein relation over the linear region of the mean-squared
displacement with a finite-size correction.

Pass criteria were fixed before any result was inspected: density within 3%, D(H₂O) within 30%, and
D(K⁺) within 40%. **The hydroxide diffusivity is reported but not gated**, because a single-site
classical hydroxide cannot reproduce structural diffusion and is expected to be too slow; treating
that as a force-field failure would be a category error, and treating it as acceptable without
saying so would be worse.

`[PENDING — gate outcome. If the density criterion is not met, the hydroxide representation is
replaced, most plausibly by a two-site model or by re-tuning the ion Lennard-Jones parameters
against density, and the contact-angle campaign is not run until the revised model passes.]`

### 3.3 Interface-resolved two-phase simulation

**Solver.** OpenFOAM v2406, geometric VOF (`interIsoFoam`), with custom boundary conditions compiled
against the standard library.

  ∂α/∂t + ∇·(α u) + ∇·(α(1−α) u_r) = (ṁ/ρ_l) δ_S                                    (14)
  ∂(ρu)/∂t + ∇·(ρ u u) = −∇p + ∇·[μ(∇u + ∇uᵀ)] + ρg + γ_lv κ ∇α                     (15)

**Wall wettability** enters through

  n̂_wall · (∇α/|∇α|) = cos θ                                                        (16)

with θ supplied by the molecular calculation of Section 3.1. **Equation (16) is the single point at
which the molecular result enters the continuum model.**

**Bubble growth** is driven by dissolved-hydrogen transport with a Henry-law interfacial condition,
with the Faradaic wall flux applied over the exposed area in the current-conserving form

  N_H₂,exposed = j / [2F (1 − Θ)],   ∫_exposed N_H₂ dA = j A_geom / (2F)             (17)

The normalisation matters. Applying j/(2F) over the uncovered area instead would reduce total gas
generation to (1 − Θ)·j/(2F) and thus violate the imposed galvanostatic current, artificially
suppressing bubble growth as coverage rises. The same convention is used in the gas source term, the
electrode boundary condition and the closure.

**Geometry.** The parametric campaign is **axisymmetric**, on a wedge domain sized to five expected
departure radii, with mesh spacing chosen to hold approximately 25 cells per expected departure
radius at each current density (5.0 µm at 100 A m⁻² down to 1.5 µm at 10⁴ A m⁻²). This is a
consequence of measured throughput on the available hardware: a three-dimensional parametric sweep
at the resolution required to resolve a contact line would need of order 1.6×10⁷ cells per case
against a practical memory ceiling of about 5×10⁶ cells, and is not feasible. Two contrasting
three-dimensional cases are run at reduced resolution to bound the effect of the axisymmetric
restriction.

**Initialisation.** Bubbles are seeded at 0.85 of the expected departure radius and the preceding
quasi-static growth is treated analytically. The departure radius itself remains an **output** of the
force balance, Eq. (8), not an input: the seed is placed well below departure so that the detachment
event is predicted rather than prescribed. This is necessary because growing a bubble from
nucleation at 100 A m⁻² requires seconds of physical time and of order 10⁷ timesteps.

### 3.4 Verification before production

Two verification cases gate the campaign and no production case runs until both pass.

1. **Diffusion-driven growth** is compared against the Epstein–Plesset/Scriven similarity solution
   R(t) = 2β√(Dt) for a bubble in a uniformly supersaturated quiescent liquid.
2. **Variable surface tension and the tangential Marangoni stress** are compared against an analytic
   thermocapillary benchmark. This case exists because a wrongly scaled or wrongly signed ∇_s γ
   produces a plausible-looking but meaningless regime map, and because with constant surface
   tension the Marangoni force is identically zero and the regime bound of Eq. (11) would be
   untestable by construction.

Mesh independence is established by refinement at three levels with Richardson extrapolation and a
reported grid convergence index.

### 3.5 Construction of the coverage closure

Coverage is **constructed**, not regressed directly from a single-bubble calculation:

  Θ = N_site · A_footprint(θ, R_det) · f_residence(j, v, θ) · f_overlap             (18)

The resolved simulations supply the footprint area A_footprint = π R_det² sin²θ, the departure radius
R_det(θ, j, v) from Eq. (8), and the residence time per cycle measured over several statistically
stationary departure events. **The active nucleation-site density N_site is an explicit external
input**, taken from experiment and stated with its source and uncertainty. It is dominated by
sub-surface cavity geometry and surface finish, which molecular dynamics of a flat single-crystal
slab cannot supply.

The functional form of the closure is specified before fitting so that it cannot be reverse-
engineered from the data:

  Θ(j, v, θ) = C (j/j_ref)^a · g(θ) · h(v),  g(θ) = [(1 − cos θ)/(1 − cos θ_ref)]^b (19)

with h(v) retained in the form of Eq. (3) so that the flow dependence is directly comparable with
the legacy correlation. Twenty per cent of the campaign is held out as a test set, and fitted
parameters are reported with 95% confidence intervals and held-out RMSE.

**Two coverage measurands are extracted, not one.** The adhering-bubble surface coverage Θ_adh, which
is the quantity that screens catalytic area, and a synthetic projected coverage A_cov,proj computed
by rendering the resolved interface as it would appear to a top-view optical measurement. These
differ by the factor sin²θ for a spherical cap even before detached bubbles in the field of view are
considered, and reporting both is what allows the apparent disagreement between optical and
electrochemical coverage measurements to be addressed quantitatively rather than asserted away.

### 3.6 Cell-scale model

The closure is implemented in an Euler–Euler two-fluid model in OpenFOAM
(`reactingMultiphaseEulerFoam`), with interphase momentum transfer closed by named drag, lift,
wall-lubrication and turbulent-dispersion models, charge transport by Eq. (6), and the electrode
boundary condition carrying Θ into Eq. (5). Exchange current density is supplied by a Cantera
surface-kinetics evaluation, pre-tabulated as a function of temperature and electrolyte
concentration and interpolated at run time; runtime linkage of Cantera into the CFD solver was
deliberately avoided as a schedule risk with no scientific benefit for an algebraic evaluation.

The reported quantity is the difference in predicted polarisation between the legacy correlation and
the derived closure,

  ΔV_cell(j) = U_cell[Θ_Vogt] − U_cell[Θ_this work]                                 (20)

evaluated only inside the closure's stated validity box.

### 3.7 Automated quality control

Every run batch is checked automatically for: mass and charge conservation residuals; Courant number
and residual convergence; boundedness of the phase fraction and of Θ; monotonicity of the
polarisation curve in j; molecular-dynamics energy drift; the presence of replica-based
uncertainties on every reported mean; and the adhering/dispersed gas transfer of Section 2.1. A check
that fails twice freezes that branch of the campaign pending review rather than being retried
indefinitely.

### 3.8 Validation anchors

`[PENDING — comparisons to be reported in Section 4.]` The anchors are fixed in advance:

- **Primary, coverage:** impedance-separated bubble-coating resistance on nickel at 1–2 A cm⁻² [7],
  and coverage resolved by scattering and optical microscopy at high current density [8].
- **Secondary, porous electrodes:** measured coverage on expanded-nickel cathodes over
  j = 100–2000 A m⁻² with and without forced flow [9]. This dataset has a stated detection floor of
  about 20% coverage, timing uncertainty of order 50%, and includes detached rising bubbles in the
  field of view; those limitations are carried into the comparison rather than ignored.
- **Cell scale:** measured polarisation of a zero-gap nickel-foam cell in 30 wt% KOH at ~91 °C [3].
- **Legacy comparability only:** local gas-fraction profiles widely used in the AWE CFD literature
  [10,11]. These are reported for commensurability with previous work, but a match to a
  cross-sectional gas fraction principally confirms that the mass source obeys Faraday's law and is
  **not** a validation of a wall-coverage closure; the caption states this.

---

## 4. Results

`[PENDING — the campaign is in progress. This section is structured in advance so that the analysis
plan is fixed before the data exist.]`

4.1 Force-field validation `[PENDING]`
4.2 Contact angle under electrode polarisation, and box convergence `[PENDING]`
4.3 Verification cases `[PENDING]`
4.4 Departure radius and the force balance `[PENDING]`
4.5 The regime bound Λ(j, v) `[PENDING]`
4.6 The derived closure and its validity box `[PENDING]`
4.7 Adhering versus projected coverage `[PENDING]`
4.8 Cell polarisation: legacy versus derived closure `[PENDING]`

---

## 5. Limitations

Several limitations here are structural rather than incidental and are stated in full.

**The molecular model is chemically inert.** SPC/E water with classical ions on a clean Ni(111)
surface cannot represent nickel oxidation, hydroxylation, specific adsorption or bond formation.
`fix electrode/conp` makes the metal charge responsive; it does not make the interface chemically
reactive. The reported angle is therefore the **electrostatic, double-layer contribution** to
potential-dependent wettability on an idealised surface, not a prediction of the wettability of an
operating electrode.

**Hydroxide transport is structurally limited.** A single-site classical OH⁻ cannot carry Grotthuss
transport. Its diffusivity is reported but not used as a continuum input, and electrolyte transport
properties are taken from experiment.

**Molecular dynamics supplies an equilibrium angle, not hysteresis.** The continuum model requires
advancing and receding angles under flow; these are taken from measured data with the molecular
calculation informing the equilibrium centre. Contact-angle hysteresis on real electrodes is
dominated by roughness and chemical heterogeneity that a flat single crystal does not contain.

**Nucleation-site density is an input, not a result.** Consequently the closure's dependence on
wettability and flow is derived, while its absolute level inherits the uncertainty of the declared
N_site.

**The parametric campaign is axisymmetric.** Lateral bubble motion, sliding and coalescence are not
represented, and axisymmetry suppresses shear-induced asymmetric contact-line depinning, which is
expected to reduce departure radius in cross-flow. Two contrasting three-dimensional cases bound
this effect; they do not eliminate it.

**The Bruggeman exponent is not validated for this system** and is carried as a sensitivity
parameter.

**The regime bound is computed for clean electrolyte** without surfactants, for a single bubble, and
is scoped accordingly.

---

## Nomenclature

`[Full symbol table with SI units — see `03_theory/governing_equations.md`.]`

---

## Data availability

All simulation inputs, analysis scripts, verification cases and the derived closure implementation
are available in the accompanying repository. The corpus analysis underlying Section 1.3 is
identified by hash `9dd4b795a80ec687`. `[Repository DOI to be minted on submission.]`

---

## References

`[Reference list is incomplete and is verified incrementally. Entries marked [verify] have not yet
been checked against the published record and must not be relied upon in this state.]`

[1] H. Vogt, R.J. Balzer, The bubble coverage of gas-evolving electrodes in stagnant electrolytes,
Electrochimica Acta (2005). https://doi.org/10.1016/j.electacta.2004.09.025

[2] J. Eigeldinger, H. Vogt, The bubble coverage of gas-evolving electrodes in a flowing
electrolyte, Electrochimica Acta 45 (2000) 4449–4456. *(No DOI is printed in the source; volume and
pages are given as printed.)*

[3] A.N. Jacobsen, E. Mahravan, M.V. Kragh-Schwarz, J. Catalano, P. Fooroghi, Multiphysics
simulations of alkaline water electrolyzer cells — a sensitivity study on the effect of two-phase
flow modeling, Electrochimica Acta (2025). https://doi.org/10.1016/j.electacta.2025.147148

[4] J. Li, H. Liang, M.A. Rehan, G. Li, Numerical simulation and analysis of a two-phase flow model
considering bubble coverage for alkaline electrolytic water, Applied Thermal Engineering 245 (2024)
122890. https://doi.org/10.1016/j.applthermaleng.2024.122890

[5] O. Moyo, H. Sun, J. Yang, X. Xu, Z. Shao, Gas bubble formation, effect on electrode performance,
and management in water electrolysis, Nano Energy (2026).
https://doi.org/10.1016/j.nanoen.2026.112024

[6] H. Zhang, Y. Ma, M. Huang, G. Mutschke, X. Zhang, Solutal Marangoni force controls lateral
motion of electrolytic gas bubbles, Soft Matter 20 (2024) 3097–3106.
https://doi.org/10.1039/D3SM01646C

[7] D. Kitajima, R. Misumi, Y. Kuroda, S. Mitsushima, Relationship between bubble generation
behavior and hydrogen evolution reaction performance at high current densities during alkaline water
electrolysis, Electrochimica Acta 502 (2024) 144772.
https://doi.org/10.1016/j.electacta.2024.144772

[8] J. Hammons et al., Nanobubble formation and coverage during high current density alkaline water
electrolysis, Nano Letters (2024). https://doi.org/10.1021/acs.nanolett.4c03657 *[author list to be
completed — verify]*

[9] H. Rox, A. Bashkatov, X. Yang, S. Loos, G. Mutschke, G. Gerbeth, K. Eckert, Bubble size
distribution and electrode coverage at porous nickel electrodes in a novel 3-electrode flow-through
cell, arXiv:2209.11550 (2022). *[check for subsequent journal version]*

[10] A. Zarghami, N.G. Deen, A.W. Vreman, CFD modeling of multiphase flow in an alkaline water
electrolyzer, Chemical Engineering Science (2020). https://doi.org/10.1016/j.ces.2020.115926

[11] R. Kanemoto, T. Araki, R. Misumi, S. Mitsushima, Numerical modeling of two-phase flow
considering multiple bubble sizes in an alkaline water electrolyzer, Chemical Engineering Science
304 (2025) 120986. https://doi.org/10.1016/j.ces.2024.120986

[12] L. Andersson, C. Zhang, Molecular dynamics simulations of metal-electrolyte interfaces under
potential control, Current Opinion in Electrochemistry (2023).
https://doi.org/10.1016/j.coelec.2023.101407

[13] S. Zhang, S. Hess, H. Marschall, U. Reimer, S. Beale, et al., openFuelCell2: a new
computational tool for fuel cells, electrolyzers, and other electrochemical devices and processes,
Computer Physics Communications 298 (2024) 109092. https://doi.org/10.1016/j.cpc.2024.109092

[14] Y. Han, M. Huang, K. Eckert, G. Mutschke, Numerical simulation of oversaturation-driven bubble
growth on solid surfaces with dynamic wetting, International Journal of Multiphase Flow (2025).
https://doi.org/10.1016/j.ijmultiphaseflow.2025.105343

[15] K.J. Vachaparambil, K.E. Einarsrud, Numerical simulation of continuum scale electrochemical
hydrogen bubble evolution, Applied Mathematical Modelling 98 (2021) 343–377.
https://doi.org/10.1016/j.apm.2021.05.007

[16] H.J.C. Berendsen, J.R. Grigera, T.P. Straatsma, The missing term in effective pair potentials,
Journal of Physical Chemistry 91 (1987) 6269–6271. *[verify]*

[17] I.S. Joung, T.E. Cheatham III, Determination of alkali and halide monovalent ion parameters for
use in explicitly solvated biomolecular simulations, Journal of Physical Chemistry B 112 (2008).
*[verify — page numbers to be confirmed]*

[18] Riegel et al., local gas-fraction measurements in an alkaline electrolyser (1997/1998), as
reported in refs [10] and [4]. *[primary reference to be obtained and verified before submission]*
