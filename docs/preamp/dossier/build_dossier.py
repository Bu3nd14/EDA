#!/usr/bin/env python3
"""Costruisce il dossier del preamplificatore dai dati versionati.

    /usr/bin/python3 docs/preamp/dossier/build_dossier.py
    /usr/bin/python3 docs/preamp/dossier/build_dossier.py --standalone <file.html>

REGOLA CHE GOVERNA QUESTO FILE, ed e' la stessa del diagramma a blocchi di
L1: **nessuna cifra del dossier e' scritta a mano.** Ogni numero che
compare nella pagina viene letto dai file versionati in
docs/preamp/data/2026-09-14/ e calcolato qui.

L32: i dati sono quelli di L27 (tre modi di guadagno, ADR-026) e di L16 (il
trim, ADR-027). **Nessun numero viene da data/2026-09-09**, che racconta il
circuito col THAT320: un percorso che contiene quella data fa rifiutare il
generatore.

Ogni numero passa per una seconda strada indipendente, e se le due divergono
oltre la tolleranza dichiarata lo script **rifiuta e non scrive niente**, come
export_fab.sh sulla DRC:
  1. le curve CSV contro le `print` che ngspice ha stampato nel .log;
  2. le tabelle scritte con `echo` contro le `print` o le `meas` dello stesso
     log, riga per riga; una cella vuota e' un rifiuto (docs/limitations.md #26);
  3. la cifra di headroom di NC-009 contro quella che stampa
     data/2026-09-14/L16/esplorazione/script/headroom_nc009.py sugli stessi CSV.

E la provenienza dei modelli non e' scritta a mano: e' letta dagli `.include`
di ogni deck e dai nomi di modello che il blocco istanzia.

Non ha flag di bypass.
"""

import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "preamp", "data", "2026-09-14")
L27 = os.path.join(DATA, "L27", "dopo")
L16 = os.path.join(DATA, "L16", "dopo")
L16X = os.path.join(DATA, "L16", "esplorazione")
TB = os.path.join(REPO, "spice", "preamp", "tb")
SCHEM = os.path.join(REPO, "docs", "preamp", "schematic")
# L32b: i due schemi si COPIANO accanto a index.html e si collegano da li'.
# Un <img src="../schematic/..."> esce dalla cartella della pagina, e un
# visualizzatore che serve solo quella cartella li perdeva in silenzio,
# mentre le figure fig_*.svg accanto alla pagina restavano visibili.
SCHEMATICS = ("gain_block.svg", "preamp_blocks.svg")
FORBIDDEN = "2026-09-09"

MODES = ("0db", "3db", "10db")
MLAB = {"0db": "0 dB", "3db": "+3 dB", "10db": "+10 dB"}
MNOM = {"0db": 0.0, "3db": 3.0, "10db": 10.0}

PM_MIN = 60.0          # V1, ADR-019
E5_MAX = 10.0          # µV, E5
E6 = 2.7               # V RMS, E6 (FiiO K11 a fondo scala)
TA = 60.0              # °C nel telaio, ADR-021
RTH_MJE = 62.5         # °C/W, RθJA MJE15032/33 TO-220, ADR-021
TJ_MAX = 125.0         # °C, P7

sys.path.insert(0, HERE)
import svgplot as sp                                   # noqa: E402

FAILURES = []


def refuse(msg):
    FAILURES.append(msg)


def rel(p):
    return os.path.relpath(p, REPO)


def src(root, *parts):
    """Ogni percorso di dati passa di qui: il guardiano del lotto L32."""
    p = os.path.join(root, *parts)
    if FORBIDDEN in p:
        raise SystemExit(f"RIFIUTATO: {rel(p)} viene dai dati del {FORBIDDEN}, "
                         "che raccontano un altro circuito. Nessun file e' stato scritto.")
    return p


# ---------------------------------------------------------------- dati ----
def load_csv(path):
    """Legge un CSV di run_simulation.sh (intestazione col0..colN)."""
    rows = []
    with open(path) as f:
        head = f.readline()
        if not head.startswith("col0"):
            raise SystemExit(f"intestazione inattesa in {rel(path)}: {head!r}")
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(v) for v in line.split(",")])
    if not rows:
        raise SystemExit(f"{rel(path)} e' vuoto")
    return rows


def load_table(path, nrows):
    """Legge una tabella scritta da `echo` (intestazione con nomi).

    Rifiuta le celle vuote: e' la forma in cui una `meas` fallita in silenzio
    arriva in tabella (docs/limitations.md #26). E rifiuta un numero di righe
    diverso da quello che i cicli del deck producono."""
    with open(path) as f:
        rows = list(csv.DictReader(f))
    empty = [(i, k) for i, r in enumerate(rows) for k, v in r.items()
             if v is None or v.strip() == ""]
    if empty:
        refuse(f"{rel(path)}: {len(empty)} celle vuote, la prima alla riga "
               f"{empty[0][0] + 2}, colonna {empty[0][1]} (#26)")
    if len(rows) != nrows:
        refuse(f"{rel(path)}: attese {nrows} righe, trovate {len(rows)}")
    return rows


def num(r, k):
    try:
        return float(r[k])
    except (TypeError, ValueError, KeyError):
        return float("nan")


def pair(rows, k):
    """La k-esima coppia (scala, valore) -> (xs, ys)."""
    return [r[2 * k] for r in rows], [r[2 * k + 1] for r in rows]


def interp(xs, ys, x):
    """Interpolazione lineare in log(x), la griglia `dec` dei deck."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(1, len(xs)):
        if xs[i] >= x:
            x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
            if x1 == x0:
                return y0
            t = (math.log10(x) - math.log10(x0)) / (math.log10(x1) - math.log10(x0))
            return y0 + t * (y1 - y0)
    return ys[-1]


def crossing(xs, ys, level=0.0):
    """Primo attraversamento di `level` scendendo. Ritorna (x, indice)."""
    for i in range(1, len(ys)):
        if (ys[i - 1] - level) >= 0 >= (ys[i] - level):
            y0, y1 = ys[i - 1] - level, ys[i] - level
            if y1 == y0:
                return xs[i], i
            t = y0 / (y0 - y1)
            lx = math.log10(xs[i - 1]) + t * (math.log10(xs[i]) - math.log10(xs[i - 1]))
            return 10 ** lx, i
    return None, None


def log_print(path, key):
    """Le occorrenze di `key = valore` stampate da `print`, in ordine.

    ngspice stampa una `meas` incolonnata (`z1k                 =  5.87602e+01`)
    e una `print` compatta (`z1k = 5.876022e+01`): qui solo la seconda, che ha
    piu' cifre. Prenderle entrambe raddoppierebbe i conteggi."""
    pat = re.compile(r"^" + re.escape(key) + r" = (\S+)\s*$")
    return _grep(path, pat)


def log_meas(path, key):
    """Le occorrenze di una `meas` incolonnata, per i deck che non fanno
    `print` e scrivono la tabella direttamente da `$&var`."""
    pat = re.compile(r"^" + re.escape(key) + r"\s{2,}=\s+(\S+)")
    return _grep(path, pat)


def _grep(path, pat):
    out = []
    with open(path) as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                try:
                    out.append(float(m.group(1)))
                except ValueError:
                    pass
    return out


def at(lst, i):
    return lst[i] if i < len(lst) else None


def check(label, mine, theirs, rtol):
    """Confronta il mio numero con quello di ngspice. Registra, non alza."""
    if theirs is None:
        refuse(f"{label}: ngspice non ha stampato il valore di riferimento")
        return mine
    if mine is None:
        refuse(f"{label}: il valore non si ricava dal CSV")
        return theirs
    den = abs(theirs) if abs(theirs) > 1e-12 else 1.0
    err = abs(mine - theirs) / den
    if not err <= rtol:
        refuse(f"{label}: calcolato {mine:.6g}, ngspice {theirs:.6g} "
               f"(scarto relativo {err:.2e} > {rtol:.0e})")
    return theirs        # si pubblica il numero del simulatore, non il mio


def cross_table(label, rows, col, logvals, rtol=1e-5):
    """Una colonna di tabella `echo` contro i valori del log, riga per riga.

    La tabella e il log vengono dalla stessa variabile, quindi il controllo non
    prova il simulatore: prova che la tabella sia intera, allineata e non
    sovrascritta (docs/limitations.md #25, #26)."""
    if len(rows) != len(logvals):
        refuse(f"{label}: {len(rows)} righe in tabella, {len(logvals)} valori nel log")
        return
    for i, (r, v) in enumerate(zip(rows, logvals)):
        t = num(r, col)
        den = abs(v) if abs(v) > 1e-12 else 1.0
        if not abs(t - v) / den <= rtol:
            refuse(f"{label}: riga {i + 2}, colonna {col}: tabella {r.get(col)!r}, "
                   f"log {v:.7g}")
            return


def capval(s):
    """'4.7n' -> 4.7e-9. Solo i suffissi che i deck usano."""
    return float(s[:-1]) * {"f": 1e-15, "p": 1e-12, "n": 1e-9}[s[-1]]


# ---------------------------------------------------------- formattazione --
def fmt(v, nd=3, unit=""):
    if v is None:
        return "&mdash;"
    if abs(v) >= 1000 or (abs(v) < 0.01 and v != 0):
        s = f"{v:.{nd}g}"
    else:
        s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
        if s in ("", "-"):
            s = "0"
    return f"{s}{unit}"


def it(v, nd=3, unit=""):
    """Numero con la virgola decimale italiana."""
    return fmt(v, nd, unit).replace(".", ",")


def fx(v, nd=2):
    """Decimali fissi, virgola italiana, meno tipografico."""
    return f"{v:.{nd}f}".replace(".", ",").replace("-", "&minus;")


def sg(v, nd=2):
    """Come fx, col segno sempre esplicito."""
    return f"{v:+.{nd}f}".replace(".", ",").replace("-", "&minus;")


def it_sci(v, nd=3):
    """Numero piccolo come m·10^e in HTML, con la virgola italiana."""
    if v == 0:
        return "0"
    e = math.floor(math.log10(abs(v)))
    m = f"{v / 10 ** e:.{nd - 1}f}".replace(".", ",").replace("-", "&minus;")
    return f'{m}&middot;10<sup>{str(e).replace("-", "&minus;")}</sup>'


def lab_c(s):
    """'2.611k' -> '2,611 kΩ', '3.3n' -> '3,3 nF': etichette dei cicli dei deck."""
    s = s.strip()
    if s[-1] in "fpn":
        return s[:-1].replace(".", ",") + " " + s[-1] + "F"
    if s[-1] == "k":
        return s[:-1].replace(".", ",") + " kΩ"
    if s[-1] == "m":
        return s[:-1].replace(".", ",") + " mΩ"
    return s.replace(".", ",") + " Ω"


def verdict(ok, yes="conforme", no="non conforme"):
    return f'<td class="{"ok" if ok else "no"}">{yes if ok else no}</td>'


# ------------------------------------------------------------ provenienza --
# Il nome della parte per ciascun modello istanziato. Sono nomi, non numeri:
# cio' che il dossier AFFERMA - costruttore o segnaposto, e con quale KF -
# viene dai file, non da questa tabella.
PART = {"LSK489X": "LSK489", "LS350": "LS352", "NSS2N5551": "2N5551",
        "PSS2N5401": "2N5401", "NMJE15032": "MJE15032", "PMJE15033": "MJE15033",
        "D1N4148": "1N4148"}
PLACEHOLDER_LIB = "spice/preamp/placeholder_devices.lib"


def _models_in(path):
    """{NOME: testo della .model, righe di continuazione comprese}."""
    out, cur = {}, None
    with open(path) as f:
        for ln in f:
            s = ln.strip()
            if s.lower().startswith(".model"):
                name = s.split()[1].split("(")[0].upper()
                out[name] = s
                cur = name
            elif s.startswith("+") and cur:
                out[cur] += " " + s[1:]
            else:
                cur = None
    return out


def _resolve_include(arg):
    if arg.startswith("@REPO@/"):
        return arg[len("@REPO@/"):]
    for root in ("spice/", "models/"):
        k = arg.find("/" + root)
        if os.path.isabs(arg) and k >= 0:
            return arg[k + 1:]
    return None


_PROV_CACHE = {}


def provenance(deckpath):
    """I modelli che un deck simula davvero, e da dove vengono.

    Legge gli `.include` del deck; i modelli definiti in ciascun file incluso;
    i nomi di modello istanziati (righe Q/J/D) dagli `.inc`/`.subckt` del
    blocco. Un modello e' «del costruttore» se sta in models/ con la sua
    .provenance.json, «segnaposto» se sta in placeholder_devices.lib. KF assente
    vale 0 in ngspice, e cosi' e' riportato."""
    if deckpath in _PROV_CACHE:
        return _PROV_CACHE[deckpath]
    incs = []
    with open(deckpath) as f:
        for ln in f:
            m = re.match(r"^\.include\s+(\S+)", ln.strip(), re.I)
            if m:
                r = _resolve_include(m.group(1))
                if r is None or not os.path.exists(os.path.join(REPO, r)):
                    refuse(f"provenienza {rel(deckpath)}: include non risolvibile {m.group(1)}")
                    continue
                incs.append(r)
    defined, used = {}, set()
    for inc in incs:
        p = os.path.join(REPO, inc)
        for name, text in _models_in(p).items():
            defined.setdefault(name, (inc, text))
        if inc.endswith((".inc", ".subckt")):
            with open(p) as f:
                for ln in f:
                    t = ln.split()
                    if t and t[0][0].upper() in "QJD" and len(t) >= 4:
                        used.add(t[-1].upper())
    out = []
    for name in sorted(used):
        if name not in defined:
            refuse(f"provenienza {rel(deckpath)}: il modello {name} non e' definito "
                   "da nessun file incluso")
            continue
        inc, text = defined[name]
        vendor = (inc.startswith("models/") and os.path.exists(
            os.path.join(REPO, os.path.splitext(inc)[0] + ".provenance.json")))
        placeholder = inc == PLACEHOLDER_LIB
        if not (vendor or placeholder):
            refuse(f"provenienza {rel(deckpath)}: {name} viene da {inc}, che non e' "
                   "ne' models/ con provenance ne' il file dei segnaposto")
            continue
        m = re.search(r"\bKF\s*=\s*([0-9.eE+-]+)", text, re.I)
        out.append({"model": name, "part": PART.get(name, name), "file": inc,
                    "vendor": vendor, "kf": float(m.group(1)) if m else 0.0})
    if not out:
        refuse(f"provenienza {rel(deckpath)}: nessun modello istanziato trovato")
    _PROV_CACHE[deckpath] = out
    return out


