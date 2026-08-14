# GOVERNING EQUATIONS
Every equation numbered, every symbol in the nomenclature table with SI units, every equation tagged
with the solver that discretises it. **This file is the manuscripts' Methods section** — written to
publication standard once, then cited by number from the manuscripts and the coupling contract.

Solver tags: **[MD]** LAMMPS · **[VOF]** OpenFOAM `interIsoFoam` · **[CELL]** OpenFOAM
`reactingMultiphaseEulerFoam` · **[CT]** Cantera/Python · **[AN]** analytic / post-processing.

---

## 1. Nomenclature

| Symbol | Quantity | SI unit |
|---|---|---|
| A_cov | projected-area bubble coverage (Rox-type measurand) | – |
| Θ | adhering-bubble surface coverage (Vogt-type measurand) | – |
| a_el | electrochemically active area per volume | m⁻¹ |
| C_dl | double-layer capacitance | F m⁻² |
| c_i | molar concentration of species i | mol m⁻³ |
| c_H₂,sat | saturation concentration of dissolved H₂ | mol m⁻³ |
| D_i | self-diffusion coefficient of species i | m² s⁻¹ |
| d_gap | electrode gap | m |
| E | electric field | V m⁻¹ |
| F | Faraday constant, 96485.33 | C mol⁻¹ |
| g | gravitational acceleration, 9.81 | m s⁻² |
| j | superficial (geometric) current density | A m⁻² |
| j₀ | exchange current density | A m⁻² |
| j_lim | limiting current density | A m⁻² |
| He | Henry coefficient | – |
| n | number of electrons transferred | – |
| p | pressure | Pa |
| q_i | induced charge on electrode atom i | C |
| R | gas constant, 8.314 | J mol⁻¹ K⁻¹ |
| R_b | bubble radius | m |
| R_det | departure radius | m |
| S | supersaturation ratio c_H₂/c_H₂,sat | – |
| T | temperature | K |
| **u** | velocity | m s⁻¹ |
| U_cell | cell voltage | V |
| U_rev | reversible cell voltage | V |
| v | electrolyte superficial velocity | m s⁻¹ |
| α_a, α_c | anodic/cathodic transfer coefficients | – |
| α (VOF) | liquid volume fraction | – |
| β | growth constant in R = 2β√t | – |
| γ_lv | liquid–vapour interfacial tension | N m⁻¹ |
| ε | dispersed gas volume fraction | – |
| ε_LJ | Lennard-Jones well depth | J |
| η | overpotential | V |
| θ | contact angle (measured through the liquid) | rad or ° |
| θ_A, θ_R | advancing / receding contact angle | ° |
| θ_∞ | line-tension-extrapolated macroscopic contact angle | ° |
| κ | interface curvature | m⁻¹ |
| μ | dynamic viscosity | Pa s |
| ρ | density | kg m⁻³ |
| σ | electrolyte ionic conductivity | S m⁻¹ |
| σ_eff | gas-corrected effective conductivity | S m⁻¹ |
| τ | line tension | N |
| φ | electric potential in the electrolyte | V |
| ΔΨ | imposed electrode potential difference (MD) | V |

Subscripts: `l` liquid, `g` gas, `a` anode, `c` cathode, `s` surface, `∞` extrapolated/bulk.

---

## 2. Scale 1 — Molecular dynamics **[MD]**

### 2.1 Equations of motion
**(1)** `m_i d²r_i/dt² = −∇_i U({r}) + F_thermostat,i`

with Nosé–Hoover NVT and SHAKE constraints on the SPC/E geometry. The potential decomposes as

**(2)** `U = U_LJ + U_Coul + U_bond + U_angle`

**(3)** `U_LJ(r_ij) = 4 ε_LJ,ij [ (σ_LJ,ij/r_ij)¹² − (σ_LJ,ij/r_ij)⁶ ]`

**(4)** `U_Coul = (1/4πε₀) Σ_{i<j} q_i q_j / r_ij`, evaluated by `pppm/electrode` with slab correction.

