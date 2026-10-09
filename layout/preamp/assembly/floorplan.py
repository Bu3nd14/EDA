#!/usr/bin/env python3
"""
L49b: the assembly in the candidate chassis, in plan and in height.

  /Users/roberto/EDA/env/venv/bin/python3 layout/preamp/assembly/floorplan.py \
      <audio_placement.json> <psu_dir> <out_dir>

Reads the two trial boards' sizes from their placement.json (L49a's audio
board, L49b's supply board), lays out each VARIANT below inside the chassis,
checks it, and writes per variant <out_dir>/assembly_<variant>.png / .pdf (the
plan, with the dimensions, and a side section), plus <out_dir>/assembly.json
with every check and the shortfall in mm where something does not fit.

Coordinates: x from the left side wall, y from the REAR panel's inner face
(the inputs) towards the front panel, z from the chassis floor. Every body is
a box (a toroid: its bounding box, drawn as a circle). Two bodies collide
when they overlap in plan AND in height, each grown by GAP. Every envelope
below carries its source; "envelope" means the body plus the room its wiring
needs, never less than the published body. Heights on the panels are
ASSUMPTIONS of this trial, written as constraints for G2 (the report).
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
from matplotlib.patches import Circle, Rectangle     # noqa: E402

# ---- the chassis: Modushop Pesante 3U, chosen by the user (L49a, 2026-10-09).
# 415 mm between the side walls (hifi2000; Modushop's own page says 430: the
# trial takes the smaller), 300 deep; inside height 115 (hifi2000; Modushop
# says 120: the smaller again).
CH_W, CH_D, CH_H = 415.0, 300.0, 115.0
GAP = 5.0            # mm between bodies in plan, and to the walls
ZGAP = 3.0           # mm between bodies stacked in height

# ---- boards: standoff, thickness, leads under the board; the tallest part.
STANDOFF, PCB_T, LEADS = 6.0, 1.6, 2.5
# Audio: C_T, 26 mm (L49a, constraint 5).
AUDIO_TALL = 26.0
# Supply: the D16 electrolytics; 4700 uF 35 V in D16 is 16 x 35.5 mm (Nichicon
# VY, RS listing). The common 4700 uF 35 V parts are D18: a footprint
# constraint, L49b's report.
PSU_TALL = 35.5

# ---- the rear panel's back side.
# 14 RCA jacks (L49a's REAR_L / REAR_R), two rows (L over R), 7 columns.
# Neutrik NF2D: flange 31 x 26 mm, overall length 28.3 mm (Adam Hall
# listing, 2026-10-09; the drawing was not opened). The whole length taken as
# the depth behind the panel, plus solder cups and the wire's bend: 30 mm.
RCA_DEPTH, RCA_PITCH_X, RCA_ROWS_Z = 30.0, 26.0, (52.0, 78.0)   # row axes: ASSUMED
RCA_BODY = 26.0
# IEC inlet with fuse and double-pole switch (SAFETY.md, ADR-048): Schurter
# DD11 (typ_DD11.pdf, 2026-10-09): flange 65 x 31.6 mm, cut-out 47.1 x 28.1,
# body 33.1 mm behind the panel, 4.8 mm quick-connects. With the receptacles
# and the bend of the mains wires: 50 mm deep. Axis ASSUMED at 80 mm.
IEC_W, IEC_D, IEC_H, IEC_Z = 65.0, 50.0, 31.6, 80.0

# ---- the front panel's back side (PR-19: selector, gain, trim, volume,
# balance, mute switch, all rotary; the mute LED; P9 (a)'s soft power switch).
# ALPS RK27 stereo: 27 x 25.3 x 24.5 mm (Audiophonics listing); Alpha RV16
# dual (the MN balance, ADR-065): body 17 wide, 11.5 deep (CE Distribution);
# Lorlin CK single wafer: 27.5 mm moulding (Lorlin CKS sheet), 18.1 mm behind
# the panel (RS, CK1061). Deepest ~25 mm, plus terminals and the wire's bend:
# 35 mm. Bodies 30 mm square around the axis. Axis ASSUMED at 65 mm above the
# floor, about half the 115 mm inside: at 62 mm T1 (45.7 mm with its bolt)
# missed passing under the DC controls by 1.7 mm (L49b) - so the axis height
# is a constraint for G2's front panel: >= 45.7 + 3 + 15 = 63.7 mm.
# The ORDER, left to right, is this trial's (a constraint for G2's panel):
# the power side is the left one (IEC, toroids, the supply's mains column and
# rectifiers), so the four DC controls sit over it and the two that carry
# audio sit at the right, over the supply's quiet logic end or nothing.
CONTROLS = ["selettore", "guadagno", "trim", "mute", "volume", "bilanciamento"]
CONTROL_W, CONTROL_D, CONTROL_Z = 30.0, 35.0, 65.0
# Only volume and balance carry the audio signal: the selector, gain, trim and
# mute switches drive relays (DC, L49a's panel headers). The toroids go under
# the DC end (P3), never under volume / balance.
AUDIO_CONTROLS = ("volume", "bilanciamento")

# ---- the toroids (P3, ADR-048): the largest datasheet figures found.
# T1 2 x 15 V 50 VA: Talema 0050P1-2-015K 87.3 x 41.7 mm, M5 bolt (RS);
# Talema 70083K 82.4 x 37.5 (DigiKey); RS PRO 80 x 33; Talema 55121 84 x 34.
# T2 the small one, 12 V: Talema 70050K (15 VA) 60 x 26.3 mm (Distrelec,
# DigiKey); Amgis L01-6342 (10 VA) 55 x 26. NC-037 picks the real part.
# Lying flat on the floor; +4 mm for the clamping disc and the bolt head.
T1_D, T1_H = 87.3, 41.7
T2_D, T2_H = 60.0, 26.3
MOUNT = 4.0


def load(path):
    with open(path) as fh:
        return json.load(fh)


class Plan:
    def __init__(self, name, title):
        self.name, self.title = name, title
        self.items, self.checks, self.notes = [], [], []

    def box(self, label, x, y, w, d, z0, z1, kind, shape="rect"):
        self.items.append(dict(label=label, shape=shape, x=round(x, 2), y=round(y, 2),
                               w=round(w, 2), d=round(d, 2), z0=round(z0, 2),
                               z1=round(z1, 2), kind=kind))

    def check(self, what, ok, value=None, limit=None, short=None):
        self.checks.append(dict(what=what, ok=bool(ok), value=value, limit=limit,
                                shortfall_mm=short))


def collide(a, b):
    plan = not (a["x"] + a["w"] + GAP <= b["x"] or b["x"] + b["w"] + GAP <= a["x"]
                or a["y"] + a["d"] + GAP <= b["y"] or b["y"] + b["d"] + GAP <= a["y"])
    height = not (a["z1"] + ZGAP <= b["z0"] or b["z1"] + ZGAP <= a["z0"])
    return plan and height


def panels(p):
    """Rear: the IEC in the LEFT corner (the power side), the RCA block
    centred in the rest. Front: the six controls evenly spaced."""
    rca_w = 7 * RCA_PITCH_X
    x_rest = GAP + IEC_W + GAP
    x0 = x_rest + (CH_W - x_rest - rca_w) / 2
    p.box("RCA (14, due file)", x0, 0, rca_w, RCA_DEPTH,
          RCA_ROWS_Z[0] - RCA_BODY / 2, RCA_ROWS_Z[1] + RCA_BODY / 2, "panel")
    p.box("IEC con fusibile e interruttore", GAP, 0, IEC_W, IEC_D,
          IEC_Z - IEC_H / 2, IEC_Z + IEC_H / 2, "mains")
    pitch = (CH_W - 2 * GAP) / len(CONTROLS)
    for i, c in enumerate(CONTROLS):
        p.box(c, GAP + i * pitch + (pitch - CONTROL_W) / 2, CH_D - CONTROL_D, CONTROL_W,
              CONTROL_D, CONTROL_Z - CONTROL_W / 2, CONTROL_Z + CONTROL_W / 2,
              "audio" if c in AUDIO_CONTROLS else "panel")


def board_top(tall):
    return STANDOFF + PCB_T + tall


def variant_l49a(audio, psu):
    """A0: L49a's own reading - the audio board behind the RCAs' full depth,
    the panels counted as full-height bands (plan only)."""
    p = Plan("A0_come_L49a", "A0 — la stima di L49a: pannelli come fasce a tutta altezza")
    aw, ad = audio["board_mm"]
    pw, pd = psu["board_mm"]
    p.box("RCA (fascia)", GAP, 0, CH_W - 2 * GAP, RCA_DEPTH, 0, CH_H, "panel")
    p.box("comandi (fascia)", GAP, CH_D - CONTROL_D, CH_W - 2 * GAP, CONTROL_D, 0, CH_H,
          "panel")
    y = RCA_DEPTH + GAP
    p.box("scheda audio", (CH_W - aw) / 2, y, aw, ad, 0, board_top(AUDIO_TALL), "board")
    y1 = y + ad + GAP
    p.box("T1 2×15 V 50 VA", GAP, y1, T1_D, T1_D, 0, T1_H + MOUNT, "toroid", "circle")
    p.box("T2 12 V", GAP + T1_D + GAP, y1, T2_D, T2_D, 0, T2_H + MOUNT, "toroid", "circle")
    p.box("scheda alimentatore", CH_W - GAP - pw, y1, pw, pd, 0, board_top(PSU_TALL), "board")
    free = CH_D - CONTROL_D - GAP - (y + ad + GAP)
    need = max(T1_D, pd)
    p.notes.append(f"Davanti alla scheda audio restano {free:.1f} mm; T1 coricato ne vuole "
                   f"{T1_D}, l'alimentatore {pd}.")
    return p


def variant_flat(audio, psu):
    """A: everything on the floor. The audio board runs under the rear panel's
    jacks (they sit above it), the toroids and the supply board under the
    front panel's controls - the toroids under the DC end (P3)."""
    p = Plan("A_tutto_sul_fondo", "A — tutto sul fondo, i pannelli sopra le schede")
    aw, ad = audio["board_mm"]
    pw, pd = psu["board_mm"]
    panels(p)
    p.box("scheda audio", (CH_W - aw) / 2, GAP, aw, ad, 0, board_top(AUDIO_TALL), "board")
    y1 = GAP + ad + GAP
    p.box("T1 2×15 V 50 VA", GAP, y1, T1_D, T1_D, 0, T1_H + MOUNT, "toroid", "circle")
    p.box("T2 12 V", GAP + T1_D + GAP, y1, T2_D, T2_D, 0, T2_H + MOUNT, "toroid", "circle")
    # The supply board right of the toroids, its mains column (left edge,
    # place.py) facing them: the primary wires stay on the power side.
    xp = GAP + T1_D + GAP + T2_D + GAP
    p.box("scheda alimentatore", xp, y1, pw, pd, 0, board_top(PSU_TALL), "board")
    mains_w = psu["groups"]["MAINS"][0] + psu["groups"]["MAINS"][2] + psu["separation_mm"]
    p.box("sezione di rete dell'alimentatore", xp, y1, mains_w, pd, 0, board_top(PSU_TALL),
          "zone")
    p.notes.append(f"Davanti alla scheda audio restano {CH_D - y1 - GAP:.1f} mm fino al "
                   f"frontale; i comandi stanno sopra, da {CONTROL_Z - CONTROL_W / 2:.0f} mm.")
    return p


