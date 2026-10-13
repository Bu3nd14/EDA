#!/usr/bin/env python3
"""L45b: il banco dei guasti dei controlli della scheda audio, e la rilettura di L45a a vuoto
(NC-042, P10 / ADR-069). Solo stdlib, /usr/bin/python3. Uso:

  genera_controlli.py controlli [--carico] [MODO...]
                                             deck/ctl/<modo>.cir (a vuoto) o deck/ctl_carico/, e
                                             deck/lista_ctl[_carico].txt (con MODO: solo quelli)
  genera_controlli.py lunghe VAR DECK...     gli stessi deck fino a 6 s, deck/VAR/
  genera_controlli.py vuoto FAMIGLIA...      ogni deck di L45a/deck/FAMIGLIA/ con i carichi tolti
                                             -> deck/vuoto_FAMIGLIA/, e deck/lista_vuoto_FAMIGLIA.txt

IL BANCO e' il canale di L45a (`L45a/script/genera_canale.py`, importato e non copiato): sorgente
K11, C_IN, R_SEL, contatto del selettore, blocco A, buffer F1 e F2, scala del trim, C_T, volume al
massimo, blocco B, le tre uscite con la geometria iii. Nessun blocco guasto: il guasto e' in UN
controllo, inserito con lo stesso interruttore di L45a (`CTL`, 0 -> 1 a 0,3 s in 10 us) e i suoi
modelli (SWFC chiude con CTL = 1, SWFO apre).

A VUOTO (P10, ADR-069): le tre righe RLD* (cj 100k, Singxer 10k, Stax 50k) si tolgono; restano i
bleed sul lato del condensatore e sul jack, il carico per cui il colpo dura di piu'.
"""
import glob
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L45B = os.path.dirname(QUI)
L45A = os.path.join(os.path.dirname(L45B), "L45a")
sys.path.insert(0, os.path.join(L45A, "script"))
import genera_canale as gc  # noqa: E402

T_F = 0.3
T_FINE = 2.3


def vuoto(testo):
    righe = testo.splitlines(keepends=True)
    tolte = [r for r in righe if r.startswith("RLD")]
    if len(tolte) != 3:
        sys.exit("RIFIUTATO: attese 3 righe RLD, trovate %d" % len(tolte))
    return "".join(r for r in righe if not r.startswith("RLD"))


def sostituisci(testo, vecchia, nuova):
    if testo.count(vecchia) != 1:
        sys.exit("RIFIUTATO: %r trovata %d volte" % (vecchia, testo.count(vecchia)))
    return testo.replace(vecchia, nuova)


def corto(a, b, nome="SFLT"):
    """Un corto fra due nodi che si chiude al guasto (10 mohm)."""
    return lambda t: t + "%s %s %s CTL 0 SWFC\n" % (nome, a, b)


def aperto(riga, nodo, x="FLTX", nome="SFLT"):
    """Il terminale NODO della riga (che deve comparire una volta) si stacca al guasto."""
    def f(t):
        p = riga.split()
        if p.count(nodo) != 1:
            sys.exit("RIFIUTATO: %s non e' un terminale unico di %r" % (nodo, riga))
        p[p.index(nodo)] = x
        t = sostituisci(t, riga + "\n", " ".join(p) + "\n")
        return t + "%s %s %s 0 CTL SWFO\n" % (nome, x, nodo)
    return f


def isolamento(nodo, r="10"):
    """L'isolamento fra bobina e contatti che cede: i 12 V di VRELAY (il capo + della bobina, pin 1,
    a 12 V per K2-K4 e K6 sempre, per le altre quando sono eccitate) sul nodo del contatto, con
    R ohm di percorso (10 ohm: il caso peggiore, il capo della bobina dal lato di VRELAY)."""
    return lambda t: t + "VBOB BOB 0 DC 12\nRBOB BOB BOBR %s\nSFLT BOBR %s CTL 0 SWFC\n" % (r, nodo)