### 2.2 Constant-potential electrodes — the physics that makes rev B "potential-aware"
Electrode atoms carry Gaussian charges that are **not fixed**; they are solved each timestep so that
every electrode atom sits at its imposed potential. Writing the electrode-atom charge vector **q**
and the elastance (capacitance-inverse) matrix **A**,

**(5)** `A q = b(Ψ, {r_electrolyte})`,  `A_ij = erf(η_G r_ij)/r_ij + self terms`

**(6)** `Σ_i q_i = 0` (charge neutrality, enforced as a constraint)

**(7)** `ΔΨ = Ψ_anode − Ψ_cathode` (imposed)

Equation (5) is solved by `fix electrode/conp` by direct matrix inversion (precomputed for rigid
electrodes) or CG. **This is the step absent from the rhodo benchmark and therefore the source of
the unmeasured 2–4× overhead in OI-1.**

The differential capacitance follows as

**(8)** `C_dl = ∂⟨Q⟩/∂(ΔΨ)`, `Q = Σ_{i ∈ anode} q_i`

### 2.3 Contact angle — protocol replaced at Audit 1

Cap fitted to the isochore of the time-averaged density field at ρ = ½(ρ_l + ρ_g), for a
**cylindrical (quasi-2D) H₂ bubble under KOH**, periodic along the cylinder axis, angle measured
**through the liquid** to match the OpenFOAM convention of eq. (24).

> **⚠️ THE 1/R LINE-TENSION EXTRAPOLATION PREVIOUSLY SPECIFIED HERE HAS BEEN REMOVED (A1.3).**
> A periodic cylindrical cap has **straight contact lines with zero in-plane curvature**, so the
> modified Young relation `cos θ(R) = cos θ_∞ − τ/(γ_lv R)` — derived for a *circular* contact line —
> does not apply. Cylindrical geometry is the standard way to **suppress** line tension, not to
> measure it. Fitting it would have manufactured a spurious size trend and, per the auditor, was
> the single result most likely to be a numerical artefact.
>
> A second, independent error was found in the same specification: the design box was 8a =
> **2.82 nm** laterally, so **none** of the intended R = 3, 5, 8 nm caps could physically fit.

**Replacement protocol.**

**(9)** *Box-size convergence* — θ measured at three lateral widths L ∈ {8, 12, 16} nm and required
to be invariant within replica scatter. This is a **convergence check**, not a physical
extrapolation, and it also converges out periodic-image and opposing-wall effects.

**(9a)** *Replica statistics* — ≥3 independent seeds per state point. Reported uncertainty is the
**replica spread**; block averages from a single trajectory are not independent realisations.

**(9b)** *Potential referencing* — the control variable is the electrode potential relative to the
**potential of zero charge**, determined in a separate run. The raw inter-slab ΔΨ is a cell voltage,
not an electrode potential, and is not used as the abscissa for P1.

**What MD delivers, stated honestly.** The *equilibrium* contact angle and its potential-induced
shift, for an idealised, chemically inert Ni surface. It does **not** deliver advancing/receding
angles or hysteresis — those are taken from measured data (corpus E15) with MD informing the
equilibrium centre. A non-reactive SPC/E + classical-ion + clean-Ni force field cannot represent Ni
oxidation, hydroxylation or specific adsorption; `fix electrode/conp` makes the metal *charge*
responsive, not the interface *chemically* reactive. See `coupling_contract.md` C1/C4 and
`LIMITATIONS.md`.

### 2.4 Interfacial tension, transport
**(10)** `γ_lv = ∫ [ p_N(z) − p_T(z) ] dz`  (Kirkwood–Buff)

**(11)** `D_i = lim_{t→∞} ⟨|r_i(t) − r_i(0)|²⟩ / 6t`, with the Yeh–Hummer finite-size correction
`D_∞ = D_PBC + 2.837297 k_B T / (6πμL)`

**(12)** `μ = (V/k_B T) ∫₀^∞ ⟨P_αβ(0) P_αβ(t)⟩ dt`  (Green–Kubo)

All means are block-averaged with the equilibration segment discarded and reported ± one standard
error.

---

## 3. Scale 1 → 2 bridge — departure radius

