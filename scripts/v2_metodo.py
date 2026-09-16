#!/usr/bin/env python3
"""v2_metodo.py - il metodo di misura di V2 (REQUIREMENTS.md, ADR-032), L29a.

Solo stdlib (scipy non c'e' nel venv, L38). Lanciare con /usr/bin/python3.

COSA FA
-------
Applica alla lettera il "Metodo di misura" di V2 alle forme d'onda al jack
scritte da `wrdata` nei deck spice/preamp/tb/tb_v2_mute_*.cir:

- ricampionamento uniforme a 96 kHz. Interpolazione CUBICA (Lagrange a 4 punti
  sulla griglia non uniforme di ngspice), non lineare: l'autotest misura quanto
  sbaglia la lineare. I punti piu' vicini di `dtmin` all'ultimo tenuto si
  scartano, perche' due campioni a 1e-12 s fanno esplodere i pesi di Lagrange;
- filtro: passa-alto Butterworth 2 ordine a 20 Hz e passa-basso Butterworth 2
  ordine a 20 kHz, biquad per trasformata bilineare COPIATI da
  docs/preamp/data/2026-09-15/L38/calcolo_v2.py (l'autotest riproduce le sue
  cifre);
- A: d(t) = evento - riferimento sulla stessa griglia, filtrato da t_evento con
  stato nullo, picco su >= 2 s. Una finestra piu' corta da' un LIMITE INFERIORE:
  basta a respingere, non ad accettare, e la riga lo dice;
- B: il testo di V2 ("per tutta la durata del mute inserito, fuori dalla
  finestra di A") e' ambiguo quando il mute dura quanto la finestra di A. Due
  letture, entrambe riportate:
    B1  la corsa di riferimento "sempre in mute", filtrata da t = 0, picco da
        0,5 s alla fine;
    B2  la corsa con l'evento, filtrata da t = 0, picco da t_ins + 20 ms a t_rel;
- C: residuo = v_jack - tono ricostruito a frequenza nota (seno + coseno, senza
  termine continuo) su una finestra scorrevole CENTRATA di 10 ms, poi filtrato;
  picco in [t_evento - 20 ms, t_evento + 200 ms] per ogni inserzione e rilascio.
  Il numero di condizione della matrice 2x2 del fit si stampa e si dichiara.

SOTTOCOMANDI
------------
  autotest [--sabota NOME]    controlli su segnali sintetici; exit 0 = tutti
                              veri. Con --sabota almeno uno DEVE cadere.
  sabotaggi                   lancia autotest con ogni sabotaggio e verifica che
                              ciascuno faccia cadere almeno un controllo.
  caratterizza                residuo di C per dissolvenze sintetiche: quanto
                              deve durare una dissolvenza per passare C.
  canale DECK...              il blocco "* >>> CANALE" ... "* <<< CANALE" e'
                              identico in tutti i deck dati.
  analizza MANIFEST DIR OUT   applica il metodo a ogni cella del manifesto
                              (scritto dal deck), coi .dat in DIR; scrive OUT.
  riassumi OUT... RIASSUNTO   massimo per variante x carico x grandezza x uscita,
                              e il verdetto dello screening per variante.
  armoniche DAT COL F T0 T1 TMAX
                              diagnostica del pavimento di C: armoniche 1..20
                              e C col segnale com'e' e senza le armoniche 2..20.
  griglia DAT F AMP T0 T1 TMAX
                              errore dello strumento sulla griglia vera di
                              ngspice: un seno esatto sugli istanti del .dat.

Soglia: 100 uV di picco (ADR-032). Ogni cifra e' SIMULATA se viene da un .dat,
CALCOLATA se viene da autotest/caratterizza: le intestazioni lo dicono.
"""
import csv
import math
import os
import subprocess
import sys

FS = 96000.0
SOGLIA = 100e-6
# La soglia di C e' separata da quella di A e B (ADR-035, decisa dall'utente il
# 2026-09-16). Ragione, coi numeri di L29a: C confronta il residuo di un fit col
# suo pavimento, e il pavimento del metodo con musica a 1 kHz a fondo scala sta
# fra 0,4 e 0,7 mV - sopra i 100 uV. A e B restano a 100 uV perche' li' la
# risoluzione c'e' davvero (A senza segnale misura a pV, a 20 Hz a 8,5 uV;
# B misura 20 mV). Provvisoria finche' i modelli sono segnaposto (NC-017).
SOGLIA_C = 1e-3
FINESTRA_C = 0.010
# 10 ms esatti = 960 campioni a 96 kHz: 10 periodi interi a 1 kHz, 200 a 20 kHz.
# La finestra non ha un campione centrale; il fit si valuta al campione i con
# la finestra [i-480, i+480). --campioni 961 riproduce la prima stesura
# (dispari, centrata), e caratterizza la usa come sensibilita' dichiarata.
CAMPIONI_C = int(round(FINESTRA_C * FS))
DURATA_A = 2.0
USCITE = ("MAINJACK", "FIXJACK1", "FIXJACK2")
SABOTA = set()
SABOTAGGI = ("senza_filtro", "hp_primo_ordine", "rif_sfasato", "senza_fit",
             "fit_perfetto", "freq_sbagliata", "lineare",
             "senza_diradamento", "canale_cieco",
             "c2_senza_riferimento", "soglia_unica")


def soglia_di(grandezza):
    """La soglia della grandezza: 1 mV per C, 100 uV per A e B (ADR-035)."""
    if "soglia_unica" in SABOTA:
        return SOGLIA
    return SOGLIA_C if grandezza.startswith("C") else SOGLIA


# --------------------------------------------------------------- filtro ----
def biquad(kind, f0, q):
    # Identico a calcolo_v2.py (L38).
    w = 2 * math.pi * f0 / FS
    c = math.cos(w)
    a = math.sin(w) / (2 * q)
    if kind == "hp":
        b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
    else:
        b = [(1 - c) / 2, 1 - c, (1 - c) / 2]
    den = [1 + a, -2 * c, 1 - a]
    return [x / den[0] for x in b], [x / den[0] for x in den]


