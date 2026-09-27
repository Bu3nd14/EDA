#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
psu_blocks_draw.py - l'alimentatore del preamplificatore, a blocchi (L42b).

DOCUMENTAZIONE DERIVATA, NON FONTE DI VERITA'.
La topologia sta in circuits/preamp/psu.py (ADR-048, ADR-049). Questo file
disegna soltanto. Se i due divergono, si corregge il disegno - o la topologia
alla sua fonte - mai le asserzioni qui sotto.

Esecuzione:
  /Users/roberto/EDA/env/venv/bin/python3 docs/preamp/schematic/psu_blocks_draw.py

Emette:
  psu_blocks.svg

E' il fratello di preamp_blocks_draw.py, con le stesse regole:
  - NON e' uno schematico e non e' coperto da scripts/check_schematic.py: un
    diagramma a blocchi omette i dispositivi di proposito;
  - ogni CIFRA stampata e' letta da circuits/preamp/psu.net, o calcolata da
    valori letti li' (le soglie del sorvegliante dai partitori e dal
    riferimento, le costanti di tempo dagli RC, la corrente di riferimento
    delle LDR da V5, VREF e R_REF). Nessuna cifra e' scritta nel testo;
  - ogni CONNESSIONE che il disegno afferma (Q505 fra VRELAY_REG e VRELAY, i
    quattro comparatori sul gate del sink di MUTE_CMD, K501 sul solo toroidale,
    Δ su PERMIT_T e Δ₂ su VR_T) e' asserita sulle net, e l'esecuzione muore se
    non e' vera. Non e' il 2e (check_relay_safe_state.py --timer), che asserisce
    l'intento coi suoi sabotaggi: qui si controlla solo che il disegno non menta.
PSU_NET punta le asserzioni a un'altra netlist (per farle fallire, L42b:
data/2026-09-27/L42b/script/sabotaggi.py); PSU_BLOCKS_SVG scrive altrove.
Le cifre MISURATE (Δ, tenute, tempi del sorvegliante) non stanno qui: stanno
nel dossier, lette dai dati dei lotti.
"""
import math
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")             # headless: deve precedere l'import schemdraw

import schemdraw                      # noqa: E402
import schemdraw.elements as elm      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SVG = os.environ.get("PSU_BLOCKS_SVG") or os.path.join(HERE, "psu_blocks.svg")
NETLIST = os.environ.get("PSU_NET") or os.path.join(REPO, "circuits", "preamp", "psu.net")

# =============================================================================
# I VALORI VENGONO DALLA NETLIST, NON DA QUI
# =============================================================================
if not os.path.exists(NETLIST):
    sys.exit(f"netlist assente: {NETLIST}\n"
             "rigenerala con: env/venv/bin/python3 circuits/preamp/psu.py")

_src = open(NETLIST, encoding="utf-8").read()
COMP = {}
for _m in re.finditer(r'\(comp\b.*?\(ref "([^"]+)"\).*?\(value "([^"]*)"\)'
                      r'.*?\(libsource\s*\(lib "([^"]*)"\)\s*\(part "([^"]*)"\)', _src, re.S):
    COMP[_m.group(1)] = (_m.group(2), _m.group(4))
PIN = {}
NETS = {}
for _chunk in re.split(r"\(net\s*\(code", _src.split("(nets", 1)[-1])[1:]:
    _nm = re.search(r'\(name "([^"]*)"\)', _chunk)
    if not _nm:
        continue
    for _r, _p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', _chunk):
        PIN[(_r, _p)] = _nm.group(1)
        NETS.setdefault(_nm.group(1), set()).add(f"{_r}.{_p}")


def v(ref):
    """Valore di un componente, dalla netlist. KeyError se non esiste."""
    return COMP[ref][0]


def ends(ref):
    """Le due net di un bipolo (pin 1, pin 2)."""
    return {PIN[(ref, "1")], PIN[(ref, "2")]}


def num(s):
    """'44.2k' -> 44200.0, '100n' -> 1e-7, '2200u' -> 2.2e-3, '1M' -> 1e6.
    'M' e' MEGA, convenzione KiCad (limitations #13)."""
    m = re.fullmatch(r"([0-9.]+)\s*([pnumkM]?)", s)
    assert m, f"valore non interpretabile: {s!r}"
    return float(m.group(1)) * {"": 1, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3,
                                "k": 1e3, "M": 1e6}[m.group(2)]


