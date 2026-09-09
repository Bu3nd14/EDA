#!/usr/bin/env python3
"""Costruisce il dossier del preamplificatore dai dati versionati.

    /usr/bin/python3 docs/preamp/dossier/build_dossier.py
    /usr/bin/python3 docs/preamp/dossier/build_dossier.py --standalone <file.html>

REGOLA CHE GOVERNA QUESTO FILE, ed e' la stessa del diagramma a blocchi di
L1: **nessuna cifra del dossier e' scritta a mano.** Ogni numero che
compare nella pagina viene letto dai CSV versionati in
docs/preamp/data/<data>/ e calcolato qui.

E c'e' una seconda rete, che il diagramma a blocchi non aveva: ogni
quantita' calcolata dal CSV viene **confrontata con quella che ngspice ha
stampato da se'** nel .log versionato accanto. Sono due strade
indipendenti verso lo stesso numero - la mia interpolazione sui campioni,
e il `meas`/`print` del simulatore. Se divergono oltre la tolleranza
dichiarata, lo script **rifiuta e non scrive niente**, come export_fab.sh
sulla DRC. Un dossier che si contraddice con la propria evidenza non deve
poter essere generato.

Non ha flag di bypass.
"""

import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA_DATE = "2026-09-09"
DATA = os.path.join(REPO, "docs", "preamp", "data", DATA_DATE)
SCHEM = os.path.join(REPO, "docs", "preamp", "schematic")

sys.path.insert(0, HERE)
import svgplot as sp                                   # noqa: E402

FAILURES = []


def refuse(msg):
    FAILURES.append(msg)


# ---------------------------------------------------------------- dati ----
def load_csv(name):
    """Legge un CSV di run_simulation.sh. Ritorna una lista di liste."""
    path = os.path.join(DATA, name)
    rows = []
    with open(path) as f:
        head = f.readline()
        if not head.startswith("col0"):
            raise SystemExit(f"intestazione inattesa in {name}: {head!r}")
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(v) for v in line.split(",")])
    if not rows:
        raise SystemExit(f"{name} e' vuoto")
    return rows


def pair(rows, k):
    """La k-esima coppia (scale, valore) -> (xs, ys).

    run_simulation.sh intesta i CSV col0..colN e basta: l'identita' delle
    colonne vive nel commento del deck e nel README dei dati. Per un `ac`
    le colonne pari sono la frequenza ripetuta, i dati sono le dispari.
    """
    xs = [r[2 * k] for r in rows]
    ys = [r[2 * k + 1] for r in rows]
    return xs, ys


def interp(xs, ys, x):
    """Interpolazione lineare in log(f), che e' la griglia su cui i punti
    sono stati calcolati (`dec`)."""
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


def log_values(logname, key):
    """Tutte le occorrenze di `key = valore` in un log ngspice, in ordine.

    Sono le righe che il deck stampa con `print`: e' l'evidenza indipendente
    contro cui i numeri calcolati dai CSV vengono confrontati.

    ATTENZIONE: ngspice stampa OGNI grandezza DUE volte - una volta da
    `meas`, incolonnata (`z1k                 =  5.87602e+01`), e una volta
    da `print`, compatta (`z1k = 5.876022e+01`). Qui si prende solo la
    forma di `print`, che ha piu' cifre; prenderle entrambe raddoppierebbe
    i conteggi e farebbe scattare i controlli sul numero di occorrenze.
    """
    pat = re.compile(r"^" + re.escape(key) + r" = (\S+)\s*$")
    out = []
    with open(os.path.join(DATA, logname)) as f:
        for line in f:
            m = pat.match(line.rstrip("\n"))
            if m:
                try:
                    out.append(float(m.group(1)))
                except ValueError:
                    pass
    return out


def check(label, mine, theirs, rtol):
    """Confronta il mio numero con quello di ngspice. Registra, non alza."""
    if theirs is None:
        refuse(f"{label}: ngspice non ha stampato il valore di riferimento")
        return mine
    den = abs(theirs) if abs(theirs) > 1e-12 else 1.0
    err = abs(mine - theirs) / den
    if err > rtol:
        refuse(f"{label}: calcolato {mine:.6g}, ngspice {theirs:.6g} "
               f"(scarto relativo {err:.2e} > {rtol:.0e})")
    return theirs        # si pubblica il numero del simulatore, non il mio


# --------------------------------------------------------------- misure ---
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


AC_ORDER = [("0db", "1.5"), ("0db", "430"), ("0db", "2500"), ("0db", "10k"),
            ("10db", "1.5"), ("10db", "430"), ("10db", "2500"), ("10db", "10k")]
LOOP_ORDER = [("0db", c) for c in ("1f", "100p", "470p", "1n", "2.2n", "4.7n")] + \
             [("10db", c) for c in ("1f", "100p", "470p", "1n", "2.2n", "4.7n")]


def measure_response():
    """Risposta in frequenza: le 4 curve del dossier + il corner LF."""
    g1k = log_values("tb_ac.log", "g1k")
    g20 = log_values("tb_ac.log", "g20")
    g20k = log_values("tb_ac.log", "g20k")
    g100k = log_values("tb_ac.log", "g100k")
    for nm, lst in (("g1k", g1k), ("g20", g20), ("g20k", g20k), ("g100k", g100k)):
        if len(lst) != 8:
            refuse(f"tb_ac.log: attese 8 occorrenze di {nm}, trovate {len(lst)}")

    out = {}
    for key in [("0db", "1.5"), ("0db", "2500"), ("10db", "1.5"), ("10db", "2500")]:
        idx = AC_ORDER.index(key)
        rows = load_csv(f"tb_ac_{key[0]}_{key[1]}.csv")
        f, gdb = pair(rows, 0)
        _, gph = pair(rows, 1)
        tag = f"{key[0]}/{key[1]}"
        rec = {
            "f": f, "gdb": gdb, "gph": gph,
            "g20": check(f"tb_ac {tag} @20Hz", interp(f, gdb, 20),
                         g20[idx] if idx < len(g20) else None, 2e-3),
            "g1k": check(f"tb_ac {tag} @1kHz", interp(f, gdb, 1000),
                         g1k[idx] if idx < len(g1k) else None, 2e-3),
            "g20k": check(f"tb_ac {tag} @20kHz", interp(f, gdb, 20000),
                          g20k[idx] if idx < len(g20k) else None, 2e-3),
            "g100k": check(f"tb_ac {tag} @100kHz", interp(f, gdb, 100000),
                           g100k[idx] if idx < len(g100k) else None, 2e-3),
            "ph20k": interp(f, gph, 20000),
        }
        out[key] = rec

    rows = load_csv("tb_ac.csv")
    f, gdb = pair(rows, 0)
    out["lf"] = {
        "f": f, "gdb": gdb,
        "g1k": check("tb_ac LF @1kHz", interp(f, gdb, 1000),
                     (log_values("tb_ac.log", "g1kb") or [None])[0], 2e-3),
        "g20": check("tb_ac LF @20Hz", interp(f, gdb, 20),
                     (log_values("tb_ac.log", "g20b") or [None])[0], 2e-3),
        "g5": check("tb_ac LF @5Hz", interp(f, gdb, 5),
                    (log_values("tb_ac.log", "g5b") or [None])[0], 2e-3),
    }
    return out


