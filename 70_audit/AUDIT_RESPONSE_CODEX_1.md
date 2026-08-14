# Independent code, numerics and claims audit — Audit 1

## Overall verdict

The problem is worth studying, but the present design is **not ready for production**. Four issues
are blocking rather than cosmetic:

1. The quoted 49 mV coverage penalty is inconsistent with the printed equation. Equation (3) gives
   **97.9 mV**, not 49 mV, for \(\Theta=0.8\), \(\alpha=0.5\), and 353 K unless an omitted
   \(n=2\) is inserted.
2. The MD throughput has been converted incorrectly by about a factor of 12 before the unmeasured
   constant-potential overhead. A 120k-atom contact-angle case needs roughly **41–203 days** for
   20–50 ns even under the favorable 2 fs assumption, not 3 days.
3. A cylindrical, periodic cap cannot be given the stated \(1/R\) line-tension correction: its
   straight contact line has zero in-plane curvature. In addition, an \(R=8\) nm base cannot fit
   in a 5 nm lateral box.
4. P3 cannot be inferred from the proposed OFAT cross. The model description also does not yet
   specify the concentration-dependent surface tension term needed to create a solutal Marangoni
   stress at all.

The campaign should be re-budgeted and the MD/VOF observables made operational before any
production matrix is launched.

## Q1 — Physics, equations, and double-counting

### Equations (1)–(3): activation

Equation (1) is a conventional bookkeeping identity, but it needs separate anodic and cathodic
coverage/concentration terms. One \(\Theta\) cannot represent H2 coverage at the cathode and O2
coverage at the anode unless one electrode is explicitly declared negligible. The signs are
acceptable if all loss terms are reported as positive voltage magnitudes.

Equation (2) is dimensionally consistent only after its area basis is fixed:

- \(j\) must be the total current divided by a stated geometric area;
- \(j_0\) must be referenced to the corresponding clean exposed area; and
- for a porous electrode, the roughness/ECSA factor cannot silently disappear into \(j_0\).

The factor \((1-\Theta)\) is physically appropriate for an impermeable, electrochemically inactive
bubble footprint. It is not a general correction for every bubble effect. Also state the kinetic
convention: the general Butler–Volmer exponent is \(\alpha nF\eta/(RT)\). Omitting \(n\) is valid
only if it has been absorbed into the definition of \(\alpha\) or the elementary rate-controlling
step is explicitly a one-electron step.

The numerical check exposes an error. At 353 K and \(\alpha=0.5\),

\[
\frac{RT}{\alpha F}=60.84\ \mathrm{mV}.
\]

Therefore the printed equation gives

| Coverage | Printed equation (3) | Stated value |
|---:|---:|---:|
| \(\Theta=0.2\) | 13.6 mV | about 6 mV |
| \(\Theta=0.8\) | **97.9 mV** | about 49 mV |

The stated values are obtained with \(\alpha n=1\), for example \(\alpha=0.5,n=2\). Either add
\(n\) to equations (2) and (3) and justify \(n=2\), or retain the equations and correct both
numbers. For HER kinetics, inserting the overall two-electron stoichiometry into a one-step
Butler–Volmer exponent is not automatically justified; the kinetic convention must match the
chosen exchange-current model.

### Equation (4): ohmic loss

Equation (4) is dimensionally correct: \(jd/\sigma\) has units of volts. The exponent 3/2 is a
standard Bruggeman baseline for an approximately isotropic dispersed gas/liquid mixture, with
liquid fraction \(1-\varepsilon\). It is not a universal law for a wall-attached bubble layer,
strongly anisotropic channels, or porous Ni, particularly as the conducting liquid approaches
loss of connectivity. The exponent should be a sensitivity parameter unless independently
validated.

There is no inherent double-counting in applying \((1-\Theta)\) to reaction area and
\((1-\varepsilon)^{3/2}\) to bulk electrolyte conductivity. They describe different losses and
different measures: \(\Theta\) is a wall-area fraction and \(\varepsilon\) a volume fraction.
Double-counting occurs if the implementation does any of the following:

