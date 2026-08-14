# ANCHOR A1 — Rox et al. 2022, measured coverage on porous nickel

**Citation.** H. Rox, A. Bashkatov, X. Yang, S. Loos, G. Mutschke, G. Gerbeth, K. Eckert,
"Bubble size distribution and electrode coverage at porous nickel electrodes in a novel 3-electrode
flow-through cell", **arXiv:2209.11550v2** [physics.flu-dyn], 28 Oct 2022.
HZDR Institute of Fluid Dynamics / TU Dresden / Fraunhofer IFAM.
**Open access — full text retrieved and read** (`/tmp/.../cov.txt`, 20 pp).

> Found during the Phase 1 prior-art sweep, **not** inherited from the corpus. Same group as
> corpus record E15 (Han/Mutschke) and as the *Soft Matter* 2024 paper that reshaped GAP-X-01.

## Why this matters to T12

It is the closest thing yet found to the measurement GAP-V-09 says is missing, **and** it is on the
electrode type GAP-M-12 says closures are untuned for:

| Requirement | Rox 2022 |
|---|---|
| Coverage measured **directly** | ✅ `A_cov` from top-view imaging + SSIM segmentation |
| **Porous nickel** electrode | ✅ three expanded-Ni cathodes (incl. EM_500) |
| Above Vogt's validated ceiling (104 A/m²) | ✅ **j = 10–200 mA/cm² = 100–2000 A/m²**, up to ~20× above |
| Alkaline | ✅ |
| Flow dependence | ✅ 0 and 5 ml/min |
| Open and reusable | ✅ arXiv |

## What it actually measures — read carefully before use

- `A_cov` develops **over time**; the headline result is the *time to reach maximal coverage*
  vs current density (their Figs. 13, 14), not a steady-state Θ(j) curve.
- **"For current densities |j| ≥ 50 mA cm⁻² the electrode is nearly fully covered in less than
  0.1 s."**
- Forced flow has a **negligible effect** on `A_cov`, and — counter-intuitively — the tendency is
  for the electrode to cover *more rapidly* with flow.

## Stated limitations — carried forward, not hidden

1. **"coverages below A_cov ≈ 20 % could not be resolved"** — low spatial resolution, illumination
   limited. The dataset has a hard floor at ~20%.
2. Camera and electrochemical signal **not synchronised**; the deviation in the reported time `t`
   reaches **≈50%**.
3. Bubbles that have already detached and are rising against the observation window contaminate the
   top view, biasing `A_cov` upward.
4. The authors themselves note their trend "agrees with Faraday's law … and with the studies by
   Vogt for **low** current densities".

## ⚠️ The tension this creates — a headline finding for the manuscript if it survives

Vogt's correlation (corpus E21), Θ = 0.023 (j/[A m⁻²])^0.3, predicts:

| j | Vogt Θ | Rox observation |
|---|---|---|
| 500 A/m² (50 mA/cm²) | **0.15** | "nearly fully covered" |
| 2000 A/m² (200 mA/cm²) | **0.22** | fully covered |

That is a discrepancy of roughly **4–6×** at the same current density.

**Do not report this as a refutation of Vogt without resolving the measurand mismatch**, which is
the obvious referee attack:
- Vogt's Θ is the fraction of the *electrode surface* screened by **adhering** bubbles.
- Rox's `A_cov` is a **projected-area** coverage from a top view of a *porous* electrode, and by
  their own statement includes detached rising bubbles in the field of view.
- A porous expanded-Ni electrode has far more real surface area than its projected footprint, so
  the two quantities are not the same normalisation.

**Action for Phase 4/5:** extract both measurands from the VOF campaign — adhering-bubble surface
coverage (Vogt-comparable) *and* projected-area coverage (Rox-comparable) — and report them
separately. If the model reproduces both, the discrepancy is explained rather than argued about,
and that explanation is a genuine contribution. Logged in `OPEN_ITEMS.md` as OI-6.

## Role assigned

**Secondary validation anchor, porous-electrode arm.** Primary remains Kitajima 2024 / Hammons 2024
(to be retrieved). Rox 2022 is the only *open-access* measured-coverage dataset located so far and
the only one on porous Ni, so it is also the reproducibility-friendly choice for the manuscript.
