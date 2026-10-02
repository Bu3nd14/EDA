"""comune.py - L47b1, la prova del mute: JFET contro fotoresistenza sullo stesso banco.

Le parti comuni: i percorsi, i modelli degli angoli del JFET (copie RINOMINATE, limitations #29),
le due celle come righe di netlist, il comando in funzione della profondita' d, l'esecuzione di
ngspice con la guardia sui log (#22 #29 #33 #35 #36 #38 #40).

IL BANCO E' RIDOTTO, e lo dice: sorgente -> cella del mute -> ingresso del blocco A (R_IN 1 Mohm
verso massa, gain_block.py). Si misura v(AIN). Gli stadi a valle sono lineari rispetto al mute:
il salto di livello e la distorsione della cella si vedono gia' qui. Il livello al jack si
ricava col guadagno massimo del percorso (x3,15, +10 dB: ADR-038 «Rumore, calcolato»). La corsa
sul preamp intero, col relè al jack e il caso peggiore di V2, e' di L47b2 sulla cella scelta.

Stdlib soltanto: si esegue con /usr/bin/python3 (come scripts/v2_metodo.py).
"""
import math
import os
import re
import subprocess

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(QUI, *[".."] * 6))
NGSPICE = "/opt/homebrew/bin/ngspice"
JFET_LIB = os.path.join(REPO, "models", "jfet", "mmbfj112.lib")
NSL_LIB = os.path.join(REPO, "models", "optocoupler", "nsl32sr3_comportamentale.lib")
INC = os.path.join(QUI, "inc")
ANGOLI_LIB = os.path.join(INC, "jfet_angoli.lib")

A_PIENO = 3.818          # 2,7 V RMS alla sorgente, il tono di prova di V2 (genera_tb_v2_casopeggiore.py)
G_JACK = 3.15            # +10 dB, il guadagno massimo dall'ingresso del blocco A al jack principale
VRAIL = 15.0
OPZIONI = ".options reltol=1e-6 vntol=1e-6 abstol=1e-12"   # quelle del modello NSL (L47a, #40)

# ---------------------------------------------------------------- gli angoli del JFET
# Datasheet onsemi MMBFJ113/D Rev. 5 (vendor/jfet/onsemi/MMBFJ111_112_113/mmbfj113-d.pdf, p. 2),
# tipo 112: VGS(off) da -1,0 a -5,0 V; IDSS >= 5 mA (nessun massimo); rDS(on) <= 50 ohm.
# Il modello del costruttore ha rDS(on) = 1/(2 BETA |VTO|) = 59,5 ohm, sopra il massimo: lo si
# tiene (e' il caso peggiore per rumore e distorsione) e lo si conserva agli angoli, muovendo
# BETA con VTO. Agli estremi IDSS = BETA VTO^2 vale 8,4 mA (VTO -1) e 42 mA (VTO -5).
VTO_TIP = -1.68
BETA_TIP = 5.002e-3
K_RON = 2 * BETA_TIP * abs(VTO_TIP)          # 1/rDS(on) di canale, tenuto costante
ANGOLI = {
    "TIP": (VTO_TIP, BETA_TIP),
    "VLO": (-1.0, K_RON / 2 / 1.0),
    "VHI": (-5.0, K_RON / 2 / 5.0),
}


def scheda_jfet():
    """Le righe .MODEL MMBFJ112 + continuazioni, lette dal file di models/ (mai modificato)."""
    righe = open(JFET_LIB, "rb").read().decode("latin-1").splitlines()
    i = next(k for k, r in enumerate(righe) if r.upper().startswith(".MODEL MMBFJ112 "))
    out = [righe[i]]
    for r in righe[i + 1:]:
        if not r.startswith("+"):
            break
        out.append(r)
    return out