def tutti(*fs):
    def f(t):
        for g in fs:
            t = g(t)
        return t
    return f


# (modo, guadagno del blocco B, descrizione, trasformazione). Righe del canale di L45a:
#   CMAIN MAIN_A MAINC 4.7u | CFIX1 FIX1_A FIX1C 4.7u | CT OUTA ATT 10u | CIN JIN SEL 1u
#   RSELK SEL INA 0.1 (il contatto del selettore) | SNOMAIN MAINC MAINJACK 0 MUTE SWKO (il NO del
#   mute) | RRGB RGB 0 <rg> e RRG10B RG10B 0 <rg10> (i rami di K1 e K5 sul blocco B)
MODI = [
    # --- i condensatori d'uscita e C_T, C_IN
    ("Cout_main_cc", 0, "4,7 uF del principale in corto", corto("MAIN_A", "MAINC")),
    ("Cout_fix1_cc", 0, "4,7 uF del Singxer in corto", corto("FIX1_A", "FIX1C")),
    ("Cout_fix2_cc", 0, "4,7 uF della Stax in corto", corto("FIX2_A", "FIX2C")),
    ("Cout_main_ap", 0, "4,7 uF del principale aperto", aperto("CMAIN MAIN_A MAINC 4.7u", "MAIN_A")),
    ("CT_cc", 0, "C_T in corto", corto("OUTA", "ATT")),
    ("CT_cc_g10", 10, "C_T in corto, blocco B a +10 dB", corto("OUTA", "ATT")),
    ("CT_ap", 0, "C_T aperto", aperto("CT OUTA ATT 10u", "OUTA")),
    ("CIN_cc", 0, "C_IN in corto (sorgente a 0 V)", corto("JIN", "SEL")),
    ("RBLmain_ap", 0, "bleed del jack principale aperto", aperto("RBLMAIN MAINJACK 0 220k", "MAINJACK")),
    ("RBCmain_ap", 0, "bleed del lato condensatore aperto", aperto("RBCMAIN MAINC 0 220k", "MAINC")),
    # --- il mute (K4 sul principale; K2/K3 uguali sulle fisse)
    ("K4_no_ap", 0, "NO del mute che si apre (contatto aperto)", aperto(
        "SNOMAIN MAINC MAINJACK 0 MUTE SWKO", "MAINJACK")),
    ("K4_cade", 0, "il mute che cade durante l'ascolto (bobina aperta, pilota aperto)", None),
    ("K4_rimbalzo", 0, "rimbalzo del NO: aperto 0,5 ms", None),
    # --- il guadagno (K1 sul ramo +3, K5 sul ramo +10, blocco B)
    ("G_0a3", 0, "il guadagno sale 0 -> +3 dB durante l'ascolto", corto("RGB", "0")),
    ("G_0a10", 0, "il guadagno sale 0 -> +10 dB", tutti(corto("RGB", "0"), corto("RG10B", "0", "SFLTB"))),
    ("G_3a0", 3, "il guadagno scende +3 -> 0 dB (K1 o K11 che cade)", aperto("RRGB RGB 0 0.1", "RGB")),
    ("G_10a0", 10, "il guadagno scende +10 -> 0 dB", tutti(aperto("RRGB RGB 0 0.1", "RGB"),
                                                         aperto("RRG10B RG10B 0 0.1", "RG10B", "FLTY", "SFLTB"))),
    ("G_10a3", 10, "il guadagno scende +10 -> +3 dB (K5 o K12 che cade)", aperto("RRG10B RG10B 0 0.1", "RG10B")),
    # --- il trim (K7 / K8 che si muovono durante l'ascolto: il permesso guasto)
    ("T_0a6", 0, "il trim va 0 -> -6 dB durante l'ascolto", tutti(
        lambda t: sostituisci(t, "CT OUTA ATT 10u\n", "CT TRC ATT 10u\n"),
        lambda t: t + "SFLT TRC OUTA 0 CTL SWFO\nSFLTB TRC TAP6 CTL 0 SWFC\n")),
    ("T_0a12", 0, "il trim va 0 -> -12 dB", tutti(
        lambda t: sostituisci(t, "CT OUTA ATT 10u\n", "CT TRC ATT 10u\n"),
        lambda t: t + "SFLT TRC OUTA 0 CTL SWFO\nSFLTB TRC TAP12 CTL 0 SWFC\n")),
    ("T_com_ap", 0, "il contatto di K7 che si apre (C_T appeso)", aperto("CT OUTA ATT 10u", "OUTA")),
    # --- il selettore
    ("S_ap", 0, "il contatto del selettore che si apre (bobina, contatto)", aperto("RSELK SEL INA 0.1", "INA")),
    # --- l'isolamento fra bobina e contatti che cede: 12 V sul nodo del contatto
    ("I_K4_jack", 0, "isolamento di K4 sul NO (il jack principale)", isolamento("MAINJACK")),
    ("I_K4_com", 0, "isolamento di K4 sul comune (lato condensatore)", isolamento("MAINC")),
    ("I_K3_jack", 0, "isolamento di K3 sul NO (il jack della Stax)", isolamento("FIX2JACK")),
    ("I_K13", 0, "isolamento del selettore sul comune (ingresso del blocco A)", isolamento("INA")),
    ("I_K7", 0, "isolamento di K7 sul comune (la cima di C_T, uscita del blocco A)", isolamento("OUTA")),
    ("I_K1", 0, "isolamento di K1 sul comune (il ramo +3 del blocco B)", isolamento("RGB")),
    ("I_K13_1k", 0, "come I_K13, con 1 kohm (meta' bobina)", isolamento("INA", "1k")),
    ("I_K4_jack_1k", 0, "come I_K4_jack, con 1 kohm", isolamento("MAINJACK", "1k")),
    # --- la 47 ohm d'uscita in corto: la capacita' del cavo arriva sullo stadio, fuori dalla 47 ohm
    #     che la teneva fuori dall'anello (preamp_audio.py). Il cavo come C sul jack.
    ("rif_cavo1n", 0, "senza guasto, 1 nF di cavo sul principale e sulla Stax",
     lambda t: t + "CCAVM MAINJACK 0 1n\nCCAV2 FIX2JACK 0 1n\n"),
    ("RSmain_cc_100p", 0, "47 ohm del principale in corto, 100 pF di cavo", tutti(
        corto("OUTB", "MAIN_A"), lambda t: t + "CCAVM MAINJACK 0 100p\n")),
    ("RSmain_cc_1n", 0, "47 ohm del principale in corto, 1 nF di cavo", tutti(
        corto("OUTB", "MAIN_A"), lambda t: t + "CCAVM MAINJACK 0 1n\n")),
    ("RSmain_cc_1n_g10", 10, "47 ohm del principale in corto, 1 nF, +10 dB", tutti(
        corto("OUTB", "MAIN_A"), lambda t: t + "CCAVM MAINJACK 0 1n\n")),
    ("RSfix2_cc_1n", 0, "47 ohm della Stax in corto, 1 nF di cavo", tutti(
        corto("OUTF2", "FIX2_A"), lambda t: t + "CCAV2 FIX2JACK 0 1n\n")),
    ("RSmain_ap", 0, "47 ohm del principale aperto", aperto("RSMAIN OUTB MAIN_A 47", "OUTB")),
]
# Lo stesso, eccitato: un gradino di 0,2 V con fronti di 1 us dalla sorgente a 0,35 s (una corsa senza
# segnale non eccita l'anello); passo massimo 1 us, fino a 0,4 s.
for _c in ("1n", "10n"):
    MODI.append(("rif_cavo%s_gradino" % _c, 0, "senza guasto, %s di cavo, gradino" % _c,
                 lambda t, c=_c: t + "CCAVM MAINJACK 0 %s\n" % c))
    MODI.append(("RSmain_cc_%s_gradino" % _c, 0, "47 ohm del principale in corto, %s di cavo, gradino" % _c,
                 tutti(corto("OUTB", "MAIN_A"), lambda t, c=_c: t + "CCAVM MAINJACK 0 %s\n" % c)))
