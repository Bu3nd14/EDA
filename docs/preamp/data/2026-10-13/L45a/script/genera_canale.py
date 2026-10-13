#!/usr/bin/env python3
"""L45a: il banco del canale con un guasto singolo nel blocco di guadagno (NC-042).

Solo stdlib, /usr/bin/python3. Uso:

  genera_canale.py modi                 scrive inc/<modo>.subckt per ogni modo e modi.csv
  genera_canale.py op POS [GAIN]        deck del punto di lavoro col guasto inserito,
                                        deck/op_<POS>[_g<GAIN>]/<modo>.cir + deck/lista_op_<POS>...
  genera_canale.py tr POS MODO... [--gain G] [--musica] [--mute] [--nome ETICHETTA]
                                        deck del transitorio, deck/tr_<etichetta>/<modo>.cir;
                                        MODO = rif e' la corsa senza guasto
  genera_canale.py lista NOME DECK...   scrive deck/lista_NOME.txt

IL CANALE e' quello di oggi, letto da circuits/preamp/preamp_audio.py e trim.py (L48a, L48b,
ADR-044, ADR-064, ADR-065), non dal blocco CANALE dei deck di V2, che e' di prima di C_T:
  sorgente (K11, 1,5 ohm) -> C_IN 1u, R_SEL 470k -> contatto del selettore 0,1 ohm -> blocco A
  blocco A -> buffer F1 (Singxer, 10k) e F2 (Stax, 50k), accoppiati in continua
  blocco A -> scala del trim 845 + 464 + 464 a massa, sempre montata; trim a 0 dB (presa in cima)
          -> C_T 10u -> volume 10k al massimo (il bilanciamento al centro non attenua, ADR-065)
          -> blocco B (R113 del subckt = R_G 1M, ADR-065)
  ogni uscita: 47 ohm -> 4,7u -> lato condensatore (bleed 220k / 470k) -> deviatore del mute
          (geometria iii, ADR-044: a riposo il lato condensatore a massa, il jack staccato)
          -> jack (bleed 220k / 470k) -> carico (cj EV250 100k, Singxer 10k come G0, Stax 50k)
  Rail ideali a +-15 V: la corrente del canale si legge e si confronta coi limiti dei
  regolatori a parte (il sorvegliante non e' nel banco).

IL GUASTO. Il blocco nella posizione POS (A, F1, F2, B) e' GAINBLOCKG: la copia del
gain_block.subckt di oggi con UNA riga cambiata e una porta in piu', CTL. Un corto e' un
interruttore SFLT fra due nodi, chiuso quando CTL = 1 (10 mohm); un aperto sposta un terminale
su un nodo nuovo FLTX e mette fra i due un interruttore chiuso quando CTL = 0 (10 mohm, poi
1e12). Il dispositivo deve esserci UNA volta sola, come in varianti.py di L56.
Gli altri tre blocchi sono GAINBLOCK, il subckt generato, intatto.
"""
import csv
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L45A = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L45A, "..", "..", "..", "..", ".."))
SUBCKT = os.path.join(ROOT, "spice", "preamp", "gain_block.subckt")
REL = "docs/preamp/data/2026-10-13/L45a"

MODELLI = """.include @REPO@/models/jfet/lsk489.lib
.include @REPO@/models/bjt_npn/mmbt5551.lib
.include @REPO@/models/bjt_pnp/mmbt5401.lib
.include @REPO@/models/bjt_npn/mje15032.lib
.include @REPO@/models/bjt_pnp/mje15033.lib
.include @REPO@/models/diodes/1n4148.lib
.include @REPO@/models/bjt_pnp/ls350.lib
.include @REPO@/spice/preamp/gain_block.subckt
"""