def only(pred, what):
    """Il solo componente che soddisfa pred; altrimenti muore."""
    got = [r for r in COMP if pred(r)]
    assert len(got) == 1, f"{what}: attesi 1, trovati {sorted(got)}"
    return got[0]


# ---- le tensioni: dai valori dei regolatori e del riferimento --------------
V_POS = float(re.search(r"(\d+(?:\.\d+)?)V$", v("U501")).group(1))
V_NEG = float(re.search(r"-(\d+(?:\.\d+)?)V$", v("U502")).group(1))
V_REL = float(re.search(r"(\d+(?:\.\d+)?)V$", v("U503")).group(1))
assert v("U504").startswith("MCP1703A-50"), f"U504 non e' il 5 V: {v('U504')}"
V_5 = 5.0                                     # MCP1703A-50xx: 5,0 V (la sigla)
V_REF = float(re.search(r"-(\d+(?:\.\d+)?)$", v("U507")).group(1))
assert COMP["U501"][1].startswith("TPS7A4701") and COMP["U503"][1].startswith("TPS7A4701")
assert COMP["U502"][1].startswith("TPS7A3301")
# il ramo negativo: la tensione la fa il partitore di FB (TPS7A3301, 1,176 V
# di riferimento, SBVS125): deve ridare la sigla entro 0,2 V
_fbm = [r for r in COMP if COMP[r][1] == "R" and "FB_M" in ends(r)]
_fbt = [r for r in _fbm if "VMINUS" in ends(r)]
_fbb = [r for r in _fbm if "GND" in ends(r)]
assert len(_fbt) == 1 and len(_fbb) == 1, f"partitore di FB_M: {_fbm}"
FB_TOP, FB_BOT = v(_fbt[0]), v(_fbb[0])
V_NEG_FB = 1.176 * (1 + num(FB_TOP) / num(FB_BOT))
assert abs(V_NEG_FB - V_NEG) < 0.2, f"U502: FB da' {V_NEG_FB:.3f} V, la sigla {V_NEG} V"

# ---- chi sta dove: la catena della potenza ---------------------------------
assert PIN[("U501", "1")] == "VPLUS" and PIN[("U502", "1")] == "VMINUS", "uscite dei rail"
assert PIN[("U503", "1")] == "VRELAY_REG" and PIN[("U504", "1")] == "VRELAY_REG", \
    "U503 non alimenta VRELAY_REG, o U504 (V5) non ne e' alimentato"
assert PIN[("U504", "3")] == "V5", "U504 non da' V5"
# Q505 (ADR-049) fra VRELAY_REG e VRELAY, e VRELAY va a J1 pin 4
assert {PIN[("Q505", "2")], PIN[("Q505", "3")]} == {"VRELAY_REG", "VRELAY"}, "Q505"
assert PIN[("J1", "4")] == "VRELAY" and PIN[("J1", "1")] == "VPLUS" and PIN[("J1", "3")] == "VMINUS"
# K501: la bobina su VRELAY_REG (prima di Q505), pilotata da MAINS_COIL
assert PIN[("K501", "A1")] == "VRELAY_REG" and PIN[("K501", "A2")] == "MAINS_COIL", "K501"
# i serbatoi e le tenute, per net
C_RAW_P = only(lambda r: COMP[r][1] == "C_Polarized" and "RAW_P" in ends(r), "serbatoio +")
C_RAW_M = only(lambda r: COMP[r][1] == "C_Polarized" and "RAW_M" in ends(r), "serbatoio -")
C_HOLD_P = only(lambda r: COMP[r][1] == "C_Polarized" and "VPLUS" in ends(r), "tenuta +")
C_HOLD_M = only(lambda r: COMP[r][1] == "C_Polarized" and "VMINUS" in ends(r), "tenuta -")
C_RAW_V = only(lambda r: COMP[r][1] == "C_Polarized" and "RAW_V" in ends(r), "serbatoio VRELAY")
C_HOLD_V = only(lambda r: COMP[r][1] == "C_Polarized" and "VRELAY_REG" in ends(r), "tenuta VRELAY")
assert v(C_RAW_P) == v(C_RAW_M) and v(C_HOLD_P) == v(C_HOLD_M), "i due rail non sono simmetrici"

