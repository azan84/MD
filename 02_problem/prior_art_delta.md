# PRIOR-ART DELTA — what T12 may and may not claim
Required by execution brief §1.4. Written **before** any result exists, so the novelty framing
cannot be retro-fitted to whatever the simulations happen to produce.

---

## 1. The paper that falsified GAP-X-01 as a field-wide claim

**H. Zhang, Y. Ma, M. Huang, G. Mutschke, X. Zhang, "Solutal Marangoni force controls lateral
motion of electrolytic gas bubbles", *Soft Matter* **20**(14) 3097–3106 (2024),
DOI `10.1039/D3SM01646C`.**

**Verified content** (RSC returns HTTP 403 to automated fetch; content confirmed via indexed
abstract, and the DOI/volume/pages resolve correctly):
- It **combines molecular dynamics with continuum fluid dynamics** for **electrolytic gas bubbles**.
- It identifies a lateral **solutal Marangoni force** arising from an asymmetric distribution of
  dissolved gas around the bubble.
- **Both MD and CFD deliver a similar force magnitude, ~0.01 nN.**
- It analyses lateral bubble oscillations and dynamic self-pinning at the electrode boundary.

**Claim I could NOT verify and therefore do not rely on:** that the CFD takes bubble morphology
(location, base radius, contact angle) *from* the MD data. This was asserted in the pre-execution
audit but the paywall blocked confirmation. It is marked `[UNVERIFIED — trace pending]` and
**nothing in T12's framing depends on it either way**.

### What this closes, and what it leaves open

| | |
|---|---|
| **Closed.** "No study passes a molecular-scale result into a continuum model of electrolytic bubbles" is **false as a field-wide statement.** | It is true only *within the 26-paper corpus*, and must always be written that way. |
| **Open.** The Soft Matter study is a **single-bubble force analysis**. It derives **no bubble-coverage closure**, addresses **no electrode-scale or cell-scale model**, and produces **no polarisation prediction**. | T12's target — a wettability-dependent coverage closure Θ(j, v, θ) propagated to cell polarisation — is untouched by it. |

**Consequence for the manuscript:** T12 must never claim to be the first to couple MD to continuum
for electrolytic bubbles. Zhang et al. (2024) is cited early, explicitly, and as *precedent for the
coupling being physically meaningful* — which strengthens T12's method rather than threatening it.

---

## 2. The Marangoni literature is active, and it is the principal threat to a θ-only closure

The Phase 1 sweep surfaced a coherent and current body of work — largely HZDR/TU Dresden and
Twente — establishing that solutal Marangoni convection materially governs electrolytic bubble
behaviour:

| Work | Relevance |
|---|---|
| "Solutal Marangoni effects on growing hydrogen **and oxygen** bubbles in **alkaline water electrolysis**", *Chem. Eng. Sci.* (S0009250925004002) | Directly alkaline; directly on growth |
| "Solutal Marangoni convection at growing oxygen bubbles during water electrolysis", *Phys. Rev. Research* **7** 023189 | Mechanism |
| "Marangoni forces on electrolytic bubbles on microelectrodes", *Electrochim. Acta* (S0013468624007503) | Force magnitudes |
| "Numerical simulation of Marangoni flow around a growing hydrogen bubble on a microelectrode", *Electrochim. Acta* (S0013468623016298) | Prior CFD |
| "Minimum current for detachment of electrolytic bubbles", *J. Fluid Mech.* | Departure criterion is **current-dependent**, not purely capillary |
| "Solutal Marangoni effect determines bubble dynamics during electrocatalytic hydrogen evolution", *Nat. Chem.* `10.1038/s41557-023-01294-y` | High-profile statement of the mechanism |

**Reading this honestly:** a closure in which departure radius is set by contact angle alone is
**already known to be wrong** in the regime where Marangoni dominates. The last title is close to
a direct contradiction of a θ-only framing.

**This does not kill T12 — it fixes its scope, and the fix was already mandated** by execution brief
§4.2, which requires quantifying the capillary:Marangoni force ratio and producing an
**applicability map** of θ-controlled vs Marangoni-controlled regimes.

**Therefore the applicability map is promoted from a supporting figure to a primary deliverable.**
A closure with an honestly bounded validity envelope, and a map showing where it applies, is
defensible. A closure claiming universality is not, and would be refuted by the table above at the
first review round.

---

## 3. Measured coverage at industrial current density exists — the gap is in the modelling

Confirmed pre-execution and reinforced here: Kitajima et al. (*Electrochim. Acta* **502** 144772,
2024) at 1–2 A/cm², Hammons et al. (*Nano Lett.*, `10.1021/acs.nanolett.4c03657`), and now
**Rox et al. (arXiv:2209.11550)** at 100–2000 A/m² on **porous nickel** (anchor A1).

**T12 must not claim "no coverage data exists at industrial current density."** The defensible
claim is narrower and still true:

> No open-source continuum coverage closure has been re-derived from resolved interface simulation
> and validated against modern measured coverage, and no cell-scale model propagates a
> wettability-dependent closure to a polarisation prediction.

---

## 4. The claims T12 is permitted to make

Each is falsifiable, and none is contradicted by anything found above.

1. **A wettability-dependent coverage closure Θ(j, v, θ) derived from interface-resolved simulation
   rather than fitted to legacy low-current data**, with contact angle supplied by
   potential-aware MD rather than assumed. *(Delta vs Li 2024/E08: E08 constructs coverage
   analytically via Fritz + Faraday counting with an assumed θ; T12 measures it from a resolved
   interface with a computed θ.)*
2. **An applicability map** in (j, v, θ) separating the θ-controlled regime, where a wettability
   closure is valid, from the Marangoni-controlled regime, where it is not. *(No located work
   provides this boundary explicitly.)*
3. **The cell-scale consequence**: ΔV_cell(j) between the legacy Vogt closure and the derived
   closure, in a fully open-source stack. *(Delta vs Jacobsen/E04: E04 compares empirical closures
   against each other; none is derived from below.)*
4. **Resolution of the measurand mismatch** between adhering-bubble coverage (Vogt-type) and
   projected-area coverage (Rox-type), which differ by ~4–6× at the same current density
   (anchor A1). *(This tension is currently unaddressed in anything located.)*

## 5. Claims that are now forbidden

- ❌ "First to pass MD into continuum for electrolytic bubbles" — Zhang et al. 2024.
- ❌ "No measured coverage exists at industrial current density" — Kitajima, Hammons, Rox.
- ❌ "Contact angle controls bubble departure" as an unqualified statement — the Marangoni
  literature contradicts it outside the map's θ-controlled region.
- ❌ "The two coverage paradigms are unreconciled" — downgraded to WEAK pre-execution; both
  auditors supplied the reconciliation.
- ❌ Any unscoped gap claim. Every gap sentence reads *"within this corpus"* or cites a check
  performed here.
