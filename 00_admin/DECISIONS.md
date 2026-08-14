# DECISIONS — T12 rev B execution

Every judgement call, with a one-line rationale. Standing order S1/S2: decisions are made and
logged, never escalated for approval.

## Phase 0

**D0.1 — sudo unavailable; proceeded without it rather than declaring a hard stop.**
`sudo apt-get` failed (no tty/password). Hard-stop rule S3.2 covers credentials the environment
does not hold, but sudo proved unnecessary: g++ 11.4, mpicc with headers, `fftw3.h`, BLAS and pip
were all already present. LAMMPS was configured with `CMAKE_INSTALL_PREFIX=$HOME/.local` and
everything else installed to user prefixes. Escalating here would have stalled the run for nothing.

**D0.2 — LAMMPS built CPU-only.**
`nvidia-smi` is absent, so CUDA is not exposed to this WSL2 instance and `PKG_GPU` was dropped.
Cost is low: `fix electrode` performs the constant-potential matrix solve on CPU in any case, so the
GPU would only have accelerated pair styles. MD wall-time estimates in `01_env/benchmark.md` are
CPU-based accordingly.

**D0.3 — `virtualenv` instead of `python3 -m venv`.**
`ensurepip` is missing and `python3.10-venv` needs sudo. `virtualenv` (pip --user) bundles pip and
produces an equally isolated environment, satisfying the brief's "never the system Python".

**D0.4 — packmol built serially.**
`make -j8` fails with `Cannot open module file 'pbc.mod'` — a dependency-ordering bug in packmol's
own Makefile, not a missing prerequisite (gfortran is present). Serial `make` succeeds.

**D0.5 — Benchmarked before sizing anything, and let the numbers overrule the plan.**
The measured interFoam throughput and the 23 GB memory ceiling make a 3D parametric VOF sweep
infeasible by ~250×. Rather than record that as a risk, the design is changed now: **the parametric
campaign is axisymmetric**, with ≤3 coarser 3D confirmation cases. This is the concrete answer to
the pre-execution audit finding that the VOF campaign was "not computationally credible as
described" — it is credible axisymmetrically, and the claim is scoped to match.

**D0.6 — `fix electrode` overhead flagged as unmeasured.**
The rhodo benchmark does not include a constant-potential solve, so MD throughput for the real
system is uncertain by an assumed 2–4×. First task of Phase 3 is to measure it directly before the
MD matrix is committed. Recorded so the estimate is never mistaken for a measurement.

## Phase 1

**D1.1 — Soft Matter 2024 paywalled; proceeded on verified abstract only.**
RSC 403s automated fetch. The core fact (MD + CFD combined for electrolytic gas bubbles, ~0.01 nN
Marangoni force from both) is confirmed and is enough to scope the novelty. The unverifiable detail
(whether contact angle specifically is passed) is marked UNVERIFIED and T12's framing is written so
it does not matter either way — the delta rests on *coverage closure + cell scale*, which that paper
does not address on any reading.

**D1.2 — Applicability map promoted to a primary deliverable.**
The prior-art sweep found a substantial, current Marangoni literature including a *Nature Chemistry*
paper stating the solutal Marangoni effect *determines* bubble dynamics in HER. A θ-only closure is
therefore already contradicted somewhere in the envelope. Rather than defend a universal closure,
T12 will map where θ control holds and where it does not. This converts the field's strongest
counter-argument into the study's second result.

**D1.3 — 3D confirmation cut from 3 cases to 1, run to first departure only.**
Generated budget showed 3 × 360 h = 1080 h — 92% of the VOF stage for 3 cases. One corner, run to
first departure (~1–2 ms rather than 10 ms), tests the axisymmetry assumption at ~7% of the cost.
Total active budget fell from 2750 h to 1742 h; critical path 1230 h (51 days). The other two
corners are marked `deferred`, not deleted, so the maintenance loop (§9) can pick them up if time
allows.

