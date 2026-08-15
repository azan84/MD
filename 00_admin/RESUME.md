# RESUME CHECKPOINT — T12 rev B
**Written 2026-08-15, updated at pause. Read this file first on resume, then `STATE.json`, then `STATUS.md`.**

> **PAUSED BY OPERATOR.** Both manuscripts are current and reflect the gate failure *and* its
> resolution. Background jobs were left running deliberately — see §2.

---

## 1. One-paragraph summary of where this stands

The corpus gap-discovery run selected topic **T12 rev B**: derive the *wettability dependence* of a
bubble-coverage closure for alkaline water electrolysis from potential-aware MD, and propagate it to
cell-scale polarisation. Phases 0–2 (environment, problem, theory) are complete and audited by two
independent reviewers. Phase 3 (MD) is **in progress**: the force-field validation gate **failed**
with an initial hydroxide model, was diagnosed, resolved by adopting published parameters with
charge scaling, and **re-validated PASS**. The contact-angle campaign is now gated behind a
**box-convergence run that is currently executing**.

---

## 2. WHAT IS RUNNING RIGHT NOW

**3 LAMMPS jobs × 4 MPI ranks = 12 cores**, launched with `nohup`, so they **survive session end**.

| Job | Directory | Progress at checkpoint |
|---|---|---|
| `bc_L8` | `10_md/runs/theta_boxconv/` | step 85 000 |
| `bc_L12` | same | step 71 000 |
| `bc_L16` | same | step 64 000 |

Each runs 590 000 steps total (40k relax @0.1 fs + 25k neutral + 25k polarised + 500k production
@2 fs). **Expected completion: ~1.0 / 1.6 / 2.1 days** from launch (10:59, 2026-08-15).

### To check on resume
```bash
pgrep -c -x lmp                                   # 12 = still running, 0 = finished/died
cd ~/research/T12_MD_wettability_closure/10_md/runs/theta_boxconv
grep -c DONE log_bc_L*.txt                        # 1 each = complete
grep -c ERROR log_bc_L*.txt                       # must be 0
```

---

## 3. THE IMMEDIATE NEXT ACTION

When the three box-convergence jobs finish:

```bash
source ~/venvs/t12/bin/activate
cd ~/research/T12_MD_wettability_closure
python3 10_md/analysis/extract_theta.py 10_md/runs/theta_boxconv
```

This prints θ for each box width. **Decision rule, fixed in advance:** adopt the **smallest** box
whose angle agrees with the 16 nm result within the estimator spread (~2–3°). Then:

```bash
# edit launch_theta.sh: set data.iface_L<chosen> ; then
bash 10_md/runs/launch_theta.sh
```

The launcher **refuses to run unless the bulk gate passed** (it reads `bulk_validation.json`), so it
is safe to invoke blind. Campaign cost: **~4.0 days at 8 nm**, 6.2 days at 12 nm, 12 jobs × 1 rank
concurrent.

---

## 4. STATE OF EACH DELIVERABLE

| Artefact | Status |
|---|---|
| `60_manuscript/paper1/manuscript.{tex,pdf}` | **Drafted, 10 pp.** Intro/Theory/Methods complete; §4 force-field results COMPLETE including §4.5 "What changed between the failing and passing models", §4.6 re-validation, §4.7 residual discrepancies; §5 wettability PENDING. Copy at `~/T12_paper1_draft.pdf` |
| `60_manuscript/paper2/manuscript.{tex,pdf}` | **Drafted, 11 pp.** §4.1 now reports the gate failure *and its resolution*, citing Paper 1 for the full account. Copy at `~/T12_paper2_draft.pdf` |
| `60_manuscript/figures/` | fig1 density gate, fig2 transport, fig3 σ-scan, fig4 pipeline, fig5 FF development, fig6 before/after — **all from real data** |
| Force field | **SETTLED** — see §5 |
| θ campaign | Blocked on box convergence (running) |
| VOF / cell stages (S-B, S-C) | Not started |

---

## 5. THE FORCE FIELD — settled, do not re-litigate

**Adopted** (SPC/E water, charges *unscaled*; `pair_modify mix geometric`):