# ---- il sorvegliante: le soglie CALCOLATE dai partitori e da VREF ------------
# U505, U506 A e B: le quattro uscite open-drain sul gate del sink di MUTE_CMD
for _p in (("U505", "1"), ("U505", "7"), ("U506", "1"), ("U506", "7")):
    assert PIN[_p] == "MUTE_G", f"{_p[0]} pin {_p[1]} non tira MUTE_G"
assert PIN[("Q501", "1")] == "MUTE_G" and PIN[("Q501", "3")] == "MUTE_CMD" \
    and PIN[("J4", "1")] == "MUTE_CMD", "il sink di MUTE_CMD"


RET = ("RLY_RET", "GND")                         # uniti da NT501 (la stella)


def divider(node, top, bottom):
    """(r_alto, r_basso) del partitore su una net: il resistore dal nodo a
    `top` e quello dal nodo a una delle net di `bottom`. Sul nodo possono
    stare altre cose (la rilettura del micro verso il suo ADC, 47k): non
    contano, ma i due capi devono esserci ed essere unici."""
    rs = [r for r in COMP if COMP[r][1] == "R" and node in ends(r)]
    hi = [r for r in rs if ends(r) == {node, top}]
    lo = [r for r in rs if (ends(r) - {node}) & set(bottom)]
    assert len(hi) == 1 and len(lo) == 1, f"partitore su {node}: {hi} verso {top}, {lo} verso {bottom}"
    return hi[0], lo[0]


def ratio(hi, lo):
    return (num(v(hi)) + num(v(lo))) / num(v(lo))


_ra, _rb = divider(PIN[("U505", "3")], "VPLUS", RET)       # + del canale A: il rail +
TRIP_P = V_REF * ratio(_ra, _rb)
# il rail -: nodo = VM + (VREF - VM) * Rvm / (Rref + Rvm), contro VREF/2 (pin 5)
_r_ref, _r_vm = divider(PIN[("U505", "6")], "VREF", ("VMINUS",))
_k = num(v(_r_vm)) / (num(v(_r_ref)) + num(v(_r_vm)))
_h1, _h2 = divider(PIN[("U505", "5")], "VREF", RET)
_vh = V_REF / ratio(_h1, _h2)
TRIP_M = (_vh - V_REF * _k) / (1 - _k)
_va, _vb = divider(PIN[("U506", "5")], "VRELAY_REG", RET)  # VRELAY_REG
TRIP_V = V_REF * ratio(_va, _vb)
assert 13.3 < TRIP_P < 13.8 and -13.8 < TRIP_M < -13.3, \
    f"soglie dei rail {TRIP_P:.2f} / {TRIP_M:.2f} V: ADR-046 dice |13,5 V|"
assert 10.5 < TRIP_V < 11.4, f"soglia di VRELAY {TRIP_V:.2f} V: sotto 11,4 V (P9)"
# il rivelatore di rete: C_MD caricato da V5 attraverso R_MD, contro VREF
_rmd = only(lambda r: COMP[r][1] == "R" and ends(r) == {"V5", "MD"}, "R_MD")
_cmd = only(lambda r: COMP[r][1] == "C" and "MD" in ends(r), "C_MD")
assert PIN[("U506", "2")] == "MD", "U506 A non legge MD"
TAU_MD = num(v(_rmd)) * num(v(_cmd)) * math.log(V_5 / (V_5 - V_REF))

# ---- il temporizzatore: Δ e Δ₂ (ADR-049) ------------------------------------
assert PIN[("U508", "3")] == "PERMIT_T" and PIN[("U508", "1")] == "PERMIT_G", "U508 A: Δ"
assert PIN[("Q502", "1")] == "PERMIT_G" and PIN[("Q502", "3")] == "PERMIT_CMD" \
    and PIN[("J4", "2")] == "PERMIT_CMD", "il sink di PERMIT_CMD"