- treats the same resolved gas geometry as nonconducting and also applies Bruggeman to it;
- substitutes \(\Theta\) for \(\varepsilon\) without a separately validated mapping;
- uses \(j/(1-\Theta)\), rather than geometric \(j\), through the full gap in the ohmic formula;
  or
- adds the algebraic \(jd/\sigma_{\rm eff}\) loss to a potential equation that has already
  integrated that same conductivity loss.

For the Euler–Euler cell model, a defensible division is: use \(\Theta\) only in the electrode
kinetic boundary condition, use the local Eulerian gas volume fraction only in
\(\sigma_{\rm eff}\), and compute the ohmic voltage from the potential solution rather than adding
equation (4) again.

### Equation (5): concentration loss

Equation (5) is dimensionally correct and has the standard limiting-current singularity, but it is
not yet a closed model. It requires \(0\leq j<j_{\rm lim}\), a declared geometric-area basis, and
separate electrode/species definitions. Most importantly, \(j_{\rm lim}(\Theta)\) must be specified.
If \(j_{\rm lim}\) already contains an exposed-area factor, that does not duplicate activation
loss—one is kinetic and one is transport—but the same concentration loss must not also be taken
from a resolved species-transport/Nernst boundary calculation.

The sentence that equations (2)–(5) establish \(\Theta\) as *the* closure that matters is too
strong. Equation (4) depends on \(\varepsilon\), not \(\Theta\), and equation (5) currently depends
on an unspecified function.

### A current-conservation inconsistency in the design

The VOF specification imposes \(\dot n=j/(2F)\) **over uncovered area**, while equation (2) defines
\(j\) as geometric total current density. Those two choices reduce total H2 generation to
\((1-\Theta)j/(2F)\), violating the prescribed galvanostatic current and artificially suppressing
bubble growth as coverage rises. If \(j\) is geometric current density, the uniform uncovered-area
flux must be

\[
\dot n_{\rm exposed}=\frac{j}{2F(1-\Theta)},
\]

or, preferably, it should come from the solved local current distribution while its surface
integral is constrained to \(jA_{\rm geom}/(2F)\). For O2 the divisor is \(4F\). This convention
must be identical in the MD-to-VOF closure, gas source, and Butler–Volmer boundary.

## Q2 — Falsifiability and P3

### P1

P1 is falsifiable in principle, but not yet pre-registered tightly enough. “Measurably” needs a
numerical decision rule, independent replicas, and a confidence interval. Block averages from one
trajectory are not independent realizations. The matrix samples only non-negative \(\Delta\Psi\)
even though the envelope says \(\pm1\) V and the prediction is written in terms of
\(|\Delta\Psi|\). Moreover, cell voltage difference is not an electrode potential until it is
referenced to the potential of zero charge or another physical reference.

A defensible test would specify the relevant cathodic potential axis, the minimum meaningful angle
change, and a regression/equivalence criterion fixed before seeing results. If both signs are not
run, remove the \(|\Delta\Psi|\) claim.

### P2

P2 is only partly falsifiable as written. “The inter-model spread E04 reports” is not numerically
defined in the audited files, and “departure increasing with \(j\)” lacks a metric. Freeze an
absolute or relative equivalence band before simulation and compare at matched temperature,
electrolyte, flow, current-area basis, and coverage measurand.

More fundamentally, an interface-resolved single-bubble calculation does not by itself produce
electrode coverage. Coverage also requires nucleation-site density, site activation, bubble-cycle
frequency, coalescence, and an averaging interval. Those variables are absent from the matrix.
The output must be operationally defined—for example, time-averaged attached contact area divided
by geometric electrode area after several statistically stationary departure cycles—and the site
population must either be resolved or supplied as an explicit external closure. Otherwise P2
compares a constructed single-bubble area fraction with an electrode-population correlation.

### P3

P3 is **not well-posed or identifiable from the current design**.

1. “Insensitive to \(\theta\)” needs a tolerance such as a confidence bound on
   \(\partial R_d/\partial\theta\), not a verbal judgment.