def scrivi_angoli():
    """inc/jfet_angoli.lib: una copia rinominata per angolo, VTO e BETA sostituiti, il resto
    identico. Rinominare invece di altermod: un nome sbagliato fallisce forte (#29)."""
    base = " ".join(scheda_jfet())
    base = base.replace("+", " ")
    corpo = re.sub(r"^\.MODEL\s+MMBFJ112\s+NJF", "", base, flags=re.I).strip()
    corpo = re.sub(r"\b(VTO|BETA)\s*=\s*\S+", "", corpo, flags=re.I)
    corpo = " ".join(corpo.split())
    os.makedirs(INC, exist_ok=True)
    out = ["* jfet_angoli.lib - GENERATO da banco/comune.py (L47b1). Non si edita.",
           "* Copie RINOMINATE della scheda onsemi MMBFJ112 di models/jfet/mmbfj112.lib, con VTO e",
           "* BETA sostituiti; ogni altro parametro identico. rDS(on) di canale tenuto a 59,5 ohm.",
           ""]
    for nome, (vto, beta) in ANGOLI.items():
        out.append(".MODEL MMBFJ112_%s NJF VTO=%.4f BETA=%.5E" % (nome, vto, beta))
        parole = corpo.split()
        for k in range(0, len(parole), 6):
            out.append("+ " + " ".join(parole[k:k + 6]))
        out.append("")
    open(ANGOLI_LIB, "w").write("\n".join(out))
    return ANGOLI_LIB


# ---------------------------------------------------------------- le celle
# GEOMETRIA (ADR-038, NEXT-SESSION L47b): un elemento in serie fra il connettore selezionato
# (SRCX) e l'ingresso del blocco A (AIN), uno verso massa su AIN; R_IN 1 Mohm a massa.
#
# IL CORRETTIVO del JFET: due resistenze uguali RD dal gate a drain e source riportano sul gate
# meta' della tensione drain-source; il comando entra da RC. Il gate vale
#   Vg = k (Vd + Vs)/2 + (1 - k) Vc,   k = RC / (RC + RD/2)
# k = 1 e' il correttivo pieno (ma il comando arriva attenuato a zero); k = 0 nessun correttivo.
# Con un comando da 0 a -15 V il gate arriva a -(1-k) 15 V: il JFET in serie deve restare spento
# col picco del segnale (3,8 V) e VGS(off) fino a -5 V, e questo limita k.
CORRETTIVI = {
    # nome: (RD, RC)
    "nessuno": (None, "100k"),
    "k030": ("1MEG", "220k"),
    "k048": ("1MEG", "470k"),
}

# IL COMANDO: d da 0 (in gioco) a 1 (in mute), lo stesso ordine di ADR-038: prima la serie si
# apre (d 0 -> 0,5), poi la derivazione si chiude (d 0,5 -> 1). Due tensioni di comando
#   serie:       Vcs = -15 * clip(d / 0,5)
#   derivazione: Vcp = -15 * (1 - clip((d - 0,5) / 0,5))
# Dopo un filtro RC sulla scheda audio (RF, CF): tiene fuori dal gate il rumore del comando.
RF, CF = "100k", "100n"    # tau 10 ms


def clip(x):
    return min(max(x, 0.0), 1.0)


def comandi(d, ordine="serie_prima"):
    if ordine == "insieme":
        return -VRAIL * clip(d), -VRAIL * (1 - clip(d))
    return -VRAIL * clip(d / 0.5), -VRAIL * (1 - clip((d - 0.5) / 0.5))


def cella_jfet(ms, mp, corr, vcs="DC 0", vcp="DC -15"):
    rd, rc = CORRETTIVI[corr]
    r = [
        "* ---- la cella a JFET: serie %s, derivazione %s, correttivo %s ----" % (ms, mp, corr),
        "JS AIN GS SRCX MMBFJ112_%s" % ms,
        "JP AIN GP 0 MMBFJ112_%s" % mp,
        "RCS GS CSF %s" % rc,
        "RCP GP CPF %s" % rc,
        "RFS CS CSF %s" % RF, "CFS CSF 0 %s" % CF,
        "RFP CP CPF %s" % RF, "CFP CPF 0 %s" % CF,
        "VCS CS 0 %s" % vcs,
        "VCP CP 0 %s" % vcp,
    ]
    if rd is not None:
        r += ["RS1 GS SRCX %s" % rd, "RS2 GS AIN %s" % rd,
              "RP1 GP AIN %s" % rd, "RP2 GP 0 %s" % rd]
    return r


# Il comando delle LDR: il profilo v4 di ADR-040 (genera_tb_v2_casopeggiore.py), in funzione di d.
ION, IRIP = 20e-3, 10e-9
SERIE_V4 = [(0, ION), (0.1, 0.2e-3), (0.45, 4.5e-6), (0.75, 0.19e-6), (0.8, IRIP), (1, IRIP)]


