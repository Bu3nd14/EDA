import sys
from pathlib import Path
sys.path.insert(0, "/Users/roberto/EDA/.claude/worktrees/L60b/scripts")
from check_psu_harness import parse_netlist

T = "/Users/roberto/.claude/jobs/9ec6bb6d/tmp/"
W = "/Users/roberto/EDA/.claude/worktrees/L60b/circuits/preamp/"
for name, prima, head, ora in (("audio", T + "audio_ab6.net", T + "audio_head.net", W + "preamp_audio.net"),
                               ("psu", T + "psu_ab6.net", T + "psu_head.net", W + "psu.net")):
    c = [parse_netlist(Path(p)) for p in (prima, head, ora)]
    print(name, "prima di L45d2b1", len(c[0][0]), "HEAD", len(c[1][0]), "L60b", len(c[2][0]))
    a, b = c[0], c[2]
    print("  parti solo prima:", sorted(set(a[0]) - set(b[0])), " solo ora:", sorted(set(b[0]) - set(a[0])))
    dv = sorted(r for r in set(a[0]) & set(b[0]) if a[0][r] != b[0][r])
    print("  parti cambiate:", [(r, a[0][r]["value"], b[0][r]["value"]) for r in dv])
    dn = sorted(k for k in set(a[1]) | set(b[1]) if a[1].get(k) != b[1].get(k))
    print("  pin cambiati:", [(k, a[1].get(k), b[1].get(k)) for k in dn])
    print("  reti col DC:", sorted({n for n in b[1].values() if "DC_" in n or "DET" in n}))
