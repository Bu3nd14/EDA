#!/usr/bin/env python3
"""L45d2b1: il banco del rivelatore di continua (ADR-072). Solo stdlib, /usr/bin/python3.

  genera_rivelatore.py prova                 deck/prova/<caso>.cir: il rivelatore da solo su casi noti
  genera_rivelatore.py guasti POS [--gain G] [--ccout]
                                             deck/riv_<POS>[_g10][_cc]/<modo>.cir: ogni modo del blocco
                                             in POS (L45a) a vuoto (L45b), col rivelatore vero
  genera_rivelatore.py musica                deck/musica/<caso>.cir: il canale sano, la musica di prova
  genera_rivelatore.py rail                  deck/rail/<caso>.cir: il filo di un rail aperto fra le schede
  genera_rivelatore.py accensione            deck/accensione/<caso>.cir: i rail che salgono e scendono

IL CANALE e' quello di L45a, generato da `L45a/script/genera_canale.py` (importato, non copiato), e
reso a vuoto come in L45b (`L45b/script/genera_controlli.py`, vuoto(): via le tre righe RLD). Al
posto del mute ideale di `--taglio` c'e' la catena vera, dal rivelatore al contatto:
  - XDET: spice/preamp/dc_detector.subckt, generato da circuits/preamp/dc_detector.py. Le tre prese
    del canale L (OUTF1, OUTF2, OUTB); le tre del canale R a massa (sane, a 0 V);
  - DC_FLT tirata su a 5 V da 10k, il lato dell'alimentatore (psu.py: R548);
  - il mute: DC_FLT sotto 2,5 V chiede il mute, e la richiesta si TIENE (un diodo su 1 uF): e' il
    GUASTO del temporizzatore (spec 4.6), che non si rilascia senza il frontale. Il contatto si
    stacca 3 ms dopo (G6K, rilascio massimo, en-g6k.pdf p. 3: 4,33 ms x 1 uF arrivano a meta' in
    3,0 ms). La catena del lato dell'alimentatore (BAT54, MUTE_G, Q501) e' di microsecondi: la
    misura il banco dell'alimentatore (../psu/).
Le colonne del .dat sono quelle di L45a, cosi' `L45b/script/analizza_p10.py` le legge com'e'. In
piu' <modo>_riv.csv: l'istante in cui DC_FLT scende (t_flt) e in cui il contatto si stacca
(t_mute), dal guasto.
"""
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.dirname(QUI)
DATA = os.path.abspath(os.path.join(BANCO, "..", "..", ".."))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45a", "script"))
sys.path.insert(0, os.path.join(DATA, "2026-10-13", "L45b", "script"))
import genera_canale as gc        # noqa: E402
import genera_controlli as gk     # noqa: E402

REL = "docs/preamp/data/2026-10-14/L45d2b1/banco"
T_F = 0.3

INCLUDE = (".include @REPO@/models/diodes/1n4148.lib\n"
           ".include @REPO@/models/bjt_npn/mmbt5551.lib\n"
           ".include @REPO@/%s/inc/cmpoc.lib\n"
           ".include @REPO@/spice/preamp/dc_detector.subckt\n" % REL)

CATENA = """* L45d2b1: la catena del rivelatore (genera_rivelatore.py)
XDET OUTF1 OUTF2 OUTB 0 0 0 VPLUS VMINUS VRELAY 0 DC_FLT DCDET
VRL VRELAY 0 %s
VV5 V5 0 5
RPU DC_FLT V5 10k
BREQ REQ 0 V = 5*0.5*(1+tanh((2.5-V(DC_FLT))/0.05))
DLAT REQ LAT DLATCH
CLAT LAT 0 1u
RLAT LAT 0 1e12
RREL LAT MDL 4.33k
CREL MDL 0 1u
BMUTE MUTE 0 V = 0.5*(1+tanh((V(MDL)-2.2)/0.01))
.model DLATCH D(Is=1e-14 N=1)
"""


def scrivi(path, testo):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(testo)


def sostituisci(t, vecchia, nuova):
    if t.count(vecchia) != 1:
        sys.exit("RIFIUTATO: %r trovata %d volte" % (vecchia, t.count(vecchia)))
    return t.replace(vecchia, nuova)