# Modi per tipo di parte. Terminali: BJT C B E, JFET D G S, diodo A K, R/C 1 2.
#  ce corto C-E | be corto B-E | ae emettitore aperto (il dispositivo non conduce piu')
#  ds corto D-S | gs corto G-S | as source aperto
#  cc corto     | ap aperto (il terminale 1)
MODI_PER_TIPO = {
    "Q": (("ce", "corto", 0, 2), ("be", "corto", 1, 2), ("ae", "aperto", 2, None)),
    "J": (("ds", "corto", 0, 2), ("gs", "corto", 1, 2), ("as", "aperto", 2, None)),
    "D": (("cc", "corto", 0, 1), ("ap", "aperto", 0, None)),
    "R": (("cc", "corto", 0, 1), ("ap", "aperto", 0, None)),
    "C": (("cc", "corto", 0, 1), ("ap", "aperto", 0, None)),
}
# Corti di un rail verso massa: con i rail ideali del banco sarebbero migliaia di ampere. Sono un
# sovraccarico del regolatore, cioe' un guasto dell'alimentatore: L45c (detto nel report).
RAIL_A_MASSA = {"C139_cc", "C140_cc", "C141_cc", "C142_cc"}
# Parti che esistono solo in certe posizioni (preamp_audio.py): R113 (R_IN) solo sul blocco A,
# e sul B fa le veci di R_G 1M (R265); i rami di guadagno R138/R143 solo sul B.
SOLO = {"R113": ("A", "B"), "R138": ("B",), "R143": ("B",)}


def righe_subckt():
    testo = open(SUBCKT).read().splitlines()
    i0 = next(i for i, r in enumerate(testo) if r.startswith(".subckt GAINBLOCK "))
    i1 = next(i for i, r in enumerate(testo) if r.startswith(".ends"))
    return testo[i0 + 1:i1]


def dispositivi():
    out = []
    for r in righe_subckt():
        p = r.split()
        if p and p[0][0] in MODI_PER_TIPO:
            out.append(p)
    return out


def modi():
    m = []
    for p in dispositivi():
        nome = p[0]
        for sigla, tipo, a, b in MODI_PER_TIPO[nome[0]]:
            m.append((nome + "_" + sigla, nome, tipo, a, b))
    return m


def subckt_controllo():
    """Il controllo che DEVE superare il tetto: l'uscita del blocco in corto franco col rail +.
    Atteso a calcolo: ~15 V di gradino al jack (47 ohm contro ~52 k), ben oltre 0,87 V."""
    out = [".subckt GAINBLOCKG IN OUT FB RG RG10 VPLUS VMINUS CTL",
           "* L45a: CONTROLLO, uscita in corto col rail positivo"]
    out += righe_subckt()
    out.append("SFLT OUT VPLUS CTL 0 SWFC")
    out.append(".ends GAINBLOCKG")
    return "\n".join(out) + "\n"


def subckt_guasto(modo):
    if modo == "CTRL_OUT_VP":
        return subckt_controllo()
    nome, sigla = modo.rsplit("_", 1)
    trovati = [r for r in righe_subckt() if r.split() and r.split()[0] == nome]
    if len(trovati) != 1:
        sys.exit("RIFIUTATO: %s trovato %d volte nel subckt" % (nome, len(trovati)))
    spec = {s: (t, a, b) for s, t, a, b in MODI_PER_TIPO[nome[0]]}
    if sigla not in spec:
        sys.exit("RIFIUTATO: modo %s sconosciuto per %s" % (sigla, nome))
    tipo, a, b = spec[sigla]
    out = [".subckt GAINBLOCKG IN OUT FB RG RG10 VPLUS VMINUS CTL",
           "* L45a: copia di gain_block.subckt col guasto %s (%s)" % (modo, tipo)]
    for r in righe_subckt():
        p = r.split()
        if p and p[0] == nome:
            nodi = p[1:]
            if tipo == "corto":
                if nodi[a] == nodi[b]:
                    sys.exit("RIFIUTATO: %s corto fra due terminali gia' sullo stesso nodo" % modo)
                out.append(r)
                out.append("SFLT %s %s CTL 0 SWFC" % (nodi[a], nodi[b]))
            else:
                orig = nodi[a]
                nodi[a] = "FLTX"
                out.append(" ".join([p[0]] + nodi))
                out.append("SFLT FLTX %s 0 CTL SWFO" % orig)
        else:
            out.append(r)
    out.append(".ends GAINBLOCKG")
    return "\n".join(out) + "\n"


