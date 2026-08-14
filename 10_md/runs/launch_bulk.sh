#!/usr/bin/env bash
# MD-1xx bulk KOH validation campaign — the force-field gate.
#
# CORE BUDGET: operator allocated 12 of 16 physical cores; 4 stay free.
# Each case is a single-rank job (measured: MD parallel efficiency collapses to
# 24% at 8 ranks, so 12 concurrent 1-rank jobs beat 1 job on 12 ranks by ~8x).
#
# 12 cases = 2 concentrations x 3 seeds x 2 temperatures = exactly 12 cores.
set -u
P=~/research/T12_MD_wettability_closure
export PATH=$HOME/.local/bin:$PATH
export OMP_NUM_THREADS=1
RUN=$P/10_md/runs/bulk_koh
mkdir -p "$RUN" && cd "$RUN"
cp "$P/10_md/inputs/in.bulk_koh" . 2>/dev/null
cp "$P/10_md/systems"/data.koh* . 2>/dev/null

MAXJOBS=12
launched=0
for wt in 20 30; do
  for s in 1 2 3; do
    for T in 298 333; do
      tag="koh${wt}_s${s}_${T}"
      [ -f "done_${tag}" ] && { echo "skip $tag (already done)"; continue; }
      nohup nice -n 5 lmp -in in.bulk_koh \
            -var data "data.koh${wt}_s${s}" \
            -var T "${T}.0" \
            -var tag "$tag" > "log_${tag}.txt" 2>&1 &
      echo "launched $tag (pid $!)"
      launched=$((launched+1))
      while [ "$(pgrep -c -u "$USER" -x lmp 2>/dev/null || echo 0)" -ge "$MAXJOBS" ]; do sleep 20; done
    done
  done
done
echo "=== $launched jobs launched; cap $MAXJOBS concurrent ==="
echo "monitor:  pgrep -c -x lmp   |   tail -f $RUN/log_koh30_s1_298.txt"
echo "validate: python3 $P/10_md/analysis/validate_bulk.py $RUN"