def con_rivelatore(t, modo, vrelay="DC 12", t0=T_F):
    """Il deck di L45a a vuoto, col rivelatore e la catena del mute al posto di VMUTE."""
    t = gk.vuoto(t)
    t = sostituisci(t, "VMUTE MUTE 0 DC 0\n", CATENA % vrelay)
    t = sostituisci(t, ".include @REPO@/models/diodes/1n4148.lib\n", INCLUDE)
    t = sostituisci(t, "save v(mainjack)", "save v(dc_flt) v(mute) v(xdet.det_tmax) v(mainjack)")
    riv = ("meas tran t_flt WHEN v(dc_flt)=2.5 FALL=1\n"
           "meas tran t_mute WHEN v(mute)=0.5 RISE=1\n"
           "meas tran tmax_max MAX v(xdet.det_tmax)\n"
           "echo \"grandezza,valore\" > %s_riv.csv\n"
           "echo \"t0,%g\" >> %s_riv.csv\n"
           "echo \"t_flt,$&t_flt\" >> %s_riv.csv\n"
           "echo \"t_mute,$&t_mute\" >> %s_riv.csv\n"
           "echo \"tmax_max,$&tmax_max\" >> %s_riv.csv\n" % (modo, t0, modo, modo, modo, modo))
    return sostituisci(t, "quit\n.endc", riv + "quit\n.endc")


# ------------------------------------------------------------------ la prova dello strumento
PROVA_CASI = {
    # nome: (presa, sorgente, VPLUS, atteso) - atteso: "scatta" o "no"
    "gradino_p095": ("BL", "PWL(0 0 0.1 0 0.10001 0.95)", "15", "scatta"),
    "gradino_m095": ("BL", "PWL(0 0 0.1 0 0.10001 -0.95)", "15", "scatta"),
    "gradino_p149": ("F1L", "PWL(0 0 0.1 0 0.10001 14.9)", "15", "scatta"),
    "gradino_m149": ("F2R", "PWL(0 0 0.1 0 0.10001 -14.9)", "15", "scatta"),
    "gradino_p050": ("BL", "PWL(0 0 0.1 0 0.10001 0.50)", "15", "no"),
    "gradino_p070": ("BL", "PWL(0 0 0.1 0 0.10001 0.70)", "15", "scatta"),
    "senza_vplus_m149": ("BL", "PWL(0 0 0.1 0 0.10001 -14.9)", "0", "scatta"),
    "seno_20hz_14v": ("BL", "SIN(0 14 20 0.1)", "15", "no"),
    "quadra_20hz_14v": ("BL", "PULSE(-14 14 0.1 10u 10u 25m 50m)", "15", "no"),
    "impulsi_20hz_95pc": ("BL", "PULSE(-13.3 0.7 0.1 10u 10u 47.5m 50m)", "15", "no"),
    # 10 Hz, 90 % in alto a +1 V, media nulla: +1 V per 90 ms, piu' di T_HOLD
    "impulsi_10hz_90pc": ("BL", "PULSE(-9 1 0.1 10u 10u 90m 100m)", "15", "scatta"),
    # un guasto gia' presente all'accensione: VPLUS sale da 0,1 a 0,12 s (VRELAY dopo, a 0,5 s),
    # l'uscita e' a -14,9 V da subito: l'inibizione (~0,1 s) e poi T_HOLD
    "accensione_con_guasto": ("BL", "PWL(0 0 0.1 0 0.10001 -14.9)", "PWL(0 0 0.1 0 0.12 15)", "dopo_por"),
}


