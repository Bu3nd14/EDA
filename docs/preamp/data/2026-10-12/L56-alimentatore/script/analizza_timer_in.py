#!/usr/bin/env python3
"""L51b: analizza_timer.py run as L47c2a ran it - from inside timer/, with the
logs' bare names (the script prints the path it is given) - and its output in
timer/analisi_timer.txt. Without a `cd` in the shell (the worktree refuses it).

    /usr/bin/python3 analizza_timer_in.py <lotto>      # <lotto>/timer, <lotto>/psu
"""
import os
import subprocess
import sys

lotto = os.path.abspath(sys.argv[1])
timer = os.path.join(lotto, "timer")
r = subprocess.run([sys.executable, os.path.join(lotto, "psu", "analizza_timer.py"),
                    "tb_psu_timer_nom.log", "tb_psu_timer_min.log"],
                   cwd=timer, capture_output=True, text=True)
open(os.path.join(timer, "analisi_timer.txt"), "w").write(r.stdout + r.stderr)
print(r.stdout + r.stderr, end="")
sys.exit(r.returncode)
