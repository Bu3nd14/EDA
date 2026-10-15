#!/usr/bin/env python3
"""L60c1: dove sta il condensatore da 1 uF della Stax rispetto al rele' di mute K3 - la prova sul
banco, prima di toccare il sorgente (l'utente, 2026-10-15: «Prima la prova»).

Solo stdlib, /usr/bin/python3 -I. Uso:

  genera_L60c1.py        scrive deck/<gruppo>/<caso>.cir e deck/lista.txt

IL BANCO e' quello di L60a (il canale di L45a, i controlli di L45b, i carichi montati), importato e
non copiato. Cambia SOLO l'uscita della fissa 2 (Stax): le sette righe che genera_canale.uscita()
scrive per FIX2 si sostituiscono con la geometria in prova. I nomi dei nodi restano quelli del banco
dove hanno lo stesso significato (FIX2_A dopo la 47 ohm, FIX2JACK il jack), cosi' l'analisi di L45b
(analizza_p10.py) legge v(fix2jack) senza cambiare.

LE GEOMETRIE (K3 e' un deviatore per canale: COM, NO chiuso fuori mute, NC chiuso in mute):
  G0   quella di oggi (ADR-044, geometria iii) con 1 uF: 47 -> C -> COM | NO -> jack, NC a massa.
       Il riferimento.
  G1   ADR-082 punto 1: 47 -> NO | COM -> C 1 uF -> jack, NC a massa. Il lato d'ingresso del
       condensatore (FIX2K) e' il comune, con il suo bleed 470k; lo stadio a riposo resta a vuoto.
  G1b  G1 col bleed del jack a 220k (come la principale) al posto di 470k: tau piu' corto.
  G2   due condensatori: C1 10 uF in geometria iii (tiene la continua del buffer a mute inserito),
       poi NO -> FIX2K (bleed 470k) -> C2 1 uF -> jack. Serie 0,91 uF.
  G2b  G2 col bleed del jack a 220k.
Il deviatore ha due comandi, MNO e MNC (0 = NO chiuso / NC aperto, 1 = il contrario), cosi' il
trasferimento di 1 ms di ADR-044 si scrive nelle corse del mute.

I GRUPPI
  riferimento  due numeri noti di L60a sul banco importato (G0 = il deck di L60a, invariato)
  v2           il gradino del mute senza segnale (V2 A, ADR-032): inserimento e rilascio, ciascuno
               col suo riferimento nello stato finale; continua nominale e VOSF2 +-20 mV
  p10          il blocco A / F2 al rail; l'isolamento di K3 sul NO e sul comune, 10 ohm e 1 kohm,
               a mute rilasciato e inserito; un pin di un rail aperto sui due di J1; C +5 %
  caldo        il carico della Stax collegato al jack fuori mute (l'inserimento a caldo)
  e9           AC: la risposta al jack della Stax a 20 Hz contro 1 kHz, C nominale e -5 %
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60C1 = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L60C1, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45b", "script"))
import genera_canale as gc        # noqa: E402
import genera_controlli as gk     # noqa: E402

T_F = 0.3
T_FINE = 2.3

VECCHIA = gc.uscita("FIX2", "OUTF2", "470k", "470k", "50k")

def geometria(g, k=1.0, carico="50k"):
    """Le righe dell'uscita della Stax per la geometria G; K scala i condensatori (tolleranza).
    I contatti: SNO chiuso quando MNO < 0,4 (SWKO del banco, VT=-0,5), SNC chiuso quando MNC > 0,6
    (SWKC). Nelle corse senza mute MNO e MNC sono il MUTE del banco (vedi comandi())."""
    def c(v):
        return "%gu" % (v * k)
    bl = "220k" if g.endswith("b") else "470k"
    rld = "RLDFIX2 FIX2JACK 0 %s\n" % carico if carico else ""
    if g == "G0":
        return ("RSFIX2 OUTF2 FIX2_A 47\n"
                "CFIX2 FIX2_A FIX2C %s\n"
                "RBCFIX2 FIX2C 0 470k\n"
                "SNOFIX2 FIX2C FIX2JACK 0 MNO SWKO\n"
                "SNCFIX2 FIX2C 0 MNC 0 SWKC\n"
                "RBLFIX2 FIX2JACK 0 470k\n" % c(1.0)) + rld
    if g in ("G1", "G1b"):
        return ("RSFIX2 OUTF2 FIX2_A 47\n"
                "SNOFIX2 FIX2_A FIX2K 0 MNO SWKO\n"
                "SNCFIX2 FIX2K 0 MNC 0 SWKC\n"
                "RBCFIX2 FIX2K 0 470k\n"
                "CFIX2 FIX2K FIX2JACK %s\n"
                "RBLFIX2 FIX2JACK 0 %s\n" % (c(1.0), bl)) + rld
    if g in ("G2", "G2b"):
        return ("RSFIX2 OUTF2 FIX2_A 47\n"
                "CFIX2 FIX2_A FIX2C %s\n"
                "RBCFIX2 FIX2C 0 470k\n"
                "SNOFIX2 FIX2C FIX2K 0 MNO SWKO\n"
                "SNCFIX2 FIX2C 0 MNC 0 SWKC\n"
                "RBKFIX2 FIX2K 0 470k\n"
                "CFIX2B FIX2K FIX2JACK %s\n"
                "RBLFIX2 FIX2JACK 0 %s\n" % (c(10.0), c(1.0), bl)) + rld
    sys.exit("RIFIUTATO: geometria %s" % g)


GEOMETRIE = ("G0", "G1", "G1b", "G2", "G2b")
# I nodi dei contatti di K3 per geometria: (NO, comune)
NODI_K3 = {"G0": ("FIX2JACK", "FIX2C"), "G1": ("FIX2_A", "FIX2K"), "G1b": ("FIX2_A", "FIX2K"),
           "G2": ("FIX2K", "FIX2C"), "G2b": ("FIX2K", "FIX2C")}


def sostituisci(t, vecchia, nuova):
    if t.count(vecchia) != 1:
        sys.exit("RIFIUTATO: %r trovata %d volte" % (vecchia[:60], t.count(vecchia)))
    return t.replace(vecchia, nuova)


def comandi(t, mno=None, mnc=None):
    """I due comandi del deviatore di K3. Senza argomenti seguono il MUTE del banco."""
    if mno is None:
        righe = "EMNO MNO 0 MUTE 0 1\nEMNC MNC 0 MUTE 0 1\n"
    else:
        righe = "VMNO MNO 0 %s\nVMNC MNC 0 %s\n" % (mno, mnc)
    return t.replace("VMUTE MUTE 0 ", righe + "VMUTE MUTE 0 ", 1)


def applica(t, g, k=1.0, carico="50k", mno=None, mnc=None):
    t = sostituisci(t, VECCHIA, geometria(g, k, carico))
    return comandi(t, mno, mnc)


def vos(t, vf2):
    """VOSF2 in serie all'ingresso del buffer F2, come nei deck di V2 (tb_v2_casopeggiore.cir)."""
    vecchia = "XF2 OUTA OUTF2 "
    if t.count(vecchia) != 1:
        sys.exit("RIFIUTATO: XF2")
    return t.replace(vecchia, "VOSF2 OUTA F2IN DC %g\nXF2 F2IN OUTF2 " % vf2)