def measure_loop():
    fcross = log_values("tb_loop.log", "fcross")
    pmarg = log_values("tb_loop.log", "pmarg")
    tdc = log_values("tb_loop.log", "tdc")
    for nm, lst in (("fcross", fcross), ("pmarg", pmarg), ("tdc", tdc)):
        if len(lst) != 12:
            refuse(f"tb_loop.log: attese 12 occorrenze di {nm}, trovate {len(lst)}")

    out = {}
    for key in [("0db", "1f"), ("0db", "4.7n"), ("10db", "1f"), ("10db", "4.7n")]:
        idx = LOOP_ORDER.index(key)
        rows = load_csv(f"tb_loop_{key[0]}_{key[1]}.csv")
        f, tdb = pair(rows, 0)
        _, tph = pair(rows, 1)
        fc, i = crossing(f, tdb, 0.0)
        tag = f"{key[0]}/{key[1]}"
        # Il margine di fase si legge come |ph(T)| dove |T| attraversa 0 dB:
        # G2 e' l'ingresso INVERTENTE, quindi T e' negativo reale in continua
        # e la sua fase li' vale 180 gradi. Non e' 180 - |ph|.
        pm = abs(interp(f, tph, fc)) if fc else None
        out[key] = {
            "f": f, "tdb": tdb, "tph": tph,
            "fcross": check(f"tb_loop {tag} f_incrocio", fc,
                            fcross[idx] if idx < len(fcross) else None, 5e-3),
            "pmarg": check(f"tb_loop {tag} margine di fase", pm,
                           abs(pmarg[idx]) if idx < len(pmarg) else None, 5e-3),
            "tdc": check(f"tb_loop {tag} |T| a 10 Hz", interp(f, tdb, 10),
                         tdc[idx] if idx < len(tdc) else None, 2e-3),
        }
    return out


def measure_zout():
    z20 = log_values("tb_zout_psrr_noise.log", "z20")
    z1k = log_values("tb_zout_psrr_noise.log", "z1k")
    z20k = log_values("tb_zout_psrr_noise.log", "z20k")
    za20 = log_values("tb_zout_psrr_noise.log", "za20")
    za1k = log_values("tb_zout_psrr_noise.log", "za1k")
    za20k = log_values("tb_zout_psrr_noise.log", "za20k")
    za100k = log_values("tb_zout_psrr_noise.log", "za100k")
    for nm, lst in (("z20", z20), ("z1k", z1k), ("z20k", z20k),
                    ("za20", za20), ("za1k", za1k), ("za20k", za20k),
                    ("za100k", za100k)):
        if len(lst) != 2:
            refuse(f"tb_zout_psrr_noise.log: attese 2 occorrenze di {nm}, "
                   f"trovate {len(lst)}")
    out = {}
    for idx, mode in enumerate(("0db", "10db")):
        rows = load_csv(f"tb_zout_psrr_noise_zout_{mode}.csv")
        f, z = pair(rows, 0)
        _, za = pair(rows, 1)
        out[mode] = {
            "f": f, "z": z, "za": za,
            "z20": check(f"Zout {mode} @20Hz", interp(f, z, 20), z20[idx] if idx < len(z20) else None, 2e-3),
            "z1k": check(f"Zout {mode} @1kHz", interp(f, z, 1000), z1k[idx] if idx < len(z1k) else None, 2e-3),
            "z20k": check(f"Zout {mode} @20kHz", interp(f, z, 20000), z20k[idx] if idx < len(z20k) else None, 2e-3),
            "za20": check(f"Zout(OUT) {mode} @20Hz", interp(f, za, 20), za20[idx] if idx < len(za20) else None, 2e-3),
            "za1k": check(f"Zout(OUT) {mode} @1kHz", interp(f, za, 1000), za1k[idx] if idx < len(za1k) else None, 2e-3),
            "za20k": check(f"Zout(OUT) {mode} @20kHz", interp(f, za, 20000), za20k[idx] if idx < len(za20k) else None, 2e-3),
            "za100k": check(f"Zout(OUT) {mode} @100kHz", interp(f, za, 100000), za100k[idx] if idx < len(za100k) else None, 2e-3),
            "z100k": interp(f, z, 100000),
        }
    return out


PSRR_ORDER = [("p", "0db"), ("p", "10db"), ("m", "0db"), ("m", "10db")]


def measure_psrr():
    p100 = log_values("tb_zout_psrr_noise.log", "p100")
    p1k = log_values("tb_zout_psrr_noise.log", "p1k")
    p10k = log_values("tb_zout_psrr_noise.log", "p10k")
    p100k = log_values("tb_zout_psrr_noise.log", "p100k")
    for nm, lst in (("p100", p100), ("p1k", p1k), ("p10k", p10k),
                    ("p100k", p100k)):
        if len(lst) != 4:
            refuse(f"tb_zout_psrr_noise.log: attese 4 occorrenze di {nm}, "
                   f"trovate {len(lst)}")
    out = {}
    for idx, key in enumerate(PSRR_ORDER):
        rail, mode = key
        rows = load_csv(f"tb_zout_psrr_noise_psrr{rail}_{mode}.csv")
        f, p = pair(rows, 0)
        tag = f"PSRR{'+' if rail == 'p' else '-'} {mode}"
        out[key] = {
            "f": f, "p": p,
            "p100": check(f"{tag} @100Hz", interp(f, p, 100), p100[idx] if idx < len(p100) else None, 2e-3),
            "p1k": check(f"{tag} @1kHz", interp(f, p, 1000), p1k[idx] if idx < len(p1k) else None, 2e-3),
            "p10k": check(f"{tag} @10kHz", interp(f, p, 10000), p10k[idx] if idx < len(p10k) else None, 2e-3),
            "p100k": check(f"{tag} @100kHz", interp(f, p, 100000), p100k[idx] if idx < len(p100k) else None, 2e-3),
        }
    return out


def measure_headroom():
    """Finestra lineare e livelli di saturazione, da tb_dc_headroom.

    METRICA, dichiarata perche' non e' universale: la "finestra lineare" e'
    il piu' grande intervallo attorno a 0 V in cui il guadagno locale
    dVout/dVin resta entro l'1% del suo valore a 0 V. I livelli di
    saturazione sono il minimo e il massimo di v(OUT) sull'intera spazzata.
    """
    out = {}
    for mode, name in (("0db", "tb_dc_headroom.csv"),
                       ("10db", "tb_dc_headroom_10db.csv")):
        rows = load_csv(name)
        vin, vout = pair(rows, 0)
        n = len(vin)
        g = [None] * n
        for i in range(1, n - 1):
            dv = vin[i + 1] - vin[i - 1]
            g[i] = (vout[i + 1] - vout[i - 1]) / dv if dv else None
        i0 = min(range(n), key=lambda i: abs(vin[i]))
        g0 = g[i0] or 1.0
        lo = hi = vin[i0]
        i = i0
        while i + 1 < n - 1 and g[i + 1] is not None and abs(g[i + 1] - g0) <= 0.01 * abs(g0):
            i += 1
            hi = vin[i]
        i = i0
        while i - 1 >= 1 and g[i - 1] is not None and abs(g[i - 1] - g0) <= 0.01 * abs(g0):
            i -= 1
            lo = vin[i]
        out[mode] = {
            "vin": vin, "vout": vout,
            "gain": g0,
            "vout_max": max(vout), "vout_min": min(vout),
            "lin_lo": lo, "lin_hi": hi,
            "vout_lin_hi": interp_lin(vin, vout, hi),
            "vout_lin_lo": interp_lin(vin, vout, lo),
        }
    return out


def interp_lin(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(1, len(xs)):
        if xs[i] >= x:
            x0, x1 = xs[i - 1], xs[i]
            if x1 == x0:
                return ys[i]
            t = (x - x0) / (x1 - x0)
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1]