assert PIN[("U508", "5")] == "VR_T" and PIN[("U508", "7")] == "VR_G", "U508 B: Δ₂"
assert PIN[("Q506", "1")] == "VR_G" and PIN[("Q505", "1")] == "SW_G", "VR_G -> Q506 -> Q505"
_rt_ = only(lambda r: COMP[r][1] == "R" and ends(r) == {"PERMIT_T", "RLY_RET"}, "R_T")
_ct_ = only(lambda r: COMP[r][1] == "C" and ends(r) == {"PERMIT_T", "RLY_RET"}, "C_T")
_rt2 = only(lambda r: COMP[r][1] == "R" and ends(r) == {"VR_T", "RLY_RET"}, "R_T2")
_ct2 = only(lambda r: COMP[r][1] == "C" and ends(r) == {"VR_T", "RLY_RET"}, "C_T2")
TAU_T = num(v(_rt_)) * num(v(_ct_))
TAU_T2 = num(v(_rt2)) * num(v(_ct2))
# D522: MUTE_G <= PERMIT_G (anodo su MUTE_G)
assert PIN[("D522", "2")] == "MUTE_G" and PIN[("D522", "1")] == "PERMIT_G", "D522"
# il micro: le quattro richieste escono da U509
MCU = v("U509")
for _n in ("MUTE_REQ", "PERMIT_REQ", "MAINS_REQ", "VRELAY_EN"):
    assert any(r == "U509" for (r, p), n in PIN.items() if n == _n), f"{_n} non esce da U509"

# ---- il pilota delle LDR (ADR-039, ADR-049) ---------------------------------
DAC = v("U510")
assert PIN[("U510", "8")] == "DAC_S" and PIN[("U510", "6")] == "DAC_P", "U510"
_rref = [r for r in COMP if COMP[r][1] == "R" and "V5" in ends(r)
         and any(n.startswith("EXP_N_") for n in ends(r))]
assert len(_rref) == 2 and v(_rref[0]) == v(_rref[1]), f"R_REF: {_rref}"
R_REF = v(_rref[0])
I_REF = (V_5 - V_REF) / num(R_REF)
_rlim = [r for r in COMP if COMP[r][1] == "R" and "RLY_RET" in ends(r)
         and any(n.startswith("EXP_FC_") for n in ends(r))]
assert len(_rlim) == 2 and v(_rlim[0]) == v(_rlim[1]), f"R_LIM: {_rlim}"
R_LIM = v(_rlim[0])
assert {PIN[("J3", "1")], PIN[("J3", "2")], PIN[("J3", "3")], PIN[("J3", "4")]} == \
    {"LDR_S_A", "LDR_S_K", "LDR_P_A", "LDR_P_K"}, "J3"


def it(x, nd=1):
    """Cifra all'italiana: virgola decimale, meno tipografico."""
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def cap_txt(s):
    return it(num(s) * 1e6, 0) + " µF"


def res_txt(s):
    x = num(s)
    return (it(x / 1e6, 0) + " MΩ" if x >= 1e6 else
            (it(x / 1e3, 0 if x % 1e3 == 0 else 1) + " kΩ" if x >= 1e3 else it(x, 0) + " Ω"))


# =============================================================================
# Disegno
# =============================================================================
INK, DIM, NETC = "#1a1a1a", "#555555", "#0b5394"
RED, GREEN, AMBER = "#c00000", "#1a7a1a", "#a06000"
FRAME = "#9a9a9a"

d = schemdraw.Drawing(show=False)
d.config(fontsize=9)


def txt(xy, s, size=9, color=INK, halign="center"):
    d.add(elm.Label().at((float(xy[0]), float(xy[1])))
          .label(s, loc="center", halign=halign, fontsize=size, color=color))


def box(cx, cy, w, h, lines, color=INK, lw=1.4, size=9, head_size=None):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d.add(elm.Line().at(p).to(q).color(color).linewidth(lw))
    n = len(lines)
    step = 0.62
    top = cy + (n - 1) * step / 2
    for i, ln in enumerate(lines):
        txt((cx, top - i * step), ln,
            size=(head_size or size + 1) if i == 0 else size - 0.5,
            color=color if i == 0 else DIM)


def panel(x0, y0, x1, y1, title, subtitle=None):
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d.add(elm.Line().at(p).to(q).color(FRAME).linewidth(0.9))
    txt((x0 + 0.4, y1 - 0.55), title, size=12, halign="left")
    if subtitle:
        txt((x0 + 0.4, y1 - 1.25), subtitle, size=8.5, color=DIM, halign="left")


