#!/usr/bin/env python3
"""L31 sabotage driver: one mini-deck per case, check_deck_refs.py on each.

Every case carries one @rsrc[resistance] citation, so a case whose only
noise name is ignored still has something to check (exit 2 otherwise).
Usage: sabotage.py <repo> <outdir>
"""
import subprocess
import sys
from pathlib import Path

BASE = """sab_{name} - L31 sabotage case
.include @REPO@/spice/preamp/placeholder_devices.lib
.include @REPO@/models/bjt_pnp/ls350.lib
.include @REPO@/spice/preamp/gain_block_flat.inc
VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15
VSRC SRCN 0 DC 0 AC 1
RSRC SRCN IN 430
CSTRAY RG 0 15p
CSTRAY10 RG10 0 15p
RRG RG 0 1G
RRG10 RG10 0 1G
RISO OUT OUTA 47
RLOAD OUTA 0 100k
.control
noise v(OUTA) VSRC lin 2 1000 1001 1
setplot noise1
print @rsrc[resistance]
{body}
.endc
.end
"""

# (name, control-block body, expected exit code)
CASES = [
    ("intatto",        "print onoise_spectrum inoise_spectrum onoise_q121a", 0),
    ("sottosorgente",  "print onoise_q122_rb", 0),
    ("suffissi",       "print onoise_jq110a_1overf onoise_d102_idsw onoise_r143_thermal", 0),
    ("elemento_deck",  "wrdata x.txt onoise_rsrc onoise_rrg10", 0),
    ("let",            "let onoise_foo = onoise_spectrum*2\nprint onoise_foo", 0),
    ("virgolette",     "echo \"onoise_zzz,inoise_total_v\" > x.csv", 0),
    ("commento",       "* onoise_q123 is a dead name in a comment", 0),
    ("totale",         "print onoise_total inoise_total", 0),
    ("suffisso_falso", "print onoise_q122_bogus", 1),
    ("inoise_morto",   "print inoise_q999", 1),
    ("morto_wrdata",   "wrdata x.txt onoise_spectrum onoise_q123", 1),
    ("let_mancante",   "print onoise_uv", 1),
    ("suffisso_solo",  "print onoise_thermal", 1),
]


def main():
    repo, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    checker = repo / "scripts" / "check_deck_refs.py"
    wrong = 0
    for name, body, want in CASES:
        deck = outdir / f"sab_{name}.cir"
        deck.write_text(BASE.format(name=name, body=body), encoding="utf-8")
        r = subprocess.run([sys.executable, str(checker), str(repo), str(deck)],
                           capture_output=True, text=True)
        ok = r.returncode == want
        wrong += not ok
        print(f"{'ok  ' if ok else 'WRONG'} {name:15s} rc={r.returncode} "
              f"(atteso {want})")
        for line in r.stdout.splitlines():
            print(f"        {line.strip()}")
    print(f"\n{len(CASES) - wrong}/{len(CASES)} casi come attesi")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
