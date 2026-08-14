# MACHINE BENCHMARK — measured, 2026-08-14

Per standing order §2.1 G: **every run-matrix size in later phases is justified against these
measured numbers, not assumed.** All figures below were produced on this machine today.

## Hardware as actually available

| | |
|---|---|
| Logical cores | 32 (16 physical) |
| RAM available to WSL2 | **23 GB** — the binding constraint |
| Disk free | 59 GB (hard-stop threshold 40 GB — **19 GB of headroom, must be monitored**) |
| GPU | **NOT AVAILABLE.** `nvidia-smi` absent; CUDA is not exposed to this WSL2 instance |

The RTX 3090 is unusable from this environment. LAMMPS is built CPU-only. Note this would have
changed little for rev B in any case: `fix electrode` solves the constant-potential matrix on CPU,
so the GPU would have accelerated pair styles only.

## LAMMPS — official `bench/in.rhodo` (32k atoms, PPPM + SHAKE + NPT, 500 steps)

Chosen because it exercises the same code paths as the T12 MD campaign (long-range electrostatics,
constrained water, thermostatted dynamics) and is comparable to published LAMMPS numbers.

| Ranks | Loop time | Throughput | ns/day |
|---|---|---|---|
| 8 | 37.91 s | 422 katom-step/s | 2.28 |
| 16 | 23.36 s | **685 katom-step/s** | 3.70 |

**Parallel efficiency 8→16 ranks: 1.62× (81%).** Acceptable; PPPM communication limits it.

### What this implies for the MD campaign
A representative Ni | KOH(aq) | Ni cell with an H₂ nanobubble is ~50–150k atoms. At 685
katom-step/s that is **~5–14 M steps/day**, i.e. **10–28 ns/day at 2 fs**.

**Critical correction to that estimate:** `fix electrode/conp` adds a constant-potential solve every
step. With ~2000 electrode atoms the elastance-matrix application is substantial and is *not*
represented in the rhodo benchmark. **Assume 2–4× slowdown until measured**, giving **~3–14 ns/day**.
A contact-angle run needing 20–50 ns is therefore **2–15 days per state point** — which alone
justifies the staged plan and forbids a naive full-factorial MD matrix.

**Action carried to Phase 3:** measure the `fix electrode` overhead directly on the real system as
the first MD task, before committing the matrix. Prefer `electrode/conq` or a reduced electrode-atom
count if the overhead exceeds 4×.

## OpenFOAM interFoam — damBreak

| Case | Cells | Steps | Ranks | Wall | Peak RSS | Throughput |
|---|---|---|---|---|---|---|
| coarse | 2 268 | 500 | 1 | 7.15 s | 66 MB | 159 k cell-step/s |
| fine | 36 288 | 18 | 1 | 9.34 s | 130 MB | 70 k cell-step/s |
| fine | 36 288 | 19 | 8 | **2.70 s** | 76 MB | **255 k cell-step/s** |

**Parallel efficiency 1→8 ranks: 3.46× (43%)** at 36k cells — communication-bound at only ~4.5k
cells/rank. Efficiency will improve substantially at the ≥10k cells/rank the production cases use.

**Marginal memory ≈ 2 kB/cell** (130 MB − 60 MB baseline over 36 288 cells).

### What this implies for the VOF campaign — the decisive calculation

Memory ceiling: 23 GB / 2 kB per cell ≈ **10 M cells absolute**, ~**5 M cells practical** with
headroom for decomposition and I/O.

Resolving a contact line on a 50–100 µm departing bubble needs Δx ≈ 1–2 µm.

| Option | Cells | Steps to departure | Cell-steps | Wall @ ~350 k cell-step/s (16 ranks) |
|---|---|---|---|---|
| **3D** 0.5 mm cube @ 2 µm | **15.6 M** | ~3 × 10⁴ | 4.7 × 10¹¹ | **~15 days/case — INFEASIBLE** |
| **2D axisymmetric wedge** 0.5 × 0.5 mm @ 2 µm | **62 500** | ~3 × 10⁴ | 1.9 × 10⁹ | **~1.5 h/case — FEASIBLE** |

Capillary timestep limit: Δt ≈ √(ρΔx³/σ) = √(1000·(2×10⁻⁶)³/0.072) ≈ **3.3 × 10⁻⁷ s**, so ~3 × 10⁴
steps reaches ~10 ms of physical growth.

### Ruling carried into Phase 1 design
**The parametric VOF campaign is axisymmetric.** A 100-case sweep in (j, v, θ) costs ~150 h ≈ 6 days
of continuous 16-rank running — affordable. A 3D sweep is not, by a factor of ~250.

A small number (≤3) of 3D confirmation cases will be run at selected corners to demonstrate the
axisymmetric assumption does not change the coverage conclusion; those are budgeted at ~15 days
each and will be **coarser** (Δx 4 µm, ~2 M cells) to fit, with that compromise stated.

This is the measured, quantitative answer to the pre-execution audit finding that the VOF campaign
"is not computationally credible as described". It is credible **axisymmetrically**, and is not
credible in 3D — so the design changes rather than the claim.

## Disk budget

59 GB free against a 40 GB hard stop. LAMMPS source + build consumed ~3 GB. VOF campaign output is
the main risk: 100 axisymmetric cases × ~30 write times × ~5 MB ≈ 15 GB if unmanaged.
**Mitigation, adopted now:** write only the fields needed for coverage extraction, use
`writeControl adjustableRunTime` with coarse intervals, and archive/compress each case on
completion. Monitor in the QC script.