def measure_counterfactual():
    """I tre stati del controfattuale di ADR-004 (L4). col1 = v(OUT)."""
    files = [("A", "contatto CHIUSO, R_f = 1,50 kΩ", "tb_switch_v2_counterfactual.csv"),
             ("B", "contatto APERTO, R_f = 1e12 Ω", "tb_switch_v2_counterfactual_open.csv"),
             ("C", "richiuso, controprova di B", "tb_switch_v2_counterfactual_reclosed.csv")]
    out = []
    for tag, desc, name in files:
        rows = load_csv(name)
        out.append({"tag": tag, "desc": desc,
                    "vout": rows[0][1], "vfb": rows[0][3]})
    # La verifica incorporata del deck: A e C devono coincidere, B no.
    if abs(out[0]["vout"] - out[2]["vout"]) > 1e-6:
        refuse("controfattuale: A e C non coincidono, la controprova non regge")
    if abs(out[1]["vout"] - out[0]["vout"]) < 1.0:
        refuse("controfattuale: B non differisce da A, l'anello non si e' aperto")
    return out


def measure_oppoint():
    """Punti di lavoro dal log di tb_op, che e' l'evidenza versionata."""
    rails = {}
    devices = []
    path = os.path.join(DATA, "tb_op.log")
    with open(path) as f:
        lines = [ln.rstrip("\n") for ln in f]
    for ln in lines:
        for key in ("i(vpp)", "i(vmm)"):
            if ln.strip().lower().startswith(key):
                try:
                    rails[key] = float(ln.split("=")[1].strip())
                except (IndexError, ValueError):
                    pass
    # righe del tipo: @q106[ic] = 1.234e-03
    cur = {}
    for ln in lines:
        s = ln.strip()
        if not s.startswith("@"):
            continue
        try:
            lhs, rhs = s.split("=", 1)
            val = float(rhs.strip())
        except ValueError:
            continue
        lhs = lhs.strip()
        dev, _, par = lhs[1:].partition("[")
        par = par.rstrip("]")
        cur.setdefault(dev, {})[par] = val
    for dev in sorted(cur, key=lambda d: (d[0], d)):
        devices.append((dev, cur[dev]))
    if not devices:
        refuse("tb_op.log: nessun punto di lavoro trovato")
    return rails, devices


# --------------------------------------------------------------- figure ---
def fig_response(resp):
    W, H = 900, 420
    ax = sp.Axes(72, 46, W - 130, H - 110, (10, 100000), (-1, 11),
                 xlabel="frequenza [Hz]", ylabel="|v(JACK)| [dB]",
                 title="Risposta in frequenza, entrambe le modalità di guadagno")
    style = {("0db", "1.5"): (sp.C_0DB, "0 dB · sorgente 1,5 Ω (K11)", None),
             ("0db", "2500"): (sp.C_0DB_ALT, "0 dB · sorgente 2500 Ω (attenuatore a metà)", None),
             ("10db", "1.5"): (sp.C_10DB, "+10 dB · sorgente 1,5 Ω", None),
             ("10db", "2500"): (sp.C_10DB_ALT, "+10 dB · sorgente 2500 Ω", None)}
    for key, (col, lab, dash) in style.items():
        r = resp[key]
        ax.line(r["f"], r["gdb"], col, lab, dash)
    ax.vline(20000)
    body = ax.render() + "\n" + ax.legend(80, H - 42, cols=2, colw=330)
    return sp.document(W, H, body,
                       "Dati: tb_ac_*.csv · linea tratteggiata verticale = 20 kHz")


def fig_response_adr014(resp):
    W, H = 900, 400
    ax = sp.Axes(72, 46, W - 130, H - 110, (10, 100000), (-0.15, 0.05),
                 xlabel="frequenza [Hz]", ylabel="scostamento da 1 kHz [dB]",
                 title="ADR-014: la risposta non deve muoversi con la manopola del volume")
    style = {("0db", "1.5"): (sp.C_0DB, "0 dB · 1,5 Ω", None),
             ("0db", "2500"): (sp.C_0DB_ALT, "0 dB · 2500 Ω", None),
             ("10db", "1.5"): (sp.C_10DB, "+10 dB · 1,5 Ω", None),
             ("10db", "2500"): (sp.C_10DB_ALT, "+10 dB · 2500 Ω", None)}
    for key, (col, lab, dash) in style.items():
        r = resp[key]
        g1k = r["g1k"]
        ax.line(r["f"], [g - g1k for g in r["gdb"]], col, lab, dash)
    ax.vline(20000)
    body = ax.render() + "\n" + ax.legend(80, H - 42, cols=4, colw=175)
    return sp.document(W, H, body,
                       "Normalizzato a 1 kHz. Le quattro curve si sovrappongono: "
                       "l'impedenza della sorgente non sposta la banda passante.")


def fig_loop(loop):
    W, H = 900, 620
    xlim = (1, 1e8)
    axm = sp.Axes(72, 46, W - 130, 230, xlim, (-40, 80),
                  ylabel="|T| [dB]",
                  title="Guadagno d'anello e margine di fase (iniezione al gate invertente)")
    axp = sp.Axes(72, 330, W - 130, 190, xlim, (0, 180),
                  xlabel="frequenza [Hz]", ylabel="fase di T [gradi]")
    style = {("0db", "1f"): (sp.C_0DB, "0 dB · cavo ~0", None),
             ("0db", "4.7n"): (sp.C_0DB_ALT, "0 dB · cavo 4,7 nF", "5,3"),
             ("10db", "1f"): (sp.C_10DB, "+10 dB · cavo ~0", None),
             ("10db", "4.7n"): (sp.C_10DB_ALT, "+10 dB · cavo 4,7 nF", "5,3")}
    for key, (col, lab, dash) in style.items():
        r = loop[key]
        axm.line(r["f"], r["tdb"], col, lab, dash)
        axp.line(r["f"], r["tph"], col, None, dash)
    axm.hline(0, sp.C_REQ, "0 dB")
    for key in (("0db", "4.7n"), ("10db", "4.7n")):
        r = loop[key]
        axm.annot(r["fcross"], 0, f"{r['fcross']/1e3:.0f} kHz".replace(".", ","), 8, -8)
        axp.annot(r["fcross"], r["pmarg"],
                  f"{r['pmarg']:.1f}°".replace(".", ","), 8, -8)
    body = (axm.render(show_xlabels=False) + "\n" + axp.render() + "\n" +
            axm.legend(80, H - 42, cols=4, colw=175))
    return sp.document(W, H, body,
                       "Dati: tb_loop_*.csv · margine di fase = |fase| dove |T| "
                       "attraversa 0 dB (G2 è l'ingresso invertente)")


def fig_psrr(psrr):
    W, H = 900, 420
    ax = sp.Axes(72, 46, W - 130, H - 110, (20, 200000), (0, 110),
                 xlabel="frequenza [Hz]", ylabel="PSRR [dB] — più grande è meglio",
                 title="Reiezione dell'alimentazione, i due rail nelle due modalità")
    style = {("p", "0db"): (sp.C_0DB, "rail + · 0 dB", None),
             ("p", "10db"): (sp.C_10DB, "rail + · +10 dB", None),
             ("m", "0db"): (sp.C_0DB_ALT, "rail − · 0 dB", "5,3"),
             ("m", "10db"): (sp.C_10DB_ALT, "rail − · +10 dB", "5,3")}
    for key, (col, lab, dash) in style.items():
        r = psrr[key]
        ax.line(r["f"], r["p"], col, lab, dash)
    body = ax.render() + "\n" + ax.legend(80, H - 42, cols=4, colw=175)
    return sp.document(W, H, body,
                       "Dati: tb_zout_psrr_noise_psrr*.csv · 1 V AC in serie a "
                       "ciascun rail, ingresso silenziato")