def hp_first(f0):
    k = math.tan(math.pi * f0 / FS)
    return [1 / (1 + k), -1 / (1 + k)], [1.0, (k - 1) / (k + 1)]


def _stadi():
    lp = biquad("lp", 20000, 1 / math.sqrt(2))
    if "hp_primo_ordine" in SABOTA:
        return [hp_first(20), lp]
    return [biquad("hp", 20, 1 / math.sqrt(2)), lp]


def filtra(x, i0=0):
    """Filtro di V2 applicato da i0 con stato nullo; zero prima di i0."""
    y = [0.0] * len(x)
    if "senza_filtro" in SABOTA:
        y[i0:] = x[i0:]
        return y
    seg = x[i0:]
    for b, den in _stadi():
        out = [0.0] * len(seg)
        x1 = x2 = y1 = y2 = 0.0
        if len(b) == 2:
            for i, xi in enumerate(seg):
                yi = b[0] * xi + b[1] * x1 - den[1] * y1
                x1, y1 = xi, yi
                out[i] = yi
        else:
            b0, b1, b2 = b
            d1, d2 = den[1], den[2]
            for i, xi in enumerate(seg):
                yi = b0 * xi + b1 * x1 + b2 * x2 - d1 * y1 - d2 * y2
                x2, x1, y2, y1 = x1, xi, y1, yi
                out[i] = yi
        seg = out
    y[i0:] = seg
    return y


def picco(y, i0, i1):
    i0 = max(i0, 0)
    i1 = min(i1, len(y))
    best, bi = 0.0, i0
    for i in range(i0, i1):
        v = abs(y[i])
        if v > best:
            best, bi = v, i
    return best, bi


# ------------------------------------------------------- ricampionamento ----
def dirada(t, cols, dtmin):
    if "senza_diradamento" in SABOTA or dtmin <= 0:
        return t, cols
    tt = [t[0]]
    cc = [[c[0]] for c in cols]
    for i in range(1, len(t)):
        if t[i] - tt[-1] >= dtmin or i == len(t) - 1:
            if t[i] <= tt[-1]:
                continue
            tt.append(t[i])
            for k, c in enumerate(cols):
                cc[k].append(c[i])
    return tt, cc


def ricampiona(t, y, t_fine):
    """y(t) non uniforme -> griglia k/FS, k = 0 .. floor(t_fine*FS)."""
    n = int(math.floor(min(t_fine, t[-1]) * FS)) + 1
    out = [0.0] * n
    N = len(t)
    i = 0
    lineare = "lineare" in SABOTA
    for k in range(n):
        tk = k / FS
        while i < N - 2 and t[i + 1] <= tk:
            i += 1
        if lineare:
            h = t[i + 1] - t[i]
            u = (tk - t[i]) / h if h > 0 else 0.0
            out[k] = y[i] + u * (y[i + 1] - y[i])
            continue
        s = min(max(i - 1, 0), N - 4)
        x0, x1, x2, x3 = t[s], t[s + 1], t[s + 2], t[s + 3]
        l0 = (tk - x1) * (tk - x2) * (tk - x3) / ((x0 - x1) * (x0 - x2) * (x0 - x3))
        l1 = (tk - x0) * (tk - x2) * (tk - x3) / ((x1 - x0) * (x1 - x2) * (x1 - x3))
        l2 = (tk - x0) * (tk - x1) * (tk - x3) / ((x2 - x0) * (x2 - x1) * (x2 - x3))
        l3 = (tk - x0) * (tk - x1) * (tk - x2) / ((x3 - x0) * (x3 - x1) * (x3 - x2))
        out[k] = l0 * y[s] + l1 * y[s + 1] + l2 * y[s + 2] + l3 * y[s + 3]
    return out


def leggi_wrdata(path, dtmin, t_fine):
    """wrdata di ngspice: 't v1 t v2 t v3 ...' -> colonne ricampionate."""
    t = []
    cols = None
    with open(path) as f:
        for line in f:
            p = line.split()
            if not p:
                continue
            try:
                v = [float(x) for x in p]
            except ValueError:
                continue
            if cols is None:
                cols = [[] for _ in v[1::2]]
            if t and v[0] <= t[-1]:
                # tempo ripetuto a un breakpoint: tiene l'ultimo valore
                for k, c in enumerate(cols):
                    c[-1] = v[1 + 2 * k]
                continue
            t.append(v[0])
            for k, c in enumerate(cols):
                c.append(v[1 + 2 * k])
    if not t:
        raise SystemExit("ERRORE: nessun dato in %s" % path)
    t, cols = dirada(t, cols, dtmin)
    return [ricampiona(t, c, t_fine) for c in cols], t[-1]


# ------------------------------------------------------------------ fit C ----
def residuo_c(x, f):
    """x - (a sin + b cos) su finestra centrata di 10 ms; ritorna (r, i0, i1, cond)."""
    n = len(x)
    nw = CAMPIONI_C
    h = nw // 2
    fine = n - (nw - h)
    if "senza_fit" in SABOTA:
        return list(x), h, fine, 1.0
    if "fit_perfetto" in SABOTA:
        return [0.0] * n, h, fine, 1.0
    if "freq_sbagliata" in SABOTA:
        f = f * 1.01
    w = 2 * math.pi * f / FS
    s = [math.sin(w * i) for i in range(n)]
    c = [math.cos(w * i) for i in range(n)]
    pss = [0.0] * (n + 1)
    psc = [0.0] * (n + 1)
    pcc = [0.0] * (n + 1)
    pxs = [0.0] * (n + 1)
    pxc = [0.0] * (n + 1)
    a1 = a2 = a3 = a4 = a5 = 0.0
    for i in range(n):
        si, ci, xi = s[i], c[i], x[i]
        a1 += si * si
        a2 += si * ci
        a3 += ci * ci
        a4 += xi * si
        a5 += xi * ci
        pss[i + 1], psc[i + 1], pcc[i + 1], pxs[i + 1], pxc[i + 1] = a1, a2, a3, a4, a5
    r = [0.0] * n
    cond = 1.0
    for i in range(h, fine):
        lo, hi = i - h, i - h + nw
        Sss = pss[hi] - pss[lo]
        Ssc = psc[hi] - psc[lo]
        Scc = pcc[hi] - pcc[lo]
        Sxs = pxs[hi] - pxs[lo]
        Sxc = pxc[hi] - pxc[lo]
        det = Sss * Scc - Ssc * Ssc
        a = (Sxs * Scc - Sxc * Ssc) / det
        b = (Sxc * Sss - Sxs * Ssc) / det
        r[i] = x[i] - (a * s[i] + b * c[i])
        if (i - h) % 97 == 0:
            tr2 = (Sss + Scc) / 2
            disc = math.sqrt(max(tr2 * tr2 - det, 0.0))
            lmin = tr2 - disc
            cnd = (tr2 + disc) / lmin if lmin > 0 else float("inf")
            cond = max(cond, cnd)
    return r, h, fine, cond