def variant_under(audio, psu):
    """B: the supply board on the floor UNDER the audio board (two levels),
    the toroids flat in front, under the DC controls."""
    p = Plan("B_alimentatore_sotto", "B — alimentatore sotto la scheda audio, toroidali davanti")
    aw, ad = audio["board_mm"]
    pw, pd = psu["board_mm"]
    panels(p)
    psu_top = board_top(PSU_TALL)
    a0 = psu_top + ZGAP + LEADS                     # the audio board's underside
    p.box("scheda audio (piano alto)", (CH_W - aw) / 2, GAP, aw, ad, a0,
          a0 + PCB_T + AUDIO_TALL, "board")
    p.box("scheda alimentatore (sotto)", CH_W - GAP - pw, GAP + ad - pd, pw, pd, 0, psu_top,
          "board")
    y1 = GAP + ad + GAP
    p.box("T1 2×15 V 50 VA", GAP, y1, T1_D, T1_D, 0, T1_H + MOUNT, "toroid", "circle")
    p.box("T2 12 V", GAP + T1_D + GAP, y1, T2_D, T2_D, 0, T2_H + MOUNT, "toroid", "circle")
    p.notes.append(f"Due piani: alimentatore fino a {psu_top:.1f} mm, scheda audio da "
                   f"{a0:.1f} a {a0 + PCB_T + AUDIO_TALL:.1f} mm.")
    return p


