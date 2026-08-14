# STATUS — T12 rev B execution

Running log. One line per action. Newest at the bottom of each phase block.

## Phase 0 — Provision the environment

- 2026-08-14 · Probed environment. Found OpenFOAM v2406 (+2512, +11), Cantera 3.2.0, mpirun, gmsh, cmake, git, ffmpeg. Missing: LAMMPS, packmol, moltemplate, ccache.
- 2026-08-14 · **GPU NOT AVAILABLE** — `nvidia-smi` absent; CUDA not exposed to this WSL2 instance. Decision D0.2: build LAMMPS CPU-only, proceed. Little practical loss — `fix electrode` solves on CPU regardless.
- 2026-08-14 · Created project skeleton at `~/research/T12_MD_wettability_closure`, git init.
- 2026-08-14 · **sudo unavailable** (no tty/password). apt install failed. Decision D0.1: verified every required build dependency already present (g++ 11.4, mpicc + headers, fftw3.h, BLAS, pip); installed to user prefixes instead. **Not a hard stop — sudo was never actually required.**
- 2026-08-14 · Built LAMMPS 22Jul2025-stable from source: CMake Release, MPI+OMP, FFTW3, prefix ~/.local. Packages: ELECTRODE, KSPACE, MOLECULE, RIGID, EXTRA-FIX/PAIR/COMPUTE, MANYBODY, MISC, REPLICA, MC.
- 2026-08-14 · **ELECTRODE VERIFIED**: `electrode/conp`, `electrode/conq`, `electrode/thermo`, `ewald/electrode`, `pppm/electrode` all present. Ran `planar-pppm-ew3dc` example — output matches the shipped 2022 reference log **bitwise across all 10 steps** (induced charges ±0.030912769 → ±0.30912769; percdev −1.4789807). Constant-potential MD is verified correct, not merely installed. Proof archived in `01_env/electrode_proof/`.
- 2026-08-14 · python3-venv unavailable without sudo → used `virtualenv` (D0.3). Installed numpy 2.2.6, scipy 1.15.3, pandas, matplotlib, cantera 3.2.0, ase 3.29.0, MDAnalysis 2.9.0, pyvista 0.48.4, sklearn, pymbar, statsmodels, h5py into `~/venvs/t12`. Cantera Solution build verified.
- 2026-08-14 · packmol built from source (serial `make`; `-j8` breaks its Fortran module ordering — D0.4). moltemplate installed in venv.
- 2026-08-14 · OpenFOAM v2406 verified: interFoam, interIsoFoam, multiphaseEulerFoam, reactingMultiphaseEulerFoam, chtMultiRegionFoam, potentialFoam all present. **`wmake` VERIFIED** — custom libso compiles and links (`libt12SmokeTest.so`). This is the capability T12 needs for the coverage-closure BC and Faradaic source terms.
- 2026-08-14 · Benchmarked. LAMMPS `in.rhodo`: 685 katom-step/s @16 ranks (81% eff. 8→16). interFoam damBreak: 255 k cell-step/s @8 ranks, marginal memory ~2 kB/cell, 43% parallel eff. at 36k cells.
- 2026-08-14 · **Campaign-sizing ruling from measured data** (`01_env/benchmark.md`): 3D VOF parametric sweep is INFEASIBLE (~15 days/case, 15.6M cells vs a ~5M practical memory ceiling). **Axisymmetric sweep is feasible at ~1.5 h/case**, so a 100-case (j,v,θ) matrix costs ~6 days continuous. Design changed accordingly; ≤3 coarser 3D confirmation cases budgeted separately.
- 2026-08-14 · Wrote `01_env/versions.json`, `01_env/benchmark.md`. **PHASE 0 COMPLETE.**

## Phase 1 — Confirm the problem

