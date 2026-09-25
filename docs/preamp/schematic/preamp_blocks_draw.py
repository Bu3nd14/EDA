#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preamp_blocks_draw.py - vista d'insieme del preamplificatore, a blocchi.

DOCUMENTAZIONE DERIVATA, NON FONTE DI VERITA'.
La topologia sta in circuits/preamp/preamp_audio.py e nel blocco che questa
istanzia otto volte (quattro per canale da L17, ADR-023),
circuits/preamp/gain_block.py. Questo file disegna
soltanto. Se i due divergono, si corregge il disegno - o la topologia alla
sua fonte - mai le asserzioni qui sotto.

Esecuzione:
  /Users/roberto/EDA/env/venv/bin/python3 \
      docs/preamp/schematic/preamp_blocks_draw.py

Emette:
  preamp_blocks.svg

QUESTO NON E' UNO SCHEMATICO, ED E' IMPORTANTE
----------------------------------------------
gain_block.svg e' uno SCHEMATICO: mostra 44 dispositivi, e
scripts/check_schematic.py lo confronta con la netlist in entrambe le
direzioni - niente inventato, niente omesso. Il blocco 2d di
scripts/run_tests.sh lo riesegue a ogni giro.

Questo file NON produce un manifesto e NON e' coperto da quel controllo,
perche' un diagramma a blocchi omette i dispositivi di proposito: e' la sua
funzione. Sarebbe sbagliato lasciar credere il contrario.

COSA E' VERIFICATO QUI, ALLORA
------------------------------
Le CIFRE ANNOTATE. Ogni valore stampato su questo disegno - 1 MOhm, 47 Ohm,
4,7 uF, 470k, 220k, 10k, 1,50k, 3,57k/866 - non e' scritto a mano nel testo
del disegno: viene LETTO da circuits/preamp/preamp_audio.net, la netlist
generata dalla fonte di verita', e le asserzioni sotto fanno fallire
l'esecuzione se non corrisponde. I guadagni "+3 dB" e "+10 dB" sono CALCOLATI
da R_f e dai due rami di R_g letti li', non dichiarati (L27, ADR-026).

E' un controllo piu' debole di check_schematic.py - non vede una connessione
sbagliata - ma copre l'errore piu' probabile in un documento derivato: la
cifra che resta indietro quando il circuito cambia. Vedi docs/limitations.md
#13 per il precedente in questo repo (una resistenza da 1 MOhm diventata
1 mOhm senza che nessuno strumento se ne accorgesse).

PERCHE' UN CANALE SOLO
----------------------
T3/ADR-006: esiste UN blocco di guadagno, progettato una volta e usato
quattro volte. Disegnare due canali identici non aggiunge informazione a una
vista d'insieme - mentre in uno schematico ogni dispositivo va mostrato.
Cio' che i due canali NON condividono e' visibile dove conta: il pannello 3
mostra i rele', che sono condivisi, e quali poli vanno a quale canale.
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
# PREAMP_BLOCKS_SVG lets scripts/run_tests.sh (block 2f) run this file for its
# ASSERTIONS without rewriting the versioned SVG: matplotlib stamps ids and a
# date, so every run would dirty the tree. Unset, the SVG lands next to here.
SVG = os.environ.get("PREAMP_BLOCKS_SVG") or os.path.join(HERE, "preamp_blocks.svg")
# PREAMP_AUDIO_NET points the assertions at another netlist - it exists so an
# assertion can be MADE TO FAIL on a known-bad netlist (L17 ran the ADR-023
# one against main's pre-L17 netlist) without touching the versioned file.
NETLIST = (os.environ.get("PREAMP_AUDIO_NET")
           or os.path.join(REPO, "circuits", "preamp", "preamp_audio.net"))

# =============================================================================
# I VALORI VENGONO DALLA NETLIST, NON DA QUI
# =============================================================================
if not os.path.exists(NETLIST):
    sys.exit(f"netlist assente: {NETLIST}\n"
             "rigenerala con: "
             "env/venv/bin/python3 circuits/preamp/preamp_audio.py")

_src = open(NETLIST, encoding="utf-8").read()
VAL = dict(re.findall(r'\(ref "([^"]+)"\)\s*\n\s*\(value "([^"]*)"\)', _src))
NETNAMES = set(re.findall(r'\(name "([^"]+)"\)', _src))


def v(ref):
    """Valore di un componente, dalla netlist. KeyError se non esiste."""
    return VAL[ref]


def same(refs, what):
    """Tutti i refs hanno lo stesso valore; lo restituisce. Altrimenti muore."""
    vals = {r: VAL[r] for r in refs}
    uniq = set(vals.values())
    assert len(uniq) == 1, f"{what}: valori diversi nella netlist -> {vals}"
    return uniq.pop()