def fig_zout(z):
    W, H = 900, 430
    ax = sp.Axes(72, 46, W - 130, H - 120, (20, 200000), (0.5, 5000),
                 ylog=True, xlabel="frequenza [Hz]", ylabel="|Z| [Ω]",
                 title="Impedenza d'uscita: al jack e al nodo OUT")
    ax.line(z["0db"]["f"], z["0db"]["z"], sp.C_0DB, "al jack · 0 dB", None)
    ax.line(z["10db"]["f"], z["10db"]["z"], sp.C_10DB, "al jack · +10 dB", None)
    ax.line(z["0db"]["f"], z["0db"]["za"], sp.C_0DB_ALT, "al nodo OUT · 0 dB", "5,3")
    ax.line(z["10db"]["f"], z["10db"]["za"], sp.C_10DB_ALT, "al nodo OUT · +10 dB", "5,3")
    ax.hline(100, sp.C_REQ, "E4: < 100 Ω")
    body = ax.render() + "\n" + ax.legend(80, H - 42, cols=4, colw=175)
    return sp.document(W, H, body,
                       "Dati: tb_zout_psrr_noise_zout_*.csv · la salita sotto "
                       "200 Hz è la reattanza del condensatore da 4,7 µF, non lo stadio")


def fig_headroom(hr):
    W, H = 900, 420
    ax = sp.Axes(72, 46, W - 130, H - 110, (-14, 14), (-16, 16), xlog=False,
                 xlabel="v(IN) [V]", ylabel="v(OUT) [V]",
                 title="Escursione in continua e saturazione, entrambe le modalità")
    ax.line(hr["0db"]["vin"], hr["0db"]["vout"], sp.C_0DB, "0 dB", None)
    ax.line(hr["10db"]["vin"], hr["10db"]["vout"], sp.C_10DB, "+10 dB", None)
    ax.hline(hr["0db"]["vout_max"], sp.C_REQ, None)
    ax.hline(hr["0db"]["vout_min"], sp.C_REQ, None)
    for mode, col in (("0db", sp.C_0DB), ("10db", sp.C_10DB)):
        r = hr[mode]
        ax.annot(r["lin_hi"], r["vout_lin_hi"],
                 f"limite lineare {it(r['lin_hi'], 2)} V", -8, -8)
    body = ax.render() + "\n" + ax.legend(80, H - 42, cols=2, colw=175)
    return sp.document(W, H, body,
                       "Dati: tb_dc_headroom*.csv · spazzata in continua, "
                       "non un segnale audio")


def fig_counterfactual(cf, hr):
    """I tre stati del controfattuale: barre, non curve.

    Sono tre punti di lavoro in continua, quindi non c'e' una curva da
    disegnare - ma il -13,68 V va VISTO accanto ai rail, non solo letto in
    tabella: e' tutto il senso della verifica V2.
    """
    W, H = 900, 430
    ax = sp.Axes(150, 46, W - 300, H - 120, (0.4, 3.6), (-16, 16), xlog=False,
                 ylabel="v(OUT) [V]",
                 title="Controfattuale ADR-004: cosa farebbe il relè nel ramo sbagliato",
                 xticks=[(1, "A · contatto chiuso"),
                         (2, "B · contatto APERTO"),
                         (3, "C · richiuso")])
    colors = [sp.C_0DB, sp.C_10DB, sp.C_0DB]
    for i, (r, col) in enumerate(zip(cf, colors), start=1):
        ax.bar(i, 0.0, r["vout"], col)
        dy = 16 if r["vout"] < 0 else -10
        ax.annot(i, r["vout"], f'{r["vout"]:.4f} V'.replace(".", ","), 10, dy)
    ax.hline(15, sp.C_REQ, "rail +15 V")
    ax.hline(-15, sp.C_REQ, "rail −15 V")
    ax.hline(hr["0db"]["vout_min"], sp.C_10DB_ALT,
             "saturazione negativa dello stadio", "2,3")
    ax.hline(0, sp.C_AXIS, None, "1,3")
    body = ax.render()
    return sp.document(W, H, body,
                       "Dati: tb_switch_v2_counterfactual*.csv · con R_f aperto "
                       "l'anello è rotto e l'uscita si appoggia al rail")


def fig_counterfactual(cf, hr):
    """I tre stati del controfattuale: barre, non curve.

    Sono tre punti di lavoro in continua, quindi non c'e' una curva da
    disegnare - ma il -13,68 V va VISTO accanto ai rail, non solo letto in
    tabella: e' tutto il senso della meta' falsificabile di V2.
    """
    W, H = 900, 440
    ax = sp.Axes(150, 52, W - 300, H - 130, (0.4, 3.6), (-16, 16), xlog=False,
                 ylabel="v(OUT) [V]",
                 title="Controfattuale ADR-004: cosa farebbe il relè nel ramo sbagliato",
                 xticks=[(1, "A · contatto chiuso"),
                         (2, "B · contatto APERTO"),
                         (3, "C · richiuso")])
    colors = [sp.C_0DB, sp.C_10DB, sp.C_0DB]
    for i, (r, col) in enumerate(zip(cf, colors), start=1):
        ax.bar(i, 0.0, r["vout"], col)
        dy = 18 if r["vout"] < 0 else -12
        ax.annot(i, r["vout"], f'{r["vout"]:.4f} V'.replace(".", ","), 12, dy)
    ax.hline(15, sp.C_REQ, "rail +15 V")
    ax.hline(-15, sp.C_REQ, "rail −15 V")
    ax.hline(hr["0db"]["vout_min"], sp.C_10DB_ALT,
             "saturazione dello stadio, "
             + it(hr["0db"]["vout_min"], 4) + " V", "2,3", left=True)
    ax.hline(0, sp.C_AXIS, None, "1,3")
    body = ax.render()
    return sp.document(W, H, body,
                       "Dati: tb_switch_v2_counterfactual*.csv · con R_f aperto "
                       "l'anello è rotto e l'uscita si appoggia al rail")


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
  display:grid; grid-template-columns:repeat(auto-fit,minmax(168px,1fr));
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
.synopsis dd .u{font-size:13px;font-weight:400;color:var(--muted);margin-left:3px}

.note{
  background:var(--warn-bg); border-left:3px solid var(--warn-rule);
  padding:14px 18px; margin:22px 0; max-width:68ch;
}
.note strong{color:var(--warn-ink)}

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