def mute_dc(t, v):
    return sostituisci(t, "VMUTE MUTE 0 DC 0\n", "VMUTE MUTE 0 DC %d\n" % v)


# ------------------------------------------------------------------ V2 ----
T_EV = 0.5
T_V2 = 3.0


def deck_v2(g, evento, vf2):
    """Senza segnale. evento: ins (NO apre a T_EV, NC chiude 1 ms dopo), rel (NC apre, NO chiude
    1 ms dopo), rif_mute (sempre in mute), rif_su (sempre rilasciato). Il resto del canale fuori
    mute (MUTE = 0): le altre uscite non toccano la Stax."""
    t = gc.canale(("-", None), 0, "DC 0", "DC 0", "DC 0")
    sale = "PWL(0 0 %g 0 %g 1)"
    scende = "PWL(0 1 %g 1 %g 0)"
    a, b = T_EV, T_EV + 20e-6
    a1, b1 = T_EV + 1e-3, T_EV + 1e-3 + 20e-6
    if evento == "ins":
        mno, mnc = sale % (a, b), sale % (a1, b1)
    elif evento == "rel":
        mno, mnc = scende % (a1, b1), scende % (a, b)
    elif evento == "rif_mute":
        mno, mnc = "DC 1", "DC 1"
    else:
        mno, mnc = "DC 0", "DC 0"
    t = applica(t, g, mno=mno, mnc=mnc)
    if vf2:
        t = vos(t, vf2)
    nome = "%s_%s_vos%+d" % (g, evento, round(vf2 * 1000))
    ctrl = (".control\nset noaskquit\noption itl1=1000\n"
            "save v(fix2jack) v(outf2)\n"
            "tran 1u %g 0 10u\n"
            "wrdata %s.dat v(fix2jack) v(outf2)\n"
            "quit\n.endc\n.end\n") % (T_V2, nome)
    return nome, "L60c1 v2 %s %s VOSF2=%g - " % (g, evento, vf2) + "\n" + t + ctrl


