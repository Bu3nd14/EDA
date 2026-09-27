#!/usr/bin/env python3
"""Costruisce il dossier del preamplificatore dai dati versionati.

    /usr/bin/python3 docs/preamp/dossier/build_dossier.py
    /usr/bin/python3 docs/preamp/dossier/build_dossier.py --standalone <file.html>

REGOLA CHE GOVERNA QUESTO FILE, ed e' la stessa del diagramma a blocchi di
L1: **nessuna cifra del dossier e' scritta a mano.** Ogni numero che
compare nella pagina viene letto dai file versionati sotto docs/preamp/data/
e calcolato qui.

L42a: la scheda audio del progetto di oggi. I 21 deck veloci sono stati
ricorsi il 2026-09-27 sul `main` di L28 (modelli del costruttore, Miller
1 nF di ADR-042) in data/2026-09-27/L42/dopo/, curve comprese: L40 le aveva
tolte prima del commit. **Nessun dato viene da un giorno in cui il blocco
simulava i segnaposto** (fino al 2026-09-21, e le cartelle `prima` di L39 e
L40): un percorso di dati che ne contiene uno fa rifiutare il generatore.
Gli SCRIPT di quei lotti (headroom_nc009.py di L16; e4.py di L13, copiato in
L42/script/e4_l42.py senza i numeri noti dei segnaposto) restano la
seconda strada, lanciati sui dati di oggi: passano da tool(), non da src().

La Zout di L27 fu misurata con la sorgente AC accesa (NC-033, limitations
#28): la guardia di L37 resta, anche se la data la copre gia'.

Ogni numero passa per una seconda strada indipendente, e se le due divergono
oltre la tolleranza dichiarata lo script **rifiuta e non scrive niente**, come
export_fab.sh sulla DRC:
  1. le curve CSV contro le `print` che ngspice ha stampato nel .log;
  2. le tabelle scritte con `echo` contro le `print` o le `meas` dello stesso
     log, riga per riga; una cella vuota e' un rifiuto (docs/limitations.md #26);
  3. la cifra di headroom di NC-009 contro quella che stampa
     data/2026-09-14/L16/esplorazione/script/headroom_nc009.py sugli stessi CSV;
  4. (L42a) ogni riga di risultato dei log di oggi contro quella del log di
     L40/dopo, corso il 2026-09-23 in un altro worktree sullo stesso circuito;
     le tabelle che L40 ha tenuto, byte per byte;
  5. (L42a) il mute: i verdetti della matrice di L29d2 ricalcolati da
     analisi.csv e dal manifesto; le celle peggiori contro quelle rifatte sul
     deck generato dal sorgente (L29e); la curva del livello al jack contro le
     S che v2_metodo.py ha scritto per la stessa cella;
  6. (L42a) l'interblocco: la corsa di L36 ricontata da corsa.csv contro
     sintesi.txt; il 2e rieseguito sulla netlist di oggi; i falsi di L35 e L36
     tutti caduti;
  7. (L42a) il calore: stima_telaio.py rieseguito contro il suo .txt, e la
     scheda audio della stima contro le correnti dei rail di tb_op di oggi.

L42b: l'alimentatore, la seconda scheda. Le cartelle dei lotti (L41a-L41c,
L30) sono la prima strada; le ricorse del 2026-09-27 la seconda
(data/2026-09-27/L42b, L42b-L41c, L42b-L41b2, con gli script dei lotti copiati
identici). Ogni log si legge prima dei suoi dati (limitations #33-#36), e ogni
deck rigenerato oggi da psu.net deve essere quello corso allora, a meno dei
percorsi del worktree: se no il circuito misurato non e' quello di oggi.
  8. la potenza: i banchi di L41a corsero sul psu.py di L41a, che L41b1 ha
     riscritto, e FORBIDDEN li rifiuta come prima strada. La prima e' la
     ricorsa di oggi; la seconda, lo stesso banco col carico di L41a, che
     deve ridare L41a su ogni colonna (0,5 ms o 1 %, 10 mV). Ogni scarto di
     oggi da L41a si pubblica; R512 si controlla caso per caso (#34);
     raddrizzatore.py rieseguito uguale byte per byte;
  9. il sorvegliante e i guasti (L41c): la catena ricorsa, analisi_seq.txt,
     i JSON del ponte, i deck al punto fisso e le uscite del core uguali;
 10. il temporizzatore (L41b1): analizza_timer.py rieseguito sui log di
     allora e su quelli corsi oggi, e i deck rigenerati uguali;
 11. il firmware (L41b2): la catena ricorsa come in 9; i falsi sull'host
     ricorsi uguali; i due falsi sul circuito caduti sul criterio giusto;
 12. le LDR (L41b2): analizza_ldr.py rieseguito sui log, le ricorse di oggi
     uguali, l'errore ricalcolato dalle correnti;
 13. spegnimento e failsafe al jack (L41c, L30): tabella.py rieseguito, le
     corse di oggi uguali, i deck rigenerati uguali, i dB SPL ricalcolati con
     la catena di NC-028 letta da NONCOMPLIANCE.md; le soglie di P9 lette da
     REQUIREMENTS.md.

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
DATAROOT = os.path.join(REPO, "docs", "preamp", "data")
# L42a: i 21 deck veloci corsi oggi, e la corsa di L40 che fa da seconda strada.
L42 = os.path.join(DATAROOT, "2026-09-27", "L42", "dopo")
L42M = os.path.join(DATAROOT, "2026-09-27", "L42", "mute")
L42S = os.path.join(DATAROOT, "2026-09-27", "L42", "script")
L40 = os.path.join(DATAROOT, "2026-09-23", "L40", "dopo")
L29D2 = os.path.join(DATAROOT, "2026-09-25", "L29d2")
L29E = os.path.join(DATAROOT, "2026-09-25", "L29e")
L35 = os.path.join(DATAROOT, "2026-09-25", "L35")
L36 = os.path.join(DATAROOT, "2026-09-25", "L36")
L30 = os.path.join(DATAROOT, "2026-09-26", "L30")
# Gli script dei lotti vecchi: codice, non dati. Passano da tool().
L16X = os.path.join(DATAROOT, "2026-09-14", "L16", "esplorazione")
TB = os.path.join(REPO, "spice", "preamp", "tb")
NET = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
SCHEM = os.path.join(REPO, "docs", "preamp", "schematic")
# L32b: i due schemi si COPIANO accanto a index.html e si collegano da li'.
# Un <img src="../schematic/..."> esce dalla cartella della pagina, e un
# visualizzatore che serve solo quella cartella li perdeva in silenzio,
# mentre le figure fig_*.svg accanto alla pagina restavano visibili.
SCHEMATICS = ("gain_block.svg", "preamp_blocks.svg", "psu_blocks.svg")
# L42a: i giorni in cui il blocco simulava i segnaposto (L39 li ha sostituiti il
# 2026-09-22), e le cartelle `prima` di L39 e L40, corse sul blocco di prima.
FORBIDDEN = ("2026-09-09", "2026-09-10", "2026-09-13", "2026-09-14", "2026-09-15",
             "2026-09-16", "2026-09-21", os.path.join("L39", "prima"),
             os.path.join("L40", "prima"),
             # L42b: i banchi di L41a corsero sul psu.py di L41a, che L41b1 ha
             # riscritto (il temporizzatore, Q505, il pilota delle LDR). Entrano
             # solo come seconda strada, da vecchio(); la prima e' la ricorsa
             os.path.join("L41a", "rete"), os.path.join("L41a", "guasti"),
             os.path.join("L41a", "varianti"))
# L42b: l'alimentatore. Le cartelle dei lotti e le ricorse di oggi.
L41A = os.path.join(DATAROOT, "2026-09-26", "L41a")
L41B1 = os.path.join(DATAROOT, "2026-09-26", "L41b1")
L41C = os.path.join(DATAROOT, "2026-09-26", "L41c")
L42B = os.path.join(DATAROOT, "2026-09-27", "L42b")
L42B_C = os.path.join(DATAROOT, "2026-09-27", "L42b-L41c")
L42B_B2 = os.path.join(DATAROOT, "2026-09-27", "L42b-L41b2")
PSU_NET = os.path.join(REPO, "circuits", "preamp", "psu.net")

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
    for bad in FORBIDDEN:
        if bad in p:
            raise SystemExit(f"RIFIUTATO: {rel(p)} viene da {bad}, dati corsi su un circuito "
                             "che non e' quello di oggi (i modelli segnaposto, il blocco di "
                             "prima di ADR-042, o il psu.py di L41a). "
                             "Nessun file e' stato scritto.")
    return p


def tool(root, *parts):
    """Uno script di un lotto vecchio, usato come seconda strada sui dati di oggi.
    Non e' un dato: non passa dal guardiano, ma deve esistere."""
    p = os.path.join(root, *parts)
    if not os.path.isfile(p):
        raise SystemExit(f"RIFIUTATO: manca lo script {rel(p)}. Nessun file e' stato scritto.")
    return p


# L37 (NC-033): tb_zout_psrr_noise.cir fino a L13 misurava la Zout con VSRC a
# 1 V AC. I suoi CSV _zout_ di L27 contengono il segnale (limitations #28).
ZOUT_FORBIDDEN = os.path.join("2026-09-14", "L27")


def zout_src(root, *parts):
    """Ogni percorso di dati di E4 passa di qui: niente Zout di L27."""
    p = src(root, *parts)
    if ZOUT_FORBIDDEN in p:
        raise SystemExit(f"RIFIUTATO: la Zout di {rel(p)} e' stata misurata con la sorgente "
                         "AC accesa (NC-033, #28). E4 si legge da data/2026-09-15/L13/. "
                         "Nessun file e' stato scritto.")
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
    if nrows is not None and len(rows) != nrows:
        refuse(f"{rel(path)}: attese {nrows} righe, trovate {len(rows)}")
    if not rows:
        refuse(f"{rel(path)}: tabella vuota")
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


_CUT = re.compile(r"^(\S+ = [-+0-9.eE]*)((?:Note|Warning): .*)$")
_TAIL = re.compile(r"^[-+0-9.eE]+$")
_SPLICED = {}


