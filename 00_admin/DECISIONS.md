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
