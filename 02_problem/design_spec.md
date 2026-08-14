# DESIGN SPEC — numerical experiment design
T12 is a modelling study, so "design" means the design of the numerical experiments. Every size
below is justified against the **measured** throughput in `01_env/benchmark.md`, per §2.1 G.

---

## 1. Scale 1 — MD (LAMMPS)

### 1.1 System
Ni | KOH(aq) | Ni parallel-slab cell, 3D-periodic in x,y with a vacuum gap and slab correction in z
(the geometry `fix electrode` is designed for, and the geometry validated bitwise in Phase 0).

| Component | Specification |
|---|---|
| Electrodes | Ni fcc(111) slabs, a = 3.524 Å, ≥4 layers, ~2000 electrode atoms total |
| Electrolyte | SPC/E water + K⁺/OH⁻ at target molality; H₂ solute for the nanobubble runs |
| Cell size | ~5 × 5 × 12 nm ⇒ **50–150k atoms** |
| Electrostatics | `pppm/electrode` with slab correction, 1e-4 accuracy |
| Constant potential | `fix electrode/conp` between the two slabs, ΔΨ imposed |
| Constraints | SHAKE on water O–H and H–O–H |
| Ensemble | NVT Nosé–Hoover, 1 fs (2 fs only if SHAKE-validated) |

**Water model: SPC/E — explicitly NOT mW/Stillinger–Weber.** Both pre-execution auditors ruled that
coarse-grained monatomic water cannot represent an electrochemical interface: no partial charges,
no ions, no double layer. SPC/E carries explicit charges and supports K⁺/OH⁻ and an EDL.

### 1.2 Contact angle protocol
A **cylindrical (quasi-2D) nanodroplet/nanobubble** on the electrode, density-profile isochore fit
to the cap, with **≥3 base radii** for line-tension extrapolation via the modified Young equation:

`cos θ(R) = cos θ_∞ − τ / (γ_lv R)`

Both a circular-fit and a centre-of-mass estimator are reported, with their spread as an
uncertainty component. **An unextrapolated nanoscale θ fed into a continuum closure is precisely
the move a referee kills**, so the extrapolation is not optional.

### 1.3 Cost control — the binding constraint
`in.rhodo` gives 685 katom-step/s at 16 ranks, so a 100k-atom system runs ~10–28 ns/day **before**
the `fix electrode` constant-potential solve, which is unmeasured and assumed to cost 2–4×
(OI-1). A 20–50 ns state point is therefore **2–15 days**.

**Ruling: the MD matrix is not full-factorial.** It is a one-factor-at-a-time (OFAT) star design
about a base state, with only the ΔΨ axis run at full resolution, since P1 depends on it alone.
Task 3.0 measures the electrode overhead before anything else is committed.

## 2. Scale 2 — VOF (OpenFOAM `interIsoFoam`)

### 2.1 Geometry — axisymmetric, and why
`01_env/benchmark.md` shows a 3D parametric sweep costs ~15 days/case at 15.6M cells, against a
~5M-cell practical memory ceiling on 23 GB. **Infeasible by ~250×.** An axisymmetric wedge at the
same 2 µm resolution is ~62.5k cells and **~1.5 h/case**, so a ~100-case sweep is ~6 days of
continuous running.

| | |
|---|---|
| Domain | 5° wedge, 0.5 mm (r) × 0.5 mm (z) |
| Base mesh | Δx = 2 µm ⇒ ~62 500 cells; AMR at the interface |
| Mesh study | 4 / 2 / 1 µm, Richardson extrapolation, **GCI reported** |
| Timestep | adjustable, capillary-limited, Δt ≈ 3.3 × 10⁻⁷ s at 2 µm |
| Wall BC | `constantAlphaContactAngle` / `dynamicAlphaContactAngle` ← **the single point where MD enters the continuum model** |
| Growth | dissolved-H₂ transport with Henry-law interfacial jump; Faradaic wall flux ṅ = j/(2F) over uncovered area |

3D confirmation: **≤3 cases** at selected corners, coarsened to Δx = 4 µm (~2M cells), to test
whether the axisymmetric restriction changes the coverage conclusion. Budgeted separately, and the
coarsening is stated rather than hidden.

### 2.2 Verification before production
Diffusion-driven growth against the Scriven/Epstein–Plesset similarity solution `R = 2β√t`, which is
the same class of check corpus record E14 uses. **No campaign case runs until this passes.**

## 3. Scale 3 — Cell (OpenFOAM `reactingMultiphaseEulerFoam`)

2D zero-gap / parallel-plate channel with dimensions taken from a named corpus paper (E04
geometry preferred, Riegel channel as the legacy comparability case). Euler–Euler two-fluid with
named drag/lift/wall-lubrication/dispersion closures, mixture turbulence with bubble-induced source,
`∇·(σ_eff ∇φ) = 0` with Bruggeman correction, and the electrode BC carrying **the T12 closure** into
Butler–Velmer via (1 − Θ).

Deliverable: **ΔV_cell(j) between the Vogt closure and the T12 closure** — the headline figure.

## 4. Operating envelope

| Variable | Range | Basis |
|---|---|---|
| j | 10² – 10⁴ A m⁻² | spans E20's validated 21–104, E04's 6000, E26's proposed 1 A cm⁻² benchmark, and anchor A1's 100–2000 |
| c_KOH | 20, 30 wt% | E04 uses 30 wt%; industrial range |
| T | 298, 333, 353 K | 298 for Vogt/A1 comparability; 353 ≈ E04's 91 °C |
| v | 0 – 0.2 m s⁻¹ | E20 validated 0.02–0.25 |
| θ | 30° – 150° | brackets E08's 90–140° sweep and E14's 15/30/45°; MD supplies the physical values |
| ΔΨ | 0 to ±1.0 V | accessible to `fix electrode` without water electrolysis in the classical FF |

## 5. Staging

Ordered so that truncation at any point still leaves a coherent result — the mechanism that
converts the 2.0/10 feasibility score into a manageable risk.

| Stage | Content | Standalone output |
|---|---|---|
| **S-A** | MD: overhead measurement → bulk KOH validation → interface/EDL → θ(ΔΨ, c, T) with size extrapolation | **Paper 1** |
| **S-B** | VOF: verification → mesh study → axisymmetric campaign → Θ regression + applicability map | closure dataset |
| **S-C** | Cell: mesh study → Vogt vs T12 polarisation → validation | **Paper 2** |
| **S-D** | Sensitivity, 3D confirmation, figures, submission package | both submittable |
