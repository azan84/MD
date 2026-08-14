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

## Phase 1

**D1.1 — Soft Matter 2024 paywalled; proceeded on verified abstract only.**
RSC 403s automated fetch. The core fact (MD + CFD combined for electrolytic gas bubbles, ~0.01 nN
Marangoni force from both) is confirmed and is enough to scope the novelty. The unverifiable detail
(whether contact angle specifically is passed) is marked UNVERIFIED and T12's framing is written so
it does not matter either way — the delta rests on *coverage closure + cell scale*, which that paper
does not address on any reading.

**D1.2 — Applicability map promoted to a primary deliverable.**
The prior-art sweep found a substantial, current Marangoni literature including a *Nature Chemistry*
paper stating the solutal Marangoni effect *determines* bubble dynamics in HER. A θ-only closure is
therefore already contradicted somewhere in the envelope. Rather than defend a universal closure,
T12 will map where θ control holds and where it does not. This converts the field's strongest
counter-argument into the study's second result.

**D1.3 — 3D confirmation cut from 3 cases to 1, run to first departure only.**
Generated budget showed 3 × 360 h = 1080 h — 92% of the VOF stage for 3 cases. One corner, run to
first departure (~1–2 ms rather than 10 ms), tests the axisymmetry assumption at ~7% of the cost.
Total active budget fell from 2750 h to 1742 h; critical path 1230 h (51 days). The other two
corners are marked `deferred`, not deleted, so the maintenance loop (§9) can pick them up if time
allows.

**D1.4 — MD matrix is OFAT, not full-factorial.**
At 685 katom-step/s before the unmeasured `fix electrode` overhead, a state point is 2–15 days. A
full factorial over (ΔΨ, c, T, R) is impossible. Only the ΔΨ axis — on which prediction P1 depends —
runs at full resolution with 3 sizes for line-tension extrapolation. Concentration and temperature
are single-factor arms at priority 6, truncatable without losing P1.

**D1.5 — Rox 2022 adopted as an anchor despite its stated limitations.**
Its ~20% resolution floor, ±50% timing uncertainty and detached-bubble contamination are real, and
are recorded in the anchor file. It is still the only open-access measured-coverage dataset located,
the only one on porous Ni, and it spans 100–2000 A/m². Used as a *secondary* anchor for the porous
arm, never as the sole basis for a claim.
