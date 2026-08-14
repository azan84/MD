# OPEN ITEMS — T12 rev B

| # | Item | Raised | Status |
|---|---|---|---|
| OI-1 | `fix electrode/conp` overhead unmeasured | Phase 0 | ✅ **CLOSED** — measured **1.72×** on the real system (better than assumed 2–4×); physics verified via equal-and-opposite induced charges |
| OI-2 | Disk: 59 GB free vs 40 GB hard stop. VOF campaign output could reach ~15 GB unmanaged | Phase 0 | **OPEN** — mitigation defined (sparse writes + per-case archiving); enforce in QC |
| OI-3 | Electrochimica Acta JCR quartile in Electrochemistry unverified (best scope fit, may be Q2) | inherited from gap report | **OPEN — operator action**, not blocking |
| OI-4 | Prior-art delta vs Soft Matter 20(14) 3097 (2024) | Phase 1 | ✅ **CLOSED** — `02_problem/prior_art_delta.md`; 3 claims forbidden. RSC 403s automated fetch so one detail stays `[UNVERIFIED]`, but nothing depends on it |
| OI-5 | Parallel efficiency measured only at 4.5k cells/rank (43%); production sizing assumes it improves at ≥10k cells/rank | Phase 0 benchmark | **OPEN** — confirm during Phase 4 mesh study |
| OI-6 | Vogt/Rox 4–6× coverage discrepancy is **characterised, not resolved**. Needs: both measurands on one time base, detached-bubble exclusion, ECSA/porosity normalisation, and synthetic top-view rendering of the simulation with Rox's optics | Phase 1 / A1.10 | **OPEN** — a smooth axisymmetric bubble cannot fully do this |
| OI-7 | γ(c) constitutive law required; without it F_Mar ≡ 0 | Phase 2 / A1.5 | **PARTIALLY CLOSED** — agy supplied estimates: ∂γ/∂c_H₂ ≈ −1×10⁻⁴ N m⁻¹ M⁻¹, ∂γ/∂c_KOH ≈ +2.5×10⁻³ N m⁻¹ M⁻¹. Both `[EXTERNAL — verify]`; enough to implement and to run the pilots. Still needs a cited source before publication |
| OI-8 | Marangoni tangential-stress implementation needs an analytic thermocapillary verification before any production case; `interIsoFoam` lacks variable surface tension as standard (custom `wmake` required) | Phase 2 / A1.5 | **OPEN** — case `VOF-000b-thermocap` added as a gate |
| OI-9 | `N_site` (nucleation-site density) is an external input. Source and its uncertainty must be declared before the closure's absolute level is reported | Phase 2 / A1.7 | **OPEN** |
| OI-10 | j=100 A/m² anchor cases cost 194 h each (46% of the VOF budget for 3 cases). First candidate for cutting if schedule slips | Phase 2 | **OPEN — watch** |
| OI-11 | Rate-determining step assumed Volmer (α_app=0.5, 140.1 mV/dec). If Heyrovsky (α_app≈1.5, 46.7 mV/dec) the Θ=0.8 penalty is 32.7 mV not 97.9 mV — a **3× swing in the headline quantity**. Needs justification against measured Ni Tafel slopes in 30 wt% KOH | Audit 1 / N5 | **OPEN** |
| OI-12 | Near-wall double-counting guard: adhering gas must enter Θ only, and join ε_g only on detachment. Must be asserted in QC, not assumed | Audit 1 / N6 | **OPEN — QC assertion to implement** |
| OI-13 | η_conc: eq (5) is OH⁻ mass transfer; eq (5a) is the Nernstian dissolved-H₂ shift (40–80 mV). Manuscript must state which is reported and not sum them without justification | Audit 1 / N4 | **OPEN** |
| OI-15 | Experimental KOH density provenance: values were 20 degC handbook figures mislabelled 298 K. Corrected, but must be pinned to one traceable source (Sipos 2000; Akerlof & Bender 1941) and pre-registered before re-running the gate | D3.8 | **OPEN** |
| OI-16 | No trajectory dumps were written, so g(O_h-O_w) cannot be computed from existing runs. The predicted 2.5-2.6 A first peak (vs experimental 2.77-2.79) is the cheapest confirmation of the diagnosis - add `dump` to future runs | D3.10 | **OPEN** |
| OI-17 | Manuscript Methods stated a finite-size correction was applied when the code did not apply one. Now true, but every other method claim in the manuscript must be re-checked against executing code | D3.7 | **OPEN - audit sweep required** |
| OI-18 | Gate design flaw: a 3% density tolerance is 62% on phi_V at 20 wt% but only 31% at 30 wt%, so the same gate is twice as strict at high concentration. Replace with a phi_V criterion (+/-2 cm3/mol at >=3 concentrations) plus drho/dw and drho/dT | D3.10 | **OPEN** |
