#!/usr/bin/env python3
"""falsi.py - make the extended relay guardian (2e) FAIL, on netlists that are
GENERATED from scratch copies of the SKiDL source, never hand-edited (L16).

For each variant: copy circuits/preamp/trim.py with ONE textual change into
esplorazione/falsi/<variant>/, copy preamp_audio.py next to it (so that its
sys.path[0] picks the scratch trim.py), generate the netlist into that
directory (PREAMP_AUDIO_NET_OUT) with gain_block/spice_export taken from the
canonical circuits/preamp via PYTHONPATH, and run
scripts/check_relay_safe_state.py on it. A variant that the guardian passes
is a guardian that does not guard.

Usage: /usr/bin/python3 falsi.py <repo-root>
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
SRC = ROOT / "circuits" / "preamp"
OUT = ROOT / "docs/preamp/data/2026-09-14/L16/esplorazione/falsi"
VENV = "/Users/roberto/EDA/env/venv/bin/python3"

VARIANTS = {
    "permissivo_su_NO": [
        ("k6[nc1] += mid", "k6[_no1] += mid"),
        ("k6[nc2] += vtrim", "k6[_no2] += vtrim"),
    ],
    "vtrim_da_vrelay": [
        ('vtrim, ret = Net("VTRIM"), Net("RLY_RET")',
         'vtrim, ret = vrelay, Net("RLY_RET")'),
    ],
    "bobina_K6_altra_net": [
        ("k6[coil_b] += mute_cmd", 'k6[coil_b] += Net("PERMIT_CMD")'),
    ],
    "reset_non_0dB": [
        ("t1[reset] += a_out", "t1[set_] += a_out"),
        ("t1[set_] += t2c", "t1[reset] += t2c"),
    ],
    "spia_polarita_invertita": [
        ("k[KU_SET_PLUS] += c1", "k[KU_SET_PLUS] += (c1 if k is kt else c8)"),
        ("k[KU_SET_MINUS] += c8", "k[KU_SET_MINUS] += (c8 if k is kt else c1)"),
    ],
    # The guardian does not judge VALUES: this one must pass 2e and fail the
    # block diagram's attenuation assertion (2f, preamp_blocks_draw.py).
    "scala_fuori_finestra": [
        ('R1_TRIM, R2_TRIM, R3_TRIM = "845", "464", "464"',
         'R1_TRIM, R2_TRIM, R3_TRIM = "845", "464", "1k"'),
    ],
    "polo2_invertito": [
        ('KU_COM2, KU_RESET2, KU_SET2 = "6", "7", "5"',
         'KU_COM2, KU_RESET2, KU_SET2 = "6", "5", "7"'),
    ],
}

text = (SRC / "trim.py").read_text()
summary = []
for name, edits in VARIANTS.items():
    d = OUT / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    t = text
    for old, new in edits:
        assert t.count(old) == 1, f"{name}: {old!r} compare {t.count(old)} volte"
        t = t.replace(old, new)
    (d / "trim.py").write_text(t)
    shutil.copy(SRC / "preamp_audio.py", d / "preamp_audio.py")
    net = d / "preamp_audio.net"
    env = dict(os.environ, PYTHONPATH=str(SRC), PREAMP_AUDIO_NET_OUT=str(net))
    gen = subprocess.run([VENV, str(d / "preamp_audio.py")], cwd=d, env=env,
                         capture_output=True, text=True)
    if gen.returncode != 0 or not net.is_file():
        summary.append((name, "GENERAZIONE FALLITA", gen.stderr[-400:]))
        continue
    chk = subprocess.run(["/usr/bin/python3",
                          str(ROOT / "scripts/check_relay_safe_state.py"),
                          str(net)], capture_output=True, text=True)
    (d / "guardiano.txt").write_text(chk.stdout)
    findings = [l.strip() for l in chk.stdout.splitlines() if l.startswith("  ")]
    summary.append((name, f"rc={chk.returncode}", findings[:3]))
    for f in ("trim.py", "preamp_audio.py", "preamp_audio.erc",
              "preamp_audio.log"):
        if (d / f).exists():
            (d / f).unlink()
    shutil.rmtree(d / "__pycache__", ignore_errors=True)

for name, rc, detail in summary:
    print(f"\n== {name}: {rc}")
    if isinstance(detail, list):
        for line in detail:
            print("   " + line[:240])
    else:
        print("   " + detail)
