#!/usr/bin/env python3
"""L48b (NC-041): il gradino al jack principale a uno scatto del volume o del trim, con la
continua del blocco A che attraversa la scala del trim e l'attenuatore, per quattro strade.

Genera un deck per variante (si corrono in parallelo):
  v0  oggi, il controfattuale: nessun condensatore fra il blocco A e il blocco B
  v1  il condensatore all'ingresso del blocco B (CB 1u) con la sua resistenza di gate (RGATE 1M)
  v2  il condensatore all'uscita del blocco A, PRIMA del trim (CA: 47u / 68u / 100u)
  v3  il condensatore fra il trim e l'attenuatore (CT: 10u)

La catena e' quella di spice/preamp/tb/tb_trim.cir (L16, L48a): la rete d'ingresso di ADR-064,
il blocco A a guadagno 1, la scala del trim di trim.py (845 / 464 / 464), i suoi contatti con
15 pF, il cablaggio 100 pF, l'attenuatore da 10 kOhm, il blocco B 0 / +3 / +10 dB, 47 ohm,
4,7 uF, il bleed 220 k e 100 k di carico.

L'ATTENUATORE e' una scala in serie da 10 kOhm (F4): ATT -RA- T1 -RB- T2 -RC- 0, e il cursore
passa dal punto T1 al punto T2 coi due contatti SW1 / SW2. Modi del cursore:
  m0  non cortocircuitante: SW1 apre a TE, SW2 chiude a TE + 1 ms (il gate del blocco B resta
      sospeso per 1 ms, se non ha resistenza di gate);
  m1  cortocircuitante: SW2 chiude a TE, SW1 apre a TE + 1 ms (per 1 ms RB e' in corto).

LA CONTINUA DEL BLOCCO A si impone con VOSA in serie fra il contatto del selettore e il gate, e
IOSA fornisce a R113 (dentro il blocco) la corrente dovuta a VOSA (limitations #44, come
iosa() del generatore V2). VOSA e' calcolata da questo script dalla continua propria del
blocco, letta dal deck di op (tb_l48b_op.cir) e passata con --va0.

Ogni caso rimette a valore OGNI grandezza che un caso altera (limitations #34); i casi sono
indici numerici, mai stringhe (#46). La tabella e' scritta con echo su un percorso assoluto.
"""
import argparse
import os

REPO = "/Users/roberto/EDA/.claude/worktrees/L48b"
QUI = os.path.dirname(os.path.abspath(__file__))

TE = 20e-3        # l'istante dello scatto
TT = 1e-3         # il trasferimento del contatto (ipotesi, la stessa di trim e guadagno)
TSTOP = 120e-3
TMAX = 5e-6

# I punti del volume, in dB sotto la cima: (da, a)
SCATTI_VOL = {1: (0.0, -2.0), 2: (-29.0, -27.0)}
# Il trim: 3 = da 0 a -6 dB, 4 = da -6 a -12 dB (volume in cima)
VA = {1: -6.6e-3, 2: -30e-3, 3: 30e-3}
GUAD = {0: (1e9, 1e9), 3: (0.1, 1e9), 10: (0.1, 0.1)}   # RRGB, RRG10B

VARIANTI = {
    0: [("oggi", {})],
    1: [("cb1u", {"cb": "1u", "rbyb": "1e12", "rgate": "1Meg"})],
    2: [("ca%s" % c, {"ca": c, "rbya": "1e12"}) for c in ("47u", "68u", "100u")],
    3: [("ct10u", {"ct": "10u", "rbyt": "1e12"})],
    # v4: il circuito di ADR-065, la scelta dell'utente: C_T 10u fra trim e volume, R_G 1M
    # sul gate del blocco B, il bilanciamento al centro
    4: [("finale", {"ct": "10u", "rbyt": "1e12", "rgate": "1Meg", "rbal": "50k"})],
}
BASE = {"ca": "1p", "rbya": "1m", "ct": "1p", "rbyt": "1m", "cb": "1p", "rbyb": "1m",
        "rgate": "1e12", "rbal": "1e12"}


def scala(da, a):
    """RA, RB, RC della scala da 10 k per i due punti del cursore."""
    k1, k2 = 10 ** (da / 20), 10 ** (a / 20)
    hi, lo = max(k1, k2), min(k1, k2)
    ra = max(10e3 * (1 - hi), 1e-3)
    rb = 10e3 * (hi - lo)
    rc = 10e3 * lo
    # SW1 sul punto di 'da', SW2 sul punto di 'a'
    t_da, t_a = ("T1", "T2") if k1 >= k2 else ("T2", "T1")
    return ra, rb, rc, t_da, t_a


