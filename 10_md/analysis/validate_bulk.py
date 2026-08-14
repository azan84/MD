#!/usr/bin/env python3
"""MD-1xx bulk KOH validation gate — compare simulated vs experimental properties.

Both Audit-1 auditors made this the gate: if the force field cannot reproduce bulk
KOH properties, it cannot be trusted at an interface, and the contact-angle campaign
must not launch.

PASS criteria (pre-registered, before any result is seen):
  density      : within  3% of experiment
  D(H2O)       : within 30% of experiment  (classical water is known to be imperfect)
  D(K+)        : within 40% of experiment
  D(OH-)       : REPORTED, NOT GATED  -- a single-site classical OH- cannot carry
                 Grotthuss transport, so it is expected to be too slow. Failing this
                 is a known limitation, not a force-field rejection. See LIMITATIONS.

Experimental reference values [EXTERNAL - verify against a cited source before
publication; recorded in OI-14]:
  KOH(aq) density at 298 K: 20 wt% ~ 1.188 g/cm3 ; 30 wt% ~ 1.290 g/cm3
  D(H2O) in pure water 298 K ~ 2.30e-9 m2/s ; falls with KOH concentration
  D(K+) infinite dilution 298 K ~ 1.96e-9 m2/s
"""
import numpy as np, glob, os, re, json, sys

EXP = {
    "density": {(20, 298): 1.188, (30, 298): 1.290, (20, 333): 1.163, (30, 333): 1.265},
    "D_water_neat": 2.30e-9,
    "D_K_inf": 1.96e-9,
}
GATE = {"density": 0.03, "D_water": 0.30, "D_K": 0.40}


def msd_slope(path, t_lo_frac=0.3, t_hi_frac=0.9):
    """Einstein fit over the linear window; returns D in m^2/s."""
    d = np.loadtxt(path, comments="#")
    if d.ndim != 2 or len(d) < 20:
        return None, None
    t_fs, msd_A2 = d[:, 0], d[:, 1]
    n = len(t_fs)
    lo, hi = int(n * t_lo_frac), int(n * t_hi_frac)
    t = t_fs[lo:hi] * 1e-15          # fs -> s
    m = msd_A2[lo:hi] * 1e-20        # A^2 -> m^2
    if len(t) < 10:
        return None, None
    A = np.vstack([t, np.ones_like(t)]).T
    slope, _ = np.linalg.lstsq(A, m, rcond=None)[0]
    resid = m - (A @ np.linalg.lstsq(A, m, rcond=None)[0])
    r2 = 1 - resid.var() / m.var() if m.var() > 0 else 0
    return slope / 6.0, r2           # D = slope/6 for 3D


def density_mean(path):
    d = np.loadtxt(path, comments="#")
    if d.ndim == 1:
        d = d.reshape(1, -1)
    return float(np.mean(d[:, 1])), float(np.std(d[:, 1]))


def main(root="."):
    tags = sorted({re.sub(r"^dens_", "", os.path.basename(f))[:-4]
                   for f in glob.glob(os.path.join(root, "dens_*.dat"))})
    if not tags:
        print("no dens_*.dat found — has the campaign run?"); return 1
    rows, byconc = [], {}
    for tag in tags:
        m = re.match(r"koh(\d+)_s(\d+)_(\d+)", tag)
        if not m:
            continue
        wt, seed, T = int(m.group(1)), int(m.group(2)), int(m.group(3))
        rho, rho_sd = density_mean(os.path.join(root, f"dens_{tag}.dat"))
        Dw, r2w = msd_slope(os.path.join(root, f"msd_water_{tag}.dat"))
        Dk, r2k = msd_slope(os.path.join(root, f"msd_k_{tag}.dat"))
        Do, r2o = msd_slope(os.path.join(root, f"msd_oh_{tag}.dat"))
        rows.append(dict(tag=tag, wt=wt, seed=seed, T=T, rho=rho, rho_sd=rho_sd,
                         D_water=Dw, D_K=Dk, D_OH=Do, r2_water=r2w, r2_K=r2k, r2_OH=r2o))
        byconc.setdefault((wt, T), []).append(rows[-1])

    print(f"{'tag':22s} {'rho':>7s} {'D_H2O':>10s} {'D_K':>10s} {'D_OH':>10s}")
    for r in rows:
        f = lambda x: f"{x:.3e}" if x else "   n/a   "
        print(f"{r['tag']:22s} {r['rho']:7.4f} {f(r['D_water']):>10s} {f(r['D_K']):>10s} {f(r['D_OH']):>10s}")

    print("\n=== GATE (replica-averaged) ===")
    verdict, summary = True, []
    for (wt, T), grp in sorted(byconc.items()):
        rho = np.mean([g["rho"] for g in grp]); rho_sd = np.std([g["rho"] for g in grp])
        exp = EXP["density"].get((wt, T))
        line = {"wt": wt, "T": T, "n_replicas": len(grp), "rho_sim": rho, "rho_sd": rho_sd,
                "rho_exp": exp}
        if exp:
            err = abs(rho - exp) / exp
            ok = err <= GATE["density"]
            verdict &= ok
            line.update(rho_err=err, rho_pass=bool(ok))
            print(f"  {wt} wt%, {T} K, n={len(grp)}: rho = {rho:.4f} +/- {rho_sd:.4f} "
                  f"vs exp {exp:.4f}  -> {err*100:5.2f}%  {'PASS' if ok else 'FAIL'}")
        Dw = [g["D_water"] for g in grp if g["D_water"]]
        if Dw:
            line["D_water_sim"] = float(np.mean(Dw))
            print(f"      D(H2O) = {np.mean(Dw):.3e} m2/s  (neat-water exp {EXP['D_water_neat']:.2e}; "
                  f"expected LOWER in KOH)")
        Do = [g["D_OH"] for g in grp if g["D_OH"]]
        if Do:
            line["D_OH_sim"] = float(np.mean(Do))
            print(f"      D(OH-) = {np.mean(Do):.3e} m2/s  [REPORTED, NOT GATED - no Grotthuss]")
        summary.append(line)

    json.dump({"rows": rows, "summary": summary, "gate_pass": bool(verdict)},
              open(os.path.join(root, "bulk_validation.json"), "w"), indent=1, default=float)
    print(f"\n  OVERALL DENSITY GATE: {'PASS' if verdict else 'FAIL'}")
    if not verdict:
        print("  -> Force field REJECTED for interface work. Do not launch the theta campaign.")
        print("     Next: try a two-site OH-, or re-tune K+/OH- LJ against density.")
    return 0 if verdict else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