def wire(x0, y0, x1, y1, color=INK, lw=1.4):
    d.add(elm.Line().at((x0, y0)).to((x1, y1)).color(color).linewidth(lw))


def arrow(x0, y0, x1, y1, color=INK, lw=1.4):
    d.add(elm.Arrow().at((x0, y0)).to((x1, y1)).color(color).linewidth(lw))


def dot(x, y, color=INK):
    d.add(elm.Dot().at((x, y)).color(color).fill(color))


# ---------------------------------------------------------------------------
txt((23.0, 33.2), "ALIMENTATORE — vista d'insieme (psu.py, seconda scheda)", size=17)
txt((23.0, 32.3),
    "rail lineari, VRELAY da un trasformatore proprio, sorvegliante in hardware, "
    "temporizzatore ibrido (ADR-048, ADR-049)", size=9.5, color=DIM)
txt((23.0, 31.55),
    "DIAGRAMMA A BLOCCHI — non è uno schematico. Cifre lette da psu.net o calcolate "
    "dai suoi valori; le cifre misurate stanno nel dossier.", size=8.5, color=AMBER)

# ---------------------------------------------------------------------------
# Pannello 1 - la potenza
# ---------------------------------------------------------------------------
panel(0.4, 20.4, 45.6, 31.0, "1 — Potenza: rete, rail audio, VRELAY, V5",
      "T2 resta acceso finché è acceso l'interruttore posteriore (lo standby); "
      "T1 solo col contatto di K501")
YT = 27.6                                     # T2: VRELAY e V5
YB = 23.2                                     # T1: i rail
box(3.2, 25.4, 4.4, 3.4, ["RETE", "IEC posteriore", "fusibile, bipolare"], head_size=10)
wire(5.4, 25.4, 6.2, 25.4)
wire(6.2, YB, 6.2, YT)
dot(6.2, 25.4)
arrow(6.2, YT, 7.4, YT)
box(9.2, YT, 3.6, 1.7, ["F501 → T2", "toroide piccolo"], size=8.5, head_size=9.5)
arrow(11.0, YT, 12.0, YT)
box(14.2, YT, 4.4, 1.7, [f"{v('D503')} + {v('D504')}", f"serbatoio {cap_txt(v(C_RAW_V))}"],
    size=8.5, head_size=9.5)
arrow(16.4, YT, 17.4, YT)
box(19.8, YT, 4.8, 1.7, [f"U503 {v('U503').split()[0]}", f"{it(V_REL, 0)} V → VRELAY_REG"],
    size=8.5, head_size=9.5)
wire(22.2, YT, 23.4, YT)
dot(23.4, YT)
wire(23.4, YT, 23.4, YT - 1.2)
box(23.4, YT - 1.75, 3.4, 1.1, [f"tenuta {cap_txt(v(C_HOLD_V))}"], size=8.5, head_size=8.5)
arrow(23.4, YT, 25.0, YT)
box(27.6, YT, 5.2, 1.7, ["Q505 " + v("Q505"), "interruttore di standby"], color=GREEN,
    size=8.5, head_size=9.5)
arrow(30.2, YT, 31.6, YT, color=NETC)
txt((31.8, YT + 0.32), "VRELAY → J1 pin 4", size=9.5, color=NETC, halign="left")
txt((31.8, YT - 0.34), "bobine della scheda audio; staccata in standby (NC-037)",
    size=8, color=DIM, halign="left")
wire(23.4, YT + 0.0, 23.4, YT + 1.6)
arrow(23.4, YT + 1.6, 25.0, YT + 1.6)
box(29.0, YT + 1.6, 8.0, 1.1, [f"U504 {v('U504')} → V5 ({it(V_5, 1)} V): logica, micro, DAC"],
    size=8.5, head_size=8.5)
# il ramo di T1, dietro K501
arrow(6.2, YB, 7.4, YB)
box(9.8, YB, 4.8, 1.7, ["K501 " + v("K501").split()[0], "bobina su VRELAY_REG"],
    color=RED, size=8.5, head_size=9.5)
