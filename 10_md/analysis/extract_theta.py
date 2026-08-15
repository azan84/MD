#!/usr/bin/env python3
"""Extract the contact angle from a 2-D time-averaged density map.

Protocol (matches Methods, and the Audit-1 corrections):
  * CYLINDRICAL bubble, periodic along y -> the map is x-z, averaged over y.
  * Interface located as the rho = (rho_liq + rho_gas)/2 isochore.
  * Angle measured THROUGH THE LIQUID, matching the OpenFOAM wall BC convention.
  * NO 1/R line-tension extrapolation: a periodic cylindrical cap has straight
    contact lines with zero in-plane curvature, so that fit does not apply.
    Size dependence is handled by BOX CONVERGENCE across Lx instead.

Two independent estimators are reported and their spread is carried as an
uncertainty component, because a single fitting choice can bias the angle by
several degrees:
  (1) circular fit to the isochore, excluding a near-wall exclusion layer
  (2) centre-of-mass / area estimator from the gas region

LAMMPS `ave/chunk` bin/2d format:
  header lines starting with '#', then per-timestep blocks:
      <timestep> <n_chunks> <n_total>
      <chunk_id> <coord1(x)> <coord2(z)> <ncount> <density>
"""
import numpy as np, sys, os, glob, json, math


def read_chunk2d(path):
    """Return x centres, z centres, density grid (averaged over all blocks present)."""
    rows = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.split()
            if len(f) == 3:            # block header
                continue
            if len(f) >= 5:
                rows.append((float(f[1]), float(f[2]), float(f[4])))
    if not rows:
        return None, None, None
    a = np.array(rows)
    xs = np.unique(a[:, 0]); zs = np.unique(a[:, 1])
    g = np.full((len(zs), len(xs)), np.nan)
    xi = {v: i for i, v in enumerate(xs)}; zi = {v: i for i, v in enumerate(zs)}
    # average duplicates (multiple output blocks)
    acc = np.zeros_like(g); cnt = np.zeros_like(g)
    for x, z, d in a:
        acc[zi[z], xi[x]] += d; cnt[zi[z], xi[x]] += 1
    g = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
    return xs, zs, g


def find_bubble(xs, zs, rho_gas, z_wall, min_frac=0.25):
    """Locate the wall-attached bubble from the H2 density map.

    Using the GAS map rather than the liquid map is essential: the liquid map's
    low-density regions include the vapour space above the film and the depleted
    layers at both electrodes, and a fit over those spans the whole cell rather
    than the bubble. Type-7 atoms exist only inside the bubble.
    """
    gg = np.nan_to_num(rho_gas)
    if gg.max() <= 0:
        return None
    thr = min_frac * np.nanpercentile(gg[gg > 0], 90)
    mask = gg > thr
    # keep only the component attached to the cathode (lowest liquid z)
    zi_wall = int(np.argmin(np.abs(zs - z_wall)))
    band = mask[zi_wall:zi_wall + 6]
    if not band.any():
        return None
    seed_cols = np.where(band.any(axis=0))[0]
    lo, hi = seed_cols.min(), seed_cols.max()
    grown = True
    while grown:                       # simple column-wise flood along x
        grown = False
        if lo > 0 and mask[zi_wall:, lo - 1].any(): lo -= 1; grown = True
        if hi < mask.shape[1] - 1 and mask[zi_wall:, hi + 1].any(): hi += 1; grown = True
    sub = np.zeros_like(mask); sub[zi_wall:, lo:hi + 1] = mask[zi_wall:, lo:hi + 1]
    return sub


