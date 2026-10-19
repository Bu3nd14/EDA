#!/usr/bin/env python3
"""L62a: il jack delle corse di diagnosi (run/diagnosi_*/), con analizza_tr.py di L45a -> diagnosi_scatto.csv."""
import glob
import os
import sys

L62A = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(L62A, "..", "..", "2026-10-13", "L45a", "script"))
import analizza_tr as at  # noqa: E402

dirs = sorted(d for d in glob.glob(os.path.join(L62A, "run", "diagnosi_*", "*")) if os.path.isdir(d))
at.main(["analizza_tr", os.path.join(L62A, "diagnosi_scatto.csv")] + dirs)