arrow(12.2, YB, 13.2, YB)
box(15.2, YB, 4.0, 1.7, ["T1 → " + v("D501"), "toroide, 2 × sec."], size=8.5, head_size=9.5)
wire(17.2, YB, 18.0, YB)
wire(18.0, YB - 1.3, 18.0, YB + 1.3)
for yy, sgn, reg, craw, chold, vv, net, pin in (
        (YB + 1.3, "+", "U501", C_RAW_P, C_HOLD_P, V_POS, "VPLUS", 1),
        (YB - 1.3, "−", "U502", C_RAW_M, C_HOLD_M, -V_NEG, "VMINUS", 3)):
    arrow(18.0, yy, 19.2, yy)
    box(21.2, yy, 3.8, 1.1, [f"serb. {cap_txt(v(craw))}"], size=8.5, head_size=8.5)
    arrow(23.1, yy, 24.2, yy)
    box(27.0, yy, 5.4, 1.1, [f"{reg} {v(reg).split()[0]}  {it(vv, 0)} V"], size=8.5,
        head_size=8.5)
    arrow(29.7, yy, 30.8, yy)
    box(33.0, yy, 4.2, 1.1, [f"tenuta {cap_txt(v(chold))}"], size=8.5, head_size=8.5)
    arrow(35.1, yy, 36.2, yy, color=NETC)
    txt((36.4, yy), f"{net} → J1 pin {pin}", size=9.5, color=NETC, halign="left")
txt((23.0, 21.1), f"U502: {it(V_NEG_FB, 2)} V dal partitore di FB ({FB_TOP} / {FB_BOT}, "
    "1,176 V di riferimento)", size=8, color=DIM)

# ---------------------------------------------------------------------------
# Pannello 2 - il sorvegliante e il temporizzatore
# ---------------------------------------------------------------------------
panel(0.4, 8.6, 45.6, 20.0, "2 — Sorvegliante e temporizzatore: l'ordine sta in hardware",
      "i comparatori tirano MUTE_G a massa senza il firmware (ADR-048 p. 5); Δ e Δ₂ sono "
      "RC su comparatori, qualunque cosa faccia il micro (ADR-049)")
YS = 16.0
for i, (tit, sub) in enumerate((
        ("U505 A · rail +", f"scatta a {it(TRIP_P, 2)} V"),
        ("U505 B · rail −", f"scatta a {it(TRIP_M, 2)} V"),
        ("U506 A · rete", f"niente semionda per {it(TAU_MD * 1e3, 1)} ms"),
        ("U506 B · VRELAY_REG", f"scatta a {it(TRIP_V, 2)} V"))):
    cx = 4.2 + i * 6.6
    box(cx, YS, 6.0, 1.7, [tit, sub], color=RED, size=8.5, head_size=9.5)
    wire(cx, YS - 0.85, cx, YS - 1.6, color=RED)
wire(4.2, YS - 1.6, 24.0, YS - 1.6, color=RED)
txt((14.1, YS - 2.0), f"open-drain su MUTE_G · riferimento U507 {v('U507')} ({it(V_REF, 1)} V)",
    size=8, color=RED)
box(30.0, YS, 5.2, 1.7, [f"U509 {MCU}", "MUTE_REQ · PERMIT_REQ"], size=8.5, head_size=9.5)
wire(30.0, YS - 0.85, 30.0, YS - 1.6)
wire(24.0, YS - 1.6, 30.0, YS - 1.6)
dot(24.0, YS - 1.6)
arrow(24.0, YS - 1.6, 24.0, 13.2, color=RED)
box(24.0, 12.4, 5.2, 1.6, ["MUTE_G → Q501", "MUTE_CMD → J4 pin 1"], color=RED,
    size=8.5, head_size=9.5)
txt((24.0, 11.2), "D522: MUTE_G ≤ PERMIT_G", size=8, color=DIM)
box(35.8, 13.8, 7.6, 1.7, [f"Δ: U508 A su PERMIT_T", f"τ = {v(_rt_)} × {v(_ct_)} = "
                           f"{it(TAU_T * 1e3, 1)} ms"], color=GREEN, size=8.5, head_size=9.5)