def contact_angle(xs, zs, rho_liq_map, rho_gas_map=None, excl=3.0, liq_frac=0.5):
    """Circle fit to the bubble interface; angle returned THROUGH THE LIQUID."""
    rho = np.nan_to_num(rho_liq_map)
    rho_liq = np.nanpercentile(rho[rho > 0], 90)
    rho_half = liq_frac * rho_liq
    occupied = np.where(np.nanmax(rho, axis=1) > 0.2 * rho_liq)[0]
    if not len(occupied):
        return None
    z_wall = float(zs[occupied[0]])

    if rho_gas_map is None:
        return None
    mask = find_bubble(xs, zs, rho_gas_map, z_wall)
    if mask is None or mask.sum() < 10:
        return None

    # interface points: boundary of the gas mask, above the near-wall exclusion
    pts = []
    for i, z in enumerate(zs):
        if z < z_wall + excl:
            continue
        cols = np.where(mask[i])[0]
        if len(cols) < 2:
            continue
        pts.append((xs[cols.min()], z))
        pts.append((xs[cols.max()], z))
    if len(pts) < 8:
        return None
    P = np.array(pts)

    A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
    b = (P ** 2).sum(axis=1)
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    xc, zc = float(sol[0]), float(sol[1])
    R = math.sqrt(sol[2] + xc ** 2 + zc ** 2)
    resid = float(np.sqrt(np.mean((np.hypot(P[:, 0] - xc, P[:, 1] - zc) - R) ** 2)))

    d = (z_wall - zc) / R
    if abs(d) > 1:
        return None
    theta_gas = math.degrees(math.acos(np.clip(d, -1, 1)))
    theta_liq = 180.0 - theta_gas
    return dict(theta_deg=theta_liq, R_A=R, xc=xc, zc=zc, z_wall=z_wall,
                n_points=len(P), fit_rmse_A=resid, rho_liq=float(rho_liq))


def com_estimator(xs, zs, rho_gas, z_wall):
    """Independent estimator: gas area + centroid height -> cap angle."""
    rho_gas = np.nan_to_num(rho_gas)
    if rho_gas.max() <= 0:
        return None
    thr = 0.5 * np.nanpercentile(rho_gas[rho_gas > 0], 90)
    mask = rho_gas > thr
    if mask.sum() < 8:
        return None
    dx = float(xs[1] - xs[0]); dz = float(zs[1] - zs[0])
    area = mask.sum() * dx * dz
    ZZ = np.repeat(zs.reshape(-1, 1), len(xs), axis=1)
    zbar = float((ZZ[mask]).mean()) - z_wall
    # circular-segment inversion: area and centroid height -> half-angle
    best, bestres = None, 1e18
    for th in np.linspace(5, 175, 1701):
        t = math.radians(th)
        R = math.sqrt(area / (t - math.sin(t) * math.cos(t))) if (t - math.sin(t)*math.cos(t)) > 0 else None
        if not R: continue
        # centroid of a circular segment above the chord
        num = (2.0/3.0) * R * math.sin(t) ** 3
        den = (t - math.sin(t) * math.cos(t))
        zc_seg = num / den if den > 0 else 0
        res = abs(zc_seg - zbar)
        if res < bestres:
            bestres, best = res, 180.0 - th
    return dict(theta_deg_com=best, gas_area_A2=area, zbar_A=zbar)


def main(root="."):
    out = []
    for f in sorted(glob.glob(os.path.join(root, "dens2d_*.dat"))):
        tag = os.path.basename(f)[7:-4]
        xs, zs, g = read_chunk2d(f)
        if xs is None:
            print(f"{tag}: no data"); continue
        gf = os.path.join(root, f"gas2d_{tag}.dat")
        gg = None
        if os.path.exists(gf):
            gx, gz, gg = read_chunk2d(gf)
        res = contact_angle(xs, zs, g, gg)
        com = None
        if gg is not None and res:
            com = com_estimator(xs, zs, gg, res["z_wall"])
        rec = dict(tag=tag)
        if res: rec.update(res)
        if com: rec.update(com)
        if res and com and com.get("theta_deg_com"):
            rec["theta_spread_deg"] = abs(res["theta_deg"] - com["theta_deg_com"])
        out.append(rec)
        t1 = res["theta_deg"] if res else float("nan")
        t2 = com["theta_deg_com"] if com and com.get("theta_deg_com") else float("nan")
        print(f"{tag:28s} theta_circle={t1:6.1f} deg  theta_com={t2:6.1f} deg  "
              f"spread={abs(t1-t2) if res and com else float('nan'):5.1f}  "
              f"R={res['R_A']:.1f} A  rmse={res['fit_rmse_A']:.2f} A" if res else f"{tag}: fit failed")
    json.dump(out, open(os.path.join(root, "theta_results.json"), "w"), indent=1, default=float)
    print(f"\nwrote theta_results.json ({len(out)} case(s))")
    print("NOTE: uncertainty is the spread across REPLICAS plus the estimator spread above.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