def c_picchi(x, f, eventi, durata=0.0):
    """Picco di C per evento, in [te - 20 ms, te + durata + 200 ms].
    durata = t_grad: un elemento graduale si guarda per tutta la dissolvenza."""
    r, i0, i1, cond = residuo_c(x, f)
    y = filtra(r, i0)
    out = []
    for te in eventi:
        a = max(int(round((te - 0.020) * FS)), i0)
        b = min(int(round((te + durata + 0.200) * FS)), i1)
        if b <= a:
            out.append((None, None))
            continue
        # il filtro parte a i0: i primi 0,3 s dopo i0 sono assestamento
        out.append(picco(y, a, b))
    return out, cond


def c2_picchi(x_ev, x_rif, f, eventi, durata=0.0):
    """C2 - il VERDETTO di C (ADR-035, scelta dell'utente il 2026-09-16).

        C2(t) = [v_ev(t) - tono_fit_ev(t)] - [v_rif(t) - tono_fit_rif(t)]

    cioe' la differenza dei residui del fit fra la corsa con l'evento e la
    corsa di riferimento, sulla stessa griglia a 96 kHz, filtrata dopo.

    PERCHE' NON LA DIFFERENZA CRUDA. Una differenza v_ev - v_rif respingerebbe
    OGNI mute, anche uno infinitamente lento: un mute toglie per forza volt di
    musica, e quel residuo sta alla frequenza del tono, non a 1/T, quindi il
    passa-alto a 20 Hz non lo tocca. E' esattamente il problema che il fit di
    ADR-032 esisteva per evitare. Sottraendo invece i due RESIDUI: la
    distorsione di regime, identica nelle due corse, si cancella; una
    dissolvenza lenta resta dentro il fit e passa; un taglio netto sopravvive.

    PERCHE' NON SERVE FITTARE LE ARMONICHE QUI. La differenza dal riferimento
    cancella OGNI contenuto di regime, non le prime venti armoniche soltanto:
    sottrae piu' di quanto un fit armonico sottrarrebbe. Il fit armonico resta
    come diagnostica nel sottocomando `armoniche`.

    Il riferimento e' quello di A: tiene dall'inizio lo stato FINALE
    dell'evento. La finestra straddle l'evento, quindi i ~20 ms prima non si
    cancellano: per questo il pavimento di C2 si MISURA (celle pav_nullo_*) e
    si riporta accanto a ogni verdetto, invece di assumerlo nullo.
    """
    return c2_da_residui(residuo_c(x_ev, f), residuo_c(x_rif, f), eventi, durata,
                         len(x_rif))


def c2_da_residui(res_ev, res_rif, eventi, durata=0.0, n_rif=0):
    """Il nucleo di C2, sui residui gia' calcolati: `analizza` li tiene in cache
    perche' ogni riferimento serve a piu' eventi e a tre uscite."""
    r_ev, i0, i1, cond_ev = res_ev
    r_rif, j0, j1, cond_rf = res_rif
    if "c2_senza_riferimento" in SABOTA:
        # C2 ricade su C1: la distorsione di regime torna nel residuo
        r_rif, j0, j1, cond_rf = [0.0] * (n_rif or len(r_rif)), i0, i1, 1.0
    if "rif_sfasato" in SABOTA:
        r_rif = [r_rif[0]] + r_rif[:-1]
    n = min(len(r_ev), len(r_rif))
    i0 = max(i0, j0)
    i1 = min(i1, j1, n)
    d = [r_ev[i] - r_rif[i] for i in range(n)]
    y = filtra(d, i0)
    out = []
    for te in eventi:
        a = max(int(round((te - 0.020) * FS)), i0)
        b = min(int(round((te + durata + 0.200) * FS)), i1)
        if b <= a:
            out.append((None, None))
            continue
        out.append(picco(y, a, b))
    return out, max(cond_ev, cond_rf)


# --------------------------------------------------------------- A e B ----
def a_picco(ev, rif, t_ev, t_stop):
    if "rif_sfasato" in SABOTA:
        rif = [rif[0]] + rif[:-1]
    n = min(len(ev), len(rif))
    i0 = int(round(t_ev * FS))
    i1 = min(int(round(t_stop * FS)), n)
    d = [ev[i] - rif[i] for i in range(n)]
    y = filtra(d, i0)
    v, i = picco(y, i0, i1)
    return v, i, (i1 - i0) / FS


def b_picco(x, t_da, t_a):
    y = filtra(x, 0)
    return picco(y, int(round(t_da * FS)), int(round(t_a * FS)))


# ----------------------------------------------------------------- canale ----
def estrai_canale(testo):
    righe = testo.splitlines()
    try:
        i0 = next(i for i, l in enumerate(righe) if l.startswith("* >>> CANALE"))
        i1 = next(i for i, l in enumerate(righe) if l.startswith("* <<< CANALE"))
    except StopIteration:
        return None
    return "\n".join(righe[i0:i1 + 1])


def canali_identici(testi):
    if "canale_cieco" in SABOTA:
        return True
    blocchi = [estrai_canale(t) for t in testi]
    if any(b is None for b in blocchi):
        return False
    return all(b == blocchi[0] for b in blocchi)


# --------------------------------------------------------------- sintetici ----
def tono(n, amp, f, fase=0.0):
    w = 2 * math.pi * f / FS
    return [amp * math.sin(w * i + fase) for i in range(n)]