**D1.4 — MD matrix is OFAT, not full-factorial.**
At 685 katom-step/s before the unmeasured `fix electrode` overhead, a state point is 2–15 days. A
full factorial over (ΔΨ, c, T, R) is impossible. Only the ΔΨ axis — on which prediction P1 depends —
runs at full resolution with 3 sizes for line-tension extrapolation. Concentration and temperature
are single-factor arms at priority 6, truncatable without losing P1.

**D1.5 — Rox 2022 adopted as an anchor despite its stated limitations.**
Its ~20% resolution floor, ±50% timing uncertainty and detached-bubble contamination are real, and
are recorded in the anchor file. It is still the only open-access measured-coverage dataset located,
the only one on porous Ni, and it spans 100–2000 A/m². Used as a *secondary* anchor for the porous
arm, never as the sole basis for a claim.

## Phase 2 — corrections, and Audit 1 reconciliation

### D2.1 — I corrected my own MD throughput error before the audit landed
`01_env/benchmark.md` claimed "5–14 M steps/day, 10–28 ns/day at 2 fs" for a 100k-atom system.
Correct arithmetic: 685 000 atom-step/s ÷ 100 000 atoms = 6.85 steps/s = **0.59 M steps/day =
1.18 ns/day**. Overstated by 10–20×. Caught by cross-checking against the measured conp run,
corrected in place with a visible CORRECTION block rather than silently. **Codex independently
found the same error (factor ~12) in Audit 1 — agreement confirms it.**

### D2.2 — MD sized at 20–30k atoms and scheduled as concurrent jobs
Measured strong scaling of the real conp system: 1 rank 132.8, 2 ranks 143.5, 4 ranks 232.8,
8 ranks 252.8 katom-step/s — **parallel efficiency collapses to 24% at 8 ranks**. Aggregate
throughput on 16 cores is therefore maximised by **16 concurrent 1-rank jobs (~2125 katom-step/s,
≈8× a single 16-rank job)**. The MD campaign is embarrassingly parallel across state points, so all
12 θ cases run simultaneously and complete in one case's wall time (~13–20 days at 20–30k atoms).
**Project wall-clock estimate: 29 days.** This is the mitigation Codex did not have when it computed
487 serial days.

### D2.3 — `fix electrode/conp` overhead MEASURED at 1.72× (OI-1 CLOSED)
Baseline `pppm` 1.846 s vs `pppm/electrode` + `fix electrode/conp` 3.171 s on the real 4006-atom
Ni|water cell (1654 electrode atoms). Better than the assumed 2–4×. Physics verified: induced
charges exactly equal and opposite each step, growing as the double layer forms.
`pppm/electrode` is mandatory — plain `pppm` raises `KSpace does not implement ElectrodeKSpace`.

---

## Audit 1 reconciliation — Codex (code/numerics/claims)

**Auditor verdict: major revision / no-go for the current matrix. I accept that verdict.**
`agy` was unavailable (OA-1), so this audit is **SINGLE-AUDITOR — DEGRADED**; the physics-and-
modelling perspective is the one missing, and it is the more consequential for this material.

Every finding was independently verified by me before acceptance.