def blocco(ist, ingresso, uscita, pos, guasto, gain):
    sub = "GAINBLOCKG" if pos == guasto else "GAINBLOCK"
    ctl = " CTL" if pos == guasto else ""
    rg = rg10 = "1G"
    if pos == "B" and gain >= 3:
        rg = "0.1"
    if pos == "B" and gain >= 10:
        rg10 = "0.1"
    s = ist[1:]
    return ("X{i} {a} {o} FB{s} RG{s} RG10{s} VPLUS VMINUS{c} {sub}\n"
            "RRG{s} RG{s} 0 {rg}\nCRG{s} RG{s} 0 15p\n"
            "RRG10{s} RG10{s} 0 {rg10}\nCRG10{s} RG10{s} 0 15p\n").format(
        i=s, a=ingresso, o=uscita, s=s, c=ctl, sub=sub, rg=rg, rg10=rg10)


def uscita(tag, da, bc, bl, carico):
    """47 ohm, 4,7u, il deviatore della geometria iii, i due bleed, il carico."""
    return ("RS{t} {d} {t}_A 47\n"
            "C{t} {t}_A {t}C 4.7u\n"
            "RBC{t} {t}C 0 {bc}\n"
            "SNO{t} {t}C {t}JACK 0 MUTE SWKO\n"
            "SNC{t} {t}C 0 MUTE 0 SWKC\n"
            "RBL{t} {t}JACK 0 {bl}\n"
            "RLD{t} {t}JACK 0 {ld}\n").format(t=tag, d=da, bc=bc, bl=bl, ld=carico)


def canale(guasto, gain, segnale, mute, ctl):
    s = []
    s.append(MODELLI)
    s.append(".include @REPO@/%s/inc/%s.subckt\n" % (REL, guasto[1]) if guasto[1] else "")
    s.append("""* interruttori: SWFC corto del guasto (chiuso con CTL=1), SWFO aperto del guasto (chiuso con
* CTL=0); SWKO / SWKC i due contatti del deviatore del mute (0,1 ohm, ADR-044): MUTE=0 rilasciato
.model SWFC SW(VT=0.5 VH=0.1 RON=0.01 ROFF=1e12)
.model SWFO SW(VT=-0.5 VH=0.1 RON=0.01 ROFF=1e12)
.model SWKO SW(VT=-0.5 VH=0.1 RON=0.1 ROFF=1e12)
.model SWKC SW(VT=0.5 VH=0.1 RON=0.1 ROFF=1e12)
VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15
VCTL CTL 0 %s
VMUTE MUTE 0 %s
VIN SRC 0 %s
RSRC SRC JIN 1.5
CIN JIN SEL 1u
RJ JIN 0 10MEG
RSEL SEL 0 470k
RSELK SEL INA 0.1
""" % (ctl, mute, segnale))
    pos = guasto[0]
    s.append(blocco("XA", "INA", "OUTA", "A", pos, gain))
    s.append(blocco("XF1", "OUTA", "OUTF1", "F1", pos, gain))
    s.append(blocco("XF2", "OUTA", "OUTF2", "F2", pos, gain))
    s.append("* scala del trim (845 + 464 + 464, sempre montata), trim a 0 dB, C_T, volume al massimo\n"
             "RTR1 OUTA TAP6 845\nRTR2 TAP6 TAP12 464\nRTR3 TAP12 0 464\n"
             "CT OUTA ATT 10u\nRVT ATT W 1m\nRVB W 0 10k\n")
    s.append(blocco("XB", "W", "OUTB", "B", pos, gain))
    s.append(uscita("MAIN", "OUTB", "220k", "220k", "100k"))
    s.append(uscita("FIX1", "OUTF1", "470k", "470k", "10k"))
    s.append(uscita("FIX2", "OUTF2", "470k", "470k", "50k"))
    return "".join(s)