def log_lines(path):
    """Le righe del log, con le `print` spezzate ricucite.

    L42a (docs/limitations.md #37): ngspice scrive le Note/Warning del gmin
    stepping su stderr senza buffer e le `print` su stdout con buffer; nel .log
    unito una Note puo' cadere DENTRO una print. In tb_e4_uscite si legge
    `zn20k = 5Note: Starting dynamic gmin stepping`, poi le Note, poi
    `.720894e-01`. Si ricuce esattamente: il prefisso della riga tagliata piu'
    la prima riga fatta solo di cifre dopo le Note. Il conteggio delle
    ricuciture si pubblica."""
    out, pend = [], None
    with open(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if pend is not None:
                if _TAIL.match(line):
                    out.append(pend + line)
                    _SPLICED.setdefault(path, set()).add(len(out))
                    pend = None
                    continue
                if line.startswith(("Note: ", "Warning: ")):
                    continue
                refuse(f"{rel(path)}: una print spezzata da una Note non si ricuce "
                       f"({pend!r} seguita da {line[:40]!r})")
                pend = None
            m = _CUT.match(line)
            if m:
                pend = m.group(1)
                continue
            out.append(line)
    if pend is not None:
        refuse(f"{rel(path)}: una print spezzata da una Note resta aperta a fine log")
    return out


def _grep(path, pat):
    out = []
    for line in log_lines(path):
        m = pat.match(line)
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
# LSK489A (L20): the vendor model of models/jfet/lsk489.lib. Without this line a
# deck simulating it names a part "LSK489A" that no comment says, and the claims
# about "LSK489" read as claims about a part the deck does not simulate.
# L39 (NC-017): the manufacturer models the source instantiates since Fase 4.
# The part of MMBT5551/MMBT5401 is the MMBT, not the 2N (ADR-017); D1N914 is
# onsemi's model of the 1N4148 DO-35 (docs/limitations.md #20). The placeholder
# names stay: the dated decks under docs/preamp/data/ still simulate them.
PART = {"LSK489X": "LSK489", "LSK489A": "LSK489", "LS350": "LS352", "NSS2N5551": "2N5551",
        "PSS2N5401": "2N5401", "NMJE15032": "MJE15032", "PMJE15033": "MJE15033",
        "D1N4148": "1N4148",
        "MMBT5551": "MMBT5551", "MMBT5401": "MMBT5401", "QMJE15032": "MJE15032",
        "QMJE15033": "MJE15033", "D1N914": "1N4148"}
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
    return (f'<p class="prov">Deck <code>{html_escape(rel(os.path.join(deckdir, deck)))}</code>'
            f' &middot; dati <code>{html_escape(rel(datadir))}/</code>{note}<br>'
            f'Modelli del costruttore: <strong>{", ".join(ven) or "nessuno"}</strong>'
            f' &middot; segnaposto scritti a mano: <strong>{", ".join(ph) or "nessuno"}</strong>'
            f' &middot; {kf_phrase(ms)}</p>')


def kf_phrase(ms):
    """Chi porta il rumore 1/f, letto dalle .model (L42a: dopo L39 lo porta solo
    l'LSK489A; NC-004)."""
    with_kf = sorted({m["part"] for m in ms if m["kf"] != 0})
    if not with_kf:
        return "tutti KF = 0: nessun rumore 1/f (NC-004)"
    return (f'rumore 1/f solo su <strong>{", ".join(with_kf)}</strong>, KF = 0 sugli altri '
            '(NC-004)')


# ------------------------------------------------- seconda corsa: L40 -----
_RESULT = re.compile(r"^([A-Za-z_][\w().\[\]#-]*)\s*=\s+([-+0-9.eE]+)\s*$")


def _results(path):
    """Le righe di risultato di un log, nell'ordine: `print` compatte e `meas`
    incolonnate. Il resto (avanzamento, gmin stepping) dipende dai buffer."""
    out = []
    for line in log_lines(path):
        m = _RESULT.match(line)
        if m:
            try:
                out.append((m.group(1), float(m.group(2))))
            except ValueError:
                pass
    return out


def measure_l40(decks):
    """L42a, la seconda strada dei deck veloci: gli stessi deck corsi da L40 il
    2026-09-23, in un altro worktree, sullo stesso circuito (dopo L40 i deck non
    sono cambiati tranne tb_mute_corto.cir in L29e, e L28 ha toccato
    gain_block.py solo nei commenti). Ogni riga di risultato deve coincidere;
    ogni tabella che L40 ha tenuto, byte per byte. Un deck che non ha ne' righe
    di risultato ne' tabelle in L40 non ha questa strada, e si dice."""
    out = {"decks": [], "n_res": 0, "n_tab": 0, "senza": []}
    for deck in decks:
        b = os.path.splitext(deck)[0]
        d42, d40 = src(L42, b), src(L40, b)
        a, c = _results(os.path.join(d42, b + ".log")), _results(os.path.join(d40, b + ".log"))
        if [k for k, _ in a] != [k for k, _ in c]:
            refuse(f"{b}: le righe di risultato di oggi e di L40 non hanno gli stessi nomi "
                   f"nello stesso ordine ({len(a)} contro {len(c)})")
            continue
        worst = 0.0
        for (k, x), (_, y) in zip(a, c):
            den = abs(y) if abs(y) > 1e-30 else 1.0
            worst = max(worst, abs(x - y) / den)
        if not worst <= 1e-9:
            refuse(f"{b}: oggi e L40 differiscono fino a {worst:.2e} (relativo)")
        tabs = sorted(f for f in os.listdir(d40) if f.endswith(".csv"))
        for t in tabs:
            with open(os.path.join(d42, t), "rb") as f1, open(os.path.join(d40, t), "rb") as f2:
                if f1.read() != f2.read():
                    refuse(f"{b}/{t}: la tabella di oggi non e' quella di L40 byte per byte")
        out["n_res"] += len(a)
        out["n_tab"] += len(tabs)
        out["decks"].append((b, len(a), len(tabs)))
        if not a and not tabs:
            out["senza"].append(b)
    out["spliced"] = sum(len(v) for p, v in _SPLICED.items() if p.startswith(L42))
    return out


# --------------------------------------------------------------- misure ---
RS_AC = ("1.5", "430", "2500", "10k")
AC_ORDER = [(m, r) for m in MODES for r in RS_AC]


def measure_response():
    """Risposta in frequenza, tb_ac di L27: 3 modi x 4 sorgenti."""
    d = src(L42, "tb_ac")
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
    d = src(L42, "tb_loop")
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

    # --- Bode: il deck scrive le curve alla sorgente di 2,5 k e carico 100 k
    # (L42a: la stessa scelta di L27, che le aveva sole; ora le righe a 2,5 k
    # stanno nella tabella di 660 insieme alle sorgenti del trim).
    bode = {}
    for m in MODES:
        cand = [r for r in tab if r["mode"] == m and r["pos"] == "1"
                and r["rsrc"] == "2.5k" and r["rload"] == "100k"]
        w = min(cand, key=pm)
        rows = load_csv(os.path.join(d, f"tb_loop_att2k5_{m}_{w['cprobe']}.csv"))
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
    v["bode_dir"] = d

    # --- blocco A (L16): senza trim e col partitore, scala 2 (845/464/464)
    d = src(L42, "tb_loop_blockA")
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
    d = src(L42, "tb_loop_bufferfissa")
    tab = _loop_table(d, "tb_loop_bufferfissa.csv", 44, "tb_loop_bufferfissa.log")
    v["F"] = min([r for r in tab if r["pos"] == "1"], key=pm)
    v["Fn"] = min([r for r in tab if r["pos"] == "2"], key=pm)
    v["F_dir"] = d
    # L42a: gli spigoli di tolleranza (toll_L16) erano un deck d'esplorazione
    # sui segnaposto e non sono stati rifatti coi modelli del costruttore. Non
    # si leggono: la pagina lo dice in «Cosa questo dossier non dice».

    inst = [(f"Blocco B &middot; {MLAB[m]}", B[m]["min"]) for m in MODES]
    inst += [(f"Blocco A &middot; trim {t}", pm(A[p]))
             for p, t in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB"))]
    inst += [("Buffer delle fisse", pm(v["F"]))]
    v["inst"] = inst
    v["min"] = min(x for _, x in inst)
    v["min_where"] = min(inst, key=lambda t: t[1])[0]
    return v


def count_errors(path):
    """Righe `Error` di un log: ngspice esce 0 anche con quelle (#26)."""
    with open(path) as f:
        return sum(1 for ln in f if "Error" in ln)


# L37, la firma di #28. La sezione Zout inietta 1 A AC; VSRC, se resta accesa,
# vale 1 V AC. Il segnale aggiunge allora al nodo OUT circa G_lin x (1 V / 1 A):
# 1,0355 Ω a 0 dB nei dati di L27, contro 0,0386 Ω veri. NON si riconosce dal
# fatto che "scala col guadagno": la Zout vera del blocco scala anch'essa col
# guadagno del modo (il guadagno d'anello cala), 0,0387 Ω x G_lin in tutti e tre
# i modi. Si riconosce dalla grandezza.
ZSIG_FRAC = 0.5


def measure_zout(resp):
    """Le curve di Zout: tb_zout_psrr_noise corretto in L13 (sorgente spenta)."""
    d = zout_src(L42, "tb_zout_psrr_noise")
    log = os.path.join(d, "tb_zout_psrr_noise.log")
    n_err = count_errors(log)
    if n_err:
        refuse(f"{rel(log)}: {n_err} righe 'Error' (#26)")
    keys = ("z20", "z1k", "z20k", "za20", "za1k", "za20k", "za100k")
    lv = {k: log_print(log, k) for k in keys}
    for k in keys:
        if len(lv[k]) != 3:
            refuse(f"tb_zout_psrr_noise.log: attese 3 occorrenze di {k}, trovate {len(lv[k])}")
    out = {"dir": d}
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
        r["glin"] = 10 ** (resp[(m, "1.5")]["g1k"] / 20)
        if not r["za1k"] < ZSIG_FRAC * r["glin"]:
            refuse(f"Zout(OUT) {m} @1 kHz: {r['za1k']:.5g} Ω non sta sotto {ZSIG_FRAC} x G_lin "
                   f"= {ZSIG_FRAC * r['glin']:.5g} Ω: la Zout al nodo contiene il segnale del "
                   "modo, sorgente AC accesa durante l'iniezione (NC-033, #28)")
        out[m] = r
    return out


E4_OUTS = ("main", "fix1", "fix2")
E4_COLS = ("zrmax", "zr20", "zr1k", "zr20k", "zm20", "zm1k", "zn1k", "zn20k")
E4_MAX = 100.0         # Ω, E4
E4_COSTANZA = 1.0      # Ω, lettura di L13 (e4.py): E4 non da' tolleranza


def _markers(log, pat):
    return [m.groups() for m in (re.match(pat, ln) for ln in log_lines(log)) if m]


def measure_e4(z):
    """E4 sulle tre uscite e a manopola che gira: tb_e4_uscite di L13."""
    d = zout_src(L42, "tb_e4_uscite")
    log = os.path.join(d, "tb_e4_uscite.log")
    n_err = count_errors(log)
    if n_err:
        refuse(f"{rel(log)}: {n_err} righe 'Error' (#26)")
    tab = load_table(os.path.join(d, "tb_e4_uscite_tab.csv"), 135)
    gain = load_table(os.path.join(d, "tb_e4_uscite_guadagno.csv"), 45)

    # le righe delle tabelle nell'ordine dei marcatori del log, poi colonna per colonna
    for label, rows, cols, pat in (
            ("tb_e4_uscite_tab.csv", tab, ("out", "trim", "att", "mode"),
             r"^CELL out=(\w+) trim=(\d+) att=(\d+) mode=(\w+)$"),
            ("tb_e4_uscite_guadagno.csv", gain, ("trim", "att", "mode"),
             r"^GAIN trim=(\d+) att=(\d+) mode=(\w+)$")):
        mine = [tuple(r.get(c) for c in cols) for r in rows]
        theirs = _markers(log, pat)
        if mine != theirs:
            i = next((i for i, (a, b) in enumerate(zip(mine, theirs)) if a != b),
                     min(len(mine), len(theirs)))
            refuse(f"{label}: l'ordine delle righe non e' quello del log dalla riga {i + 2} "
                   f"({len(mine)} righe, {len(theirs)} marcatori)")
    for c in E4_COLS:
        cross_table(f"tb_e4_uscite_tab.csv [{c}]", tab, c, log_print(log, c))
    cross_table("tb_e4_uscite_guadagno.csv [g1k_db]", gain, "g1k_db", log_print(log, "g1k"))

    out = {"dir": d, "groups": []}
    for o, ms in [("main", (m,)) for m in MODES] + [(o, MODES) for o in ("fix1", "fix2")]:
        sel = [r for r in tab if r.get("out") == o and r.get("mode") in ms]
        if not sel:
            refuse(f"tb_e4_uscite_tab.csv: nessuna riga per {o} {'+'.join(ms)}")
            continue
        g = {"out": o, "modes": ms, "n": len(sel)}
        for c in ("zrmax", "zr1k", "zm1k", "zn1k"):
            vs = [num(r, c) for r in sel]
            g[c + "_min"], g[c + "_max"] = min(vs), max(vs)
            g[c + "_disp"] = max(vs) - min(vs)
        g["disp"] = max(g[c + "_disp"] for c in ("zrmax", "zr1k", "zm1k"))
        out["groups"].append(g)

    # stessa grandezza da due deck diversi: il flat corretto e la catena in subckt
    for m in MODES:
        for r in tab:
            if r.get("out") != "main" or r.get("mode") != m:
                continue
            bad = [(zk, tk) for zk, tk in (("za1k", "zn1k"), ("z1k", "zm1k"))
                   if not abs(z[m][zk] - num(r, tk)) <= 1e-3 * abs(num(r, tk))]
            if bad:
                zk, tk = bad[0]
                refuse(f"Zout {m}: tb_zout_psrr_noise {zk} {z[m][zk]:.6g} Ω, tb_e4_uscite main "
                       f"trim {r['trim']} att {r['att']} {tk} {num(r, tk):.6g} Ω "
                       "(scarto > 1e-3): i due deck non misurano la stessa impedenza")
                break

    # la stessa cifra dal verificatore di L13, sugli stessi file
    script = tool(L42S, "e4_l42.py")
    proc = subprocess.run([sys.executable, script, d], capture_output=True, text=True)
    if proc.returncode != 0:
        tail = " | ".join(proc.stdout.strip().splitlines()[-3:])
        refuse(f"e4.py esce {proc.returncode}: {tail[-300:]}")
        return out
    got = {}
    for ln in proc.stdout.splitlines():
        t = ln.replace("..", " ").split()
        if len(t) == 11 and t[0] in E4_OUTS:
            got[(t[0], t[1])] = [float(x) for x in t[2:]]
    for g in out["groups"]:
        key = (g["out"], "+".join(g["modes"]))
        if key not in got:
            refuse(f"e4.py: manca la riga {' '.join(key)}")
            continue
        n, zrmax, r1a, r1b, m1a, m1b, na, nb, dsp = got[key]
        mine = (g["n"], g["zrmax_max"], g["zr1k_min"], g["zr1k_max"], g["zm1k_min"],
                g["zm1k_max"], g["zn1k_min"], g["zn1k_max"], g["zrmax_disp"])
        # lo script stampa 4 decimali, 5 al nodo, 3 cifre per la dispersione
        tol = (0, 5.1e-5, 5.1e-5, 5.1e-5, 5.1e-5, 5.1e-5, 5.1e-6, 5.1e-6, 5.1e-8 + 5e-4 * dsp)
        for name, a, b, tl in zip(("celle", "Re(Z)max", "Re(Z)1k min", "Re(Z)1k max",
                                   "|Z|1k min", "|Z|1k max", "nodo min", "nodo max",
                                   "dispersione Re(Z)max"),
                                  mine, (n, zrmax, r1a, r1b, m1a, m1b, na, nb, dsp), tol):
            if not abs(a - b) <= tl:
                refuse(f"E4 {' '.join(key)} {name}: dossier {a:.6g}, e4.py {b:.6g}")
    out["script"] = rel(script)
    return out


PSRR_ORDER = [("p", m) for m in MODES] + [("m", m) for m in MODES]


def measure_psrr():
    d = src(L42, "tb_zout_psrr_noise")
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
    d = src(L42, "tb_zout_psrr_noise")
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

    d = src(L42, "tb_noise_breakdown")
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
    d = src(L42, "tb_trim")
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
    d = src(L42, "tb_dc_headroom")
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
    script = tool(L16X, "script", "headroom_nc009.py")
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
    d = src(L42, "tb_switch_v2_counterfactual")
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
    d = src(L42, "tb_switch_v2")
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
    d = src(L42, "tb_v3_overload")
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
    d = src(L42, "tb_mute_corto")
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
    d = src(L42, "tb_op")
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


# ------------------------------------------------------------ il mute -----
V2_AB = 100e-6        # V di picco, A e B (ADR-032)
V2_S = 20.0           # dB in 100 ms, S (ADR-040)
V2_SOGLIA = {"A_ins": V2_AB, "A_rel": V2_AB, "B2": V2_AB, "S_ins": V2_S, "S_rel": V2_S}
S_PAV = -70.0         # dB, il pavimento di S (v2_metodo.py, PAVIMENTO_S)
S_FIN = 100           # campioni da 1 ms: la finestra di S, 100 ms (ADR-040)
V2_GRUPPI = {"1": "cambio di guadagno", "2": "cambio di trim", "3": "dispersione dell&rsquo;LSK489",
             "4": "durata del mute", "5": "accensione"}


def _csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def v2_verdetti(man_path, ana_path):
    """I verdetti di V2 ricalcolati da analisi.csv e dal manifesto, con la regola di
    verdetto.py (L29c) scritta di nuovo qui: per cella e grandezza di verdetto,
    il peggiore sulle tre uscite; regge se sta sotto la soglia e nessuna uscita
    ha la finestra corta."""
    man = {r["cella"]: r for r in _csv(man_path)}
    ana = {}
    for a in _csv(ana_path):
        ana.setdefault((a["cella"], a["grandezza"]), []).append(a)
    out = {}
    for c, r in man.items():
        for g in [x for x in r.get("conta", "").split(";") if x]:
            vals = ana.get((c, g), [])
            if len(vals) != 3:
                refuse(f"{rel(ana_path)}: {c} {g} ha {len(vals)} uscite, attese 3")
                continue
            w = max(vals, key=lambda a: float(a["picco_V"]) if a["picco_V"] else float("inf"))
            v = float(w["picco_V"]) if w["picco_V"] else None
            ok = (v is not None and v <= V2_SOGLIA[g]
                  and not any("non accetta" in a["esito"] for a in vals))
            out[(c, g)] = {"cella": c, "g": g, "gruppo": r["gruppo"], "amp": float(r["amp"]),
                           "f": r["f_hz"], "gm": r["gm"], "uscita": w["uscita"], "v": v, "ok": ok}
    return out


def measure_mute():
    """Il mute: LDR col profilo v4 a monte, relè al jack in serie, geometria iii
    (ADR-038, ADR-039, ADR-040, ADR-044)."""
    out = {}
    # --- 1. la matrice di L29d2 sulla geometria iii: verdetto.csv contro il ricalcolo
    d = src(L29D2, "matrice")
    mine = v2_verdetti(os.path.join(d, "manifest_sel.csv"), os.path.join(d, "analisi.csv"))
    theirs = _csv(os.path.join(d, "verdetto.csv"))
    if len(theirs) != len(mine):
        refuse(f"L29d2 verdetto.csv: {len(theirs)} verdetti, il ricalcolo ne da' {len(mine)}")
    for t in theirs:
        m = mine.get((t["cella"], t["grandezza"]))
        if m is None:
            refuse(f"L29d2 verdetto.csv: {t['cella']} {t['grandezza']} non viene dal ricalcolo")
            continue
        if abs(float(t["soglia"]) - V2_SOGLIA[t["grandezza"]]) > 1e-12:
            refuse(f"L29d2 verdetto.csv: soglia {t['soglia']} per {t['grandezza']}, "
                   f"il dossier usa {V2_SOGLIA[t['grandezza']]} (ADR-032, ADR-040)")
        if (t["uscita"] != m["uscita"] or float(t["picco"]) != m["v"]
                or (t["esito"] == "regge") != m["ok"]):
            refuse(f"L29d2 verdetto.csv: {t['cella']} {t['grandezza']} scritto "
                   f"{t['picco']} {t['uscita']} {t['esito']}, ricalcolato {m['v']} "
                   f"{m['uscita']} {'regge' if m['ok'] else 'NON REGGE'}")
    out["mat_dir"] = d
    out["n"] = len(mine)
    out["n_fuori"] = sum(1 for m in mine.values() if not m["ok"])
    rows = []
    for gr in sorted(V2_GRUPPI):
        sel = [m for m in mine.values() if m["gruppo"] == gr]
        row = {"gruppo": gr, "lab": V2_GRUPPI[gr], "n": len(sel),
               "fuori": sum(1 for m in sel if not m["ok"])}
        for crit, gs in (("A", ("A_ins", "A_rel")), ("B2", ("B2",)), ("S", ("S_ins", "S_rel"))):
            cand = [m for m in sel if m["g"] in gs]
            row[crit] = max(cand, key=lambda m: m["v"]) if cand else None
        rows.append(row)
    if sum(r["n"] for r in rows) != len(mine):
        refuse(f"L29d2: {len(mine)} verdetti, i gruppi 1-5 ne contano {sum(r['n'] for r in rows)}")
    out["rows"] = rows

    # --- 2. le celle peggiori rifatte sul deck generato dal sorgente (L29e)
    d = src(L29E, "celle")
    src_v = v2_verdetti(os.path.join(d, "manifest_sel.csv"), os.path.join(d, "analisi.csv"))
    tab = _csv(src(L29E, "tabella_sorgente.csv"))
    worst = 0.0
    for t in tab:
        s = src_v.get((t["cella"], t["grandezza"]))
        b = mine.get((t["cella"], t["grandezza"]))
        if s is None or b is None:
            refuse(f"L29e tabella_sorgente.csv: {t['cella']} {t['grandezza']} manca "
                   f"{'nel ricalcolo del sorgente' if s is None else 'nella matrice di L29d2'}")
            continue
        for lab, x, y in (("sorgente", float(t["sorgente"]), s["v"]),
                          ("banco_L29d2", float(t["banco_L29d2"]), b["v"])):
            if not abs(x - y) <= 5e-4 * abs(y):
                refuse(f"L29e tabella_sorgente.csv: {t['cella']} {t['grandezza']} {lab} "
                       f"scritto {x}, ricalcolato {y}")
        worst = max(worst, abs(s["v"] - b["v"]) / (abs(b["v"]) or 1.0))
        if not s["ok"]:
            refuse(f"L29e: {t['cella']} {t['grandezza']} non regge sul sorgente")
    out["src_n"] = len(tab)
    out["src_scarto"] = worst
    out["src_dir"] = d

    # --- 3. la cella del grafico, rifatta oggi sul deck versionato (L42a)
    d = src(L42M)
    today = _csv(os.path.join(d, "analisi.csv"))
    man = {r["cella"]: r for r in _csv(os.path.join(d, "manifest_sel.csv"))}
    # ogni riga, con l'istante del picco: C_pav ha due righe per uscita, una per evento
    key = lambda a: (a["cella"], a["grandezza"], a["uscita"], a["t_picco_s"], a["picco_V"])  # noqa: E731
    mine_rows = sorted(key(a) for a in today)
    e29 = sorted(key(a) for a in _csv(os.path.join(src(L29E, "celle"), "analisi.csv"))
                 if a["cella"] in man)
    if mine_rows != e29:
        diff = sorted(set(mine_rows) ^ set(e29))
        refuse(f"L42 mute analisi.csv: {len(diff)} righe diverse da L29e sulle stesse celle, "
               f"la prima {diff[0] if diff else '(conteggi diversi)'}")
    cell = [c for c, r in man.items() if r["tipo"] == "evento"]
    if len(cell) != 1:
        refuse(f"L42 mute: attesa una cella evento nel manifesto, trovate {len(cell)}")
        return out
    c = man[cell[0]]
    rows = load_table(os.path.join(d, "profilo.csv"), None)
    t = [num(r, "t_s") for r in rows]
    lv = [num(r, "livello_db") for r in rows]
    s_mine = {}
    tg = float(c["t_grad"])
    for nm, te in (("S_ins", float(c["t_ins"])), ("S_rel", float(c["t_rel"]))):
        lo, hi = te - 0.020, te + tg + 0.200
        L = [max(x, S_PAV) for tt, x in zip(t, lv) if lo - 1e-9 <= tt < hi]
        s_mine[nm] = max(abs(L[j + S_FIN] - L[j]) for j in range(len(L) - S_FIN))
        theirs = [float(a["picco_V"]) for a in today
                  if a["cella"] == c["cella"] and a["grandezza"] == nm and a["uscita"] == "MAINJACK"]
        check(f"S {nm} dalla curva del livello", s_mine[nm], at(theirs, 0), 5e-4)
    out["prof"] = {"t": t, "lv": lv, "cella": c["cella"], "t_ins": float(c["t_ins"]),
                   "t_rel": float(c["t_rel"]), "tg": tg, "f": c["f_hz"], "gm": c["gm"],
                   "S": s_mine, "n_today": len(today)}
    out["prof_dir"] = d

    # --- 4. la cima dei LED nei deck che hanno prodotto questi numeri, letta dalla tabella
    # del profilo (BILS: I = pow(10, pwl(V(DEP), 0, log10(I_cima), ...))
    cime = []
    for deck in (os.path.join(TB, "tb_v2_casopeggiore.cir"),
                 os.path.join(L29D2, "deck", "tb_v2_l29d2.cir")):
        with open(deck) as f:
            txt = f.read()
        ms = re.findall(r"^BILS .*pow\(10, *pwl\(V\(DEP\), *0, *(-?[\d.]+),", txt, re.M)
        # la derivazione: I = 1e-08 * pow(2e+06, ...) arriva a 1e-08 x 2e+06 a d = 1
        mp = re.findall(r"^BILP .*\* *([\d.eE+-]+) *\* *pow\(([\d.eE+-]+), *min\(", txt, re.M)
        if len(ms) != 1 or len(mp) != 1:
            refuse(f"{rel(deck)}: attese le due tabelle dei LED (BILS, BILP), "
                   f"trovate {len(ms)} e {len(mp)}")
            continue
        i_s, i_p = 10 ** float(ms[0]), float(mp[0][0]) * float(mp[0][1])
        if abs(i_s - i_p) > 1e-3 * i_s:
            refuse(f"{rel(deck)}: cima della serie {i_s:.4g} A, della derivazione {i_p:.4g} A")
        cime.append(i_s)
    if len(cime) != 2 or abs(cime[0] - cime[1]) > 1e-12:
        refuse(f"la cima dei LED non e' la stessa nel deck versionato e nel banco di L29d2: {cime}")
    out["cima_deck"] = cime[0] if cime else float("nan")
    return out


L41B2 = os.path.join(DATAROOT, "2026-09-26", "L41b2")
LDR_STATI = {"gioco": "in ascolto (serie a 12 mA, derivazione spenta)",
             "meta": "a metà del profilo", "mute": "in mute (derivazione a 12 mA)"}


def measure_ldr_e3e5():
    """E3 ed E5 con le LDR del mute all'ingresso del blocco A, con la cima a 12 mA
    di ADR-050: la copia del deck di L29b2 fatta in L41b2 (copia_12mA.py cambia
    solo le correnti dei LED e le resistenze della cella in serie)."""
    d = src(L41B2, "e3_e5")
    log = os.path.join(d, "tb_e3_e5_ldr_cima12mA.log")
    e3 = load_table(os.path.join(d, "tb_e3_e5_ldr_cima12mA_e3.csv"), 27)
    e5 = load_table(os.path.join(d, "tb_e3_e5_ldr_cima12mA_e5.csv"), 108)
    cross_table("tb_e3_e5_ldr_cima12mA_e3.csv [zmin_ohm]", e3, "zmin_ohm", log_print(log, "zmin"))
    cross_table("tb_e3_e5_ldr_cima12mA_e5.csv [onoise_uv]", e5, "onoise_uv", log_print(log, "onu"))
    n_err = count_errors(log)
    if n_err:
        refuse(f"{rel(log)}: {n_err} righe 'Error' (#26)")
    csels = sorted({r["csel"] for r in e3}, key=capval)
    z = {(s, c): min(num(r, "zmin_ohm") for r in e3 if r["stato"] == s and r["csel"] == c)
         for s in LDR_STATI for c in csels}
    n5 = {l: max(num(r, "onoise_uv") for r in e5 if r["ldr"] == l)
          for l in sorted({r["ldr"] for r in e5})}
    if "nessuna" not in n5:
        refuse("tb_e3_e5_ldr_cima12mA_e5.csv: manca la catena senza LDR")
    rs = sorted({r["rs_ohm"] for r in e3 if r["stato"] == "gioco"})
    return {"dir": d, "deck": "tb_e3_e5_ldr_cima12mA.cir", "csels": csels, "z": z,
            "e3min": min(z.values()), "e5": n5,
            "e5max": max(v for k, v in n5.items() if k != "nessuna"), "rs_gioco": rs}


# ------------------------------------------------------ l'interblocco -----
def measure_interlock():
    """Il guadagno interbloccato (ADR-041, L36) e i comandi a pannello (ADR-045, L35)."""
    out = {}
    # --- la corsa al rilascio del mute: corsa.csv ricontato contro sintesi.txt
    d = src(L36, "corsa")
    rows = _csv(os.path.join(d, "corsa.csv"))
    cnt = {}
    for r in rows:
        v = cnt.setdefault(r["variante"], {"n": 0, "ril": 0, "ins": 0, "bad": 0})
        v["n"] += 1
        v["ril"] += r["tiene_al_rilascio"] != "True"
        v["ins"] += r["tiene_all_inserimento"] != "True"
        v["bad"] += not (r["rc"] == "0" and r["corsa"] == "ok")
    with open(os.path.join(d, "sintesi.txt")) as f:
        sint = f.read()
    for var in ("ingenua", "progetto"):
        m = re.search(r"== " + var + r": (\d+) celle\n\s+cade al rilascio del mute:\s+(\d+)\n"
                      r"\s+cade all'inserimento del mute:\s+(\d+)", sint)
        if not m or var not in cnt:
            refuse(f"L36 sintesi.txt: manca il blocco della variante {var}")
            continue
        got = tuple(int(x) for x in m.groups())
        mine = (cnt[var]["n"], cnt[var]["ril"], cnt[var]["ins"])
        if got != mine:
            refuse(f"L36 {var}: sintesi.txt {got}, corsa.csv ricontato {mine}")
    if any(v["bad"] for v in cnt.values()):
        refuse("L36 corsa.csv: corse non andate a buon fine")
    out["corsa"] = cnt
    out["corsa_n"] = len(rows)
    out["corsa_dir"] = d

    # --- il 2e rieseguito sulla netlist di oggi
    proc = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "check_relay_safe_state.py"),
                           NET], capture_output=True, text=True)
    if proc.returncode != 0:
        refuse(f"check_relay_safe_state.py esce {proc.returncode} sulla netlist di oggi")
    txt = proc.stdout
    relays = re.findall(r"^\s+(K\d+)\s+'([^']+)'\s+ruolo=(\w+)$", txt, re.M)
    m = re.search(r"(\d+) componenti, (\d+) rele' noti", txt)
    if not m or int(m.group(2)) != len(relays):
        refuse("2e: il numero di relè dichiarato non coincide con quelli elencati")
    out["relays"] = relays
    out["n_comp"] = int(m.group(1)) if m else None
    mi = re.search(r"interblocco: .*?(\d+) stati provati", txt)
    mg = re.search(r"interblocco del guadagno: (.*?); (\d+) coppie stato/posizione.*?(\d+) trasferimenti", txt)
    if not (mi and mg):
        refuse("2e: le righe dell'interblocco non si leggono nell'uscita")
    out["stati_trim"] = int(mi.group(1)) if mi else None
    out["guad"] = (mg.group(1), int(mg.group(2)), int(mg.group(3))) if mg else None
    out["net"] = rel(NET)

    # --- i falsi di L35 e L36: ogni variante ha il suo .txt, e tutte cadono come voluto
    fz = {}
    for lot, root in (("L35", L35), ("L36", L36)):
        d = src(root, "falsi")
        es = _csv(os.path.join(d, "esito.csv"))
        sab = [e for e in es if e["variante"] != "vera"]
        for e in es:
            if e["rc"] != e["rc_atteso"] or e["esito"] != "ok":
                refuse(f"{lot} falsi: {e['variante']} rc {e['rc']}, atteso {e['rc_atteso']}")
            if e["variante"] != "vera" and not os.path.isfile(os.path.join(d, e["variante"] + ".txt")):
                refuse(f"{lot} falsi: manca l'uscita {e['variante']}.txt")
        fz[lot] = {"n": len(sab), "vera": any(e["variante"] == "vera" for e in es), "dir": d}
    out["falsi"] = fz
    return out