def deck_prova(nome):
    presa, sorg, vp, _ = PROVA_CASI[nome]
    prese = ["F1L", "F2L", "BL", "F1R", "F2R", "BR"]
    nodi = ["TAP" if p == presa else "0" for p in prese]
    vrl = "PWL(0 0 0.5 0 0.503 12)" if vp.startswith("PWL") else "12"
    vmm = "PWL(0 0 0.1 0 0.12 -15)" if vp.startswith("PWL") else "-15"
    return ("L45d2b1 prova del rivelatore: %s\n" % nome + INCLUDE +
            "VPP VPLUS 0 %s\nVMM VMINUS 0 %s\nVRL VRELAY 0 %s\nVV5 V5 0 5\nRPU DC_FLT V5 10k\n"
            % (vp, vmm, vrl) +
            # la sorgente si apre a 0,1 s: prima la presa sta a 0 V (un PULSE sta al suo primo
            # valore fino al ritardo, e il punto di lavoro partiva gia' scattato)
            "VRAW RAW 0 %s\nBTAP TAP 0 V = V(RAW)*0.5*(1+tanh((time-0.1)/1e-5))\n" % sorg +
            "XDET %s VPLUS VMINUS VRELAY 0 DC_FLT DCDET\n" % " ".join(nodi) +
            ".control\nset noaskquit\ntran 10u 0.6 0 20u\n"
            "meas tran t_flt WHEN v(dc_flt)=2.5 FALL=1\n"
            "meas tran tmax_max MAX v(xdet.det_tmax)\n"
            "meas tran vdp AVG v(xdet.det_vdp) from=0.05 to=0.1\n"
            "echo \"grandezza,valore\" > %s_riv.csv\n"
            "echo \"t_flt,$&t_flt\" >> %s_riv.csv\n"
            "echo \"tmax_max,$&tmax_max\" >> %s_riv.csv\n"
            "echo \"vdp,$&vdp\" >> %s_riv.csv\n"
            "wrdata %s.dat v(tap) v(dc_flt) v(xdet.det_tmax) v(xdet.det_t_bl_p) v(xdet.det_t_bl_m)\n"
            "quit\n.endc\n.end\n" % ((nome,) * 5))


# ------------------------------------------------------------------ la musica di prova
# La sorgente e' K11 (genera_canale.py, VIN SRC 0 ...); B a +10 dB (gain 10): B ~ 3,16 x la
# sorgente, A / F1 / F2 = la sorgente. Ampiezze di picco alla sorgente.
MUSICA_CASI = {
    "seno_20hz_g10_e6": ("SIN(0 3.818 20 0.05)", 10, "20 Hz, E6 (2,7 V RMS): B ~12 V di picco"),
    "seno_20hz_g10_clip": ("SIN(0 5 20 0.05)", 10, "20 Hz sopra E6: B al clip"),
    "quadra_20hz_g10_clip": ("PULSE(-5 5 0.05 100u 100u 24.8m 50m)", 10, "quadra 20 Hz, B al clip"),
    # media nulla alla sorgente (0,5 x 0,9 = 4,5 x 0,1): la prima stesura aveva 4,2 V di media, un
    # gradino di continua all'ingresso che C_IN porta all'uscita, e scattava (giustamente)
    "impulsi_20hz_g10": ("PULSE(-4.5 0.5 0.05 100u 100u 45m 50m)", 10,
                         "impulsi a 20 Hz, 90 % in alto, media nulla: l'uscita resta da una parte ~45 ms"),
    "burst_20hz_g10": ("PWL(0 0 0.05 0 %s)" % " ".join(
        "%.5f %.4f" % (0.05 + k * 0.0025, 5 * math.sin(2 * math.pi * 20 * k * 0.0025))
        for k in range(1, 21)) + " 0.2 0", 10, "un periodo a 20 Hz da 5 V poi silenzio: l'attacco"),
    "seno_16hz_g10_clip": ("SIN(0 5 16 0.05)", 10, "16 Hz, sotto la banda: il margine"),
    "seno_10hz_g10_clip": ("SIN(0 5 10 0.05)", 10, "10 Hz, sotto la banda: atteso lo scatto"),
    "seno_1k_g10_e6": ("SIN(0 3.818 1k 0.05)", 10, "1 kHz, E6: B a ~12 V di picco"),
    "seno_1k_g10_clip": ("SIN(0 5 1k 0.05)", 10, "1 kHz 2,3 dB sopra E6: B al clip"),
    "seno_5k_g10_clip": ("SIN(0 5 5k 0.05)", 10, "5 kHz 2,3 dB sopra E6: B al clip"),
    "seno_20hz_g0_e6": ("SIN(0 3.818 20 0.05)", 0, "20 Hz, E6, B a 0 dB"),
}


def deck_musica(nome):
    sorg, gain, _ = MUSICA_CASI[nome]
    t = gc.deck_tr("B", gain, "rif", False, False, tfine=1.0)
    t = sostituisci(t, "VIN SRC 0 DC 0\n", "VIN SRC 0 %s\n" % sorg)
    t = sostituisci(t, "tran 1u 1 0 50u", "tran 1u 1 0 20u")
    return con_rivelatore(t, "rif", t0=0.05)