2. Define a dimensionless force ratio, for example
   \(\Pi_M=|F_M|/|F_{\rm cap}|\), and a boundary such as \(\Pi_M=1\). The Marangoni force must be
   evaluated from the surface integral of the tangential stress, while capillary retention must
   include advancing/receding angles. Buoyancy, imposed-flow drag, pressure, and electric forces
   must also be reported. At \(v=0.2\) m/s, an observed loss of angle sensitivity could be
   shear-controlled rather than Marangoni-controlled.
3. Dissolved-H2 transport plus a Henry jump is not sufficient to generate Marangoni stress. The
   model needs validated \(\sigma(c,T,c_{\rm KOH})\) and the tangential
   \(\nabla_s\sigma\) term. With constant surface tension, \(F_M\) is identically zero.
4. The matrix measures all \(\theta\) values only at \(v=0.05\) m/s and all velocities only at
   \(\theta=90^\circ\). That OFAT cross cannot estimate the \(v\times\theta\),
   \(j\times\theta\), and three-way interactions needed to locate a boundary. At minimum, run
   low/high \(\theta\) at every \((j,v)\) point and adaptively refine cells that bracket
   \(\Pi_M=1\).
5. The boundary is not generally a curve in \((j,v)\). It is a surface depending on at least
   \(\theta_a,\theta_r\), bubble size, electrolyte, temperature, site geometry, and surface state.

Reachability is not established by the cited evidence. The only force magnitude stated in the
audited material is about 0.01 nN. A crude capillary scale for a 50–100 micrometre bubble is
\(\gamma R\approx3.6\)–7.2 micronewtons, five to six orders larger. That is **not** a valid
cross-scale force comparison, but it demonstrates why the cited number cannot be used to assert
that a boundary lies inside the proposed envelope. Corner pilot cases with a verified Marangoni
implementation are required before allocating the map.

If Marangoni dominates the entire industrial envelope, the project still has a legitimate negative
result: it can report that no \(\theta\)-controlled regime was found for
\(100\leq j\leq10{,}000\) A m\(^{-2}\), with a bound on the missing transition. It would, however,
**falsify P3 as written and invalidate the central claim that a wettability closure has a bounded
industrial region whose polarization consequence is mapped**. P1 could remain a molecular result,
but propagating the resulting angle through a cell-scale industrial coverage closure would no
longer be mechanistically justified. Calling this automatically a field-redirecting result is too
strong without experimental validation.

## Q3 — Vogt versus Rox

The measurand-mismatch explanation is **plausible and probably a large part of the discrepancy,
but it has not been demonstrated**. It must not yet be called a resolution.

The numerical comparison itself is correct: Vogt gives 0.148 at 500 A m\(^{-2}\) and 0.225 at
2000 A m\(^{-2}\). The claimed factor of 4–6 is only order-of-magnitude language because Rox's
“nearly fully covered” is not a precise steady-state number in the anchor. Rox reports a transient
time to maximal projected coverage, has a roughly 20% detection floor, up to about 50% timing
uncertainty, and explicitly includes detached bubbles in the viewing volume. Vogt concerns an
adhering-bubble surface fraction. Porosity, roughness/ECSA, projected versus true area, and current
normalization can all change the comparison; they do not merely add measurement noise.

The following analysis would settle whether a real physical discrepancy remains:

1. Define and report three quantities on the same time base: projected coverage by all visible
   bubbles; projected coverage by attached bubbles only; and true wall-contact area divided by
   true/ECSA or geometric area, with both denominators retained.
2. Reprocess synchronized high-speed top and side views, or another depth-resolving measurement,
   so detached bubbles can be excluded using contact-line/depth criteria. Quantify segmentation
   uncertainty rather than treating “nearly full” as 1.
3. Measure the porous electrode's geometric area, roughness factor/ECSA, pore morphology, and the
   exact basis of reported current. Repeat on a smooth Ni control under matched KOH, temperature,
   pressure, and flow.
