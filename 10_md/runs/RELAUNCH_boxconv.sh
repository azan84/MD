#!/usr/bin/env bash
# Relaunch box convergence — the run killed at 2026-08-16 06:31.
#
# WHY IT WAS KILLED: operator request. It was NOT resumable (no restart files),
# so this starts from zero. Killed at: L8 105k/500k (21%), L12 60k (12%), L16 35k (7%)
# after 19.5 h. Partial output archived in 10_md/runs/theta_boxconv_KILLED/.
#
# WHAT IS DIFFERENT NOW: in.theta writes alternating restarts every 25k steps,
# so this run IS interruptible. Resume a killed job with:
#   lmp -in in.theta_restart -var rst <tag>.restart.a -var tag <same tag>
set -u
P=~/research/T12_MD_wettability_closure
export PATH=$HOME/.local/bin:$PATH
export OMP_NUM_THREADS=1
RUN=$P/10_md/runs/theta_boxconv
mkdir -p "$RUN" && cd "$RUN"
cp "$P/10_md/inputs/in.theta" . && cp "$P/10_md/systems"/data.iface_L* .
for L in 8 12 16; do
  nohup nice -n 5 mpirun --oversubscribe -np 4 lmp -in in.theta \
        -var data data.iface_L${L} -var T 333.0 -var dpsi 0.0 -var seed $((7000+L)) \
        -var tag "bc_L${L}" > log_bc_L${L}.txt 2>&1 &
  echo "launched L=${L} nm (pid $!)"
done
echo "=== 3 jobs x 4 ranks = 12 cores; ETA ~3.5 d, L16 critical ==="