# Zin del blocco A: la resistenza d'ingresso, una per canale (E3 >= 100 kOhm).
ZIN = same(["R113", "R313"], "resistenza d'ingresso blocco A")

# Il mute graduale a monte (ADR-038, L29b2): due LDR per canale. Il valore
# porta la parte e il ruolo ("VTL5C4 LDR_S_L"); qui si confronta la parte, e
# si asserisce che la serie stia fra il connettore d'ingresso e il nodo di
# R_IN e la derivazione fra quel nodo e GND. Lo stesso lo asserisce, per
# intento e con i sabotaggi, scripts/check_relay_safe_state.py (blocco 2e).
_ldr = {r: VAL[r].split() for r in ("U101", "U102", "U301", "U302")}
assert all(p[0] == "VTL5C4" for p in _ldr.values()), f"LDR diverse: {_ldr}"
assert [_ldr[r][1] for r in ("U101", "U102", "U301", "U302")] == [
    "LDR_S_L", "LDR_P_L", "LDR_S_R", "LDR_P_R"], f"ruoli delle LDR: {_ldr}"
_pins = {}
for _chunk in re.split(r"\(net\s*\(code", _src.split("(nets", 1)[-1])[1:]:
    _nm = re.search(r'\(name "([^"]*)"\)', _chunk).group(1)
    for _m in re.finditer(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', _chunk):
        _pins[(_m.group(1), _m.group(2))] = _nm
for _s, _p, _j, _rin in (("U101", "U102", "J101", "R113"),
                         ("U301", "U302", "J301", "R313")):
    _node = _pins[(_rin, "1")]
    assert {_pins[(_s, "3")], _pins[(_s, "4")]} == {_pins[(_j, "1")], _node}, (
        f"{_s}: la serie non sta fra {_j} e il nodo di R_IN ({_node})")
    assert {_pins[(_p, "3")], _pins[(_p, "4")]} == {_node, "GND"}, (
        f"{_p}: la derivazione non va dal nodo di R_IN a GND")
LDR_S = LDR_P = _ldr["U101"][0]

# Resistenze d'isolamento d'uscita, 3 per canale (47 Ohm, addendum di ADR-008;
# da L17 le due delle fisse stanno dopo il proprio buffer, T5/ADR-023).
RISO = same(["R161", "R164", "R261", "R361", "R364", "R461"], "isolamento uscite")

# Condensatori d'accoppiamento, 3 per canale (E8/ADR-007 addendum: 4,7 uF).
COUT = same(["C162", "C165", "C262", "C362", "C365", "C462"], "cap d'uscita")

# Resistenze di scarico: fisse 470k, principale 220k.
RBLEED_FIX = same(["R163", "R166", "R363", "R366"], "bleeder uscite fisse")
RBLEED_MAIN = same(["R263", "R463"], "bleeder uscita principale")
# L29e (ADR-044): lo scarico dal lato del condensatore, prima del deviatore di mute.
RBLEEDC_FIX = same(["R167", "R168", "R367", "R368"], "bleeder lato C, fisse")
RBLEEDC_MAIN = same(["R264", "R464"], "bleeder lato C, principale")

# Attenuatore: e' fuori scheda, appare come connettore a 3 pin il cui VALORE
# porta la resistenza del potenziometro a scatti (F4/ADR-009).
# Il valore del connettore porta il canale ("ATT_L 10k"), quindi si confronta
# solo l'ultimo campo - che e' la resistenza, la sola cosa che il disegno cita.
_att = {r: VAL[r].split()[-1] for r in ("J120", "J320")}
assert len(set(_att.values())) == 1, f"attenuatore diverso fra canali: {_att}"
ATT = _att["J120"]                           # "ATT_L 10k" -> "10k"

# Rete di controreazione del blocco B: e' cio' che i rele' commutano (ADR-004).
# Da L27 (ADR-026) R_f e' fissa e i rami di R_g sono DUE, in parallelo verso
# massa: R237/R437 attraverso K1, R242/R442 attraverso K5.
RF = same(["R235", "R435"], "R_f blocco B")
RG3 = same(["R237", "R437"], "R_g3 blocco B (K1)")
RG10 = same(["R242", "R442"], "R_g10 blocco B (K5)")


def ohms(s):
    """'1.50k' -> 1500.0 . Solo i suffissi che compaiono qui.
    NB: 'M' e' MEGA, convenzione KiCad - non la 'milli' di SPICE.
    E' la limitazione #13, e qui si legge un file KiCad."""
    m = re.fullmatch(r"([0-9.]+)\s*([kKmM]?)", s)
    assert m, f"valore non interpretabile: {s!r}"
    return float(m.group(1)) * {"": 1.0, "k": 1e3, "K": 1e3,
                                "m": 1e6, "M": 1e6}[m.group(2)]


# I guadagni NON sono dichiarati: sono calcolati da cio' che c'e'.
def _db(rg_ohm):
    return 20.0 * math.log10(1.0 + ohms(RF) / rg_ohm)


RG_PAR = 1.0 / (1.0 / ohms(RG3) + 1.0 / ohms(RG10))   # K1 e K5 chiusi
GAIN_LIN = 1.0 + ohms(RF) / RG_PAR
GAIN_DB = _db(RG_PAR)                 # +10 dB
GAIN3_LIN = 1.0 + ohms(RF) / ohms(RG3)
GAIN3_DB = _db(ohms(RG3))             # +3 dB: solo K1
GAIN_K5_DB = _db(ohms(RG10))          # solo K5: esiste solo come guasto di K1
assert 9.5 <= GAIN_DB <= 10.5, (
    f"E2 chiede +10 dB commutabili; R_f={RF} / (R_g3={RG3} || R_g10={RG10}) "
    f"danno {GAIN_DB:.2f} dB")
# ADR-026: il gradino intermedio di E2 e' +3 dB entro 0,1 dB.
assert 2.9 <= GAIN3_DB <= 3.1, (
    f"E2/ADR-026 chiedono +3 dB entro 0,1 dB; R_f={RF} / R_g3={RG3} danno "
    f"{GAIN3_DB:.2f} dB")
# ADR-026: nessuno stato dei contatti supera il +10 dB. Coi valori e' vero per
# costruzione solo se i rami sono IN PARALLELO: che lo siano lo asserisce la
# connettivita', piu' sotto, dopo che le net sono lette.
assert max(GAIN3_DB, GAIN_K5_DB) < GAIN_DB, (
    f"uno stato parziale ({GAIN3_DB:.2f} / {GAIN_K5_DB:.2f} dB) supera il "
    f"+10 dB ({GAIN_DB:.2f} dB)")

# Il blocco A non ha affatto una gamba di guadagno: nessuna rete AL_RG/AR_RG
# esiste nella netlist. E' cosi' che "guadagno 1" e' garantito per costruzione
# e non per scelta di valori.
for _n in ("AL_RG", "AR_RG"):
    assert _n not in NETNAMES, (
        f"il blocco A ha una rete {_n}: non e' piu' a guadagno unitario "
        "per costruzione, e questo disegno mente")

# I rele' sono CONDIVISI fra i canali: due di guadagno (K1, K5), tre di mute.
K_GAIN = v("K1")
K_GAIN10 = v("K5")
K_MUTE = [v(f"K{i}") for i in (2, 3, 4)]
assert ("GAIN" in K_GAIN and "GAIN" in K_GAIN10
        and all("MUTE" in k for k in K_MUTE)), \
    f"i rele' non sono quelli attesi: {K_GAIN}, {K_GAIN10}, {K_MUTE}"
RELAY_PN = K_GAIN.split()[0]                 # "G6K-2F-Y"

# =============================================================================
# ADR-023: OGNI USCITA FISSA HA IL PROPRIO BUFFER (L17, chiude NC-010)
# =============================================================================
# Il pannello 1 disegna un buffer per fissa. E' vero solo se la 47 ohm di ogni
# fissa parte dall'uscita di un blocco che NON e' il blocco A - cioe' se un
# apparecchio spento su una fissa non puo' portare in classe B il blocco che
# alimenta il percorso principale e l'altra fissa. Si verifica sulla netlist,
# per centinaia di riferimento: blocco A 1xx/3xx, buffer 5xx/6xx (canale L)
# e 7xx/8xx (canale R), come preamp_audio.py li numera. Un blocco e' fatto
# solo di riferimenti della propria centinaia; le 47 ohm, i condensatori e le
# scarichi delle fisse restano numerati dal canale (R161, R164, R361, R364).
# Fatto fallire in L17 sulla netlist di main prima dei buffer.
_NETS = {}
for _chunk in re.split(r"\(net\s*\(code", _src.split("(nets", 1)[-1])[1:]:
    _m = re.search(r'\(name "([^"]*)"\)', _chunk)
    if _m:
        _NETS[_m.group(1)] = set(re.findall(r'\(ref "([^"]+)"\)', _chunk))


def _hundreds(ref):
    num = re.sub(r"\D", "", ref)
    return int(num) // 100 if num else None


for _riso, _buf, _blkA, _fix in (("R161", 5, 1, "L_FIX1"), ("R164", 6, 1, "L_FIX2"),
                                 ("R361", 7, 3, "R_FIX1"), ("R364", 8, 3, "R_FIX2")):
    _nets = [n for n, refs in _NETS.items() if _riso in refs]
    assert _fix in _nets and len(_nets) == 2, (
        f"{_riso}: attesi due nodi, {_fix} e l'uscita di un blocco -> {_nets}")
    _src_net = next(n for n in _nets if n != _fix)
    _blocks = {_hundreds(r) for r in _NETS[_src_net] - {_riso}}
    assert _blocks == {_buf}, (
        f"{_riso} ({_fix}) parte da {_src_net}, che porta riferimenti delle "
        f"centinaia {sorted(b for b in _blocks if b is not None)}: ADR-023 vuole "
        f"che parta SOLO dall'uscita del buffer {_buf}xx. Se c'e' {_blkA}xx, e' "
        "il cablaggio di ADR-008 che NC-010 ha chiuso")
    # il buffer e' pilotato dal blocco A: un suo riferimento sta sul nodo
    # d'uscita del blocco A. Da L16 (ADR-027) quel nodo si trova dal capo
    # alto della scala del trim (R901 / R911), e l'attenuatore (J120 / J320)
    # NON ci sta: le fisse prendono il segnale PRIMA del trim, l'attenuatore
    # DOPO. Fino a L16 lo si cercava da J120, che ora e' sul COM di K7.
    _att = "J120" if _blkA == 1 else "J320"
    _rtop = "R901" if _blkA == 1 else "R911"
    # GND excluded: it carries every decoupling cap of block A
    _a_out = [n for n, refs in _NETS.items()
              if n != "GND" and _rtop in refs
              and any(_hundreds(r) == _blkA for r in refs - {_rtop})]
    assert len(_a_out) == 1 and any(_hundreds(r) == _buf for r in _NETS[_a_out[0]]), (
        f"il buffer {_buf}xx non e' pilotato dall'uscita del blocco {_blkA}xx "
        f"(nodi con {_rtop}: {_a_out})")
    assert _att not in _NETS[_a_out[0]], (
        f"{_att} (l'attenuatore) sta sull'uscita del blocco {_blkA}xx: il trim "
        "di ADR-027 non e' fra il blocco A e l'attenuatore")
    # guadagno 1 per costruzione, come il blocco A: nessuna rete di R_g
    _tag = ("F1" if _buf in (5, 7) else "F2") + ("L" if _blkA == 1 else "R")
    assert f"{_tag}_RG" not in NETNAMES, (
        f"il buffer {_tag} ha una rete {_tag}_RG: non e' piu' a guadagno "
        "unitario per costruzione")

# =============================================================================
# ADR-026: I DUE RAMI DI R_g SONO IN PARALLELO, OGNUNO COL PROPRIO RELE'
# =============================================================================
# Per canale: R_f, R_g3 e R_g10 condividono la stessa net (FB); l'altro capo di
# R_g3 sta su una net col solo K1, quello di R_g10 su una net col solo K5. E'
# questo, non i valori, che garantisce che nessuno stato dei contatti superi il
# +10 dB e che nessun contatto stia in serie a un altro. Fatto fallire in L27.
for _rf, _rg3, _rg10 in (("R235", "R237", "R242"), ("R435", "R437", "R442")):
    _fb = [n for n, refs in _NETS.items() if {_rf, _rg3, _rg10} <= refs]
    assert len(_fb) == 1, (
        f"{_rf}, {_rg3} e {_rg10} non condividono un nodo: i rami di R_g non "
        "sono in parallelo sulla controreazione (ADR-026)")
    for _rg, _k in ((_rg3, "K1"), (_rg10, "K5")):
        _far = [n for n, refs in _NETS.items() if _rg in refs and n != _fb[0]]
        assert len(_far) == 1 and _NETS[_far[0]] - {_rg} == {_k}, (
            f"l'altro capo di {_rg} deve andare al solo {_k} -> "
            f"{[(n, sorted(_NETS[n])) for n in _far]}")

# =============================================================================
# ADR-027: UN SOLO TRIM, SUL RAMO VARIABILE, FRA IL BLOCCO A E L'ATTENUATORE
# =============================================================================
# Le attenuazioni si CALCOLANO dai valori della netlist, col carico
# dell'attenuatore sul nodo scelto, e devono cadere a -6 e -12 dB entro
# 0,1 dB. Sul pin alto dell'attenuatore (J120 / J320) c'e' solo il COM di K7.
# Quale contatto e' il reset, l'interblocco col mute e le spie li asserisce il
# 2e (check_relay_safe_state.py). Fatto fallire in L16: vedi il report.
TR1 = same(["R901", "R911"], "trim R1")
TR2 = same(["R902", "R912"], "trim R2")
TR3 = same(["R903", "R913"], "trim R3")


def _par(a, b):
    return a * b / (a + b)


_ra = ohms(ATT)
_low6 = _par(ohms(TR2) + ohms(TR3), _ra)
TRIM6_DB = 20 * math.log10(_low6 / (ohms(TR1) + _low6))
_low12 = _par(ohms(TR3), _ra)
TRIM12_DB = 20 * math.log10(_low12 / (ohms(TR1) + ohms(TR2) + _low12))
assert abs(TRIM6_DB + 6.0) <= 0.1 and abs(TRIM12_DB + 12.0) <= 0.1, (
    f"il trim {TR1}/{TR2}/{TR3} col carico di {ATT} da' {TRIM6_DB:.3f} e "
    f"{TRIM12_DB:.3f} dB: fuori da -6 e -12 dB +/- 0,1 (ADR-027)")
for _j in ("J120", "J320"):
    _top = [n for n, refs in _NETS.items() if refs == {_j, "K7"}]
    assert len(_top) == 1, (
        f"il pin alto dell'attenuatore {_j} non sta sul solo COM di K7: "
        f"{[(n, sorted(r)) for n, r in _NETS.items() if _j in r]}")
K_TRIM = [v(f"K{i}") for i in (6, 7, 8, 9, 10)]
assert ("PERMIT" in K_TRIM[0] and all("TRIM" in k for k in K_TRIM[1:3])
        and all("SPIA" in k for k in K_TRIM[3:])), \
    f"i rele' del trim non sono quelli attesi: {K_TRIM}"
TRIM_PN = K_TRIM[1].split()[0]                # "G6KU-2F-Y"


def pretty(val, unit):
    """'470k' -> '470 kOhm' scritto come si scrive: cifra, prefisso, unita'.
    Il valore resta quello LETTO dalla netlist - qui si formatta soltanto,
    e la virgola decimale e' quella italiana."""
    m = re.fullmatch(r"([0-9.]+)\s*([a-zA-Z]?)", val)
    assert m, f"valore non formattabile: {val!r}"
    num, pfx = m.group(1).replace(".", ","), m.group(2)
    return f"{num} {pfx}{unit}".replace("  ", " ")


OHM = "Ω"                                # Ω
R_ISO = pretty(RISO, OHM)
C_OUT = pretty(COUT, "F").replace("u", "µ")     # 4,7 µF
R_ZIN = pretty(ZIN, OHM)
R_BFIX = pretty(RBLEED_FIX, OHM)
R_BMAIN = pretty(RBLEED_MAIN, OHM)
R_BCFIX = pretty(RBLEEDC_FIX, OHM)
R_BCMAIN = pretty(RBLEEDC_MAIN, OHM)
R_ATT = pretty(ATT, OHM)
R_F, R_G3, R_G10 = pretty(RF, OHM), pretty(RG3, OHM), pretty(RG10, OHM)

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
    """Un blocco. lines[0] e' il titolo, il resto e' didascalia."""
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
    return (x0, x1)


def dashed_frame(x0, y0, x1, y1, title=None, color=FRAME):
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d.add(elm.Line().at(p).to(q).color(color).linewidth(0.9)
              .linestyle("--"))
    if title:
        txt((x0 + 0.15, y1 - 0.42), title, size=8.5, color=color,
            halign="left")


def panel(x0, y0, x1, y1, title, subtitle=None):
    for p, q in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                 ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        d.add(elm.Line().at(p).to(q).color(FRAME).linewidth(0.9))
    txt((x0 + 0.4, y1 - 0.55), title, size=12, halign="left")
    if subtitle:
        txt((x0 + 0.4, y1 - 1.25), subtitle, size=8.5, color=DIM,
            halign="left")


def wire(x0, y0, x1, y1, color=INK, lw=1.4):
    d.add(elm.Line().at((x0, y0)).to((x1, y1)).color(color).linewidth(lw))


def arrow(x0, y0, x1, y1, color=INK, lw=1.4):
    d.add(elm.Arrow().at((x0, y0)).to((x1, y1)).color(color).linewidth(lw))


def dot(x, y, color=INK):
    d.add(elm.Dot().at((x, y)).color(color).fill(color))


def series(cx, cy, label, w=2.6, h=1.15):
    """Un componente in SERIE sulla linea di segnale."""
    return box(cx, cy, w, h, [label], size=9.5, head_size=9.5)


# Profondita' totale di un ramo verso massa, cornice compresa. Le righe di
# segnale vanno distanziate ALMENO di questo, o i rami sfondano il pannello
# sotto - cosa che la prima versione di questo disegno faceva.
SHUNT_DEPTH = 3.15


def shunt_to_gnd(x, y, label, sub=None, color=RED, drop=1.0):
    """Un ramo che va A MASSA dalla linea di segnale: scarico, LDR.
    Disegnato in derivazione, non in serie: in un diagramma a blocchi la
    differenza si vede solo se si disegna cosi'. Il mute al jack, da L29e, e'
    un deviatore IN SERIE (ADR-044) e si disegna con box()."""
    dot(x, y)
    wire(x, y, x, y - drop, color=color, lw=1.2)
    box(x, y - drop - 0.62, 2.4, 1.25,
        [label] + ([sub] if sub else []), color=color, lw=1.2, size=8,
        head_size=8.5)
    wire(x, y - drop - 1.25, x, y - drop - 1.62, color=color, lw=1.2)
    d.add(elm.Ground().at((x, y - drop - 1.62)).color(color))


# ---------------------------------------------------------------------------
# Intestazione
# ---------------------------------------------------------------------------
txt((23.0, 32.2), "PREAMPLIFICATORE DI LINEA — vista d'insieme", size=17)
txt((23.0, 31.3),
    "guadagno unitario, Classe A a discreti su ogni percorso ascoltabile, "
    "nessun operazionale nel percorso del segnale (T1/ADR-003, ADR-023)",
    size=9.5, color=DIM)
txt((23.0, 30.55),
    "DIAGRAMMA A BLOCCHI — non è uno schematico e non è coperto da "
    "scripts/check_schematic.py.  Lo schematico del blocco di guadagno "
    "è gain_block.svg.", size=8.5, color=AMBER)

# ---------------------------------------------------------------------------
# Pannello 1 - ingresso, blocco A, le due uscite a livello fisso
# ---------------------------------------------------------------------------
panel(0.4, 18.4, 45.6, 30.0,
      "1 — Ingresso, blocco A, buffer e uscite a livello fisso",
      "un canale; il secondo è identico (T3/ADR-006: un blocco, otto "
      "istanze). I relè sono condivisi — pannello 3.")

# Tre righe, distanziate di almeno SHUNT_DEPTH: i rami verso massa scendono,
# e devono avere posto senza attraversare la riga sotto.
YS = 27.0                                  # uscita fissa 1 - Singxer
Y = 22.9                                   # ingresso, blocco A, uscita fissa 2
YA = 19.3                                  # prosecuzione verso l'attenuatore
assert YS - Y >= SHUNT_DEPTH and Y - YA >= SHUNT_DEPTH, \
    "righe troppo vicine: i rami verso massa sfonderebbero quella sotto"

box(3.0, Y, 4.0, 2.7,
    ["4 × RCA", "sbilanciati", "F1"], head_size=10)
arrow(5.0, Y, 6.3, Y)
box(9.0, Y, 5.2, 2.7,
    ["SELETTORE", "a relè", "ADR-009"], head_size=10)
# Da L16 (ADR-027) il trim non sta qui: e' uno solo, sul ramo dell'uscita
# variabile, sulla riga YA piu' sotto. Da L29b2 (ADR-038) fra il selettore e
# il blocco A sta il mute graduale: una LDR in serie e una verso massa, sul
# nodo di R_IN. Il comando dei LED e' fuori dal segnale (ADR-022), sulla J3.
wire(11.6, Y, 12.4, Y)
series(14.0, Y, f"LDR serie {LDR_S}", w=3.2)
wire(15.6, Y, 17.6, Y)
shunt_to_gnd(17.6, Y, f"LDR {LDR_P}", "mute graduale")
arrow(17.6, Y, 19.8, Y)
box(23.0, Y, 5.6, 3.4,
    ["BLOCCO A", "guadagno 1 (0 dB)", f"Zin {R_ZIN}",
     "coppia JFET cascodata"], head_size=11)

# Nodo di diramazione: il blocco A pilota TRE ingressi - i due buffer delle
# fisse e l'attenuatore. Da L17 (ADR-023, che supera ADR-008) nessuna uscita
# fissa sta piu' sul suo nodo di controreazione: le asserzioni ADR-023 sopra
# lo verificano sulla netlist.
wire(25.8, Y, 27.6, Y)
dot(27.6, Y)
wire(27.6, YA, 27.6, YS)                   # montante verticale

for yy, dest, tag, kref, bname in (
        (YS, "Singxer SA-1 V2", "uscita fissa 1", "K2", "BUFFER F1"),
        (Y, "Stax SRM-T1", "uscita fissa 2", "K3", "BUFFER F2")):
    dot(27.6, yy)
    wire(27.6, yy, 28.4, yy)
    box(29.9, yy, 3.0, 1.9, [bname, "guadagno 1", "ADR-023"],
        size=8.5, head_size=9.5)
    wire(31.4, yy, 32.0, yy)
    series(33.1, yy, R_ISO, w=2.2)
    wire(34.2, yy, 34.8, yy)
    series(35.9, yy, C_OUT, w=2.2)
    # L29e (ADR-044, geometria iii): il mute e' un DEVIATORE in serie fra il
    # lato del condensatore e il jack - NC a massa sul lato C, NO al jack.
    wire(37.0, yy, 37.6, yy)
    shunt_to_gnd(37.6, yy, R_BCFIX, "scarico lato C")
    wire(37.6, yy, 38.3, yy)
    box(39.3, yy, 2.0, 1.4, [f"MUTE {kref}", "deviatore"], color=RED,
        lw=1.2, size=7.5, head_size=8.5)
    wire(40.3, yy, 40.9, yy)
    shunt_to_gnd(40.9, yy, R_BFIX, "scarico jack")
    arrow(40.9, yy, 41.6, yy)
    txt((41.8, yy + 0.32), dest, size=9.5, halign="left")
    txt((41.8, yy - 0.34), tag, size=8, color=DIM, halign="left")

# Prosecuzione verso il pannello 2 attraverso il TRIM (L16, ADR-027): e' uno
# solo e sta SOLO su questo ramo - le due fisse qui sopra prendono il segnale
# prima di lui. Sta sulla riga piu' bassa e finisce presto: sopra di lei
# scendono i rami verso massa dell'uscita fissa 2. Le attenuazioni scritte
# sono quelle CALCOLATE dalla netlist e asserite sopra.
dot(27.6, YA)
wire(27.6, YA, 28.2, YA)
_t6 = f"{TRIM6_DB:.1f}".replace(".", ",").replace("-", "−")
_t12 = f"{TRIM12_DB:.1f}".replace(".", ",").replace("-", "−")
box(31.0, YA, 5.6, 1.5,
    [f"TRIM 0 / {_t6} / {_t12} dB", f"K7 K8 {TRIM_PN}, bistabili"],
    size=7.5, head_size=8.5)
arrow(33.8, YA, 34.6, YA, color=NETC)
txt((34.8, YA), "all'ATTENUATORE — pann. 2", size=8, color=NETC,
    halign="left")

# ---------------------------------------------------------------------------
# Pannello 2 - attenuatore, blocco B, uscita principale
# ---------------------------------------------------------------------------
panel(0.4, 8.0, 45.6, 17.6,
      "2 — Attenuatore, blocco B, uscita principale",
      "è il solo ramo il cui livello si regola: le due uscite del pannello 1 "
      "hanno un volume proprio a bordo apparecchio.")

YM = 14.0

txt((1.0, YM), "dal BLOCCO A", size=9, color=NETC, halign="left")
arrow(4.6, YM, 5.9, YM)
box(9.2, YM, 6.2, 3.2,
    ["ATTENUATORE", f"{R_ATT} a scatti", "commutatore rotativo",
     "resistenze 0,1% — F4"], head_size=11)
arrow(12.3, YM, 13.6, YM)
box(17.0, YM, 6.2, 3.4,
    ["BLOCCO B", "0 / +3 / +10 dB commutabili",
     f"R_f {R_F} / R_g {R_G3} ∥ {R_G10}", "stesso blocco del pannello 1"],
    head_size=11)
arrow(20.1, YM, 21.6, YM)
series(23.4, YM, R_ISO)
wire(24.7, YM, 25.6, YM)
series(27.0, YM, C_OUT)
wire(28.3, YM, 29.6, YM)
# L29e (ADR-044): come sulle fisse, il deviatore di mute in serie.
shunt_to_gnd(29.6, YM, R_BCMAIN, "scarico lato C")
wire(29.6, YM, 30.6, YM)
box(31.7, YM, 2.2, 1.4, ["MUTE K4", "deviatore"], color=RED, lw=1.2,
    size=7.5, head_size=8.5)
wire(32.8, YM, 33.4, YM)
shunt_to_gnd(33.4, YM, R_BMAIN, "scarico jack")
arrow(33.4, YM, 34.1, YM)
txt((34.3, YM + 0.32), "conrad-johnson Evolution 250", size=9.5,
    halign="left")
txt((34.3, YM - 0.34), f"= MV50 in triodo, 30 W, Zin 100 k{OHM}",
    size=8, color=DIM, halign="left")

# Le due note stanno SOTTO i rami verso massa, non accanto: alla loro altezza
# la meta' destra del pannello e' occupata.
txt((16.0, 9.9),
    "K1 e K5 a riposo → guadagno 1.   K1 → R_g3 a massa → "
    f"{GAIN3_LIN:.3f}".replace(".", ",") + "× = +"
    f"{GAIN3_DB:.2f}".replace(".", ",") + " dB.   K1 + K5 → R_g3 ∥ R_g10 → "
    f"{GAIN_LIN:.3f}".replace(".", ",") + "× = +"
    f"{GAIN_DB:.2f}".replace(".", ",") + " dB",
    size=8.5, color=GREEN)
txt((16.0, 9.2),
    "i relè commutano rami di R_g verso massa, MAI R_f in serie: l'anello di "
    "controreazione non si apre durante la commutazione (V2)",
    size=8.5, color=GREEN)
txt((16.0, 8.55),
    "rami in parallelo (ADR-026): nessuno stato dei contatti, saldati "
    "compresi, supera il +10 dB",
    size=8.5, color=GREEN)

# ---------------------------------------------------------------------------
# Pannello 3 - cio' che i due canali condividono
# ---------------------------------------------------------------------------
panel(0.4, 0.2, 45.6, 7.9,
      "3 — Relè, alimentazione, e cosa sta su quale scheda",
      "è qui che i due canali si toccano: due relè di guadagno, tre di "
      "mute e i cinque del trim servono entrambi.")

box(6.6, 4.95, 11.0, 2.4,
    [f"K1 K5 — GUADAGNO   {RELAY_PN}",
     "K1 → R_g3, K5 → R_g10; polo 1 canale L, polo 2 canale R",
     "servono NORMALMENTE APERTI: a riposo 0 dB"], head_size=10)

box(19.6, 4.95, 12.2, 2.4,
    [f"K2 K3 K4 — MUTE   {RELAY_PN}",
     "2 scambi ciascuno = 6 linee (3 uscite × 2 canali)",
     "deviatori (ADR-044): a riposo lato C a massa, jack staccati"],
    color=RED, head_size=10)

# ADR-027 (L16): il permissivo K6 sul comando del mute, i due bistabili del
# trim e le loro due spie. Chi fa cosa lo asserisce il 2e.
box(35.4, 4.95, 18.6, 2.4,
    [f"K6 PERMESSO {RELAY_PN} · K7 K8 TRIM, K9 K10 SPIA {TRIM_PN}",
     "K6 sul comando del mute, due NC in serie: il trim si comanda "
     "solo in mute (F8)",
     "bistabili: il valore resta all'uscita dal mute; i LED leggono K9 K10"],
    color=GREEN, head_size=9.5, size=8.5)

txt((23.0, 3.30),
    f"Contatti NO/NC del {RELAY_PN} (L21) e del {TRIM_PN} (L16) letti dal "
    "datasheet e asseriti sulla netlist da check_relay_safe_state.py. Il "
    "progetto fallisce in sicurezza solo se restano quelli giusti:",
    size=9, color=AMBER)
txt((23.0, 2.70),
    "a relè diseccitati — alimentazione assente, o temporizzatore non ancora "
    "rilasciato — il guadagno deve essere 0 dB e i jack staccati. Mancare "
    "il verso significa un transitorio d'accensione negli elettrostatici "
    "Stax.", size=8.5, color=AMBER)

# Le tre cornici tratteggiate: il titolo sta in ALTO e il testo piu' in
# basso. Nella prima versione si sovrapponevano.
dashed_frame(1.6, 0.5, 15.4, 2.4, "SCHEDA INGRESSI (a monte)")
txt((8.5, 1.15), "selettore d'ingresso.  Non è in preamp_audio.py:\n"
                 "il trim sì, da L16 (ADR-027)",
    size=8, color=DIM)

dashed_frame(16.2, 0.5, 30.0, 2.4, "SCHEDA AUDIO (P4)")
txt((23.1, 1.15), "blocchi A, B e 2 buffer ×2 canali, trim, contatti di mute,\n"
                  "LDR del mute graduale (comando dei LED fuori scheda, J3),\n"
                  f"{len(VAL)} componenti — preamp_audio.py + trim.py",
    size=8, color=DIM)

dashed_frame(30.8, 0.5, 44.4, 2.4, "PANNELLO E ALIMENTAZIONE")
txt((37.6, 1.15), "attenuatore rotativo e commutatori sul pannello;\n"
                  "alimentatore su scheda separata, massa a stella (P4)",
    size=8, color=DIM)

# ---------------------------------------------------------------------------
d.save(SVG)
print(f"SVG -> {SVG}")
print(f"valori letti da {os.path.relpath(NETLIST, REPO)} "
      f"({len(VAL)} componenti nella netlist)")
print(f"  Zin blocco A ............ {ZIN}")
print(f"  isolamento uscite ....... {RISO} ohm  x3 per canale")
print(f"  accoppiamento d'uscita .. {COUT}     x3 per canale")
print(f"  scarico fisse / main .... {RBLEED_FIX} / {RBLEED_MAIN}")
print(f"  scarico lato C (ADR-044)  {RBLEEDC_FIX} / {RBLEEDC_MAIN}")
print(f"  attenuatore ............. {ATT}")
print(f"  guadagno +3 dB (K1) ..... 1 + {RF}/{RG3} = "
      f"{GAIN3_LIN:.4f}x = +{GAIN3_DB:.3f} dB")
print(f"  guadagno +10 dB (K1+K5) . 1 + {RF}/({RG3}||{RG10}) = "
      f"{GAIN_LIN:.4f}x = +{GAIN_DB:.3f} dB   (solo K5: +{GAIN_K5_DB:.3f} dB)")
print("  rele' ................... " + " | ".join([K_GAIN, K_GAIN10] + K_MUTE))
print("  trim (ADR-027) ........... " + " | ".join(K_TRIM)
      + f"   {TR1}/{TR2}/{TR3}: {TRIM6_DB:.3f} / {TRIM12_DB:.3f} dB")
if os.environ.get("PREVIEW_PNG"):
    d.save(os.environ["PREVIEW_PNG"], dpi=110)
    print("anteprima PNG ->", os.environ["PREVIEW_PNG"])
