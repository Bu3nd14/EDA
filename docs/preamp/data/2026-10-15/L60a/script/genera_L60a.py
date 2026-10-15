#!/usr/bin/env python3
"""L60a: le scelte 6, 8, 9 e 10 di ADR-072 senza il rivelatore, con 1 uF sulla fissa 2 (ADR-081).

Solo stdlib, /usr/bin/python3. Uso:

  genera_L60a.py        scrive deck/<gruppo>/<caso>.cir e deck/lista.txt

IL BANCO e' il canale di L45a (`L45a/script/genera_canale.py`) e i guasti dei controlli di L45b
(`L45b/script/genera_controlli.py`), importati e non copiati. Rispetto a quei banchi cambiano due
cose, e solo nel banco (il circuito non cambia in L60a):
  - il condensatore d'uscita della fissa 2 (Stax) e' 1 uF (ADR-081) al posto di 4,7 uF;
  - i carichi restano: P10 si misura sulla fissa 2 col carico della Stax (50 kohm sul jack,
    ADR-081 punto 3), non a vuoto come in L45b / L45d2b1.
Nessun rivelatore (ADR-081 punto 4): nessuna corsa ha un mute che si inserisce dopo il guasto.
Rail ideali a +-15 V, come in L45a: il sorvegliante dei rail non e' nel banco.

I gruppi:
  riferimento  tre corse che riproducono numeri noti prima di guardare i nuovi
  scelta1      il blocco al rail (il controllo di L45a) in A e in F2, con 1 uF: il numero di ADR-081
  scelta6      l'isolamento bobina-contatti che cede (12 V, 10 ohm o 1 kohm di percorso)
  scelta8      il filo di un rail aperto fra le schede
  scelta9      il condensatore della fissa 2 in corto, da solo e poi col blocco al rail
  scelta10     R126 in corto (il secondo guasto per calore, da solo)
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L60A = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(L60A, "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45b", "script"))
import genera_canale as gc        # noqa: E402
import genera_controlli as gk     # noqa: E402

T_F = 0.3
T_FINE = 2.3
C_STAX = "1u"   # ADR-081


def sostituisci(t, vecchia, nuova):
    if t.count(vecchia) != 1:
        sys.exit("RIFIUTATO: %r trovata %d volte" % (vecchia, t.count(vecchia)))
    return t.replace(vecchia, nuova)


def stax_1u(t):
    return sostituisci(t, "CFIX2 FIX2_A FIX2C 4.7u\n", "CFIX2 FIX2_A FIX2C %s\n" % C_STAX)


def guasto_blocco(pos, modo, gain=0, c1u=True, carico=True, ccfix2=False):
    """Il deck di L45a (tr) col guasto MODO del blocco in POS a T_F."""
    t = gc.deck_tr(pos, gain, modo, False, False, tfine=T_FINE)
    if c1u:
        t = stax_1u(t)
    if ccfix2:
        # scelta 9: il condensatore della Stax gia' in corto (franco, da sempre), poi il guasto del
        # blocco: come deck_guasto(--ccout) di L45d2b1, sulla fissa 2
        vecchia = "CFIX2 FIX2_A FIX2C %s\n" % (C_STAX if c1u else "4.7u")
        t = sostituisci(t, vecchia, "RFIX2_CC FIX2_A FIX2C 0.01\n")
    if not carico:
        t = gk.vuoto(t)
    return t


def rail_aperto(lato, gain):
    """Come deck_rail di L45d2b1, senza il rivelatore: il filo del rail fra le schede si apre a T_F."""
    t = gc.deck_tr("B", gain, "rif", False, False, tfine=T_FINE)
    t = stax_1u(t)
    vecchia = "VPP VPLUS 0 DC 15\n" if lato == "p" else "VMM VMINUS 0 DC -15\n"
    nodo = "VPLUS" if lato == "p" else "VMINUS"
    nuova = (vecchia.replace(nodo + " ", "%s_PSU " % nodo) +
             "SFILO %s_PSU %s 0 CTLF SWFO\nVCTLF CTLF 0 PWL(0 0 %g 0 %g 1)\n"
             "RFILO %s 0 1G\n" % (nodo, nodo, T_F, T_F + 10e-6, nodo))
    return sostituisci(t, vecchia, nuova)


# Le righe di L45b che servono, piu' i due nodi della Stax e della fissa 1 che L45b non aveva
CONTROLLI = {m[0]: m for m in gk.MODI}
NUOVI = {
    "I_K3_com": (0, "isolamento di K3 sul comune (lato condensatore della Stax)", gk.isolamento("FIX2C")),
    "I_K3_jack_1k": (0, "come I_K3_jack, con 1 kohm", gk.isolamento("FIX2JACK", "1k")),
    "I_K2_jack": (0, "isolamento di K2 sul NO (il jack del Singxer)", gk.isolamento("FIX1JACK")),
    "I_K7_1k": (0, "come I_K7, con 1 kohm", gk.isolamento("OUTA", "1k")),
}


def controllo(modo):
    if modo in NUOVI:
        gain, desc, f = NUOVI[modo]
    else:
        _, gain, desc, f = CONTROLLI[modo]
    t = gk.deck_controllo(modo, gain, desc, f, True)
    t = stax_1u(t)
    # le corse dei controlli non scrivono il _fine.csv: la corrente dei rail e l'uscita dei blocchi
    # si leggono dal .dat
    return t


def casi():
    c = []
    # --- riferimento: numeri noti
    #   R126 in corto in F2 a vuoto con 4,7 uF: L45d2b1 riv_F2, fix2 44,2 ms sopra (non scattava)
    c.append(("riferimento", "R126_cc_F2_47u_vuoto", guasto_blocco("F2", "R126_cc", c1u=False, carico=False)))
    #   il blocco F2 al rail con 4,7 uF sulla Stax: L61, ~0,56 s
    c.append(("riferimento", "CTRL_F2_47u", guasto_blocco("F2", "CTRL_OUT_VP", c1u=False)))
    #   l'isolamento di K3 sul jack a vuoto con 4,7 uF: L45b ctl, 12 V fino alla fine
    c.append(("riferimento", "I_K3_jack_47u_vuoto",
              gk.deck_controllo("I_K3_jack", 0, CONTROLLI["I_K3_jack"][2], CONTROLLI["I_K3_jack"][3], False)))
    # --- scelta 1 (per confronto): il blocco al rail, 1 uF
    for pos in ("A", "F2", "F1", "B"):
        c.append(("scelta1", "CTRL_%s" % pos, guasto_blocco(pos, "CTRL_OUT_VP")))
    # --- scelta 6
    for m in ("I_K3_jack", "I_K3_jack_1k", "I_K3_com", "I_K2_jack", "I_K4_jack", "I_K4_com",
              "I_K13", "I_K13_1k", "I_K7", "I_K7_1k", "I_K1"):
        c.append(("scelta6", m, controllo(m)))
    # --- scelta 8
    for lato in ("p", "m"):
        for gain in (0, 10):
            c.append(("scelta8", "filo_%s_g%d" % (lato, gain), rail_aperto(lato, gain)))
    # --- scelta 9
    c.append(("scelta9", "Cout_fix2_cc", controllo("Cout_fix2_cc")))
    for pos in ("A", "F2"):
        c.append(("scelta9", "Cout_fix2_cc_poi_CTRL_%s" % pos, guasto_blocco(pos, "CTRL_OUT_VP", ccfix2=True)))
    # --- scelta 10
    for pos in ("A", "F2", "F1", "B"):
        c.append(("scelta10", "R126_cc_%s" % pos, guasto_blocco(pos, "R126_cc")))
    c.append(("scelta10", "R126_cc_B_g10", guasto_blocco("B", "R126_cc", gain=10)))
    return c


def main():
    lista = []
    for gruppo, nome, testo in casi():
        # i file della corsa (wrdata, _fine.csv) prendono il nome del deck: uno.sh e analizza_p10.py
        # cercano <nome>.dat in run/<gruppo>/<nome>/
        righe = testo.split("\n")
        for i, r in enumerate(righe):
            if r.startswith("wrdata ") or (r.startswith("echo ") and "_fine.csv" in r):
                parti = r.split(" ")
                for k, p in enumerate(parti):
                    if p.endswith(".dat"):
                        parti[k] = nome + ".dat"
                    elif p.endswith("_fine.csv"):
                        parti[k] = nome + "_fine.csv"
                righe[i] = " ".join(parti)
        testo = "\n".join(righe)
        p = os.path.join(L60A, "deck", gruppo, nome + ".cir")
        gc.scrivi(p, "L60a %s %s - " % (gruppo, nome) + testo)
        lista.append(p)
    gc.scrivi(os.path.join(L60A, "deck", "lista.txt"), "\n".join(lista) + "\n")
    print("L60a: %d deck" % len(lista))


if __name__ == "__main__":
    main()