def prov_line(deck, datadir, deckdir=TB, note=""):
    ms = provenance(os.path.join(deckdir, deck))
    ven = sorted({m["part"] for m in ms if m["vendor"]})
    ph = sorted({m["part"] for m in ms if not m["vendor"]})
    kf = "tutti KF = 0" if all(m["kf"] == 0 for m in ms) else "KF &ne; 0 su qualche modello"
    return (f'<p class="prov">Deck <code>{html_escape(rel(os.path.join(deckdir, deck)))}</code>'
            f' &middot; dati <code>{html_escape(rel(datadir))}/</code>{note}<br>'
            f'Modelli del costruttore: <strong>{", ".join(ven) or "nessuno"}</strong>'
            f' &middot; segnaposto scritti a mano: <strong>{", ".join(ph) or "nessuno"}</strong>'
            f' (NC-017) &middot; {kf}: nessun rumore 1/f (NC-004)</p>')


# --------------------------------------------------------------- misure ---
RS_AC = ("1.5", "430", "2500", "10k")
AC_ORDER = [(m, r) for m in MODES for r in RS_AC]


def measure_response():
    """Risposta in frequenza, tb_ac di L27: 3 modi x 4 sorgenti."""
    d = src(L27, "tb_ac")
    log = os.path.join(d, "tb_ac.log")
    keys = {k: log_print(log, k) for k in ("g1k", "g20", "g20k", "g100k")}
    for nm, lst in keys.items():
        if len(lst) != len(AC_ORDER):
            refuse(f"tb_ac.log: attese {len(AC_ORDER)} occorrenze di {nm}, trovate {len(lst)}")
    out = {}
    for key in [(m, r) for m in MODES for r in ("1.5", "2500")]:
        idx = AC_ORDER.index(key)
        rows = load_csv(os.path.join(d, f"tb_ac_{key[0]}_{key[1]}.csv"))
        f, gdb = pair(rows, 0)
        tag = f"tb_ac {key[0]}/{key[1]}"
        out[key] = {"f": f, "gdb": gdb}
        for k, fr in (("g20", 20), ("g1k", 1000), ("g20k", 20000), ("g100k", 100000)):
            out[key][k] = check(f"{tag} @{fr} Hz", interp(f, gdb, fr),
                                at(keys[k], idx), 2e-3)
    rows = load_csv(os.path.join(d, "tb_ac.csv"))
    f, gdb = pair(rows, 0)
    out["lf"] = {"f": f, "gdb": gdb}
    for k, lk, fr in (("g1k", "g1kb", 1000), ("g20", "g20b", 20), ("g5", "g5b", 5)):
        out["lf"][k] = check(f"tb_ac LF @{fr} Hz", interp(f, gdb, fr),
                             at(log_print(log, lk), 0), 2e-3)
    return out


def adr014(resp):
    """NC-007: `shape` e' la claim di ADR-014 (20 kHz riferito a 1 kHz, sorgente
    2500 contro 1,5 ohm); `level` e' lo scarto assoluto, cioe' il partitore fra
    la sorgente e la Zin."""
    shape, level = {}, {}
    for m in MODES:
        hi, lo = resp[(m, "2500")], resp[(m, "1.5")]
        shape[m] = (hi["g20k"] - hi["g1k"]) - (lo["g20k"] - lo["g1k"])
        level[m] = {f: hi[f] - lo[f] for f in ("g1k", "g20k")}
    return shape, level


def _loop_table(d, name, nrows, logname):
    tab = load_table(os.path.join(d, name), nrows)
    log = os.path.join(d, logname)
    for col, key in (("fcross_hz", "fcross"), ("pm_deg", "pmarg"), ("tdb_10hz", "tdc")):
        cross_table(f"{rel(os.path.join(d, name))} [{col}]", tab, col, log_print(log, key))
    return tab


def pm(r):
    return num(r, "pm_deg")


def measure_v1():
    """V1 come la vuole ADR-024: sonda al jack, minimo della spazzata fino a
    4,7 nF; blocco A col cablaggio <= 1 nF."""
    v = {}
    # --- blocco B, col trim (L16): sorgenti fino a (10 k + 442)/4 = 2,611 k
    d = src(L16, "tb_loop")
    tab = _loop_table(d, "tb_loop_margini.csv", 660, "tb_loop.log")
    v["B_dir"] = d
    B = {}
    for m in MODES:
        jack = [r for r in tab if r["mode"] == m and r["pos"] == "1"]
        node = [r for r in tab if r["mode"] == m and r["pos"] == "2"]
        w = min(jack, key=pm)
        wn = min(node, key=pm)
        same = lambda r: r["rsrc"] == w["rsrc"] and r["rload"] == w["rload"]  # noqa: E731
        curve = sorted([r for r in jack if same(r)], key=lambda r: capval(r["cprobe"]))
        curve_n = sorted([r for r in node if same(r)], key=lambda r: capval(r["cprobe"]))
        at47 = [r for r in curve if r["cprobe"] == "4.7n"]
        B[m] = {"min": pm(w), "w": w, "node_min": pm(wn), "wn": wn, "n": len(jack),
                "curve": ([capval(r["cprobe"]) for r in curve], [pm(r) for r in curve]),
                "curve_n": ([capval(r["cprobe"]) for r in curve_n], [pm(r) for r in curve_n]),
                "at47": pm(at47[0]) if at47 else None}
    v["B"] = B

    # --- le 396 righe di L27 devono tornare identiche nella tabella di L16
    d27 = src(L27, "tb_loop")
    tab27 = _loop_table(d27, "tb_loop_margini.csv", 396, "tb_loop.log")
    key = lambda r: (r["mode"], r["rsrc"], r["pos"], r["cprobe"], r["rload"])  # noqa: E731
    idx16 = {key(r): r for r in tab}
    worst = 0.0
    for r in tab27:
        r16 = idx16.get(key(r))
        if r16 is None:
            refuse(f"tb_loop: la riga L27 {key(r)} manca nella tabella L16")
            break
        worst = max(worst, abs(pm(r) - pm(r16)))
    if not worst <= 1e-9:
        refuse(f"tb_loop: le righe comuni a L27 e L16 differiscono fino a {worst:.3g} gradi")
    v["B_L27_scarto"] = worst

    # --- Bode: le curve versionate sono quelle di L27, sorgente 2,5 k, 100 k
    bode = {}
    for m in MODES:
        cand = [r for r in tab27 if r["mode"] == m and r["pos"] == "1"
                and r["rsrc"] == "2.5k" and r["rload"] == "100k"]
        w = min(cand, key=pm)
        rows = load_csv(os.path.join(d27, f"tb_loop_att2k5_{m}_{w['cprobe']}.csv"))
        f, tdb = pair(rows, 0)
        _, tph = pair(rows, 1)
        fc, _ = crossing(f, tdb, 0.0)
        # G2 e' l'ingresso INVERTENTE: il margine e' |fase| dove |T| = 0 dB.
        pmv = abs(interp(f, tph, fc)) if fc else None
        bode[m] = {"f": f, "tdb": tdb, "tph": tph, "C": w["cprobe"],
                   "fcross": check(f"Bode {m} {w['cprobe']} f_incrocio", fc,
                                   num(w, "fcross_hz"), 5e-3),
                   "pmarg": check(f"Bode {m} {w['cprobe']} margine", pmv,
                                  abs(pm(w)), 5e-3),
                   "tdc": check(f"Bode {m} {w['cprobe']} |T| a 10 Hz",
                                interp(f, tdb, 10), num(w, "tdb_10hz"), 2e-3)}
    v["bode"] = bode
    v["bode_dir"] = d27

    # --- blocco A (L16): senza trim e col partitore, scala 2 (845/464/464)
    d = src(L16, "tb_loop_blockA")
    base = load_table(os.path.join(d, "tb_loop_blockA.csv"), 32)
    trim = load_table(os.path.join(d, "tb_loop_blockA_trim.csv"), 96)
    log = os.path.join(d, "tb_loop_blockA.log")
    for col, k in (("fcross_hz", "fcross"), ("pm_deg", "pmarg"), ("tdb_10hz", "tdc")):
        cross_table(f"tb_loop_blockA + _trim [{col}]", base + trim, col, log_print(log, k))
    A = {"notrim": min([r for r in base if r["carico"] == "1"
                        and capval(r["cwire"]) <= 1e-9], key=pm)}
    for pos in ("0", "6", "12"):
        A[pos] = min([r for r in trim if r["cand"] == "2" and r["pos"] == pos
                      and capval(r["cwire"]) <= 1e-9], key=pm)
        A[pos + "_all"] = min([r for r in trim if r["cand"] == "2" and r["pos"] == pos],
                              key=pm)
    v["A"] = A
    v["A_dir"] = d

    # --- buffer delle fisse (L27)
    d = src(L27, "tb_loop_bufferfissa")
    tab = _loop_table(d, "tb_loop_bufferfissa.csv", 44, "tb_loop_bufferfissa.log")
    v["F"] = min([r for r in tab if r["pos"] == "1"], key=pm)
    v["Fn"] = min([r for r in tab if r["pos"] == "2"], key=pm)
    v["F_dir"] = d

    # --- agli spigoli di tolleranza (deck d'esplorazione di L16)
    d = src(L16X, "toll_L16")
    tab = load_table(os.path.join(d, "toll_L16_tab.csv"), 704)
    cross_table("toll_L16_tab.csv [pm_deg]", tab, "pm_deg",
                log_meas(os.path.join(d, "toll_L16.log"), "pmarg"))
    v["T"] = {m: min([r for r in tab if r["mode"] == mm], key=pm)
              for mm, m in (("0", "0db"), ("3", "3db"))}
    v["T_dir"] = d

    inst = [(f"Blocco B &middot; {MLAB[m]}", B[m]["min"]) for m in MODES]
    inst += [(f"Blocco A &middot; trim {t}", pm(A[p]))
             for p, t in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB"))]
    inst += [("Buffer delle fisse", pm(v["F"]))]
    v["inst"] = inst
    v["min"] = min(x for _, x in inst)
    v["min_where"] = min(inst, key=lambda t: t[1])[0]
    return v


def measure_zout():
    d = src(L27, "tb_zout_psrr_noise")
    log = os.path.join(d, "tb_zout_psrr_noise.log")
    keys = ("z20", "z1k", "z20k", "za20", "za1k", "za20k", "za100k")
    lv = {k: log_print(log, k) for k in keys}
    for k in keys:
        if len(lv[k]) != 3:
            refuse(f"tb_zout_psrr_noise.log: attese 3 occorrenze di {k}, trovate {len(lv[k])}")
    out = {}
    for idx, m in enumerate(MODES):
        rows = load_csv(os.path.join(d, f"tb_zout_psrr_noise_zout_{m}.csv"))
        f, z = pair(rows, 0)
        _, za = pair(rows, 1)
        r = {"f": f, "z": z, "za": za, "z100k": interp(f, z, 100000)}
        for k, fr in (("20", 20), ("1k", 1000), ("20k", 20000)):
            r["z" + k] = check(f"Zout {m} @{fr} Hz", interp(f, z, fr), at(lv["z" + k], idx), 2e-3)
            r["za" + k] = check(f"Zout(OUT) {m} @{fr} Hz", interp(f, za, fr),
                                at(lv["za" + k], idx), 2e-3)
        r["za100k"] = check(f"Zout(OUT) {m} @100 kHz", interp(f, za, 100000),
                            at(lv["za100k"], idx), 2e-3)
        out[m] = r
    return out


PSRR_ORDER = [("p", m) for m in MODES] + [("m", m) for m in MODES]


def measure_psrr():
    d = src(L27, "tb_zout_psrr_noise")
    log = os.path.join(d, "tb_zout_psrr_noise.log")
    keys = ("p100", "p1k", "p10k", "p100k")
    lv = {k: log_print(log, k) for k in keys}
    for k in keys:
        if len(lv[k]) != len(PSRR_ORDER):
            refuse(f"tb_zout_psrr_noise.log: attese 6 occorrenze di {k}, trovate {len(lv[k])}")
    out = {}
    for idx, (rail, m) in enumerate(PSRR_ORDER):
        rows = load_csv(os.path.join(d, f"tb_zout_psrr_noise_psrr{rail}_{m}.csv"))
        f, p = pair(rows, 0)
        tag = f"PSRR{'+' if rail == 'p' else '-'} {m}"
        r = {"f": f, "p": p}
        for k, fr in (("p100", 100), ("p1k", 1000), ("p10k", 10000), ("p100k", 100000)):
            r[k] = check(f"{tag} @{fr} Hz", interp(f, p, fr), at(lv[k], idx), 2e-3)
        out[(rail, m)] = r
    return out


def integrate_noise(f, s):
    """sqrt(integrale di s(f)^2 df), trapezi sulla griglia del deck."""
    tot = 0.0
    for i in range(1, len(f)):
        tot += 0.5 * (s[i] ** 2 + s[i - 1] ** 2) * (f[i] - f[i - 1])
    return math.sqrt(tot)


def measure_noise():
    """E5 del blocco: spettri integrati contro `onoise_total` stampato."""
    out = {}
    d = src(L27, "tb_zout_psrr_noise")
    tot = log_print(os.path.join(d, "tb_zout_psrr_noise.log"), "onoise_total")
    if len(tot) != 5:
        refuse(f"tb_zout_psrr_noise.log: attese 5 occorrenze di onoise_total, trovate {len(tot)}")
    zp = []
    for i, (fname, lab) in enumerate((
            ("tb_zout_psrr_noise_noise_0db.csv", "0 dB &middot; sorgente 430 Ω (phono)"),
            ("tb_zout_psrr_noise_noise_3db.csv", "+3 dB &middot; sorgente 430 Ω"),
            ("tb_zout_psrr_noise_noise_10db.csv", "+10 dB &middot; sorgente 430 Ω"),
            ("tb_zout_psrr_noise_noise_intrinsic.csv", "0 dB &middot; sorgente 1 Ω (intrinseco)"),
            ("tb_zout_psrr_noise.csv", "+10 dB &middot; sorgente 2500 Ω &mdash; caso peggiore"))):
        f, s = pair(load_csv(os.path.join(d, fname)), 0)
        val = check(f"E5 {fname}", integrate_noise(f, s), at(tot, i), 1e-2)
        zp.append((lab, val))
    out["zout"] = zp
    out["zout_dir"] = d

    d = src(L27, "tb_noise_breakdown")
    tot = log_print(os.path.join(d, "tb_noise_breakdown.log"), "onoise_total")
    if len(tot) != 5:
        refuse(f"tb_noise_breakdown.log: attese 5 occorrenze di onoise_total, trovate {len(tot)}")
    nb = []
    for i, (fname, lab) in enumerate((
            ("tb_noise_breakdown_a_0db_1r.csv", "A) 0 dB, sorgente 1 Ω &mdash; blocco A intrinseco"),
            ("tb_noise_breakdown_b_0db_430r.csv", "B) 0 dB, sorgente 430 Ω &mdash; blocco A sul phono"),
            ("tb_noise_breakdown_c_0db_2500r.csv", "C) 0 dB, sorgente 2500 Ω &mdash; blocco B"),
            ("tb_noise_breakdown_e_3db_2500r.csv", "E) +3 dB, sorgente 2500 Ω &mdash; blocco B"),
            ("tb_noise_breakdown_d_10db_2500r.csv", "D) +10 dB, sorgente 2500 Ω &mdash; blocco B, caso peggiore"))):
        # l'ordine delle print nel log e' A, B, C, D, E (foreach cfg 1..5)
        li = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}[fname.split("_")[3]]
        f, s = pair(load_csv(os.path.join(d, fname)), 0)
        nb.append((lab, check(f"E5 {fname}", integrate_noise(f, s), at(tot, li), 1e-2)))
    out["nb"] = nb
    out["nb_dir"] = d
    return out