SEGNALE_MODO = {m[0]: "PULSE(0 0.2 0.35 1u 1u 20m 1)" for m in MODI if m[0].endswith("_gradino")}
PASSO_MODO = {m: "1u" for m in SEGNALE_MODO}

# I guasti LATENTI del mute (un NO saldato, il sink Q501 in corto): al guasto non succede niente, ma
# il jack resta collegato quando i rail si spengono o si accendono. Rail ideali con una rampa: allo
# spegnimento 15 -> 0 V in 110 ms (2200 uF di tenuta con ~0,3 A, L30: 13,5 V dopo 63-123 ms), il
# negativo uguale; all'accensione 0 -> 15 V in 50 ms. Il mute resta rilasciato (DC 0).
def rail(pwl_p, pwl_m):
    return tutti(lambda t: sostituisci(t, "VPP VPLUS 0 DC 15\n", "VPP VPLUS 0 %s\n" % pwl_p),
                 lambda t: sostituisci(t, "VMM VMINUS 0 DC -15\n", "VMM VMINUS 0 %s\n" % pwl_m))


MODI.append(("L_spegnimento", 0, "mute che non si inserisce (NO saldato, Q501 in corto): spegnimento",
             rail("PWL(0 15 0.3 15 0.41 0)", "PWL(0 -15 0.3 -15 0.41 0)")))