def pwl_apre(t):
    return "[ 0 1 %.6g 1 %.6g 0 ]" % (t, t + 1e-6)


def pwl_chiude(t):
    return "[ 0 0 %.6g 0 %.6g 1 ]" % (t, t + 1e-6)


FERMO1 = "[ 0 1 1 1 ]"
FERMO0 = "[ 0 0 1 0 ]"

TESTA = """tb_l48b_scatti - L48b variante {var}: il gradino al jack a uno scatto del volume o del trim
* GENERATO da docs/preamp/data/2026-10-07/L48b/scatti/genera_scatti.py - non modificare a mano.
* Prima riga = titolo (limitations #10).
.include {repo}/models/jfet/lsk489.lib
.include {repo}/models/bjt_npn/mmbt5551.lib
.include {repo}/models/bjt_pnp/mmbt5401.lib
.include {repo}/models/bjt_npn/mje15032.lib
.include {repo}/models/bjt_pnp/mje15033.lib
.include {repo}/models/diodes/1n4148.lib
.include {repo}/models/bjt_pnp/ls350.lib
.include {repo}/spice/preamp/gain_block.subckt
* il blocco B vero non ha R113 (r_in=None, preamp_audio.py): la copia senza, scritta da
* genera_scatti.py dal file generato (col cursore aperto, m0, R113 deciderebbe il gate)
.include {subb}

VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15

* --- la sorgente scelta e la rete d'ingresso di ADR-064 (tb_trim.cir) ---
VSRC  VSN 0 DC 0 AC 1
RSRC  VSN JIN 1.5
RJ    JIN 0 10Meg
CIN   JIN SEL 1u
RSEL  SEL 0 470k
RKSEL SEL SELK 0.1
* la continua del blocco A (limitations #44: IOSA da' a R113 la corrente di VOSA)
VOSA  SELK AIN DC 0
IOSA  AIN 0 DC 0

XA AIN AOUT AFB ARG ARG10 VPLUS VMINUS GAINBLOCK
RARG   ARG   0 1G
RARG10 ARG10 0 1G

* --- v2: il condensatore all'uscita del blocco A, prima del trim (RBYA = 1m: assente) ---
CA   AOUT AOC 1p
RBYA AOUT AOC 1m

* --- la scala del trim, cand 2 di trim.py ---
RL1 AOC TAP6 845
RL2 TAP6 TAP12 464
RL3 TAP12 0 464

.model SWK SW(RON=0.1 ROFF=1e12 VT=0.5 VH=0.25)
* --- i contatti del trim, che si muovono nel tempo; 15 pF ciascuno ---
ST1R AOC ATOP NT1R 0 SWK
CT1R AOC ATOP 15p
ST1S T2C ATOP NT1S 0 SWK
CT1S T2C ATOP 15p
ST2R TAP6 T2C NT2R 0 SWK
CT2R TAP6 T2C 15p
ST2S TAP12 T2C NT2S 0 SWK
CT2S TAP12 T2C 15p
VT1R NT1R 0 PWL(0 1 1 1)
VT1S NT1S 0 PWL(0 0 1 0)
VT2R NT2R 0 PWL(0 1 1 1)
VT2S NT2S 0 PWL(0 0 1 0)

* --- v3: il condensatore fra il trim e l'attenuatore (RBYT = 1m: assente) ---
CTX  ATOP ATT 1p
RBYT ATOP ATT 1m
* il cablaggio verso l'attenuatore a pannello
CWIRE ATT 0 100p
* v4: il bilanciamento MN 50k allo scatto centrale (ADR-065), la pista dalla cima a massa
RBAL ATT 0 1e12

* --- l'attenuatore a scatti da 10 k, scala in serie, e il cursore ---
RA ATT T1 1m
RB T1 T2 2.057k
RC T2 0 7.943k
SW1 T1 WIP NW1 0 SWK
SW2 T2 WIP NW2 0 SWK
VW1 NW1 0 PWL(0 1 1 1)
VW2 NW2 0 PWL(0 0 1 0)
* il cavo del cursore dal pannello alla scheda: la stessa ipotesi del cablaggio della cima
* (100 pF). Senza, col cursore aperto (m0) il gate del blocco B non ha nessuna capacita' verso
* massa e il simulatore lo porta a 0 V in < 30 us: un artefatto del banco (sonda L48b).
CWIP WIP 0 100p

* --- v1: il condensatore all'ingresso del blocco B, con la sua resistenza di gate ---
CB    WIP BIN 1p
RBYB  WIP BIN 1m
RGATE BIN 0 1e12

* --- il blocco B, 0 / +3 / +10 dB ---
XB BIN BOUT BFB BRG BRG10 VPLUS VMINUS GAINBLOCKB
CSTB    BRG   0 15p
RRGB    BRG   0 1G
CSTB10  BRG10 0 15p
RRG10B  BRG10 0 1G

RISO   BOUT BOUTA 47
COUT   BOUTA JACK 4.7u
RBLEED JACK 0 220k
RLOAD  JACK 0 100k

.control
set noaskquit
* gmin 1e-15: col default (1e-12 S su ogni giunzione) il gate-drain del JFET a ~14 V porta
* ~14 pA che il modello non ha, e col cursore aperto (m0) il gate derivava di 289 uV al jack
* (sonda L48b: 0,48 uV con 1e-15). La corrente di gate vera (datasheet) e' in analizza.py.
option itl1=1000 gmin=1e-15
echo "var,cap,va_mv,guad_db,evento,modo,va_misurata_mv,jack_prima_uv,pk_uv" > {csv}
"""


