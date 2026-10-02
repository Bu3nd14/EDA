"""statico.py - L47b1: la cella a profondita' fissa, per ogni angolo e correttivo.

Per ogni d della griglia, con i comandi fermi (la sfumatura vista come una successione di stati;
la sfumatura vera e' in sfumatura.py):
  - tran + fourier a 1 kHz e a 20 kHz, tono di prova 3,818 V di picco (2,7 V RMS) da 1,5 ohm:
    il livello della fondamentale su AIN (dB sotto il pieno) e la THD, con il pavimento numerico
    della stessa corsa su v(vsn);
  - ac: |H| sorgente -> AIN a 20 Hz, 1 kHz, 20 kHz (B in mute, lineare);
  - ac: |Zin| al connettore (iniezione di corrente, sorgente staccata: limitations #28), il minimo
    su 20 Hz-20 kHz (E3, e il carico che la sorgente vede durante la sfumatura);
  - ac: |H| dal comando (prima del filtro RC) ad AIN, a 1 kHz e 20 kHz: il rumore del comando
    ammesso nella quota ausiliaria di 1 uV (ADR-022 punto 4).

    /usr/bin/python3 statico.py jfet      # tutti gli angoli e i correttivi
    /usr/bin/python3 statico.py ldr       # la NSL-32SR3, curve A-E, profilo v4 per d
Scrive run/statico_<cella>/<combo>.cir|.log e tabelle/statico_<cella>.csv.
"""
import csv
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from comune import (A_PIENO, QUI, cella_jfet, cella_ldr, comandi, correnti_ldr, corri, db,
                    guardia, ricuci, testa)

GRIGLIA = [round(k * 0.025, 4) for k in range(41)]
COMBO_JFET = [("TIP", "TIP"), ("VLO", "VLO"), ("VHI", "VHI"), ("VHI", "VLO"), ("VLO", "VHI")]
CORR = ["nessuno", "k030", "k048"]
COMBO_LDR = [("B", "B"), ("A", "A"), ("C", "C"), ("D", "D"), ("E", "E"), ("C", "A"), ("A", "C")]
FREQ = [(1000, 4e-3, 0.5e-6), (20000, 0.4e-3, 25e-9)]


def deck_jfet(ms, mp, corr, ordine):
    r = testa("statico jfet %s %s %s %s" % (ms, mp, corr, ordine)) + cella_jfet(ms, mp, corr)
    r += [".control", "option itl1=1000", "set numdgt=10", "set fourgridsize=8192", "set nfreqs=10"]
    for d in GRIGLIA:
        vcs, vcp = comandi(d, ordine)
        r += _caso(d, ["alter vcs dc = %.6f" % vcs, "alter vcp dc = %.6f" % vcp],
                   [("vcs", "dc %.6f" % vcs), ("vcp", "dc %.6f" % vcp)])
    return r + [".endc", ".end"]


def deck_ldr(cs, cp):
    r = testa("statico ldr %s %s" % (cs, cp)) + cella_ldr(cs, cp)
    r += [".control", "option itl1=1000", "set numdgt=10", "set fourgridsize=8192", "set nfreqs=10"]
    for d in GRIGLIA:
        ils, ilp = correnti_ldr(d)
        # #40: lo stato della LDR si legge nell'op; la tabella stampa xs, controllato dopo
        # la LDR del modello e' un resistore lineare (BCELL): la THD e' zero per costruzione, e la
        # tran a stato fermo fa collassare il passo su BDX (L47b1, «Timestep too small»). Qui
        # solo op + ac; la distorsione della LDR e' «non modellata» nella tabella.
        r += _caso(d, ["alter ils dc = %.6e" % ils, "alter ilp dc = %.6e" % ilp], None,
                   extra=["op", "print v(xls.xs) v(xlp.xs)", "destroy all"], tran=False)
    return r + [".endc", ".end"]


def _caso(d, imposta, cmd, extra=(), tran=True):
    """Un caso: ogni grandezza che un caso altera e' rimessa da ogni caso (#34)."""
    r = ["echo L47B1_CASO d=%.4f" % d] + imposta + [
        "alter vsrc ac = 1", "alter rsrc = 1.5"]
    if cmd:
        r += ["alter vcs ac = 0", "alter vcp ac = 0"]
    if not tran:
        r += list(extra)
    for f, tstop, tmax in (FREQ if tran else []):
        r += ["alter @vsrc[sin] = [ 0 %g %g ]" % (A_PIENO, f),
              "tran %g %g %g %g" % (tmax, tstop, tstop - 2.0 / f, tmax),
              "fourier %d v(vsn) v(ain)" % f]
        r += list(extra) if f == 1000 else []
        r += ["destroy all"]
    r += ["ac lin 1 1k 1k 1", "let h1k = mag(v(ain))", "print h1k", "destroy all",
          "ac lin 1 20k 20k 1", "let h20k = mag(v(ain))", "print h20k", "destroy all"]
    r += ["ac lin 1 20 20 1", "print mag(v(ain))", "destroy all"]
    # Zin al connettore: v(srcx) diviso la corrente di ramo della sorgente. Con la sorgente
    # staccata (RSRC 1 T e iniezione) il connettore restava senza percorso in continua e l'op
    # cambiava: la prima stesura di L47b1 lo ha mostrato (6 kohm in mute che non esistono).
    r += ["ac dec 20 20 20k", "let zmin = vecmin(mag(v(srcx) / (-i(vsrc))))", "print zmin",
          "destroy all"]
    if cmd:
        for n in ("vcs", "vcp"):
            r += ["alter %s ac = 1" % n, "ac lin 1 1k 1k 1",
                  "let c%s1k = mag(v(ain))" % n, "print c%s1k" % n, "destroy all",
                  "ac lin 1 20k 20k 1", "let c%s20k = mag(v(ain))" % n, "print c%s20k" % n,
                  "destroy all", "alter %s ac = 0" % n]
    r += ["alter vsrc ac = 1"]
    return r


