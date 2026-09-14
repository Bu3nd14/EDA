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
4,7 uF, 470k, 220k, 10k, 1,50k/698 - non e' scritto a mano nel testo del
disegno: viene LETTO da circuits/preamp/preamp_audio.net, la netlist generata
dalla fonte di verita', e le asserzioni sotto fanno fallire l'esecuzione se
non corrisponde. Il guadagno "+10 dB" e' CALCOLATO da R_f e R_g letti li',
non dichiarato.

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

# Resistenze d'isolamento d'uscita, 3 per canale (47 Ohm, addendum di ADR-008;
# da L17 le due delle fisse stanno dopo il proprio buffer, T5/ADR-023).
RISO = same(["R161", "R164", "R261", "R361", "R364", "R461"], "isolamento uscite")

# Condensatori d'accoppiamento, 3 per canale (E8/ADR-007 addendum: 4,7 uF).
COUT = same(["C162", "C165", "C262", "C362", "C365", "C462"], "cap d'uscita")

# Resistenze di scarico: fisse 470k, principale 220k.
RBLEED_FIX = same(["R163", "R166", "R363", "R366"], "bleeder uscite fisse")
RBLEED_MAIN = same(["R263", "R463"], "bleeder uscita principale")

# Attenuatore: e' fuori scheda, appare come connettore a 3 pin il cui VALORE
# porta la resistenza del potenziometro a scatti (F4/ADR-009).
# Il valore del connettore porta il canale ("ATT_L 10k"), quindi si confronta
# solo l'ultimo campo - che e' la resistenza, la sola cosa che il disegno cita.
_att = {r: VAL[r].split()[-1] for r in ("J120", "J320")}
assert len(set(_att.values())) == 1, f"attenuatore diverso fra canali: {_att}"
ATT = _att["J120"]                           # "ATT_L 10k" -> "10k"

# Rete di controreazione del blocco B: e' cio' che il rele' commuta (ADR-004).
RF = same(["R235", "R435"], "R_f blocco B")
RG = same(["R237", "R437"], "R_g blocco B")


def ohms(s):
    """'1.50k' -> 1500.0 . Solo i suffissi che compaiono qui.
    NB: 'M' e' MEGA, convenzione KiCad - non la 'milli' di SPICE.
    E' la limitazione #13, e qui si legge un file KiCad."""
    m = re.fullmatch(r"([0-9.]+)\s*([kKmM]?)", s)
    assert m, f"valore non interpretabile: {s!r}"
    return float(m.group(1)) * {"": 1.0, "k": 1e3, "K": 1e3,
                                "m": 1e6, "M": 1e6}[m.group(2)]


# Il guadagno alternativo NON e' dichiarato: e' calcolato da cio' che c'e'.
GAIN_LIN = 1.0 + ohms(RF) / ohms(RG)
GAIN_DB = 20.0 * math.log10(GAIN_LIN)
assert 9.5 <= GAIN_DB <= 10.5, (
    f"E2 chiede +10 dB commutabili; R_f={RF} / R_g={RG} danno {GAIN_DB:.2f} dB")

# Il blocco A non ha affatto una gamba di guadagno: nessuna rete AL_RG/AR_RG
# esiste nella netlist. E' cosi' che "guadagno 1" e' garantito per costruzione
# e non per scelta di valori.
for _n in ("AL_RG", "AR_RG"):
    assert _n not in NETNAMES, (
        f"il blocco A ha una rete {_n}: non e' piu' a guadagno unitario "
        "per costruzione, e questo disegno mente")

# I rele' sono CONDIVISI fra i canali: uno di guadagno, tre di mute.
K_GAIN = v("K1")
K_MUTE = [v(f"K{i}") for i in (2, 3, 4)]
assert "GAIN" in K_GAIN and all("MUTE" in k for k in K_MUTE), \
    f"i rele' non sono quelli attesi: {K_GAIN}, {K_MUTE}"
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
    # d'uscita del blocco A, quello dell'attenuatore (J120 / J320)
    _att = "J120" if _blkA == 1 else "J320"
    # GND excluded: it carries J120 pin 3 and every decoupling cap of block A
    _a_out = [n for n, refs in _NETS.items()
              if n != "GND" and _att in refs
              and any(_hundreds(r) == _blkA for r in refs - {_att})]
    assert len(_a_out) == 1 and any(_hundreds(r) == _buf for r in _NETS[_a_out[0]]), (
        f"il buffer {_buf}xx non e' pilotato dall'uscita del blocco {_blkA}xx "
        f"(nodi con {_att}: {_a_out})")
    # guadagno 1 per costruzione, come il blocco A: nessuna rete di R_g
    _tag = ("F1" if _buf in (5, 7) else "F2") + ("L" if _blkA == 1 else "R")
    assert f"{_tag}_RG" not in NETNAMES, (
        f"il buffer {_tag} ha una rete {_tag}_RG: non e' piu' a guadagno "
        "unitario per costruzione")


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
R_ATT = pretty(ATT, OHM)
R_F, R_G = pretty(RF, OHM), pretty(RG, OHM)

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
    """Un ramo che va A MASSA dalla linea di segnale: mute, scarico.
    Disegnato in derivazione, non in serie - ADR-012 lo argomenta, e in un
    diagramma a blocchi la differenza si vede solo se si disegna cosi'."""
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
arrow(11.6, Y, 12.9, Y)
box(15.9, Y, 5.2, 2.7,
    ["TRIM d'ingresso", "0 / −6 / −12 dB", "ponticelli, ADR-011"],
    head_size=10)
