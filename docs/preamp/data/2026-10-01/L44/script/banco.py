#!/usr/bin/env python3
"""L44 - il banco del rumore 1/f fuori dalla coppia d'ingresso.

Per ogni variante scrive in ../inc/ e ../deck/<variante>/:
  inc/<v>_modelli.lib     copie dei modelli di models/ RINOMINATE per gruppo
                          (LS350 -> LS350_SPECCHIO, ...) con KF/AF aggiunti;
  inc/<v>_flat.inc        spice/preamp/gain_block_flat.inc con le righe Q dei
                          gruppi toccati ripuntate ai modelli rinominati;
  inc/<v>.subckt          lo stesso per spice/preamp/gain_block.subckt;
  deck/<v>/<deck>.cir     i deck di rumore con l'include del blocco sostituito
                          (e il .lib della variante incluso accanto).

Perche' rinominare e non `altermod` (limitations #29): un nome sbagliato non da'
errore e un modello alterato porta ancora il nome del costruttore. Qui il nome
del modello dice che e' alterato, e una riga Q che punta a un modello inesistente
fa fallire ngspice ("could not find model"). Il controllo `ctrl` non tocca niente:
i suoi .inc/.subckt sono copie byte-identiche dei sorgenti, e deve ridare L46b.

IL FLICKER IN ngspice (BJT Gummel-Poon): densita' del rumore di corrente di base
    i_n^2 = 2 q Ib + KF * Ib^AF / f      [A^2/Hz]
L'angolo 1/f f_c, dove il flicker eguaglia lo shot, e'
    f_c = KF * Ib^(AF-1) / (2 q)
Con AF = 1 l'angolo NON dipende dalla corrente: KF = 2 q f_c. Le varianti si
scrivono quindi per angolo (Hz) e AF; kf() fa il conto. Con AF != 1 l'angolo
e' riferito a una corrente di base dichiarata (ib_rif).

Uso: /usr/bin/python3 banco.py <variante>... | tutte     (VARIANTI qui sotto)
Scrive ../deck/lista_<varianti unite da _>.txt e la stampa.
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L44 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L44, *[".."] * 5))
REL = os.path.relpath(L44, ROOT)
TB = os.path.join(ROOT, "spice", "preamp", "tb")
Q_E = 1.602176634e-19

INC_FLAT = ".include @REPO@/spice/preamp/gain_block_flat.inc"
INC_SUB = ".include @REPO@/spice/preamp/gain_block.subckt"

# istanza -> gruppo. Il modello lo si legge dalla riga Q (non si assume).
GRUPPI = {
    "Q121A": "specchio", "Q121B": "specchio",     # LS352 (modello LS350)
    "Q117": "cascode", "Q118": "cascode",         # MMBT5551
    "Q122": "vas",                                # MMBT5401
    "Q106": "pozzi", "Q125": "pozzi",             # MMBT5551: coda JFET, pozzo del VAS
    "Q127": "vbe",                                # MMBT5551, moltiplicatore di Vbe
    "Q132": "finali", "Q133": "finali",           # Qmje15032 / Qmje15033
}
LIB = {"LS350": "models/bjt_pnp/ls350.lib", "MMBT5551": "models/bjt_npn/mmbt5551.lib",
       "MMBT5401": "models/bjt_pnp/mmbt5401.lib", "QMJE15032": "models/bjt_npn/mje15032.lib",
       "QMJE15033": "models/bjt_pnp/mje15033.lib"}
TUTTI = ["specchio", "cascode", "vas", "pozzi", "vbe", "finali"]


def kf(fc, af=1.0, ib_rif=1e-6):
    return 2 * Q_E * fc * ib_rif ** (1.0 - af)


def uniforme(fc, gruppi=TUTTI, af=1.0):
    return {g: (kf(fc, af), af) for g in gruppi}


# variante -> {gruppo: (KF, AF)}. Le varianti delle curve trovate (passo 2 del
# piano) si aggiungono qui, con la fonte nel commento.
VARIANTI = {"ctrl": {}}
for _fc in (100, 1000, 10000, 100000):
    VARIANTI["tutti_fc%d" % _fc] = uniforme(_fc)
    for _g in TUTTI:
        VARIANTI["%s_fc%d" % (_g, _fc)] = uniforme(_fc, [_g])
for _fc in (1e6, 1e7):
    VARIANTI["specchio_fc%d" % _fc] = uniforme(_fc, ["specchio"])
    VARIANTI["tutti_fc%d" % _fc] = uniforme(_fc)

# Le curve trovate (passo 1, bom-component-manager; letture nei PROVENANCE di vendor/):
#  - 2N5087, Motorola, Fig. 2 p. 3 (vendor/bjt_pnp/motorola/2N5087/): rumore di
#    corrente a 10 uA...1 mA; AF = 1,35 coerente sulle cinque correnti, KF ~2e-14
#    a 10 Hz, ~5e-14 a 300 Hz (hFE assunto 250);
#  - databook Linear Systems, nota "Solving the Noise Puzzle", Fig. 3 p. 329
#    (vendor/bjt_pnp/linear_systems/LS350/4be30b_6071...pdf): famiglia LS310/LS350,
#    10 e 300 uA; AF ~1,46, KF ~6e-14; il caso peggiore a 10 uA e' ~2x il tipico.
# Classe dei piccoli segnali: AF = 1,4, KF = 5e-14 ("dati"), 1e-13 il tetto
# prudente. NPN (MMBT5551) e potenza (MJE): NESSUNA curva - gli si da' lo stesso
# valore per scelta dichiarata, e la scansione per gruppo dice che non conta.
VARIANTI["dati"] = {g: (5e-14, 1.4) for g in TUTTI}
VARIANTI["tetto"] = {g: (1e-13, 1.4) for g in TUTTI}
VARIANTI["tetto_x10"] = {g: (1e-12, 1.4) for g in TUTTI}

DECK = ("tb_noise_breakdown", "tb_noise_vectors", "tb_e3_e5_ldr", "rumore_dispositivi")


def scheda(nome_mod):
    """La scheda .model di nome_mod dal suo file in models/, come lista di righe."""
    righe = open(os.path.join(ROOT, LIB[nome_mod.upper()])).read().split("\n")
    out, dentro = [], False
    for r in righe:
        if re.match(r"\.model\s+%s\b" % re.escape(nome_mod), r, re.I):
            dentro = True
            out.append(r)
            continue
        if dentro:
            if r.startswith("+"):
                out.append(r)
            else:
                break
    if not out:
        sys.exit("modello %s non trovato in %s" % (nome_mod, LIB[nome_mod.upper()]))
    return out


def rinomina(nome_mod, gruppo, kfv, afv):
    testo = " ".join(r.lstrip("+").strip() for r in scheda(nome_mod))
    testo = testo.replace("(", " ").replace(")", " ")
    testo = re.sub(r"\b(KF|AF)\s*=\s*\S+", " ", testo, flags=re.I)
    t = testo.split()
    assert t[0].lower() == ".model" and t[1].lower() == nome_mod.lower()
    nuovo = "%s_%s" % (nome_mod.upper(), gruppo.upper())
    corpo, righe, cur = t[2:], [], ".model %s" % nuovo
    for tok in corpo:
        if len(cur) + len(tok) > 90:
            righe.append(cur)
            cur = "+"
        cur += " " + tok
    righe.append(cur)
    righe.append("+ KF=%.6e AF=%.4g" % (kfv, afv))
    return nuovo, righe


def blocco(src, var):
    """Ripunta le righe Q dei gruppi toccati; ritorna (testo, {modello_nuovo: righe})."""
    righe, modelli, viste = open(src).read().split("\n"), {}, set()
    for i, r in enumerate(righe):
        m = re.match(r"^(Q\w+)(\s+\S+\s+\S+\s+\S+\s+)(\S+)\s*$", r)
        if not m or m.group(1) not in GRUPPI:
            continue
        viste.add(m.group(1))
        g = GRUPPI[m.group(1)]
        if g not in var:
            continue
        nuovo, card = rinomina(m.group(3), g, *var[g])
        modelli[nuovo] = card
        righe[i] = m.group(1) + m.group(2) + nuovo
    if viste != set(GRUPPI):
        sys.exit("%s: istanze attese %s, trovate %s" % (src, sorted(GRUPPI), sorted(viste)))
    return "\n".join(righe), modelli


def rumore_dispositivi(inc_flat, inc_lib, v):
    """Lo spettro per dispositivo, blocco B a +10 dB, sorgente 430 e 2500 ohm.

    Stesso banco di tb_noise_breakdown.cir (stessi include, carichi, relè).
    wrdata a nomi espliciti (niente print: #37); 10 Hz - 20 kHz, 10 punti/decade.
    """
    src = open(os.path.join(TB, "tb_noise_breakdown.cir")).read().split("\n")
    testa = [r for r in src if r.startswith(".include") and "gain_block" not in r]
    vett = ["onoise_spectrum"] + ["onoise_" + q.lower() for q in sorted(GRUPPI)] + \
        ["onoise_jq110a", "onoise_jq110b", "onoise_r119", "onoise_r120", "onoise_r136",
         "onoise_rsrc"]
    t = ["rumore_dispositivi - L44: spettro per dispositivo, blocco B +10 dB; variante %s" % v,
         "* generato da L44/script/banco.py. Colonne: coppie (frequenza, valore) nell'ordine:",
         "* " + " ".join(vett)] + testa + [inc_flat, inc_lib, "",
         "VPP VPLUS 0 DC 15", "VMM VMINUS 0 DC -15", "VSRC SRCN 0 DC 0 AC 1",
         "RSRC SRCN IN 430", "CSTRAY RG 0 15p", "RRG RG 0 0.1", "CSTRAY10 RG10 0 15p",
         "RRG10 RG10 0 0.1", "RISO OUT OUTA 47", "COUT OUTA JACK 4.7u",
         "RBLEED JACK 0 220k", "RLOAD JACK 0 100k", "", ".control", "set t = .txt"]
    for rs in ("430", "2500"):
        t += ["alter rsrc = %s" % rs, "noise v(JACK) VSRC dec 10 10 20000 1", "setplot noise1",
              "wrdata rumore_dispositivi_r%s$t %s" % (rs, " ".join(vett)),
              "setplot noise2", "print onoise_total", "destroy all"]
    return "\n".join(t + [".endc", ".end", ""])


def copia_deck(nome, inc_flat, inc_sub, inc_lib, v):
    righe = open(os.path.join(TB, nome + ".cir")).read().split("\n")
    n = 0
    for i, r in enumerate(righe):
        if r == INC_FLAT:
            righe[i] = inc_flat + "\n" + inc_lib
            n += 1
        elif r == INC_SUB:
            righe[i] = inc_sub + "\n" + inc_lib
            n += 1
    if n != 1:
        sys.exit("%s: include del blocco trovato %d volte" % (nome, n))
    righe[0] = "%s.cir - L44, variante %s (modelli da inc/%s_modelli.lib)" % (nome, v, v)
    return "\n".join(righe)


def main():
    lista = []
    if sys.argv[1:] == ["tutte"]:
        sys.argv[1:] = sorted(VARIANTI)
    for v in sys.argv[1:]:
        var = VARIANTI[v]
        flat, mod1 = blocco(os.path.join(ROOT, "spice/preamp/gain_block_flat.inc"), var)
        sub, mod2 = blocco(os.path.join(ROOT, "spice/preamp/gain_block.subckt"), var)
        assert mod1 == mod2
        os.makedirs(os.path.join(L44, "inc"), exist_ok=True)
        lib = ["* L44 - variante %s: modelli rinominati per gruppo, KF/AF aggiunti (banco.py)" % v]
        for g in sorted(var):
            lib.append("* %s: KF=%.6e AF=%.4g (angolo %.4g Hz con AF=1)"
                       % (g, var[g][0], var[g][1], var[g][0] / (2 * Q_E)))
        for nome in sorted(mod1):
            lib += mod1[nome] + ["*"]
        open(os.path.join(L44, "inc", v + "_modelli.lib"), "w").write("\n".join(lib) + "\n")
        open(os.path.join(L44, "inc", v + "_flat.inc"), "w").write(flat)
        open(os.path.join(L44, "inc", v + ".subckt"), "w").write(sub)
        i_flat = ".include @REPO@/%s/inc/%s_flat.inc" % (REL, v)
        i_sub = ".include @REPO@/%s/inc/%s.subckt" % (REL, v)
        i_lib = ".include @REPO@/%s/inc/%s_modelli.lib" % (REL, v)
        d = os.path.join(L44, "deck", v)
        os.makedirs(d, exist_ok=True)
        for nome in DECK:
            testo = (rumore_dispositivi(i_flat, i_lib, v) if nome == "rumore_dispositivi"
                     else copia_deck(nome, i_flat, i_sub, i_lib, v))
            p = os.path.join(d, nome + ".cir")
            open(p, "w").write(testo)
            lista.append(p)
    et = "_".join(sys.argv[1:]) if len(sys.argv) < 5 else "%s_e_altre_%d" % (sys.argv[1], len(sys.argv) - 2)
    out = os.path.join(L44, "deck", "lista_%s.txt" % et)
    open(out, "w").write("\n".join(lista) + "\n")
    print(out)
    print("\n".join(lista))


if __name__ == "__main__":
    main()