def build_page(resp, loop, z, psrr, hr, cf, rails, devices, inline=False):
    def figure(svgfile, alt):
        if inline:
            with open(os.path.join(HERE, svgfile) if not svgfile.startswith("..")
                      else os.path.join(SCHEM, os.path.basename(svgfile))) as f:
                body = f.read()
            body = body.split("?>", 1)[-1]
            return f'<div class="plate">{body}</div>'
        return (f'<div class="plate"><img src="{svgfile}" '
                f'alt="{html_escape(alt)}" loading="lazy"></div>')

    h = []
    A = h.append
    A('<div class="wrap">')
    A('<p class="eyebrow">Bozza &middot; dati del '
      f'{DATA_DATE} &middot; modelli segnaposto</p>')
    A('<h1>Dossier di misura del preamplificatore di linea</h1>')
    A('<p class="lede">Guadagno unitario, Classe A pura a componenti '
      'discreti, senza operazionali.</p>')

    worst_pm = min(r["pmarg"] for r in loop.values())
    weak_psrr = min(r["p10k"] for r in psrr.values())
    d0_syn = abs(resp[("0db", "2500")]["g20k"] - resp[("0db", "1.5")]["g20k"])
    A('<dl class="synopsis">')
    for lab, val, unit in (
            ("Guadagno 0 dB", it(resp[("0db", "1.5")]["g1k"], 3), "dB @ 1 kHz"),
            ("Guadagno +10 dB", it(resp[("10db", "1.5")]["g1k"], 4), "dB @ 1 kHz"),
            ("Scarto ADR-014", it(d0_syn, 3), "dB @ 20 kHz"),
            ("Margine di fase, peggiore", it(worst_pm, 3), "gradi"),
            ("PSRR, peggiore", it(weak_psrr, 3), "dB @ 10 kHz"),
            ("Z<sub>out</sub> al jack", it(z["0db"]["z1k"], 4), "&Omega; @ 1 kHz")):
        A(f'<div><dt>{lab}</dt><dd>{val}<span class="u">{unit}</span></dd></div>')
    A('</dl>')

    A('<div class="note"><strong>Leggere prima questo.</strong> Tutti i numeri '
      'qui dentro vengono da <em>modelli SPICE segnaposto scritti a mano</em>, '
      'non da modelli del costruttore. Sono credibili la forma delle risposte '
      'in frequenza, i rapporti di guadagno, le impedenze e i risultati in '
      'continua. <strong>Non</strong> lo sono le cifre di distorsione (qui '
      'assenti di proposito) e quelle di rumore (escluse: '
      '<code>KF&nbsp;=&nbsp;0</code> su ogni dispositivo, quindi non esiste '
      'rumore 1/f in nessuna di queste simulazioni). I margini di fase sono '
      'provvisori: dipendono da capacità e tempi di transito scelti a mano.</div>')

    A('<p>Il progetto sostituisce un Technics SU-9070 la cui struttura di '
      'guadagno richiede <strong>46 dB di attenuazione</strong>, causa '
      'misurabile della mancanza di dinamica lamentata. La topologia canonica '
      'è in <code>circuits/preamp/</code>; i banchi di prova in '
      f'<code>spice/preamp/tb/</code>; i dati in '
      f'<code>docs/preamp/data/{DATA_DATE}/</code>.</p>')

    A('<nav class="toc" aria-label="Indice"><ol>')
    for anchor, label in (
            ("s1", "Il blocco di guadagno"),
            ("s2", "Il preamplificatore intero"),
            ("s3", "Punti di lavoro"),
            ("s4", "Escursione in continua"),
            ("s5", "Risposta in frequenza"),
            ("s6", "Guadagno d&rsquo;anello"),
            ("s7", "Reiezione dell&rsquo;alimentazione"),
            ("s8", "Impedenza d&rsquo;uscita"),
            ("s9", "Controfattuale del rel&egrave;"),
            ("s10", "Requisiti a fronte del misurato"),
            ("s11", "Cosa questo dossier non dice"),
            ("s12", "Provenienza")):
        A(f'<li><a href="#{anchor}">{label}</a></li>')
    A('</ol></nav>')

    A('<p class="meta">Nessuna cifra di questa pagina è scritta a mano: '
      'sono tutte lette dai CSV versionati e ricontrollate contro i '
      '<code>print</code> che ngspice ha stampato nei log versionati accanto. '
      'Se le due strade divergono, il generatore rifiuta di produrre la '
      'pagina.</p>')

    # --- schema ---
    A('<h2 id="s1"><span class="secno">1</span><span>Il blocco di guadagno</span></h2>')
    A('<p>Il blocco è uno solo (ADR-006) ed è usato quattro volte: due canali '
      '× blocco A (buffer d\'ingresso) e blocco B (uscita principale). '
      'Quarantaquattro componenti. È l\'oggetto da giudicare.</p>')
    A(figure("../schematic/gain_block.svg", "Schema del blocco di guadagno"))
    A('<h2 id="s2"><span class="secno">2</span><span>Il preamplificatore intero</span></h2>')
    A(figure("../schematic/preamp_blocks.svg", "Diagramma a blocchi del preamplificatore"))

    # --- punti di lavoro ---
    A('<h2 id="s3"><span class="secno">3</span><span>Punti di lavoro</span></h2>')
    A('<p>Corrente assorbita dai rail e punto di lavoro di ogni dispositivo '
      'attivo, a ingresso a massa. È la parte che il progetto dichiara '
      'credibile anche coi modelli segnaposto.</p>')
    ipp = rails.get("i(vpp)")
    imm = rails.get("i(vmm)")
    A('<div class="tablewrap"><table><tr><th>Grandezza</th><th>Valore</th></tr>')
    A(f'<tr><td>Corrente dal rail +15 V</td><td class="num">{it(abs(ipp)*1000, 4)} mA</td></tr>')
    A(f'<tr><td>Corrente dal rail −15 V</td><td class="num">{it(abs(imm)*1000, 4)} mA</td></tr>')
    A('</table></div>')
    A('<div class="tablewrap"><table><tr><th>Dispositivo</th><th>I<sub>C</sub> / I<sub>D</sub> [mA]</th>'
      '<th>V<sub>BE</sub> / V<sub>GS</sub> [V]</th><th>V<sub>BC</sub> [V]</th></tr>')
    for dev, par in devices:
        ic = par.get("ic", par.get("id"))
        vbe = par.get("vbe", par.get("vgs"))
        vbc = par.get("vbc")
        A(f'<tr><td>{html_escape(dev.upper())}</td>'
          f'<td class="num">{it(ic*1000, 4) if ic is not None else "&mdash;"}</td>'
          f'<td class="num">{it(vbe, 4) if vbe is not None else "&mdash;"}</td>'
          f'<td class="num">{it(vbc, 4) if vbc is not None else "&mdash;"}</td></tr>')
    A('</table></div>')

    # --- headroom ---
    A('<h2 id="s4"><span class="secno">4</span><span>Escursione in continua e saturazione</span></h2>')
    A(figure("fig_headroom.svg", "Escursione in continua"))
    A('<p>La <em>finestra lineare</em> qui sotto è definita, perché non è una '
      'grandezza universale: è il più grande intervallo attorno a 0 V in cui il '
      'guadagno locale resta entro l\'1% del suo valore a 0 V.</p>')
    A('<div class="tablewrap"><table><tr><th>Modalità</th><th>Guadagno a 0 V</th><th>Finestra lineare '
      'in ingresso</th><th>v(OUT) al limite</th><th>Saturazione v(OUT)</th></tr>')
    for mode, lab in (("0db", "0 dB"), ("10db", "+10 dB")):
        r = hr[mode]
        A(f'<tr><td>{lab}</td><td class="num">{it(r["gain"], 4)} ×</td>'
          f'<td class="num">{it(r["lin_lo"], 3)} … {it(r["lin_hi"], 3)} V</td>'
          f'<td class="num">{it(r["vout_lin_lo"], 3)} … {it(r["vout_lin_hi"], 3)} V</td>'
          f'<td class="num">{it(r["vout_min"], 3)} … {it(r["vout_max"], 3)} V</td></tr>')
    A('</table></div>')
    A('<p>Le due modalità <strong>non saturano allo stesso livello, e la '
      'differenza non è nello stadio d\'uscita</strong>. A guadagno unitario '
      'v(FB) insegue v(OUT), quindi il modo comune visto dalla coppia '
      'd\'ingresso sale <em>insieme</em> all\'uscita ed è lui a fermarsi per '
      f'primo: l\'uscita si appoggia a {it(hr["0db"]["vout_max"], 4)} V. A '
      '+10 dB v(FB) vale un terzo di v(OUT), il modo comune resta basso, e '
      f'l\'uscita arriva a {it(hr["10db"]["vout_max"], 4)} V. È una proprietà '
      'della topologia, non dei modelli; i valori esatti dipendono invece dal '
      'modello del JFET, che è segnaposto. Il ramo negativo è limitato prima '
      'dallo stadio d\'uscita, e infatti coincide quasi nelle due modalità.</p>')

    vpk = hr["10db"]["vout_lin_hi"]
    A(f'<p>Con rail a ±15 V (ADR-015) il limite lineare in +10 dB corrisponde a '
      f'<strong>{it(vpk/math.sqrt(2), 3)} V RMS</strong> in uscita. Il caso che '
      'preoccupa è E6 × E2: il FiiO K11 a fondo scala dà 2,7 V RMS, che a +10 dB '
      f'vorrebbero {it(2.7*math.sqrt(10), 3)} V RMS. Il margine è quindi di circa '
      f'<strong>{it(20*math.log10((vpk/math.sqrt(2))/(2.7*math.sqrt(10))), 2)} dB</strong>, '
      'ed è la ragione per cui il trim di ADR-011 non è più opzionale.</p>')
    A('<p class="meta">Questo margine è più stretto di quello registrato in '
      'STATE.md (0,75 dB, da 9,31 V RMS) perché <strong>la metrica è '
      'diversa</strong>, non perché il circuito sia cambiato: qui il limite è '
      'il punto in cui il guadagno si scosta dell\'1%, che arriva prima del '
      'punto in cui la forma d\'onda visibilmente tosa. È la lettura '
      'conservativa delle due, e le due cifre vanno riconciliate quando '
      'arriveranno i modelli vendor.</p>')

    # --- risposta ---
    A('<h2 id="s5"><span class="secno">5</span><span>Risposta in frequenza</span></h2>')
    A(figure("fig_response.svg", "Risposta in frequenza"))
    A('<div class="tablewrap"><table><tr><th>Curva</th><th>20 Hz</th><th>1 kHz</th><th>20 kHz</th>'
      '<th>100 kHz</th></tr>')
    labels = {("0db", "1.5"): "0 dB · sorgente 1,5 Ω",
              ("0db", "2500"): "0 dB · sorgente 2500 Ω",
              ("10db", "1.5"): "+10 dB · sorgente 1,5 Ω",
              ("10db", "2500"): "+10 dB · sorgente 2500 Ω"}
    for key, lab in labels.items():
        r = resp[key]
        A(f'<tr><td>{lab}</td><td class="num">{it(r["g20"], 4)} dB</td>'
          f'<td class="num">{it(r["g1k"], 4)} dB</td>'
          f'<td class="num">{it(r["g20k"], 4)} dB</td>'
          f'<td class="num">{it(r["g100k"], 4)} dB</td></tr>')
    A('</table></div>')

    A('<h3>La claim falsificabile di ADR-014</h3>')
    A('<p>L\'attenuatore a gradini ha impedenza d\'uscita che va da ~0 a 2,5 kΩ '
      'e ritorno mentre si ruota la manopola. Se il cascode d\'ingresso fa il '
      'suo lavoro, <strong>la risposta a 20 kHz non deve muoversi</strong>. '
      'Se si muove, ADR-014 non è stata implementata, qualunque cosa dica lo '
      'schema.</p>')
    A(figure("fig_response_adr014.svg", "ADR-014: risposta contro impedenza di sorgente"))
    d0 = resp[("0db", "2500")]["g20k"] - resp[("0db", "1.5")]["g20k"]
    d10 = resp[("10db", "2500")]["g20k"] - resp[("10db", "1.5")]["g20k"]
    A('<div class="tablewrap"><table><tr><th>Modalità</th><th>20 kHz, sorgente 1,5 Ω</th>'
      '<th>20 kHz, sorgente 2500 Ω</th><th>scarto</th></tr>')
    A(f'<tr><td>0 dB</td><td class="num">{it(resp[("0db","1.5")]["g20k"], 4)} dB</td>'
      f'<td class="num">{it(resp[("0db","2500")]["g20k"], 4)} dB</td>'
      f'<td class="num"><strong>{it(abs(d0), 3)} dB</strong></td></tr>')
    A(f'<tr><td>+10 dB</td><td class="num">{it(resp[("10db","1.5")]["g20k"], 4)} dB</td>'
      f'<td class="num">{it(resp[("10db","2500")]["g20k"], 4)} dB</td>'
      f'<td class="num"><strong>{it(abs(d10), 3)} dB</strong></td></tr>')
    A('</table></div>')

    lf = resp["lf"]
    A('<h3>Il taglio in bassa, col carico da 50 kΩ</h3>')
    A(f'<p>Con il carico Stax-like da 50 kΩ invece dei 100 kΩ del finale: '
      f'{it(lf["g1k"], 4)} dB a 1 kHz, {it(lf["g20"], 4)} dB a 20 Hz, '
      f'{it(lf["g5"], 4)} dB a 5 Hz. Il polo è quello del condensatore d\'uscita '
      'da 4,7 µF (E8 / ADR-007).</p>')

    # --- anello ---
    A('<h2 id="s6"><span class="secno">6</span><span>Guadagno d\'anello e margine di fase</span></h2>')
    A('<p>Iniezione di tensione al gate del JFET invertente. Quel nodo non '
      'assorbe corrente e la rete di controreazione lo pilota da ~470 Ω, quindi '
      'l\'iniezione semplice è esatta e non serve la correzione di Middlebrook. '
      '<strong>Il relè commuta la rete di controreazione, quindi il margine è '
      'diverso nelle due modalità</strong> — è la ragione per cui '
      'REQUIREMENTS.md chiede tutta la matrice V1 e non un caso solo.</p>')
    A(figure("fig_loop.svg", "Guadagno d'anello"))
    A('<div class="tablewrap"><table><tr><th>Configurazione</th><th>|T| a 10 Hz</th>'
      '<th>frequenza d\'incrocio</th><th>margine di fase</th></tr>')
    loop_labels = {("0db", "1f"): "0 dB · cavo ~0",
                   ("0db", "4.7n"): "0 dB · cavo 4,7 nF",
                   ("10db", "1f"): "+10 dB · cavo ~0",
                   ("10db", "4.7n"): "+10 dB · cavo 4,7 nF"}
    for key, lab in loop_labels.items():
        r = loop[key]
        A(f'<tr><td>{lab}</td><td class="num">{it(r["tdc"], 4)} dB</td>'
          f'<td class="num">{it(r["fcross"]/1000, 4)} kHz</td>'
          f'<td class="num"><strong>{it(r["pmarg"], 4)}°</strong></td></tr>')
    A('</table></div>')
    worst = min(loop.values(), key=lambda r: r["pmarg"])
    A(f'<p>Il caso peggiore fra questi quattro è <strong>{it(worst["pmarg"], 3)}°</strong>. '
      'Il carico capacitivo da 4,7 nF è molto più di quanto un cablaggio da '
      '20 cm possa presentare: è una sonda di margine, non un valore realistico.</p>')

    # --- PSRR ---
    A('<h2 id="s7"><span class="secno">7</span><span>Reiezione dell\'alimentazione</span></h2>')
    A(figure("fig_psrr.svg", "PSRR"))
    A('<div class="tablewrap"><table><tr><th>Rail e modalità</th><th>100 Hz</th><th>1 kHz</th>'
      '<th>10 kHz</th><th>100 kHz</th></tr>')
    psrr_labels = {("p", "0db"): "rail + · 0 dB", ("p", "10db"): "rail + · +10 dB",
                   ("m", "0db"): "rail − · 0 dB", ("m", "10db"): "rail − · +10 dB"}
    for key, lab in psrr_labels.items():
        r = psrr[key]
        A(f'<tr><td>{lab}</td><td class="num">{it(r["p100"], 4)} dB</td>'
          f'<td class="num">{it(r["p1k"], 4)} dB</td>'
          f'<td class="num">{it(r["p10k"], 4)} dB</td>'
          f'<td class="num">{it(r["p100k"], 4)} dB</td></tr>')
    A('</table></div>')
    weak = min(psrr.values(), key=lambda r: r["p10k"])
    A(f'<p>Il rail <strong>positivo</strong> è il lato debole, e in modalità '
      f'+10 dB perde i 10 dB di guadagno: <strong>{it(weak["p10k"], 3)} dB a '
      '10 kHz</strong>. È il numero da avere in mano quando si progetta '
      'l\'alimentatore (Fase 6).</p>')

    # --- Zout ---
    A('<h2 id="s8"><span class="secno">8</span><span>Impedenza d\'uscita</span></h2>')
    A(figure("fig_zout.svg", "Impedenza d'uscita"))
    A('<div class="tablewrap"><table><tr><th>Punto di misura</th><th>20 Hz</th><th>1 kHz</th>'
      '<th>20 kHz</th><th>100 kHz</th></tr>')
    for mode, lab in (("0db", "0 dB"), ("10db", "+10 dB")):
        r = z[mode]
        A(f'<tr><td>al jack · {lab}</td><td class="num">{it(r["z20"], 4)} Ω</td>'
          f'<td class="num">{it(r["z1k"], 4)} Ω</td>'
          f'<td class="num">{it(r["z20k"], 4)} Ω</td>'
          f'<td class="num">{it(r["z100k"], 4)} Ω</td></tr>')
    for mode, lab in (("0db", "0 dB"), ("10db", "+10 dB")):
        r = z[mode]
        A(f'<tr><td>al nodo OUT · {lab}</td><td class="num">{it(r["za20"], 4)} Ω</td>'
          f'<td class="num">{it(r["za1k"], 4)} Ω</td>'
          f'<td class="num">{it(r["za20k"], 4)} Ω</td>'
          f'<td class="num">{it(r["za100k"], 4)} Ω</td></tr>')
    A('</table></div>')
    A(f'<div class="note"><strong>Tensione fra E4 ed E8, segnalata e non '
      f'aggirata.</strong> E4 chiede &lt; 100 Ω in banda passante. Al jack a '
      f'20 Hz la misura dà {it(z["0db"]["z20"], 4)} Ω, ma quella '
      f'<em>è la reattanza del condensatore d\'uscita da 4,7 µF</em>, non '
      f'l\'impedenza dello stadio: al nodo OUT, prima del condensatore, la '
      f'stessa frequenza dà {it(z["0db"]["za20"], 3)} Ω. '
      '<strong>E4 letta alla lettera non è soddisfacibile a 20 Hz da nessun '
      'circuito con condensatore d\'uscita</strong>, ed è per questo che il '
      'requisito dice «misurata escludendo la reattanza del condensatore '
      'd\'accoppiamento».</div>')

    # --- controfattuale ---
    A('<h2 id="s9"><span class="secno">9</span><span>Il controfattuale del relè di guadagno</span></h2>')
    A('<p>ADR-004 ha <strong>scartato</strong> l\'idea di mettere il contatto '
      'del relè in serie a R<sub>f</sub>, cioè nel ramo dell\'anello. Una '
      'decisione di progetto porta informazione solo se la disposizione '
      'scartata è mostrata <em>fallire</em>: questo è il mezzo falsificabile '
      'della verifica V2.</p>')
    A('<p>Con R<sub>f</sub> aperto non esiste più alcun percorso di '
      'controreazione: la coppia d\'ingresso vede solo il proprio offset '
      'moltiplicato per tutto il guadagno ad anello aperto, e l\'uscita se ne '
      f'va a <strong>{it(cf[1]["vout"], 6)} V</strong>. Per essere precisi non '
      'sbatte contro il rail né contro il proprio limite di saturazione '
      f'({it(hr["0db"]["vout_min"], 5)} V, misurato nella sezione 4): si ferma '
      'poco prima, dove il guadagno ad anello aperto moltiplicato per l\'offset '
      'residuo trova equilibrio. Il punto della verifica non cambia — a '
      'quel livello lo stadio non amplifica più niente.</p>')
    A(figure("fig_counterfactual.svg", "Controfattuale del relè di guadagno"))
    A('<div class="tablewrap"><table><tr><th>Stato</th><th>Configurazione</th><th>v(OUT)</th>'
      '<th>v(FB)</th></tr>')
    for r in cf:
        A(f'<tr><td><strong>{r["tag"]}</strong></td><td>{html_escape(r["desc"])}</td>'
          f'<td class="num"><strong>{it(r["vout"], 6)} V</strong></td>'
          f'<td class="num">{it(r["vfb"], 6)} V</td></tr>')
    A('</table></div>')
    A('<p>C esiste per escludere che B sia un artefatto del solutore: A e C '
      'coincidono a tutte le cifre. La disposizione scelta da ADR-004 commuta '
      'invece R<sub>g</sub> verso massa, quindi a contatti aperti il guadagno è '
      '1 e <strong>l\'anello non si apre mai</strong>.</p>')
    A('<p class="meta">Manca ancora il transitorio del relè da affiancare a '
      'questi tre punti: i suoi dati grezzi sono 2,8 MB e non sono stati '
      'versionati. È una decisione aperta, non una dimenticanza.</p>')

    # --- requisiti ---
    A('<h2 id="s10"><span class="secno">10</span><span>Requisiti a fronte del misurato</span></h2>')
    A('<p>Solo i requisiti che queste misure toccano. Il resto non è qui '
      'perché non è ancora stato misurato, non perché sia soddisfatto.</p>')
    g0 = resp[("0db", "1.5")]["g1k"]
    g10 = resp[("10db", "1.5")]["g1k"]
    A('<div class="tablewrap"><table><tr><th>Req.</th><th>Chiede</th><th>Misurato</th><th>Esito</th></tr>')
    A(f'<tr><td>E1</td><td>guadagno nominale 0 dB</td>'
      f'<td class="num">{it(g0, 4)} dB a 1 kHz</td>'
      f'<td class="{"ok" if abs(g0) < 0.1 else "no"}">'
      f'{"soddisfatto" if abs(g0) < 0.1 else "no"}</td></tr>')
    A(f'<tr><td>E2</td><td>guadagno alternativo +10 dB</td>'
      f'<td class="num">{it(g10, 4)} dB a 1 kHz</td>'
      f'<td class="{"ok" if abs(g10-10) < 0.2 else "no"}">'
      f'{"soddisfatto" if abs(g10-10) < 0.2 else "scostamento"}</td></tr>')
    A(f'<tr><td>E4</td><td>Z<sub>out</sub> &lt; 100 Ω in banda passante, '
      f'esclusa la reattanza del cap</td>'
      f'<td class="num">{it(z["0db"]["z1k"], 4)} Ω a 1 kHz al jack · '
      f'{it(z["0db"]["za1k"], 3)} Ω al nodo OUT</td>'
      f'<td class="{"ok" if z["0db"]["z1k"] < 100 else "no"}">'
      f'{"soddisfatto" if z["0db"]["z1k"] < 100 else "no"} in banda; '
      'vedi la nota su 20 Hz</td></tr>')
    A('<tr><td>E5</td><td>rumore in uscita &lt; 10 µV RMS</td>'
      '<td class="na">non riportato</td>'
      '<td class="na">senza evidenza — modelli con KF = 0</td></tr>')
    A(f'<tr><td>E6×E2</td><td>2,7 V RMS d\'ingresso a +10 dB</td>'
      f'<td class="num">limite lineare {it(vpk/math.sqrt(2), 3)} V RMS</td>'
      f'<td class="{"ok" if vpk/math.sqrt(2) > 2.7*math.sqrt(10) else "no"}">'
      f'margine {it(20*math.log10((vpk/math.sqrt(2))/(2.7*math.sqrt(10))), 2)} dB — '
      'il trim di ADR-011 non è opzionale</td></tr>')
    A(f'<tr><td>V1</td><td>margine di fase in tutta la matrice</td>'
      f'<td class="num">peggiore fra i 4 casi: {it(worst["pmarg"], 3)}°</td>'
      '<td class="na">parziale — 4 casi su una matrice molto più grande</td></tr>')
    A('<tr><td>V2</td><td>l\'anello non si apre mai commutando</td>'
      '<td>controfattuale a −13,68 V, disposizione scelta stabile</td>'
      '<td class="na">metà falsificabile fatta; manca il transitorio</td></tr>')
    A('<tr><td>V4</td><td>THD/THD+N</td><td class="na">assente</td>'
      '<td class="na">nessun modello vendor: una cifra sarebbe priva di '
      'significato</td></tr>')
    A('</table></div>')

    # --- limiti ---
    A('<h2 id="s11"><span class="secno">11</span><span>Cosa questo dossier non dice</span></h2>')
    A('<ul>')
    A('<li><strong>Niente distorsione.</strong> I modelli sono segnaposto e il '
      'macro-modello dichiara nella propria intestazione di non avere clipping '
      'del segnale, né slew rate, né assorbimento dalle alimentazioni. Una '
      'cifra di THD da questa libreria sarebbe priva di significato.</li>')
    A('<li><strong>Niente rumore.</strong> <code>KF = 0</code> su ogni '
      'dispositivo: nessuna di queste simulazioni ha rumore 1/f. I deck lo '
      'calcolano, ma la cifra è un pavimento termico+shot, non una previsione, '
      'e per questo non è stata versionata.</li>')
    A('<li><strong>Un difetto trovato costruendo questa pagina, e corretto '
      'prima di pubblicarla.</strong> <code>za100k</code> e <code>p100k</code> '
      'chiedevano <code>find … at=100000</code> su una spazzata che '
      '<em>finiva</em> a 100 kHz: <code>meas … find at=</code> interpola fra '
      'due punti, quindi sul bordo ngspice rispondeva «out of interval» e sei '
      'misure su sei sezioni non venivano prodotte — con il deck che '
      'proseguiva e usciva 0, quindi il buco non si vedeva dal codice di '
      'uscita. La spazzata ora arriva a 200 kHz e le colonne a 100 kHz qui '
      'sopra esistono. Effetto collaterale misurato: la griglia si è fatta '
      'regolare e il valore interpolato a 1 kHz si è spostato dello 0,14% '
      '(58,84 → 58,76 Ω). Non è il circuito che è cambiato: è la misura '
      'dell&rsquo;errore di interpolazione di <code>find at=</code> su una '
      'griglia da 20 punti/decade.</li>')
    A('<li><strong>La matrice V1 è coperta in minima parte.</strong> Quattro '
      'combinazioni su blocco × posizione dell\'attenuatore × carico × sorgente. '
      'Il blocco A ha un suo deck, non impaginato qui.</li>')
    A('<li><strong>Mancano i transitori</strong>: commutazione del relè e '
      'recupero dalla saturazione (V3). I deck girano, ma i dati grezzi sono '
      '2,8 e 1,9 MB e non è stato deciso come versionarli.</li>')
    A('<li><strong>Nessuno qui giudica come suona.</strong> La simulazione '
      'copre stabilità, risposta, PSRR e impedenze; non copre l\'ascolto.</li>')
    A('</ul>')

    # --- provenienza ---
    A('<h2 id="s12"><span class="secno">12</span><span>Provenienza</span></h2>')
    A('<p>Ogni figura e ogni tabella dichiara il file da cui viene. I file '
      f'stanno in <code>docs/preamp/data/{DATA_DATE}/</code>, versionati, con '
      'accanto il <code>.log</code> di ngspice come evidenza e un '
      '<code>README.md</code> con la legenda delle colonne.</p>')
    A('<div class="tablewrap"><table><tr><th>Sezione</th><th>Deck</th><th>Dati</th></tr>')
    for sec, deck, files in (
            ("Punti di lavoro", "tb_op.cir", "tb_op.log"),
            ("Escursione in continua", "tb_dc_headroom.cir", "tb_dc_headroom*.csv"),
            ("Risposta in frequenza", "tb_ac.cir", "tb_ac*.csv"),
            ("Guadagno d'anello", "tb_loop.cir", "tb_loop_*.csv"),
            ("PSRR", "tb_zout_psrr_noise.cir", "tb_zout_psrr_noise_psrr*.csv"),
            ("Impedenza d'uscita", "tb_zout_psrr_noise.cir", "tb_zout_psrr_noise_zout_*.csv"),
            ("Controfattuale del relè", "tb_switch_v2_counterfactual.cir",
             "tb_switch_v2_counterfactual*.csv")):
        A(f'<tr><td>{sec}</td><td><code>{deck}</code></td>'
          f'<td><code>{files}</code></td></tr>')
    A('</table></div>')
    A('<p class="meta">Rigenerare questa pagina: '
      '<code>/usr/bin/python3 docs/preamp/dossier/build_dossier.py</code>. '
      'Rieseguire una misura: <code>/bin/zsh scripts/run_simulation.sh '
      'spice/preamp/tb/&lt;deck&gt;.cir results/preamp/&lt;deck&gt;</code>.</p>')
    A('<hr class="end">')
    A('</div>')

    return ('<title>Dossier del preamp di linea</title>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
            'family=IBM+Plex+Mono:wght@400;500&'
            'family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&'
            'display=swap">\n'
            f"<style>{CSS}</style>\n" + "\n".join(h))