def inviluppo(n, t0, T, forma):
    out = [1.0] * n
    for i in range(n):
        u = (i / FS - t0) / T if T > 0 else (1.0 if i / FS >= t0 else 0.0)
        u = min(max(u, 0.0), 1.0)
        if forma == "coseno":
            out[i] = 0.5 + 0.5 * math.cos(math.pi * u)
        elif forma == "lineare":
            out[i] = 1.0 - u
        else:  # netto
            out[i] = 0.0 if i / FS >= t0 else 1.0
    return out


def c_dissolvenza(f, T, forma, amp=1.0, t0=0.4):
    """Residuo C (picco) di un tono che si dissolve in T a partire da t0."""
    n = int((t0 + T + 0.4) * FS)
    x = tono(n, amp, f, fase=math.pi / 2 - 2 * math.pi * f * t0)
    env = inviluppo(n, t0, T, forma)
    x = [a * b for a, b in zip(x, env)]
    r, i0, i1, cond = residuo_c(x, f)
    y = filtra(r, i0)
    a = max(int(round((t0 - 0.02) * FS)), i0)
    b = min(int(round((t0 + T + 0.2) * FS)), i1)
    return picco(y, a, b)[0], cond


# ---------------------------------------------------------------- autotest ----
def autotest():
    esiti = []

    def verifica(nome, ok, dettaglio):
        esiti.append(ok)
        print("%-4s %-58s %s" % ("OK" if ok else "CADE", nome, dettaglio))

    print("# autotest di v2_metodo.py - cifre CALCOLATE su segnali sintetici, nessun circuito")
    print("# sabotaggi attivi: %s" % (", ".join(sorted(SABOTA)) or "nessuno"))

    # T1 - incrocio con calcolo_v2.out.txt (L38), 2 ordine
    n = int(1.5 * FS)
    gr = [0.104 if i / FS >= 0.1 else 0.0 for i in range(n)]
    rp = [0.104 * min(max((i / FS - 0.1) / 0.5, 0.0), 1.0) for i in range(n)]
    pg = picco(filtra(gr), 0, n)[0]
    pr = picco(filtra(rp), 0, n)[0]
    verifica("T1 gradino 104 mV = 0.1109 V (calcolo_v2)", "%.4g" % pg == "0.1109", "%.6g V" % pg)
    verifica("T1 rampa 104 mV/500 ms = 0.0007547 V (calcolo_v2)", "%.4g" % pr == "0.0007547", "%.6g V" % pr)
    rapporto = pg / 0.104

    # T2 - gradino noto da 1 mV sotto la musica, A come differenza dal riferimento
    n = int(1.3 * FS)
    rif = tono(n, 12.0, 1000.0)
    ev = [v + (1e-3 if i / FS >= 1.0 else 0.0) for i, v in enumerate(rif)]
    va, _, _ = a_picco(ev, rif, 1.0, 1.3)
    verifica("T2 A di un gradino da 1 mV sotto 12 V a 1 kHz = 1 mV x %.4f" % rapporto,
             abs(va / 1e-3 - rapporto) < 1e-3 * rapporto, "%.6g V" % va)

    # T3 - evento identico al riferimento
    va, _, _ = a_picco(list(rif), rif, 1.0, 1.3)
    verifica("T3 A con evento identico al riferimento = 0", va == 0.0, "%.3g V" % va)

    # T4 - dissolvenza lenta: 5 s a coseno rialzato, 12 V pk. A 20 Hz nessuna
    # dissolvenza di durata ragionevole passa (vedi caratterizza): la riga e'
    # informativa, e il limite va all'utente, non dentro un controllo verde.
    # Il residuo scende solo come 1/T (caratterizza): a 1 kHz passa una
    # dissolvenza di 10 s a 3,82 V pk (il livello delle fisse), non una di 5 s a
    # 12 V (302 uV).
    for f in (1000.0, 20000.0):
        v, cond = c_dissolvenza(f, 10.0, "coseno", amp=3.818)
        verifica("T4 dissolvenza di 10 s, 3,82 V pk, %g Hz passa C" % f, v <= SOGLIA,
                 "%.3g V (cond %.3g)" % (v, cond))
    v, cond = c_dissolvenza(20.0, 5.0, "coseno", amp=12.0)
    print("     LIMITE DEL METODO: dissolvenza di 5 s, 12 V pk, 20 Hz: C = %.3g V (cond %.3g)" % (v, cond))

    # T5 - taglio netto sul picco
    for f in (20.0, 1000.0, 20000.0):
        v, cond = c_dissolvenza(f, 0.0, "netto", amp=12.0)
        verifica("T5 taglio netto, 12 V pk, %g Hz cade su C" % f, v > 1000 * SOGLIA,
                 "%.3g V" % v)

    # T6 - tono stazionario a 20 Hz: il fit mal condizionato ricostruisce ancora
    n = int(1.0 * FS)
    x = tono(n, 12.0, 20.0, 0.3)
    r, i0, i1, cond = residuo_c(x, 20.0)
    v = picco(r, i0, i1)[0]
    verifica("T6 tono stazionario 12 V a 20 Hz: residuo del fit <= 1 uV", v <= 1e-6,
             "%.3g V, numero di condizione %.4g" % (v, cond))
    for f in (1000.0, 20000.0):
        _, _, _, cnd = residuo_c(tono(int(0.05 * FS), 1.0, f), f)
        print("     numero di condizione del fit a %g Hz: %.4g" % (f, cnd))

    # T7 - ricampionamento su griglia non uniforme alla ngspice
    def griglia(tmax, durata):
        t, k = [0.0], 0
        while t[-1] < durata:
            k += 1
            passo = tmax * (0.55 + 0.45 * math.sin(0.37 * k) ** 2)
            t.append(t[-1] + passo)
            if k % 1000 == 500:
                t.append(t[-1] + 1e-12)   # coppia quasi coincidente, come ai breakpoint
        return t

    for f, tmax, lim in ((1000.0, 10e-6, 10e-6), (20000.0, 0.5e-6, 10e-6), (20000.0, 10e-6, None)):
        t = griglia(tmax, 0.02)
        # +-1 uV di rumore deterministico: e' l'ordine dell'errore del solutore
        # (reltol 1e-6 su 12 V). Su campioni esatti una coppia a 1e-12 s non
        # guasta Lagrange; su campioni col loro errore si' - ed e' il caso vero.
        y = [12.0 * math.sin(2 * math.pi * f * tt) + 1e-6 * math.sin(7919.0 * k)
             for k, tt in enumerate(t)]
        tt2, cc = dirada(t, [y], tmax / 5)
        z = ricampiona(tt2, cc[0], 0.019)
        err = max(abs(z[k] - 12.0 * math.sin(2 * math.pi * f * k / FS)) for k in range(len(z)))
        if lim is None:
            print("     ricampionamento %g Hz con passi da %g s: errore %.3g V (informativo)" % (f, tmax, err))
        else:
            verifica("T7 ricampionamento 12 V %g Hz, passi <= %g s: errore <= 10 uV" % (f, tmax),
                     err <= lim, "%.3g V" % err)

    # T8 - identita' del canale
    d1 = "titolo\n* >>> CANALE\nR1 a b 1k\n* <<< CANALE\n.control\n"
    d2 = "altro\n* >>> CANALE\nR1 a b 1k\n* <<< CANALE\n.endc\n"
    d3 = "altro\n* >>> CANALE\nR1 a b 1.1k\n* <<< CANALE\n"
    verifica("T8 canale: due deck uguali nel blocco passano", canali_identici([d1, d2]), "")
    verifica("T8 canale: un valore diverso nel blocco cade", not canali_identici([d1, d3]), "")

    # T9 - C2 cancella la distorsione di REGIME, C1 no. E' la ragione per cui
    # C2 e' il verdetto (ADR-035): con h2 a 900 uV su una corsa senza nessun
    # evento, C1 la conta tutta e boccerebbe un circuito fermo.
    n = int(1.6 * FS)
    f = 1000.0
    rif_d = [a + b for a, b in zip(tono(n, 12.0, f), tono(n, 900e-6, 2 * f, 0.7))]
    ev_d = list(rif_d)
    pk1, _ = c_picchi(ev_d, f, [1.0])
    v1 = pk1[0][0]
    pk2, _ = c2_picchi(ev_d, rif_d, f, [1.0])
    v2 = pk2[0][0]
    verifica("T9 C1 conta la distorsione di regime (h2 900 uV) >= 500 uV", v1 >= 500e-6,
             "C1 = %.3g V" % v1)
    verifica("T9 C2 la cancella: corsa identica al riferimento = 0", v2 == 0.0,
             "C2 = %.3g V" % v2)

    # T10 - C2 di una dissolvenza a coseno rialzato da 3 s, 12 V pk, 1 kHz:
    # passa la soglia di C. E' la rampa aggiunta al deck graduale.
    def c2_dissolvenza(f, T, forma, amp, t0=0.4):
        m = int((t0 + T + 0.4) * FS)
        base = tono(m, amp, f, fase=math.pi / 2 - 2 * math.pi * f * t0)
        env = inviluppo(m, t0, T, forma)
        ev = [a * b for a, b in zip(base, env)]
        pk, cnd = c2_picchi(ev, base, f, [t0], durata=T)
        return pk[0][0], cnd

    v, cond = c2_dissolvenza(1000.0, 3.0, "coseno", 12.0)
    verifica("T10 C2 dissolvenza 3 s a coseno, 12 V pk, 1 kHz passa (<= 1 mV)",
             v is not None and v <= SOGLIA_C, "%.3g V (cond %.3g)" % (v, cond))

    # T11 - C2 di un taglio netto a 12 V cade, alle tre frequenze
    for f in (20.0, 1000.0, 20000.0):
        v, cond = c2_dissolvenza(f, 0.0, "netto", 12.0)
        verifica("T11 C2 taglio netto, 12 V pk, %g Hz cade" % f,
                 v is not None and v > 100 * SOGLIA_C, "%.3g V" % v)

    # T13 - C2 al RILASCIO, col riferimento "mai in mute". Prima dell'evento le
    # due corse sono in stati DIVERSI per costruzione: quella con l'evento e' in
    # mute, il riferimento suona. La finestra di C2 comincia 20 ms prima
    # dell'evento, quindi quei 20 ms entrano nel picco. Il fit toglie il tono da
    # entrambe, percio' cio' che resta non e' il segnale ma la DISTORSIONE del
    # riferimento: qui, su un tono sintetico senza distorsione, dev'essere
    # trascurabile. Sul circuito vero vale il pavimento di C (~1,2 mV sulla
    # principale), ed e' la ragione per cui il pavimento si riporta accanto a
    # ogni C2 invece di essere assunto nullo.
    m = int((0.4 + 3.0 + 0.4) * FS)
    f = 1000.0
    rif_r = tono(m, 12.0, f, fase=math.pi / 2 - 2 * math.pi * f * 0.4)
    env_out = inviluppo(m, 0.4, 3.0, "coseno")
    ev_r = [a * (1.0 - b) for a, b in zip(rif_r, env_out)]   # dissolvenza in salita
    pk_r, cond_r = c2_picchi(ev_r, rif_r, f, [0.4], durata=3.0)
    v_r = pk_r[0][0]
    verifica("T13 C2 di un rilascio graduale da 3 s passa (<= 1 mV)",
             v_r is not None and v_r <= SOGLIA_C, "%.3g V (cond %.3g)" % (v_r, cond_r))

    # T12 - le soglie sono due, e sono quelle di ADR-035
    verifica("T12 soglia di C = 1 mV, di A e B = 100 uV",
             soglia_di("C") == 1e-3 and soglia_di("C2_rel") == 1e-3
             and soglia_di("A") == 100e-6 and soglia_di("B1") == 100e-6,
             "C %.3g V, A %.3g V" % (soglia_di("C"), soglia_di("A")))

    nf = esiti.count(False)
    print("# %d controlli, %d caduti" % (len(esiti), nf))
    return 1 if nf else 0


