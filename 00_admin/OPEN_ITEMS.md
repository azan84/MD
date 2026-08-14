# OPEN ITEMS — T12 rev B

| # | Item | Raised | Status |
|---|---|---|---|
| OI-1 | `fix electrode/conp` overhead unmeasured | Phase 0 | ✅ **CLOSED** — measured **1.72×** on the real system (better than assumed 2–4×); physics verified via equal-and-opposite induced charges |
| OI-2 | Disk: 59 GB free vs 40 GB hard stop. VOF campaign output could reach ~15 GB unmanaged | Phase 0 | **OPEN** — mitigation defined (sparse writes + per-case archiving); enforce in QC |
| OI-3 | Electrochimica Acta JCR quartile in Electrochemistry unverified (best scope fit, may be Q2) | inherited from gap report | **OPEN — operator action**, not blocking |
| OI-4 | Prior-art delta vs Soft Matter 20(14) 3097 (2024) | Phase 1 | ✅ **CLOSED** — `02_problem/prior_art_delta.md`; 3 claims forbidden. RSC 403s automated fetch so one detail stays `[UNVERIFIED]`, but nothing depends on it |
| OI-5 | Parallel efficiency measured only at 4.5k cells/rank (43%); production sizing assumes it improves at ≥10k cells/rank | Phase 0 benchmark | **OPEN** — confirm during Phase 4 mesh study |
| OI-6 | Vogt/Rox 4–6× coverage discrepancy is **characterised, not resolved**. Needs: both measurands on one time base, detached-bubble exclusion, ECSA/porosity normalisation, and synthetic top-view rendering of the simulation with Rox's optics | Phase 1 / A1.10 | **OPEN** — a smooth axisymmetric bubble cannot fully do this |
| OI-7 | **γ(c_H₂) constitutive law required.** With constant surface tension F_Mar ≡ 0 and P3 is untestable by construction. Need ∂γ/∂c_H₂ from literature or MD (Kirkwood–Buff at two dissolved-gas concentrations) | Phase 2 / A1.5 | **OPEN — GATES the entire P3 branch.** If unobtainable, P3 is withdrawn, not reported as null |
| OI-8 | Marangoni tangential-stress implementation needs an analytic thermocapillary verification before any production case; `interIsoFoam` lacks variable surface tension as standard (custom `wmake` required) | Phase 2 / A1.5 | **OPEN** — case `VOF-000b-thermocap` added as a gate |
| OI-9 | `N_site` (nucleation-site density) is an external input. Source and its uncertainty must be declared before the closure's absolute level is reported | Phase 2 / A1.7 | **OPEN** |
| OI-10 | j=100 A/m² anchor cases cost 194 h each (46% of the VOF budget for 3 cases). First candidate for cutting if schedule slips | Phase 2 | **OPEN — watch** |