# ------------------------------------------------------------------ il filo di un rail aperto
def deck_rail(lato, gain):
    """Il filo del rail fra le schede si apre a T_F: il lato della scheda audio del rail resta coi
    soli condensatori della scheda; il sorvegliante, dal lato dell'alimentatore, non vede niente."""
    t = gc.deck_tr("B", gain, "rif", False, False)
    vecchia = "VPP VPLUS 0 DC 15\n" if lato == "p" else "VMM VMINUS 0 DC -15\n"
    nodo = "VPLUS" if lato == "p" else "VMINUS"
    nuova = (vecchia.replace(nodo + " ", "%s_PSU " % nodo) +
             "SFILO %s_PSU %s 0 CTLF SWFO\nVCTLF CTLF 0 PWL(0 0 %g 0 %g 1)\n"
             "RFILO %s 0 1G\n" % (nodo, nodo, T_F, T_F + 10e-6, nodo))
    t = sostituisci(t, vecchia, nuova)
    return con_rivelatore(t, "rif")


# ------------------------------------------------------------------ l'accensione
ACC_CASI = {
    # nome: (VPLUS, VMINUS, VRELAY) come sorgenti PWL; il canale sano, nessun guasto
    "insieme_20ms": ("PWL(0 0 0.1 0 0.12 15)", "PWL(0 0 0.1 0 0.12 -15)", "PWL(0 0 0.3 0 0.303 12)"),
    "insieme_200ms": ("PWL(0 0 0.1 0 0.3 15)", "PWL(0 0 0.1 0 0.3 -15)", "PWL(0 0 0.5 0 0.503 12)"),
    "prima_il_piu": ("PWL(0 0 0.1 0 0.12 15)", "PWL(0 0 0.2 0 0.22 -15)", "PWL(0 0 0.5 0 0.503 12)"),
    "prima_il_meno": ("PWL(0 0 0.2 0 0.22 15)", "PWL(0 0 0.1 0 0.12 -15)", "PWL(0 0 0.5 0 0.503 12)"),
    "spegnimento": ("PWL(0 15 0.3 15 0.5 0)", "PWL(0 -15 0.3 -15 0.5 0)", "PWL(0 12 0.25 12 0.26 0)"),
    "spegnimento_storto": ("PWL(0 15 0.3 15 0.35 0)", "PWL(0 -15 0.3 -15 0.6 0)", "PWL(0 12 0.25 12 0.26 0)"),
    # lo sfasamento fra i rail: il banco dell'alimentatore (regolatori comportamentali, senza
    # partenza morbida) da' 0,2 ms in 31 ms di rampa; i bordi del rivelatore a 20 e 50 ms
    "meno_dopo_20ms": ("PWL(0 0 0.1 0 0.13 15)", "PWL(0 0 0.12 0 0.15 -15)", "PWL(0 0 0.5 0 0.503 12)"),
    "meno_dopo_50ms": ("PWL(0 0 0.1 0 0.13 15)", "PWL(0 0 0.15 0 0.18 -15)", "PWL(0 0 0.5 0 0.503 12)"),
    "meno_prima_20ms": ("PWL(0 0 0.12 0 0.15 15)", "PWL(0 0 0.1 0 0.13 -15)", "PWL(0 0 0.5 0 0.503 12)"),
    "meno_prima_50ms": ("PWL(0 0 0.15 0 0.18 15)", "PWL(0 0 0.1 0 0.13 -15)", "PWL(0 0 0.5 0 0.503 12)"),
    # la partenza morbida dei datasheet coi 10 uF di oggi su NR (psu.py C507, C508): il + in
    # ~1,4 s (SBVS204G eq. 5), il - in ~12 s (SBVS169D eq. 1); 3 s di corsa
    "partenza_datasheet": ("PWL(0 0 0.1 0 1.5 15)", "PWL(0 0 0.1 0 12.1 -15)", "PWL(0 0 2.9 0 2.903 12)", 3.0),
}


def deck_accensione(nome):
    vp, vm, vr = ACC_CASI[nome][:3]
    tfine = ACC_CASI[nome][3] if len(ACC_CASI[nome]) > 3 else 1.0
    t = gc.deck_tr("B", 10, "rif", False, False, tfine=tfine)
    t = sostituisci(t, "VPP VPLUS 0 DC 15\n", "VPP VPLUS 0 %s\n" % vp)
    t = sostituisci(t, "VMM VMINUS 0 DC -15\n", "VMM VMINUS 0 %s\n" % vm)
    return con_rivelatore(t, "rif", vrelay=vr, t0=0.0)