def deck_caldo(g):
    """Il carico della Stax (50k) collegato al jack a T_EV, fuori mute, senza segnale."""
    t = gc.canale(("-", None), 0, "DC 0", "DC 0", "DC 0")
    t = applica(t, g, carico=None)
    t += ".model SWPL SW(VT=0.5 VH=0.1 RON=0.01 ROFF=1e12)\nVPL PL 0 PWL(0 0 %g 0 %g 1)\n" \
         "SPL FIX2JACK FIX2LD PL 0 SWPL\nRLDFIX2 FIX2LD 0 50k\n" % (T_EV, T_EV + 20e-6)
    nome = "%s_caldo" % g
    ctrl = (".control\nset noaskquit\noption itl1=1000\n"
            "save v(fix2jack)\ntran 1u %g 0 10u\nwrdata %s.dat v(fix2jack)\n"
            "quit\n.endc\n.end\n") % (T_V2, nome)
    return nome, "L60c1 caldo %s - " % g + "\n" + t + ctrl


def deck_e9(g, k):
    t = gc.canale(("-", None), 0, "DC 0 AC 1", "DC 0", "DC 0")
    t = applica(t, g, k)
    # Nel punto di lavoro che precede l'AC il deviatore di K3 non lasciava passare niente (il jack
    # della Stax a -147 dB, anche col flag ON sull'istanza): fuori mute il NO si scrive come la sua
    # resistenza (0,1 ohm, ADR-044) e il NC, aperto, si toglie.
    righe = t.split("\n")
    no = [i for i, r in enumerate(righe) if r.startswith("SNOFIX2 ")]
    nc = [i for i, r in enumerate(righe) if r.startswith("SNCFIX2 ")]
    if len(no) != 1 or len(nc) != 1:
        sys.exit("RIFIUTATO: il deviatore della Stax")
    p_ = righe[no[0]].split()
    righe[no[0]] = "RNOFIX2 %s %s 0.1" % (p_[1], p_[2])
    del righe[nc[0]]
    t = "\n".join(righe)
    nome = "%s_e9_k%g" % (g, k)
    ctrl = (".control\nset noaskquit\noption itl1=1000\nop\nprint v(outa) v(outf2) v(fix2jack)\nac dec 50 5 2k\n"
            "meas ac v20 FIND vdb(fix2jack) AT=20\nmeas ac v1k FIND vdb(fix2jack) AT=1000\n"
            "let d = v20 - v1k\necho \"e9,%s,%g,$&d\" > %s_e9.csv\nquit\n.endc\n.end\n") % (g, k, nome)
    return nome, "L60c1 e9 %s k=%g - " % (g, k) + "\n" + t + ctrl


# ----------------------------------------------------------------- P10 ----
def p10_blocco(g, pos, k=1.0):
    t = gc.deck_tr(pos, 0, "CTRL_OUT_VP", False, False, tfine=T_FINE)
    return applica(t, g, k)


