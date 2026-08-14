#!/usr/bin/env python3
"""Build Ni(111) | KOH(aq) | Ni(111) slab cell with an optional cylindrical H2 bubble.

For MD-2xx (EDL structure) and MD-3xx (contact angle theta(dPsi)).

Geometry follows the Audit-1 corrections:
  * CYLINDRICAL (quasi-2D) bubble, periodic along y -- straight contact lines.
    NO 1/R line-tension fit is possible or intended (A1.3): cylinders SUPPRESS
    line tension. Size dependence is checked by BOX CONVERGENCE over Lx, not by
    extrapolation.
  * Lateral box must actually fit the cap (A1.4 found the original 2.82 nm box
    could not fit any intended bubble). Lx is set from --lx_nm directly and the
    bubble radius is checked against it.
  * Angle is measured THROUGH THE LIQUID to match the OpenFOAM convention (eq. 24).

Types: 1=Ow 2=Hw 3=K+ 4=OH- 5=Ni_bot(cathode) 6=Ni_top(anode) 7=H2(coarse site)
"""
import numpy as np, argparse, math

MW_W, MW_KOH = 18.015, 56.106
NA = 6.02214076e23
A_NI = 3.524


def ni111_slab(lx, ly, z0, nlayers, atype, aid0, mid0):
    """fcc(111) layers: ABC stacking. Returns atoms, next aid, next mid, slab top z."""
    a = A_NI
    dx, dy = a / math.sqrt(2), a * math.sqrt(3) / math.sqrt(2)
    dz = a / math.sqrt(3)
    nx, ny = int(lx / dx), int(ly / dy)
    atoms, aid, mid = [], aid0, mid0
    for L in range(nlayers):
        offx = (L % 3) * dx / 3.0
        offy = (L % 3) * dy / 3.0
        for i in range(nx):
            for j in range(ny):
                for sx, sy in ((0.0, 0.0), (dx / 2, dy / 2)):
                    x = (i * dx + sx + offx) % lx
                    y = (j * dy + sy + offy) % ly
                    aid += 1; mid += 1
                    atoms.append((aid, mid, atype, 0.0, x, y, z0 + L * dz))
    return atoms, aid, mid, z0 + (nlayers - 1) * dz


