#!/usr/bin/env python3
"""L46b (copiato da L46a), ESPLORAZIONE - genera i deck di una variante in ../deck/<variante>/.

Ogni deck include ../inc/<variante>.inc (scritto da varianti.py) al posto di
gain_block_flat.inc, con @REPO@ (risolto da run_simulation.sh), cosi' i deck
restano rieseguibili dopo la chiusura del worktree.

Famiglie:
  op      tb_op (punto di lavoro, corrente di riposo)
  v1      tb_loop, tb_loop_blockA, tb_loop_bufferfissa (V1, criterio ADR-024);
          i wrdata delle curve diventano un `let` innocuo (#32), come in L40
  psrr    tb_zout_psrr_noise (PSRR+/-, Zout, rumore), tb_noise_breakdown (E5)
  thd     thd_1k, thd_10k, thd_20k: blocco B nei tre modi, sorgente 2,5 kOhm,
          47 Ohm + 4,7 uF + 10 kOhm (il banco dell'architetto, L43a), a due
          livelli d'uscita: lo = 0,2 V RMS (-20 dB, il livello musicale deciso
          dall'utente il 2026-10-01, ~99 dB SPL a 1 m) e hi = 2 V RMS (lo stress
          dell'architetto). `fourier` su v(vsn) (il pavimento numerico) e v(out)
  imd     CCIF 19 + 20 kHz, stesso banco, due toni uguali, picco composto pari
          al picco del sinusoide del livello; prodotto a 1 kHz contro un tono
  slew    il metodo di L12/L40 (genera_slew.py), senza spazzare C124 e R128:
          la variante e' gia' nel suo .inc
  arch    i due deck dell'architetto (thd_10_20000, imd_A) col solo include
          ripuntato: il controllo che il banco di oggi ridia L43a

Uso: /usr/bin/python3 genera.py <famiglia[,famiglia]|tutto> <variante>...
Scrive la lista dei deck in ../deck/lista_<etichetta>.txt (etichetta = primo argomento
con le virgole tolte) e la stampa.
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L46A = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L46A, *[".."] * 5))
TB = os.path.join(ROOT, "spice", "preamp", "tb")
REL = os.path.relpath(L46A, ROOT)
INC_BLOCCO = ".include @REPO@/spice/preamp/gain_block_flat.inc"
ARCH = os.path.join(ROOT, "docs", "preamp", "data", "2026-09-27", "L43a", "architetto")

MODI = [("0", 1.0, "1G", "1G"), ("3", 1.420, "0.1", "1G"), ("10", 3.152, "0.1", "0.1")]
LIVELLI = [("lo", 0.2 * 2 ** 0.5), ("hi", 2.0 * 2 ** 0.5)]   # picco in uscita, V
ASSESTA = 2e-3


def inc_var(v):
    return ".include @REPO@/%s/inc/%s.inc" % (REL, v)


def modelli():
    src = open(os.path.join(TB, "tb_loop.cir")).read().split("\n")
    return [r for r in src if r.startswith(".include") and "gain_block" not in r]


def copia(v, deck, curve=True):
    righe = open(os.path.join(TB, deck + ".cir")).read().split("\n")
    n = sum(r == INC_BLOCCO for r in righe)
    if n != 1:
        sys.exit("%s: include del blocco trovato %d volte" % (deck, n))
    righe = [inc_var(v) if r == INC_BLOCCO else r for r in righe]
    righe[0] = "%s.cir - L46b ESPLORAZIONE, variante %s (blocco da inc/%s.inc)" % (deck, v, v)
    if not curve:
        i = righe.index(".control")
        for k in range(i + 1, len(righe)):
            r = righe[k]
            if re.match(r"\s*wrdata\b", r):
                righe[k] = r[:len(r) - len(r.lstrip())] + "let l46a_nessuna_curva = 0"
    return "\n".join(righe)


def banco(v, titolo):
    return [titolo, "* generato da L46b/script/genera.py"] + modelli() + [inc_var(v), "",
            "VPP VPLUS 0 DC 15", "VMM VMINUS 0 DC -15"]


CARICO = ["CSTRAY RG 0 15p", "CSTRAY10 RG10 0 15p", "RRG RG 0 1G", "RRG10 RG10 0 1G",
          "RISO OUT OUTA 47", "COUT OUTA JACK 4.7u", "RBLEED JACK 0 220k", "RLOAD JACK 0 10k",
          ".options reltol=1e-6 abstol=1e-15 vntol=1e-9", ""]


def thd(v, f):
    tmax = 1.0 / (f * 2500)
    tstop = ASSESTA + 2.0 / f
    t = banco(v, "thd_%dk - L46b: THD a %d Hz, blocco B nei tre modi, livelli lo/hi; variante %s"
              % (f // 1000, f, v))
    # l'ampiezza del primo caso sta gia' nella netlist (innocuo: la `alter` la
    # riscrive). leggi_four.py controlla comunque l'ampiezza di v(vsn) di ogni caso.
    # Il primo imd sembrava a sorgente spenta: era una Note dentro la tabella (#37)
    a0 = LIVELLI[0][1] / MODI[0][1]
    t += ["VS VSN 0 SIN(0 %.6g %d)" % (a0, f), "RSRC VSN IN 2500"] + CARICO
    # itl1=1000: coi ZXT l'op della tran, dopo l'alter del modo, ripiegava sul
    # «transient op» (#33) e la THD usciva al 73 %. Il rimedio di L29c
    # (gminsteps=40) qui fa il contrario: fa ripiegare anche i MJE. Con itl1=1000
    # nessun ripiego, e sul blocco di oggi le cifre sono quelle senza opzione alla
    # sesta cifra (prova in L46a, report §1). Su tutti i deck: il banco resta uno
    c = [".control", "option itl1=1000", "set numdgt=10", "set fourgridsize=8192",
         "set nfreqs=10", "save out vsn"]
    for modo, g, rg, rg10 in MODI:
        for liv, vpk in LIVELLI:
            a = vpk / g
            c += ["alter rrg = %s" % rg, "alter rrg10 = %s" % rg10,
                  "alter @vs[sin] = [ 0 %.6g %d ]" % (a, f),
                  "tran %.4g %.6g 0 %.4g" % (tmax, tstop, tmax),
                  'echo "L46A_CASO modo=%s livello=%s freq=%d ampin=%.6g"' % (modo, liv, f, a),
                  "fourier %d v(vsn) v(out)" % f, "destroy all"]
    return "\n".join(t + c + [".endc", ".end", ""])


def imd(v):
    t = banco(v, "imd - L46b: IMD CCIF 19+20 kHz, blocco B nei tre modi, livelli lo/hi; variante %s" % v)
    a0 = LIVELLI[0][1] / 2 / MODI[0][1]     # vedi thd(): il primo caso nella netlist
    t += ["VS1 VSN VMIDS SIN(0 %.6g 19000)" % a0, "VS2 VMIDS 0 SIN(0 %.6g 20000)" % a0,
          "RSRC VSN IN 2500"] + CARICO
    c = [".control", "option itl1=1000", "set numdgt=10", "set fourgridsize=16384",
         "set nfreqs=24", "save out vsn"]     # itl1: vedi thd()
    for modo, g, rg, rg10 in MODI:
        for liv, vpk in LIVELLI:
            a = vpk / 2 / g
            c += ["alter rrg = %s" % rg, "alter rrg10 = %s" % rg10,
                  "alter @vs1[sin] = [ 0 %.6g 19000 ]" % a,
                  "alter @vs2[sin] = [ 0 %.6g 20000 ]" % a,
                  "tran 0.02u %.6g 0 0.02u" % (ASSESTA + 1e-3),
                  'echo "L46A_CASO modo=%s livello=%s freq=1000 ampin=%.6g"' % (modo, liv, a),
                  "fourier 1000 v(vsn) v(out)", "destroy all"]
    return "\n".join(t + c + [".endc", ".end", ""])


def slew(v):
    t = banco(v, "slew - L46b: slew rate e 20 kHz a fondo scala, blocco B +10 dB (metodo L12/L40); variante %s" % v)
    t += ["VSIN  VSRCN NMIDS SIN(0 3.818 20k)", "VSTEP NMIDS 0 PULSE(0 0 1m 1u 1u 1m 10m)",
          "RSRCB VSRCN IN 1.5",
          "CSTRAY   RG   0 15p", "RRG      RG   0 0.1",
          "CSTRAY10 RG10 0 15p", "RRG10    RG10 0 0.1",
          "RISO   OUT OUTA 47", "COUT   OUTA JACK 4.7u", "RBLEED JACK 0 220k", "RLOAD  JACK 0 100k", ""]
    c = [".control",
         'echo "amp_in,vo_max,vo_min,vo_mean_dc,slope_pos_vus,slope_neg_vus,ideal_slope_vus,gain" > slew_tab.csv',
         'echo "sr_rise_vus,sr_fall_vus" > slew_step.csv',
         "show c124 : capacitance", "show r128 : resistance",
         "foreach amp 3.818 1.909",
         "  alter @vsin[sin] = [ 0 $amp 20k ]",
         "  alter @vstep[pulse] = [ 0 0 1m 1u 1u 1m 10m ]",
         "  tran 10n 1m",
         "  let dvo = deriv(v(out))",
         "  meas tran vomax max v(out) from=0.7m to=0.95m",
         "  meas tran vomin min v(out) from=0.7m to=0.95m",
         "  meas tran vodc avg v(out) from=0.7m to=0.95m",
         "  meas tran vimax max v(in) from=0.7m to=0.95m",
         "  meas tran sp max dvo from=0.7m to=0.95m",
         "  meas tran sn min dvo from=0.7m to=0.95m",
         "  let spv = sp/1e6", "  let snv = sn/1e6",
         "  let gg = (vomax-vomin)/(2*vimax)",
         "  let ideal = 2*3.14159265*20e3*gg*vimax/1e6",
         '  echo "$amp,$&vomax,$&vomin,$&vodc,$&spv,$&snv,$&ideal,$&gg" >> slew_tab.csv',
         "  destroy all", "end",
         "alter @vsin[sin] = [ 0 0 20k ]",
         "alter @vstep[pulse] = [ -1.9 1.9 1m 1u 1u 1m 10m ]",
         "tran 10n 3m",
         "let dvo = deriv(v(out))",
         "meas tran srr max dvo from=0.95m to=1.5m",
         "meas tran srf min dvo from=1.95m to=2.5m",
         "let srrv = srr/1e6", "let srfv = srf/1e6",
         'echo "$&srrv,$&srfv" >> slew_step.csv',
         "destroy all", ".endc", ".end", ""]
    return "\n".join(t + c)


def arch(v, nome):
    righe = open(os.path.join(ARCH, nome + ".cir")).read().split("\n")
    out = []
    for r in righe:
        m = re.match(r"\.include \S+/L43a-architetto/(\S+)$", r)
        if m and m.group(1) == "spice/preamp/gain_block_flat.inc":
            r = inc_var(v)
        elif m:
            r = ".include @REPO@/" + m.group(1)
        out.append(r)
    out[0] = "arch_%s - L46b: il deck dell'architetto (L43a) col blocco della variante %s" % (nome, v)
    return "\n".join(out)


FAMIGLIE = {
    "op": lambda v: {"tb_op": copia(v, "tb_op")},
    "v1": lambda v: {d: copia(v, d, curve=False)
                     for d in ("tb_loop", "tb_loop_blockA", "tb_loop_bufferfissa")},
    "psrr": lambda v: {"tb_zout_psrr_noise": copia(v, "tb_zout_psrr_noise"),
                       "tb_noise_breakdown": copia(v, "tb_noise_breakdown")},
    # L46b: il clip, perche' la caduta sulla resistenza della cella costa headroom
    "clip": lambda v: {"tb_dc_headroom": copia(v, "tb_dc_headroom"),
                       "tb_v3_overload": copia(v, "tb_v3_overload")},
    "thd": lambda v: {"thd_%dk" % (f // 1000): thd(v, f) for f in (1000, 10000, 20000)},
    "imd": lambda v: {"imd": imd(v)},
    "slew": lambda v: {"slew": slew(v)},
    "arch": lambda v: {"arch_thd_10_20000": arch(v, "thd_10_20000"),
                       "arch_imd_A": arch(v, "imd_A")},
}

def main():
    fam = list(FAMIGLIE) if sys.argv[1] == "tutto" else sys.argv[1].split(",")
    lista = []
    for v in sys.argv[2:]:
        if not os.path.exists(os.path.join(L46A, "inc", v + ".inc")):
            sys.exit("manca inc/%s.inc: prima varianti.py %s" % (v, v))
        d = os.path.join(L46A, "deck", v)
        os.makedirs(d, exist_ok=True)
        for f in fam:
            for nome, testo in FAMIGLIE[f](v).items():
                p = os.path.join(d, nome + ".cir")
                open(p, "w").write(testo)
                lista.append(p)
    etich = sys.argv[1].replace(",", "")
    with open(os.path.join(L46A, "deck", "lista_%s.txt" % etich), "w") as fh:
        fh.write("\n".join(lista) + "\n")
    print("%d deck in deck/lista_%s.txt" % (len(lista), etich))


if __name__ == "__main__":
    main()