| Site | ε (kcal/mol) | σ (Å) | q (e) |
|---|---|---|---|
| O (SPC/E) | 0.15530 | 3.16600 | −0.8476 |
| H (SPC/E) | 0 | 0 | +0.4238 |
| K⁺ (Loche) | 0.21510 | 2.83000 | **+0.8** |
| OH⁻ (Bonthuis, single site) | 0.01195 | 3.81000 | **−0.8** |

**Why, in one line:** correct hydroxide *size* alone still overpredicts density by 6–8 %; ECC charge
scaling to 0.8 is what closes it (measured −1.1 % / −1.5 %). A σ-only fit at 3.70 Å *passes the
density gate at −0.57 %* and was **rejected** because it hides a charge error inside a size
parameter and would fail at the interface.

**Validated:** density 1.00–1.78 % at four state points, 3 seeds each.

---

## 6. OPEN ITEMS THAT MATTER ON RESUME

Full list in `OPEN_ITEMS.md`. The ones that bite:

- **OI-17 — audit sweep required.** The manuscript once claimed a finite-size correction that the
  code did not apply. It does now, but **every other method claim in both manuscripts must be
  re-checked against executing code.** This is the highest-value unfinished task.
- **OI-19 — methods duplication.** Paper 1 carries full MD methods; Paper 2 repeats them. Paper 2
  §3.1 must compress to a summary citing Paper 1, and **Paper 1 must be submitted first**.
- **OI-18 — the gate is weaker than advertised.** Only density is gated in code; the D(H₂O) and
  D(K⁺) criteria were never implemented. Also, a 3 % density tolerance is 62 % on φ_V at 20 wt%
  but 31 % at 30 wt% — not concentration-neutral.
- **Structural residual:** the OH⁻–water first peak sits at **2.68 Å vs 2.77–2.79 Å experimental**,
  and D(H₂O) may now be ~1.5–1.8× too *fast*. Both point the same way (slightly over-loosened
  ion–water binding), so the density agreement may be partly compensating. Belongs in the
  discussion, not hidden.
- **OI-3 — operator action:** Electrochimica Acta JCR quartile in *Electrochemistry* unverified. It
  is the best scope fit for Paper 2 but may be Q2.

---

## 7. HARD-WON LESSONS — read before touching the code

These cost real time and will recur if forgotten.

1. **Benchmark the system you are going to run, not a simpler one.** Campaign estimates carried over
   from the bulk system were wrong by ~2× because the slab is Kspace-dominated.
2. **A docstring is not an implementation.** The Yeh–Hummer correction was documented, absent, and
   had already propagated into a manuscript sentence.
3. **Verify file contents after an edit before launching compute.** An edit reported success, did
   not persist, and a smoke test silently ran stale input.
4. **Do not add neighbour exclusions with `fix electrode`.** It needs electrode–electrode
   interactions; the verified reference case does not exclude them.
5. **`nve/limit` is incompatible with SHAKE.** LAMMPS says so; use small-timestep NVE + Langevin.
6. **Test the analysis pipeline on real data before the campaign.** The contact-angle extraction
   failed on its first real input and would have produced 12 jobs of unanalysable output.
7. **Gates must be able to block.** `launch_theta.sh` reads the gate result and refuses to run —
   enforced in code, not in discipline.

---

## 8. ESCALATION POLICY (operator-set)

Blocking gate → escalate to **Opus, max 3 attempts** → then **Fable, max 3 attempts** → then stop
and request human approval. Ledger in `DECISIONS.md`. The force-field gate was resolved on
**attempt 1**; Fable was never invoked.

---

## 9. CORE BUDGET (operator-set)

**Keep 4 logical cores free; use the rest.** 32 logical cores total; the operator runs their own
jobs concurrently. All my jobs run at `nice -n 5`. Current split: 12 mine + operator's = 28 of 32.

---

## 10. RESUME COMMAND SEQUENCE

```bash
cd ~/research/T12_MD_wettability_closure
cat 00_admin/RESUME.md                            # this file
python3 -c "import json;print(json.load(open('00_admin/STATE.json'))['next_action'])"
pgrep -c -x lmp                                   # are the jobs still alive?
tail -40 00_admin/STATUS.md                       # what happened last
git log --oneline | head -10
```