def measure_trim():
    """ADR-027: attenuazione, E3 al connettore, E5 della catena (tb_trim di L16)."""
    d = src(L16, "tb_trim")
    log = os.path.join(d, "tb_trim.log")
    e3 = load_table(os.path.join(d, "tb_trim_e3.csv"), 24)
    for col, k in (("zmin_ohm", "zmin"), ("z20_ohm", "z20"), ("z1k_ohm", "z1k"),
                   ("z20k_ohm", "z20k"), ("att1k_db", "att1k")):
        cross_table(f"tb_trim_e3.csv [{col}]", e3, col, log_print(log, k))
    e5 = load_table(os.path.join(d, "tb_trim_e5.csv"), 96)
    cross_table("tb_trim_e5.csv [onoise_uv]", e5, "onoise_uv", log_print(log, "onu"))

    c2 = [r for r in e3 if r["cand"] == "2"]
    scale = "/".join(c2[0][k] for k in ("r1", "r2", "r3")) if c2 else "?"
    att = {}
    for pos in ("99", "0", "6", "12"):
        vals = [num(r, "att1k_db") for r in c2 if r["pos"] == pos]
        if not vals or max(vals) - min(vals) > 1e-6:
            refuse(f"tb_trim_e3: l'attenuazione della posizione {pos} dipende da CSEL")
        att[pos] = vals[0] if vals else float("nan")
    zmin = {(r["pos"], r["csel"]): num(r, "zmin_ohm") for r in c2}
    e3min = min(v for (p, _), v in zmin.items() if p in ("0", "6", "12"))
    e3min_cs = min(((p, c) for (p, c) in zmin if p in ("0", "6", "12")), key=lambda k: zmin[k])[1]

    c25 = [r for r in e5 if r["cand"] == "2"]
    e5w = {pos: max([r for r in c25 if r["pos"] == pos], key=lambda r: num(r, "onoise_uv"))
           for pos in ("99", "0", "6", "12")}
    e5max = max(num(e5w[p], "onoise_uv") for p in ("0", "6", "12"))
    return {"dir": d, "scale": scale, "att": att, "zmin": zmin, "e3min": e3min,
            "e3min_cs": e3min_cs, "e5w": e5w, "e5max": e5max}


def m1_window(vin, vout):
    """La finestra di M1, con lo stesso algoritmo di headroom_nc009.py:
    il guadagno locale entro l'1 % del valore a 0 V, bordi ai campioni."""
    n = len(vin)
    i0 = min(range(n), key=lambda i: abs(vin[i]))
    g = [(vout[i + 1] - vout[i - 1]) / (vin[i + 1] - vin[i - 1]) for i in range(1, n - 1)]
    g0 = g[i0 - 1]
    lo = hi = i0 - 1
    while lo - 1 >= 0 and abs(g[lo - 1] - g0) / abs(g0) <= 0.01:
        lo -= 1
    while hi + 1 < len(g) and abs(g[hi + 1] - g0) / abs(g0) <= 0.01:
        hi += 1
    return g0, vin[lo + 1], vin[hi + 1], vout[lo + 1], vout[hi + 1]


def db20(x):
    return 20 * math.log10(x)


def measure_headroom(trim):
    """NC-009, una cifra con la sua metrica (M1, scelta in L16).

    M1: limite lineare (uscita ai bordi della finestra all'1 %, bordo minore,
    come seno RMS) contro 2,7 V RMS x guadagno misurato x attenuazione del
    trim misurata. M2 (ADR-015) e M3 (dossier fino a L32) sono etichettate."""
    d = src(L16, "tb_dc_headroom")
    names = {"0db": "tb_dc_headroom.csv", "3db": "tb_dc_headroom_3db.csv",
             "10db": "tb_dc_headroom_10db.csv"}
    att = {"0": 0.0, "6": trim["att"]["6"], "12": trim["att"]["12"]}
    out = {"dir": d, "att": att, "modes": {}}
    for m in MODES:
        vin, vout = pair(load_csv(os.path.join(d, names[m])), 0)
        g0, vi_lo, vi_hi, vo_lo, vo_hi = m1_window(vin, vout)
        lin = min(abs(vo_lo), abs(vo_hi)) / math.sqrt(2)
        sat = min(abs(max(vout)), abs(min(vout))) / math.sqrt(2)
        r = {"vin": vin, "vout": vout, "gain": g0, "vi_lo": vi_lo, "vi_hi": vi_hi,
             "vo_lo": vo_lo, "vo_hi": vo_hi, "lin": lin, "sat": sat,
             "vout_max": max(vout), "vout_min": min(vout), "trim": {}}
        for tpos, tnom in (("0", 0), ("6", -6), ("12", -12)):
            req = E6 * abs(g0) * 10 ** (att[tpos] / 20)
            req_nom = E6 * 10 ** (MNOM[m] / 20) * 10 ** (tnom / 20)
            r["trim"][tpos] = {"req": req, "M1": db20(lin / req),
                               "M2": db20(sat / req_nom), "M3": db20(lin / req_nom)}
        out["modes"][m] = r

    # la stessa cifra dallo script di L16, sugli stessi CSV e le stesse attenuazioni
    script = os.path.join(L16X, "script", "headroom_nc009.py")
    proc = subprocess.run([sys.executable, script] +
                          [os.path.join(d, names[m]) for m in MODES] +
                          [repr(att["6"]), repr(att["12"])],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        refuse(f"headroom_nc009.py esce {proc.returncode}: {proc.stderr.strip()[-200:]}")
        return out
    got, mode = {}, None
    mmap = {"0": "0db", "+3": "3db", "+10": "10db"}
    for ln in proc.stdout.splitlines():
        mm = re.match(r"^== modo (\S+) dB", ln)
        if mm:
            mode = mmap.get(mm.group(1))
            continue
        mt = re.match(r"^\s+trim\s+(-?\d+) dB .*M1 ([+-]\d+\.\d+) dB \| "
                      r"M2 ([+-]\d+\.\d+) dB \| M3 ([+-]\d+\.\d+) dB", ln)
        if mt and mode:
            got[(mode, mt.group(1).lstrip("-"))] = [float(mt.group(i)) for i in (2, 3, 4)]
    if len(got) != 9:
        refuse(f"headroom_nc009.py: attese 9 righe M1/M2/M3, lette {len(got)}")
    for (m, tpos), vals in got.items():
        mine = out["modes"][m]["trim"][tpos]
        for name, theirs in zip(("M1", "M2", "M3"), vals):
            # lo script stampa due decimali: lo scarto ammesso e' l'arrotondamento
            if not abs(mine[name] - theirs) <= 0.0051:
                refuse(f"NC-009 {m} trim -{tpos} dB {name}: dossier {mine[name]:+.4f} dB, "
                       f"headroom_nc009.py {theirs:+.2f} dB")
    out["script"] = rel(script)
    return out


def measure_counterfactual():
    """I tre stati del controfattuale di ADR-004. col1 = v(OUT), col3 = v(FB)."""
    d = src(L27, "tb_switch_v2_counterfactual")
    files = [("A", "contatto CHIUSO, R_f = 1,50 kΩ", "tb_switch_v2_counterfactual.csv"),
             ("B", "contatto APERTO, R_f = 1e12 Ω", "tb_switch_v2_counterfactual_open.csv"),
             ("C", "richiuso, controprova di B", "tb_switch_v2_counterfactual_reclosed.csv")]
    out = []
    for tag, desc, name in files:
        rows = load_csv(os.path.join(d, name))
        out.append({"tag": tag, "desc": desc, "vout": rows[0][1], "vfb": rows[0][3]})
    if abs(out[0]["vout"] - out[2]["vout"]) > 1e-6:
        refuse("controfattuale: A e C non coincidono, la controprova non regge")
    if abs(out[1]["vout"] - out[0]["vout"]) < 1.0:
        refuse("controfattuale: B non differisce da A, l'anello non si e' aperto")
    return {"dir": d, "rows": out}


V2_WINDOWS = [("regime_0db", "s0", "regime a 0 dB"), ("regime_3db", "s3", "regime a +3 dB"),
              ("regime_10db", "s10", "regime a +10 dB"),
              ("regime_10db_bis", "s10b", "regime a +10 dB, seconda volta"),
              ("trans_0_3", "t03", "0 &rarr; +3 dB (K1)"),
              ("trans_3_10", "t310", "+3 &rarr; +10 dB (K5)"),
              ("trans_10_3", "t103", "+10 &rarr; +3 dB (K5)"),
              ("trans_3_0", "t30", "+3 &rarr; 0 dB (K1)"),
              ("trans_0_10_k5_prima", "t010", "0 &rarr; +10 dB, K5 per primo"),
              ("trans_10_0_k1_prima", "t100", "+10 &rarr; 0 dB, K1 per primo")]


def measure_v2():
    """V2: le finestre di tb_switch_v2 contro l'inviluppo del regime a +10 dB."""
    d = src(L27, "tb_switch_v2")
    log = os.path.join(d, "tb_switch_v2.log")
    tab = load_table(os.path.join(d, "tb_switch_v2_finestre.csv"), len(V2_WINDOWS))
    rows = []
    for (fin, pre, lab), r in zip(V2_WINDOWS, tab):
        if r["finestra"] != fin:
            refuse(f"tb_switch_v2_finestre.csv: attesa la finestra {fin}, trovata {r['finestra']}")
        for col, suf in (("vmax", "max"), ("vmin", "min")):
            lv = log_meas(log, pre + suf)
            if len(lv) != 1:
                refuse(f"tb_switch_v2.log: attesa una meas {pre + suf}, trovate {len(lv)}")
            else:
                cross_table(f"tb_switch_v2_finestre.csv {fin} [{col}]", [r], col, lv)
        rows.append({"fin": fin, "lab": lab, "vmax": num(r, "vmax"), "vmin": num(r, "vmin")})
    reg = [x for x in rows if x["fin"].startswith("regime_10db")]
    env_hi = max(x["vmax"] for x in reg)
    env_lo = min(x["vmin"] for x in reg)
    tol = 1e-4       # V: le tabelle hanno sei cifre significative
    for x in rows:
        x["inside"] = x["vmax"] <= env_hi + tol and x["vmin"] >= env_lo - tol
    gmax, gmin = at(log_print(log, "vmax"), 0), at(log_print(log, "vmin"), 0)
    check("tb_switch_v2 estremo positivo su 70 ms", max(x["vmax"] for x in rows), gmax, 1e-4)
    check("tb_switch_v2 estremo negativo su 70 ms", min(x["vmin"] for x in rows), gmin, 1e-4)
    return {"dir": d, "rows": rows, "env_hi": env_hi, "env_lo": env_lo,
            "gmax": gmax, "gmin": gmin, "all_inside": all(x["inside"] for x in rows)}


def measure_v3():
    """V3, tb_v3_overload: v(SRCN), v(OUT), v(JACK), v(NX). Il deck non fa
    `print`: questi numeri hanno solo il CSV, e la pagina lo dice."""
    d = src(L27, "tb_v3_overload")
    rows = load_csv(os.path.join(d, "tb_v3_overload.csv"))
    vout = [r[3] for r in rows]
    return {"dir": d, "vmax": max(vout), "vmin": min(vout), "jack_end": rows[-1][5],
            "t_end": rows[-1][2], "n": len(rows)}


# ADR-023: i percorsi ascoltabili per caso, dall'intestazione di tb_mute_corto.cir.
LISTEN = {"0": {"A", "F1", "F2", "B"}, "1": set(), "2": {"A", "F2", "B"},
          "5": {"A", "F2", "B"}, "6": {"A", "F2", "B"}, "3": {"A", "F1", "B"},
          "4": {"A", "F1", "F2"}}


def measure_p7():
    """P7 (ADR-021): MJE peggiore per blocco e modo, Tj = 60 °C + P·RθJA."""
    d = src(L27, "tb_mute_corto")
    log = os.path.join(d, "tb_mute_corto.log")
    tab = load_table(os.path.join(d, "tb_mute_corto_regime.csv"), 600)
    cross_table("tb_mute_corto_regime.csv [p_q132]", tab, "p_q132", log_meas(log, "pq132"))
    cross_table("tb_mute_corto_regime.csv [p_q133]", tab, "p_q133", log_meas(log, "pq133"))
    worst = {}
    for blk in ("A", "F1", "F2", "B"):
        for m in ("0", "3", "10"):
            rows = [r for r in tab if r["blk"] == blk and r["modo_db"] == m]
            if not rows:
                refuse(f"tb_mute_corto: nessuna riga per {blk} a {m} dB")
                continue
            w = max(rows, key=lambda r: max(num(r, "p_q132"), num(r, "p_q133")))
            p = max(num(w, "p_q132"), num(w, "p_q133"))
            worst[(blk, m)] = {"p": p, "tj": TA + p * RTH_MJE, "caso": w["caso"],
                               "f": w["f_hz"]}
    classA = lambda r: num(r, "icmin_q132") > 0 and num(r, "icmax_q133") < 0  # noqa: E731
    listen = [r for r in tab if r["blk"] in LISTEN.get(r["caso"], set())]
    bad = [r for r in listen if not classA(r)]
    rsep = {m: max(num(r, "p_rsep") for r in tab if r["blk"] == "B" and r["modo_db"] == m)
            for m in ("0", "3", "10")}
    return {"dir": d, "worst": worst, "n_listen": len(listen), "n_bad": len(bad),
            "rsep": rsep, "tjmax": max(x["tj"] for x in worst.values())}


def measure_oppoint():
    """Punti di lavoro dal log di tb_op di L27."""
    d = src(L27, "tb_op")
    rails, cur = {}, {}
    with open(os.path.join(d, "tb_op.log")) as f:
        lines = [ln.rstrip("\n") for ln in f]
    for ln in lines:
        s = ln.strip()
        for key in ("i(vpp)", "i(vmm)"):
            if s.lower().startswith(key):
                try:
                    rails[key] = float(s.split("=")[1].strip())
                except (IndexError, ValueError):
                    pass
        if s.startswith("@"):
            try:
                lhs, rhs = s.split("=", 1)
                val = float(rhs.strip())
            except ValueError:
                continue
            dev, _, par = lhs.strip()[1:].partition("[")
            cur.setdefault(dev, {})[par.rstrip("]")] = val
    devices = [(dev, cur[dev]) for dev in sorted(cur, key=lambda d: (d[0], d))
               if any(k in cur[dev] for k in ("ic", "id"))]
    if not devices or len(rails) != 2:
        refuse("tb_op.log: punti di lavoro o correnti dei rail non trovati")
    return {"dir": d, "rails": rails, "devices": devices}


# --------------------------------------------------------------- figure ---
def mcol(m, alt=False):
    return {"0db": (sp.C_0DB, sp.C_0DB_ALT), "3db": (sp.C_3DB, sp.C_3DB_ALT),
            "10db": (sp.C_10DB, sp.C_10DB_ALT)}[m][1 if alt else 0]


def fig_response(resp):
    W, H = 900, 440
    ax = sp.Axes(72, 46, W - 130, H - 160, (10, 100000), (-1, 11),
                 xlabel="frequenza [Hz]", ylabel="|v(JACK)| [dB]",
                 title="Risposta in frequenza, i tre modi di guadagno")
    for m in MODES:
        ax.line(resp[(m, "1.5")]["f"], resp[(m, "1.5")]["gdb"], mcol(m),
                f"{MLAB[m]} · sorgente 1,5 Ω", None)
        ax.line(resp[(m, "2500")]["f"], resp[(m, "2500")]["gdb"], mcol(m, True),
                f"{MLAB[m]} · sorgente 2500 Ω", "5,3")
    ax.vline(20000)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L27 tb_ac_*.csv · linea verticale = 20 kHz")


def fig_response_adr014(resp):
    W, H = 900, 420
    ax = sp.Axes(72, 46, W - 130, H - 160, (10, 100000), (-0.15, 0.03),
                 xlabel="frequenza [Hz]", ylabel="scostamento da 1 kHz [dB]",
                 title="ADR-014: la risposta non deve muoversi con la manopola del volume")
    for m in MODES:
        for rs, alt, dash in (("1.5", False, None), ("2500", True, "5,3")):
            r = resp[(m, rs)]
            ax.line(r["f"], [g - r["g1k"] for g in r["gdb"]], mcol(m, alt),
                    f"{MLAB[m]} · {rs.replace('.', ',')} Ω", dash)
    ax.vline(20000)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Normalizzato a 1 kHz: l'impedenza della sorgente "
                       "non sposta la banda passante.")


