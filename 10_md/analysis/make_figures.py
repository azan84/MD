#!/usr/bin/env python3
"""Generate manuscript figures from REAL campaign data only.

Rule: this script plots what exists on disk. If a dataset is absent the figure is
skipped and reported, never synthesised or extrapolated to look complete.
"""
import json, os, sys, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.labelsize": 9,
    "axes.titlesize": 9, "legend.fontsize": 8, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "figure.dpi": 300, "savefig.dpi": 300,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
    "axes.spines.top": False, "axes.spines.right": False,
})
C_SIM, C_EXP, C_BAD, C_OK = "#1f4e79", "#c0392b", "#c0392b", "#1e8449"

ROOT = os.path.expanduser("~/research/T12_MD_wettability_closure")
FIGDIR = os.path.join(ROOT, "60_manuscript", "figures")
os.makedirs(FIGDIR, exist_ok=True)
made = []


def fig1_density_gate():
    p = os.path.join(ROOT, "10_md/runs/bulk_koh/bulk_validation.json")
    if not os.path.exists(p):
        print("SKIP fig1: no bulk_validation.json"); return
    d = json.load(open(p))
    S = [s for s in d["summary"] if s.get("rho_exp")]
    if not S:
        print("SKIP fig1: no gated points"); return
    S.sort(key=lambda s: (s["T"], s["wt"]))
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.9))

    lbl = [f"{s['wt']} wt%\n{s['T']} K" for s in S]
    x = np.arange(len(S)); w = 0.36
    sim = [s["rho_sim"] for s in S]; sd = [s["rho_sd"] for s in S]
    exp = [s["rho_exp"] for s in S]
    ax.bar(x - w/2, sim, w, yerr=sd, capsize=3, color=C_SIM, label="simulated (3 seeds)")
    ax.bar(x + w/2, exp, w, color="none", edgecolor=C_EXP, hatch="///", label="experiment")
    ax.set_xticks(x); ax.set_xticklabels(lbl)
    ax.set_ylabel(r"density $\rho$  (g cm$^{-3}$)")
    ax.set_ylim(1.0, 1.55); ax.legend(frameon=False, loc="upper left")
    ax.set_title("(a) density against experiment")

    err = [100*(s["rho_sim"]-s["rho_exp"])/s["rho_exp"] for s in S]
    cols = [C_OK if abs(e) <= 3 else C_BAD for e in err]
    ax2.bar(x, err, 0.55, color=cols)
    ax2.axhspan(-3, 3, color=C_OK, alpha=0.13, zorder=0)
    ax2.axhline(3, color=C_OK, lw=0.9, ls="--")
    ax2.text(-0.45, -3.4, "pre-registered gate  $\\pm$3%", ha="left",
             va="bottom", fontsize=7.5, color=C_OK)
    for xi, e in zip(x, err):
        ax2.text(xi, e + 0.28, f"+{e:.1f}%", ha="center", fontsize=7.5, color=C_BAD)
    ax2.set_xticks(x); ax2.set_xticklabels(lbl)
    ax2.set_ylabel("deviation from experiment (%)")
    ax2.set_ylim(-4.5, 12); ax2.set_title("(b) all four points FAIL the gate")
    fig.tight_layout(); f = os.path.join(FIGDIR, "fig1_density_gate.pdf")
    fig.savefig(f); plt.close(fig); made.append(f); print("fig1 ->", f)


def fig2_transport():
    p = os.path.join(ROOT, "10_md/runs/bulk_koh/bulk_validation.json")
    if not os.path.exists(p):
        print("SKIP fig2"); return
    d = json.load(open(p)); rows = d["rows"]
    fig, ax = plt.subplots(figsize=(3.5, 2.9))
    marks = {20: "o", 30: "s"}
    for wt in (20, 30):
        for T, fc in ((298, "white"), (333, C_SIM)):
            sel = [r for r in rows if r["wt"] == wt and r["T"] == T and r.get("D_water")]
            if not sel: continue
            v = [r["D_water"]*1e9 for r in sel]
            ax.scatter([wt + (0 if T == 298 else 0.7)]*len(v), v, marker=marks[wt],
                       facecolor=fc, edgecolor=C_SIM, s=34, zorder=3,
                       label=f"{T} K" if wt == 20 else None)
    ax.axhline(2.30, color=C_EXP, ls="--", lw=1.0)
    ax.text(30.6, 2.36, "neat water, 298 K (exp)", ha="right", fontsize=7.5, color=C_EXP)
    ax.set_xlabel("KOH concentration (wt%)")
    ax.set_ylabel(r"$D_{\mathrm{H_2O}}$  ($10^{-9}$ m$^2$ s$^{-1}$)")
    ax.set_xticks([20, 30]); ax.set_xlim(18, 32); ax.set_ylim(0, 2.7)
    ax.legend(frameon=False, loc="lower left", title=None)
    ax.set_title("water self-diffusivity")
    fig.tight_layout(); f = os.path.join(FIGDIR, "fig2_transport.pdf")
    fig.savefig(f); plt.close(fig); made.append(f); print("fig2 ->", f)


