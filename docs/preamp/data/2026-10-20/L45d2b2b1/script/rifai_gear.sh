#!/bin/zsh
# rifai_gear.sh <corse> - L45c1: every run of <corse>/tempi.txt whose LAST line is not rc=0 is run
# once more with method=gear added to its .options (the three tries of L29c's corri.sh are the
# nodeset's, all with the trapezoidal method). The first log is kept as corsa_<c>_trap.log; the
# guard is corri.sh's (rc, and «Transient op started» = rc OPT). The result is appended to
# tempi.txt, which solo_riuscite.py reads by its last line per run.
set -u
DIR=$1
cd "$DIR" || exit 1
for c in $(/usr/bin/python3 -c "
import re
u = {}
for r in open('tempi.txt'):
    p = r.split()
    if p: u[p[0]] = p[1]
print(' '.join(k for k, v in u.items() if v != 'rc=0'))
"); do
    t0=$SECONDS
    mv "corsa_$c.log" "corsa_${c}_trap.log"
    /usr/bin/sed 's/^\.options reltol=1e-6 vntol=1e-6 abstol=1e-12$/.options reltol=1e-6 vntol=1e-6 abstol=1e-12 method=gear/' \
        "corsa_$c.cir" > "corsa_${c}_gear.cir"
    grep -q 'method=gear' "corsa_${c}_gear.cir" || { echo "$c: .options non trovato"; continue; }
    /opt/homebrew/bin/ngspice -b "corsa_${c}_gear.cir" > "corsa_$c.log" 2>&1
    rc=$?
    grep -q 'Transient op started' "corsa_$c.log" && rc=OPT
    grep -qiE 'timestep too small|aborted' "corsa_$c.log" && [ "$rc" = 0 ] && rc=ABORT
    print -r -- "$c rc=$rc $((SECONDS-t0))s $(date +%H:%M:%S) gear" >> tempi.txt
    echo "$c: gear rc=$rc"
done