MODI.append(("L_spegnimento_g10", 10, "come L_spegnimento, a +10 dB",
             rail("PWL(0 15 0.3 15 0.41 0)", "PWL(0 -15 0.3 -15 0.41 0)")))
# asimmetrici: un rail scende in 110 ms, l'altro nel doppio (tolleranze dei 2200 uF e dei carichi)
MODI.append(("L_spegnimento_piu_lento", 0, "come L_spegnimento, il + scende in 220 ms",
             rail("PWL(0 15 0.3 15 0.52 0)", "PWL(0 -15 0.3 -15 0.41 0)")))
MODI.append(("L_spegnimento_meno_lento", 0, "come L_spegnimento, il - scende in 220 ms",
             rail("PWL(0 15 0.3 15 0.41 0)", "PWL(0 -15 0.3 -15 0.52 0)")))
MODI.append(("L_accensione", 0, "mute che non si inserisce: accensione, rail 0 -> 15 V in 50 ms",
             rail("PWL(0 0 0.3 0 0.35 15)", "PWL(0 0 0.3 0 0.35 -15)")))

# Corse piu' corte: un'oscillazione costa passi fitti (L45a: 20 ms costavano 87 s)
T_FINE_MODO = {"RSmain_cc_100p": 0.6, "RSmain_cc_1n": 0.6, "RSmain_cc_1n_g10": 0.6,
               "RSfix2_cc_1n": 0.6, "rif_cavo1n": 0.6}
T_FINE_MODO.update({m: 0.4 for m in SEGNALE_MODO})