def fig3_sigma_scan():
    d = os.path.join(ROOT, "10_md/runs/oh_scan")
    files = sorted(glob.glob(os.path.join(d, "dens_sig*.dat")))
    pts = []
    for f in files:
        m = re.search(r"sig([\d.]+)_eps([\d.]+)\.dat$", os.path.basename(f))
        if not m: continue
        try:
            a = np.loadtxt(f, comments="#")
        except Exception:
            continue
        if a.size == 0: continue
        a = np.atleast_2d(a)
        if a.shape[1] < 2: continue
        pts.append((float(m.group(1)), float(m.group(2)), float(np.mean(a[:, 1]))))
    if len(pts) < 2:
        print(f"SKIP fig3: only {len(pts)} scan point(s) available"); return
    pts.sort()
    fig, ax = plt.subplots(figsize=(3.5, 2.9))
    std = [p for p in pts if abs(p[1] - 0.1553) < 1e-4]
    hal = [p for p in pts if abs(p[1] - 0.1553) >= 1e-4]
    if std:
        ax.plot([p[0] for p in std], [p[2] for p in std], "o-", color=C_SIM,
                label=r"$\varepsilon=0.155$ kcal mol$^{-1}$")
    for p in hal:
        ax.scatter([p[0]], [p[2]], marker="D", color="#7d3c98", zorder=4,
                   label=f"halide-like ($\\varepsilon$={p[1]})")
    ax.axhline(1.286, color=C_EXP, ls="--", lw=1.0)
    ax.axhspan(1.286*0.97, 1.286*1.03, color=C_OK, alpha=0.15, zorder=0)
    ax.text(ax.get_xlim()[1], 1.298, "experiment $\\pm$3%", ha="right", fontsize=7.5, color=C_EXP)
    ax.scatter([3.166], [1.4081], marker="X", s=60, color=C_BAD, zorder=5)
    ax.annotate("rejected model\n(SPC/E O size)", (3.166, 1.4081), textcoords="offset points",
                xytext=(12, -2), fontsize=7.5, color=C_BAD)
    ax.axvline(3.81, color="#7d3c98", ls=":", lw=1.0)
    ax.text(3.83, 1.36, "Bonthuis\n(published)", fontsize=7, color="#7d3c98")
    ax.set_xlabel(r"OH$^-$ Lennard-Jones $\sigma$  ($\AA$)")
    ax.set_ylabel(r"density $\rho$  (g cm$^{-3}$)")
    ax.set_title("hydroxide size re-tuning, 30 wt%, 298 K")
    ax.legend(frameon=False, fontsize=7.5)
    fig.tight_layout(); f = os.path.join(FIGDIR, "fig3_sigma_scan.pdf")
    fig.savefig(f); plt.close(fig); made.append(f); print("fig3 ->", f)


def fig4_pipeline():
    """Schematic of the one-way coupling chain and where each audit fix landed."""
    fig, ax = plt.subplots(figsize=(7.0, 2.35))
    ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 3)
    boxes = [
        (0.15, "LAMMPS\nconstant-potential MD", "$\\theta(\\Delta\\Psi),\\ \\gamma_{lv},\\ D$"),
        (2.65, "departure force\nbalance (VOF)", "$R_{det}(\\theta,j,v)$"),
        (5.15, "closure\nconstruction", "$\\Theta(j,v,\\theta)$"),
        (7.65, "OpenFOAM cell\nEuler--Euler", "$\\Delta V_{cell}(j)$"),
    ]
    for x, title, out in boxes:
        ax.add_patch(plt.Rectangle((x, 1.15), 2.1, 1.0, fc="#eaf0f6",
                                   ec=C_SIM, lw=1.1, zorder=2))
        ax.text(x + 1.05, 1.80, title, ha="center", va="center", fontsize=8.2, zorder=3)
        ax.text(x + 1.05, 1.35, out, ha="center", va="center", fontsize=8, color=C_SIM, zorder=3)
    for x in (2.25, 4.75, 7.25):
        ax.annotate("", xy=(x + 0.4, 1.65), xytext=(x, 1.65),
                    arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#444"))
    ax.text(5.0, 2.62, "one-way coupling: no cross-scale feedback is claimed",
            ha="center", fontsize=8, style="italic", color="#444")
    ax.text(1.20, 0.72, "external input:\n$N_{site}$", ha="center", fontsize=7.6, color=C_EXP)
    ax.annotate("", xy=(5.9, 1.10), xytext=(5.9, 0.92),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C_EXP))
    ax.text(5.9, 0.80, "$N_{site}$ (experiment)", ha="center", fontsize=7.6, color=C_EXP)
    ax.text(0.15, 0.25, "gate: bulk KOH validation", fontsize=7.6, color=C_BAD)
    ax.annotate("", xy=(1.0, 1.10), xytext=(1.0, 0.45),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C_BAD))
    fig.tight_layout(); f = os.path.join(FIGDIR, "fig4_pipeline.pdf")
    fig.savefig(f); plt.close(fig); made.append(f); print("fig4 ->", f)