4. Compare cycle-averaged steady statistics and distributions, not the time to first/maximal
   optical coverage. Include the low-current Vogt range in the same apparatus as an internal
   bridge.
5. From simulation, render synthetic top-view images with Rox's field depth, resolution, and
   segmentation, then compare that apparent \(A_{\rm cov}\) with the known attached contact area.
   A smooth, axisymmetric, single-bubble wedge cannot by itself perform this porous-electrode
   reconciliation; it needs either representative porous geometry and a bubble population or an
   experimentally constrained observation model.

If the harmonized attached-wall measure remains near unity while Vogt predicts 0.15–0.22, then the
disagreement is real and likely reflects porous-electrode nucleation/population physics or
extrapolation of Vogt. Until this analysis is done, neither “Vogt is refuted” nor “the discrepancy
is explained” is supported.

## Q4 — Can the MD plan provide a usable contact angle?

**No—not the macroscopic advancing/receding underwater-gas angle required by the continuum model.**
The present plan could, after correction and force-field validation, estimate an intrinsic
equilibrium angle for an idealized surface. That is a different observable.

The principal problems are:

- **Wrong line-tension geometry.** The modified Young expression is dimensionally sound for a
  circular contact line, but a periodic quasi-2D cylinder has straight contact lines with zero
  in-plane curvature. Its line free energy per unit cylinder length does not generate the stated
  \(\tau/(\gamma R)\) correction. Cylindrical droplets are normally used to suppress this
  correction, not measure it.
- **The largest cap does not fit.** An \(R=8\) nm base has a 16 nm diameter before adding liquid
  buffer, so it cannot fit in a 5 nm lateral dimension. Giving the R=3, 5, and 8 nm cases the same
  approximately 120k atoms is not geometrically credible. A spherical cap would require both
  lateral dimensions to grow; even a cylinder requires one to grow substantially. Periodic-image
  and opposing-wall effects must be converged.
- **The extrapolation is underdetermined as a validation exercise.** Three radii fit two
  parameters with only one residual degree of freedom. Over 3–8 nm, interface thickness,
  curvature-dependent surface tension, disjoining pressure, and finite-box effects can all mimic a
  \(1/R\) trend. Independent seeds and at least one out-of-fit larger size are needed.
- **Equilibrium is not advancing/receding.** A static cap on atomically flat Ni(111) supplies one
  Young angle and essentially no realistic pinning hysteresis. The required continuum input is
  \(\theta_a\) and \(\theta_r\), normally with contact-line-speed dependence. Flow, roughness,
  oxide/hydroxide state, adsorbates, and surface defects dominate that hysteresis at 50–100
  micrometres.
- **The phase and potential definitions are incomplete.** The calculation must use an H2 gas
  bubble under KOH and report the angle using the same through-phase convention as OpenFOAM; a
  water droplet in vapor is not interchangeable without a carefully demonstrated transformation.
  The relevant control variable is the individual electrode potential relative to a physical
  reference/PZC, not merely the voltage difference between two slabs.
- **Classical chemistry limits the claim.** Lack of Grotthuss transport is not fatal for a strictly
  equilibrium angle, but it matters for dynamic EDL/concentration response. More seriously, a
  nonreactive SPC/E + classical-ion + clean-Ni force field cannot change Ni oxidation,
  hydroxylation, specific adsorption, or bond chemistry with potential. `fix electrode/conp`
  makes the metal charge responsive; it does not make the interface chemically reactive.

The minimum defensible change is to narrow the MD claim and change the coupling:

1. Use a direct underwater H2 bubble. Either use a properly sized **spherical cap** and a
   circular-contact-line finite-size analysis, or retain a cylinder and treat it as an estimate of
   the planar equilibrium angle without the spherical \(1/R\) line-tension fit.
2. Converge box size, film thickness, surface tension, and surface termination; reference electrode
   potential to PZC; and add independent replicas.
3. Pass only the intrinsic equilibrium angle or its potential-induced shift from MD. Obtain
   macroscopic \(\theta_a,\theta_r\) from matched experiment/literature and use a stated dynamic
   contact-angle law, with MD informing its equilibrium center rather than pretending to supply
   its hysteresis.