| # | Finding | Verified? | Disposition |
|---|---|---|---|
| **A1.1** | Eq (3) gives **97.9 mV** at Θ=0.8, not the 49 mV stated; 13.6 mV not 6 mV at Θ=0.2 | ✅ recomputed: RT/(αF)=60.84 mV at 353 K, α=0.5 | **ACCEPT.** My numbers silently assumed αn=1 (n=2). Equations and numbers corrected; the kinetic convention is now stated explicitly rather than assumed. |
| **A1.2** | Faradaic flux ṅ=j/(2F) over *uncovered* area contradicts geometric-j Butler–Volmer; total gas becomes (1−Θ)j/(2F), violating galvanostatic current | ✅ inspection | **ACCEPT — this was a current-conservation bug** that would have silently suppressed growth as coverage rose. Corrected to ṅ_exposed = j/(2F(1−Θ)), with the surface integral constrained to jA_geom/(2F). Convention now stated once and used identically in MD→VOF closure, gas source and BV boundary. |
| **A1.3** | Cylindrical periodic cap has **straight contact lines, zero in-plane curvature** → the τ/(γR) correction does not apply. Cylinders *suppress* line tension, they don't measure it | ✅ geometry | **ACCEPT IN FULL — a real physics error.** The 1/R line-tension extrapolation is removed. |
| **A1.4** | R = 8 nm cap cannot fit a 5 nm box | ✅ **worse than stated** — my design-spec box is 8a = **2.82 nm**, so even R=3 nm fails | **ACCEPT.** Box redesigned; see D2.4. |
| **A1.5** | Marangoni stress requires a constitutive γ(c); with constant surface tension **F_M ≡ 0** and P3 can never be tested | ✅ inspection of eq (18) — I wrote ∂γ/∂c but never specified it | **ACCEPT — design-fatal if unfixed.** A γ(c, T, c_KOH) law is now a required deliverable before any P3 case runs. |
| **A1.6** | P3 not identifiable from an OFAT cross (all θ at one v, all v at one θ) — cannot estimate v×θ or j×θ interactions | ✅ inspection | **ACCEPT.** VOF matrix rebuilt as an interaction-resolving factorial. |
| **A1.7** | A single-bubble VOF calculation does not produce electrode coverage: needs nucleation-site density, cycle frequency, coalescence, averaging window | ✅ | **ACCEPT — and it reshapes the claim.** See D2.5. |
| **A1.8** | Uniform 1.5 h per VOF case ignores growth time ∝ 1/j | ✅ computed: to R=50 µm, t ≈ 5.74 s at j=100 vs 57 ms at j=10⁴ — **100×** | **ACCEPT.** Per-case end times are now physics-based; the low-j corner is redesigned (D2.6). |
| **A1.9** | The 0.01 nN Soft Matter force cannot establish that a Λ=1 boundary lies in the envelope (capillary scale γR ≈ 3.6–7.2 µN for a 50–100 µm bubble) | ✅ 5–6 orders apart | **ACCEPT.** Reachability of the P3 boundary is now an open question to be settled by pilot cases, not an assumption. |
| **A1.10** | Vogt/Rox "measurand mismatch" is plausible but **not demonstrated**; must not be called a resolution | ✅ | **ACCEPT.** The anchor file already said "do not report as refutation"; `problem_statement.md` was more confident than the anchor and is corrected to match. |
| **A1.11** | "Potential-aware molecular contact angle" overstates what a non-reactive force field establishes (no Ni oxidation/hydroxylation/specific adsorption) | ✅ | **ACCEPT.** Claim narrowed to a *model-potential-dependent intrinsic angle*, with the chemistry limitation stated in LIMITATIONS. |
| **A1.12** | Equilibrium nanocap angle ≠ the advancing/receding dynamic angle the continuum needs | ✅ | **ACCEPT, PARTIALLY MITIGATED.** MD supplies the *equilibrium centre and its potential-induced shift*; θ_A/θ_R hysteresis comes from measured data (E15's fitted values). Stated in the coupling contract. |
| **A1.13** | One coarse 3D case cannot bound the axisymmetry assumption; ≥2 contrasting cases needed | ✅ | **PARTIALLY ACCEPT.** Reinstate a **second, contrasting** 3D case (high-j, high-θ) — cost ~144 h total, affordable under the concurrency finding. The claim is narrowed to "does not change the *coverage trend* at the two corners tested". |
| **A1.14** | Mesh-refinement cost budgeted equally for 4/2/1 µm ignores ~11.3× scaling per halving in a 2D wedge | ✅ 2²×2^1.5 | **ACCEPT.** Mesh-study budget corrected. |
| **A1.15** | 8 h insufficient for converged Green–Kubo viscosity + 3 diffusivities in concentrated KOH | ✅ | **ACCEPT.** Bulk-validation budget raised and replicas added. |
| **A1.16** | No allowance for failed starts, discarded equilibration, replicas, restarts, rework | ✅ | **ACCEPT.** A 30% contingency is added to the wall-clock estimate. |

### Rejected: nothing
No finding was rejected. Every one was verified and every one was correct. That is an unusually
clean audit and it is recorded as such.

### D2.4 — MD contact-angle protocol redesigned (A1.3 + A1.4)
- **Cylindrical (quasi-2D) H₂ bubble under KOH**, periodic along the cylinder axis.
- **No 1/R line-tension fit.** The cylinder is used, as is standard, to *suppress* the line-tension
  correction; the reported quantity is the planar equilibrium angle.
- **Box-size convergence replaces size extrapolation**: lateral box swept at 3 sizes to demonstrate
  the angle is converged with respect to periodic images and the opposing wall, which is a
  *convergence check*, not a physical extrapolation.
- Angle reported through the **liquid**, matching the OpenFOAM convention.
- Potential referenced to the **PZC**, computed as a separate run, not to the raw slab ΔΨ.
- **Independent replicas (≥3 seeds)** at each state point; uncertainty from replica spread, not
  from block averaging of one trajectory.

### D2.5 — The coverage claim is restructured (A1.7)
A single-bubble simulation cannot produce Θ. Coverage is therefore constructed explicitly:

> **Θ = N_site · A_footprint(θ, R_det) · f_residence(j, v, θ) · f_overlap**

T12 derives the **wettability-dependent factors** — A_footprint(θ), R_det(θ, j, v) and the residence
time — from the resolved simulations. **N_site is an explicit external input** taken from
experiment/literature and stated as such, not derived. This is exactly the decomposition both
auditors supplied in the pre-execution review, and adopting it converts A1.7 from an objection into
the manuscript's structure. The claim becomes "the wettability dependence of coverage is derived",
which is defensible, rather than "coverage is derived", which is not.

### D2.6 — VOF matrix rebuilt (A1.6 + A1.8)
- Interaction-resolving factorial: **j ∈ {100, 500, 2000, 10000}, v ∈ {0, 0.05, 0.2},
  θ ∈ {30, 90, 150}°** = 36 cases, with adaptive refinement near any Λ = 1 transition.
- **Per-case end time is physics-based**, from the Faradaic growth-time estimate t ∝ 1/j, and
  measured over several stationary departure cycles rather than a fixed 10 ms.
- **Low-j redesign:** growing a 50 µm bubble at 100 A/m² needs ~5.7 s (~10⁷ steps) and is not
  affordable. The low-j corner instead uses a **seeded near-departure bubble** to measure the
  departure event directly, with the growth phase treated analytically. Stated as a method choice.

## Audit 1 — agy (physics & modelling). Two-auditor reconciliation.

**OA-1 withdrawn: `agy` was never unauthenticated** — the failure was an intermittent IPv6 route
problem in the eligibility check (see `OPERATOR_ACTION.md`). Audit 1 is therefore **NOT degraded**;
it has both auditors. My earlier "SINGLE-AUDITOR — DEGRADED" tag is retracted.

**agy verdict: CONDITIONAL PASS / major modelling revisions required.**
(Codex verdict: major revision / no-go for the current matrix.)

### Independent confirmation — the two auditors agree, having never seen each other's response

| Finding | Codex | agy | Status |
|---|---|---|---|
| Eq (3) → **97.9 mV** at Θ=0.8, not 49 mV | ✅ | ✅ identical derivation | **Confirmed twice.** Already fixed. |
| Faradaic flux must be **j/(2F(1−Θ))** | ✅ | ✅ identical | **Confirmed twice.** Already fixed. |
| Cylindrical cap: **κ_line ≡ 0**, so no 1/R line-tension fit | ✅ | ✅ + geodesic-curvature derivation | **Confirmed twice.** Already fixed. |
| `N_site` must be an external input; only wettability-dependent factors are derived | ✅ | ✅ | **Confirmed twice.** Already fixed. |
| MD concurrency: 12 concurrent 1-rank jobs ≈ one case's wall time | (not raised) | ✅ computes 16.3 d | Matches my measured 19.6 d. |
| Seed low-j cases at 0.90 R_det | ✅ | ✅ | Already implemented (0.85). |

Two independent auditors reaching the same four blocking findings by different routes is strong
evidence the findings are real, and it retires any doubt about the corrections already applied.

### New physics from agy that Codex did not supply — all verified by me

**N1 — P3 is quantitatively out of reach, and this is the most consequential finding of Audit 1.**
agy computes the force ratio directly. I reproduced it:

| Driver | ∂γ/∂c | Δc | Δγ | F_Mar | **Λ = F_cap/F_Mar** |
|---|---|---|---|---|---|
| dissolved H₂ | ~1×10⁻⁴ N m⁻¹ M⁻¹ | 10 mM | 1.0×10⁻⁶ N m⁻¹ | **0.05 nN** | **~78 000** |
| KOH gradient | ~2.5×10⁻³ N m⁻¹ M⁻¹ | 0.1 M | 2.5×10⁻⁴ N m⁻¹ | **12.5 nN** | **~313** |

against `F_cap = π R_base γ sinθ ≈ **3.9 µN**` for a 50 µm bubble. **Marangoni is 2–5 orders of
magnitude too small.** The Λ = 1 boundary is not reachable in the industrial envelope except as
θ → 0 or for sub-micron bubbles.

**N2 — Lippmann electrowetting gives P1 a pre-registered quantitative threshold**, which is exactly
what Codex demanded ("'measurably' needs a numerical decision rule"). The two audits complement:
`cos θ(ΔΨ) = cos θ_pzc + C_dl(ΔΨ − Ψ_pzc)²/(2γ_lv)`.
Verified: at C_dl = 0.1 F m⁻², ΔΨ = 0.5 V → **10° shift**; C_dl = 0.3 F m⁻², 0.5 V → **31°**.
*My addition:* at C_dl ≥ 0.2 F m⁻² and ΔΨ = 1.0 V the quadratic predicts cos θ > 1, i.e. complete
wetting — unphysical. **Contact-angle saturation is a real, documented electrowetting phenomenon**,
so the quadratic is an upper bound and observing saturation in the MD is a result, not a failure.

**N3 — The Vogt/Rox reconciliation has an exact geometric mechanism.**
`A_contact/A_projected = sin²θ`. Verified: at θ = 30° or 150° the optical measure is inflated
**4.00×**; at 90°, 1.00×. Combined with 3D porous-mesh line-of-sight integration and detached-plume
occlusion, this accounts for the 4–6× discrepancy without either dataset being wrong.

**N4 — Nernstian dissolved-gas overpotential is missing from eq (5).**
`ΔE_rev = (RT/2F) ln(c_H₂,surf/c_H₂,sat)`, reaching **40–80 mV** at high current density, is
distinct from the mass-transfer limiting current. Eq (5) must state which it represents.

**N5 — The kinetic convention choice is worth 3× in the answer.**
Volmer-limited (αn = 0.5): **140.1 mV/dec**, penalty 97.9 mV at Θ = 0.8.
Heyrovsky-limited (α_app = 1.5): **46.7 mV/dec**, penalty **32.7 mV**. Both verified.
The manuscript must name the assumed rate-determining step and quote the implied Tafel slope, since
the coverage penalty — the study's headline quantity — depends on it by a factor of three.

**N6 — Double-counting has a concrete failure mode.** If the near-wall cell carries the adhering
bubble volume inside ε_g *and* the boundary face applies (1−Θ), the ohmic drop across that cell is
penalised twice. Guard: adhering gas → Θ only; on detachment it is injected as a volumetric source
into ε_g. Added to the QC assertions.

### Reviewer-vs-reviewer disagreements — my rulings

**D-AUDIT-1 — Number of 3D confirmation cases.**
*Codex:* one corner cannot bound the axisymmetry assumption; **≥2 contrasting** cases required.
*agy:* cut to one; defer the second (Cut 3).
**RULING: Codex.** Keep **two contrasting corners**, at priority 5 (deferrable if the schedule
slips). agy's own §(b)(2) strengthens Codex's case: axisymmetry suppresses shear-induced asymmetric
contact-line depinning and bubble tilting, which cause departure at *smaller* radii. Since
agy's N1 shows Marangoni is negligible, **asymmetric shear departure becomes the leading
uncertainty**, so bounding it with one case is not enough. Cost is 144 h, affordable.

**D-AUDIT-2 — Is the Vogt/Rox mismatch demonstrated?**
*Codex:* "plausible and probably a large part of it, **but not demonstrated** — must not be called
a resolution."
*agy:* "physically correct and **mathematically demonstrable**", and supplies sin²θ.
**RULING: Codex's standard, agy's mechanism.** The mechanism is adopted as the *route* to a
demonstration; the claim remains "characterised, not resolved" until the dual extraction
(Θ_adh and synthetic-optical A_cov,proj on one time base) actually reproduces both numbers.
Codex is right that a smooth axisymmetric bubble cannot fully perform a *porous-electrode*
reconciliation, so the manuscript will state what the demonstration does and does not cover.
OI-6 stays open.

**D-AUDIT-3 — Status of P3.**
*Codex:* reachability "not established by the cited evidence"; requires pilot cases before
allocating the map.
*agy:* quantitatively unreachable (Λ ≈ 300–78 000); reframe as a bounding test.
**RULING: agy, with Codex's guard.** P3 is **reformulated** (D2.7). The scaling is accepted as the
pre-registered expectation; Codex's demand for verification is met by the mandatory thermocapillary
benchmark (`VOF-000b`) plus **two pilot cases at the most Marangoni-favourable corner** before any
map is allocated. If the pilots contradict the scaling, the map is reinstated at full resolution.

### D2.7 — P3 reformulated, and D1.2 partially reversed

**Old P3:** "There exists a boundary in (j, v) beyond which departure is Marangoni-controlled and
θ-insensitive." — Likely false, and it was driving a large campaign toward a null.

**New P3:** *"Across the industrial envelope (j = 10²–10⁴ A m⁻², v = 0–0.2 m s⁻¹), the
capillary-to-Marangoni force ratio Λ satisfies Λ ≫ 1, so bubble departure is capillary/wettability-
controlled and a θ-dependent coverage closure is valid throughout. The θ-controlled region is
bounded quantitatively rather than assumed."*
*Falsified if* any (j, v) in the envelope yields Λ < 10 in the verified implementation.

**This partially reverses D1.2**, which promoted the applicability map to a primary deliverable on
the grounds that Marangoni was the principal threat to a θ-only closure. agy's scaling shows it is
not a threat *at this scale*. The map survives but changes role: from "where wettability closures
break down" to **"quantitative demonstration that wettability control is the dominant lever across
the whole industrial envelope"**.

**Regime distinction that must be stated in the manuscript, or a referee will raise it:** the
Marangoni literature identified in `prior_art_delta.md` (*Nature Chemistry*, *PRR*, *Electrochim.
Acta*) is predominantly **microelectrode** work — single bubbles, tens of µm and below, with very
high local supersaturation. agy's scaling applies to **macroscopic bubbles on planar/porous
electrodes at industrial current density**. The apparent contradiction is a *regime difference*,
not a disagreement, and saying so explicitly is itself a contribution.

## Phase 3

**D3.1 — No `minimize`; displacement-capped push instead.**
LAMMPS warns "Using fix shake with minimization" because SHAKE is *ignored* during minimisation, so
a minimised configuration is not consistent with the constrained dynamics that follow. CG with PPPM
on a lattice start was also measured at ~21 iterations in 2 minutes. A `fix nve/limit 0.05` push
with a strong Langevin thermostat relaxes close contacts robustly, keeps SHAKE active throughout,
and is ~30× cheaper.

**D3.2 — Verify file contents after every edit, before launching compute.**
An edit reported success but did not persist; a smoke test then silently ran stale input containing
the very `minimize` command I had removed, and I nearly diagnosed a phantom problem. Cheap rule,
adopted: `grep` the file for the changed token before any run that costs more than a minute.

**D3.3 — Launched the campaign despite an adverse early density signal.**
The smoke test suggests ρ may land ~5% high, outside the 3% gate. Launching anyway is correct: the
smoke had 1500 equilibration steps against production's 70 000, and the gate is only meaningful on
converged, replica-averaged data. Deciding the force field is wrong from an unconverged smoke test
would be exactly the kind of premature conclusion the gate is designed to prevent. **If production
confirms the miss, the force field is replaced — most likely by a two-site OH⁻ or a K⁺/OH⁻ LJ
re-tune against density — and the θ campaign does not launch until it passes.**

**D3.4 — Core budget interpreted as logical cores.**
Operator instruction was "keep 4 cores free, use the rest". Their own two jobs hold 16 ranks; mine
take 12; total 28 of 32 logical cores, leaving exactly 4. My jobs run at `nice -n 5` so the
operator's work retains priority under contention.

**D3.5 — Force field REJECTED by its own gate; re-tuning rather than excusing.**
The pre-registered density criterion (3%) failed by 6.3–9.2% at every state point, with replica
scatter 20–60× smaller than the discrepancy. This is exactly the outcome the gate was built to
catch, and it caught it *before* 12 concurrent contact-angle runs were committed to a model that
would have produced a confidently wrong wettability.

**Diagnosis, not just detection.** The error scales with ion concentration (6.5% → 9.2% from 20 to
30 wt%), and D(H₂O) is suppressed ~7× versus neat water where experiment suggests far less. Both
point to over-compact, over-bound ions rather than a water-model problem. The ad-hoc element of the
force field is the hydroxide: a single LJ site carrying −1 with SPC/E *oxygen* size. Real OH⁻ has a
larger effective radius; a bare oxygen-sized unit anion over-attracts its solvation shell.

**Fix under test:** a σ-scan on OH⁻ at the worst state point, spanning oxygen-like to halide-like
size. Re-tuning an ion's LJ diameter to reproduce solution density is a standard and defensible
parametrisation route, and will be reported as such — the manuscript will state that the hydroxide
LJ diameter was tuned against KOH(aq) density rather than implying it was taken from a source.

**If the scan cannot reach 3% at both concentrations simultaneously**, the single-site
representation is inadequate and a two-site OH⁻ (explicit O–H with partial charges) is adopted
instead. That is a larger change and would be logged as such.

**Note on what did NOT happen:** no attempt was made to widen the gate to accommodate the result.
The criterion was fixed before the data existed and is being held to.

**D3.6 — Operator escalation policy for blocking gates (2026-08-14).**
Operator instruction: when a gate blocks and requires resolution, escalate to a higher model
(Opus) for up to **3 attempts**; if unresolved, escalate to **Fable** for up to 3 attempts; if still
unresolved, **stop and require human approval**. Recorded here as standing procedure.

Escalation ledger:
| Gate | Attempt | Model | Outcome |
|---|---|---|---|
| FF density gate (D3.5) | 1 | Opus | dispatched 2026-08-14 |

## Phase 3 — escalated gate analysis (Opus, attempt 1 of 3) and three self-inflicted bugs it exposed

The escalated analysis resolved the diagnosis and exposed **three defects in my own work**, two of
which I verified arithmetically before accepting.

### D3.7 — Yeh–Hummer correction was DOCUMENTED BUT NEVER IMPLEMENTED
`validate_bulk.py` promised a finite-size correction in its docstring and returned `slope/6.0` with
no correction applied. **Worse: I had already written "with a finite-size correction" into the
manuscript Methods (§3.2), so that sentence was false at the time of writing.** Now implemented
(`D_inf = D_pbc + k_BT·ξ/(6πηL)`, ξ = 2.837297). Measured corrections: **+10% to +17%**, largest at
30 wt% where the box is smallest and viscosity highest.
*This is the most serious class of error in the run so far: a documented-but-absent method that had
already propagated into a manuscript claim.* Lesson recorded — a docstring is not an implementation,
and anything the manuscript asserts about method must be traced to executing code before it is written.

### D3.8 — Experimental reference densities were 20 °C values mislabelled as 298 K
1.188 and 1.290 g/cm³ are the standard handbook figures at **20 °C**, not 25 °C. Corrected to
1.185 / 1.286 (298 K) and 1.166 (20 wt%, 333 K). **This made the failure slightly worse**
(30 wt%/298 K: 9.16% → 9.50%), which is the right direction for honesty — the correction was not
made to help the model. Provenance still needs pinning to one traceable source (Sipos et al.,
*JCED* **45**, 613 (2000) at 298 K; Åkerlöf & Bender, *JACS* **63**, 1085 (1941) for T-dependence) — **OI-15**.

### D3.9 — K⁺ ε was a unit-conversion bug
Joung–Cheatham publish ε(K⁺) = **0.4297 kcal/mol**. I used 0.10270, which is exactly 0.4297/4.184 —
I treated a kcal/mol value as if it were kJ/mol. Verified: 0.4297/4.184 = 0.102700. The σ I used
(2.8384 Å) *is* the correct JC value, so the parameter set was **internally inconsistent**, and my
own halide scan point (σ 4.83, ε 0.01279) used correct kcal/mol units. Corrected to 0.42970.
**It is not the cause of the density failure** — at K–O contact the Coulomb term is ~−100 kcal/mol
against a ~0.13 kcal/mol ε difference — and correcting it makes density marginally *worse*. Fixed
for reproducibility, not to chase the gate.

### D3.10 — My diagnosis was right in direction but wrong in reasoning
I argued "the error grows with concentration, therefore the ions". **That is a non-sequitur.**
Expressed as apparent molar volume the deficit is **≈13 cm³ per mole of KOH and nearly
concentration-independent** (15.0 at 20 wt%, 12.4 at 30 wt%). The growth from 6.9% to 9.5% is mostly
arithmetic — more ions times a roughly constant per-ion defect. The correct statement of the failure:

> **φ_V(KOH) = −3.5 cm³/mol at 20 wt% and +1.6 at 30 wt%, against experimental +11.5 and +14.0.
> The model says dissolving KOH in water *shrinks* the liquid.**

Equivalent to a spurious internal pressure of ~2.5 kbar. The physical cause is that SPC/E's oxygen
σ/ε are calibrated for a site carrying −0.8476 *shielded* by two hydrogens; giving that same
repulsive core a bare, unshielded −1.0 strengthens ion–water attraction ~18% with no compensating
core growth, so the first shell collapses (predicted OH–O_w peak 2.5–2.6 Å against an experimental
2.77–2.79 Å).

### D3.11 — Adopt a published, validated force field rather than re-deriving one
Two peer-reviewed KOH force fields already solve this, one of them a LAMMPS study of KOH at
20–45 wt% (Frischknecht & Stevens, Sandia) which reports **this exact failure mode** and finds that
scaling ion charges by 0.8 is required *even with a correctly sized OH⁻*. Bonthuis et al. (2016)
independently derived σ(OH⁻) = 3.81 Å, ε = 0.01195 kcal/mol for SPC/E — **within 0.04 Å of the
crossing predicted from my own σ-scan slope**, which is strong mutual corroboration.

Also important: Bonthuis found the optimal q_H(OH⁻) is **exactly zero**, i.e. the best available
non-polarisable OH⁻ for SPC/E *is* a single charged LJ sphere. **My single-site topology was right;
only the parameter values were wrong.** That retires the "move to a two-site OH⁻" plan as the
primary fix.

**Launched now (4 runs, decisive):** Bonthuis OH⁻ + Loche K⁺, geometric mixing, at
**q = 1.0 and q = 0.8**, at both 20 and 30 wt%. This separates the size error from the charge error
in two simulations: if q = 1.0 with correct σ still overpredicts density, charge scaling is
load-bearing and no σ can substitute.

### Escalation ledger update
| Gate | Attempt | Model | Outcome |
|---|---|---|---|
| FF density gate | 1 | Opus | **Diagnosis resolved; concrete published parameters supplied; 3 of my own bugs found. Fix under test.** Not yet closed — closure requires the published-FF runs to pass. |