arrow(32.6, YS, 35.8, 14.65, color=GREEN)
arrow(39.6, 13.8, 41.0, 13.8, color=NETC)
txt((41.2, 13.8), "PERMIT_CMD →\nJ4 pin 2", size=8.5, color=NETC, halign="left")
box(35.8, 10.6, 7.6, 1.7, [f"Δ₂: U508 B su VR_T", f"τ = {v(_rt2)} × {v(_ct2)} = "
                           f"{it(TAU_T2 * 1e3, 0)} ms"], color=GREEN, size=8.5, head_size=9.5)
wire(35.8, 12.95, 35.8, 11.45, color=GREEN)
arrow(39.6, 10.6, 41.0, 10.6, color=GREEN)
txt((41.2, 10.6), "VR_G → Q506\n→ Q505", size=8.5, color=GREEN, halign="left")
txt((12.0, 10.0), "MAINS_REQ → Q503 → bobina di K501: il toroidale si stacca a mute completo "
    "(lo spegnimento morbido, ADR-046)", size=8, color=DIM)
txt((12.0, 9.3), "Δ: PERMIT_CMD rilasciato non prima di Δ dopo la caduta della richiesta di "
    "mute; Δ₂: VRELAY a J1 dopo PERMIT", size=8, color=DIM)

# ---------------------------------------------------------------------------
# Pannello 3 - il pilota delle LDR
# ---------------------------------------------------------------------------
panel(0.4, 0.2, 45.6, 8.2, "3 — Il pilota delle LDR del mute (profilo v4, ADR-039, ADR-049)",
      "una stringa in serie e una in derivazione; il firmware calcola il codice dalla "
      "legge esponenziale e dalla temperatura")
YL = 4.2
box(4.8, YL, 6.4, 1.7, [f"U510 {DAC}", "DAC doppio, SPI dal micro"], size=8.5, head_size=9.5)
arrow(8.0, YL, 9.6, YL)
box(15.4, YL, 11.0, 1.9, ["convertitore esponenziale × 2 (U511, Q507–Q512)",
                          f"I_ref = (V5 − VREF) / {res_txt(R_REF)} = {it(I_REF * 1e6, 1)} µA",
                          f"coda limitata da {res_txt(R_LIM)}"],
    size=8.5, head_size=9.5)
arrow(20.9, YL, 22.6, YL)
box(26.2, YL, 7.0, 1.7, ["specchio → J3", "LED delle VTL5C4 (scheda audio)"],
    size=8.5, head_size=9.5)
arrow(29.7, YL, 31.2, YL, color=NETC)
txt((31.4, YL + 0.32), "LDR_S_A/K, LDR_P_A/K → J3", size=9.5, color=NETC, halign="left")
txt((31.4, YL - 0.34), "la corrente letta dal micro sul sense (calibrazione)",
    size=8, color=DIM, halign="left")
txt((23.0, 1.2), f"{len(COMP)} componenti in {os.path.basename(NETLIST)} — il disegno ne "
    "mostra i blocchi, non i dispositivi", size=8, color=DIM)

# ---------------------------------------------------------------------------
d.save(SVG)
print(f"SVG -> {SVG}")
print(f"valori letti da {os.path.relpath(NETLIST, REPO)} ({len(COMP)} componenti)")
print(f"  rail ..................... +{V_POS:g} / -{V_NEG:g} V (FB: {V_NEG_FB:.3f}), VRELAY_REG {V_REL:g} V, V5 {V_5:g} V")
print(f"  serbatoi / tenute ........ {v(C_RAW_P)} / {v(C_HOLD_P)} per rail, VRELAY {v(C_RAW_V)} / {v(C_HOLD_V)}")
print(f"  sorvegliante ............. +{TRIP_P:.3f} / {TRIP_M:.3f} V, VRELAY_REG {TRIP_V:.3f} V, rete {TAU_MD * 1e3:.2f} ms")
print(f"  temporizzatore ........... tau_T {TAU_T * 1e3:.2f} ms, tau_T2 {TAU_T2 * 1e3:.2f} ms")
print(f"  LDR ...................... I_ref {I_REF * 1e6:.2f} uA, R_LIM {R_LIM}")
if os.environ.get("PREVIEW_PNG"):
    d.save(os.environ["PREVIEW_PNG"], dpi=110)
    print("anteprima PNG ->", os.environ["PREVIEW_PNG"])