def sabotaggi():
    rc_tot = 0
    base = subprocess.run([sys.executable, __file__, "autotest"], capture_output=True, text=True)
    print("-- senza sabotaggi: exit %d" % base.returncode)
    print(base.stdout)
    if base.returncode != 0:
        rc_tot = 1
    for s in SABOTAGGI:
        p = subprocess.run([sys.executable, __file__, "autotest", "--sabota", s],
                           capture_output=True, text=True)
        caduti = [l for l in p.stdout.splitlines() if l.startswith("CADE")]
        ok = p.returncode != 0 and caduti
        print("-- sabotaggio %-18s exit %d, %d controlli caduti: %s" %
              (s, p.returncode, len(caduti), "OK" if ok else "NON CADE - IL CONTROLLO NON VEDE"))
        for l in caduti:
            print("     " + l)
        if not ok:
            rc_tot = 1
    return rc_tot


def caratterizza():
    print("# Residuo di C per un tono che si dissolve in T - CALCOLATO sul metodo, nessun circuito")
    print("# picco filtrato per 1 V di picco di tono; e' lineare nell'ampiezza.")
    print("# T_min = durata minima che passa 100 uV, per 12,07 V pk (principale a +10 dB) e 3,82 V pk (fisse)")
    print("# finestra del fit: %d campioni a 96 kHz" % CAMPIONI_C)
    Ts = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0)
    print("forma,f_hz," + ",".join("T%g" % T for T in Ts) + ",Tmin_12V,Tmin_3V82")
    for forma in ("coseno", "lineare"):
        for f in (20.0, 1000.0, 20000.0):
            vals = [c_dissolvenza(f, T, forma)[0] for T in Ts]
            tmins = []
            for amp in (12.07, 3.818):
                tm = "oltre 10 s"
                for T, v in zip(Ts, vals):
                    if v * amp <= SOGLIA:
                        tm = "<= %g s" % T
                        break
                tmins.append(tm)
            print("%s,%g,%s,%s,%s" % (forma, f, ",".join("%.3g" % v for v in vals), tmins[0], tmins[1]))