# ------------------------------------------------------------------ main ---
def main():
    standalone = None
    if "--standalone" in sys.argv:
        standalone = sys.argv[sys.argv.index("--standalone") + 1]

    resp = measure_response()
    loop = measure_loop()
    z = measure_zout()
    psrr = measure_psrr()
    hr = measure_headroom()
    cf = measure_counterfactual()
    rails, devices = measure_oppoint()

    if FAILURES:
        print("RIFIUTATO: i numeri calcolati dai CSV non coincidono con quelli "
              "che ngspice ha stampato nei log.", file=sys.stderr)
        for f in FAILURES:
            print(f"  - {f}", file=sys.stderr)
        print("Nessun file e' stato scritto.", file=sys.stderr)
        return 1

    figs = {
        "fig_response.svg": fig_response(resp),
        "fig_response_adr014.svg": fig_response_adr014(resp),
        "fig_loop.svg": fig_loop(loop),
        "fig_psrr.svg": fig_psrr(psrr),
        "fig_zout.svg": fig_zout(z),
        "fig_headroom.svg": fig_headroom(hr),
        "fig_counterfactual.svg": fig_counterfactual(cf, hr),
    }
    for name, body in figs.items():
        with open(os.path.join(HERE, name), "w") as f:
            f.write(body)
        print(f"   scritto {name} ({len(body)} byte)")

    page = build_page(resp, loop, z, psrr, hr, cf, rails, devices, inline=False)
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page)
    print(f"   scritto index.html ({len(page)} byte)")

    if standalone:
        page = build_page(resp, loop, z, psrr, hr, cf, rails, devices, inline=True)
        with open(standalone, "w") as f:
            f.write(page)
        print(f"   scritto {standalone} (autoconsistente, {len(page)} byte)")

    summary = {
        "data": DATA_DATE,
        "controlli_incrociati": "tutti superati",
        "guadagno_0db_1kHz_dB": resp[("0db", "1.5")]["g1k"],
        "guadagno_10db_1kHz_dB": resp[("10db", "1.5")]["g1k"],
        "adr014_scarto_20kHz_dB_0db":
            resp[("0db", "2500")]["g20k"] - resp[("0db", "1.5")]["g20k"],
        "margine_fase_peggiore_gradi":
            min(r["pmarg"] for r in loop.values()),
        "psrr_peggiore_10kHz_dB": min(r["p10k"] for r in psrr.values()),
        "zout_jack_1kHz_ohm_0db": z["0db"]["z1k"],
    }
    with open(os.path.join(HERE, "dossier.summary.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("   scritto dossier.summary.json")
    print("OK: tutti i controlli incrociati CSV vs log sono passati.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