### 3.1 Legacy baseline only — Fritz **[AN]**
**(13)** `R_det,Fritz = 0.5 · 0.0208 θ √( γ_lv / (g (ρ_l − ρ_g)) )`, θ in degrees

**Fritz is implemented as the legacy comparison, not as the mechanism.** It is a quasi-static
buoyancy-versus-capillarity balance for an isolated bubble in a stagnant pool; both pre-execution
auditors ruled it invalid at industrial current density under forced convection. Its role is to
appear in a figure showing *where it fails*.

### 3.2 The actual criterion — resolved force balance **[VOF]**
Departure is detected in the resolved simulation when the net upward force changes sign:

**(14)** `F_buoy + F_cap + F_drag + F_lift + F_Mar + F_el = 0`

with

**(15)** `F_buoy = (4/3)π R_b³ (ρ_l − ρ_g) g`

**(16)** `F_cap = −π R_base γ_lv sin θ_c · f(θ_A, θ_R)`  — contact-line pinning, hysteresis-dependent

**(17)** `F_drag = ½ C_D ρ_l π R_b² |u_rel| u_rel`

**(18)** `F_Mar = ∮_S ∇_s γ_lv dS`,  with  `∇_s γ_lv = (∂γ_lv/∂T) ∇_s T + (∂γ_lv/∂c) ∇_s c`

Equation (18) is the **solutal Marangoni** term and the principal threat to a θ-only closure.

> ### ⚠️ REQUIRED CONSTITUTIVE LAW — added at Audit 1 (A1.5), design-fatal if omitted
> Equation (18) is **identically zero unless γ_lv is made an explicit function of composition.**
> The earlier specification wrote `∂γ_lv/∂c` but never supplied a law for it, so the VOF model
> would have run with constant surface tension, `F_Mar ≡ 0`, and **prediction P3 could never have
> been tested** — the campaign would have produced a null result by construction rather than by
> physics. This is the most consequential single finding of Audit 1.
>
> **(18a)** `γ_lv(c_H₂, c_KOH, T) = γ₀(c_KOH, T) + (∂γ/∂c_H₂)·(c_H₂ − c_sat)`
>
> Implementation requirements, all of which gate any P3 case:
> 1. `γ₀(c_KOH, T)` from measured KOH surface-tension data (electrolyte composition raises γ).
> 2. **`∂γ/∂c_H₂` must be supplied and justified** — either from literature for dissolved H₂ in
>    alkaline electrolyte, or computed by MD as an additional deliverable (Kirkwood–Buff, eq. 10,
>    at two dissolved-gas concentrations). **If neither is available, P3 is not testable and must be
>    withdrawn rather than reported as a null.**
> 3. The tangential-stress term must be verified against an analytic thermocapillary benchmark
>    before any production case, since a wrongly signed or scaled ∇_s γ silently produces a
>    plausible-looking but meaningless map.
> 4. `interIsoFoam` does not carry variable surface tension as standard — this requires a custom
>    `wmake` addition, which is why the Phase 0 wmake capability test was performed.
>
> **Logged as OI-7 and as a gate on the entire P3 branch.**

### 3.3 The applicability map — a primary deliverable **[AN]**
Define the capillary-to-Marangoni ratio

**(19)** `Λ = |F_cap| / |F_Mar|`

**Λ ≫ 1** → θ-controlled: a wettability-dependent closure is valid.
**Λ ≪ 1** → Marangoni-controlled: departure is θ-insensitive and the closure must not be applied.
The locus **Λ = 1** in (j, v) is the map's boundary and the test of prediction **P3**.

---

## 4. Scale 2 — Interface-resolved VOF **[VOF]**

### 4.1 Two-phase flow
**(20)** `∇·u = ṁ (1/ρ_g − 1/ρ_l) δ_S`  (volumetric expansion at the phase interface)

**(21)** `∂(ρu)/∂t + ∇·(ρ u u) = −∇p + ∇·[μ(∇u + ∇uᵀ)] + ρg + f_σ`

**(22)** `∂α/∂t + ∇·(α u) + ∇·(α(1−α) u_r) = (ṁ/ρ_l) δ_S`

with mixture properties `ρ = αρ_l + (1−α)ρ_g`, `μ = αμ_l + (1−α)μ_g`.