- 2026-08-14 · Attempted retrieval of Zhang et al., *Soft Matter* 20(14) 3097 (2024) `10.1039/D3SM01646C` — RSC returns **HTTP 403** to automated fetch. Content confirmed via indexed abstract; DOI/volume/pages resolve correctly. Codex's specific claim that CFD morphology/contact angle is taken from MD **could not be verified** and is marked `[UNVERIFIED — trace pending]`; nothing in T12's framing depends on it.
- 2026-08-14 · Wrote `02_problem/prior_art_delta.md`. **Three claims now forbidden**: first MD→continuum coupling for electrolytic bubbles (Zhang 2024); no measured coverage at industrial j (Kitajima/Hammons/Rox); unqualified "contact angle controls departure" (Marangoni literature).
- 2026-08-14 · Prior-art sweep surfaced an **active Marangoni literature** (CES 2025 alkaline; PRR 7 023189; Electrochim. Acta ×2; JFM; *Nat. Chem.* `10.1038/s41557-023-01294-y`). Consequence: **the applicability map is promoted from supporting figure to primary deliverable** — a θ-only closure is already known to fail where Marangoni dominates.
- 2026-08-14 · **NEW VALIDATION ANCHOR FOUND AND RETRIEVED** (not inherited from corpus): Rox et al., arXiv:2209.11550 — measured coverage on **porous expanded-Ni**, **j = 100–2000 A/m²** (up to 20× above Vogt's validated ceiling), alkaline, 0 and 5 ml/min. Open access, full text read. Recorded as `50_validation/anchors/A1` with all stated limitations.
- 2026-08-14 · **Scientific tension identified and recorded**: Vogt predicts Θ ≈ 0.15 at 500 A/m² where Rox reports "nearly fully covered" — a 4–6× discrepancy. Flagged as a **measurand mismatch** (adhering-bubble Θ vs projected-area A_cov on a porous electrode incl. detached bubbles), NOT reported as a refutation. Both measurands will be extracted from the VOF campaign (OI-6).
- 2026-08-14 · Wrote `02_problem/problem_statement.md` with the loss decomposition (eqs 1–5), corpus evidence, the T12 claim, and **three falsifiable predictions P1–P3**. P3 is deliberately written to be losable — Marangoni dominance everywhere would be a publishable negative result.
- 2026-08-14 · Wrote `02_problem/design_spec.md` and generated `parameter_matrix.csv` (98 cases, `stage`/`priority`/`status` columns so it truncates without invalidating what has run).
- 2026-08-14 · **Budget triage (D1.3)**: initial matrix totalled 2750 h; the 3 3-D confirmation cases alone were 1080 h = 92% of the VOF budget. Cut to **one** corner run to first departure only. **Active budget now 1742 h (72.6 d), critical path 1230 h (51.2 d)** — fits the window with margin. VOF stage fell 7× (1172 → 164 h).
- 2026-08-14 · **PHASE 1 COMPLETE.** Audit 1 dispatched.

## Phase 3 (S-A) — MD force-field validation gate

- 2026-08-14 · Wrote `10_md/systems/build_bulk_koh.py`; built 6 bulk systems (20/30 wt% × 3 seeds, ~4.7–4.9k atoms; 206 KOH per 1500 H₂O at 30 wt%). **Replicas, not block averages** — both auditors ruled single-trajectory blocks are not independent samples.
- 2026-08-14 · Wrote `in.bulk_koh` with a **pre-registered PASS gate**: density ≤3%, D(H₂O) ≤30%, D(K⁺) ≤40%. **D(OH⁻) reported but NOT gated** — a single-site classical hydroxide cannot carry Grotthuss transport and is expected to be too slow; that is a declared limitation, not a hidden failure.
- 2026-08-14 · Smoke test 1: lattice start spiked to 436 K. Added `minimize` → discovered LAMMPS **ignores `fix shake` during minimisation** and CG+PPPM managed only 21 iterations in ~2 min. **Replaced with a displacement-capped `nve/limit` + Langevin push** (D3.1). Verified: T 729 K → 331 K by step 1500 with monotonically falling PE, nothing destabilised.
- 2026-08-14 · **Process failure caught:** one file edit reported success but did not reach disk, so a smoke test silently re-ran stale input (with `minimize` still present). Now grepping the actual file after every edit before launch (D3.2).
- 2026-08-14 · Smoke test 3 validated the deck end-to-end: nve/limit → Langevin → NPT → density `ave/time` → NVT transport with MSD and pressure output. All five output streams confirmed writing.
- 2026-08-14 · **EARLY SIGNAL (not yet a verdict):** smoke NPT gave ρ ≈ 1.34–1.36 g/cm³ at 298 K, 30 wt% vs experiment ≈1.29 — **~5% high, outside the 3% gate**. From only 1500 equilibration steps, so not conclusive; production has 70k steps of equilibration before 50k of density production. **Flagged as the likely outcome the gate was built to catch.**
- 2026-08-14 · Wrote `build_interface.py`; built Ni(111)|KOH|Ni(111) systems for box convergence: **Lx = 8/12/16 nm → 19k/30k/41k atoms** (12 nm = 30k hits the revised size target), plus an EDL system with no bubble.
- 2026-08-14 · **A1.4 failure mode made structurally impossible:** the builder refuses a bubble whose diameter exceeds 80% of Lx. Tested — a 5 nm bubble in an 8 nm box is rejected by name. The original spec's 3–8 nm caps in a 2.82 nm box cannot recur.
- 2026-08-14 · **LAUNCHED 12-case validation campaign** (2 wt% × 3 seeds × 2 T) as concurrent single-rank jobs at `nice -n 5`. Core budget honoured: 12 mine + 16 operator's = 28 of 32 logical, **4 free** as instructed. ETA ~7–8 h under shared load.

## Phase 3 — FORCE-FIELD GATE FIRED: **FAIL**

- 2026-08-14 · 12-case campaign completed equilibration (85k–200k steps). `validate_bulk.py` verdict: **OVERALL DENSITY GATE FAIL** at all four state points.

| System | ρ sim (3 seeds) | ρ exp | error |
|---|---|---|---|
| 20 wt%, 298 K | 1.2672 ± 0.0020 | 1.188 | **+6.67%** |
| 20 wt%, 333 K | 1.2367 ± 0.0021 | 1.163 | **+6.33%** |
| 30 wt%, 298 K | 1.4081 ± 0.0048 | 1.290 | **+9.16%** |
| 30 wt%, 333 K | 1.3817 ± 0.0008 | 1.265 | **+9.23%** |

- 2026-08-14 · **The failure is systematic, not statistical** — replica scatter is ±0.002–0.005 g/cm³ against a 0.08–0.12 g/cm³ discrepancy, i.e. the error is 20–60× the seed-to-seed spread.
- 2026-08-14 · **The failure is diagnostic**: error grows with KOH content (6.5% at 20 wt% → 9.2% at 30 wt%), so it scales with ion concentration and implicates the **ion parameters, not the water model**. Corroborated by transport: D(H₂O) at 30 wt%/298 K = 3.28e-10 m²/s, ~7× below neat water — far more suppression than real KOH shows. The electrolyte is over-dense and over-structured.
- 2026-08-14 · **Prime suspect identified**: OH⁻ was modelled as a single LJ site with SPC/E-*oxygen* parameters (σ = 3.166 Å) carrying full −1 charge. A bare oxygen-sized anion at unit charge produces excessive electrostriction. K⁺ (Joung–Cheatham) is well established and is not the first suspect.
- 2026-08-14 · **The θ campaign is NOT launched** — the gate exists precisely to stop this, and it stopped it.
- 2026-08-14 · Launched a 5-point OH⁻ σ-scan at the worst state point (30 wt%, 298 K): σ ∈ {3.4, 3.7, 4.0, 4.3} Å at fixed ε, plus one halide-like point (σ = 4.83 Å, ε = 0.0128 kcal/mol). 12 jobs total, exactly at the allocated budget.
