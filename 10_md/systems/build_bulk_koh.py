#!/usr/bin/env python3
"""Build a bulk KOH(aq) LAMMPS data file: SPC/E water + K+ + single-site OH-.

Purpose: force-field validation gate (MD-1xx). Both Audit-1 auditors required that the
force field reproduce bulk KOH properties BEFORE any interface or contact-angle run.

Force field provenance — stated honestly, see LIMITATIONS and OI-14:
  water  SPC/E                     : O sigma 3.166 A, eps 0.1553 kcal/mol, q_O -0.8476, q_H +0.4238
  K+     Joung-Cheatham (SPC/E)    : sigma 2.8384 A, eps 0.4297 kJ/mol = 0.10270 kcal/mol
  OH-    SINGLE SITE, LJ taken identical to SPC/E oxygen (a documented practice for
         hydroxide in SPC/E-based simulations), q = -1.0
         >>> A single-site OH- cannot carry Grotthuss (structural) transport. This is a
         >>> stated limitation, not a hidden one. Its ONLY justification is that it must
         >>> pass the bulk-property gate below; if it fails, it is replaced.

Types: 1=Ow  2=Hw  3=K+  4=OH-
"""
import numpy as np, argparse, math

MW_W, MW_KOH = 18.015, 56.106
NA = 6.02214076e23

def build(wt_pct=30.0, n_water_target=2000, seed=12345, rho_guess=None):
    rng = np.random.default_rng(seed)
    # composition: per 100 g solution -> wt_pct g KOH, (100-wt_pct) g water
    n_koh_per_water = (wt_pct / MW_KOH) / ((100.0 - wt_pct) / MW_W)
    n_water = int(n_water_target)
    n_ion = max(1, int(round(n_water * n_koh_per_water)))
    # experimental density of KOH(aq) at 298 K (kg/m3) - used ONLY to set the initial box
    rho = rho_guess if rho_guess else (997.0 + 8.6 * wt_pct)
    mass_g = (n_water * MW_W + n_ion * MW_KOH) / NA
    vol_A3 = mass_g / (rho * 1e-3) * 1e24
    L = vol_A3 ** (1.0 / 3.0)

    # lattice placement then random selection for ions (avoids overlaps by construction)
    n_sites = n_water + 2 * n_ion
    m = int(math.ceil(n_sites ** (1.0 / 3.0)))
    step = L / m
    sites = [(i * step, j * step, k * step) for i in range(m) for j in range(m) for k in range(m)]
    rng.shuffle(sites)
    sites = sites[:n_sites]

    atoms, bonds, angles = [], [], []
    aid = mid = 0
    # SPC/E internal geometry
    dOH, ang = 1.0, math.radians(109.47)
    for idx, (x, y, z) in enumerate(sites):
        mid += 1
        if idx < n_ion:                                   # K+
            aid += 1; atoms.append((aid, mid, 3, 1.0, x, y, z))
        elif idx < 2 * n_ion:                             # OH- single site
            aid += 1; atoms.append((aid, mid, 4, -1.0, x, y, z))
        else:                                             # SPC/E water, random orientation
            q = rng.normal(size=4); q /= np.linalg.norm(q)
            w, i_, j_, k_ = q
            R = np.array([
                [1-2*(j_*j_+k_*k_), 2*(i_*j_-k_*w),   2*(i_*k_+j_*w)],
                [2*(i_*j_+k_*w),    1-2*(i_*i_+k_*k_), 2*(j_*k_-i_*w)],
                [2*(i_*k_-j_*w),    2*(j_*k_+i_*w),   1-2*(i_*i_+j_*j_)]])
            o = np.array([0.0, 0.0, 0.0])
            h1 = np.array([dOH*math.sin(ang/2),  dOH*math.cos(ang/2), 0.0])
            h2 = np.array([-dOH*math.sin(ang/2), dOH*math.cos(ang/2), 0.0])
            com = np.array([x, y, z])
            o, h1, h2 = [com + R @ p for p in (o, h1, h2)]
            aid += 1; iO = aid; atoms.append((aid, mid, 1, -0.8476, *o))
            aid += 1; iH1 = aid; atoms.append((aid, mid, 2, 0.4238, *h1))
            aid += 1; iH2 = aid; atoms.append((aid, mid, 2, 0.4238, *h2))
            bonds.append((len(bonds)+1, 1, iO, iH1))
            bonds.append((len(bonds)+1, 1, iO, iH2))
            angles.append((len(angles)+1, 1, iH1, iO, iH2))
    return atoms, bonds, angles, L, n_water, n_ion


def write(path, atoms, bonds, angles, L):
    with open(path, "w") as f:
        f.write("LAMMPS data file - bulk KOH(aq), SPC/E + K+ + single-site OH-\n\n")
        f.write(f"{len(atoms)} atoms\n{len(bonds)} bonds\n{len(angles)} angles\n\n")
        f.write("4 atom types\n1 bond types\n1 angle types\n\n")
        for d in "xyz":
            f.write(f"0.0 {L:.6f} {d}lo {d}hi\n")
        f.write("\nMasses\n\n1 15.9994\n2 1.00794\n3 39.0983\n4 17.0073\n")
        f.write("\nAtoms # full\n\n")
        for a in atoms:
            f.write(f"{a[0]} {a[1]} {a[2]} {a[3]:.4f} {a[4]:.5f} {a[5]:.5f} {a[6]:.5f}\n")
        if bonds:
            f.write("\nBonds\n\n")
            for b in bonds: f.write(f"{b[0]} {b[1]} {b[2]} {b[3]}\n")
        if angles:
            f.write("\nAngles\n\n")
            for g in angles: f.write(f"{g[0]} {g[1]} {g[2]} {g[3]} {g[4]}\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wt", type=float, default=30.0)
    ap.add_argument("--nwater", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--out", default="data.koh")
    a = ap.parse_args()
    atoms, bonds, angles, L, nw, ni = build(a.wt, a.nwater, a.seed)
    write(a.out, atoms, bonds, angles, L)
    print(f"{a.out}: {len(atoms)} atoms | {nw} H2O | {ni} KOH | box {L:.2f} A | {a.wt} wt% | seed {a.seed}")