def fig_v1(v1):
    W, H = 900, 460
    ax = sp.Axes(72, 46, W - 130, H - 160, (0, 4.8), (20, 110), xlog=False,
                 xlabel="capacità del cavo [nF]", ylabel="margine di fase [gradi]",
                 title="V1, blocco B: il margine contro la capacità del cavo (ADR-024)")
    for m in MODES:
        b = v1["B"][m]
        w = b["w"]
        xs, ys = b["curve"]
        ax.line([x * 1e9 for x in xs], ys, mcol(m),
                f"{MLAB[m]} · al jack · {lab_c(w['rsrc'])}, {lab_c(w['rload'])}", None)
        xs, ys = b["curve_n"]
        ax.line([x * 1e9 for x in xs], ys, mcol(m, True),
                f"{MLAB[m]} · sul nodo (informazione)", "5,3")
        ax.annot(capval(w["cprobe"]) * 1e9, b["min"], f"min {fx(b['min'])}°", 8, -8)
    ax.hline(PM_MIN, sp.C_REQ, "soglia 60° (ADR-019)", left=True)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L16 tb_loop_margini.csv · il verdetto è il "
                       "minimo della curva al jack, non il valore a 4,7 nF")


def fig_loop(v1):
    W, H = 900, 620
    xlim = (1, 1e8)
    axm = sp.Axes(72, 46, W - 130, 230, xlim, (-40, 80), ylabel="|T| [dB]",
                  title="Guadagno d'anello del blocco B alla capacità del minimo "
                        "(sorgente 2,5 kΩ, carico 100 kΩ)")
    axp = sp.Axes(72, 330, W - 130, 190, xlim, (0, 180),
                  xlabel="frequenza [Hz]", ylabel="fase di T [gradi]")
    for m in MODES:
        b = v1["bode"][m]
        lab = f"{MLAB[m]} · cavo {lab_c(b['C'])}"
        axm.line(b["f"], b["tdb"], mcol(m), lab, None)
        axp.line(b["f"], b["tph"], mcol(m), None, None)
        axp.annot(b["fcross"], b["pmarg"], f"{fx(b['pmarg'])}°".replace("&minus;", "-"), 8, -8)
    axm.hline(0, sp.C_REQ, "0 dB")
    body = (axm.render(show_xlabels=False) + "\n" + axp.render() + "\n" +
            axm.legend(80, H - 42, cols=3, colw=270))
    return sp.document(W, H, body, "Dati: L27 tb_loop_att2k5_*.csv · margine = |fase| "
                       "dove |T| attraversa 0 dB (G2 è l'ingresso invertente)")


def fig_psrr(psrr):
    W, H = 900, 440
    ax = sp.Axes(72, 46, W - 130, H - 160, (20, 200000), (0, 120),
                 xlabel="frequenza [Hz]", ylabel="PSRR [dB] — più grande è meglio",
                 title="Reiezione dell'alimentazione, i due rail nei tre modi")
    for m in MODES:
        ax.line(psrr[("p", m)]["f"], psrr[("p", m)]["p"], mcol(m), f"rail + · {MLAB[m]}", None)
        ax.line(psrr[("m", m)]["f"], psrr[("m", m)]["p"], mcol(m, True), f"rail − · {MLAB[m]}", "5,3")
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L27 tb_zout_psrr_noise_psrr*.csv · 1 V AC in "
                       "serie a ciascun rail, ingresso silenziato")


def fig_zout(z):
    W, H = 900, 450
    ax = sp.Axes(72, 46, W - 130, H - 160, (20, 200000), (0.5, 5000), ylog=True,
                 xlabel="frequenza [Hz]", ylabel="|Z| [Ω]",
                 title="Impedenza d'uscita: al jack e al nodo OUT")
    for m in MODES:
        ax.line(z[m]["f"], z[m]["z"], mcol(m), f"al jack · {MLAB[m]}", None)
        ax.line(z[m]["f"], z[m]["za"], mcol(m, True), f"al nodo OUT · {MLAB[m]}", "5,3")
    ax.hline(100, sp.C_REQ, "E4: < 100 Ω")
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L27 tb_zout_psrr_noise_zout_*.csv · la salita "
                       "sotto 200 Hz è la reattanza del 4,7 µF, non lo stadio")


def fig_headroom(hr):
    W, H = 900, 430
    ax = sp.Axes(72, 46, W - 130, H - 140, (-14, 14), (-15, 15), xlog=False,
                 xlabel="v(IN) [V]", ylabel="v(OUT) [V]",
                 title="Escursione in continua e saturazione, i tre modi")
    for m in MODES:
        r = hr["modes"][m]
        ax.line(r["vin"], r["vout"], mcol(m), MLAB[m], None)
        ax.annot(r["vi_hi"], r["vo_hi"],
                 f"limite M1 {fx(r['lin'])} V RMS".replace("&minus;", "-"),
                 -8 if m == "10db" else 8, -8 if m == "10db" else 16)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=175)
    return sp.document(W, H, body, "Dati: L16 tb_dc_headroom*.csv · spazzata in continua; "
                       "il punto segna il bordo positivo della finestra all'1 %")


def fig_counterfactual(cf, hr):
    """I tre stati del controfattuale: barre, non curve. Il valore di B va
    VISTO accanto ai rail: e' tutto il senso della meta' falsificabile di V2."""
    W, H = 900, 440
    ax = sp.Axes(150, 52, W - 300, H - 130, (0.4, 3.6), (-18, 18), xlog=False,
                 ylabel="v(OUT) [V]",
                 title="Controfattuale ADR-004: cosa farebbe il relè nel ramo sbagliato",
                 xticks=[(1, "A · contatto chiuso"), (2, "B · contatto APERTO"),
                         (3, "C · richiuso")])
    colors = [sp.C_0DB, sp.C_10DB, sp.C_0DB]
    for i, (r, col) in enumerate(zip(cf["rows"], colors), start=1):
        ax.bar(i, 0.0, r["vout"], col)
        dy = 18 if r["vout"] < 0 else -12
        ax.annot(i, r["vout"], f'{r["vout"]:.4f} V'.replace(".", ","), 12, dy)
    ax.hline(15, sp.C_REQ, "rail +15 V")
    ax.hline(-15, sp.C_REQ, "rail −15 V")
    vmin = hr["modes"]["0db"]["vout_min"]
    ax.hline(vmin, sp.C_10DB_ALT, "saturazione dello stadio a 0 dB, "
             + f"{vmin:.4f}".replace(".", ",") + " V", "2,3", left=True)
    ax.hline(0, sp.C_AXIS, None, "1,3")
    return sp.document(W, H, ax.render(), "Dati: L27 tb_switch_v2_counterfactual*.csv · "
                       "con R_f aperto l'anello è rotto e l'uscita si appoggia al rail")


