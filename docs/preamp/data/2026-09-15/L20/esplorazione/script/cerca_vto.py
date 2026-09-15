#!/usr/bin/env python3
"""
cerca_vto.py - L20: which Vto gives the LSK489A vendor model a chosen I_DSS,
with Beta held at the transcribed 2.2m (NC-013 prescribes moving Vto only).

Conditions are L7's, i.e. the datasheet's (RevA40 p.2): V_DG = 15 V with
V_GS = 0, so V_DS = 15 V at the terminals, and 25 C via `set temp` (the model
carries Vtotc = -2.5m, Vto is the value at Tnom = 27 C).

The model file is included UNTOUCHED; Vto is changed with `altermod` inside
.control. Step 0 of L20 proved altermod reaches the model and survives
`set temp`, and that a wrong model name only prints an Error line and changes
nothing - so every run here refuses on any line containing "Error".

Method: bisection on Vto for each target, then the Vto is ROUNDED TO 1 mV and
declared, and the I_DSS it gives is MEASURED again with the rounded value, at
25 C and at 27 C. The declared I_DSS is the measured one, never the target.

Usage:  python3 cerca_vto.py <repo-root> <scratch-dir> <out.csv>
"""
import math
import os
import re
import subprocess
import sys

NGSPICE = "/opt/homebrew/bin/ngspice"
TARGETS = [("A_tip", 5.5e-3), ("B_min", 8.0e-3), ("B_tip", 11.5e-3), ("B_max", 15.0e-3)]


def idss(repo, scratch, vto, temp):
    lib = os.path.join(repo, "models", "jfet", "lsk489.lib")
    alt = f"altermod lsk489a vto = {vto!r}\n" if vto is not None else ""
    deck = (f"cerca_vto probe\n.include {lib}\nVdd d 0 DC 15\nVgg g 0 DC 0\n"
            f"J1 d g 0 LSK489A\n.control\nset temp = {temp}\n{alt}op\n"
            "print i(vdd)\n.endc\n.end\n")
    path = os.path.join(scratch, "cerca_vto_probe.cir")
    with open(path, "w") as f:
        f.write(deck)
    r = subprocess.run([NGSPICE, "-b", path], capture_output=True, text=True, cwd=scratch)
    out = r.stdout + r.stderr
    if r.returncode != 0 or "Error" in out:
        raise RuntimeError(f"ngspice rc={r.returncode} or Error line for vto={vto}:\n{out}")
    m = re.search(r"^i\(vdd\)\s*=\s*(\S+)", out, re.M)
    if not m:
        raise RuntimeError(f"no i(vdd) printed for vto={vto}:\n{out}")
    return abs(float(m.group(1)))


def main(argv):
    if len(argv) != 4:
        print(__doc__)
        return 2
    repo, scratch, csv = argv[1], argv[2], argv[3]
    os.makedirs(scratch, exist_ok=True)

    # Positive control first: the vendor model as-is must give L7's number.
    base = idss(repo, scratch, None, 25)
    if abs(base - 2.59283e-3) > 0.5e-8:
        print(f"REFUSED: vendor model as-is gives {base:.6e} A at 25 C, L7 measured 2.59283e-03")
        return 1
    print(f"control: LSK489A as-is, 25 C: I_DSS = {base:.6e} A (L7 2.59283e-03)")

    rows = [("A_come_e", -1.13, idss(repo, scratch, -1.13, 25), idss(repo, scratch, -1.13, 27))]
    for label, target in TARGETS:
        lo, hi = -1.13, -4.0          # |Vto| larger -> I_DSS larger
        if not idss(repo, scratch, hi, 25) > target > idss(repo, scratch, lo, 25):
            print(f"REFUSED: target {target} not bracketed by Vto {lo}..{hi}")
            return 1
        for _ in range(30):
            mid = (lo + hi) / 2
            if idss(repo, scratch, mid, 25) < target:
                lo = mid
            else:
                hi = mid
        exact = (lo + hi) / 2
        # Rounded to 1 mV. A window EDGE is rounded toward the INSIDE of the
        # window: nearest-mV put B_min at 7.99795 mA, below the 8.0 minimum.
        if label.endswith("_min"):
            vto = math.floor(exact * 1000) / 1000     # more negative -> more I_DSS
        elif label.endswith("_max"):
            vto = math.ceil(exact * 1000) / 1000      # less negative -> less I_DSS
        else:
            vto = round(exact, 3)
        i25 = idss(repo, scratch, vto, 25)
        i27 = idss(repo, scratch, vto, 27)
        print(f"{label}: target {target*1e3:.1f} mA -> Vto exact {exact:.6f}, "
              f"declared {vto:.3f} V -> I_DSS 25 C {i25*1e3:.5f} mA, 27 C {i27*1e3:.5f} mA")
        rows.append((label, vto, i25, i27))

    with open(csv, "w") as f:
        f.write("variante,vto_v,idss_25c_a,idss_27c_a\n")
        for label, vto, i25, i27 in rows:
            f.write(f"{label},{vto:.3f},{i25:.6e},{i27:.6e}\n")
    print(f"written {csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