def run_checks(p):
    for it in p.items:
        over = max(-it["x"], -it["y"], it["x"] + it["w"] - CH_W, it["y"] + it["d"] - CH_D,
                   it["z1"] - CH_H)
        p.check(f"{it['label']} dentro il telaio", over <= 1e-6, None, None,
                None if over <= 1e-6 else round(over, 1))
    for i in range(len(p.items)):
        for j in range(i + 1, len(p.items)):
            a, b = p.items[i], p.items[j]
            if "zone" in (a["kind"], b["kind"]):
                continue       # an area of a board, not a body
            if collide(a, b):
                # the smallest move that clears it: along the depth (the scarce
                # axis in plan) or in height, whichever is less
                dy = min(a["y"] + a["d"] + GAP - b["y"], b["y"] + b["d"] + GAP - a["y"])
                dz = min(a["z1"] + ZGAP - b["z0"], b["z1"] + ZGAP - a["z0"])
                short = round(min(dy, dz), 1)
                axis = "in profondità" if dy <= dz else "in altezza"
                p.check(f"{a['label']} / {b['label']} ({axis})", False, None, None, short)
    # P3: toroids and the supply's mains section not under the audio-carrying
    # controls (ADR-010: mains wiring away from the audio).
    for t in (i for i in p.items if i["kind"] in ("toroid", "zone")):
        for c in (i for i in p.items if i["kind"] == "audio"):
            plan = not (t["x"] + t["w"] <= c["x"] or c["x"] + c["w"] <= t["x"])
            p.check(f"{t['label']} non sotto {c['label']} (P3)", not plan)