arrow(18.5, Y, 19.8, Y)
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
    wire(37.0, yy, 38.2, yy)
    shunt_to_gnd(38.2, yy, R_BFIX, "scarico")
    wire(38.2, yy, 40.2, yy)
    shunt_to_gnd(40.2, yy, f"MUTE {kref}", "in derivazione")
    arrow(40.2, yy, 41.6, yy)
    txt((41.8, yy + 0.32), dest, size=9.5, halign="left")
    txt((41.8, yy - 0.34), tag, size=8, color=DIM, halign="left")

# Prosecuzione verso il pannello 2. Sta sulla riga piu' bassa e finisce
# presto: sopra di lei scendono i rami verso massa dell'uscita fissa 2.
dot(27.6, YA)
arrow(27.6, YA, 29.6, YA, color=NETC)
txt((29.9, YA), "all'ATTENUATORE — pannello 2", size=9, color=NETC,
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
    ["BLOCCO B", "0 / +10 dB commutabili",
     f"R_f {R_F} / R_g {R_G}", "stesso blocco del pannello 1"], head_size=11)
arrow(20.1, YM, 21.6, YM)
series(23.4, YM, R_ISO)
wire(24.7, YM, 25.6, YM)
series(27.0, YM, C_OUT)
wire(28.3, YM, 29.6, YM)
shunt_to_gnd(29.6, YM, R_BMAIN, "scarico")
wire(29.6, YM, 31.8, YM)
shunt_to_gnd(31.8, YM, "MUTE K4", "in derivazione")
arrow(31.8, YM, 34.0, YM)
txt((34.3, YM + 0.32), "conrad-johnson Evolution 250", size=9.5,
    halign="left")
txt((34.3, YM - 0.34), f"= MV50 in triodo, 30 W, Zin 100 k{OHM}",
    size=8, color=DIM, halign="left")

# Le due note stanno SOTTO i rami verso massa, non accanto: alla loro altezza
# la meta' destra del pannello e' occupata.
txt((16.0, 9.9),
    "K1 a riposo → R_g flottante → guadagno 1.    "
    "K1 eccitato → R_g a massa → 1 + R_f/R_g = "
    f"{GAIN_LIN:.3f}".replace(".", ",") + "× = +"
    f"{GAIN_DB:.2f}".replace(".", ",") + " dB",
    size=8.5, color=GREEN)
txt((16.0, 9.2),
    "il relè commuta R_g verso massa, MAI R_f in serie: l'anello di "
    "controreazione non si apre durante la commutazione (V2)",
    size=8.5, color=GREEN)

# ---------------------------------------------------------------------------
# Pannello 3 - cio' che i due canali condividono
# ---------------------------------------------------------------------------
panel(0.4, 0.2, 45.6, 7.9,
      "3 — Relè, alimentazione, e cosa sta su quale scheda",
      "è qui che i due canali si toccano: un solo relè di guadagno e tre di "
      "mute servono entrambi.")

box(6.6, 4.95, 11.0, 2.4,
    [f"K1 — GUADAGNO   {RELAY_PN}",
     "2 scambi: polo 1 → R_g canale L, polo 2 → R_g canale R",
     "serve NORMALMENTE APERTO: a riposo 0 dB"], head_size=10)

box(20.4, 4.95, 13.0, 2.4,
    [f"K2 K3 K4 — MUTE   {RELAY_PN}",
     "2 scambi ciascuno = 6 linee (3 uscite × 2 canali)",
     "servono NORMALMENTE CHIUSI: a riposo uscite a massa"],
    color=RED, head_size=10)

box(35.0, 4.95, 11.6, 2.4,
    ["J1 — ALIMENTAZIONE",
     "V+ / GND / V− / V_relè",
     "±15 V regolati (E7/ADR-015)"], head_size=10)

txt((23.0, 3.30),
    f"NON ANCORA CONFERMATO quale contatto del {RELAY_PN} sia NO e quale NC "
    "(lotto L8). Il progetto fallisce in sicurezza solo se sono quelli "
    "giusti:", size=9, color=AMBER)
txt((23.0, 2.70),
    "a relè diseccitati — alimentazione assente, o temporizzatore non ancora "
    "rilasciato — il guadagno deve essere 0 dB e le uscite a massa. Mancare "
    "il verso significa un transitorio d'accensione negli elettrostatici "
    "Stax.", size=8.5, color=AMBER)

# Le tre cornici tratteggiate: il titolo sta in ALTO e il testo piu' in
# basso. Nella prima versione si sovrapponevano.
dashed_frame(1.6, 0.5, 15.4, 2.4, "SCHEDA INGRESSI (a monte)")
txt((8.5, 1.15), "selettore + trim.  Non è in preamp_audio.py:\n"
                 "è un'altra scheda, e non interagisce coi blocchi",
    size=8, color=DIM)

dashed_frame(16.2, 0.5, 30.0, 2.4, "SCHEDA AUDIO (P4)")
txt((23.1, 1.15), "blocchi A, B e 2 buffer ×2 canali, contatti di mute,\n"
                  f"{len(VAL)} componenti — circuits/preamp/preamp_audio.py",
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
print(f"  attenuatore ............. {ATT}")
print(f"  guadagno alternativo .... 1 + {RF}/{RG} = "
      f"{GAIN_LIN:.4f}x = +{GAIN_DB:.3f} dB   (E2 chiede +10 dB)")
print("  rele' ................... " + K_GAIN + " | " + " | ".join(K_MUTE))
if os.environ.get("PREVIEW_PNG"):
    d.save(os.environ["PREVIEW_PNG"], dpi=110)
    print("anteprima PNG ->", os.environ["PREVIEW_PNG"])