# ------------------------------------------------------------ il calore ---
def measure_heat(op):
    """Il calore del telaio (L30, ADR-047): una stima CALCOLATA, non simulata."""
    d = src(L30, "termica")
    script = os.path.join(d, "stima_telaio.py")
    proc = subprocess.run([sys.executable, script], capture_output=True, text=True)
    with open(os.path.join(d, "stima_telaio.txt")) as f:
        saved = f.read()
    if proc.returncode != 0 or proc.stdout != saved:
        refuse("stima_telaio.py rieseguito non ridà stima_telaio.txt")
    P = re.findall(r"^(.+?)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)$", saved, re.M)
    P = [(k.strip(), float(a), float(b), float(c)) for k, a, b, c in P]
    tot = [p for p in P if p[0] == "TOTALE"]
    parts = [p for p in P if p[0] != "TOTALE"]
    if len(tot) != 1 or not all(abs(sum(p[i] for p in parts) - tot[0][i]) <= 0.02 for i in (1, 2, 3)):
        refuse("stima_telaio.txt: le voci non sommano al totale")
    V = re.findall(r"^(\S+(?: cm)?|all'aria)\s+(nominale|peggiore)\s+(\d+\.\d)\s+(\d+\.\d)\s+"
                   r"(\d+\.\d)\s+(\d+\.\d)$", saved, re.M)
    gm = re.search(r"gioco minimo del vano chiuso per 60 C nel caso peggiore: ([\d.]+) cm", saved)
    if not V or not gm:
        refuse("stima_telaio.txt: la tabella del vano non si legge")
    # la seconda strada: la scheda audio della stima contro i rail di tb_op di oggi
    audio = [p for p in parts if p[0].startswith("scheda audio")]
    p_blk = 15.0 * (abs(op["rails"].get("i(vpp)", 0)) + abs(op["rails"].get("i(vmm)", 0)))
    # stima_telaio.py scrive 7,94 da 15 V x (32,6 + 33,6) mA x 8, cioe' con le correnti a
    # tre cifre: lo scarto ammesso e' quell'arrotondamento, 8 x 15 V x 0,05 mA x 2 = 12 mW
    if len(audio) != 1 or not abs(8 * p_blk - audio[0][1]) <= 0.012:
        refuse(f"calore: la scheda audio della stima vale {audio[0][1] if audio else '?'} W, "
               f"8 x 15 V x i(rail) di tb_op di oggi da' {8 * p_blk:.4f} W")
    return {"dir": d, "parts": parts, "tot": tot[0] if tot else None,
            "vano": [(g, c, float(p), float(a), float(b), float(t)) for g, c, p, a, b, t in V],
            "gioco": float(gm.group(1)) if gm else None, "p_blk": p_blk}


# ================================================================ L42b ===
# L'alimentatore. Le cartelle dei lotti (L41a-L41c, L30) sono la prima strada;
# le ricorse di oggi (data/2026-09-27/L42b, L42b-L41c, L42b-L41b2) la seconda.
# Una ricorsa che non ridice il lotto fa rifiutare, e anche un deck rigenerato
# oggi da psu.net che non e' quello corso allora: vorrebbe dire che il circuito
# misurato non e' quello di oggi.

# ngspice esce 0 su tutto questo (limitations #29, #33, #35, #36): il log si
# legge prima dei dati
LOG_GUARD = re.compile(r"error|singular|no such|too many args|transient op|"
                       r"timestep too small|aborted", re.I)
# i percorsi assoluti di un deck (il worktree in cui e' stato scritto) non sono
# il circuito: si tolgono prima del confronto
_ROOTP = re.compile(r"/Users/\S*?/(?=(?:circuits|models|docs|firmware|spice)/)")


def log_pulito(path):
    """Un log di ngspice senza nessuna delle righe che invalidano una corsa."""
    bad = [ln.strip() for ln in open(path, errors="replace") if LOG_GUARD.search(ln)]
    if bad:
        refuse(f"{rel(path)}: il log ha {len(bad)} righe che invalidano la corsa, "
               f"la prima: {bad[0][:80]!r}")
    return not bad