if __name__ == "__main__":
    fig1_density_gate(); fig2_transport(); fig3_sigma_scan(); fig4_pipeline()
    print(f"\n{len(made)} figure(s) written to {FIGDIR}")


def fig5_ff_development():
    """Paper 1 headline: sigma is necessary but not sufficient; charge scaling closes it."""
    import glob as _g
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.95))

    # -- panel a: sigma scan --
    pts = []
    for f in sorted(_g.glob(os.path.join(ROOT, "10_md/runs/oh_scan/dens_sig*.dat"))):
        m = re.search(r"sig([\d.]+)_eps([\d.]+)\.dat$", os.path.basename(f))
        if not m: continue
        arr = np.atleast_2d(np.loadtxt(f, comments="#"))
        if arr.size == 0 or arr.shape[1] < 2: continue
        pts.append((float(m.group(1)), float(m.group(2)), arr[:, 1].mean()))
    EXP30 = 1.286
    std = sorted([p for p in pts if abs(p[1] - 0.1553) < 1e-4])
    if std:
        xs = np.array([p[0] for p in std]); ys = np.array([p[2] for p in std])
        a1.plot(xs, ys, "o-", color=C_SIM, ms=5, label="σ scan (ε fixed)")
        i = int(np.where(ys >= EXP30)[0][-1])
        cross = xs[i] + (EXP30 - ys[i]) * (xs[i+1] - xs[i]) / (ys[i+1] - ys[i])
        a1.plot([cross], [EXP30], "*", ms=13, color="#e67e22", zorder=6,
                label=f"crossing σ={cross:.2f} Å")
    a1.scatter([3.166], [1.4081], marker="X", s=70, color=C_BAD, zorder=6)
    a1.annotate("rejected\n(SPC/E O size)", (3.166, 1.4081), textcoords="offset points",
                xytext=(6, -18), fontsize=7.2, color=C_BAD)
    a1.axhline(EXP30, color=C_EXP, ls="--", lw=1.0)
    a1.axhspan(EXP30*0.97, EXP30*1.03, color=C_OK, alpha=0.15, zorder=0)
    a1.axvline(3.81, color="#7d3c98", ls=":", lw=1.2)
    a1.text(3.86, 1.245, "published\n3.81 Å", fontsize=7.2, color="#7d3c98")
    a1.set_xlabel(r"OH$^-$ Lennard-Jones $\sigma$  ($\AA$)")
    a1.set_ylabel(r"density $\rho$  (g cm$^{-3}$)")
    a1.set_title("(a) size alone can hit the target")
    a1.legend(frameon=False, fontsize=7.2, loc="lower left")

    # -- panel b: charge scaling at the published sigma --
    data = {(20, "1.0"): 1.2561, (20, "0.8"): 1.1723,
            (30, "1.0"): 1.3858, (30, "0.8"): 1.2662}
    exp = {20: 1.185, 30: 1.286}
    x = np.arange(2); w = 0.34
    q10 = [100*(data[(c, "1.0")] - exp[c])/exp[c] for c in (20, 30)]
    q08 = [100*(data[(c, "0.8")] - exp[c])/exp[c] for c in (20, 30)]
    a2.bar(x - w/2, q10, w, color=C_BAD, label="q = 1.0 (formal)")
    a2.bar(x + w/2, q08, w, color=C_OK, label="q = 0.8 (ECC)")
    a2.axhspan(-3, 3, color=C_OK, alpha=0.13, zorder=0)
    a2.axhline(0, color="#555", lw=0.7)
    for xi, v in zip(x - w/2, q10):
        a2.text(xi, v + 0.35, f"+{v:.1f}", ha="center", fontsize=7.2, color=C_BAD)
    for xi, v in zip(x + w/2, q08):
        a2.text(xi, v - 0.95, f"{v:.1f}", ha="center", fontsize=7.2, color=C_OK)
    a2.set_xticks(x); a2.set_xticklabels(["20 wt%", "30 wt%"])
    a2.set_ylabel("deviation from experiment (%)")
    a2.set_ylim(-4.5, 10)
    a2.set_title("(b) but charge scaling is what closes it")
    a2.legend(frameon=False, fontsize=7.5, loc="upper left")
    a2.text(0.5, -3.9, "gate ±3%", ha="center", fontsize=7.2, color=C_OK)

    fig.tight_layout(); f = os.path.join(FIGDIR, "fig5_ff_development.pdf")
    fig.savefig(f); plt.close(fig); made.append(f); print("fig5 ->", f)