def nomi_stampa(pos):
    """Le grandezze del blocco guasto da stampare nel punto di lavoro."""
    x = {"A": "xa", "F1": "xf1", "F2": "xf2", "B": "xb"}[pos]
    v = []
    for p in dispositivi():
        n = p[0].lower()
        if n[0] == "q":
            v += ["@q.%s.%s[p]" % (x, n), "@q.%s.%s[ic]" % (x, n)]
        elif n[0] == "j":
            v += ["@j.%s.%s[id]" % (x, n)]
        elif n[0] == "r":
            v += ["@r.%s.%s[p]" % (x, n)]
    v += ["v(%s.d1n)" % x, "v(%s.s1)" % x, "v(%s.d2n)" % x, "v(%s.s2)" % x,
          "v(%s.vpf)" % x, "v(%s.nx)" % x, "v(%s.ny)" % x, "v(%s.nref)" % x]
    return v


def deck_op(pos, gain, modo):
    t = "L45a op %s g%d %s - punto di lavoro col guasto inserito\n" % (pos, gain, modo)
    g = ("-", None) if modo == "rif" else (pos, modo)
    corpo = canale(g, gain, "DC 0", "DC 0", "DC 1")
    st = ["v(outa)", "v(outf1)", "v(outf2)", "v(outb)", "v(mainc)", "v(mainjack)",
          "v(fix1jack)", "v(fix2jack)", "i(vpp)", "i(vmm)"] + nomi_stampa(pos)
    ctrl = ".control\nset noaskquit\nop\n"
    for k in range(0, len(st), 1):
        ctrl += "print %s\n" % st[k]
    ctrl += "quit\n.endc\n.end\n"
    return t + corpo + ctrl


def deck_tr(pos, gain, modo, musica, mute, tfine=None, gear=False, taglio=None):
    t_f = 0.3
    t_rel = 1.0
    t_fine = tfine or (3.0 if mute else 2.3)
    sig = "SIN(0 3.818 1k)" if musica else "DC 0"
    ctl = "DC 0" if modo == "rif" else "PWL(0 0 %g 0 %g 1)" % (t_f, t_f + 10e-6)
    mt = "PWL(0 1 %g 1 %g 0)" % (t_rel, t_rel + 1e-3) if mute else "DC 0"
    if taglio is not None:
        # un rivelatore ideale + il rele': il mute si inserisce TAGLIO s dopo il guasto, in 100 us
        mt = "PWL(0 0 %g 0 %g 1)" % (t_f + taglio, t_f + taglio + 100e-6)
    passo = "10u" if musica else "50u"
    t = "L45a tr %s g%d %s musica=%d mute=%d - guasto a %g s\n" % (pos, gain, modo, musica, mute, t_f)
    corpo = canale((pos if modo != "rif" else "-", None if modo == "rif" else modo), gain, sig, mt, ctl)
    # Il calore e lo stato finale: medie sugli ultimi 10 ms (un'oscillazione si media, e la sua
    # ampiezza si legge da MAX - MIN dell'uscita del blocco nella stessa finestra).
    x = {"A": "xa", "F1": "xf1", "F2": "xf2", "B": "xb"}[pos]
    pot = []
    for p in dispositivi():
        n = p[0].lower()
        if n[0] in "qr":
            pot.append(("p_" + n, "@%s.%s.%s[p]" % (n[0], x, n)))
    salva = " ".join(v for _, v in pot)
    salva += " @j.%s.jq110a[id] @j.%s.jq110b[id] v(%s.d1n) v(%s.s1) v(%s.d2n) v(%s.s2)" % ((x,) * 6)
    da, a_ = t_fine - 10e-3, t_fine
    misure = ""
    for nome, v in pot:
        misure += "meas tran %s AVG %s from=%g to=%g\n" % (nome, v, da, a_)
    misure += ("let pja = @j.{x}.jq110a[id] * (v({x}.d1n) - v({x}.s1))\n"
               "let pjb = @j.{x}.jq110b[id] * (v({x}.d2n) - v({x}.s2))\n").format(x=x)
    misure += "meas tran p_jq110a AVG pja from=%g to=%g\n" % (da, a_)
    misure += "meas tran p_jq110b AVG pjb from=%g to=%g\n" % (da, a_)
    nomi = [n for n, _ in pot] + ["p_jq110a", "p_jq110b"]
    for k, v in (("out", "v(out%s)" % pos.lower()), ("ipp", "i(vpp)"), ("imm", "i(vmm)")):
        misure += "meas tran %s_avg AVG %s from=%g to=%g\n" % (k, v, da, a_)
        misure += "meas tran %s_max MAX %s from=%g to=%g\n" % (k, v, da, a_)
        misure += "meas tran %s_min MIN %s from=%g to=%g\n" % (k, v, da, a_)
        nomi += [k + "_avg", k + "_max", k + "_min"]
    misure += "echo \"grandezza,valore\" > %s_fine.csv\n" % modo
    for n in nomi:
        misure += "echo \"%s,$&%s\" >> %s_fine.csv\n" % (n, n, modo)
    ctrl = (".control\nset noaskquit\noption itl1=1000\n" + ("option method=gear\n" if gear else "")) + (
            "save v(mainjack) v(fix1jack) v(fix2jack) v(outa) v(outf1) v(outf2) v(outb) i(vpp) i(vmm) %s\n"
            "tran 1u %g 0 %s\n"
            "wrdata %s.dat v(mainjack) v(fix1jack) v(fix2jack) v(outa) v(outf1) v(outf2) v(outb) i(vpp) i(vmm)\n"
            "%squit\n.endc\n.end\n") % (salva, t_fine, passo, modo, misure)
    return t + corpo + ctrl