def rows_of(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def stessi_byte(label, a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        if fa.read() != fb.read():
            refuse(f"{label}: {rel(a)} e {rel(b)} non sono uguali byte per byte")
            return False
    return True


def deck_norm(path, swap=()):
    """Le righe di un deck, coi percorsi assoluti ridotti a @/ e le cartelle
    delle ricorse riportate a quelle dei lotti."""
    with open(path) as f:
        text = f.read()
    for a, b in swap:
        text = text.replace(a, b)
    return _ROOTP.sub("@/", text)


def stesso_deck(label, a, b, swap=()):
    if deck_norm(a, swap) != deck_norm(b, swap):
        refuse(f"{label}: {rel(a)} non e' {rel(b)} (a meno dei percorsi del worktree): "
               "il circuito corso non e' quello di oggi")
        return False
    return True


def in_tmp(script, files, args, cwd_files=True):
    """Esegue uno script di un lotto su COPIE dei suoi file d'ingresso, in una
    cartella temporanea: alcuni scrivono accanto ai dati (analizza_timer.py,
    analizza_ldr.py), e il generatore non scrive mai nelle cartelle versionate.
    Ritorna (stdout, cartella)."""
    import tempfile
    d = tempfile.mkdtemp(prefix="l42b_")
    for f in files:
        shutil.copy(f, d)
    a = [x.replace("@TMP@", d) for x in args]
    proc = subprocess.run([sys.executable, script] + a, capture_output=True, text=True,
                          cwd=d if cwd_files else REPO)
    if proc.returncode not in (0, 1):
        refuse(f"{rel(script)} {' '.join(args)}: rc {proc.returncode} ({proc.stderr.strip()[-120:]})")
    return proc.stdout, d


def p9_soglie():
    """Le soglie di P9, lette dalla sua riga di REQUIREMENTS.md, non scritte qui."""
    with open(os.path.join(REPO, "docs", "preamp", "REQUIREMENTS.md")) as f:
        row = next((ln for ln in f if ln.startswith("| P9 |")), "")
    pats = {"entro_ms": r"rilascia `MUTE_CMD` entro (\d+) ms",
            "vrelay_ms": r"`VRELAY` resta in tolleranza per ≥ (\d+) ms",
            "margine_ms": r"≥ (\d+) ms di margine",
            "tetto_V": r"\*\*tetto di non-danno\*\* è ([\d,]+) V",
            "obiettivo_mV": r"\*\*obiettivo\*\* è ≤ (\d+) mV",
            "soglia_V": r"sotto \\\|(\d+,\d+) V\\\|"}
    out = {}
    for k, p in pats.items():
        m = re.search(p, row)
        if not m:
            refuse(f"REQUIREMENTS.md, riga di P9: non trovo {k} ({p})")
            out[k] = float("nan")
        else:
            out[k] = float(m.group(1).replace(",", "."))
    return out


def nc028_formula():
    """La catena di NC-028 (finale e diffusore), letta da NONCOMPLIANCE.md: la
    seconda strada dei dB SPL che le tabelle di L30 e L41c scrivono."""
    with open(os.path.join(REPO, "docs", "preamp", "NONCOMPLIANCE.md")) as f:
        m = re.search(r"(\d+) \+ 20·log\((\d+,\d+)·ΔV / (\d+,\d+)\) dB SPL", f.read())
    if not m:
        refuse("NONCOMPLIANCE.md: la formula di NC-028 non si legge")
        return None
    spl, g, v = (float(x.replace(",", ".")) for x in m.groups())
    return {"spl": spl, "g": g, "v1w": v, "db": lambda dv: spl + 20 * math.log10(g * dv / v)}


# ---- potenza, VRELAY, sorvegliante sul lato alimentatore (L41a, ricorsa L42b)
# le colonne di analisi.csv di L41a; la ricorsa ne ha tre in piu' (vrelay_reg e
# la tenuta a J1). Tolleranze della ricorsa col carico di L41a contro L41a:
# 0,5 ms o l'1 % sui tempi, 10 mV sulle tensioni (i regolatori di oggi hanno la
# corrente di riposo per parte, L41b1; L41a caricava 1 mA a tutti).
T_COLS = ("t_off_ms", "t_md_ms", "t_p135_ms", "t_p106_ms", "t_m135_ms", "t_m106_ms",
          "trip_after_135_ms", "vr_hold_ms", "vr80_hold_ms")
V_COLS = ("vplus", "vminus", "vrelay", "v5", "raw_p_min", "raw_m_min_abs", "raw_v_min",
          "vplus_at_off", "vminus_at_off")


def _cella(r, k):
    s = (r.get(k) or "").strip()
    if not s:
        return None
    return (">", float(s[1:])) if s.startswith(">") else ("=", float(s))


def _uguali(k, a, b):
    if a is None or b is None:
        return a is None and b is None
    if a[0] != b[0]:
        return False
    # le tensioni lette ALL'ISTANTE dello scatto ereditano la tolleranza del
    # tempo: il rail scende di 265 mA / 1760 uF ~ 0,15 V/ms, e 0,3 ms sono 50 mV
    tol = (max(0.5, 0.01 * abs(b[1])) if k in T_COLS else
           0.050 if k.endswith("_at_off") else 0.010)
    return abs(a[1] - b[1]) <= tol


def _psu_log(path, r512):
    """I casi di un deck rete / guasti, e R512 com'era in ciascuno: la guardia
    di limitations #34 (ogni caso rimette R512 prima delle sue alterazioni)."""
    casi, cur = [], None
    for ln in open(path, errors="replace"):
        m = re.match(r"@rr512\[resistance\] = (\S+)", ln.strip())
        if m:
            cur = float(m.group(1))
        m = re.match(r"CASO (\S+)", ln.strip())
        if m:
            casi.append((m.group(1), cur))
            cur = None
    for nome, r in casi:
        want = 1e15 if "senza_rivelatore" in nome else r512
        if r is None or abs(r - want) > 1e-6 * want:
            refuse(f"{rel(path)}: nel caso {nome} R512 vale {r}, atteso {want:g} (#34)")
    return [c for c, _ in casi]


def measure_psu_power():
    d = src(L42B)
    net = open(PSU_NET).read()
    m = re.search(r'\(ref "R512"\)\s*\(value "([\d.]+)k"\)', net)
    r512 = float(m.group(1)) * 1e3 if m else float("nan")
    gen = tool(L42B, "deck", "genera_tb_psu.py")
    out = {}
    for tag, sub, extra in (("oggi", "", ()), ("carico", "carico_l41a", ("--carico", "l41a"))):
        rows = {}
        for nome in ("rete", "guasti"):
            dd = os.path.join(d, sub, nome)
            deck = os.path.join(dd, f"tb_psu_{nome}{'_carico_l41a' if sub else ''}.cir")
            log = deck[:-4] + ".log"
            log_pulito(log)
            casi = _psu_log(log, r512)
            # il deck si rigenera oggi da psu.net e dev'essere quello corso
            _, tmp = in_tmp(gen, [], ["--nome", nome, "--cima", "12e-3", *extra,
                                      "--uscita", "@TMP@"], cwd_files=False)
            stesso_deck(f"deck {nome} {tag}", os.path.join(tmp, os.path.basename(deck)), deck,
                        swap=((tmp, dd),))
            rr = rows_of(src(dd, "analisi.csv"))
            if sorted(r["file"] for r in rr) != sorted(casi):
                refuse(f"{rel(dd)}/analisi.csv: casi {sorted(r['file'] for r in rr)}, il log {sorted(casi)}")
            rows.update({r["file"]: r for r in rr})
        out[tag] = rows
    # la seconda strada: L41a (sul psu.py di L41a). Il banco di oggi col carico di
    # L41a deve ridarla su ogni colonna; allora ogni scarto di oggi e' il carico.
    old = {}
    for nome in ("rete", "guasti"):
        old.update({r["file"]: r for r in rows_of(vecchio(L41A, nome, "analisi.csv"))})
    if sorted(old) != sorted(out["carico"]):
        refuse(f"L41a e la ricorsa col carico di L41a non hanno gli stessi casi")
    for caso, ro in old.items():
        rc = out["carico"].get(caso, {})
        for k in T_COLS + V_COLS:
            kc = "vrelay_reg" if k == "vrelay" else k   # il VRELAY di L41a e' VRELAY_REG
            if not _uguali(k, _cella(rc, kc), _cella(ro, k)):
                refuse(f"carico di L41a, {caso}, {k}: oggi {rc.get(kc)!r}, L41a {ro.get(k)!r}")
    scarti = []
    for caso, ro in old.items():
        rt = out["oggi"].get(caso, {})
        for k in T_COLS + V_COLS:
            kt = "vrelay_reg" if k == "vrelay" else k
            if not _uguali(k, _cella(rt, kt), _cella(ro, k)):
                scarti.append((caso, k, ro.get(k), rt.get(kt), out["carico"][caso].get(kt)))
    # il raddrizzatore (le scelte portate all'utente prima di ADR-048), rieseguito
    rad = src(L41A, "scelte", "raddrizzatore.csv")
    stessi_byte("raddrizzatore", src(L42B, "scelte", "raddrizzatore.csv"), rad)
    rad_rows = [r for r in rows_of(rad) if r["vn_ac"] == "15" and r["va"] == "50"]
    if len(rad_rows) != 6:
        refuse(f"raddrizzatore.csv: righe per 2x15 V 50 VA {len(rad_rows)}, attese 6")
    return {"dir": d, "oggi": out["oggi"], "carico": out["carico"], "old": old,
            "scarti": scarti, "rad": rad_rows}


def prov_psu(deck, datadir, note=""):
    """La provenienza di un deck dell'alimentatore: i file inclusi (dagli
    `.include`) e i sottocircuiti comportamentali che il deck definisce. Non
    ci sono modelli del costruttore: i regolatori, i comparatori, il micro, il
    DAC e gli op-amp sono comportamentali, dichiarati nell'intestazione del
    generatore (L41a, L41b1)."""
    incs, subs = [], []
    for ln in open(deck):
        m = re.match(r"^\.include\s+(\S+)", ln.strip(), re.I)
        if m:
            r = _resolve_include(m.group(1))
            if r is None or not os.path.exists(os.path.join(REPO, r)):
                refuse(f"provenienza {rel(deck)}: include non risolvibile {m.group(1)}")
                continue
            incs.append(r)
        m = re.match(r"^\.subckt\s+(\S+)", ln.strip(), re.I)
        if m:
            subs.append(m.group(1))
    if not incs or not subs:
        refuse(f"provenienza {rel(deck)}: include {incs}, sottocircuiti {subs}")
    return (f'<p class="prov">Deck <code>{html_escape(rel(deck))}</code>'
            f' &middot; dati <code>{html_escape(rel(datadir))}/</code>{note}<br>'
            f'Inclusi: {", ".join(f"<code>{i}</code>" for i in incs)} (generici, dichiarati)'
            f' &middot; comportamentali: <strong>{", ".join(subs)}</strong> &middot; '
            'nessun modello del costruttore: regolatori, comparatori, micro, DAC e op-amp '
            'sono modelli dichiarati</p>')


def vecchio(root, *parts):
    """I dati di L41a sul psu.py di L41a: SOLO come seconda strada. Non passano da
    src(), che li rifiuta come prima strada (FORBIDDEN)."""
    p = os.path.join(root, *parts)
    if not os.path.isfile(p):
        raise SystemExit(f"RIFIUTATO: manca {rel(p)}. Nessun file e' stato scritto.")
    return p


# ---- le sequenze sul circuito (L41b2, L41c): analizza_seq.txt -----------
def parse_seq(path):
    """{caso: {"crit": {nome: (ok, testo)}, "fatti": {k: v}}, "_verdetto": ...}."""
    out, cur = {}, None
    verd = None
    for ln in open(path):
        m = re.match(r"^== (\S+)", ln)
        if m:
            cur = out.setdefault(m.group(1), {"crit": {}, "fatti": {}})
            continue
        m = re.match(r"^   (\S+)\s+(ok|NO|info)\s+(.*)$", ln.rstrip("\n"))
        if m and cur is not None:
            cur["crit"][m.group(1)] = (m.group(2), m.group(3).strip())
            continue
        m = re.match(r"^   \. (\S+): (.*)$", ln.rstrip("\n"))
        if m and cur is not None:
            cur["fatti"][m.group(1)] = m.group(2).strip()
            continue
        m = re.match(r"^VERDETTO: (\S+)", ln)
        if m:
            verd = m.group(1)
    out["_verdetto"] = verd
    return out


def ms_in(text, pat):
    m = re.search(pat, text or "")
    return float(m.group(1)) if m else None


def seq_ricorsa(label, orig_dir, rerun_dir, casi, swap):
    """La ricorsa di una catena di sequenze: lo stesso verdetto, e per ogni caso
    lo stesso giro al punto fisso, lo stesso deck (da psu.net di oggi) e le
    stesse uscite del core."""
    stessi_byte(f"{label}: analisi_seq.txt", os.path.join(rerun_dir, "analisi_seq.txt"),
                os.path.join(orig_dir, "analisi_seq.txt"))
    for c in casi:
        pf = [open(os.path.join(x, c, "punto_fisso.txt")).read().strip() for x in (orig_dir, rerun_dir)]
        if pf[0] != pf[1]:
            refuse(f"{label}, {c}: punto fisso al giro {pf[0]} allora, {pf[1]} oggi")
            continue
        g = pf[0]
        stesso_deck(f"{label}, {c}", os.path.join(rerun_dir, c, f"tb_psu_seq_{c}_g{g}.cir"),
                    os.path.join(orig_dir, c, f"tb_psu_seq_{c}_g{g}.cir"), swap)
        stessi_byte(f"{label}, {c}: core_g{g}.csv", os.path.join(rerun_dir, c, f"core_g{g}.csv"),
                    os.path.join(orig_dir, c, f"core_g{g}.csv"))


L41C_CASI = ("spegnimento_l", "perdita", "perdita_min", "guasto", "guasto_u501", "guasto_u503",
             "guasto_u503_min", "cf_nodelta", "corto_u503")
L41B2_CASI = ("accensione", "rilascio", "inversione", "spegnimento", "buco20", "buco200", "guasto")


def measure_supervisor():
    """Il sorvegliante e i guasti sul circuito vero (L41c), lato alimentatore."""
    d = src(L41C, "seq")
    s = parse_seq(os.path.join(d, "analisi_seq.txt"))
    if s.get("_verdetto") != "PASSA" or sorted(k for k in s if k != "_verdetto") != sorted(L41C_CASI):
        refuse(f"L41c analisi_seq.txt: verdetto {s.get('_verdetto')}, casi {sorted(s)}")
    rr = src(L42B_C, "seq")
    seq_ricorsa("L41c", d, rr, L41C_CASI,
                ((os.path.join("2026-09-27", "L42b-L41c"), os.path.join("2026-09-26", "L41c")),))
    for j in L41C_CASI:
        stessi_byte(f"L41c ponte {j}", src(L42B_C, "ponte", j + ".json"), src(L41C, "ponte", j + ".json"))
    righe = []
    for c in L41C_CASI:
        cr = s.get(c, {}).get("crit", {})
        get = lambda k: cr.get(k, (None, ""))[1]
        # i casi che DEVONO fallire (il controfattuale) portano l'asterisco
        c3 = cr.get("C3") or cr.get("C3*") or (None, "")
        rr_ = cr.get("r") or cr.get("r*") or (None, "")
        righe.append({
            "caso": c, "ok": all(v[0] in ("ok", "info") for v in cr.values()),
            "info": all(v[0] == "info" for v in cr.values()),
            "n_crit": len(cr),
            "m": ms_in(get("m"), r"rilasciato ([\d.]+) ms"),
            "delta": ms_in(c3[1], r"Delta ai rilasci: ([\d.]+) ms"),
            "deve_fallire": "C3*" in cr,
            "jack": ms_in(rr_[1], r"jack \(tardi\) a \+([\d.]+) ms"),
            "guad": ms_in(rr_[1], r"guadagno \(presto\) a \+([\d.]+) ms"),
            "v106": ms_in(get("s"), r"V\+ sotto 10,6 V a \+([\d.]+) ms"),
            "k501": ms_in(get("p"), r"K501 aperto ([\d.]+) ms dopo MUTE_REQ") or
                    ms_in(get("j"), r"K501 aperto ([\d.]+) ms dopo il rilascio di PERMIT_CMD"),
            "i_s": ms_in(get("i"), r"rilasciato ([\d.]+) s dopo FRONT_IN"),
            "finale": (re.search(r"stato finale (?:del core: )?(\w+)", get("q") or get("l")) or [None, None])[1],
        })
    return {"dir": d, "rows": righe}


def measure_timer():
    """Δ e lo standby (L41b1): il testo del lotto, lo script rieseguito sui suoi
    log e sui log corsi oggi dai deck rigenerati da psu.net di oggi."""
    d = src(L41B1, "timer")
    saved = open(os.path.join(d, "analisi_timer.txt")).read()
    an = tool(L41B1, "deck", "analizza_timer.py")
    logs = [os.path.join(d, f"tb_psu_timer_{a}.log") for a in ("nom", "min")]
    for lg in logs:
        log_pulito_timer(lg)
    out1, _ = in_tmp(an, logs, [os.path.basename(x) for x in logs])
    if out1 != saved:
        refuse("analizza_timer.py rieseguito sui log di L41b1 non ridà analisi_timer.txt")
    oggi = [src(L42B, "timer", f"tb_psu_timer_{a}.log") for a in ("nom", "min")]
    out2, _ = in_tmp(an, oggi, [os.path.basename(x) for x in oggi])
    if out2 != saved:
        refuse("i deck del temporizzatore corsi oggi non ridanno analisi_timer.txt di L41b1")
    gen = tool(L41B1, "deck", "genera_tb_psu.py")
    for a, extra in (("nom", ()), ("min", ("--angolo", "min", "--v5", "4.9"))):
        _, tmp = in_tmp(gen, [], ["--uscita", "@TMP@", "--nome", "timer", *extra], cwd_files=False)
        stesso_deck(f"deck del temporizzatore {a}", os.path.join(tmp, f"tb_psu_timer_{a}.cir"),
                    os.path.join(d, f"tb_psu_timer_{a}.cir"))
    res = {}
    blk = None
    for ln in saved.splitlines():
        m = re.match(r"^== tb_psu_timer_(\w+)\.log", ln)
        if m:
            blk = res.setdefault(m.group(1), {})
            continue
        m = re.match(r"^   (\S+)\s+(.*)$", ln)
        if m and blk is not None and not ln.startswith("      "):
            blk[m.group(1)] = m.group(2)
    if sorted(res) != ["min", "nom"] or saved.count(": PASSA") != 2:
        refuse(f"analisi_timer.txt: blocchi {sorted(res)}, verdetti PASSA {saved.count(': PASSA')}")
    t = {}
    for a in ("nom", "min"):
        r = res.get(a, {})
        t[a] = {k: {"d": ms_in(r.get(k), r"D = ([\d.]+) ms"),
                    "vr": ms_in(r.get(k), r"VRELAY < 9,6 V ([\d.]+) ms"),
                    "mute": ms_in(r.get(k), r"MUTE_CMD a \+([\d.]+) ms")}
                for k in ("micro_reset", "micro_a_zero", "perdita_rete_micro_reset",
                          "guasto_U503_micro_reset", "controfattuale_senza_C528")}
        t[a]["fermo_alto"] = ms_in(r.get("perdita_rete_micro_fermo_alto"), r"MUTE_CMD a \+([\d.]+) ms")
        t[a]["fermo_alto_mai"] = "PERMIT_CMD mai" in (r.get("perdita_rete_micro_fermo_alto") or "")
        t[a]["drain"] = ms_in(r.get("solo_permit_req_giu"), r"di MUTE_CMD max ([\d.]+) V")
        t[a]["anticipo"] = ms_in(r.get("rilascio_solo_mute_req"), r"anticipo ([\d.]+) ms")
        t[a]["standby_j1"] = ms_in(r.get("standby"), r"VRELAY a J1 max (-?[\d.]+) V")
        t[a]["standby_mw"] = ms_in(r.get("standby"), r"potenza da T2 ([\d.]+) mW")
    # la soglia di Δ (ADR-045: >= 10 ms garantiti) e' quella che lo script usa
    dmin = ms_in(saved, r"fallisce come deve \(D < ([\d.]+) ms\)")
    if dmin is None:
        refuse("analisi_timer.txt: la soglia di Δ del controfattuale non si legge")
    return {"dir": d, "t": t, "dmin": dmin if dmin is not None else float("nan")}


def log_pulito_timer(path):
    """La guardia di analizza_timer.py: le `meas` che non trovano l'evento
    scrivono «Error» e sono misure, lette come tali; il resto rifiuta."""
    for ln in open(path, errors="replace"):
        if LOG_GUARD.search(ln) and not re.search(r"meas|out of interval|not found|failed",
                                                  ln, re.I):
            refuse(f"{rel(path)}: {ln.strip()[:80]!r}")
            return


def measure_fw():
    """Il firmware sul circuito (L41b2): le sette sequenze e i falsi."""
    d = src(L41B2, "seq")
    s = parse_seq(os.path.join(d, "analisi_seq.txt"))
    if s.get("_verdetto") != "PASSA" or sorted(k for k in s if k != "_verdetto") != sorted(L41B2_CASI):
        refuse(f"L41b2 analisi_seq.txt: verdetto {s.get('_verdetto')}, casi {sorted(s)}")
    seq_ricorsa("L41b2", d, src(L42B_B2, "seq"), L41B2_CASI,
                ((os.path.join("2026-09-27", "L42b-L41b2"), os.path.join("2026-09-26", "L41b2")),))
    rows = []
    for c in L41B2_CASI:
        cr = s.get(c, {}).get("crit", {})
        f = s.get(c, {}).get("fatti", {})
        pf = ms_in(cr.get("F", (0, ""))[1], r"punto fisso al giro (\d+)")
        rows.append({"caso": c, "n": len(cr), "ok": sum(v[0] == "ok" for v in cr.values()),
                     "giro": pf, "stati": f.get("stati", ""), "crit": cr})
    # i falsi sull'host (L41b2) e la loro ricorsa di oggi (L42b/falsi)
    es = src(L41B2, "falsi", "esito.txt")
    stessi_byte("falsi sull'host", src(L42B, "falsi", "esito.txt"), es)
    txt = open(es).read()
    fall = re.findall(r"^falso (\d+) .*: FALLISCE .* come deve", txt, re.M)
    tot = re.search(r"^== falsi: (\d+) su (\d+) fanno fallire il loro test", txt, re.M)
    if not tot or int(tot.group(1)) != len(fall) or int(tot.group(2)) != len(fall):
        refuse(f"esito.txt dei falsi: {len(fall)} righe che falliscono, sintesi "
               f"{tot.group(0) if tot else 'assente'}")
    # due falsi fatti fallire anche sul circuito: sul criterio giusto
    circ = {}
    for n, caso, crit in (("6", "guasto", "n"), ("9", "spegnimento", "j")):
        p = src(L41B2, "falsi", f"seq_falso{n}_{caso}.txt")
        sf = parse_seq(p)
        no = [k for k, v in sf.get(caso, {}).get("crit", {}).items() if v[0] == "NO"]
        if sf.get("_verdetto") != "FALLISCE" or no != [crit]:
            refuse(f"{rel(p)}: verdetto {sf.get('_verdetto')}, criteri caduti {no}, atteso [{crit}]")
        circ[n] = (caso, no, sf.get(caso, {}).get("crit", {}).get(crit, (None, ""))[1])
    return {"dir": d, "rows": rows, "falsi": len(fall), "circ": circ}


LDR_FILES = ("tb_psu_ldr_cima12mA", "tb_psu_ldr_ledmax_v5_4.9_cima12mA",
             "tb_psu_ldr_cal_cima12mA", "tb_psu_ldr_cal_ledmax_v5_4.9_cima12mA")


def measure_ldr_drive():
    """Il pilota delle LDR con la cima a 12 mA (ADR-050), dai CSV di L41b2."""
    d = src(L41B2, "ldr")
    an = tool(L41B2, "deck", "analizza_ldr.py")
    data = {}
    for f in LDR_FILES:
        log = os.path.join(d, f + ".log")
        out, tmp = in_tmp(an, [log], [os.path.basename(log)])
        stessi_byte(f"analizza_ldr.py rieseguito su {f}", os.path.join(tmp, f + ".log.csv"),
                    log + ".csv")
        if "VERDETTO" not in out or "PASSA" not in out.split("VERDETTO", 1)[1]:
            refuse(f"analizza_ldr.py su {f}: il verdetto non e' PASSA")
        stessi_byte(f"LDR corse oggi, {f}", src(L42B, "ldr", f + ".log.csv"), log + ".csv")
        data[f] = rows_of(log + ".csv")
    for c in ("cal_cima12mA.json", "cal_ledmax_v5_4.9_cima12mA.json"):
        stessi_byte(f"calibrazione {c}", src(L42B, "ldr", c), os.path.join(d, c))
    cal = [r for r in data["tb_psu_ldr_cal_cima12mA"] if r["modo"] == "cal"]
    calx = [r for r in data["tb_psu_ldr_cal_ledmax_v5_4.9_cima12mA"] if r["modo"] == "cal"]
    comp = [r for r in data["tb_psu_ldr_cal_cima12mA"] if r["modo"] == "comp"]
    noc = [r for r in data["tb_psu_ldr_cal_cima12mA"] if r["modo"] == "nocomp"]
    rst = [r for r in data["tb_psu_ldr_cal_cima12mA"] if r["modo"] == "dac_reset"]
    tops = {float(r["target"]) for r in cal if r["nome"] in ("d0", "d1")}
    if len(tops) != 1:
        refuse(f"LDR: la cima non e' una sola: {sorted(tops)}")
    # la seconda strada dell'errore: ricalcolato dalle correnti, non letto
    for r in cal + calx + comp + noc:
        e = 20 * math.log10(float(r["i_meas"]) / float(r["target"]))
        if abs(e - float(r["err_db"])) > 1e-6:
            refuse(f"LDR {r['modo']} {r['s']} {r['nome']} {r['t']} C: err_db {r['err_db']}, "
                   f"dalle correnti {e:.6f}")
    worst = lambda rr, riposo: max((abs(float(r["err_db"])), r) for r in rr
                                   if (r["nome"] == "riposo") == riposo)
    rst_i = [float(r["i(vls)"]) for r in rst] + [float(r["i(vlp)"]) for r in rst]
    return {"dir": d, "cima": tops.pop() if tops else None, "cal": cal, "calx": calx,
            "comp": comp, "noc": noc,
            "w_cal": worst(cal, False), "w_calx": worst(calx, False),
            "w_cal_rip": worst(cal, True), "w_comp": worst(comp, False),
            "w_noc": max((abs(float(r["err_db"])), r) for r in noc),
            "reset": (min(rst_i), max(rst_i)) if rst_i else (None, None)}


def measure_shutdown():
    """Spegnimento e failsafe al jack: L41c (il circuito vero) e L30 (le PWL)."""
    f = nc028_formula()
    out = {}
    for tag, root, tab, rerun, extra in (
            ("l41c", L41C, os.path.join("script", "tabella.py"), L42B_C,
             ("cf_nodelta_fino_all_aborto.txt",)),
            ("l30", L30, os.path.join("script", "tabella.py"), os.path.join(L42B, "l30"), ())):
        d = src(root)
        t = os.path.join(d, "tabella.csv")
        ins = [os.path.join(d, "corse", "analisi.csv"), os.path.join(d, "corse", "fallite.txt")] + \
              [os.path.join(d, x) for x in extra]
        _, tmp = in_tmp(tool(root, tab), ins,
                        [os.path.basename(ins[0]), os.path.basename(ins[1]), "tabella.csv"]
                        + [os.path.basename(x) for x in ins[2:]])
        stessi_byte(f"{tag}: tabella.py rieseguito", os.path.join(tmp, "tabella.csv"), t)
        # la ricorsa di oggi: le stesse corse, la stessa analisi, la stessa tabella
        stessi_byte(f"{tag}: analisi.csv corso oggi", src(rerun, "corse", "analisi.csv"), ins[0])
        stessi_byte(f"{tag}: tabella corsa oggi", src(rerun, "tabella.csv"), t)
        rows = rows_of(t)
        for r in rows:
            v, db = r.get("picco_V", "-"), r.get("dB_SPL_picco_1m", "-")
            if v in ("-", "") or f is None:
                continue
            if abs(f["db"](float(v)) - float(db)) > 0.05:
                refuse(f"{tag} {r.get('caso') or r.get('corsa')}: {db} dB SPL in tabella, "
                       f"la formula di NC-028 da' {f['db'](float(v)):.2f}")
        out[tag] = rows
    # i deck della scheda audio: rigenerati oggi e uguali a quelli corsi
    stessi_byte("il deck di L30 rigenerato oggi", src(L42B, "l30", "tb_v2_l30.cir"),
                src(L30, "deck", "tb_v2_l30.cir"))
    stessi_byte("il deck di L41c rigenerato oggi", src(L42B_C, "deck", "tb_v2_l41c.cir"),
                src(L41C, "deck", "tb_v2_l41c.cir"))
    return {"rows": out, "f": f}


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
    return sp.document(W, H, body, "Dati: L42 tb_ac_*.csv · linea verticale = 20 kHz")


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
    return sp.document(W, H, body, "Dati: L42 tb_loop_margini.csv · il verdetto è il "
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
    return sp.document(W, H, body, "Dati: L42 tb_loop_att2k5_*.csv · margine = |fase| "
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
    return sp.document(W, H, body, "Dati: L42 tb_zout_psrr_noise_psrr*.csv · 1 V AC in "
                       "serie a ciascun rail, ingresso silenziato")


def fig_zout(z):
    W, H = 900, 450
    # L37: da 0,01 Ω, perche' il nodo OUT a sorgente spenta sta a ~0,04 Ω (NC-033)
    ax = sp.Axes(72, 46, W - 130, H - 160, (20, 200000), (0.01, 5000), ylog=True,
                 xlabel="frequenza [Hz]", ylabel="|Z| [Ω]",
                 title="Impedenza d'uscita: al jack e al nodo OUT")
    for m in MODES:
        ax.line(z[m]["f"], z[m]["z"], mcol(m), f"al jack · {MLAB[m]}", None)
        ax.line(z[m]["f"], z[m]["za"], mcol(m, True), f"al nodo OUT · {MLAB[m]}", "5,3")
    ax.hline(100, sp.C_REQ, "E4: < 100 Ω")
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L42 tb_zout_psrr_noise_zout_*.csv, sorgente spenta · "
                       "la salita sotto 200 Hz è la reattanza del 4,7 µF, non lo stadio")


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
    return sp.document(W, H, body, "Dati: L42 tb_dc_headroom*.csv · spazzata in continua; "
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
    return sp.document(W, H, ax.render(), "Dati: L42 tb_switch_v2_counterfactual*.csv · "
                       "con R_f aperto l'anello è rotto e l'uscita si appoggia al rail")


def fig_mute(mu):
    """Il profilo v4 visto al jack: il livello del tono nel tempo, inserzione e
    rilascio del mute graduale, con le finestre in cui S e' misurata."""
    p = mu["prof"]
    W, H = 900, 440
    # 0,3 s: prima il fit vede l'avvio della corsa (analizza parte da li'). Sotto
    # -120 dB c'e' il jack a massa dal relè: si taglia, e si scrive il minimo vero.
    YMIN, TMAX = -120.0, 16.0
    sel = [(t, x) for t, x in zip(p["t"], p["lv"]) if 0.3 <= t <= TMAX]
    ax = sp.Axes(72, 46, W - 130, H - 150, (0, TMAX), (YMIN, 0), xlog=False,
                 xlabel="tempo [s]", ylabel="livello al jack [dB sotto il pieno]",
                 title="Il mute graduale a LDR, profilo v4: il livello della musica al jack")
    ax.line([t for t, _ in sel], [max(x, YMIN) for _, x in sel], sp.C_0DB,
            f"{p['f']} Hz · +10 dB · jack principale · cella {p['cella']}", None)
    ax.hline(S_PAV, sp.C_REQ, "pavimento di S, −70 dB", left=True)
    for te, lab in ((p["t_ins"], "comando di mute"), (p["t_rel"], "rilascio")):
        ax.vline(te)
        ax.annot(te, 0, lab, 6, 14)
    tm, xm = min(sel, key=lambda a: a[1])
    if xm < YMIN:
        ax.annot(tm, YMIN, f"relè a massa: fino a {fx(xm, 0)} dB".replace("&minus;", "−"), 8, -8)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 56, cols=1, colw=600)
    return sp.document(W, H, body, "Dati: L42 mute/profilo.csv · il livello è il fit del tono "
                       "su 10 ms di v2_metodo.py; S è il salto massimo in 100 ms")


# L42b: una tinta per temperatura del telaio, dal freddo al caldo
T_COL = {15: "#1f5c99", 25: "#2e7d4f", 35: "#8a7a1a", 45: "#c0662a", 60: "#a8452a"}


def fig_ldr_drive(ld):
    """L'errore del pilota delle LDR contro la tabella v4, la stringa in serie:
    compensato col sensore del micro (tratteggio) e calibrato (pieno)."""
    W, H = 900, 460
    ax = sp.Axes(72, 46, W - 130, H - 170, (5e-9, 3e-2), (-3.0, 1.5),
                 xlabel="corrente chiesta dalla tabella v4 [A]",
                 ylabel="errore [dB] contro la tabella",
                 title=f"Il pilota delle LDR, cima a {it(ld['cima'] * 1000, 3)} mA (ADR-050): "
                       "stringa in serie, 15–60 °C")
    for modo, dash, lab in (("comp", "5,3", "compensato"), ("cal", None, "calibrato")):
        for t in sorted(T_COL):
            pts = sorted((float(r["target"]), float(r["err_db"])) for r in ld[modo]
                         if r["s"] == "S" and int(r["t"]) == t)
            ax.line([x for x, _ in pts], [y for _, y in pts], T_COL[t],
                    f"{lab} · {t} °C", dash)
    ax.hline(1.0, sp.C_REQ, "±1 dB, il criterio (L41b1)")
    ax.hline(-1.0, sp.C_REQ, None)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 56, cols=5, colw=160)
    return sp.document(W, H, body, "Dati: L41b2 ldr/tb_psu_ldr_cal_cima12mA.log.csv · ricorso "
                       "il 2026-09-27 in L42b/ldr, uguale byte per byte")


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
            ("s11", "I relè di guadagno: V2"), ("smute", "Il mute: LDR e relè al jack, V2"),
            ("sint", "Il guadagno interbloccato e i comandi"),
            ("s12", "Sovraccarico e corto: V3, P7"), ("sheat", "Il calore del telaio"),
            ("spsu", "L&rsquo;alimentatore: schema e decisioni"),
            ("spow", "Potenza, rail e VRELAY"),
            ("ssup", "Il sorvegliante e i guasti, sul circuito"),
            ("stim", "Il temporizzatore: Δ in hardware e lo standby"),
            ("sfw", "Il firmware sul circuito"),
            ("sldr", "Il pilota delle LDR"),
            ("soff", "Spegnimento e failsafe al jack"),
            ("s13", "Requisiti a fronte del misurato"), ("s14", "Cosa questo dossier non dice"),
            ("s15", "Provenienza"))


def build_page(M, inline=False):
    resp, v1, z, psrr, hr, cf = M["resp"], M["v1"], M["z"], M["psrr"], M["hr"], M["cf"]
    trim, noise, v2, v3, p7, op = M["trim"], M["noise"], M["v2"], M["v3"], M["p7"], M["op"]
    e4 = M["e4"]
    e4_main = max(g["zrmax_max"] for g in e4["groups"] if g["out"] == "main")
    e4_fix = max(g["zrmax_max"] for g in e4["groups"] if g["out"] != "main")
    e4_disp = max(g["disp"] for g in e4["groups"])
    e4_ok = all(g["zrmax_max"] < E4_MAX and g["disp"] < E4_COSTANZA for g in e4["groups"])

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
    mu, il, heat, ldr, l40 = M["mute"], M["il"], M["heat"], M["ldr"], M["l40"]
    A('<div class="wrap">')
    A('<p class="eyebrow">Scheda audio &middot; deck veloci corsi il 2026-09-27 (L42a) sul '
      'circuito di L28 &middot; mute da L29d2, L29e e L41b2 &middot; interblocco da L35 e L36 '
      '&middot; calore da L30 &middot; alimentatore da L41a–L41c e L30, ricorso il 2026-09-27 '
      '(L42b)</p>')
    A('<h1>Dossier di misura del preamplificatore di linea</h1>')
    A('<p class="lede">Classe A pura a componenti discreti, senza operazionali nel '
      'percorso del segnale. Guadagno 0 / +3 / +10 dB, trim 0 / &minus;6 / &minus;12 dB '
      'sull&rsquo;uscita variabile, mute graduale a LDR a monte e relè al jack. Le due schede: '
      'la scheda audio, poi l&rsquo;alimentatore, coi rail lineari, il sorvegliante in hardware '
      'e il temporizzatore che ordina mute, guadagno e rete.</p>')

    shape, level = adr014(resp)
    worst_shape = max(shape.values(), key=abs)
    weak_psrr = min(r["p10k"] for r in psrr.values())
    nc9 = hr["modes"]["10db"]["trim"]["6"]["M1"]
    gains = " · ".join(sg(resp[(m, "1.5")]["g1k"]) if m != "0db"
                       else fx(resp[(m, "1.5")]["g1k"]) for m in MODES)
    off_db = [M["off"]["f"]["db"](float(r["picco_V"])) for r in M["off"]["rows"]["l41c"]
              if r["criterio"].startswith("<= 0.002")]
    A('<dl class="synopsis">')
    for lab, val, unit in (
            ("Guadagni a 1 kHz", gains, "dB &middot; 0 / +3 / +10 &middot; sorgente 1,5 Ω"),
            ("V1, margine minimo", f"{fx(v1['min'])}°",
             f"soglia 60° &middot; guardia {fx(v1['min'] - PM_MIN)}° &middot; {v1['min_where']}"),
            ("Headroom, NC-009", f"{sg(nc9)} dB",
             "metrica M1 &middot; +10 dB col trim a &minus;6 dB"),
            ("E3, min |Z<sub>in</sub>|", f"{fx(min(trim['e3min'], ldr['e3min']) / 1000, 1)} kΩ",
             "ogni posizione del trim, LDR del mute comprese"),
            ("E5, catena peggiore", f"{fx(max(trim['e5max'], ldr['e5max']))} µV",
             "LDR comprese &middot; 1/f solo sulla coppia d&rsquo;ingresso"),
            ("V2, mute", f"{mu['n'] - mu['n_fuori']} su {mu['n']}",
             "verdetti che reggono &middot; geometria iii (ADR-044)"),
            ("Scarto ADR-014", it_sci(worst_shape),
             "dB a 20 kHz rif. 1 kHz &middot; peggiore dei 3 modi"),
            ("PSRR, peggiore", f"{fx(weak_psrr)} dB", "a 10 kHz"),
            ("E4, Re(Z<sub>out</sub>) max", f"{fx(max(e4_main, e4_fix))} Ω",
             "al jack &middot; 20 Hz–20 kHz &middot; 3 uscite, costante col volume"),
            ("Δ, angolo minimo", f"{fx(M['tm']['t']['min']['micro_reset']['d'])} ms",
             f"col micro in reset &middot; soglia {fx(M['tm']['dmin'], 0)} ms (ADR-045)"),
            ("Guasto dell&rsquo;alimentatore, al jack",
             f"{fx(max(off_db), 1)} dB SPL" if off_db else "&mdash;",
             "il peggiore sul circuito vero (L41c) &middot; di picco a 1 m")):
        A(f'<div><dt>{lab}</dt><dd>{val}<span class="u">{unit}</span></dd></div>')
    A('</dl>')

    kf_parts = sorted({m["part"] for m in allm if m["kf"] != 0})
    A('<div class="note"><strong>Leggere prima questo.</strong> '
      + (f'Dei {len(vendors) + len(placeholders)} dispositivi attivi che questi deck '
         f'simulano, <strong>{len(vendors)} usano il modello del costruttore</strong> '
         f'({", ".join(vendors)})'
         + (f' e {len(placeholders)} sono segnaposto scritti a mano ({", ".join(placeholders)})'
            if placeholders else ', nessuno è un segnaposto') + '. ')
      + ('<strong>Nessun modello simulato ha rumore 1/f</strong>: ogni cifra di rumore è un '
         'pavimento termico e shot (NC-004). ' if all_kf0 else
         f'<strong>Solo {", ".join(kf_parts)} porta il rumore 1/f</strong>: specchio, VAS e '
         'buffer ne sono senza, e le cifre di E5 restano un pavimento per quella parte '
         '(NC-004, bloccante per G1). ')
      + 'Nessuna cifra di distorsione. La provenienza è scritta sotto ogni titolo di '
      'sezione, ed è letta dagli <code>.include</code> dei deck, non dichiarata.</div>')

    A('<p>Il progetto sostituisce un Technics SU-9070 la cui struttura di guadagno '
      'richiede <strong>46 dB di attenuazione</strong>, causa misurabile della mancanza '
      'di dinamica lamentata. La topologia canonica è in <code>circuits/preamp/</code>; i '
      'banchi di prova in <code>spice/preamp/tb/</code>; i dati dei deck veloci in '
      f'<code>{rel(L42)}/</code>, corsi oggi sul circuito di <code>main</code>; quelli del '
      'mute, dell&rsquo;interblocco e del calore nelle cartelle dei loro lotti, nominate sotto '
      'ogni sezione.</p>')

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
    A(f'<p class="meta"><strong>La seconda corsa.</strong> Gli stessi {len(l40["decks"])} deck '
      f'sono stati corsi da L40 il 2026-09-23, in un altro worktree, sullo stesso circuito '
      f'(<code>{rel(L40)}/</code>): le {l40["n_res"]} righe di risultato dei log coincidono una '
      f'per una, e le {l40["n_tab"]} tabelle che L40 ha tenuto coincidono byte per byte. '
      + (f'Senza questa strada: {", ".join(l40["senza"])}, che non stampa risultati e di cui '
         'L40 non ha tenuto tabelle. ' if l40["senza"] else '')
      + ((f'{l40["spliced"]} <code>print</code> spezzate nei log da una Note del gmin stepping '
          'sono state ricucite (limitations #37). ' if l40["spliced"] > 1 else
          'Una <code>print</code> spezzata nel log da una Note del gmin stepping è stata '
          'ricucita (limitations #37). ') if l40["spliced"] else '') + '</p>')

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
    A(prov_line("tb_ac.cir", src(L42, "tb_ac")))
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
      'da 1 mΩ a (10 kΩ + Thévenin del trim)/4, carichi 100 kΩ e 10 kΩ. Il Miller è da 1 nF '
      '(ADR-042): con i modelli del costruttore il blocco a guadagno unitario era sceso '
      'sotto i 60° (NC-034, chiusa). '
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
    A(f'<p class="meta">Il deck scrive le curve solo alla sorgente di 2,5 kΩ col carico da '
      f'100 kΩ (<code>{rel(v1["bode_dir"])}/</code>); le sorgenti che il trim aggiunge stanno '
      'nella tabella dei margini qui sopra, non in queste figure.</p>')

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
    A('<h3>Con le LDR del mute all&rsquo;ingresso</h3>')
    A(prov_line(ldr["deck"], ldr["dir"], deckdir=ldr["dir"],
                note=" &middot; <strong>copia del deck</strong> di L29b2 con la cima a 12 mA "
                     "(ADR-050), fatta in L41b2"))
    A('<p>Il mute graduale mette due LDR all&rsquo;ingresso del blocco A (ADR-039): una in '
      'serie, una verso massa. In ascolto la cella in serie è accesa e vale '
      f'{" / ".join(it(float(x), 4) for x in ldr["rs_gioco"])} Ω; la derivazione è spenta. '
      'Il minimo di |Z<sub>in</sub>| su ogni posizione del trim:</p>')
    A('<div class="tablewrap"><table><tr><th>Stato delle LDR</th>'
      + "".join(f'<th class="num">selettore {lab_c(c)}</th>' for c in ldr["csels"])
      + '<th>Esito</th></tr>')
    for s, lab in LDR_STATI.items():
        vals = [ldr["z"][(s, c)] for c in ldr["csels"]]
        A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{it(x / 1000, 4)} kΩ</td>' for x in vals)
          + verdict(all(x >= 1e5 for x in vals)) + '</tr>')
    A('</table></div>')
    A('<div class="tablewrap"><table><tr><th>Catena col trim, peggiore su trim, modo, '
      'attenuatore e sorgente</th><th class="num">Rumore</th></tr>')
    llab = {"nessuna": "senza LDR", "curvab": "LDR in curva B (tipica)",
            "curvad": "LDR in curva D (la più resistiva)"}
    for k, v in ldr["e5"].items():
        A(f'<tr><td>{llab.get(k, html_escape(k))}</td><td class="num">{fx(v, 3)} µV</td></tr>')
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
    A(prov_line("tb_zout_psrr_noise.cir", src(L42, "tb_zout_psrr_noise")))
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
    A(prov_line("tb_e4_uscite.cir", e4["dir"]))
    A('<p><strong>E4</strong> chiede un&rsquo;impedenza d&rsquo;uscita &lt; 100 Ω in banda '
      'passante, misurata escludendo la reattanza del condensatore d&rsquo;accoppiamento, e '
      'costante con la posizione del volume. Il deck porta la catena intera in subckt: blocco A, '
      'buffer delle fisse, trim, attenuatore, blocco B. Inietta 1 A AC in un jack per volta, '
      'a sorgente spenta, in ogni cella di trim &times; attenuatore &times; modo. «Escludendo la '
      'reattanza» si legge come Re(Z) al jack: il condensatore in serie è reattanza pura, e '
      'nella parte reale resta lo scarico in parallelo, che pesa a 20 Hz.</p>')
    A('<div class="tablewrap"><table><tr><th>Uscita</th><th class="num">Celle</th>'
      '<th class="num">Re(Z) max, 20 Hz–20 kHz</th><th class="num">Re(Z) 1 kHz</th>'
      '<th class="num">|Z| 1 kHz</th><th class="num">nodo, 1 kHz</th>'
      '<th class="num">dispersione su trim &times; attenuatore</th><th>Esito</th></tr>')
    olab = {"main": "principale", "fix1": "fissa 1", "fix2": "fissa 2"}
    for g in e4["groups"]:
        mlab = MLAB[g["modes"][0]] if len(g["modes"]) == 1 else "tre modi"

        def rng(c, nd=4):
            lo, hi = it(g[c + "_min"], nd), it(g[c + "_max"], nd)
            return lo if lo == hi else f"{lo}&ndash;{hi}"
        A(f'<tr><td>{olab[g["out"]]} &middot; {mlab}</td><td class="num">{g["n"]}</td>'
          f'<td class="num">{it(g["zrmax_max"], 4)} Ω</td><td class="num">{rng("zr1k")} Ω</td>'
          f'<td class="num">{rng("zm1k")} Ω</td><td class="num">{rng("zn1k")} Ω</td>'
          f'<td class="num">{it_sci(g["disp"], 2)} Ω</td>'
          f'{verdict(g["zrmax_max"] < E4_MAX and g["disp"] < E4_COSTANZA)}</tr>')
    A('</table></div>')
    A(f'<p class="meta">La soglia di costanza, {it(E4_COSTANZA, 0)} Ω, è la lettura di L13: E4 '
      'non dà tolleranza, e il termine di confronto è il passivo di ADR-002, che a metà corsa '
      'porta in uscita un quarto della sua resistenza. La dispersione è il massimo su Re(Z) max, '
      'Re(Z) e |Z| a 1 kHz. Le tabelle coincidono col log riga per riga; lo stesso esito lo dà '
      f'<code>{html_escape(e4.get("script", ""))}</code> sugli stessi file; la Zout al nodo e al '
      'jack del deck qui sotto coincide con quella della principale entro 10<sup>&minus;3</sup>.</p>')
    A(prov_line("tb_zout_psrr_noise.cir", z["dir"]))
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
      f'E4 chiede &lt; 100 Ω in banda passante. Al jack a 20 Hz la |Z| vale '
      f'{it(z["0db"]["z20"], 4)} Ω, ma quella <em>è la reattanza del condensatore '
      f'd&rsquo;uscita da 4,7 µF</em>: al nodo OUT la stessa frequenza dà '
      f'{it(z["0db"]["za20"], 3)} Ω, e la parte reale al jack resta ≤ '
      f'{it(max(e4_main, e4_fix), 4)} Ω. Per questo il requisito dice «misurata escludendo la '
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

    # --- il mute ---
    A(h2("smute"))
    A(prov_line("tb_v2_l29d2.cir", mu["mat_dir"], deckdir=os.path.join(L29D2, "deck"),
                note=" &middot; la matrice, sul banco generato di L29d2"))
    A(prov_line("tb_v2_casopeggiore.cir", mu["src_dir"],
                note=" &middot; le celle peggiori, sul deck generato dal sorgente (L29e)"))
    A('<p>Il mute ha due stadi. <strong>A monte</strong>, due LDR all&rsquo;ingresso del '
      'blocco A abbassano la musica lungo il profilo v4 (ADR-038, ADR-039): la corrente dei '
      'LED segue una tabella log-lineare nella profondità d, percorsa in '
      f'{it(mu["prof"]["tg"], 3)} s. <strong>Al jack</strong>, un relè per uscita in serie, '
      'geometria iii (ADR-044): comune sul lato del condensatore, NO sul jack, NC a massa, '
      'uno scarico su entrambi i lati. Il relè stacca il jack quando la musica è già giù.</p>')
    A('<p>V2 si giudica con tre grandezze (ADR-032, ADR-040): <strong>A</strong>, il gradino '
      'senza musica, all&rsquo;inserzione e al rilascio; <strong>B2</strong>, il residuo al jack '
      'a mute inserito; soglia 100 µV di picco per entrambe. <strong>S</strong>, il salto di '
      'livello della musica in 100 ms, soglia 20 dB: il taglio si giudica sul salto, non sul '
      'residuo di un fit.</p>')
    A('<h3>La matrice, peggiore per gruppo</h3>')
    A('<div class="tablewrap"><table><tr><th>Gruppo</th><th class="num">Verdetti</th>'
      '<th class="num">A, peggiore</th><th class="num">B2, peggiore</th>'
      '<th class="num">S, peggiore</th><th>Esito</th></tr>')

    def cellv(m, unit):
        if m is None:
            return '<td class="num">&mdash;</td>'
        v = f"{fx(m['v'], 2)} dB" if unit == "dB" else f"{it(m['v'] * 1e6, 3)} µV"
        return (f'<td class="num"><strong>{v}</strong><br><span class="na">'
                f'{html_escape(m["cella"])} &middot; {m["uscita"].lower()}</span></td>')
    for r in mu["rows"]:
        A(f'<tr><td>{r["gruppo"]} &middot; {r["lab"]}</td><td class="num">{r["n"]}</td>'
          + cellv(r["A"], "µV") + cellv(r["B2"], "µV") + cellv(r["S"], "dB")
          + verdict(r["fuori"] == 0, "regge", f'{r["fuori"]} fuori') + '</tr>')
    A('</table></div>')
    A(f'<p><strong>{mu["n"] - mu["n_fuori"]} verdetti su {mu["n"]} reggono.</strong> Ogni '
      'verdetto è il peggiore sulle tre uscite; il dossier li ricalcola da '
      '<code>analisi.csv</code> e dal manifesto, con la regola di <code>verdetto.py</code> '
      'scritta di nuovo, e li confronta con <code>verdetto.csv</code> uno per uno. Le '
      f'{mu["src_n"]} grandezze delle celle peggiori, rifatte sul deck generato dal sorgente '
      f'in L29e, coincidono con la matrice (scarto relativo massimo {it_sci(mu["src_scarto"], 2) if mu["src_scarto"] else "0"}).</p>')
    p = mu["prof"]
    A('<h3>Il profilo v4 visto al jack</h3>')
    A(prov_line("tb_v2_casopeggiore.cir", mu["prof_dir"],
                note=f' &middot; la cella <code>{html_escape(p["cella"])}</code> e i suoi due '
                     'riferimenti, rifatti oggi'))
    A(figure("fig_mute.svg", "Livello della musica al jack durante il mute graduale"))
    A(f'<p>Musica a {p["f"]} Hz a fondo scala, +10 dB, sul jack principale; comando di mute a '
      f'{it(p["t_ins"], 3)} s, rilascio a {it(p["t_rel"], 3)} s. Il salto più grande in '
      f'100 ms vale <strong>{fx(p["S"]["S_ins"], 2)} dB</strong> scendendo e '
      f'<strong>{fx(p["S"]["S_rel"], 2)} dB</strong> risalendo, contro 20 dB. Il dossier li '
      'ricava dalla curva e li confronta con quelli che <code>v2_metodo.py</code> ha scritto '
      f'per la stessa corsa; le {p["n_today"]} righe dell&rsquo;analisi di oggi coincidono con '
      'quelle di L29e.</p>')
    A(f'<div class="note"><strong>Con quale cima.</strong> La matrice, le celle del sorgente e '
      f'questa curva sono corse col deck versionato, che accende i LED fino a '
      f'<strong>{it(mu["cima_deck"] * 1000, 3)} mA</strong> (la tabella del profilo in '
      '<code>tb_v2_casopeggiore.cir</code>). ADR-050 ha portato la cima del firmware a 12 mA e '
      'ha rifatto E3 ed E5 (sezione 6), non questa matrice: S con la cima nuova non è '
      'misurato.</div>')

    # --- l'interblocco ---
    A(h2("sint"))
    A('<p>Guadagno e trim si cambiano solo a mute inserito, e il guadagno si tiene da sé '
      '(ADR-041, strada B di ADR-030): due relè ausiliari in autoritenuta sui relè del '
      'guadagno, un polo ponte per bobina sul rotativo, i LED dagli ausiliari. Il permissivo '
      'ha un comando proprio, sfasato dopo i jack (ADR-045); comandi e LED stanno su header '
      'verso il pannello (ADR-028).</p>')
    A(f'<p class="prov">Netlist <code>{html_escape(il["net"])}</code> &middot; '
      '<code>scripts/check_relay_safe_state.py</code> (il 2e di <code>run_tests.sh</code>), '
      'rieseguito da questa pagina</p>')
    A(f'<div class="tablewrap"><table><tr><th>Relè</th><th>Parte e sigla</th><th>Ruolo</th></tr>')
    for k, part, role in il["relays"]:
        A(f'<tr><td>{k}</td><td>{html_escape(part)}</td><td>{role.lower()}</td></tr>')
    A('</table></div>')
    g = il["guad"]
    A(f'<p>Sulla netlist di oggi il 2e prova per raggiungibilità: {il["stati_trim"]} stati dei '
      f'bistabili del trim fuori mute, nella finestra del permissivo e in mute; per il guadagno '
      f'({html_escape(g[0]) if g else "?"}) {g[1] if g else "?"} coppie stato/posizione e '
      f'{g[2] if g else "?"} trasferimenti con la manopola allo stato. Che il controllo sappia '
      'cadere lo dicono i falsi: '
      + "; ".join(f'{lot}, {v["n"]} netlist sabotate, tutte respinte per la ragione voluta'
                  for lot, v in il["falsi"].items()) + '.</p>')
    A('<h3>La corsa al rilascio del mute</h3>')
    A(f'<p class="prov">Dati <code>{html_escape(rel(il["corsa_dir"]))}/</code> &middot; un deck '
      'ngspice per cella, scritto da <code>corsa.py</code>: bobine, contatti e ausiliari, '
      'nessun transistor; il modello del relè è dichiarato nel suo docstring</p>')
    A('<div class="tablewrap"><table><tr><th>Variante</th><th class="num">Celle</th>'
      '<th class="num">Cade al rilascio</th><th class="num">Cade all&rsquo;inserimento</th></tr>')
    vlab = {"ingenua": "senza polo ponte", "progetto": "<strong>il progetto</strong>, col polo ponte"}
    for var in ("progetto", "ingenua"):
        c = il["corsa"].get(var, {})
        A(f'<tr><td>{vlab[var]}</td><td class="num">{c.get("n", "?")}</td>'
          f'<td class="num">{c.get("ril", "?")}</td><td class="num">{c.get("ins", "?")}</td></tr>')
    A('</table></div>')
    A(f'<p>{il["corsa_n"]} corse: induttanza della bobina, buco del permissivo, resistenza, soglia '
      'di rilascio e tensione dei relè spazzate. La corsa è chiusa <em>per struttura</em>, dal '
      'polo ponte: il datasheet non dà la dinamica della bobina, e il modello del relè è '
      'dichiarato, non del costruttore. I conteggi sono ricontati da <code>corsa.csv</code> e '
      'confrontati con <code>sintesi.txt</code>.</p>')

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

    # --- il calore ---
    A(h2("sheat"))
    A(f'<p class="prov">Script <code>{html_escape(rel(os.path.join(heat["dir"], "stima_telaio.py")))}</code>'
      ' &middot; <strong>stima calcolata, non simulata</strong>; rieseguito da questa pagina</p>')
    A('<p>P5 e ADR-021 chiedono 60 °C nel telaio, dentro un vano di libreria chiuso, con la '
      'stanza a 35 °C. La scheda audio non è sola nel telaio: la stima somma tutto '
      'l&rsquo;apparecchio (ADR-047).</p>')
    A('<div class="tablewrap"><table><tr><th>Dissipazione</th><th class="num">nominale</th>'
      '<th class="num">minima</th><th class="num">massima</th></tr>')
    for k, a, b, c in heat["parts"] + ([heat["tot"]] if heat["tot"] else []):
        strong = k == "TOTALE"
        cells = "".join(f'<td class="num">{"<strong>" if strong else ""}{fx(x, 2)} W'
                        f'{"</strong>" if strong else ""}</td>' for x in (a, b, c))
        A(f'<tr><td>{"<strong>totale</strong>" if strong else html_escape(k)}</td>{cells}</tr>')
    A('</table></div>')
    A('<div class="tablewrap"><table><tr><th>Gioco del vano</th><th>Caso</th>'
      '<th class="num">P</th><th class="num">salto del telaio</th><th class="num">salto del vano</th>'
      '<th class="num">aria nel telaio</th><th>60 °C</th></tr>')
    for gio, caso, p_, dtt, dtv, tin in heat["vano"]:
        A(f'<tr><td>{html_escape(gio.replace(".", ","))}</td><td>{caso}</td>'
          f'<td class="num">{fx(p_, 1)} W</td><td class="num">{fx(dtt, 1)} °C</td>'
          f'<td class="num">{fx(dtv, 1)} °C</td><td class="num"><strong>{fx(tin, 1)} °C</strong></td>'
          f'{verdict(tin <= TA)}</tr>')
    A('</table></div>')
    A(f'<p>Il vano chiuso regge i 60 °C nel caso peggiore con almeno '
      f'<strong>{it(heat["gioco"], 3)} cm</strong> di gioco per lato. La scheda audio della stima '
      f'coincide coi rail di <code>tb_op</code> di oggi: 8 &times; 15 V &times; (|i<sub>+</sub>| + '
      f'|i<sub>&minus;</sub>|) = {it(8 * heat["p_blk"], 4)} W. La conferma è la temperatura '
      'nel telaio del prototipo (ADR-021, «Da riaprire se»).</p>')

    # ============================================== L42b: l'alimentatore ===
    pw, sv, tm, fw, ld, off, p9 = M["pw"], M["sv"], M["tm"], M["fw"], M["ld"], M["off"], M["p9"]
    dbf = off["f"]["db"]

    def volt(v):
        """Una tensione piccola nella sua unita', virgola italiana."""
        for k, u in ((1, "V"), (1e-3, "mV"), (1e-6, "µV"), (1e-9, "nV")):
            if abs(v) >= k:
                return f"{it(v / k, 3)} {u}"
        return f"{it(v / 1e-9, 3)} nV"

    def spl(v):
        return f"{fx(dbf(v), 1)} dB SPL <span class=\"na\">({volt(v)})</span>"

    def cella(r, k, u=""):
        """Una cella di analisi.csv: '>x' e' un limite (la corsa finisce prima),
        vuota e' «non si applica»; il meno e' tipografico."""
        s = (r.get(k) or "").strip()
        if not s:
            return "&mdash;"
        v = ("&gt; " + it(float(s[1:]), 4)) if s.startswith(">") else it(float(s), 4)
        return v.replace("-", "&minus;") + (f" {u}" if u else "")

    t_nom, t_min = tm["t"]["nom"], tm["t"]["min"]
    today = pw["oggi"]
    rl = {r["caso"]: r for r in sv["rows"]}
    offl = {r["caso"]: r for r in off["rows"]["l41c"]}

    A(h2("spsu"))
    A(f'<p class="prov">Disegno <code>docs/preamp/schematic/psu_blocks_draw.py</code>, ogni cifra '
      f'letta da <code>{rel(PSU_NET)}</code> e asserita &middot; sorgente '
      '<code>circuits/preamp/psu.py</code></p>')
    A('<p>La seconda scheda. Porta i rail audio, <code>VRELAY</code> per le bobine della scheda '
      'audio e la logica; decide <em>quando</em> il mute si inserisce e si rilascia, e lo '
      'fa in un ordine che sta nell&rsquo;hardware, non nel firmware. Il diagramma è a '
      'blocchi: le soglie e le costanti di tempo stampate sono calcolate dai valori della '
      'netlist, le cifre misurate stanno nelle sezioni che seguono.</p>')
    A(figure("psu_blocks.svg", "Diagramma a blocchi dell'alimentatore"))
    A('<div class="tablewrap"><table><tr><th>Decisione</th><th>Che cosa</th>'
      '<th>La cifra che la regge, dai dati</th></tr>')
    pn = today.get("perdita_rete_nom", {})
    A(f'<tr><td>ADR-048</td><td>rail lineari (nessuno switching), <code>VRELAY</code> da un '
      'trasformatore proprio, standby con l&rsquo;interruttore posteriore, sorvegliante in '
      'hardware sul gate del sink di <code>MUTE_CMD</code></td>'
      f'<td class="num">alla perdita di rete <code>MUTE_CMD</code> rilasciato a '
      f'{cella(pn, "t_off_ms", "ms")}, coi rail ancora a '
      f'{cella(pn, "vplus_at_off")} / {cella(pn, "vminus_at_off", "V")}</td></tr>')
    A(f'<tr><td>ADR-049</td><td>Δ e Δ₂ come RC su comparatori; <code>VRELAY</code> tolta '
      'alla scheda audio in standby (NC-037)</td>'
      f'<td class="num">Δ ≥ {fx(t_min["micro_reset"]["d"], 2)} ms all&rsquo;angolo minimo col micro '
      f'in reset &middot; standby: {fx(abs(t_nom["standby_j1"]), 3)} V a J1, '
      f'{fx(t_nom["standby_mw"], 1)} mW da T2</td></tr>')
    A(f'<tr><td>ADR-050</td><td>la cima delle LDR a 12 mA a ogni temperatura</td>'
      f'<td class="num">cima della tabella {it(ld["cima"] * 1000, 3)} mA &middot; calibrato entro '
      f'{fx(ld["w_cal"][0], 2)} dB</td></tr>')
    if "corto_u503" in offl:
        A(f'<tr><td>ADR-051</td><td>il corto della linea a 12 V dei relè accettato sotto il '
          'tetto (guasto singolo)</td>'
          f'<td class="num">{spl(float(offl["corto_u503"]["picco_V"]))} al jack &middot; tetto '
          f'{fx(dbf(p9["tetto_V"]), 1)} dB SPL</td></tr>')
    A('</table></div>')

    # --- potenza ---
    A(h2("spow"))
    A(prov_psu(os.path.join(pw["dir"], "rete", "tb_psu_rete.cir"), pw["dir"],
               " &middot; corso il 2026-09-27 sul <code>psu.net</code> di oggi"))
    A('<p><strong>Una cosa trovata rigenerando.</strong> I banchi della potenza di L41a sono '
      'corsi sul <code>psu.py</code> di L41a, che L41b1 ha riscritto (il temporizzatore, '
      'Q505, il pilota delle LDR). Queste cifre sono una ricorsa di oggi: gli stessi casi e '
      'le stesse sonde di L41a, sul circuito di oggi, col micro che gira e resta fermo '
      'durante l&rsquo;evento (il solo percorso hardware, come le sorgenti fisse di L41a). '
      'Lo stesso banco <em>col carico di L41a</em> (senza le bistabili del trim, le stringhe '
      'delle LDR alla cima e il micro) ridà L41a su ogni colonna, entro 0,5 ms o l&rsquo;1 % '
      'e 10 mV: la parte di potenza è quella, e ogni scarto qui sotto è il carico.</p>')
    A('<h3>A regime</h3>')
    A('<div class="tablewrap"><table><tr><th>Rete</th><th class="num">V+</th><th class="num">V−</th>'
      '<th class="num">VRELAY_REG</th><th class="num">VRELAY a J1</th><th class="num">V5</th>'
      '<th class="num">valle del grezzo +</th><th class="num">valle −</th>'
      '<th class="num">valle di VRELAY</th></tr>')
    for f_, lab in (("m10", "−10 %"), ("nom", "nominale"), ("p10", "+10 %")):
        r = today.get(f"regime_{f_}", {})
        A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{cella(r, k)} V</td>' for k in (
            "vplus", "vminus", "vrelay_reg", "vrelay", "v5", "raw_p_min", "raw_m_min_abs",
            "raw_v_min")) + '</tr>')
    A('</table></div>')
    A('<h3>La perdita di rete, col rivelatore</h3>')
    A('<div class="tablewrap"><table><tr><th>Rete</th><th class="num">MUTE_CMD rilasciato</th>'
      '<th class="num">rivelatore</th><th class="num">rail + a 13,5 / 10,6 V</th>'
      '<th class="num">rail al rilascio</th>'
      f'<th class="num">VRELAY_REG ≥ 11,4 V dopo</th><th>P9: ≥ {fx(p9["vrelay_ms"], 0)} ms</th></tr>')
    for f_, lab in (("m10", "−10 %"), ("nom", "nominale"), ("p10", "+10 %")):
        r = today.get(f"perdita_rete_{f_}", {})
        vh = float(r.get("vr_hold_ms") or "nan")
        A(f'<tr><td>{lab}</td><td class="num">{cella(r, "t_off_ms")} ms</td>'
          f'<td class="num">{cella(r, "t_md_ms")} ms</td>'
          f'<td class="num">{cella(r, "t_p135_ms")} / {cella(r, "t_p106_ms")} ms</td>'
          f'<td class="num">{cella(r, "vplus_at_off")} / {cella(r, "vminus_at_off")} V</td>'
          f'<td class="num">{cella(r, "vr_hold_ms")} ms</td>{verdict(vh >= p9["vrelay_ms"])}</tr>')
    A('</table></div>')
    A('<h3>Un regolatore che cede, e il rivelatore guasto</h3>')
    A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">MUTE_CMD rilasciato</th>'
      f'<th class="num">dopo lo scatto a |{fx(p9["soglia_V"], 1)} V|</th>'
      '<th class="num">rail al rilascio</th><th class="num">VRELAY_REG ≥ 11,4 / ≥ 9,6 V</th>'
      f'<th>P9: entro {fx(p9["entro_ms"], 0)} ms</th></tr>')
    for c, lab in (("guasto_u501", "U501 (rail +) spento"), ("guasto_u502", "U502 (rail −) spento"),
                   ("guasto_u503", "U503 (<code>VRELAY_REG</code>) spento"),
                   ("perdita_senza_rivelatore_m10", "perdita di rete, rivelatore guasto, −10 %"),
                   ("perdita_senza_rivelatore_nom", "idem, nominale"),
                   ("perdita_senza_rivelatore_p10", "idem, +10 %")):
        r = today.get(c, {})
        tr = (r.get("trip_after_135_ms") or "").strip()
        ok = (float(tr) <= p9["entro_ms"]) if tr else None
        A(f'<tr><td>{lab}</td><td class="num">{cella(r, "t_off_ms")} ms</td>'
          f'<td class="num">{cella(r, "trip_after_135_ms", "ms")}</td>'
          f'<td class="num">{cella(r, "vplus_at_off")} / {cella(r, "vminus_at_off")} V</td>'
          f'<td class="num">{cella(r, "vr_hold_ms")} / {cella(r, "vr80_hold_ms")} ms</td>'
          + (verdict(ok) if ok is not None else '<td class="na">scatta su VRELAY_REG</td>') + '</tr>')
    A('</table></div>')
    A('<p>Un tempo negativo dopo lo scatto vuol dire che il mute è già rilasciato prima '
      'che un rail arrivi alla soglia. Col rivelatore di rete guasto il caso è doppio (la '
      'rete persa e il rivelatore rotto), come L41a lo dichiarò: a rete bassa scatta per '
      'primo il sorvegliante di <code>VRELAY_REG</code>, e i rail sono ancora sopra la soglia.</p>')
    A('<h3>Cosa è cambiato da L41a</h3>')
    A('<div class="tablewrap"><table><tr><th>Caso</th><th>Grandezza</th><th class="num">L41a</th>'
      '<th class="num">oggi</th><th class="num">oggi, col carico di L41a</th></tr>')
    names = {"vr_hold_ms": "VRELAY_REG ≥ 11,4 V [ms]", "vr80_hold_ms": "VRELAY_REG ≥ 9,6 V [ms]",
             "raw_v_min": "valle di VRELAY [V]", "t_off_ms": "MUTE_CMD rilasciato [ms]",
             "trip_after_135_ms": "dopo lo scatto a 13,5 V [ms]", "vplus_at_off": "V+ al rilascio [V]",
             "vminus_at_off": "V− al rilascio [V]"}
    for caso, k, a, b, c in pw["scarti"]:
        A(f'<tr><td>{html_escape(caso)}</td><td>{names.get(k, html_escape(k))}</td>'
          f'<td class="num">{html_escape((a or "").replace(".", ","))}</td>'
          f'<td class="num"><strong>{html_escape((b or "").replace(".", ","))}</strong></td>'
          f'<td class="num">{html_escape((c or "").replace(".", ","))}</td></tr>')
    A('</table></div>')
    vr_m10 = float(today.get("perdita_rete_m10", {}).get("vr_hold_ms") or "nan")
    vr_old = float(pw["old"].get("perdita_rete_m10", {}).get("vr_hold_ms") or "nan")
    A(f'<p>Ogni scarto sta su <code>VRELAY_REG</code>, o sui casi in cui è lei a far scattare '
      f'il sorvegliante. A rete −10 % la tenuta scende da {it(vr_old, 4)} a '
      f'<strong>{it(vr_m10, 4)} ms</strong>: P9 regge ancora (≥ {fx(p9["vrelay_ms"], 0)} ms), '
      f'con {it(vr_m10 - p9["vrelay_ms"], 3)} ms di margine invece di '
      f'{it(vr_old - p9["vrelay_ms"], 3)}. La causa è il carico che L41b1 e L41b2 hanno messo '
      'su <code>VRELAY_REG</code>, soprattutto il ramo d&rsquo;ingresso dello specchio delle LDR '
      'alla cima, che attraverso V5 la scarica. Il commento di <code>C_VRELAY</code> in '
      '<code>psu.py</code> cita ancora le cifre di L41a; il sorgente non si tocca in questo '
      'lotto.</p>')
    A('<h3>Il raddrizzatore: il dimensionamento, non il circuito</h3>')
    A(f'<p class="prov">Script <code>{rel(os.path.join(L41A, "scelte", "raddrizzatore.py"))}</code>, '
      'modello ipotetico dichiarato (un Thevenin per semi-avvolgimento, i regolatori come '
      'carichi costanti), rieseguito il 2026-09-27 in '
      f'<code>{rel(os.path.join(L42B, "scelte"))}/</code>: la tabella è uguale byte per byte</p>')
    A('<div class="tablewrap"><table><tr><th>Rete</th><th class="num">carico del +</th>'
      '<th class="num">V+ min / medio</th><th class="num">margine della valle</th></tr>')
    for r in pw["rad"]:
        rete = float(r["rete"]) * 100 - 100
        A(f'<tr><td>{sg(rete, 0) if abs(rete) > 1e-9 else "nominale"}'
          f'{" %" if abs(rete) > 1e-9 else ""}</td><td class="num">{r["carico_plus_mA"]} mA</td>'
          f'<td class="num">{it(float(r["v_plus_min"]), 4)} / {it(float(r["v_plus_avg"]), 4)} V</td>'
          f'<td class="num">{sg(float(r["margine_valle_V"]), 3)} V</td></tr>')
    A('</table></div>')
    carichi = sorted({int(r["carico_plus_mA"]) for r in pw["rad"]})
    A('<p>Sono le righe del toroidale scelto con ADR-048 (2 &times; 15 V, 50 VA), portate '
      'all&rsquo;utente prima della decisione; il margine è la valle del grezzo sopra 15 V più '
      f'il dropout. La riga a {carichi[-1]} mA è il rail + con <code>VRELAY</code> ricavata da lì, '
      'la strada che ADR-048 ha scartato per un trasformatore proprio. Il trasformatore vero va '
      'confermato sul pezzo.</p>')

    # --- sorvegliante ---
    A(h2("ssup"))
    A(prov_psu(os.path.join(L41C, "seq", "perdita", "tb_psu_seq_perdita_g3.cir"), sv["dir"],
               " &middot; ricorso il 2026-09-27 in "
               f'<code>{rel(L42B_C)}/</code>: lo stesso verdetto byte per byte, e per ogni caso lo '
               'stesso punto fisso, lo stesso deck rigenerato da <code>psu.net</code> e le stesse '
               'uscite del firmware'))
    A('<p>Il circuito dell&rsquo;alimentatore col firmware del temporizzatore come micro, '
      'iterati fino al punto fisso (L41c). I relè sono presi all&rsquo;angolo peggiore del '
      'G6K: il jack staccato <em>il più tardi possibile</em>, il guadagno a 0 dB <em>il più '
      'presto possibile</em>. Il criterio r chiede che il guadagno non si muova mai col jack '
      'collegato (ADR-045); s che il jack si stacchi prima che il rail + perda la '
      'regolazione (L30).</p>')
    A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">MUTE_CMD rilasciato</th>'
      '<th class="num">Δ ai rilasci</th><th class="num">jack, tardi</th>'
      '<th class="num">guadagno, presto</th><th class="num">V+ &lt; 10,6 V</th>'
      '<th class="num">K501</th><th>Criteri</th></tr>')
    labs = {"spegnimento_l": "spegnimento morbido", "perdita": "perdita di rete",
            "perdita_min": "idem, Δ all&rsquo;angolo minimo", "guasto": "U502 (rail −) spento",
            "guasto_u501": "U501 (rail +) spento", "guasto_u503": "U503 (<code>VRELAY_REG</code>) spento",
            "guasto_u503_min": "idem, angolo minimo", "cf_nodelta": "controfattuale senza Δ",
            "corto_u503": "corto dell&rsquo;uscita di U503"}
    for r in sv["rows"]:
        o = lambda x, u="ms", nd=4: "&mdash;" if x is None else f"{it(x, nd)} {u}"
        mm = o(r["i_s"], "s") if r["caso"] == "spegnimento_l" else o(r["m"])
        esito = ('<td class="na">nessun verdetto: decisione dell&rsquo;utente (ADR-051)</td>' if r["info"]
                 else f'<td class="ok">C3 e r cadono, come devono ({r["n_crit"]} criteri)</td>'
                 if r["deve_fallire"] else verdict(r["ok"], f'{r["n_crit"]} su {r["n_crit"]}'))
        A(f'<tr><td>{labs[r["caso"]]}</td><td class="num">{mm}</td><td class="num">{o(r["delta"])}</td>'
          f'<td class="num">{o(r["jack"])}</td><td class="num">{o(r["guad"])}</td>'
          f'<td class="num">{o(r["v106"])}</td><td class="num">{o(r["k501"])}</td>{esito}</tr>')
    A('</table></div>')
    k501 = rl.get("spegnimento_l", {}).get("k501")
    A(f'<p>Allo spegnimento morbido il mute si rilascia {it(rl.get("spegnimento_l", {}).get("i_s") or float("nan"), 5)} s '
      f'dopo l&rsquo;interruttore frontale (la dissolvenza intera), e K501 stacca il toroidale '
      f'{it(k501 or float("nan"), 3)} ms dopo il rilascio di <code>PERMIT_CMD</code>: P9 ne chiede '
      f'≥ {fx(p9["margine_ms"], 0)}. I tempi dopo l&rsquo;evento sono in ms, tranne il '
      'rilascio dello spegnimento morbido.</p>')

    # --- temporizzatore ---
    A(h2("stim"))
    A(prov_psu(os.path.join(tm["dir"], "tb_psu_timer_nom.cir"), tm["dir"],
               " &middot; ricorso il 2026-09-27 in "
               f'<code>{rel(os.path.join(L42B, "timer"))}/</code>: deck rigenerati uguali, '
               '<code>analizza_timer.py</code> ridà lo stesso testo sui log di allora e di oggi'))
    A('<p>Il ritardo Δ fra il rilascio di <code>MUTE_CMD</code> e quello di '
      '<code>PERMIT_CMD</code> sta in un RC su un comparatore, e deve reggere <em>qualunque '
      'cosa faccia il micro</em>. L&rsquo;angolo minimo prende C<sub>T</sub> e C<sub>T2</sub> '
      '−5 %, R<sub>T</sub> e R<sub>T2</sub> −1 %, V5 a 4,90 V e il riferimento a 2,505 V.</p>')
    A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">Δ nominale</th>'
      '<th class="num">Δ angolo minimo</th><th class="num">VRELAY a J1 &lt; 9,6 V dopo PERMIT</th>'
      f'<th>Δ ≥ {fx(tm["dmin"], 0)} ms</th></tr>')
    for k, lab in (("micro_reset", "il micro in reset (uscite in alta impedenza)"),
                   ("micro_a_zero", "il micro porta tutto a zero"),
                   ("perdita_rete_micro_reset", "perdita di rete, micro in reset"),
                   ("guasto_U503_micro_reset", "U503 spento, micro in reset"),
                   ("controfattuale_senza_C528", "controfattuale: senza C528")):
        a, b = t_nom[k], t_min[k]
        senza_c528 = k.startswith("controfattuale")
        ok = ((a["d"] < tm["dmin"] and b["d"] < tm["dmin"]) if senza_c528
              else min(a["d"], b["d"]) >= tm["dmin"])
        A(f'<tr><td>{lab}</td><td class="num">{it(a["d"], 4)} ms</td><td class="num">{it(b["d"], 4)} ms</td>'
          f'<td class="num">{it(a["vr"], 4)} / {it(b["vr"], 4)} ms</td>'
          + (f'<td class="{"ok" if ok else "no"}">{"cade, come deve" if ok else "NON cade"}</td>'
             if senza_c528 else verdict(ok)) + '</tr>')
    A('</table></div>')
    A(f'<p>Col micro bloccato alto durante una perdita di rete <code>MUTE_CMD</code> si rilascia '
      f'a +{it(t_nom["fermo_alto"], 4)} ms (il sorvegliante) e <code>PERMIT_CMD</code> '
      f'{"non si rilascia mai" if t_nom["fermo_alto_mai"] else "SI RILASCIA"} nei 400 ms: il '
      'guadagno resta dov&rsquo;è, a jack staccati. Un firmware che abbassa solo '
      f'<code>PERMIT_REQ</code> non muove niente (drain ≤ {it(max(t_nom["drain"], t_min["drain"]), 3)} V, '
      f'contro i 6 V del rilascio). Al rilascio del mute <code>PERMIT_CMD</code> si eccita '
      f'{it(t_nom["anticipo"], 3)} ms prima di <code>MUTE_CMD</code>. In standby <code>VRELAY</code> a '
      f'J1 vale {fx(abs(t_nom["standby_j1"]), 3)} V e T2 eroga {fx(t_nom["standby_mw"], 1)} / '
      f'{fx(t_min["standby_mw"], 1)} mW (nominale / angolo minimo): le perdite a vuoto di T2 non '
      'sono qui, e NC-037 si chiude con quelle (giro BOM).</p>')

    # --- firmware ---
    A(h2("sfw"))
    A(prov_psu(os.path.join(fw["dir"], "accensione", "tb_psu_seq_accensione_g5.cir"), fw["dir"],
               " &middot; firmware <code>firmware/preamp_timer/src/timer_core.c</code> &middot; "
               f'ricorso il 2026-09-27 in <code>{rel(L42B_B2)}/</code>: lo stesso verdetto, gli '
               'stessi deck e le stesse uscite del core'))
    A('<p>Il core del firmware fa da micro del banco: circuito e firmware si iterano finché '
      'le uscite del core non cambiano più fra due giri (il punto fisso), senza che il ponte '
      'debba ricostruire un pin. I criteri sono scritti prima delle corse, nell&rsquo;intestazione '
      'di <code>analizza_seq.py</code>.</p>')
    A('<div class="tablewrap"><table><tr><th>Sequenza</th><th>Stati del firmware</th>'
      '<th class="num">giro del punto fisso</th><th>Criteri</th></tr>')
    for r in fw["rows"]:
        quanti = "%d su %d" % (r["ok"], r["n"])
        A(f'<tr><td>{r["caso"]}</td><td>{html_escape(r["stati"]).replace("-&gt;", "→")}</td>'
          f'<td class="num">{int(r["giro"]) if r["giro"] else "&mdash;"}</td>'
          f'{verdict(r["ok"] == r["n"], quanti)}</tr>')
    A('</table></div>')
    c6, c9 = fw["circ"].get("6"), fw["circ"].get("9")
    A(f'<p><strong>I falsi.</strong> Sull&rsquo;host {fw["falsi"]} falsi del core su {fw["falsi"]} '
      'fanno fallire il loro test (<code>run_host_tests.sh --falsi</code>, rieseguito il '
      '2026-09-27: lo stesso esito byte per byte; lo riesegue anche il blocco 2k di '
      '<code>run_tests.sh</code>). Sul circuito ne sono stati fatti fallire due'
      + (f', ciascuno sul criterio giusto: il falso 6 nel {c6[0]} cade su <code>{c6[1][0]}</code> '
         f'(«{html_escape(c6[2])}»), il falso 9 nello {c9[0]} su <code>{c9[1][0]}</code> '
         f'(«{html_escape(c9[2])}»)' if c6 and c9 else '')
      + '. Questi due non sono stati ricorsi oggi: richiedono di ricompilare il ponte col '
      'falso dentro. <code>src/main_attiny.c</code> non è scritto.</p>')

    # --- LDR ---
    A(h2("sldr"))
    A(prov_psu(os.path.join(ld["dir"], "tb_psu_ldr_cal_cima12mA.cir"), ld["dir"],
               " &middot; ricorso il 2026-09-27 in "
               f'<code>{rel(os.path.join(L42B, "ldr"))}/</code>: calibrazioni e CSV uguali byte per '
               'byte; <code>analizza_ldr.py</code> rieseguito sui log di allora'))
    A('<p>Il DAC comanda due convertitori esponenziali, uno per stringa; il firmware calcola il '
      'codice dalla legge esponenziale alla temperatura del telaio (il sensore del micro), e '
      'corregge la parte ohmica in cima con una calibrazione a due punti letta sul sense. '
      'L&rsquo;errore è ricalcolato qui dalle correnti del CSV, non letto dalla sua colonna.</p>')
    A(figure("fig_ldr_drive.svg", "Errore del pilota delle LDR contro la tabella v4"))
    wc, wx, wr, wp, wn = ld["w_cal"], ld["w_calx"], ld["w_cal_rip"], ld["w_comp"], ld["w_noc"]
    lr = lambda r: f'{r["s"]} {r["nome"]}, {r["t"]} °C'
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">errore peggiore</th>'
      '<th>dove</th><th>±1 dB</th></tr>')
    for lab, w, ok in (("letto a 25 °C, senza compensazione", wn, None),
                       ("compensato col sensore del micro", wp, None),
                       ("compensato e calibrato", wc, wc[0] <= 1.0),
                       ("calibrato, LED al massimo e V5 a 4,90 V", wx, wx[0] <= 1.0)):
        A(f'<tr><td>{lab}</td><td class="num">{fx(w[0], 2)} dB</td><td>{lr(w[1])}</td>'
          + (verdict(ok) if ok is not None else '<td class="na">riferimento</td>') + '</tr>')
    A('</table></div>')
    lo, hi = ld["reset"]
    A(f'<p>Il riposo a 10 nA, calibrato, sta entro {fx(wr[0], 2)} dB ({lr(wr[1])}); il '
      'criterio è 5–20 nA, cioè buio e mai zero. Col DAC in reset le stringhe portano '
      f'{it(lo * 1e9, 3)}–{it(hi * 1e9, 3)} nA: mai zero, sotto il ginocchio di 190 nA.</p>')

    # --- spegnimento e failsafe al jack ---
    A(h2("soff"))
    A(f'<p class="prov">Scheda audio <code>{rel(os.path.join(L41C, "deck", "tb_v2_l41c.cir"))}</code> '
      f'(dal ponte di L41c) e <code>{rel(os.path.join(L30, "deck", "tb_v2_l30.cir"))}</code> (PWL), '
      'col metodo di V2 &middot; i due deck rigenerati oggi sono uguali byte per byte, le corse '
      'rifatte oggi ridanno le stesse analisi e le stesse tabelle &middot; i dB SPL ricalcolati '
      f'con la catena di NC-028 (finale ×{it(off["f"]["g"], 3)}, {fx(off["f"]["spl"], 0)} dB con '
      f'{it(off["f"]["v1w"], 3)} V): un limite superiore, di picco, a 1 m</p>')
    A(f'<p>Un gradino al jack, detto contro una stanza silenziosa (25–35 dB(A), un livello pesato '
      f'contro un picco): V2 è {fx(dbf(1e-4), 1)} dB SPL, l&rsquo;obiettivo di P9 '
      f'{fx(dbf(p9["obiettivo_mV"] * 1e-3), 1)} dB, il tetto di non-danno {fx(dbf(p9["tetto_V"]), 1)} dB.</p>')
    A('<h3>Sul circuito vero (L41c)</h3>')
    A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">picco al jack</th>'
      '<th>Criterio</th><th>Esito</th></tr>')
    for r in off["rows"]["l41c"]:
        v = r["picco_V"]
        esito = r["esito"]
        good = esito.startswith(("sotto", "fallisce, come deve", "tetto sotto"))
        A(f'<tr><td>{labs.get(r["caso"], html_escape(r["caso"]))}</td>'
          f'<td class="num">{spl(float(v)) if v not in ("-", "") else "&mdash;"}</td>'
          f'<td>{html_escape(r["criterio"].replace("<=", "≤").replace(".", ","))}</td>'
          f'<td class="{"ok" if good else "no"}">{html_escape(esito)}</td></tr>')
    A('</table></div>')
    A('<h3>Sul banco di L30 (i rail come PWL)</h3>')
    cls = {"n": "spegnimento morbido", "f": "guasto di un rail o di entrambi",
           "g": "guasto con VRELAY persa", "cf": "controfattuali"}
    A('<div class="tablewrap"><table><tr><th>Classe</th><th class="num">corse</th>'
      '<th class="num">picco peggiore</th><th>Soglia</th><th>Esito</th></tr>')
    for c in ("n", "f", "g", "cf"):
        rr = [r for r in off["rows"]["l30"] if r["classe"] == c]
        corse = [r for r in rr if r["picco_V"] not in ("-", "")]
        w = max(corse, key=lambda r: float(r["picco_V"])) if corse else None
        non = [r["corsa"] for r in rr if r not in corse]
        ok = all(r["esito"] == "sotto" for r in corse) if c != "cf" else None
        A(f'<tr><td>{cls[c]}</td><td class="num">{len(corse)}'
          + (f' + {len(non)} non corse' if non else '') + '</td>'
          f'<td class="num">{spl(float(w["picco_V"])) if w else "&mdash;"}</td>'
          f'<td>{"≤ " + volt(float(w["soglia_V"])) if w and w["soglia_V"] != "-" else "&mdash;"}</td>'
          + (verdict(ok, "tutte sotto", "una sopra") if ok is not None else
             f'<td class="na">senza Δ: {spl(float(w["picco_V"])) if w else "—"}; '
             f'{len(non)} non corse («Timestep too small» nel JFET)</td>') + '</tr>')
    A('</table></div>')
    l30s = [r for r in off["rows"]["l30"] if r["corsa"].startswith("f_") and
            r["corsa"].endswith("s_l30") and r["picco_V"] not in ("-", "")]
    l30w = max(l30s, key=lambda r: float(r["picco_V"])) if l30s else None
    l41p = offl.get("perdita")
    l41g = max((r for r in off["rows"]["l41c"] if r["caso"].startswith("guasto")),
               key=lambda r: float(r["picco_V"]), default=None)
    if l30w and l41p and l41g:
        A(f'<p>L30 disegnava i rail a mano; L41c li prende dall&rsquo;alimentatore vero. La '
          f'perdita di rete passa da {spl(float(l30w["picco_V"]))} (L30, entrambi i rail che '
          f'scendono da subito) a {spl(float(l41p["picco_V"]))}: il rivelatore stacca il jack '
          'coi rail ancora in regolazione. Il caso peggiore resta un regolatore che cede '
          f'({labs.get(l41g["caso"], l41g["caso"])}): {spl(float(l41g["picco_V"]))}, sotto '
          'l&rsquo;obiettivo.</p>')

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
    e3w = min(trim["e3min"], ldr["e3min"])
    A(f'<tr><td>E3</td><td>≥ 100 kΩ al connettore, ogni posizione del trim</td>'
      f'<td class="num">min {it(e3w / 1000, 4)} kΩ, LDR del mute comprese</td>'
      f'{verdict(e3w >= 1e5)}</tr>')
    A(f'<tr><td>E4</td><td>Z<sub>out</sub> &lt; 100 Ω in banda, esclusa la reattanza del cap, '
      'costante col volume</td>'
      f'<td class="num">Re(Z) max al jack {it(e4_main, 4)} Ω principale &middot; {it(e4_fix, 4)} Ω '
      f'fisse &middot; dispersione su trim &times; attenuatore ≤ {it_sci(e4_disp, 2)} Ω</td>'
      f'{verdict(e4_ok, "conforme su tre uscite, ogni posizione di trim e attenuatore")}</tr>')
    A(f'<tr><td>E5</td><td>rumore in uscita &lt; 10 µV RMS</td>'
      f'<td class="num">catena ≤ {fx(max(trim["e5max"], ldr["e5max"]), 3)} µV, LDR comprese</td>'
      '<td class="na">sotto soglia, ma 1/f solo sulla coppia d&rsquo;ingresso &mdash; NC-004 '
      'aperta</td></tr>')
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
    smax = max(r["S"]["v"] for r in mu["rows"] if r["S"])
    A(f'<tr><td>V2</td><td>il mute: A e B2 ≤ 100 µV di picco, S ≤ 20 dB in 100 ms '
      '(ADR-032, ADR-040)</td>'
      f'<td class="num">{mu["n"] - mu["n_fuori"]} verdetti su {mu["n"]} &middot; S massimo '
      f'{fx(smax, 2)} dB &middot; LED a {it(mu["cima_deck"] * 1000, 3)} mA</td>'
      f'{verdict(mu["n_fuori"] == 0, "conforme con la cima del deck; S a 12 mA non misurato")}</tr>')
    A(f'<tr><td>V3</td><td>recupero dalla saturazione</td>'
      f'<td class="num">clipping {sg(v3["vmax"], 3)} / {sg(v3["vmin"], 3)} V &middot; '
      f'{sg(v3["jack_end"] * 1000, 2)} mV al jack a fine corsa</td>'
      '<td class="na">impaginato dal CSV, senza controllo incrociato</td></tr>')
    A(f'<tr><td>P7</td><td>corto e mute a tempo indefinito, Tj ≤ 125 °C</td>'
      f'<td class="num">Tj massima {fx(p7["tjmax"], 1)} °C &middot; {p7["n_bad"]} righe '
      'ascoltabili fuori classe A</td>'
      f'{verdict(p7["tjmax"] <= TJ_MAX and p7["n_bad"] == 0)}</tr>')
    hv = [v for v in heat["vano"] if v[1] == "peggiore" and v[0] != "all'aria"]
    hworst = max(hv, key=lambda v: v[5]) if hv else None
    if hworst:
        A(f'<tr><td>P5</td><td>60 °C nel telaio, vano chiuso, stanza a 35 °C (ADR-021, ADR-047)</td>'
          f'<td class="num">{fx(hworst[5], 1)} °C col gioco di {html_escape(hworst[0].replace(".", ","))} '
          f'&middot; {fx(heat["tot"][3], 2)} W</td>'
          f'<td class="{"ok" if hworst[5] <= TA else "no"}">stima calcolata, da confermare sul '
          'prototipo</td></tr>')
    # L42b: P9, dall'alimentatore
    sp_l = offl.get("spegnimento_l")
    if sp_l:
        okp9a = float(sp_l["picco_V"]) <= 1e-4 and (k501 or 0) >= p9["margine_ms"]
        A(f'<tr><td>P9 (a)</td><td>spegnimento morbido: V2 al jack, K501 ≥ {fx(p9["margine_ms"], 0)} ms '
          'dopo il mute (ADR-046, ADR-048)</td>'
          f'<td class="num">{spl(float(sp_l["picco_V"]))} &middot; K501 a {it(k501 or float("nan"), 3)} ms</td>'
          f'{verdict(okp9a)}</tr>')
    gv = [r for r in off["rows"]["l41c"] if r["criterio"].startswith("<= 0.002")]
    gw = max(gv, key=lambda r: float(r["picco_V"])) if gv else None
    trips = [float(today[c]["trip_after_135_ms"]) for c in ("guasto_u501", "guasto_u502")
             if today.get(c, {}).get("trip_after_135_ms")]
    vrmin = min(float(today[f"perdita_rete_{x}"]["vr_hold_ms"]) for x in ("m10", "nom", "p10")
                if today.get(f"perdita_rete_{x}", {}).get("vr_hold_ms"))
    if gw and trips:
        okp9b = (float(gw["picco_V"]) <= p9["obiettivo_mV"] * 1e-3 and max(trips) <= p9["entro_ms"]
                 and vrmin >= p9["vrelay_ms"])
        A(f'<tr><td>P9 (b)</td><td>perdita di rete e guasto: <code>MUTE_CMD</code> entro '
          f'{fx(p9["entro_ms"], 0)} ms dallo scatto, <code>VRELAY</code> ≥ {fx(p9["vrelay_ms"], 0)} ms, '
          f'al jack ≤ {fx(p9["obiettivo_mV"], 0)} mV</td>'
          f'<td class="num">scatto {sg(max(trips), 3)} ms al peggio &middot; VRELAY {it(vrmin, 4)} ms &middot; '
          f'{spl(float(gw["picco_V"]))} ({labs.get(gw["caso"], gw["caso"])})</td>'
          f'{verdict(okp9b, "conforme; tenuta di VRELAY ridotta dal carico di oggi")}</tr>')
    A(f'<tr><td>ADR-045</td><td>Δ ≥ {fx(tm["dmin"], 0)} ms qualunque cosa faccia il micro</td>'
      f'<td class="num">{it(min(t_min[k]["d"] for k in ("micro_reset", "micro_a_zero", "perdita_rete_micro_reset", "guasto_U503_micro_reset")), 4)} ms '
      'all&rsquo;angolo minimo</td>'
      f'{verdict(min(t_min[k]["d"] for k in ("micro_reset", "micro_a_zero", "perdita_rete_micro_reset", "guasto_U503_micro_reset")) >= tm["dmin"])}</tr>')
    A(f'<tr><td>NC-037</td><td>standby ≤ 0,5 W (Reg. UE 2023/826)</td>'
      f'<td class="num">{fx(t_nom["standby_mw"], 1)} mW dal secondario di T2</td>'
      '<td class="na">aperta: mancano le perdite a vuoto di T2 (giro BOM) e la misura</td></tr>')
    A('<tr><td>V4</td><td>THD/THD+N</td><td class="na">assente</td>'
      '<td class="na">non misurata in questo dossier</td></tr>')
    A('</table></div>')

    # --- 14 limiti ---
    A(h2("s14"))
    A('<ul>')
    A('<li><strong>Niente distorsione.</strong> Nessuna cifra di THD è stata misurata per '
      'questo dossier.</li>')
    if all_kf0:
        A('<li><strong>Il rumore è un pavimento.</strong> Nessun modello simulato ha '
          'rumore 1/f: le cifre di E5 sono termico e shot. NC-004 resta aperta.</li>')
    else:
        A(f'<li><strong>Il rumore è un pavimento fuori dalla coppia d&rsquo;ingresso.</strong> '
          f'Solo {", ".join(kf_parts)} porta KF; specchio, VAS e buffer sono senza 1/f. '
          'NC-004 resta aperta, ed è bloccante per G1.</li>')
    if placeholders:
        A(f'<li><strong>{len(placeholders)} dispositivi attivi su '
          f'{len(vendors) + len(placeholders)} sono segnaposto</strong> ({", ".join(placeholders)}).</li>')
    A('<li><strong>V1 agli spigoli di tolleranza</strong> non è misurato coi modelli del '
      'costruttore: gli spigoli di L16 erano un deck d&rsquo;esplorazione sui segnaposto, e non '
      'sono stati rifatti. Qui c&rsquo;è solo V1 ai valori nominali.</li>')
    A(f'<li><strong>S del mute con la cima a 12 mA</strong> (ADR-050) non è misurato: la matrice '
      f'di V2 è corsa coi LED a {it(mu["cima_deck"] * 1000, 3)} mA del deck versionato.</li>')
    A('<li><strong>Le forme d&rsquo;onda dei transitori</strong> non sono versionate, tranne la '
      'curva del livello del mute: di V2 del guadagno ci sono le finestre, della matrice del '
      'mute le analisi, di V3 il CSV.</li>')
    A('<li><strong>Il relè nella corsa dell&rsquo;interblocco</strong> è un modello dichiarato, '
      'non del costruttore: il datasheet non dà la dinamica della bobina.</li>')
    A('<li><strong>Il calore</strong> è una stima calcolata con coefficienti da letteratura, '
      'non una simulazione termica.</li>')
    A('<li><strong>L&rsquo;alimentatore è simulato con modelli dichiarati</strong>, nessuno del '
      'costruttore: regolatori e comparatori comportamentali (il modello TI del TPS7A4701 dà un '
      'punto di lavoro sbagliato, quello del TLV1701 non commuta in ngspice), micro, DAC e op-amp '
      'comportamentali, i trasformatori come Thevenin ipotetici da confermare sui pezzi. '
      '<strong>Niente PSRR né rumore dei regolatori</strong>: la quota di ADR-020 non è verificata '
      '(NC-011).</li>')
    A('<li><strong>Il carico della scheda audio sull&rsquo;alimentatore</strong> è un carico '
      'dichiarato (265 mA per rail, le bobine come resistenze senza induttanza, i LED delle LDR '
      'come diodi): la catena di L41c va dall&rsquo;alimentatore alla scheda audio, mai indietro.</li>')
    A('<li><strong>Il commento di <code>C_VRELAY</code> in <code>psu.py</code></strong> cita la '
      'tenuta di L41a, più lunga di quella del circuito di oggi (sezione della potenza).</li>')
    A('<li><strong>L&rsquo;autoriscaldamento di Q2</strong> nel pilota delle LDR non è modellato: la '
      'calibrazione è il rimedio, e la conferma è il prototipo. <code>src/main_attiny.c</code> non '
      'è scritto, e il firmware è provato sull&rsquo;host e come core del banco, non sul micro.</li>')
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
         "tb_switch_v2_counterfactual.cir", "tb_v3_overload.cir", "tb_mute_corto.cir",
         "tb_e4_uscite.cir"]