def caso(var, nome, vals, va, va0, g, ev, modo, csv, onde=None):
    """Un caso: rimette tutto, applica la variante, l'evento e il modo, corre, misura."""
    vos = -(va - va0)            # AIN = SELK - VOSA, il blocco A segue AIN
    i_os = vos / 1e6             # IOSA AIN -> 0: toglie da AIN la corrente che R113 vi porta
    v = dict(BASE, **vals)
    out = ["* ---- caso %s va=%g g=%d ev=%d m=%d" % (nome, va * 1e3, g, ev, modo)]
    out += ["alter ca = %s" % v["ca"], "alter rbya = %s" % v["rbya"],
            "alter ctx = %s" % v["ct"], "alter rbyt = %s" % v["rbyt"],
            "alter cb = %s" % v["cb"], "alter rbyb = %s" % v["rbyb"],
            "alter rgate = %s" % v["rgate"], "alter rbal = %s" % v["rbal"],
            "alter vosa dc = %.6g" % vos, "alter iosa dc = %.6g" % i_os,
            "alter rrgb = %g" % GUAD[g][0], "alter rrg10b = %g" % GUAD[g][1]]
    # il trim e il volume: posizioni di partenza
    t1r, t1s, t2r, t2s = FERMO1, FERMO0, FERMO1, FERMO0       # 0 dB
    w1, w2 = FERMO1, FERMO0
    if ev in SCATTI_VOL:
        da, a = SCATTI_VOL[ev]
        ra, rb, rc, t_da, _ = scala(da, a)
        # SW1 deve stare sul punto di partenza: se 'da' e' il punto basso, i ruoli si scambiano
        su_t1 = (t_da == "T1")
        if modo == 0:          # non cortocircuitante
            apre, chiude = pwl_apre(TE), pwl_chiude(TE + TT)
        else:                  # cortocircuitante
            apre, chiude = pwl_apre(TE + TT), pwl_chiude(TE)
        w1, w2 = (apre, chiude) if su_t1 else (chiude, apre)
    else:
        ra, rb, rc, _, _ = scala(0.0, -2.0)    # volume fermo in cima, SW1 su T1 = cima
        if ev == 3:            # da 0 a -6: T1 reset -> set (T2 resta reset, TAP6)
            t1r, t1s = pwl_apre(TE), pwl_chiude(TE + TT)
        else:                  # da -6 a -12: T1 set fermo, T2 reset -> set
            t1r, t1s = FERMO0, FERMO1
            t2r, t2s = pwl_apre(TE), pwl_chiude(TE + TT)
    out += ["alter ra = %.6g" % ra, "alter rb = %.6g" % rb, "alter rc = %.6g" % rc,
            "alter @vt1r[pwl] = %s" % t1r, "alter @vt1s[pwl] = %s" % t1s,
            "alter @vt2r[pwl] = %s" % t2r, "alter @vt2s[pwl] = %s" % t2s,
            "alter @vw1[pwl] = %s" % w1, "alter @vw2[pwl] = %s" % w2,
            "tran 20u %g 0 %g" % (TSTOP, TMAX),
            "meas tran vam find v(aout) at=%g" % (TE - 2e-3),
            "meas tran jb find v(jack) at=%g" % (TE - 1e-4),
            "meas tran jmax max v(jack) from=%g to=%g" % (TE - 1e-4, TSTOP),
            "meas tran jmin min v(jack) from=%g to=%g" % (TE - 1e-4, TSTOP),
            "let vamv = vam*1e3",
            ] + (["wrdata %s_%s_m%d.txt v(wip) v(bin) v(bout) v(jack)" % (onde, nome, modo)] if onde else []) + [
            "let jbu = jb*1e6",
            "let pa = abs(jmax - jb)",
            "let pb = abs(jmin - jb)",
            "let pku = pa*1e6",
            "if pb > pa",
            "  let pku = pb*1e6",
            "end",
            'echo "%s,%s,%g,%d,%d,%d,$&vamv,$&jbu,$&pku" >> %s'
            % (var, nome, va * 1e3, g, ev, modo, csv),
            "destroy all"]
    return out


