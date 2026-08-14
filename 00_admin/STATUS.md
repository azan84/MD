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
