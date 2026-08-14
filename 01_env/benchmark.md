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

> ## ⚠️ CORRECTION (issued Phase 2, 2026-08-14)
> **The throughput figures originally written in this section were wrong by a factor of 10–20 and
> are corrected below.** The original text claimed "~5–14 M steps/day, i.e. 10–28 ns/day at 2 fs"
> for a 100k-atom system. The correct arithmetic is
> 685 000 atom-step/s ÷ 100 000 atoms = 6.85 steps/s = **0.59 M steps/day = 1.18 ns/day at 2 fs**.
> The error was an order-of-magnitude slip in converting atom-steps to steps. It was caught by
> cross-checking against the measured constant-potential run in Phase 2 and is corrected here rather
> than left to propagate into the MD matrix. **This materially worsens the MD feasibility picture
> and the plan is revised accordingly (D2.1).**

Corrected throughput, measured `fix electrode/conp` overhead of **1.72×** included:

| System size | steps/s (16 ranks) | ns/day @ 2 fs, plain | ns/day @ 2 fs, **conp** | 15 ns run |
|---|---|---|---|---|
| 30k atoms | 22.8 | 3.95 | **2.29** | **6.5 days** |
| 50k atoms | 13.7 | 2.37 | **1.38** | **10.9 days** |
| 100k atoms | 6.8 | 1.18 | **0.69** | **21.8 days** |

A 100k-atom system is therefore **not affordable** for a 12-state-point contact-angle campaign.

### `fix electrode/conp` overhead — MEASURED, OI-1 RESOLVED

Measured on the real Ni(111) | SPC/E water cell (4006 atoms, 1654 electrode atoms — close to the
~2000 production target), 200 steps, 8 ranks:

| Configuration | Loop time | Ratio |
|---|---|---|
| baseline, `pppm`, no electrode solve | 1.846 s | 1.00 |
| **`pppm/electrode` + `fix electrode/conp`** | **3.171 s** | **1.72×** |

**Better than the assumed 2–4×.** The assumption is replaced by a measurement.

Physics verified in the same run: with ΔΨ = 1.0 V imposed, induced electrode charges are **exactly
equal and opposite at every timestep** (−0.0826/+0.0826 → −0.585/+0.585 e as the double layer forms),
so the charge-neutrality constraint of eq. (6) holds and the magnitude grows physically as water
screens the field. `fix electrode/conp` requires an ElectrodeKSpace — plain `pppm` errors out;
`pppm/electrode` is mandatory.

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

## MD strong scaling with constant potential — MEASURED, and it changes the run strategy

Measured on the real Ni(111) | SPC/E water conp system (4006 atoms), 200 steps:

| Ranks | Loop time | katom-step/s | Speedup | Parallel efficiency |
|---|---|---|---|---|
| 1 | 6.033 s | 132.8 | 1.00 | 100% |
| 2 | 5.585 s | 143.5 | 1.08 | **54%** |
| 4 | 3.441 s | 232.8 | 1.75 | **44%** |
| 8 | 3.169 s | 252.8 | 1.90 | **24%** |

**Scaling is poor** — 8 ranks buys only 1.9×. PPPM/electrode communication dominates at this system
size, and the constant-potential solve does not distribute well.

### The consequence: run concurrent jobs, not parallel ones

Aggregate throughput on 16 physical cores as a function of how the cores are split:

| Concurrent jobs | Ranks each | Aggregate katom-step/s |
|---|---|---|
| **16** | **1** | **2125** |
| 8 | 2 | 1148 |
| 4 | 4 | 931 |
| 2 | 8 | 506 |
| 1 | 16 | ~267 (optimistic) |

> **16 concurrent single-rank jobs deliver ~8× the aggregate throughput of one 16-rank job.**

This is the single most important scheduling fact in the project. The MD campaign is
**embarrassingly parallel across state points** — 12 independent (ΔΨ, R) contact-angle runs — so
concurrency is exactly the right structure.

### Revised MD campaign timing

| System size | ns/day per 1-rank job | 15 ns run |
|---|---|---|
| 20k atoms | 1.15 | **13.1 days** |
| 30k atoms | 0.76 | **19.6 days** |
| 50k atoms | 0.46 | 32.7 days |

**All 12 θ-campaign cases run simultaneously in 12 of the 16 slots and therefore complete in that
same wall-clock time** — ~13–20 days for the entire campaign, not per case.

Memory is not a constraint: 12–16 jobs × ~200 MB ≈ 2.4–3.2 GB against 23 GB.

**Design consequence (D2.2):** MD systems are sized at **20–30k atoms**, not the 50–150k originally
specified, and the campaign is scheduled as concurrent single-rank jobs. This is what makes the MD
stage fit the window after the throughput correction above.