def armoniche(path, col, f, t0, t1, tmax):
    """Ampiezza di picco delle armoniche 1..20 di una colonna, su [t0, t1).
    Serve a dire DA COSA e' fatto il pavimento di C: se le armoniche 2..7
    spiegano il residuo, il pavimento e' distorsione e non numerica."""
    cols, _ = leggi_wrdata(path, tmax / 5, t1)
    x = cols[col]
    i0, i1 = int(round(t0 * FS)), int(round(t1 * FS))
    n = i1 - i0
    w = 2 * math.pi * f / FS
    print("# armoniche di %s colonna %d (%s), %g Hz, %g-%g s - SIMULATE" % (
        os.path.basename(path), col, USCITE[col], f, t0, t1))
    somma = 0.0
    coeff = {}
    for h in range(1, 21):
        a = sum(x[i] * math.sin(h * w * i) for i in range(i0, i1)) * 2 / n
        b = sum(x[i] * math.cos(h * w * i) for i in range(i0, i1)) * 2 / n
        coeff[h] = (a, b)
        amp = math.hypot(a, b)
        if h > 1:
            somma += amp
        print("h%d  %.4g V di picco" % (h, amp))
    print("somma dei picchi h2..h20 (limite superiore del loro picco combinato): %.4g V" % somma)
    # Composizione del pavimento di C: il metodo sul segnale com'e', e sul
    # segnale a cui si tolgono le armoniche 2..20 stimate su [t0, t1).
    senza = list(x)
    for i in range(len(x)):
        for h in range(2, 21):
            a, b = coeff[h]
            senza[i] -= a * math.sin(h * w * i) + b * math.cos(h * w * i)
    g0, g1 = i0 + int(0.05 * FS), i1 - int(0.05 * FS)
    for nome, sig in (("com'e'", x), ("senza h2..h20", senza)):
        r, ri0, _, _ = residuo_c(sig, f)
        y = filtra(r, ri0)
        pk = picco(y, g0, g1)[0]
        print("C sul segnale %-13s picco in [t0+50 ms, t1-50 ms]: %.4g V" % (nome, pk))
    # Forma nel tempo di cio' che resta: sparso (pochi campioni isolati, firma
    # numerica) o diffuso (un segnale).
    seg = y[g0:g1]
    rms = math.sqrt(sum(v * v for v in seg) / len(seg))
    sopra = sum(1 for v in seg if abs(v) > pk / 2)
    top = sorted(range(len(seg)), key=lambda i: -abs(seg[i]))[:8]
    print("resto senza h2..h20: RMS %.4g V, picco/RMS %.3g, campioni sopra meta' picco %d su %d" % (
        rms, pk / rms if rms > 0 else float("inf"), sopra, len(seg)))
    print("istanti dei picchi piu' alti (s): " + " ".join(
        "%.6f(%.3g)" % ((g0 + i) / FS, seg[i]) for i in sorted(top)))
    # Spettro grossolano del resto filtrato: 25 Hz .. 20 kHz a passi di 25 Hz,
    # ampiezza di picco per proiezione su [t0+50 ms, t1-50 ms). Dice se cio' che
    # resta e' un tono (un'oscillazione, un battimento) o un fondo diffuso.
    m = len(seg)
    righe = []
    for fb in range(25, 20001, 25):
        wb = 2 * math.pi * fb / FS
        a = b = 0.0
        for j in range(m):
            ph = wb * (g0 + j)
            a += seg[j] * math.sin(ph)
            b += seg[j] * math.cos(ph)
        righe.append((2 * math.hypot(a, b) / m, fb))
    righe.sort(reverse=True)
    print("spettro del resto, le 10 righe piu' alte: " + " ".join(
        "%d Hz %.3g V" % (fb, amp_) for amp_, fb in righe[:10]))