# ------------------------------------------------------------------ i guasti del blocco
def deck_guasto(pos, gain, modo, ccout, tfine=None, gear=False):
    t = gc.deck_tr(pos, gain, modo, False, False, tfine=tfine, gear=gear)
    if ccout:
        # scelta 9 di ADR-072: il condensatore d'uscita gia' in corto (un corto franco, da
        # sempre), poi il guasto del blocco a T_F: l'uscita e' accoppiata in continua
        tag = "MAIN" if pos in ("A", "B") else pos.replace("F", "FIX")
        t = sostituisci(t, "C%s %s_A %sC 4.7u\n" % (tag, tag, tag), "R%s_CC %s_A %sC 0.01\n" % (tag, tag, tag))
    return con_rivelatore(t, modo)


def main(argv):
    cmd = argv[1]
    if cmd == "prova":
        lista = []
        for nome in PROVA_CASI:
            p = os.path.join(BANCO, "deck", "prova", nome + ".cir")
            scrivi(p, deck_prova(nome))
            lista.append(p)
        scrivi(os.path.join(BANCO, "deck", "lista_prova.txt"), "\n".join(lista) + "\n")
        print("prova: %d deck" % len(lista))
    elif cmd == "musica":
        lista = []
        for nome in MUSICA_CASI:
            p = os.path.join(BANCO, "deck", "musica", nome, "rif.cir")
            scrivi(p, deck_musica(nome))
            lista.append(p)
        scrivi(os.path.join(BANCO, "deck", "lista_musica.txt"), "\n".join(lista) + "\n")
        print("musica: %d deck" % len(lista))
    elif cmd == "rail":
        lista = []
        for lato in ("p", "m"):
            for gain in (0, 10):
                p = os.path.join(BANCO, "deck", "rail", "filo_%s_g%d" % (lato, gain), "rif.cir")
                scrivi(p, deck_rail(lato, gain))
                lista.append(p)
        scrivi(os.path.join(BANCO, "deck", "lista_rail.txt"), "\n".join(lista) + "\n")
        print("rail: %d deck" % len(lista))
    elif cmd == "accensione":
        lista = []
        for nome in ACC_CASI:
            p = os.path.join(BANCO, "deck", "accensione", nome, "rif.cir")
            scrivi(p, deck_accensione(nome))
            lista.append(p)
        scrivi(os.path.join(BANCO, "deck", "lista_accensione.txt"), "\n".join(lista) + "\n")
        print("accensione: %d deck" % len(lista))
    elif cmd == "guasti":
        args = argv[2:]
        pos = args.pop(0)
        gain, ccout, tfine, gear, rshunt, solo = 0, False, None, False, False, []
        while args:
            a = args.pop(0)
            if a == "--gain":
                gain = int(args.pop(0))
            elif a == "--ccout":
                ccout = True
            elif a == "--tfine":
                # come i tr_corta_* di L45a: i casi che non finiscono in 30 min, fino a 0,6 s
                tfine = float(args.pop(0))
            elif a == "--rshunt":
                # Q146 in corto: anche gear si ferma all'istante dello scatto (0,376 s, «Timestep
                # too small» sul JFET del blocco A); rshunt = 1e10 (100 pS su ogni nodo) la fa finire
                rshunt = True
            elif a == "--gear":
                # come vuoto_tr_gear_* di L45b: i casi che trap ferma con «Timestep too small»
                gear = True
            else:
                solo.append(a)
        var = "riv_%s" % pos + ("_g%d" % gain if gain else "") + ("_cc" if ccout else "") \
            + ("_corta" if tfine else "") + ("_gear" if gear else "") + ("_rshunt" if rshunt else "")
        lista = []
        tutti = ["rif"] + [m for m, nm, _, _, _ in gc.modi()
                           if m not in gc.RAIL_A_MASSA and not (nm in gc.SOLO and pos not in gc.SOLO[nm])]
        for m in (solo or tutti):
            if m not in tutti:
                sys.exit("RIFIUTATO: %s non e' un modo di %s" % (m, pos))
            p = os.path.join(BANCO, "deck", var, m + ".cir")
            testo = deck_guasto(pos, gain, m, ccout, tfine, gear)
            if rshunt:
                testo = sostituisci(testo, "option itl1=1000\n", "option itl1=1000\noption rshunt=1e10\n")
            scrivi(p, testo)
            lista.append(p)
        scrivi(os.path.join(BANCO, "deck", "lista_%s.txt" % var), "\n".join(lista) + "\n")
        print("%s: %d deck" % (var, len(lista)))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