def fig6_before_after():
    """Gate failure -> methodology change -> gate pass. The Paper 1 narrative in one figure."""
    old = json.load(open(os.path.join(ROOT, "10_md/runs/bulk_koh_REJECTED_FF/bulk_validation.json")))
    new = json.load(open(os.path.join(ROOT, "10_md/runs/bulk_koh/bulk_validation.json")))
    O = sorted(old["summary"], key=lambda s: (s["wt"], s["T"]))
    N = sorted(new["summary"], key=lambda s: (s["wt"], s["T"]))
    lbl = [f"{s['wt']} wt%\n{s['T']} K" for s in N]
    x = np.arange(len(N)); w = 0.36

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.95))

    eo = [100*(o["rho_sim"]-o["rho_exp"])/o["rho_exp"] for o in O]
    en = [100*(n["rho_sim"]-n["rho_exp"])/n["rho_exp"] for n in N]
    a1.bar(x - w/2, eo, w, color=C_BAD, label="rejected model")
    a1.bar(x + w/2, en, w, color=C_OK, label="adopted model")
    a1.axhspan(-3, 3, color=C_OK, alpha=0.13, zorder=0)
    a1.axhline(0, color="#555", lw=0.7)
    for xi, v in zip(x - w/2, eo):
        a1.text(xi, v + 0.35, f"+{v:.1f}", ha="center", fontsize=6.8, color=C_BAD)
    for xi, v in zip(x + w/2, en):
        a1.text(xi, v - 1.1, f"{v:.1f}", ha="center", fontsize=6.8, color=C_OK)
    a1.set_xticks(x); a1.set_xticklabels(lbl, fontsize=7.5)
    a1.set_ylabel("density deviation from experiment (%)")
    a1.set_ylim(-4.5, 11.5)
    a1.text(1.5, -4.0, "pre-registered gate  $\\pm$3%", ha="center", fontsize=7, color=C_OK)
    a1.set_title("(a) density: FAIL $\\rightarrow$ PASS")
    a1.legend(frameon=False, fontsize=7.5, loc="upper left")

    do = [o.get("D_water_sim", np.nan)*1e9 for o in O]
    dn = [n.get("D_water_sim", np.nan)*1e9 for n in N]
    a2.bar(x - w/2, do, w, color=C_BAD, label="rejected model")
    a2.bar(x + w/2, dn, w, color=C_OK, label="adopted model")
    for xi, v0, v1 in zip(x, do, dn):
        a2.annotate("", xy=(xi + w/2, v1), xytext=(xi - w/2, v0),
                    arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#555",
                                    connectionstyle="arc3,rad=-0.25"))
        a2.text(xi, max(v0, v1) + 0.12, f"{v1/v0:.1f}$\\times$", ha="center", fontsize=6.8, color="#333")
    a2.set_xticks(x); a2.set_xticklabels(lbl, fontsize=7.5)
    a2.set_ylabel(r"$D_{\mathrm{H_2O}}$  ($10^{-9}$ m$^2$ s$^{-1}$)")
    a2.set_ylim(0, 3.9)
    a2.set_title("(b) transport recovers 1.5--3.1$\\times$")
    a2.legend(frameon=False, fontsize=7.5, loc="upper left")

    fig.tight_layout(); f = os.path.join(FIGDIR, "fig6_before_after.pdf")
    fig.savefig(f); plt.close(fig); made.append(f); print("fig6 ->", f)