def main():
    standalone = None
    if "--standalone" in sys.argv:
        standalone = sys.argv[sys.argv.index("--standalone") + 1]

    M = {"resp": measure_response(), "v1": measure_v1(),
         "psrr": measure_psrr(), "noise": measure_noise(), "trim": measure_trim(),
         "cf": measure_counterfactual(), "v2": measure_v2(), "v3": measure_v3(),
         "p7": measure_p7(), "op": measure_oppoint(),
         "mute": measure_mute(), "il": measure_interlock(), "ldr": measure_ldr_e3e5()}
    M["z"] = measure_zout(M["resp"])
    M["e4"] = measure_e4(M["z"])
    M["hr"] = measure_headroom(M["trim"])
    M["heat"] = measure_heat(M["op"])
    M["l40"] = measure_l40(DECKS)
    # L42b: l'alimentatore
    M.update({"pw": measure_psu_power(), "sv": measure_supervisor(), "tm": measure_timer(),
              "fw": measure_fw(), "ld": measure_ldr_drive(), "off": measure_shutdown(),
              "p9": p9_soglie()})
    M["decks"] = ([os.path.join(TB, d) for d in DECKS]
                  + [os.path.join(TB, "tb_v2_casopeggiore.cir"),
                     os.path.join(L29D2, "deck", "tb_v2_l29d2.cir"),
                     os.path.join(L41B2, "e3_e5", "tb_e3_e5_ldr_cima12mA.cir")])
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
        "fig_mute.svg": fig_mute(M["mute"]),
        "fig_ldr_drive.svg": fig_ldr_drive(M["ld"]),
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

    v1, hr, trim, mu, ldr = M["v1"], M["hr"], M["trim"], M["mute"], M["ldr"]
    summary = {
        "dati": [rel(L42), rel(L42M), rel(mu["mat_dir"]), rel(mu["src_dir"]), rel(ldr["dir"]),
                 rel(M["il"]["corsa_dir"]), rel(M["heat"]["dir"])],
        "controlli_incrociati": "tutti superati",
        "seconda_corsa_L40": {"deck": len(M["l40"]["decks"]), "righe": M["l40"]["n_res"],
                              "tabelle": M["l40"]["n_tab"]},
        "guadagno_1kHz_dB": {m: M["resp"][(m, "1.5")]["g1k"] for m in MODES},
        "adr014_scarto_20kHz_rif_1kHz_dB_peggiore": max(adr014(M["resp"])[0].values(), key=abs),
        "v1_minimo_gradi": v1["min"],
        "v1_minimo_per_istanza_gradi": {html_escape(k).replace("&amp;middot;", "·")
                                        .replace("&amp;minus;", "−"): x for k, x in v1["inst"]},
        "headroom_nc009_M1_dB_10db_trim_-6": hr["modes"]["10db"]["trim"]["6"]["M1"],
        "headroom_nc009_M1_dB_10db_trim_0": hr["modes"]["10db"]["trim"]["0"]["M1"],
        "trim_attenuazione_dB": {p: trim["att"][p] for p in ("0", "6", "12")},
        "e3_min_zin_ohm": min(trim["e3min"], ldr["e3min"]),
        "e5_catena_peggiore_uV": max(trim["e5max"], ldr["e5max"]),
        "v2_mute_verdetti": {"totale": mu["n"], "fuori": mu["n_fuori"]},
        "v2_mute_S_curva_dB": mu["prof"]["S"],
        "v2_mute_cima_led_deck_A": mu["cima_deck"],
        "interblocco_corsa_cadute_al_rilascio": {k: v["ril"] for k, v in M["il"]["corsa"].items()},
        "calore_totale_W": {"nominale": M["heat"]["tot"][1], "massimo": M["heat"]["tot"][3]},
        "psrr_peggiore_10kHz_dB": min(r["p10k"] for r in M["psrr"].values()),
        "zout_jack_1kHz_ohm_0db": M["z"]["0db"]["z1k"],
        "e4_rez_max_ohm": {f'{g["out"]} {"+".join(g["modes"])}': g["zrmax_max"]
                           for g in M["e4"]["groups"]},
        "e4_dispersione_volume_ohm": max(g["disp"] for g in M["e4"]["groups"]),
        "p7_tj_massima_C": M["p7"]["tjmax"],
        # L42b: l'alimentatore
        "alimentatore_dati": [rel(L42B), rel(L42B_C), rel(L42B_B2), rel(L41B1), rel(L41B2),
                              rel(L41C), rel(L30)],
        "psu_tenuta_vrelay_ms": {f: float(M["pw"]["oggi"][f"perdita_rete_{f}"]["vr_hold_ms"])
                                 for f in ("m10", "nom", "p10")},
        "psu_tenuta_vrelay_ms_L41a": {f: float(M["pw"]["old"][f"perdita_rete_{f}"]["vr_hold_ms"])
                                      for f in ("m10", "nom", "p10")},
        "psu_scarti_da_L41a": len(M["pw"]["scarti"]),
        "delta_ms_angolo_minimo_micro_reset": M["tm"]["t"]["min"]["micro_reset"]["d"],
        "standby_mW_da_T2": M["tm"]["t"]["nom"]["standby_mw"],
        "firmware_sequenze": {r["caso"]: f'{r["ok"]} su {r["n"]}' for r in M["fw"]["rows"]},
        "firmware_falsi_host": M["fw"]["falsi"],
        "ldr_calibrato_peggiore_dB": M["ld"]["w_cal"][0],
        "jack_L41c_V": {r["caso"]: float(r["picco_V"]) for r in M["off"]["rows"]["l41c"]
                        if r["picco_V"] not in ("-", "")},
    }
    with open(os.path.join(HERE, "dossier.summary.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("   scritto dossier.summary.json")
    print("OK: tutti i controlli incrociati sono passati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