def griglia(path, f, amp, t0, t1, tmax):
    """Errore dello STRUMENTO sulla griglia vera di ngspice: gli istanti di un
    .dat, un seno esatto (nessun circuito), diradamento + ricampionamento +
    C. Tutto cio' che esce e' errore del metodo implementato, non del circuito."""
    t = []
    with open(path) as fh:
        for line in fh:
            p = line.split()
            if not p:
                continue
            try:
                tt = float(p[0])
            except ValueError:
                continue
            if t and tt <= t[-1]:
                continue
            t.append(tt)
    passi = sorted(t[i + 1] - t[i] for i in range(len(t) - 1) if t0 <= t[i] < t1)
    print("# griglia di %s su [%g, %g) s: %d passi, min %.3g s, mediana %.3g s, max %.3g s" % (
        os.path.basename(path), t0, t1, len(passi), passi[0], passi[len(passi) // 2], passi[-1]))
    w = 2 * math.pi * f
    y = [amp * math.sin(w * tt + math.pi / 2) for tt in t]
    tt2, cc = dirada(t, [y], tmax / 5)
    z = ricampiona(tt2, cc[0], t1)
    err = max(abs(z[k] - amp * math.sin(w * k / FS + math.pi / 2))
              for k in range(int(t0 * FS), len(z)))
    r, ri0, _, _ = residuo_c(z, f)
    yy = filtra(r, ri0)
    g0, g1 = int((t0 + 0.05) * FS), min(len(yy), int((t1 - 0.05) * FS))
    print("seno esatto da %g V a %g Hz: errore massimo del ricampionamento %.4g V" % (amp, f, err))
    print("C del seno esatto su quella griglia, picco in [t0+50 ms, t1-50 ms]: %.4g V - CALCOLATO" % picco(yy, g0, g1)[0])


# ----------------------------------------------------------------- analizza ----
def analizza(manifest, datadir, outpath):
    with open(manifest) as f:
        celle = list(csv.DictReader(f))
    per_nome = {c["cella"]: c for c in celle}
    # LRU di 6 celle: un manifesto da ~90 corse terrebbe altrimenti in memoria
    # ~3 GB di colonne ricampionate.
    cache = {}
    ordine = []

    def dati(c):
        k = c["cella"]
        if k in cache:
            ordine.remove(k)
            ordine.append(k)
            return cache[k]
        tmax = float(c["tmax"])
        cols, tend = leggi_wrdata(os.path.join(datadir, c["file"]), tmax / 5, float(c["t_fine"]))
        cache[k] = (cols, tend)
        ordine.append(k)
        while len(ordine) > 6:
            vecchia = ordine.pop(0)
            del cache[vecchia]
            for kk in [q for q in rordine if q[0] == vecchia]:
                rordine.remove(kk)
                del rcache[kk]
        return cache[k]

    # I residui del fit costano quanto tutto il resto messo insieme, e C2 di
    # ogni cella ne vuole tre (la cella, il riferimento dell'inserzione, quello
    # del rilascio) per ognuna delle tre uscite. Senza questa cache un
    # manifesto da ~200 corse impiega ore: i riferimenti verrebbero rifatti per
    # ogni evento. Stessa disciplina LRU di `cache`.
    rcache = {}
    rordine = []

    def residuo_di(nome, k, x, f):
        key = (nome, k)
        if key in rcache:
            rordine.remove(key)
            rordine.append(key)
            return rcache[key]
        rcache[key] = residuo_c(x, f)
        rordine.append(key)
        while len(rordine) > 18:
            del rcache[rordine.pop(0)]
        return rcache[key]

    righe = []

    def scrivi(c, gr, u, v, i, fin, nota):
        if v is None:
            esito = "n/d"
        elif v > soglia_di(gr):
            esito = "SOPRA"
        elif fin is not None and fin < DURATA_A - 1e-9:
            esito = "sotto, finestra corta: non accetta"
        else:
            esito = "sotto"
        righe.append([c["cella"], c["variante"], c["f_hz"], c["amp"], c["gm"], c["rl"], gr, u,
                      "" if v is None else "%.4g" % v,
                      "" if i is None else "%.6f" % (i / FS),
                      "" if fin is None else "%.3f" % fin, esito, nota])

    for c in celle:
        cols, tend = dati(c)
        t_fine = min(float(c["t_fine"]), tend)
        t_ins, t_rel = float(c["t_ins"]), float(c["t_rel"])
        tg = float(c.get("t_grad") or 0.0)
        f = float(c["f_hz"])
        amp = float(c["amp"])
        tipo = c["tipo"]
        for k, u in enumerate(USCITE):
            x = cols[k]
            if tipo == "rif_sempre":
                v, i = b_picco(x, 0.5, t_fine)
                scrivi(c, "B1", u, v, i, None, "riferimento sempre in mute, da 0,5 s")
            # Il pavimento di C e' della corsa MAI in mute: in quella sempre in
            # mute il C misura il residuo in mute (gia' B1), non un pavimento.
            if tipo == "rif_mai" and amp > 0:
                ev = [te for te in (t_ins, t_rel) if 0.3 < te < t_fine]
                if ev:
                    pk, cond = c_picchi(x, f, ev)
                    for te, (v, i) in zip(ev, pk):
                        scrivi(c, "C_pav", u, v, i, None,
                               "pavimento di C a %.3f s, cond %.3g" % (te, cond))
            if tipo == "pav_num":
                # pavimento numerico: la stessa corsa con un altro TMAX, letta come A
                rcols, _ = dati(per_nome[c["rif_ins"]])
                v, i, fin = a_picco(x, rcols[k], t_ins, min(t_ins + DURATA_A, t_fine))
                scrivi(c, "A_pav", u, v, i, fin, "contro %s" % c["rif_ins"])
                # e lo stesso evento nullo letto come C2: e' il pavimento del
                # VERDETTO di C, quello che va riportato accanto a ogni C2
                if amp > 0:
                    ev = [te for te in (t_ins,) if 0.3 < te < t_fine]
                    if ev:
                        pk, cond = c2_picchi(x, rcols[k], f, ev)
                        for te, (v2, i2) in zip(ev, pk):
                            scrivi(c, "C2_pav", u, v2, i2, None,
                                   "pavimento di C2 contro %s, cond %.3g"
                                   % (c["rif_ins"], cond))
                continue
            if tipo != "evento":
                continue
            for nome, te, rif_k, t_stop in (("A_ins", t_ins, "rif_ins", min(t_rel, t_ins + DURATA_A)),
                                            ("A_rel", t_rel, "rif_rel", t_rel + DURATA_A)):
                rn = c.get(rif_k, "-")
                if rn in ("", "-") or not (0 < te < t_fine):
                    continue
                rcols, _ = dati(per_nome[rn])
                v, i, fin = a_picco(x, rcols[k], te, min(t_stop, t_fine))
                scrivi(c, nome, u, v, i, fin, "riferimento %s" % rn)
            if 0 < t_ins < t_fine:
                v, i = b_picco(x, t_ins + tg + 0.020, min(t_rel, t_fine))
                scrivi(c, "B2", u, v, i, None, "mute da t_ins+t_grad+20 ms a t_rel")
            if amp > 0:
                ev = [te for te in (t_ins, t_rel) if 0.3 < te < t_fine]
                # C1: il fit della sola fondamentale, com'e' in ADR-032.
                # DIAGNOSTICA, non piu' il verdetto: porta dentro tutta la
                # distorsione di regime del circuito (h2 da solo vale 887 uV
                # su una corsa mai in mute, L29a).
                pk, cond = c_picchi(x, f, ev, tg)
                for te, (v, i) in zip(ev, pk):
                    nm = "C1_ins" if te == t_ins else "C1_rel"
                    scrivi(c, nm, u, v, i, None, "diagnostica, cond %.3g" % cond)
                # C2: il VERDETTO (ADR-035). Stesso riferimento di A.
                res_ev = residuo_di(c["cella"], k, x, f)
                for nm, te, rif_k in (("C2_ins", t_ins, "rif_ins"),
                                      ("C2_rel", t_rel, "rif_rel")):
                    rn = c.get(rif_k, "-")
                    if rn in ("", "-") or not (0.3 < te < t_fine):
                        continue
                    rcols, _ = dati(per_nome[rn])
                    res_rf = residuo_di(rn, k, rcols[k], f)
                    pk2, cond2 = c2_da_residui(res_ev, res_rf, [te], tg)
                    v2, i2 = pk2[0]
                    scrivi(c, nm, u, v2, i2, None,
                           "riferimento %s, cond %.3g" % (rn, cond2))
    with open(outpath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cella", "variante", "f_hz", "amp", "gm", "rl", "grandezza", "uscita",
                    "picco_V", "t_picco_s", "finestra_s", "esito", "nota"])
        w.writerows(righe)
    print("%d righe -> %s" % (len(righe), outpath))
    return 0


def riassumi(ingressi, out):
    """Dalle tabelle di analizza: per variante x carico x grandezza x uscita il
    picco massimo e la cella che lo produce; poi il verdetto per variante.
    A = A_ins, A_rel; B = B1, B2 (riportate anche separate); C = C2_ins, C2_rel.
    Una variante e' RESPINTA se una sola riga A, B o C sta SOPRA la soglia
    della sua grandezza (100 uV per A e B, 1 mV per C - ADR-035); non e' mai
    'conforme' da qui: lo screening non copre la matrice di V2.
    C1 e i pavimenti (A_pav, C_pav, C2_pav) sono DIAGNOSTICI: entrano nella
    tabella ma non nel verdetto."""
    righe = []
    for p in ingressi:
        with open(p) as f:
            righe += list(csv.DictReader(f))
    grp = {}
    for r in righe:
        g = r["grandezza"]
        base = {"A_ins": "A", "A_rel": "A",
                "C2_ins": "C", "C2_rel": "C",
                "C1_ins": "C1", "C1_rel": "C1"}.get(g, g)
        if not r["picco_V"]:
            continue
        chiave = (r["variante"], r["rl"], base, r["uscita"])
        v = float(r["picco_V"])
        if chiave not in grp or v > grp[chiave][0]:
            grp[chiave] = (v, r["cella"], g, r["esito"])
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["variante", "rl", "grandezza", "uscita", "picco_max_V", "cella", "da", "esito"])
        for k in sorted(grp):
            v, cella, g, es = grp[k]
            w.writerow(list(k) + ["%.4g" % v, cella, g, es])
    verd = {}
    for (var, rl, base, u), (v, cella, g, es) in grp.items():
        if base in ("A", "B1", "B2", "C") and v > soglia_di(base):
            verd.setdefault(var, []).append("%s %s %s %.3g V (%s)" % (base, u, rl, v, cella))
    print("# verdetto dello screening - SIMULATO; A e B 100 uV, C 1 mV (ADR-035)")
    for var in sorted({k[0] for k in grp}):
        if var == "nessuna":
            continue
        sopra = verd.get(var, [])
        if sopra:
            peggiore = max(sopra, key=lambda s: float(s.split(" V (")[0].split()[-1]))
            print("%-24s RESPINTA: %d righe sopra soglia; la peggiore: %s" % (var, len(sopra), peggiore))
        else:
            print("%-24s nessuna riga sopra soglia nello screening (NON e' conformita')" % var)
    return 0


def main(argv):
    global CAMPIONI_C
    if "--campioni" in argv:
        i = argv.index("--campioni")
        CAMPIONI_C = int(argv[i + 1])
        del argv[i:i + 2]
    if "--sabota" in argv:
        i = argv.index("--sabota")
        nome = argv[i + 1]
        if nome not in SABOTAGGI:
            raise SystemExit("sabotaggio sconosciuto: %s" % nome)
        SABOTA.add(nome)
        del argv[i:i + 2]
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "autotest":
        return autotest()
    if cmd == "sabotaggi":
        return sabotaggi()
    if cmd == "caratterizza":
        caratterizza()
        return 0
    if cmd == "canale":
        testi = [open(p).read() for p in argv[2:]]
        ok = len(testi) >= 2 and canali_identici(testi)
        print("canale identico in %d deck: %s" % (len(testi), "OK" if ok else "NO"))
        return 0 if ok else 1
    if cmd == "analizza":
        return analizza(argv[2], argv[3], argv[4])
    if cmd == "riassumi":
        return riassumi(argv[2:-1], argv[-1])
    if cmd == "griglia":
        griglia(argv[2], float(argv[3]), float(argv[4]), float(argv[5]), float(argv[6]),
                float(argv[7]))
        return 0
    if cmd == "armoniche":
        armoniche(argv[2], int(argv[3]), float(argv[4]), float(argv[5]), float(argv[6]),
                  float(argv[7]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