def scrivi(path, testo):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(testo)


def main(argv):
    cmd = argv[1]
    if cmd == "modi":
        with open(os.path.join(L45A, "modi.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["modo", "parte", "tipo", "terminali"])
            for m, nome, tipo, a, b in modi():
                scrivi(os.path.join(L45A, "inc", m + ".subckt"), subckt_guasto(m))
                w.writerow([m, nome, tipo, "%s-%s" % (a, b) if b is not None else str(a)])
        scrivi(os.path.join(L45A, "inc", "CTRL_OUT_VP.subckt"), subckt_controllo())
        print("modi: %d" % len(modi()))
    elif cmd == "op":
        pos = argv[2]
        gain = int(argv[3]) if len(argv) > 3 else 0
        var = "op_%s" % pos + ("_g%d" % gain if gain else "")
        p = os.path.join(L45A, "deck", var, "rif.cir")
        scrivi(p, deck_op(pos, gain, "rif"))
        lista = [p]
        for m, nome, tipo, a, b in modi():
            if m in RAIL_A_MASSA or (nome in SOLO and pos not in SOLO[nome]):
                continue
            p = os.path.join(L45A, "deck", var, m + ".cir")
            scrivi(p, deck_op(pos, gain, m))
            lista.append(p)
        scrivi(os.path.join(L45A, "deck", "lista_%s.txt" % var), "\n".join(lista) + "\n")
        print("%s: %d deck" % (var, len(lista)))
    elif cmd == "tr":
        args = argv[2:]
        gain, musica, mute, nome, tfine, gear, taglio = 0, False, False, None, None, False, None
        modi_tr = []
        pos = args.pop(0)
        while args:
            a = args.pop(0)
            if a == "--gain":
                gain = int(args.pop(0))
            elif a == "--musica":
                musica = True
            elif a == "--mute":
                mute = True
            elif a == "--nome":
                nome = args.pop(0)
            elif a == "--tfine":
                tfine = float(args.pop(0))
            elif a == "--gear":
                gear = True
            elif a == "--taglio":
                taglio = float(args.pop(0))
            elif a == "TUTTI":
                modi_tr.append("rif")
                for m, nm, tipo, x1, x2 in modi():
                    if m in RAIL_A_MASSA or (nm in SOLO and pos not in SOLO[nm]):
                        continue
                    modi_tr.append(m)
            else:
                modi_tr.append(a)
        var = "tr_" + (nome or pos)
        lista = []
        for m in modi_tr:
            p = os.path.join(L45A, "deck", var, m + ".cir")
            scrivi(p, deck_tr(pos, gain, m, musica, mute, tfine, gear, taglio))
            lista.append(p)
        scrivi(os.path.join(L45A, "deck", "lista_%s.txt" % var), "\n".join(lista) + "\n")
        print("%s: %d deck" % (var, len(lista)))
    elif cmd == "lista":
        scrivi(os.path.join(L45A, "deck", "lista_%s.txt" % argv[2]), "\n".join(argv[3:]) + "\n")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