Surface tension by CSF with the isoAdvector geometric reconstruction:

**(23)** `f_σ = γ_lv κ ∇α`,  `κ = −∇·( ∇α / |∇α| )`

### 4.2 Wall wettability — the single point where MD enters the continuum model
**(24)** `n̂_wall · (∇α/|∇α|) = cos θ`

with θ = θ_∞(ΔΨ, c, T) from equation (9), and in the dynamic variant θ = θ_d(Ca, θ_A, θ_R) with
`Ca = μ_l U_cl / γ_lv`. **Equation (24) is the coupling.** It gets its own Methods subsection.

### 4.3 Bubble growth by dissolved-gas transfer
**(25)** `∂c/∂t + ∇·(u c) = ∇·(D ∇c) − ṁ/(M δ_S)`

**(26)** interfacial equilibrium: `c_S = He · p_g / (R T)`

**(27)** `ṁ = k_m ( c − c_S )` over the interface

**(28)** Faradaic wall flux — **current-conserving form**:

`N_H₂,exposed = j / (2F (1 − Θ))`  applied over the exposed (uncovered) area, so that the surface
integral recovers the imposed galvanostatic current:

**(28a)** `∫_exposed N_H₂ dA = j A_geom / (2F)`

> **⚠️ CORRECTED AT AUDIT 1 (finding A1.2).** The earlier form applied `N = j/(2F)` over the
> uncovered area, which yields total generation `(1 − Θ)·j/(2F)` and therefore **violates the
> imposed galvanostatic current**, artificially suppressing bubble growth as coverage rises. This
> was a genuine current-conservation bug that would have silently corrupted the whole campaign.
> For O₂ the divisor is `4F`.
>
> **This convention is used identically in the gas source term, the Butler–Volmer boundary
> condition and the MD→VOF closure** — stated once, here, and not restated differently anywhere.

### 4.4 Verification target
For a bubble growing in a uniformly supersaturated quiescent liquid, the Epstein–Plesset/Scriven
similarity solution gives

**(29)** `R_b(t) = 2 β √(D t)`, with β from `S = 2β²[1 − β√π exp(β²) erfc(β)]⁻¹`-type closure

**No campaign case runs until (29) is reproduced.**

---

## 5. Closure regression — the deliverable object **[AN]**

### 5.0 ⚠️ What a single-bubble simulation can and cannot deliver — restructured at Audit 1 (A1.7)

An interface-resolved **single-bubble** calculation does **not** produce electrode coverage.
Coverage additionally requires nucleation-site density, site activation statistics, bubble-cycle
frequency, coalescence and an averaging window — none of which a single axisymmetric bubble
contains. Regressing Θ directly from such a campaign would compare a *constructed single-bubble
area fraction* against an *electrode-population correlation*, which is not a like-for-like test.

**Coverage is therefore constructed explicitly, not regressed directly:**

**(29a)** `Θ = N_site · A_footprint(θ, R_det) · f_residence(j, v, θ) · f_overlap`

| Factor | Origin | Derived here? |
|---|---|---|
| `A_footprint(θ, R_det)` = π R_det² sin²θ | resolved VOF | ✅ **yes** |
| `R_det(θ, j, v)` | resolved VOF force balance, eq. (14) | ✅ **yes** |
| `f_residence(j, v, θ)` — growth + waiting time per cycle | resolved VOF, several stationary cycles | ✅ **yes** |
| `f_overlap` — geometric overlap correction | analytic, stated | ✅ yes (assumption) |
| **`N_site`** — active nucleation-site density | **external: experiment/literature** | ❌ **NO — explicit external input** |

> **The claim is therefore "the wettability dependence of coverage is derived", not "coverage is
> derived".** The former is defensible; the latter is not, and the auditor identified it as one of
> the two attacks that challenge the central word *derived*. `N_site` is dominated by sub-surface
> cavity geometry and surface finish, which classical MD of a flat Ni(111) slab cannot supply.
> This decomposition is the one both pre-execution reviewers independently proposed, so adopting it
> converts the objection into the manuscript's structure.

### 5.1 Regression of the derived factors