def toroid_distances(p):
    """P3: distance from each toroid's centre to the nearest input jack and to
    the nearest audio-carrying control, in plan."""
    rca = [i for i in p.items if i["label"].startswith("RCA")][0]
    audio = [i for i in p.items if i["kind"] == "audio"]
    out = {}
    for t in (i for i in p.items if i["kind"] == "toroid"):
        cx, cy = t["x"] + t["w"] / 2, t["y"] + t["d"] / 2

        def dist(b):
            nx = min(max(cx, b["x"]), b["x"] + b["w"])
            ny = min(max(cy, b["y"]), b["y"] + b["d"])
            return round(math.hypot(cx - nx, cy - ny), 1)
        out[t["label"]] = {"ingressi_RCA": dist(rca),
                           "volume_bilanciamento": min((dist(a) for a in audio), default=None)}
    return out


COLORS = {"board": "#4C78A8", "toroid": "#E45756", "mains": "#F58518",
          "zone": "#F58518", "panel": "#BAB0AC", "audio": "#B279A2"}


def draw(p, out_dir):
    fig, (ax, sx) = plt.subplots(2, 1, figsize=(11, 12.5),
                                 gridspec_kw={"height_ratios": [3.2, 1.3]})
    ax.add_patch(Rectangle((0, 0), CH_W, CH_D, fill=False, lw=2, ec="black"))
    order = sorted(p.items, key=lambda i: i["z0"])
    for it in order:
        c = COLORS[it["kind"]]
        low = it["z0"] < 20
        style = dict(fc=c, ec="black", alpha=0.35 if low else 0.18, lw=1.0,
                     ls="-" if low else "--")
        if it["shape"] == "circle":
            ax.add_patch(Circle((it["x"] + it["w"] / 2, it["y"] + it["d"] / 2), it["w"] / 2,
                                **style))
        else:
            ax.add_patch(Rectangle((it["x"], it["y"]), it["w"], it["d"], **style))
        txt = it["label"]
        if it["kind"] in ("board", "toroid"):
            txt += f"\n{it['w']:.1f} × {it['d']:.1f}"
        ax.text(it["x"] + it["w"] / 2, it["y"] + it["d"] / 2 + (0 if low else 6), txt,
                ha="center", va="center", fontsize=7 if not low else 8)
        # depth dimension of every board and toroid, from the rear panel
        if it["kind"] in ("board", "toroid"):
            ax.annotate("", (it["x"] + 3, it["y"]), (it["x"] + 3, it["y"] + it["d"]),
                        arrowprops=dict(arrowstyle="<->", lw=0.6, color="0.3"))
    ax.annotate("", (0, CH_D + 8), (CH_W, CH_D + 8), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(CH_W / 2, CH_D + 12, f"{CH_W:.0f} mm fra i fianchi", ha="center", va="top",
            fontsize=8)
    ax.annotate("", (CH_W + 8, 0), (CH_W + 8, CH_D), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(CH_W + 11, CH_D / 2, f"{CH_D:.0f} mm", rotation=90, va="center", fontsize=8)
    ax.text(CH_W / 2, -5, "pannello posteriore (ingressi)", ha="center", fontsize=8)
    ax.text(CH_W / 2, CH_D + 24, "pannello frontale", ha="center", fontsize=8)
    bad = [c for c in p.checks if not c["ok"]]
    verdict = "CI STA" if not bad else "NON CI STA — " + "; ".join(
        f"{c['what']}" + (f" (mancano {c['shortfall_mm']} mm)" if c["shortfall_mm"] else "")
        for c in bad[:4])
    ax.set_title(f"{p.title}\n{verdict}", fontsize=10)
    ax.set_xlim(-10, CH_W + 25)
    ax.set_ylim(CH_D + 30, -15)
    ax.set_aspect("equal")
    ax.set_xlabel("mm dal fianco sinistro (vista dall'alto; tratteggio = sopra i 20 mm)")
    ax.set_ylabel("mm dal pannello posteriore")
    # Side section: depth (y) against height (z), every body projected.
    sx.add_patch(Rectangle((0, 0), CH_D, CH_H, fill=False, lw=2, ec="black"))
    for it in order:
        sx.add_patch(Rectangle((it["y"], it["z0"]), it["d"], it["z1"] - it["z0"],
                               fc=COLORS[it["kind"]], ec="black", alpha=0.25, lw=0.8))
    sx.text(2, CH_H - 6, "posteriore", fontsize=7)
    sx.text(CH_D - 2, CH_H - 6, "frontale", fontsize=7, ha="right")
    sx.set_xlim(-5, CH_D + 5)
    sx.set_ylim(-5, CH_H + 5)
    sx.set_aspect("equal")
    sx.set_xlabel("mm dal pannello posteriore (sezione laterale, tutti i corpi proiettati)")
    sx.set_ylabel("mm dal fondo")
    y = -0.32
    for n in p.notes:
        sx.text(0, y, n, fontsize=8, transform=sx.transAxes)
        y -= 0.09
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out_dir, f"assembly_{p.name}.{ext}"), dpi=150)
    plt.close(fig)