def deck_controllo(modo, gain, desc, f, carico):
    mute = "DC 0"
    if modo == "K4_cade":
        # il comando del mute che cade: NO apre e 1 ms dopo NC chiude, come all'inserzione
        mute = "PWL(0 0 %g 0 %g 1)" % (T_F, T_F + 1e-3)
    elif modo == "K4_rimbalzo":
        mute = "PWL(0 0 %g 0 %g 1 %g 1 %g 0)" % (T_F, T_F + 20e-6, T_F + 0.5e-3, T_F + 0.52e-3)
    ctl = "PWL(0 0 %g 0 %g 1)" % (T_F, T_F + 10e-6) if modo != "rif" else "DC 0"
    corpo = gc.canale(("-", None), gain, SEGNALE_MODO.get(modo, "DC 0"), mute, ctl)
    if f is not None:
        corpo = f(corpo)
    if not carico:
        corpo = vuoto(corpo)
    t = "L45b controlli %s g%d %s - %s, guasto a %g s\n" % ("carico" if carico else "vuoto", gain, modo,
                                                           desc, T_F)
    ctrl = (".control\nset noaskquit\noption itl1=1000\n"
            "save v(mainjack) v(fix1jack) v(fix2jack) v(outa) v(outf1) v(outf2) v(outb) i(vpp) i(vmm)\n"
            "tran 1u %g 0 %s\n"
            "wrdata %s.dat v(mainjack) v(fix1jack) v(fix2jack) v(outa) v(outf1) v(outf2) v(outb) i(vpp) i(vmm)\n"
            "quit\n.endc\n.end\n") % (T_FINE_MODO.get(modo, T_FINE), PASSO_MODO.get(modo, "50u"), modo)
    return t + corpo + ctrl


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "controlli":
        carico = "--carico" in argv
        var = "ctl_carico" if carico else "ctl"
        lista = []
        solo = [a for a in argv[2:] if not a.startswith("--")]
        for modo, gain, desc, f in [("rif", 0, "senza guasto", None), ("rif_g3", 3, "senza guasto", None),
                                    ("rif_g10", 10, "senza guasto", None)] + MODI:
            if solo and modo not in solo:
                continue
            p = os.path.join(L45B, "deck", var, modo + ".cir")
            gc.scrivi(p, deck_controllo(modo, gain, desc, f, carico))
            lista.append(p)
        gc.scrivi(os.path.join(L45B, "deck", "lista_%s.txt" % var), "\n".join(lista) + "\n")
        print("%s: %d deck" % (var, len(lista)))
    elif cmd == "vuoto":
        for fam in argv[2:]:
            src = sorted(glob.glob(os.path.join(L45A, "deck", fam, "*.cir")))
            if not src:
                sys.exit("RIFIUTATO: nessun deck in L45a/deck/%s" % fam)
            lista = []
            for s in src:
                testo = open(s).read()
                righe = testo.split("\n", 1)
                testo = "L45b A VUOTO (RLD tolti) - " + righe[0] + "\n" + vuoto(righe[1])
                p = os.path.join(L45B, "deck", "vuoto_" + fam, os.path.basename(s))
                gc.scrivi(p, testo)
                lista.append(p)
            gc.scrivi(os.path.join(L45B, "deck", "lista_vuoto_%s.txt" % fam), "\n".join(lista) + "\n")
            print("vuoto_%s: %d deck" % (fam, len(lista)))
    elif cmd == "lunghe":
        # Le fisse a vuoto decadono con 4,7 uF su 235 k (tau 1,1 s): in 2,3 s il jack e' ancora
        # sopra 0,87 V. Le stesse corse, fino a 6 s.
        var, lista = argv[2], []
        for s in argv[3:]:
            testo = open(s).read()
            vecchia = "tran 1u %g 0 " % T_FINE
            if testo.count(vecchia) != 1:
                sys.exit("RIFIUTATO: %r non c'e' una volta in %s" % (vecchia, s))
            testo = "L45b fino a 6 s - " + testo.replace(vecchia, "tran 1u 6 0 ")
            v = os.path.basename(os.path.dirname(s))
            vecchio, nuovo = os.path.basename(s)[:-4], v + "__" + os.path.basename(s)[:-4]
            # i file della corsa prendono il nome del deck (uno.sh, analizza_p10.py)
            for suff in (".dat", "_fine.csv"):
                testo = testo.replace(" %s%s" % (vecchio, suff), " %s%s" % (nuovo, suff))
            p = os.path.join(L45B, "deck", var, nuovo + ".cir")
            gc.scrivi(p, testo)
            lista.append(p)
        gc.scrivi(os.path.join(L45B, "deck", "lista_%s.txt" % var), "\n".join(lista) + "\n")
        print("%s: %d deck" % (var, len(lista)))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