Functional form **specified before fitting**, so the fit cannot be reverse-engineered from the data:

**(30)** `Θ(j, v, θ) = C · (j / j_ref)^a · g(θ) · h(v)`  — fitted to eq. (29a) evaluated with a
**stated, fixed** `N_site`, so the closure's θ- and v-dependence is traceable to the resolved
simulations and its absolute level is traceable to the declared `N_site`.

with the Vogt form recovered as the special case `a = 0.3, C = 0.023 j_ref^0.3, g ≡ 1, h ≡ 1`, and

**(31)** `g(θ) = [ (1 − cos θ) / (1 − cos θ_ref) ]^b`

**(32)** `h(v) = [ 1 + (C₄ v)² ]^{−2}`  (E20 form retained so the flow dependence is directly
comparable with Eigeldinger & Vogt)

Fitted parameters {C, a, b, C₄} with 95% confidence intervals from the covariance of the nonlinear
least-squares fit; **20% of the campaign held out as a test set**; reported with the RMSE on held-out
points. The **validity box** in (j, v, θ, c, T) is reported explicitly and the cell model refuses to
extrapolate outside it — the direct answer to the closure-extrapolation problem this study exists
to address.

---

## 6. Scale 2.5 — Kinetics **[CT]**

**(33)** `j = (1 − Θ) j₀(T, c, a_el) [ exp(α_a n F η_act / RT) − exp(−α_c n F η_act / RT) ]`

with the kinetic convention of §2 (n = 1, α = 0.5, geometric `j`, ECSA carried explicitly).

Cantera evaluates `j₀(T, c_KOH)` and its temperature/concentration dependence, **pre-tabulated** to a
`foamFile` lookup and interpolated in the OpenFOAM boundary condition. Runtime C++ linkage of
Cantera into OpenFOAM is deliberately avoided: it is a schedule risk with no scientific benefit,
since the kinetics evaluated here is algebraic.

---

## 7. Scale 3 — Cell **[CELL]**

### 7.1 Two-fluid equations
**(34)** `∂(ε_k ρ_k)/∂t + ∇·(ε_k ρ_k u_k) = Γ_k`,  Σ_k ε_k = 1

**(35)** `∂(ε_k ρ_k u_k)/∂t + ∇·(ε_k ρ_k u_k u_k) = −ε_k ∇p + ∇·(ε_k τ_k) + ε_k ρ_k g + M_k`

with interphase momentum transfer `M_k = M_drag + M_lift + M_wall + M_disp`, each closure named and
attributed to its corpus source in the Methods.

### 7.2 Charge transport
**(36)** `∇·( σ_eff ∇φ ) = 0`

**(37)** `σ_eff = σ₀ (1 − ε_g)^{3/2}`  (Bruggeman)

### 7.3 Loss decomposition — as stated in the problem statement
**(38)** `U_cell = U_rev + η_act,a + |η_act,c| + η_ohm + η_conc`

**(39)** `Δη_act = (RT / (α n F)) ln[ 1/(1 − Θ) ]`  (Tafel limit)
At α = 0.5, n = 1, 353 K: Θ = 0.2 → **13.6 mV**; Θ = 0.8 → **97.9 mV**.

**(40)** `η_ohm = j d_gap / σ_eff`

**(41)** `η_conc = (RT/nF) ln[ 1/(1 − j/j_lim(Θ)) ]`

### 7.4 ⚠️ No double counting — explicit statement
Bubble effects enter in **two physically distinct places** and must not be applied twice:
- **Θ (adhering, at the wall)** reduces *active area* → equations (33), (39).
- **ε_g (dispersed, in the bulk)** reduces *conductivity* → equations (36), (37), (40).

These are different populations of gas. A bubble that has detached leaves Θ and joins ε_g. The
implementation must conserve that transfer, and the QC script checks it. *(Flagged for Audit 1 Q1.)*

### 7.5 Headline result
**(42)** `ΔV_cell(j) = U_cell[Θ_Vogt] − U_cell[Θ_T12]`

evaluated over j ∈ [10², 10⁴] A m⁻², with the T12 closure applied only inside its validity box.