# ----------------------------------------------------------------- pagina --
CSS = """
:root{
  --paper:#f6f7f9; --surface:#ffffff; --ink:#161a1f; --muted:#5b6472;
  --rule:#d8dde4; --rule-soft:#e9edf2; --accent:#1f5c99; --accent2:#a8452a;
  --ok:#1c6b3c; --warn-ink:#7a4a12; --warn-bg:#fdf4e6; --warn-rule:#c98b2e;
  --chip:#eef1f5; --plate:#ffffff;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#101317; --surface:#181c22; --ink:#e6e9ed; --muted:#98a2b0;
  --rule:#2a3038; --rule-soft:#22272e; --accent:#7fb3e0; --accent2:#e09880;
  --ok:#5fbb85; --warn-ink:#e6b878; --warn-bg:#23200f; --warn-rule:#8a6a28;
  --chip:#20252c; --plate:#ffffff;
}}
:root[data-theme="dark"]{
  --paper:#101317; --surface:#181c22; --ink:#e6e9ed; --muted:#98a2b0;
  --rule:#2a3038; --rule-soft:#22272e; --accent:#7fb3e0; --accent2:#e09880;
  --ok:#5fbb85; --warn-ink:#e6b878; --warn-bg:#23200f; --warn-rule:#8a6a28;
  --chip:#20252c; --plate:#ffffff;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Sans","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:16px; line-height:1.62; font-weight:400;
}
.wrap{max-width:1000px;margin:0 auto;padding:40px 24px 96px}
.col{max-width:68ch}

.eyebrow{
  font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--muted); margin:0 0 10px;
}
h1{
  font-size:clamp(28px,4.2vw,40px); line-height:1.12; letter-spacing:-.021em;
  font-weight:600; margin:0 0 10px; text-wrap:balance;
}
.lede{font-size:18px; color:var(--muted); margin:0 0 4px; max-width:60ch}

h2{
  font-size:22px; font-weight:600; letter-spacing:-.012em; line-height:1.25;
  margin:64px 0 14px; padding-top:20px; border-top:1px solid var(--rule);
  display:flex; gap:14px; align-items:baseline; text-wrap:balance;
}
h2 .secno{
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:13px; font-weight:500; color:var(--accent);
  letter-spacing:.04em; flex:none; padding-top:2px;
}
h3{font-size:16.5px;font-weight:600;margin:30px 0 8px;letter-spacing:-.008em}
p{margin:12px 0;max-width:68ch}
ul{margin:12px 0;padding-left:20px;max-width:68ch}
li{margin:9px 0}
strong{font-weight:600}
em{font-style:italic}

code,.mono{
  font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:.86em;
}
code{background:var(--chip); padding:1.5px 5px; border-radius:3px;
  border:1px solid var(--rule-soft);}

/* Tavole grafiche: lastre su bianco, come in un datasheet. Gli SVG sono
   file versionati a parte e non possono leggere i token del tema, quindi
   stanno su fondo bianco in entrambi i temi - scelta, non svista. */
.plate{
  background:var(--plate); border:1px solid var(--rule); border-radius:3px;
  padding:8px; margin:20px 0; overflow-x:auto;
}
.plate img,.plate svg{display:block;max-width:100%;height:auto;margin:0 auto}

.tablewrap{overflow-x:auto;margin:18px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
caption{
  caption-side:top; text-align:left; color:var(--muted); padding-bottom:8px;
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:11.5px; letter-spacing:.08em; text-transform:uppercase;
}
th,td{
  border-bottom:1px solid var(--rule-soft); padding:8px 14px 8px 0;
  text-align:left; white-space:nowrap; vertical-align:baseline;
}
th{
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  font-weight:500; color:var(--muted); border-bottom:1px solid var(--rule);
}
tbody tr:last-child td{border-bottom:1px solid var(--rule)}
td.num{
  text-align:right; font-variant-numeric:tabular-nums;
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; font-size:13px;
}
th.num{text-align:right}

/* Quadro sinottico: i numeri di testa, non tessere giganti. */
.synopsis{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:0; margin:26px 0 6px; border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule);
}
.synopsis div{padding:14px 18px 14px 0}
.synopsis dt{
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:11px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); margin:0 0 5px;
}
.synopsis dd{
  margin:0; font-size:21px; font-weight:600; letter-spacing:-.015em;
  font-variant-numeric:tabular-nums;
}
.synopsis dd .u{display:block;font-size:12.5px;font-weight:400;color:var(--muted);
  letter-spacing:0;line-height:1.4;margin-top:2px}

.note{
  background:var(--warn-bg); border-left:3px solid var(--warn-rule);
  padding:14px 18px; margin:22px 0; max-width:68ch;
}
.note strong{color:var(--warn-ink)}

/* Provenienza sotto ogni titolo di sezione: deck, dati, modelli. */
.prov{
  color:var(--muted); font-size:12.5px; line-height:1.55; max-width:none;
  margin:4px 0 16px; padding-left:10px; border-left:2px solid var(--rule);
}
.prov code{font-size:.92em}

nav.toc{margin:26px 0 0;border-top:1px solid var(--rule);padding-top:16px}
nav.toc ol{
  list-style:none; margin:0; padding:0; max-width:none;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  gap:2px 26px; counter-reset:toc;
}
nav.toc li{margin:0;counter-increment:toc}
nav.toc a{
  color:var(--ink); text-decoration:none; display:block; padding:4px 0;
  border-bottom:1px solid transparent; font-size:14.5px;
}
nav.toc a::before{
  content:counter(toc,decimal-leading-zero) "  ";
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  color:var(--accent); font-size:12px;
}
nav.toc a:hover{border-bottom-color:var(--rule)}
a{color:var(--accent)}
a:focus-visible,nav.toc a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.ok{color:var(--ok);font-weight:600}
.no{color:var(--accent2);font-weight:600}
.na{color:var(--muted)}
.meta{color:var(--muted);font-size:13.5px;max-width:68ch}
hr.end{border:0;border-top:1px solid var(--rule);margin:56px 0 0}
@media (max-width:640px){
  .wrap{padding:28px 16px 72px}
  h2{flex-direction:column;gap:2px}
}
"""


def html_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


SECTIONS = (("s1", "Il blocco di guadagno"), ("s2", "Il preamplificatore intero"),
            ("s3", "Punti di lavoro"), ("s4", "Risposta in frequenza"),
            ("s5", "Stabilità: la matrice V1"), ("s6", "Il trim e l&rsquo;impedenza d&rsquo;ingresso"),
            ("s7", "Rumore in uscita"), ("s8", "Escursione e headroom"),
            ("s9", "Reiezione dell&rsquo;alimentazione"), ("s10", "Impedenza d&rsquo;uscita"),
            ("s11", "I relè di guadagno: V2"), ("s12", "Sovraccarico e corto: V3, P7"),
            ("s13", "Requisiti a fronte del misurato"), ("s14", "Cosa questo dossier non dice"),
            ("s15", "Provenienza"))