def build(lx_nm=12.0, ly_nm=3.0, gap_nm=8.0, wt_pct=30.0, nlayers=5,
          bubble_r_nm=0.0, seed=2026):
    rng = np.random.default_rng(seed)
    lx, ly, gap = lx_nm * 10, ly_nm * 10, gap_nm * 10
    atoms, aid, mid = [], 0, 0

    # --- electrodes ---------------------------------------------------------
    bot, aid, mid, ztop_bot = ni111_slab(lx, ly, 0.0, nlayers, 5, aid, mid)
    atoms += bot
    zliq0 = ztop_bot + 2.6                      # first liquid layer offset
    zliq1 = zliq0 + gap
    top, aid, mid, _ = ni111_slab(lx, ly, zliq1 + 2.6, nlayers, 6, aid, mid)
    atoms += top
    lz = zliq1 + 2.6 + (nlayers - 1) * (A_NI / math.sqrt(3)) + 15.0   # vacuum for slab correction

    # --- electrolyte site lattice ------------------------------------------
    rho = 997.0 + 8.6 * wt_pct                  # kg/m3, initial guess only
    vol_A3 = lx * ly * gap
    mass_g = rho * 1e-3 * vol_A3 * 1e-24
    n_koh_per_water = (wt_pct / MW_KOH) / ((100.0 - wt_pct) / MW_W)
    # mass per "unit" = 1 water + n_koh_per_water KOH
    m_unit = (MW_W + n_koh_per_water * MW_KOH) / NA
    n_water = max(1, int(mass_g / m_unit))
    n_ion = max(1, int(round(n_water * n_koh_per_water)))
    n_sites = n_water + 2 * n_ion

    step = (vol_A3 / n_sites) ** (1 / 3)
    nx, ny, nz = max(1, int(lx / step)), max(1, int(ly / step)), max(1, int(gap / step))
    sites = [((i + 0.5) * lx / nx, (j + 0.5) * ly / ny, zliq0 + (k + 0.5) * gap / nz)
             for i in range(nx) for j in range(ny) for k in range(nz)]

    # --- carve the cylindrical bubble (axis along y, sitting on the cathode) --
    rb = bubble_r_nm * 10
    if rb > 0:
        if 2 * rb > 0.8 * lx:
            raise SystemExit(f"ERROR: bubble diameter {2*rb/10:.1f} nm exceeds 80% of Lx="
                             f"{lx/10:.1f} nm. Enlarge --lx_nm. (This is the A1.4 failure mode.)")
        cx, cz = lx / 2, zliq0
        sites = [s for s in sites if (s[0] - cx) ** 2 + (s[2] - cz) ** 2 > rb ** 2]

    rng.shuffle(sites)
    n_ion = min(n_ion, len(sites) // 3)
    dOH, ang = 1.0, math.radians(109.47)
    bonds, angles = [], []
    for idx, (x, y, z) in enumerate(sites):
        if idx < n_ion:
            aid += 1; mid += 1; atoms.append((aid, mid, 3, 1.0, x, y, z))
        elif idx < 2 * n_ion:
            aid += 1; mid += 1; atoms.append((aid, mid, 4, -1.0, x, y, z))
        else:
            q = rng.normal(size=4); q /= np.linalg.norm(q)
            w, i_, j_, k_ = q
            R = np.array([
                [1-2*(j_*j_+k_*k_), 2*(i_*j_-k_*w),   2*(i_*k_+j_*w)],
                [2*(i_*j_+k_*w),    1-2*(i_*i_+k_*k_), 2*(j_*k_-i_*w)],
                [2*(i_*k_-j_*w),    2*(j_*k_+i_*w),   1-2*(i_*i_+j_*j_)]])
            com = np.array([x, y, z])
            o  = com + R @ np.array([0.0, 0.0, 0.0])
            h1 = com + R @ np.array([ dOH*math.sin(ang/2), dOH*math.cos(ang/2), 0.0])
            h2 = com + R @ np.array([-dOH*math.sin(ang/2), dOH*math.cos(ang/2), 0.0])
            mid += 1
            aid += 1; iO = aid;  atoms.append((aid, mid, 1, -0.8476, *o))
            aid += 1; iH1 = aid; atoms.append((aid, mid, 2,  0.4238, *h1))
            aid += 1; iH2 = aid; atoms.append((aid, mid, 2,  0.4238, *h2))
            bonds.append((len(bonds)+1, 1, iO, iH1))
            bonds.append((len(bonds)+1, 1, iO, iH2))
            angles.append((len(angles)+1, 1, iH1, iO, iH2))
    return atoms, bonds, angles, lx, ly, lz, n_water, n_ion


def write(path, atoms, bonds, angles, lx, ly, lz):
    with open(path, "w") as f:
        f.write("LAMMPS data - Ni(111)|KOH(aq)|Ni(111), SPC/E + K+ + single-site OH-\n\n")
        f.write(f"{len(atoms)} atoms\n{len(bonds)} bonds\n{len(angles)} angles\n\n")
        f.write("7 atom types\n1 bond types\n1 angle types\n\n")
        f.write(f"0.0 {lx:.6f} xlo xhi\n0.0 {ly:.6f} ylo yhi\n0.0 {lz:.6f} zlo zhi\n")
        f.write("\nMasses\n\n1 15.9994\n2 1.00794\n3 39.0983\n4 17.0073\n"
                "5 58.6934\n6 58.6934\n7 2.01588\n")
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
    ap.add_argument("--lx_nm", type=float, default=12.0, help="lateral box (bubble axis normal)")
    ap.add_argument("--ly_nm", type=float, default=3.0, help="cylinder axis length (periodic)")
    ap.add_argument("--gap_nm", type=float, default=8.0)
    ap.add_argument("--wt", type=float, default=30.0)
    ap.add_argument("--layers", type=int, default=5)
    ap.add_argument("--bubble_nm", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default="data.iface")
    a = ap.parse_args()
    at, bo, an, lx, ly, lz, nw, ni = build(a.lx_nm, a.ly_nm, a.gap_nm, a.wt,
                                           a.layers, a.bubble_nm, a.seed)
    write(a.out, at, bo, an, lx, ly, lz)
    nel = sum(1 for x in at if x[2] in (5, 6))
    print(f"{a.out}: {len(at)} atoms ({nel} electrode) | box {lx/10:.1f} x {ly/10:.1f} x {lz/10:.1f} nm "
          f"| gap {a.gap_nm} nm | {a.wt} wt% | bubble R={a.bubble_nm} nm | seed {a.seed}")