def main():
    audio = load(sys.argv[1])
    psu_dir = sys.argv[2]
    psu = load(os.path.join(psu_dir, "placement.json"))
    out_dir = sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    report = {"chassis_mm": [CH_W, CH_D, CH_H], "gap_mm": GAP, "zgap_mm": ZGAP,
              "audio_board_mm": audio["board_mm"], "supply_board_mm": psu["board_mm"],
              "assumed_heights_mm": {"control_axis": CONTROL_Z, "rca_rows": RCA_ROWS_Z,
                                     "iec_axis": IEC_Z, "standoff": STANDOFF},
              "variants": {}}
    for fn in (variant_l49a, variant_flat, variant_under):
        p = fn(audio, psu)
        run_checks(p)
        draw(p, out_dir)
        bad = [c for c in p.checks if not c["ok"]]
        report["variants"][p.name] = {
            "title": p.title, "fits": not bad, "failed": bad, "notes": p.notes,
            "toroid_distances_mm": toroid_distances(p), "items": p.items}
        print(f"{p.name:22s} fits={not bad}")
        for c in bad:
            print("    FAIL", c["what"], c["shortfall_mm"])
        for n in p.notes:
            print("    ", n)
        print("    toroids:", report["variants"][p.name]["toroid_distances_mm"])
    with open(os.path.join(out_dir, "assembly.json"), "w") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