If the continuum angles must be entirely MD-derived, the minimum is no longer a small correction:
nonequilibrium advancing/receding simulations on representative rough, hydroxylated/oxidized Ni at
several contact-line speeds are required to parameterize a dynamic law. That is a materially
different and more expensive MD project.

## Q5 — Budget realism

The CSV arithmetic is internally correct: 96 active cases sum to 1742 nominal wall-hours, split as
1522 h MD, 164 h VOF/VOF3D, and 56 h cell scale. Priorities 0–3 sum to the quoted 1230 h. The inputs
to that sum are not credible.

### The decisive MD unit-conversion error

At 685 katom-step/s, the number of timesteps per second is \(685{,}000/N\). Thus:

| Atoms | Correct ns/day at 1 fs | Correct ns/day at 2 fs |
|---:|---:|---:|
| 50k | 1.184 | 2.367 |
| 100k | 0.592 | 1.184 |
| 150k | 0.395 | 0.789 |

This is consistent with the reported 3.70 ns/day for the 32k-atom rhodo benchmark and directly
contradicts the stated 10–28 ns/day for larger systems. After a 2–4x `fix electrode` slowdown, the
50–150k range is only about **0.20–1.18 ns/day at 2 fs**, or **0.10–0.59 ns/day at the specified
1 fs**.

For a nominal 120k-atom contact-angle case, the corrected 2 fs rate after that slowdown is
0.247–0.493 ns/day. Therefore 20–50 ns needs about **41–203 days per state point**. At 1 fs it is
about **81–406 days**. Each such row is budgeted for 72 h. The 12 primary contact-angle rows alone
therefore require at least about 487 serial days under the most favorable stated assumptions,
versus 36 days in the CSV, before replicas or the larger box required by R=8 nm. The 51-day critical
path is not recoverable by a modest contingency factor.

Other optimistic assumptions are material:

- The rhodo benchmark does not contain slab electrostatics, 2000 constant-potential atoms, the
  production neighbor environment, or the enlarged R=8 geometry. The overhead may be size
  dependent rather than a constant factor.
- Eight hours is unlikely to support converged Green–Kubo viscosity plus three diffusivities in
  concentrated KOH. Differential capacitance and angle uncertainty also need replicas and longer
  equilibration than the matrix records.
- The axisymmetric VOF base mesh has only about 3900 cells per rank on 16 ranks, not the stated
  greater-than-10k production cells/rank. The assumed 350k cell-step/s is extrapolated from a
  different dam-break solver workload and omits species transport, variable surface tension,
  AMR, contact-line treatment, and nonlinear convergence.
- Giving every VOF campaign case 1.5 h assumes every case reaches the required statistic in 10 ms.
  For a fixed departure volume, a Faradaic lower-bound scaling gives growth time proportional to
  \(1/j\); the 100 A m\(^{-2}\) cases can take roughly 100 times longer than 10,000 A m\(^{-2}\)
  cases. Coverage needs multiple cycles, not merely first departure.
- Equal 6 h budgets for 4, 2, and 1 micrometre meshes ignore both cell-count and capillary-timestep
  scaling. In a 2D wedge, halving \(\Delta x\) increases cell-steps by roughly
  \(2^2\times2^{3/2}\approx11.3\) before solver effects.
- Conversely, retaining 360 h for a 4 micrometre, approximately 2M-cell 3D case does not follow
  from the same benchmark scaling unless an unstated large solver penalty is included. The budget
  is not using one consistent cost model.
- No allowance is visible for failed starts, equilibration discarded from production, independent
  seeds, checkpoint/restart, analysis, or model rework after verification failures.

### What to cut or redesign first

1. Keep `MD-000-overhead` as a hard gate, but benchmark the actual 120k geometry and the feasible
   largest geometry at both 1 and 2 fs. Do not launch another MD row until ns/day, memory, and
   equilibration length are measured.