def leggi(log):
    righe = ricuci(log)
    casi, cur, nodo, f = [], None, None, None
    for r in righe:
        m = re.search(r"L47B1_CASO d=([0-9.]+)", r)
        if m:
            cur = {"d": float(m.group(1)), "four": {}, "ac20": []}
            casi.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"\s*Fourier analysis for (\S+):", r)
        if m:
            nodo = m.group(1)
            continue
        m = re.search(r"No\. Harmonics: \d+, THD: ([-+0-9.eE]+) %", r)
        m2 = re.search(r"THD: ([-+0-9.eE]+) %", r)
        if m2 and nodo:
            cur["_thd"] = float(m2.group(1))
            continue
        m = re.match(r"\s*(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*$", r)
        if m and nodo:
            k, fr, mag = int(m.group(1)), float(m.group(2)), float(m.group(3))
            if k == 0:
                continue
            if k == 1:
                f = int(round(fr))
                cur["four"][(nodo, f)] = {"thd": cur.pop("_thd"), "h": {}}
            cur["four"][(nodo, f)]["h"][k] = mag
            continue
        m = re.match(r"\s*([a-z0-9_.()]+)\s*=\s*([-+0-9.eE]+)\s*$", r.lower())
        if m:
            k, v = m.group(1), float(m.group(2))
            if k == "mag(v(ain))":
                cur["h20"] = v
            elif k.startswith("v(xl"):
                cur[k] = v
            else:
                cur[k] = v
    return casi


def tabella(cella, combo, casi):
    out = []
    for c in casi:
        riga = {"cella": cella, "combo": combo, "d": c["d"]}
        for f in (1000, 20000):
            a = c["four"].get(("v(ain)", f))
            s = c["four"].get(("v(vsn)", f))
            if cella == "ldr":
                h = c.get("h1k" if f == 1000 else "h20k")
                riga["liv%d_db" % f] = db(h)
                riga["thd%d_pct" % f] = "non modellata"
                continue
            if a is None or s is None:
                raise SystemExit("%s d=%g: fourier a %d Hz mancante" % (combo, c["d"], f))
            riga["liv%d_db" % f] = db(a["h"][1] / A_PIENO)
            riga["thd%d_pct" % f] = a["thd"]
            riga["h2_%d_db" % f] = db(a["h"].get(2, 0) / max(a["h"][1], 1e-300))
            riga["h3_%d_db" % f] = db(a["h"].get(3, 0) / max(a["h"][1], 1e-300))
            riga["pav%d_pct" % f] = s["thd"]
        riga["h20"] = c.get("h20")
        riga["h1k"] = c.get("h1k")
        riga["h20k"] = c.get("h20k")
        riga["zmin_ohm"] = c.get("zmin")
        for k in ("cvcs1k", "cvcs20k", "cvcp1k", "cvcp20k", "v(xls.xs)", "v(xlp.xs)"):
            if k in c:
                riga[k.replace("v(", "").replace(".xs)", "_log10r")] = c[k]
        out.append(riga)
    return out


def esegui(cella):
    # --cima12: la cima del LED a 12 mA (ADR-050, NC-049); file separati da quelli a 20 mA
    suff = "_cima12" if "--cima12" in sys.argv else ""
    cartella = os.path.join(QUI, "run", "statico_" + cella + suff)
    os.makedirs(cartella, exist_ok=True)
    lavori = []
    if cella == "jfet":
        for ms, mp in COMBO_JFET:
            for corr in CORR:
                nome = "%s_%s_%s" % (ms, mp, corr)
                lavori.append((nome, deck_jfet(ms, mp, corr, "serie_prima")))
    else:
        for cs, cp in COMBO_LDR:
            lavori.append(("%s_%s" % (cs, cp), deck_ldr(cs, cp)))
    for nome, r in lavori:
        open(os.path.join(cartella, nome + ".cir"), "w").write("\n".join(r) + "\n")

    def uno(nome):
        rc, log = corri(os.path.join(cartella, nome + ".cir"))
        return nome, rc, log

    with ThreadPoolExecutor(8) as ex:
        esiti = list(ex.map(uno, [n for n, _ in lavori]))
    righe, ok = [], True
    for nome, rc, log in esiti:
        cattive = guardia(log)
        if rc != 0 or cattive:
            print("RIFIUTATA %s: rc=%d %s" % (nome, rc, cattive[:3]))
            ok = False
            continue
        casi = leggi(log)
        if len(casi) != len(GRIGLIA):
            print("RIFIUTATA %s: %d casi su %d" % (nome, len(casi), len(GRIGLIA)))
            ok = False
            continue
        righe += tabella(cella, nome, casi)
    os.makedirs(os.path.join(QUI, "tabelle"), exist_ok=True)
    out = os.path.join(QUI, "tabelle", "statico_%s%s.csv" % (cella, suff))
    campi = []
    for r in righe:
        for k in r:
            if k not in campi:
                campi.append(k)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        for r in righe:
            w.writerow({k: ("%.6g" % v if isinstance(v, float) else v) for k, v in r.items()})
    print("scritto %s (%d righe), esito %s" % (out, len(righe), "OK" if ok else "CON RIFIUTI"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(esegui(sys.argv[1]))
