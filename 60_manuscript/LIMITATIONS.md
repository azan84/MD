# LIMITATIONS — maintained continuously, folded into both Discussions

Every item here is stated in the manuscripts. Nothing on this list is hidden.

## Molecular scale
1. **No Grotthuss transport.** Classical OH⁻ cannot hop; hydroxide transport is structurally
   limited. MD viscosity/diffusivity are force-field *validation checks*, and the continuum uses
   experimental KOH transport data (coupling contract §5).
2. **Chemically inert surface.** SPC/E + classical ions + clean Ni(111) cannot represent Ni
   oxidation, hydroxylation, specific adsorption or bond chemistry. `fix electrode/conp` makes the
   metal *charge* responsive, not the interface *chemically* reactive. The reported angle is a
   **model-potential-dependent intrinsic angle**, not a measured electrode wettability. (A1.11)
3. **Equilibrium, not dynamic.** MD supplies the equilibrium angle and its potential shift only.
   Advancing/receding angles and hysteresis come from measured data (corpus E15). (A1.12)
4. **No line-tension extrapolation.** The cylindrical geometry suppresses line tension rather than
   resolving it; box-size convergence replaces the (invalid) 1/R fit. (A1.3)
5. Ideal flat Ni(111); no roughness, defects or sub-surface cavities — which is also why
   `N_site` cannot be derived here.

## Bridge and closure
6. **`N_site` is an external input, not derived.** Only the wettability-dependent factors of
   eq. (29a) are derived. The claim is "the wettability dependence of coverage is derived". (A1.7)
7. **Fritz is a legacy baseline only**, retained to show where it fails, not used as the mechanism.
8. **Closure refuses to extrapolate** outside its validity box — by design, since the study exists
   because a legacy closure was extrapolated ~60×.

## Continuum scale
9. **Axisymmetric campaign.** Lateral bubble motion, coalescence and sliding are not represented.
   Two contrasting 3D corners bound the assumption; they do not eliminate it. (A1.13)
10. **Seeded initialisation.** Bubbles are seeded at 0.85 R_det and the earlier quasi-static growth
    is treated analytically. R_det is still *predicted* by the force balance, not prescribed.
11. **Bruggeman exponent 3/2** is a baseline for isotropic dispersed gas; it is not validated for a
    wall-attached bubble layer or porous Ni, and is carried as a sensitivity parameter. (A1)
12. **Marangoni requires γ(c).** Without the constitutive law of eq. (18a) the Marangoni force is
    identically zero and P3 is untestable. If ∂γ/∂c_H₂ cannot be sourced or computed, **P3 is
    withdrawn rather than reported as a null result**. (A1.5, OI-7)
13. **One Θ, cathode only.** The anode is not modelled.

## Validation
14. **Riegel is legacy comparability only** — channel gas fraction is Faraday-constrained, so
    agreement tests the mass source, not the wall closure.
15. **The Vogt/Rox discrepancy is not resolved**, only characterised. Demonstrating the measurand
    mismatch requires the synthetic-imaging analysis of OI-6, which a smooth axisymmetric single
    bubble cannot fully perform. (A1.10)
16. **Audits to date are single-auditor** while `agy` is unauthenticated (OA-1) — the missing
    perspective is physics-and-modelling, the more consequential one.
