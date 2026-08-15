#!/usr/bin/env bash
# MD-3xx theta(dPsi) campaign -- the primary result of Paper 1.
#
# GATED: only runs if the bulk KOH validation gate passed.
# CORE BUDGET: 12 concurrent single-rank jobs; 4 logical cores stay free.
#
# Design (post-Audit-1):
#   * 4 potentials x 3 seeds at Lx = 12 nm  = 12 jobs  -> the P1 test
#   * box convergence (Lx = 8, 16 nm) runs AFTER, reusing the same slots
#   * uncertainty = spread across REPLICAS, not block averages
set -u
P=~/research/T12_MD_wettability_closure
export PATH=$HOME/.local/bin:$PATH
export OMP_NUM_THREADS=1

GATE=$(python3 -c "import json;print(json.load(open('$P/10_md/runs/bulk_koh/bulk_validation.json'))['gate_pass'])" 2>/dev/null)
if [ "$GATE" != "True" ]; then
  echo "REFUSING TO LAUNCH: bulk validation gate is not passed (gate_pass=$GATE)."
  echo "The whole point of the gate is that this campaign does not run before it."
  exit 1
fi
echo "gate_pass=True -> proceeding"

RUN=$P/10_md/runs/theta
mkdir -p "$RUN" && cd "$RUN"
cp "$P/10_md/inputs/in.theta" . 2>/dev/null
cp "$P/10_md/systems"/data.iface_L* . 2>/dev/null

MAXJOBS=12
n=0
for dpsi in 0.0 0.25 0.50 1.00; do
  for s in 1 2 3; do
    tag="th_L12_d${dpsi}_s${s}"
    [ -f "DONE_${tag}" ] && { echo "skip $tag"; continue; }
    seed=$(( 40000 + s*97 + $(echo "$dpsi*100" | bc | cut -d. -f1) ))
    nohup nice -n 5 lmp -in in.theta \
          -var data data.iface_L12 \
          -var T 333.0 -var dpsi "$dpsi" -var seed "$seed" -var tag "$tag" \
          > "log_${tag}.txt" 2>&1 &
    echo "launched $tag (dPsi=${dpsi} V, seed ${seed}, pid $!)"
    n=$((n+1))
    while [ "$(pgrep -c -u "$USER" -x lmp 2>/dev/null || echo 0)" -ge "$MAXJOBS" ]; do sleep 30; done
  done
done
echo "=== $n jobs launched, cap $MAXJOBS ==="
echo "analyse: python3 $P/10_md/analysis/extract_theta.py $RUN"
