# DECISIONS — T12 rev B execution

Every judgement call, with a one-line rationale. Standing order S1/S2: decisions are made and
logged, never escalated for approval.

## Phase 0

**D0.1 — sudo unavailable; proceeded without it rather than declaring a hard stop.**
`sudo apt-get` failed (no tty/password). Hard-stop rule S3.2 covers credentials the environment
does not hold, but sudo proved unnecessary: g++ 11.4, mpicc with headers, `fftw3.h`, BLAS and pip
were all already present. LAMMPS was configured with `CMAKE_INSTALL_PREFIX=$HOME/.local` and
everything else installed to user prefixes. Escalating here would have stalled the run for nothing.

**D0.2 — LAMMPS built CPU-only.**
`nvidia-smi` is absent, so CUDA is not exposed to this WSL2 instance and `PKG_GPU` was dropped.
Cost is low: `fix electrode` performs the constant-potential matrix solve on CPU in any case, so the
GPU would only have accelerated pair styles. MD wall-time estimates in `01_env/benchmark.md` are
CPU-based accordingly.

**D0.3 — `virtualenv` instead of `python3 -m venv`.**
`ensurepip` is missing and `python3.10-venv` needs sudo. `virtualenv` (pip --user) bundles pip and
produces an equally isolated environment, satisfying the brief's "never the system Python".

**D0.4 — packmol built serially.**
`make -j8` fails with `Cannot open module file 'pbc.mod'` — a dependency-ordering bug in packmol's
own Makefile, not a missing prerequisite (gfortran is present). Serial `make` succeeds.

**D0.5 — Benchmarked before sizing anything, and let the numbers overrule the plan.**
The measured interFoam throughput and the 23 GB memory ceiling make a 3D parametric VOF sweep
infeasible by ~250×. Rather than record that as a risk, the design is changed now: **the parametric
campaign is axisymmetric**, with ≤3 coarser 3D confirmation cases. This is the concrete answer to
the pre-execution audit finding that the VOF campaign was "not computationally credible as
described" — it is credible axisymmetrically, and the claim is scoped to match.

**D0.6 — `fix electrode` overhead flagged as unmeasured.**
The rhodo benchmark does not include a constant-potential solve, so MD throughput for the real
system is uncertain by an assumed 2–4×. First task of Phase 3 is to measure it directly before the
MD matrix is committed. Recorded so the estimate is never mistaken for a measurement.