def build_page(M, inline=False):
    resp, v1, z, psrr, hr, cf = M["resp"], M["v1"], M["z"], M["psrr"], M["hr"], M["cf"]
    trim, noise, v2, v3, p7, op = M["trim"], M["noise"], M["v2"], M["v3"], M["p7"], M["op"]

    def figure(svgfile, alt):
        if inline:
            with open(os.path.join(SCHEM if svgfile in SCHEMATICS else HERE, svgfile)) as f:
                body = f.read()
            return f'<div class="plate">{body.split("?>", 1)[-1]}</div>'
        return (f'<div class="plate"><img src="{svgfile}" '
                f'alt="{html_escape(alt)}" loading="lazy"></div>')

    def h2(anchor):
        n = [a for a, _ in SECTIONS].index(anchor) + 1
        lab = dict(SECTIONS)[anchor]
        return f'<h2 id="{anchor}"><span class="secno">{n}</span><span>{lab}</span></h2>'

    allm = [m for deck in M["decks"] for m in provenance(deck)]
    vendors = sorted({m["part"] for m in allm if m["vendor"]})
    placeholders = sorted({m["part"] for m in allm if not m["vendor"]})
    all_kf0 = all(m["kf"] == 0 for m in allm)
    lsk_lib = os.path.exists(os.path.join(REPO, "models", "jfet", "lsk489.lib"))

    h = []
    A = h.append
    A('<div class="wrap">')
    A('<p class="eyebrow">Bozza &middot; dati del 2026-09-14, lotti L27 e L16 &middot; '
      'modelli in gran parte segnaposto</p>')
    A('<h1>Dossier di misura del preamplificatore di linea</h1>')
    A('<p class="lede">Classe A pura a componenti discreti, senza operazionali nel '
      'percorso del segnale. Guadagno 0 / +3 / +10 dB, trim 0 / &minus;6 / &minus;12 dB '
      'sull&rsquo;uscita variabile.</p>')

    shape, level = adr014(resp)
    worst_shape = max(shape.values(), key=abs)
    weak_psrr = min(r["p10k"] for r in psrr.values())
    nc9 = hr["modes"]["10db"]["trim"]["6"]["M1"]
    gains = " · ".join(sg(resp[(m, "1.5")]["g1k"]) if m != "0db"
                       else fx(resp[(m, "1.5")]["g1k"]) for m in MODES)
    A('<dl class="synopsis">')
    for lab, val, unit in (
            ("Guadagni a 1 kHz", gains, "dB &middot; 0 / +3 / +10 &middot; sorgente 1,5 Ω"),
            ("V1, margine minimo", f"{fx(v1['min'])}°",
             f"soglia 60° &middot; guardia {fx(v1['min'] - PM_MIN)}° &middot; {v1['min_where']}"),
            ("Headroom, NC-009", f"{sg(nc9)} dB",
             "metrica M1 &middot; +10 dB col trim a &minus;6 dB"),
            ("E3, min |Z<sub>in</sub>|", f"{fx(trim['e3min'] / 1000, 1)} kΩ",
             f"con {lab_c(trim['e3min_cs'])} di selettore &middot; ogni posizione del trim"),
            ("E5, catena col trim", f"{fx(trim['e5max'])} µV",
             "peggiore &middot; pavimento senza 1/f"),
            ("Scarto ADR-014", it_sci(worst_shape),
             "dB a 20 kHz rif. 1 kHz &middot; peggiore dei 3 modi"),
            ("PSRR, peggiore", f"{fx(weak_psrr)} dB", "a 10 kHz"),
            ("Z<sub>out</sub> al jack", f"{fx(z['0db']['z1k'])} Ω", "a 1 kHz, 0 dB")):
        A(f'<div><dt>{lab}</dt><dd>{val}<span class="u">{unit}</span></dd></div>')
    A('</dl>')

    A(f'<div class="note"><strong>Leggere prima questo.</strong> Dei '
      f'{len(vendors) + len(placeholders)} dispositivi attivi che questi deck simulano, '
      f'<strong>solo {", ".join(vendors)} usa il modello del costruttore</strong>. '
      f'{", ".join(placeholders)} sono modelli segnaposto scritti a mano (NC-017): i '
      'margini di fase dipendono da capacità e tempi di transito scelti a mano, e la '
      'soglia di 60° esiste anche per coprire questo. '
      + ('<strong>Nessun modello simulato ha rumore 1/f</strong> (KF = 0 o assente '
         'su tutti): ogni cifra di rumore qui è un pavimento termico e shot, non una '
         'previsione (NC-004). ' if all_kf0 else '')
      + ('Il modello del costruttore dell&rsquo;LSK489 esiste in '
         '<code>models/jfet/lsk489.lib</code>, ma nessuno di questi deck lo include. '
         if lsk_lib and "LSK489" in placeholders else '')
      + 'Nessuna cifra di distorsione. La provenienza è scritta sotto ogni titolo di '
      'sezione, ed è letta dagli <code>.include</code> dei deck, non dichiarata.</div>')

    A('<p>Il progetto sostituisce un Technics SU-9070 la cui struttura di guadagno '
      'richiede <strong>46 dB di attenuazione</strong>, causa misurabile della mancanza '
      'di dinamica lamentata. La topologia canonica è in <code>circuits/preamp/</code>; i '
      'banchi di prova in <code>spice/preamp/tb/</code>; i dati in '
      f'<code>{rel(L27)}/</code> (tre modi di guadagno, ADR-026) e '
      f'<code>{rel(L16)}/</code> (il trim, ADR-027).</p>')

    A('<nav class="toc" aria-label="Indice"><ol>')
    for anchor, label in SECTIONS:
        A(f'<li><a href="#{anchor}">{label}</a></li>')
    A('</ol></nav>')

    A('<p class="meta">Nessuna cifra di questa pagina è scritta a mano. Le curve sono '
      'ricontrollate contro le <code>print</code> che ngspice ha stampato nei log '
      'versionati; le tabelle, riga per riga, contro le <code>print</code> o le '
      '<code>meas</code> dello stesso log, e una cella vuota è un rifiuto; la cifra di '
      'headroom contro lo script di L16 che l&rsquo;ha scelta. Se una strada diverge, il '
      'generatore rifiuta di produrre la pagina.</p>')

    # --- 1-2 schemi ---
    A(h2("s1"))
    A('<p>Il blocco è uno solo (ADR-006) e il prodotto lo usa otto volte: per canale, '
      'il blocco A (buffer d&rsquo;ingresso), i due buffer delle uscite fisse (ADR-023) e '
      'il blocco B (uscita variabile). È l&rsquo;oggetto da giudicare.</p>')
    A(figure("gain_block.svg", "Schema del blocco di guadagno"))
    A(h2("s2"))
    A(figure("preamp_blocks.svg", "Diagramma a blocchi del preamplificatore"))

    # --- 3 punti di lavoro ---
    A(h2("s3"))
    A(prov_line("tb_op.cir", op["dir"]))
    A('<p>Corrente dai rail e punto di lavoro di ogni dispositivo attivo, a ingresso a '
      'massa. Il trim sta dopo il condensatore d&rsquo;uscita del blocco A e non tocca la '
      'continua.</p>')
    A('<div class="tablewrap"><table><tr><th>Grandezza</th><th class="num">Valore</th></tr>')
    A(f'<tr><td>Corrente dal rail +15 V</td><td class="num">{it(abs(op["rails"].get("i(vpp)", 0)) * 1000, 4)} mA</td></tr>')
    A(f'<tr><td>Corrente dal rail −15 V</td><td class="num">{it(abs(op["rails"].get("i(vmm)", 0)) * 1000, 4)} mA</td></tr>')
    A('</table></div>')
    A('<div class="tablewrap"><table><tr><th>Dispositivo</th><th class="num">I<sub>C</sub> / I<sub>D</sub> [mA]</th>'
      '<th class="num">V<sub>BE</sub> / V<sub>GS</sub> [V]</th><th class="num">V<sub>BC</sub> [V]</th></tr>')
    for dev, par in op["devices"]:
        ic = par.get("ic", par.get("id"))
        vbe = par.get("vbe", par.get("vgs"))
        vbc = par.get("vbc")
        A(f'<tr><td>{html_escape(dev.upper())}</td>'
          f'<td class="num">{it(ic * 1000, 4) if ic is not None else "&mdash;"}</td>'
          f'<td class="num">{it(vbe, 4) if vbe is not None else "&mdash;"}</td>'
          f'<td class="num">{it(vbc, 4) if vbc is not None else "&mdash;"}</td></tr>')
    A('</table></div>')

    # --- 4 risposta ---
    A(h2("s4"))
    A(prov_line("tb_ac.cir", src(L27, "tb_ac")))
    A(figure("fig_response.svg", "Risposta in frequenza"))
    A('<div class="tablewrap"><table><tr><th>Curva</th><th class="num">20 Hz</th>'
      '<th class="num">1 kHz</th><th class="num">20 kHz</th><th class="num">100 kHz</th></tr>')
    for m in MODES:
        for rs, lab in (("1.5", "sorgente 1,5 Ω (K11)"), ("2500", "sorgente 2500 Ω (attenuatore a metà)")):
            r = resp[(m, rs)]
            A(f'<tr><td>{MLAB[m]} &middot; {lab}</td>'
              + "".join(f'<td class="num">{fx(r[k], 4)} dB</td>' for k in ("g20", "g1k", "g20k", "g100k"))
              + '</tr>')
    A('</table></div>')
    A('<h3>La claim falsificabile di ADR-014</h3>')
    A('<p>L&rsquo;attenuatore a gradini ha un&rsquo;impedenza d&rsquo;uscita che varia con la '
      'manopola. Se il cascode d&rsquo;ingresso fa il suo lavoro, <strong>la forma della '
      'risposta non si muove</strong>: la risposta a 20 kHz <em>riferita a quella a '
      '1 kHz</em> resta la stessa con la sorgente a 1,5 Ω e a 2500 Ω, in ogni modo.</p>')
    A(figure("fig_response_adr014.svg", "ADR-014: risposta contro impedenza di sorgente"))
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">scarto assoluto a 1 kHz</th>'
      '<th class="num">scarto assoluto a 20 kHz</th><th class="num">20 kHz riferito a 1 kHz &mdash; la claim</th></tr>')
    for m in MODES:
        A(f'<tr><td>{MLAB[m]}</td><td class="num">{fx(level[m]["g1k"], 5)} dB</td>'
          f'<td class="num">{fx(level[m]["g20k"], 5)} dB</td>'
          f'<td class="num"><strong>{it_sci(shape[m])} dB</strong></td></tr>')
    A('</table></div>')
    A('<p>Ogni scarto è «sorgente 2500 Ω meno sorgente 1,5 Ω». Le colonne di scarto '
      '<em>assoluto</em> coincidono a 1 kHz e a 20 kHz perché sono una perdita di livello '
      'a banda larga, il partitore fra la sorgente e la Zin del blocco: non misurano la '
      'claim. La claim è l&rsquo;ultima colonna.</p>')
    lf = resp["lf"]
    A('<h3>Il taglio in bassa, col carico da 50 kΩ</h3>')
    A(f'<p>Con il carico Stax-like da 50 kΩ: {fx(lf["g1k"], 4)} dB a 1 kHz, '
      f'{fx(lf["g20"], 4)} dB a 20 Hz, {fx(lf["g5"], 4)} dB a 5 Hz. Il polo è quello '
      'del condensatore d&rsquo;uscita da 4,7 µF (E8, ADR-007).</p>')

    # --- 5 V1 ---
    B = v1["B"]
    A(h2("s5"))
    A(prov_line("tb_loop.cir", v1["B_dir"], note=" (blocco B)"))
    A(prov_line("tb_loop_blockA.cir", v1["A_dir"], note=" (blocco A)"))
    A(prov_line("tb_loop_bufferfissa.cir", v1["F_dir"], note=" (buffer delle fisse)"))
    A('<p><strong>Soglia: 60° su ogni combinazione della matrice</strong> (ADR-019). '
      '<strong>Dove si applica la sonda</strong> lo dice ADR-024: la sonda capacitiva è '
      'il cavo d&rsquo;interconnessione e sta <em>al jack</em>, dopo i 47 Ω e il 4,7 µF, '
      'sul blocco B e sui buffer delle fisse; il verdetto è il <strong>minimo sulla '
      'spazzata</strong> fino a 4,7 nF, non il valore a 4,7 nF. Il blocco A pilota il '
      'cablaggio interno fino all&rsquo;attenuatore e si giudica con una capacità '
      'realistica, ≤ 1 nF. La sonda sul nodo d&rsquo;uscita resta come informazione.</p>')
    A('<p>Iniezione di tensione al gate del JFET invertente: quel nodo non assorbe '
      'corrente e la rete di controreazione lo pilota a bassa impedenza, quindi '
      'l&rsquo;iniezione semplice è esatta. I relè commutano la rete di controreazione, '
      'quindi <strong>il margine è diverso nei tre modi</strong>, e l&rsquo;impedenza '
      'dell&rsquo;attenuatore cambia con la manopola: per questo si spazza tutto.</p>')
    A('<div class="tablewrap"><table><tr><th>Istanza</th><th>Dove cade il minimo</th>'
      '<th class="num">Minimo della spazzata</th><th class="num">A 4,7 nF</th>'
      '<th class="num">Sonda sul nodo</th><th>Esito</th></tr>')
    for m in MODES:
        b, w = B[m], B[m]["w"]
        A(f'<tr><td>Blocco B &middot; {MLAB[m]}</td>'
          f'<td>sorgente {lab_c(w["rsrc"])} &middot; carico {lab_c(w["rload"])} &middot; cavo {lab_c(w["cprobe"])}</td>'
          f'<td class="num"><strong>{fx(b["min"], 3)}°</strong></td>'
          f'<td class="num">{fx(b["at47"], 3)}°</td>'
          f'<td class="num">{fx(b["node_min"], 3)}°</td>{verdict(b["min"] >= PM_MIN)}</tr>')
    for p, t in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        w = v1["A"][p]
        A(f'<tr><td>Blocco A &middot; trim {t}</td>'
          f'<td>sorgente {lab_c(w["rsrc"])} &middot; cablaggio {lab_c(w["cwire"])}</td>'
          f'<td class="num"><strong>{fx(pm(w), 3)}°</strong></td><td class="num">&mdash;</td>'
          f'<td class="num">&mdash;</td>{verdict(pm(w) >= PM_MIN)}</tr>')
    w, wn = v1["F"], v1["Fn"]
    A(f'<tr><td>Buffer delle fisse</td>'
      f'<td>carico {lab_c(w["rld"])} &middot; cavo {lab_c(w["cprobe"])}</td>'
      f'<td class="num"><strong>{fx(pm(w), 3)}°</strong></td><td class="num">&mdash;</td>'
      f'<td class="num">{fx(pm(wn), 3)}°</td>{verdict(pm(w) >= PM_MIN)}</tr>')
    A('</table></div>')
    na = v1["A"]["notrim"]
    A(f'<p>Blocco B: {B["0db"]["n"]} righe per modo al jack, sorgenti dell&rsquo;attenuatore '
      'da 1 mΩ a (10 kΩ + Thévenin del trim)/4, carichi 100 kΩ e 10 kΩ. Le righe che '
      f'esistevano già in L27 tornano identiche (scarto {it(v1["B_L27_scarto"], 3)}°). '
      f'Blocco A: scala {trim["scale"].replace("/", " / ")} Ω; senza trim il minimo è '
      f'{fx(pm(na), 3)}° (sorgente {lab_c(na["rsrc"])}, {lab_c(na["cwire"])}). Con 4,7 nF sul '
      f'cablaggio, che ADR-024 non chiede, il blocco A a trim 0 dB scende a '
      f'{fx(pm(v1["A"]["0_all"]), 2)}°.</p>')
    A(figure("fig_v1.svg", "Margine di fase contro capacità del cavo"))
    b0 = B["0db"]
    A(f'<p>Al jack il margine <strong>non è monotono</strong>: a 0 dB il minimo, '
      f'{fx(b0["min"], 2)}°, cade a {lab_c(b0["w"]["cprobe"])}, e a 4,7 nF la stessa curva '
      f'risale a {fx(b0["at47"], 2)}°. Letto a 4,7 nF il verdetto sarebbe ottimista. Sul nodo, '
      f'dove nessun cavo vero sta, lo stesso blocco scende a {fx(b0["node_min"], 2)}°.</p>')
    A('<h3>Agli spigoli di tolleranza</h3>')
    A(prov_line("toll_L16.cir", v1["T_dir"], deckdir=os.path.join(L16X, "deck"),
                note=" &middot; <strong>deck d&rsquo;esplorazione</strong>, non sotto "
                     "<code>spice/preamp/tb/</code>"))
    A('<div class="tablewrap"><table><tr><th>Modo</th><th>Dove cade il minimo</th>'
      '<th class="num">Minimo agli spigoli</th><th>Esito</th></tr>')
    for m, w in v1["T"].items():
        A(f'<tr><td>Blocco B &middot; {MLAB[m]}</td>'
          f'<td>C124 {it(num(w, "c124") * 1e12, 4)} pF &middot; C137 {it(num(w, "c137") * 1e12, 4)} pF '
          f'&middot; R<sub>iso</sub> {it(num(w, "riso"), 4)} Ω &middot; sorgente {lab_c(w["rsrc"])} '
          f'&middot; carico {lab_c(w["rload"])} &middot; cavo {lab_c(w["ccable"])}</td>'
          f'<td class="num"><strong>{fx(pm(w), 3)}°</strong></td>{verdict(pm(w) >= PM_MIN)}</tr>')
    A('</table></div>')
    A('<p>C124 e C137 a ±5 %, R<sub>iso</sub> a ±1 %, su una griglia fitta di cavo fra '
      '2 e 4,7 nF. Il +10 dB non è negli spigoli: sta oltre i 100°.</p>')
    A('<h3>Il guadagno d&rsquo;anello</h3>')
    A(figure("fig_loop.svg", "Guadagno d'anello"))
    A('<div class="tablewrap"><table><tr><th>Blocco B, sorgente 2,5 kΩ, carico 100 kΩ</th>'
      '<th class="num">|T| a 10 Hz</th><th class="num">frequenza d&rsquo;incrocio</th>'
      '<th class="num">margine</th></tr>')
    for m in MODES:
        bb = v1["bode"][m]
        A(f'<tr><td>{MLAB[m]} &middot; cavo {lab_c(bb["C"])}</td>'
          f'<td class="num">{fx(bb["tdc"], 2)} dB</td>'
          f'<td class="num">{it(bb["fcross"] / 1000, 4)} kHz</td>'
          f'<td class="num">{fx(bb["pmarg"], 3)}°</td></tr>')
    A('</table></div>')
    A(f'<p class="meta">Le curve versionate sono quelle di L27, alla sorgente di 2,5 kΩ '
      f'(<code>{rel(v1["bode_dir"])}/</code>): L16 ha versionato la tabella dei margini '
      'anche per le sorgenti che il trim aggiunge, non le curve. La differenza fra le due '
      'sorgenti è nella tabella qui sopra, non in queste figure.</p>')

    # --- 6 trim, E3 ---
    A(h2("s6"))
    A(prov_line("tb_trim.cir", trim["dir"]))
    A('<p>Il trim è uno solo, fra l&rsquo;uscita del blocco A e l&rsquo;attenuatore '
      '(ADR-027): le uscite fisse prendono il segnale prima di lui e restano copia '
      f'fedele della sorgente. Scala per canale {trim["scale"].replace("/", " / ")} Ω, '
      'a relè bistabili. L&rsquo;attenuazione è misurata col carico dell&rsquo;attenuatore.</p>')
    A('<div class="tablewrap"><table><tr><th>Posizione</th><th class="num">Attenuazione a 1 kHz</th></tr>')
    for p, lab in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        A(f'<tr><td>{lab}</td><td class="num">{fx(trim["att"][p], 4)} dB</td></tr>')
    A('</table></div>')
    A('<p><strong>E3</strong> chiede ≥ 100 kΩ al connettore d&rsquo;ingresso <em>in ogni '
      'posizione del trim</em>, sul minimo di |Z<sub>in</sub>| fra 20 Hz e 20 kHz '
      '(«Nota su E3»). Col trim sul ramo variabile il connettore vede il blocco A; la '
      'capacità del selettore è spazzata.</p>')
    csels = sorted({c for _, c in trim["zmin"]}, key=capval)
    A('<div class="tablewrap"><table><tr><th>Posizione del trim</th>'
      + "".join(f'<th class="num">selettore {lab_c(c)}</th>' for c in csels) + '<th>Esito</th></tr>')
    for p, lab in (("99", "senza trim (riferimento)"), ("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        vals = [trim["zmin"].get((p, c)) for c in csels]
        ok = all(x is not None and x >= 1e5 for x in vals)
        A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{it(x / 1000, 4)} kΩ</td>' for x in vals)
          + (verdict(ok) if p != "99" else '<td class="na">&mdash;</td>') + '</tr>')
    A('</table></div>')

    # --- 7 E5 ---
    A(h2("s7"))
    A(prov_line("tb_zout_psrr_noise.cir", noise["zout_dir"]))
    A(prov_line("tb_noise_breakdown.cir", noise["nb_dir"]))
    A('<p><strong>E5</strong> chiede meno di 10 µV RMS in uscita fra 20 Hz e 20 kHz, non '
      'pesati, e di questi 1 µV è la quota dell&rsquo;alimentazione (ADR-020). '
      + ('Nessun modello simulato ha rumore 1/f, quindi <strong>queste cifre sono un '
         'pavimento, non una previsione</strong>, e il pavimento cade proprio dove il '
         'rumore del blocco è dominante (NC-004). ' if all_kf0 else '')
      + 'Ogni totale è ricontrollato integrando lo spettro versionato.</p>')
    A('<div class="tablewrap"><table><tr><th>Blocco da solo, uscita al jack</th>'
      '<th class="num">Rumore 20 Hz–20 kHz</th></tr>')
    for lab, val in noise["nb"]:
        A(f'<tr><td>{lab}</td><td class="num">{fx(val * 1e6, 3)} µV</td></tr>')
    for lab, val in noise["zout"][:3]:
        A(f'<tr><td>{lab}</td><td class="num">{fx(val * 1e6, 3)} µV</td></tr>')
    A('</table></div>')
    A('<p><strong>La catena col trim</strong>: blocco A, trim, attenuatore, blocco B, '
      'sorgente phono (430 Ω) o K11 (1,5 Ω), attenuatore al massimo o a metà corsa, '
      'tre modi. Per ogni posizione del trim la cella peggiore:</p>')
    A('<div class="tablewrap"><table><tr><th>Trim</th><th>Cella peggiore</th>'
      '<th class="num">Rumore</th><th>Esito contro 10 µV</th></tr>')
    for p, lab in (("99", "senza trim (riferimento)"), ("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        w = trim["e5w"][p]
        val = num(w, "onoise_uv")
        A(f'<tr><td>{lab}</td><td>{MLAB[w["mode"]]} &middot; attenuatore '
          f'{"al massimo" if w["att"] == "max" else "a metà"} &middot; sorgente {lab_c(w["rsrc"])}</td>'
          f'<td class="num"><strong>{fx(val, 3)} µV</strong></td>'
          + (f'<td class="{"na" if val < E5_MAX else "no"}">'
             f'{"sotto soglia &mdash; pavimento, NC-004" if val < E5_MAX else "sopra soglia"}</td>'
             if p != "99" else '<td class="na">&mdash;</td>') + '</tr>')
    A('</table></div>')

    # --- 8 headroom ---
    A(h2("s8"))
    A(prov_line("tb_dc_headroom.cir", hr["dir"]))
    A(figure("fig_headroom.svg", "Escursione in continua"))
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">Guadagno a 0 V</th>'
      '<th class="num">Finestra all&rsquo;1 % in ingresso</th><th class="num">v(OUT) ai bordi</th>'
      '<th class="num">Limite lineare</th><th class="num">Saturazione</th></tr>')
    for m in MODES:
        r = hr["modes"][m]
        A(f'<tr><td>{MLAB[m]}</td><td class="num">{fx(r["gain"], 5)} ×</td>'
          f'<td class="num">{fx(r["vi_lo"], 2)} … {fx(r["vi_hi"], 2)} V</td>'
          f'<td class="num">{fx(r["vo_lo"], 3)} … {fx(r["vo_hi"], 3)} V</td>'
          f'<td class="num">{fx(r["lin"], 4)} V RMS</td>'
          f'<td class="num">{fx(r["sat"], 4)} V RMS</td></tr>')
    A('</table></div>')
    A('<p>I modi non saturano allo stesso livello, e la differenza non sta nello stadio '
      'd&rsquo;uscita: a guadagno unitario v(FB) insegue v(OUT), il modo comune della '
      'coppia d&rsquo;ingresso sale con l&rsquo;uscita e si ferma per primo; con più guadagno '
      'v(FB) è una frazione di v(OUT) e l&rsquo;uscita arriva più in alto. È una proprietà '
      'della topologia; i valori esatti dipendono dai modelli.</p>')
    A('<h3>NC-009: una cifra, con la sua metrica</h3>')
    A('<p>Il caso che preoccupa è E6 × E2: il FiiO K11 a fondo scala dà 2,7 V RMS, e '
      'con rail a ±15 V (ADR-015) il +10 dB non ha quasi margine senza trim. La cifra '
      'pubblicata usa <strong>una</strong> metrica, <strong>M1</strong>, scelta in L16:</p>')
    A('<ul><li><strong>limite lineare</strong>: l&rsquo;uscita ai bordi della finestra in '
      'cui il guadagno locale dV<sub>out</sub>/dV<sub>in</sub> resta entro l&rsquo;1 % del '
      'valore a 0 V, il bordo minore in modulo, come seno RMS;</li>'
      '<li><strong>richiesto</strong>: 2,7 V RMS × il guadagno <em>misurato</em> a 0 V × '
      'l&rsquo;attenuazione del trim <em>misurata</em> (sezione 6);</li>'
      '<li><strong>margine</strong> = 20·log<sub>10</sub>(limite / richiesto).</li></ul>')
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">trim 0 dB</th>'
      '<th class="num">trim &minus;6 dB</th><th class="num">trim &minus;12 dB</th></tr>')
    for m in MODES:
        cells = []
        for p in ("0", "6", "12"):
            val = hr["modes"][m]["trim"][p]["M1"]
            s = f"{sg(val)} dB"
            cells.append(f'<td class="num">{"<strong>" + s + "</strong>" if (m, p) == ("10db", "6") else s}</td>')
        A(f'<tr><td>M1 &middot; {MLAB[m]}</td>{"".join(cells)}</tr>')
    A('</table></div>')
    t10 = hr["modes"]["10db"]["trim"]
    A(f'<p><strong>La cifra per NC-009 è {sg(t10["6"]["M1"])} dB</strong>: +10 dB, trim a '
      f'&minus;6 dB, metrica M1. Il caso raggiungibile per errore, +10 dB col trim a 0 dB, '
      f'lascia <strong>{sg(t10["0"]["M1"])} dB</strong>; il LED del trim (ADR-027) lo rende '
      'visibile.</p>')
    A('<p>Le altre due cifre che circolavano misurano cose diverse, e restano solo '
      'etichettate:</p>')
    A('<div class="tablewrap"><table><tr><th>+10 dB</th><th class="num">trim 0 dB</th>'
      '<th class="num">trim &minus;6 dB</th><th class="num">trim &minus;12 dB</th></tr>')
    for name, lab in (("M1", "<strong>M1</strong> &mdash; 1 % contro il richiesto misurato &mdash; <strong>la cifra</strong>"),
                      ("M2", "M2 &mdash; saturazione contro il richiesto nominale (ADR-015)"),
                      ("M3", "M3 &mdash; 1 % contro il richiesto nominale (dossier fino a L32)")):
        A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{sg(t10[p][name])} dB</td>'
                                          for p in ("0", "6", "12")) + '</tr>')
    A('</table></div>')
    A(f'<p class="meta">Ricontrollata su tutte le nove celle contro '
      f'<code>{hr.get("script", "headroom_nc009.py")}</code>, lanciato sugli stessi CSV e '
      'con le stesse attenuazioni. Il richiesto nominale è 2,7 V RMS × 10<sup>(G+T)/20</sup> '
      'coi valori di targa del modo e del trim.</p>')

    # --- 9 PSRR ---
    A(h2("s9"))
    A(prov_line("tb_zout_psrr_noise.cir", src(L27, "tb_zout_psrr_noise")))
    A(figure("fig_psrr.svg", "PSRR"))
    A('<div class="tablewrap"><table><tr><th>Rail e modo</th><th class="num">100 Hz</th>'
      '<th class="num">1 kHz</th><th class="num">10 kHz</th><th class="num">100 kHz</th></tr>')
    for rail in ("p", "m"):
        for m in MODES:
            r = psrr[(rail, m)]
            A(f'<tr><td>rail {"+" if rail == "p" else "−"} &middot; {MLAB[m]}</td>'
              + "".join(f'<td class="num">{fx(r[k], 2)} dB</td>' for k in ("p100", "p1k", "p10k", "p100k"))
              + '</tr>')
    A('</table></div>')
    wk = min(psrr, key=lambda k: psrr[k]["p10k"])
    A(f'<p>Il lato debole è il rail {"positivo" if wk[0] == "p" else "negativo"} a '
      f'{MLAB[wk[1]]}: <strong>{fx(psrr[wk]["p10k"], 2)} dB a 10 kHz</strong>. La quota '
      'di ripple che l&rsquo;alimentatore può lasciare si ricava da queste curve '
      '(«Nota su E5 — la quota del ripple», ADR-020).</p>')

    # --- 10 Zout ---
    A(h2("s10"))
    A(prov_line("tb_zout_psrr_noise.cir", src(L27, "tb_zout_psrr_noise")))
    A(figure("fig_zout.svg", "Impedenza d'uscita"))
    A('<div class="tablewrap"><table><tr><th>Punto di misura</th><th class="num">20 Hz</th>'
      '<th class="num">1 kHz</th><th class="num">20 kHz</th><th class="num">100 kHz</th></tr>')
    for m in MODES:
        r = z[m]
        A(f'<tr><td>al jack &middot; {MLAB[m]}</td>' + "".join(
            f'<td class="num">{it(r[k], 4)} Ω</td>' for k in ("z20", "z1k", "z20k", "z100k")) + '</tr>')
    for m in MODES:
        r = z[m]
        A(f'<tr><td>al nodo OUT &middot; {MLAB[m]}</td>' + "".join(
            f'<td class="num">{it(r[k], 4)} Ω</td>' for k in ("za20", "za1k", "za20k", "za100k")) + '</tr>')
    A('</table></div>')
    A(f'<div class="note"><strong>Tensione fra E4 ed E8, segnalata e non aggirata.</strong> '
      f'E4 chiede &lt; 100 Ω in banda passante. Al jack a 20 Hz la misura dà '
      f'{it(z["0db"]["z20"], 4)} Ω, ma quella <em>è la reattanza del condensatore '
      f'd&rsquo;uscita da 4,7 µF</em>: al nodo OUT la stessa frequenza dà '
      f'{it(z["0db"]["za20"], 3)} Ω. Per questo il requisito dice «misurata escludendo la '
      'reattanza del condensatore d&rsquo;accoppiamento».</div>')

    # --- 11 V2 ---
    A(h2("s11"))
    A(prov_line("tb_switch_v2.cir", v2["dir"]))
    A('<p><strong>V2</strong>: l&rsquo;anello non si apre mai commutando. Il deck modella '
      'K1 e K5 come contatti veri, con rimbalzi in chiusura e in apertura, e percorre '
      'ogni passaggio fra 0, +3 e +10 dB, compresi i due ordini in cui una coppia di relè '
      'può arrivare sul salto diretto. La previsione falsificabile: v(OUT) resta '
      'nell&rsquo;inviluppo del regime a +10 dB in ogni istante.</p>')
    A('<div class="tablewrap"><table><tr><th>Finestra</th><th class="num">v(OUT) max</th>'
      '<th class="num">v(OUT) min</th><th>Dentro l&rsquo;inviluppo del +10 dB</th></tr>')
    for x in v2["rows"]:
        A(f'<tr><td>{x["lab"]}</td><td class="num">{fx(x["vmax"], 4)} V</td>'
          f'<td class="num">{fx(x["vmin"], 4)} V</td>{verdict(x["inside"], "sì", "no")}</tr>')
    A('</table></div>')
    A(f'<p>Inviluppo del regime a +10 dB: {sg(v2["env_hi"], 4)} / {sg(v2["env_lo"], 4)} V. '
      f'Estremi sull&rsquo;intera corsa di 70 ms, rimbalzi compresi: {sg(v2["gmax"], 4)} / '
      f'{sg(v2["gmin"], 4)} V. La forma d&rsquo;onda non è versionata; le finestre sono '
      'confrontate con le <code>meas</code> del log.</p>')
    A('<h3>Il controfattuale: il relè nel ramo sbagliato</h3>')
    A(prov_line("tb_switch_v2_counterfactual.cir", cf["dir"]))
    A('<p>ADR-004 ha <strong>scartato</strong> il contatto in serie a R<sub>f</sub>. Una '
      'decisione porta informazione solo se la disposizione scartata è mostrata '
      '<em>fallire</em>: con R<sub>f</sub> aperto non esiste più controreazione, e '
      f'l&rsquo;uscita va a <strong>{fx(cf["rows"][1]["vout"], 4)} V</strong>, dove lo stadio '
      'non amplifica più niente.</p>')
    A(figure("fig_counterfactual.svg", "Controfattuale del relè di guadagno"))
    A('<div class="tablewrap"><table><tr><th>Stato</th><th>Configurazione</th>'
      '<th class="num">v(OUT)</th><th class="num">v(FB)</th></tr>')
    for r in cf["rows"]:
        A(f'<tr><td><strong>{r["tag"]}</strong></td><td>{html_escape(r["desc"])}</td>'
          f'<td class="num"><strong>{fx(r["vout"], 6)} V</strong></td>'
          f'<td class="num">{fx(r["vfb"], 6)} V</td></tr>')
    A('</table></div>')
    A('<p>C esiste per escludere che B sia un artefatto del solutore: A e C coincidono. '
      'La disposizione scelta commuta R<sub>g</sub> verso massa, e i due rami di ADR-026 '
      'stanno in parallelo: a contatti aperti il guadagno è 1 e <strong>l&rsquo;anello non '
      'si apre mai</strong>.</p>')

    # --- 12 V3, P7 ---
    A(h2("s12"))
    A(prov_line("tb_v3_overload.cir", v3["dir"]))
    A('<p><strong>V3</strong>, recupero dalla saturazione: +10 dB, 1 kHz, pilotato oltre '
      'il clipping per alcuni cicli e poi riportato a un livello basso.</p>')
    A('<div class="tablewrap"><table><tr><th>Grandezza</th><th class="num">Valore</th></tr>')
    A(f'<tr><td>v(OUT) massima, in clipping</td><td class="num">{sg(v3["vmax"], 3)} V</td></tr>')
    A(f'<tr><td>v(OUT) minima, in clipping</td><td class="num">{sg(v3["vmin"], 3)} V</td></tr>')
    A(f'<tr><td>v(JACK) a fine corsa, {fx(v3["t_end"] * 1000, 0)} ms</td>'
      f'<td class="num">{sg(v3["jack_end"] * 1000, 2)} mV</td></tr>')
    A('</table></div>')
    A('<p class="meta">Questi tre numeri hanno una sola strada: il deck non stampa '
      '<code>print</code>, quindi vengono dal CSV senza controllo incrociato. La cifra '
      '<code>.four</code> del deck non è riportata: con questi modelli è priva di '
      'significato.</p>')
    A('<h3>P7: ogni uscita regge un corto, il mute si tiene a tempo indefinito</h3>')
    A(prov_line("tb_mute_corto.cir", p7["dir"]))
    A(f'<p>Criterio di ADR-021: Tj = {it(TA, 3)} °C + P<sub>media</sub> · R<sub>θJA</sub> ≤ '
      f'{it(TJ_MAX, 3)} °C, con R<sub>θJA</sub> = {it(RTH_MJE, 3)} °C/W per i MJE in TO-220. '
      'Casi: normale, mute, corto su ciascuna uscita, apparecchio spento su una fissa; '
      'manopola e ampiezza spazzate, 1 kHz e 20 kHz. Il dispositivo d&rsquo;uscita peggiore '
      'per blocco e modo:</p>')
    A('<div class="tablewrap"><table><tr><th>Blocco</th>'
      + "".join(f'<th class="num">{MLAB[m]}</th>' for m in MODES) + '<th>Esito</th></tr>')
    for blk, lab in (("A", "Blocco A"), ("F1", "Buffer fissa 1"), ("F2", "Buffer fissa 2"), ("B", "Blocco B")):
        ws = [p7["worst"].get((blk, m)) for m in ("0", "3", "10")]
        A(f'<tr><td>{lab}</td>' + "".join(
            f'<td class="num">{it(w["p"] * 1000, 4)} mW &middot; {fx(w["tj"], 1)} °C</td>' if w else
            '<td class="num">&mdash;</td>' for w in ws)
          + verdict(all(w and w["tj"] <= TJ_MAX for w in ws)) + '</tr>')
    A('</table></div>')
    A(f'<p>Classe A sui percorsi ascoltabili (ADR-023): <strong>{p7["n_bad"]} righe su '
      f'{p7["n_listen"]}</strong> ne escono. La 47 Ω dell&rsquo;uscita principale dissipa al '
      f'massimo {it(p7["rsep"]["0"], 3)} / {it(p7["rsep"]["3"], 3)} / {it(p7["rsep"]["10"], 3)} W '
      'a 0 / +3 / +10 dB, e va dimensionata di conseguenza.</p>')

    # --- 13 requisiti ---
    A(h2("s13"))
    A('<p>Solo i requisiti che queste misure toccano. Il resto non è qui perché non è '
      'ancora stato misurato, non perché sia soddisfatto.</p>')
    g = {m: resp[(m, "1.5")]["g1k"] for m in MODES}
    A('<div class="tablewrap"><table><tr><th>Req.</th><th>Chiede</th><th>Misurato</th><th>Esito</th></tr>')
    A(f'<tr><td>E1</td><td>guadagno nominale 0 dB</td><td class="num">{fx(g["0db"], 4)} dB a 1 kHz</td>'
      f'{verdict(abs(g["0db"]) < 0.1)}</tr>')
    ok2 = abs(g["3db"] - 3.0) <= 0.1 and 9.5 <= g["10db"] <= 10.5
    A(f'<tr><td>E2</td><td>+3 dB (±0,1) e +10 dB (9,5–10,5)</td>'
      f'<td class="num">{sg(g["3db"], 4)} / {sg(g["10db"], 4)} dB a 1 kHz</td>{verdict(ok2)}</tr>')
    A(f'<tr><td>E3</td><td>≥ 100 kΩ al connettore, ogni posizione del trim</td>'
      f'<td class="num">min {it(trim["e3min"] / 1000, 4)} kΩ con {lab_c(trim["e3min_cs"])}</td>'
      f'{verdict(trim["e3min"] >= 1e5)}</tr>')
    z1k = max(z[m]["z1k"] for m in MODES)
    A(f'<tr><td>E4</td><td>Z<sub>out</sub> &lt; 100 Ω in banda, esclusa la reattanza del cap</td>'
      f'<td class="num">≤ {it(z1k, 4)} Ω a 1 kHz al jack, tre modi</td>'
      f'<td class="{"ok" if z1k < 100 else "no"}">{"conforme" if z1k < 100 else "no"} sull&rsquo;uscita '
      'principale; fisse e manopola: NC-008</td></tr>')
    A(f'<tr><td>E5</td><td>rumore in uscita &lt; 10 µV RMS</td>'
      f'<td class="num">catena ≤ {fx(trim["e5max"], 3)} µV</td>'
      '<td class="na">sotto soglia, ma pavimento senza 1/f &mdash; NC-004 aperta</td></tr>')
    A(f'<tr><td>E6×E2</td><td>2,7 V RMS d&rsquo;ingresso a +10 dB</td>'
      f'<td class="num">M1 {sg(t10["6"]["M1"])} dB col trim a &minus;6 dB &middot; '
      f'{sg(t10["0"]["M1"])} dB a trim 0</td>'
      f'<td class="{"ok" if t10["6"]["M1"] > 0 else "no"}">margine col trim (ADR-015, ADR-027); '
      'legenda di pannello ancora da fare (NC-009)</td></tr>')
    A(f'<tr><td>V1</td><td>margine ≥ 60° su tutta la matrice (ADR-019, ADR-024)</td>'
      f'<td class="num">minimo {fx(v1["min"], 3)}° &middot; {v1["min_where"]}</td>'
      f'{verdict(v1["min"] >= PM_MIN)}</tr>')
    okv2 = v2["all_inside"] and abs(cf["rows"][1]["vout"]) > 1.0
    A(f'<tr><td>V2</td><td>l&rsquo;anello non si apre mai commutando</td>'
      f'<td class="num">{sum(x["inside"] for x in v2["rows"])} finestre su {len(v2["rows"])} '
      f'nell&rsquo;inviluppo &middot; controfattuale a {fx(cf["rows"][1]["vout"], 3)} V</td>'
      f'{verdict(okv2)}</tr>')
    A(f'<tr><td>V3</td><td>recupero dalla saturazione</td>'
      f'<td class="num">clipping {sg(v3["vmax"], 3)} / {sg(v3["vmin"], 3)} V &middot; '
      f'{sg(v3["jack_end"] * 1000, 2)} mV al jack a fine corsa</td>'
      '<td class="na">impaginato dal CSV, senza controllo incrociato</td></tr>')
    A(f'<tr><td>P7</td><td>corto e mute a tempo indefinito, Tj ≤ 125 °C</td>'
      f'<td class="num">Tj massima {fx(p7["tjmax"], 1)} °C &middot; {p7["n_bad"]} righe '
      'ascoltabili fuori classe A</td>'
      f'{verdict(p7["tjmax"] <= TJ_MAX and p7["n_bad"] == 0)}</tr>')
    A('<tr><td>V4</td><td>THD/THD+N</td><td class="na">assente</td>'
      '<td class="na">modelli segnaposto: una cifra sarebbe priva di significato</td></tr>')
    A('</table></div>')

    # --- 14 limiti ---
    A(h2("s14"))
    A('<ul>')
    A('<li><strong>Niente distorsione.</strong> Con modelli segnaposto la non linearità '
      'non è stata adattata a niente: una cifra di THD sarebbe priva di significato.</li>')
    if all_kf0:
        A('<li><strong>Il rumore è un pavimento.</strong> Nessun modello simulato ha '
          'rumore 1/f: le cifre di E5 sono termico e shot. NC-004 resta aperta.</li>')
    A(f'<li><strong>{len(placeholders)} dispositivi attivi su '
      f'{len(vendors) + len(placeholders)} sono segnaposto</strong> ({", ".join(placeholders)}). '
      'I margini di fase, il PSRR e le impedenze hanno la forma giusta e numeri '
      'provvisori: la sostituzione coi modelli del costruttore è la Fase 4 (NC-017).</li>')
    A('<li><strong>E4 è misurata solo sull&rsquo;uscita principale</strong> e a manopola '
      'ferma (NC-008).</li>')
    A('<li><strong>Gli spigoli di tolleranza di V1</strong> vengono da un deck '
      'd&rsquo;esplorazione, non da un banco versionato sotto '
      '<code>spice/preamp/tb/</code>.</li>')
    A('<li><strong>Le forme d&rsquo;onda dei transitori</strong> non sono versionate: di V2 '
      'ci sono le finestre, di V3 il CSV.</li>')
    A('<li><strong>Nessuno qui giudica come suona.</strong> La simulazione copre '
      'stabilità, risposta, PSRR e impedenze; non copre l&rsquo;ascolto.</li>')
    A('</ul>')

    # --- 15 provenienza ---
    A(h2("s15"))
    A('<p>Ogni sezione dichiara il deck, la cartella dei dati e i modelli, e questi ultimi '
      'sono letti dagli <code>.include</code> del deck: un modello è «del costruttore» se '
      'sta in <code>models/</code> con la sua <code>.provenance.json</code>, «segnaposto» '
      'se sta in <code>spice/preamp/placeholder_devices.lib</code>.</p>')
    A('<div class="tablewrap"><table><tr><th>Modello istanziato</th><th>Parte</th>'
      '<th>File</th><th>Tipo</th><th class="num">KF</th></tr>')
    seen = {}
    for mm in allm:
        seen.setdefault(mm["model"], mm)
    for name in sorted(seen):
        mm = seen[name]
        A(f'<tr><td><code>{name}</code></td><td>{mm["part"]}</td><td><code>{mm["file"]}</code></td>'
          f'<td class="{"ok" if mm["vendor"] else "na"}">{"costruttore" if mm["vendor"] else "segnaposto"}</td>'
          f'<td class="num">{it(mm["kf"], 3)}</td></tr>')
    A('</table></div>')
    A('<p class="meta">Rigenerare questa pagina: '
      '<code>/usr/bin/python3 docs/preamp/dossier/build_dossier.py</code>. Rieseguire una '
      'misura: <code>/bin/zsh scripts/run_simulation.sh spice/preamp/tb/&lt;deck&gt;.cir '
      'results/preamp/&lt;deck&gt;</code>.</p>')
    A('<hr class="end">')
    A('</div>')

    return ('<meta charset="utf-8">\n<title>Dossier del preamp di linea</title>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
            'family=IBM+Plex+Mono:wght@400;500&'
            'family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&'
            'display=swap">\n'
            f"<style>{CSS}</style>\n" + "\n".join(h))