def correnti_ldr(d):
    lg = math.log10
    for (d0, i0), (d1, i1) in zip(SERIE_V4, SERIE_V4[1:]):
        if d0 <= d <= d1:
            u = (d - d0) / (d1 - d0)
            iserie = 10 ** (lg(i0) + u * (lg(i1) - lg(i0)))
            break
    ideriv = IRIP * (ION / IRIP) ** clip((d - 0.5) / 0.5)
    return iserie, ideriv


def cella_ldr(cs, cp, ils="DC 20m", ilp="DC 10n"):
    return [
        "* ---- la cella a fotoresistenze NSL-32SR3: serie curva %s, derivazione curva %s ----" % (cs, cp),
        "XLS ALS 0 SRCX AIN NSL32SR3_%s" % cs,
        "XLP ALP 0 AIN 0 NSL32SR3_%s" % cp,
        "ILS 0 ALS %s" % ils,
        "ILP 0 ALP %s" % ilp,
        "* 10 M dall'anodo a massa: un LED col solo generatore non ha percorso in continua (L29b)",
        "RALS ALS 0 10MEG", "RALP ALP 0 10MEG",
    ]


def testa(titolo, rsrc="1.5"):
    return [
        titolo,
        "* GENERATO da docs/preamp/data/2026-10-02/L47b1/banco/ (L47b1). Banco ridotto: vedi comune.py.",
        ".include %s" % ANGOLI_LIB,
        ".include %s" % NSL_LIB,
        OPZIONI,
        "VSRC VSN 0 DC 0 AC 1 SIN(0 %g 1k)" % A_PIENO,
        "RSRC VSN SRCX %s" % rsrc,
        "* R_IN del blocco A (gain_block.py, r_in=1M)",
        "RIN AIN 0 1MEG",
    ]


# ---------------------------------------------------------------- l'esecuzione
RIFIUTI = ("Transient op started", "Error", "error:", "aborted", "Timestep too small",
           "too many args", "no such device", "is not available", "could not find", "singular matrix")


def corri(deck_path, timeout=3600):
    """ngspice in batch; stdout e stderr nello stesso .log (le Note vanno su stderr, #40).
    Ritorna (rc, log). La guardia la applica chi legge (guardia())."""
    log = deck_path[:-4] + ".log"
    with open(log, "w") as f:
        p = subprocess.run([NGSPICE, "-b", deck_path], stdout=f, stderr=subprocess.STDOUT,
                           cwd=os.path.dirname(deck_path), timeout=timeout)
    return p.returncode, log


def guardia(log):
    """Le righe che invalidano una corsa (#33 #35 #36 #29). «failed» da solo NON e' un rifiuto:
    «Dynamic gmin stepping failed» precede un op valido (#40)."""
    cattive = []
    for r in open(log, errors="replace"):
        for x in RIFIUTI:
            if x in r:
                cattive.append(r.strip())
    return cattive


def ricuci(log):
    """#37: una Note/Warning dentro una riga di print si ricuce."""
    grezze = open(log, errors="replace").read().split("\n")
    righe, k = [], 0
    while k < len(grezze):
        r = grezze[k]
        m = re.match(r"(.*\S)\s*(Note:|Warning:)", r)
        if m and not re.match(r"\s*(Note:|Warning:)", r):
            k += 1
            while k < len(grezze) and re.match(r"\s*(Note:|Warning:)", grezze[k]):
                k += 1
            righe.append(m.group(1) + (grezze[k].strip() if k < len(grezze) else ""))
        else:
            righe.append(r)
        k += 1
    return righe


def valori(log, nomi):
    """Le righe 'nome = valore' delle print, ricucite."""
    out = {}
    for r in ricuci(log):
        m = re.match(r"\s*([A-Za-z_][\w()#.\[\]@]*)\s*=\s*([-+0-9.eE]+)\s*$", r)
        if m and m.group(1).lower() in nomi:
            out[m.group(1).lower()] = float(m.group(2))
    return out


def db(x):
    return 20 * math.log10(max(abs(x), 1e-300))


def spl(v_jack):
    """dB SPL di picco a 1 m dal picco al jack: 100 uV = 33 dB SPL (ADR-032, formula di NC-028)."""
    return 33.0 + db(v_jack / 100e-6)