def blocco_b(uscita):
    """gain_block.subckt senza R113, col nome GAINBLOCKB. Rifiuta se R113 non c'e' una volta."""
    src = open(os.path.join(REPO, "spice/preamp/gain_block.subckt")).read().splitlines()
    r113 = [r for r in src if r.split()[:1] == ["R113"]]
    assert len(r113) == 1 and r113[0].split()[1:4] == ["IN", "0", "1MEG"], r113
    out = []
    for r in src:
        if r.split()[:1] == ["R113"]:
            out.append("* R113 tolta: il blocco B ha r_in=None (L48b)")
            continue
        out.append(r.replace("GAINBLOCK", "GAINBLOCKB") if r.startswith((".subckt", ".ends")) else r)
    p = os.path.join(uscita, "gain_block_b_senza_r113.subckt")
    with open(p, "w") as f:
        f.write("\n".join(out) + "\n")
    return p


def caso_ac(var, nome, vals, g, att, csv):
    """E9 e E5 di una variante: trim a 0 dB, volume in cima (att 1) o a meta' (att 2, 5k/5k come
    tb_trim.cir). E9: la risposta a 20 Hz riferita a 1 kHz, col carico 100 k (il cj) e 10 k (il
    finale futuro di ADR-007). E5: noise al jack, 100 k, sorgente 430 ohm (il phono) e 1,5 ohm."""
    v = dict(BASE, **vals)
    ra, rb, rc = (1e-3, 2057.0, 7943.0) if att == 1 else (5000.0, 1e-3, 5000.0)
    out = ["* ---- ac %s g=%d att=%d" % (nome, g, att),
           "alter ca = %s" % v["ca"], "alter rbya = %s" % v["rbya"],
           "alter ctx = %s" % v["ct"], "alter rbyt = %s" % v["rbyt"],
           "alter cb = %s" % v["cb"], "alter rbyb = %s" % v["rbyb"],
           "alter rgate = %s" % v["rgate"], "alter rbal = %s" % v["rbal"],
           "alter vosa dc = 0", "alter iosa dc = 0",
           "alter rrgb = %g" % GUAD[g][0], "alter rrg10b = %g" % GUAD[g][1],
           "alter ra = %.6g" % ra, "alter rb = %.6g" % rb, "alter rc = %.6g" % rc,
           "alter @vt1r[pwl] = %s" % FERMO1, "alter @vt1s[pwl] = %s" % FERMO0,
           "alter @vt2r[pwl] = %s" % FERMO1, "alter @vt2s[pwl] = %s" % FERMO0,
           "alter @vw1[pwl] = %s" % FERMO1, "alter @vw2[pwl] = %s" % FERMO0]
    for rl in ("100k", "10k"):
        out += ["alter rload = %s" % rl, "alter rsrc = 1.5",
                "ac dec 50 10 20k",
                "let rdb = vdb(jack)",
                "meas ac r20 find rdb at=20",
                "meas ac r1k find rdb at=1000",
                "let e9 = r20 - r1k",
                'echo "%s,%s,%d,%d,%s,e9_db,$&e9" >> %s' % (var, nome, g, att, rl, csv),
                "destroy all"]
    out.append("alter rload = 100k")
    for rs in ("1.5", "430"):
        out += ["alter rsrc = %s" % rs,
                "noise v(jack) vsrc dec 50 20 20000 1",
                "setplot noise2",
                "let onu = onoise_total*1e6",
                'echo "%s,%s,%d,%d,%s,e5_uv,$&onu" >> %s' % (var, nome, g, att, rs, csv),
                "destroy all"]
    out.append("alter rsrc = 1.5")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--va0", type=float, required=True,
                    help="la continua propria del blocco A, in V (dal deck di op)")
    ap.add_argument("--uscita", default=os.path.join(QUI, "deck"))
    ap.add_argument("--rapido", action="store_true", help="un caso per variante (sonda)")
    ap.add_argument("--op", action="store_true", help="solo il deck di op (la continua propria)")
    ap.add_argument("--ac", action="store_true", help="il deck di E9 e E5 per ogni variante")
    a = ap.parse_args()
    os.makedirs(a.uscita, exist_ok=True)
    subb = blocco_b(a.uscita)
    if a.op:
        testa = TESTA.format(var="op", repo=REPO, csv="/dev/null", subb=subb).split(".control")[0]
        with open(os.path.join(a.uscita, "tb_l48b_op.cir"), "w") as f:
            f.write(testa + ".control\noption itl1=1000 gmin=1e-15\nop\nprint v(aout) v(atop) v(bin) v(bout) v(jack)\n"
                    "quit\n.endc\n\n.end\n")
        print(os.path.join(a.uscita, "tb_l48b_op.cir"))
        return
    if a.ac:
        csv = os.path.join(a.uscita, "ac_rumore.csv")
        rete = TESTA.format(var="ac", repo=REPO, csv="/dev/null", subb=subb).split(".control")[0]
        # In AC un SW resta spento anche col comando a 1, e anche dichiarato ON sull'istanza: la
        # sonda di L48b vedeva la cima dell'attenuatore a -58 dB e il jack a -165 dB. Nel deck AC
        # i contatti sono resistenze ferme (0,1 ohm chiuso, 1 G aperto, come tb_trim.cir):
        # trim a 0 dB (T1 reset, T2 reset), cursore su T1.
        for sw, val in (("ST1R", "0.1"), ("ST1S", "1G"), ("ST2R", "0.1"), ("ST2S", "1G"),
                        ("SW1", "0.1"), ("SW2", "1G")):
            riga = [r for r in rete.splitlines() if r.split()[:1] == [sw]]
            assert len(riga) == 1, sw
            a_, b_ = riga[0].split()[1:3]
            rete = rete.replace(riga[0], "R%s %s %s %s" % (sw, a_, b_, val))
        righe = [rete,
                 ".control", "set noaskquit", "option itl1=1000 gmin=1e-15",
                 'echo "var,cap,guad_db,att,carico_o_rsrc,grandezza,valore" > %s' % csv]
        for var, caps in VARIANTI.items():
            for nome, vals in caps:
                for g in (0, 10):
                    for att in (1, 2):
                        righe += caso_ac(var, nome, vals, g, att, csv)
        righe += ["quit", ".endc", "", ".end", ""]
        with open(os.path.join(a.uscita, "tb_l48b_ac_rumore.cir"), "w") as f:
            f.write("\n".join(righe))
        print(os.path.join(a.uscita, "tb_l48b_ac_rumore.cir"))
        return
    for var, caps in VARIANTI.items():
        csv = os.path.join(a.uscita, "scatti_v%d.csv" % var)
        righe = [TESTA.format(var=var, repo=REPO, csv=csv, subb=subb)]
        for nome, vals in caps:
            for iv, va in VA.items():
                for g in GUAD:
                    for ev in (1, 2, 3, 4):
                        modi = (0, 1) if ev in SCATTI_VOL else (0,)
                        for modo in modi:
                            if a.rapido and not (iv == 1 and g == 10 and ev == 1):
                                continue
                            righe += caso(var, nome, vals, va, a.va0, g, ev, modo, csv,
                                          os.path.join(a.uscita, "onde_v%d" % var) if a.rapido else None)
        righe += ["quit", ".endc", "", ".end", ""]
        nome_deck = os.path.join(a.uscita, "tb_l48b_scatti_v%d.cir" % var)
        with open(nome_deck, "w") as f:
            f.write("\n".join(righe))
        print(nome_deck)


if __name__ == "__main__":
    main()