# ------------------------------------------------------------------ main ---
DECKS = ["tb_op.cir", "tb_ac.cir", "tb_loop.cir", "tb_loop_blockA.cir",
         "tb_loop_bufferfissa.cir", "tb_trim.cir", "tb_zout_psrr_noise.cir",
         "tb_noise_breakdown.cir", "tb_dc_headroom.cir", "tb_switch_v2.cir",
         "tb_switch_v2_counterfactual.cir", "tb_v3_overload.cir", "tb_mute_corto.cir"]


def main():
    standalone = None
    if "--standalone" in sys.argv:
        standalone = sys.argv[sys.argv.index("--standalone") + 1]

    M = {"resp": measure_response(), "v1": measure_v1(), "z": measure_zout(),
         "psrr": measure_psrr(), "noise": measure_noise(), "trim": measure_trim(),
         "cf": measure_counterfactual(), "v2": measure_v2(), "v3": measure_v3(),
         "p7": measure_p7(), "op": measure_oppoint()}
    M["hr"] = measure_headroom(M["trim"])
    M["decks"] = [os.path.join(TB, d) for d in DECKS]
    for deck in M["decks"]:
        provenance(deck)
    for name in SCHEMATICS:
        if not os.path.isfile(os.path.join(SCHEM, name)):
            refuse(f"schema mancante: {rel(os.path.join(SCHEM, name))}")

    if FAILURES:
        print("RIFIUTATO: il dossier non coincide con la propria evidenza.", file=sys.stderr)
        for f in FAILURES:
            print(f"  - {f}", file=sys.stderr)
        print("Nessun file e' stato scritto.", file=sys.stderr)
        return 1

    figs = {
        "fig_response.svg": fig_response(M["resp"]),
        "fig_response_adr014.svg": fig_response_adr014(M["resp"]),
        "fig_v1.svg": fig_v1(M["v1"]),
        "fig_loop.svg": fig_loop(M["v1"]),
        "fig_psrr.svg": fig_psrr(M["psrr"]),
        "fig_zout.svg": fig_zout(M["z"]),
        "fig_headroom.svg": fig_headroom(M["hr"]),
        "fig_counterfactual.svg": fig_counterfactual(M["cf"], M["hr"]),
    }
    page = build_page(M, inline=False)
    spage = build_page(M, inline=True) if standalone else None
    if FAILURES:          # la provenienza delle sezioni passa anche da build_page
        print("RIFIUTATO:", *FAILURES, sep="\n  - ", file=sys.stderr)
        print("Nessun file e' stato scritto.", file=sys.stderr)
        return 1

    for name, body in figs.items():
        with open(os.path.join(HERE, name), "w") as f:
            f.write(body)
        print(f"   scritto {name} ({len(body)} byte)")
    for name in SCHEMATICS:
        shutil.copyfile(os.path.join(SCHEM, name), os.path.join(HERE, name))
        print(f"   copiato {name} da {rel(SCHEM)}/")
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page)
    print(f"   scritto index.html ({len(page)} byte)")
    if standalone:
        with open(standalone, "w") as f:
            f.write(spage)
        print(f"   scritto {standalone} (autoconsistente, {len(spage)} byte)")

    v1, hr, trim = M["v1"], M["hr"], M["trim"]
    summary = {
        "dati": [rel(L27), rel(L16)],
        "controlli_incrociati": "tutti superati",
        "guadagno_1kHz_dB": {m: M["resp"][(m, "1.5")]["g1k"] for m in MODES},
        "adr014_scarto_20kHz_rif_1kHz_dB_peggiore": max(adr014(M["resp"])[0].values(), key=abs),
        "v1_minimo_gradi": v1["min"],
        "v1_minimo_per_istanza_gradi": {html_escape(k).replace("&amp;middot;", "·")
                                        .replace("&amp;minus;", "−"): x for k, x in v1["inst"]},
        "v1_spigoli_gradi": {m: pm(w) for m, w in v1["T"].items()},
        "headroom_nc009_M1_dB_10db_trim_-6": hr["modes"]["10db"]["trim"]["6"]["M1"],
        "headroom_nc009_M1_dB_10db_trim_0": hr["modes"]["10db"]["trim"]["0"]["M1"],
        "trim_attenuazione_dB": {p: trim["att"][p] for p in ("0", "6", "12")},
        "e3_min_zin_ohm": trim["e3min"],
        "e5_catena_peggiore_uV": trim["e5max"],
        "psrr_peggiore_10kHz_dB": min(r["p10k"] for r in M["psrr"].values()),
        "zout_jack_1kHz_ohm_0db": M["z"]["0db"]["z1k"],
        "p7_tj_massima_C": M["p7"]["tjmax"],
    }
    with open(os.path.join(HERE, "dossier.summary.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("   scritto dossier.summary.json")
    print("OK: tutti i controlli incrociati sono passati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