def p10_k3(g, quale, r, mute, k=1.0):
    nodo = NODI_K3[g][0 if quale == "no" else 1]
    t = gk.deck_controllo("I_K3_%s" % quale, 0, "isolamento di K3 sul %s (%s)" % (quale, nodo),
                          gk.isolamento(nodo, r), True)
    t = applica(t, g, k)
    if mute:
        t = mute_dc(t, 1)
    return t


def p10_pin(g, lato, gain):
    """Un pin dei due di J1 che si apre (ADR-082 punto 2, ADR-083): il rail passa da due rami di
    20 mohm (pin + filo) a uno. L'aperto di tutto il rail e' scelta 8 di L60a."""
    t = gc.deck_tr("B", gain, "rif", False, False, tfine=T_FINE)
    t = applica(t, g)
    vecchia = "VPP VPLUS 0 DC 15\n" if lato == "p" else "VMM VMINUS 0 DC -15\n"
    nodo = "VPLUS" if lato == "p" else "VMINUS"
    nuova = (vecchia.replace(nodo + " ", "%s_PSU " % nodo) +
             "RPIN1 %s_PSU %s 20m\nRPIN2 %s_PSU %s_P2 20m\n"
             "SPIN %s_P2 %s 0 CTLF SWFO\nVCTLF CTLF 0 PWL(0 0 %g 0 %g 1)\n"
             % (nodo, nodo, nodo, nodo, nodo, nodo, T_F, T_F + 10e-6))
    return sostituisci(t, vecchia, nuova)


def rinomina(testo, nome):
    """I file della corsa prendono il nome del deck (uno.sh, analizza_p10.py), come in L60a."""
    righe = testo.split("\n")
    for i, r in enumerate(righe):
        if r.startswith("wrdata ") or (r.startswith("echo ") and "_fine.csv" in r):
            parti = r.split(" ")
            for j, p in enumerate(parti):
                if p.endswith(".dat"):
                    parti[j] = nome + ".dat"
                elif p.endswith("_fine.csv"):
                    parti[j] = nome + "_fine.csv"
            righe[i] = " ".join(parti)
    return "\n".join(righe)


def casi():
    c = []
    # --- riferimento: G0 deve riprodurre L60a (F2 al rail 117,5 ms; K3 sul NO 12 V per sempre)
    c.append(("riferimento", "G0_CTRL_F2", p10_blocco("G0", "F2")))
    c.append(("riferimento", "G0_I_K3_no", p10_k3("G0", "no", "10", False)))
    for g in GEOMETRIE:
        for ev in ("ins", "rel", "rif_mute", "rif_su"):
            for vf2 in (0.0, 0.02, -0.02):
                nome, t = deck_v2(g, ev, vf2)
                c.append(("v2", nome, t))
        nome, t = deck_caldo(g)
        c.append(("caldo", nome, t))
        for k in (1.0, 0.95):
            nome, t = deck_e9(g, k)
            c.append(("e9", nome, t))
        for k in (1.0, 1.05):
            sk = "" if k == 1.0 else "_k105"
            for pos in ("A", "F2"):
                c.append(("p10", "%s_CTRL_%s%s" % (g, pos, sk), p10_blocco(g, pos, k)))
            for quale in ("no", "com"):
                for r in ("10", "1k"):
                    for mute in (False, True):
                        c.append(("p10", "%s_I_K3_%s_%s%s%s" % (g, quale, r, "_mute" if mute else "", sk),
                                  p10_k3(g, quale, r, mute, k)))
        for lato in ("p", "m"):
            c.append(("p10", "%s_pin_%s" % (g, lato), p10_pin(g, lato, 0)))
    return c


def main():
    lista = []
    for gruppo, nome, testo in casi():
        testo = rinomina(testo, nome)
        p = os.path.join(L60C1, "deck", gruppo, nome + ".cir")
        if testo.startswith("L60c1 "):
            gc.scrivi(p, testo)
        else:
            gc.scrivi(p, "L60c1 %s %s - " % (gruppo, nome) + testo)
        lista.append(p)
    gc.scrivi(os.path.join(L60C1, "deck", "lista.txt"), "\n".join(lista) + "\n")
    print("L60c1: %d deck" % len(lista))


if __name__ == "__main__":
    main()