2. Cut all six priority-6 concentration/temperature OFAT contact-angle cases first (432 nominal
   hours). They add breadth but do not rescue P1 or the continuum coupling.
3. Replace the 12-case “three sizes at every potential” block with a sequential design: screen the
   physically referenced potential dependence at one feasible, box-converged geometry with
   independent replicas; run size scaling only at zero potential and at the largest statistically
   established shift. Stop if the force field or effect fails its gate. Do not cut validation or
   replicas to preserve an oversized matrix.
4. Replace the VOF OFAT cross with an initial identifiable grid, for example
   \(j=\{100,500,2000,10000\}\), \(v=\{0,0.05,0.2\}\), and
   \(\theta=\{30,90,150\}^\circ\), then refine only near a force-ratio transition. This is 36
   interaction-resolving cases rather than 48 non-identifying slices. Give each case a
   physics-based end time rather than a uniform 1.5 h.
5. Defer the Riegel legacy run and the 3D case until the main closure and force decomposition pass.
   A single coarse 3D case at \(j=2000\), \(v=0.05\), \(\theta=60^\circ\) is not a corner and cannot
   demonstrate that axisymmetry is harmless. At least two deliberately contrasting 3D cases are
   needed before making that claim.

The cheap cell-scale runs need not be cut for cost, but they should not run until the closure's
domain and current/coverage conventions are frozen.

## Q6 — Standing questions

### (a) What a hostile Reviewer 2 will attack first

The first attack will be that the alleged multiscale link is not physically the quantity used by
the continuum model: an equilibrium nanocap angle on ideal Ni(111) is being promoted to a dynamic
advancing/receding angle for a rough, chemically evolving, porous electrode under flow. The next
attack will be that a single axisymmetric bubble with no explicit nucleation-site population or
coalescence model cannot derive electrode coverage. Together these challenge the central word
“derived,” not merely a parameter choice.

### (b) Result most likely to be a numerical artefact

The most likely artefact is the extrapolated \(\theta_\infty(\Delta\Psi)\): the proposed
\(1/R\) relation is being applied to the wrong contact-line geometry, the largest radius does not
fit the stated box, and only three sizes with no replicas are planned. An apparent P3 boundary is a
close second because axisymmetry suppresses lateral motion, the contact-angle wall treatment can
set departure, and the current OFAT matrix confounds Marangoni, shear, and angle effects.

### (c) Claims stronger than the evidence

- The central block quote is presently a **hypothesis**, not a claim: no result yet shows that the
  T12 closure changes industrial polarization by more than empirical-model spread.
- “Potential-aware molecular contact angle” overstates what a classical constant-potential metal
  plus nonreactive water/ion force field establishes. It is a model-potential-dependent intrinsic
  angle unless validated against surface chemistry and macroscopic data.
- “The applicability map” is not supported by a matrix that cannot estimate the relevant
  interactions and by a specification that does not yet state a Marangoni constitutive law.
- One coarse 3D run cannot demonstrate or bound the effect of axisymmetry on coverage, lateral
  motion, or coalescence.
- Extracting two image measures from the current smooth axisymmetric VOF case will not by itself
  “resolve” the Rox/Vogt porous-electrode discrepancy.
- A negative model result showing Marangoni dominance would bound this model's wettability domain;
  without external validation it would not by itself “redirect the field.”

## Required disposition before Phase 2/3 production

I recommend a **major revision / no-go for the current matrix**. Production should be gated on:

1. correction of equations (2)–(3) and the geometric/local-current gas-flux convention;
2. a measured production-geometry MD rate and a rebuilt wall-time budget;
3. a geometrically valid, box-converged bubble-angle protocol with a defensible dynamic-angle
   coupling or a narrowed equilibrium-only claim;
4. an explicit and verified \(\sigma(c)\), Marangoni-stress, and all-force decomposition; and
5. an interaction-resolving/adaptive VOF design with operational definitions of coverage,
   departure, stationarity, and falsification thresholds.

These changes do not kill the study. They change it from an overclaimed, underbudgeted chain into
a testable one.
