#!/usr/bin/env python3
"""L62b (copiato da L60d1, che lo copiava da L56): V4 a caldo sul blocco coi quattro diodi di ADR-090
(inc/l62b.inc = spice/preamp/gain_block_flat.inc del sorgente). Un'opzione in piu', `diodi`: D154-D157
alla Tj del finale NPN (Q132), il caso peggiore dei diodi montati vicino ai finali, che ADR-090 nomina
nel «Da riaprire se». Senza l'opzione i diodi stanno all'aria (dissipano ~0 a blocco sano). Da
confrontare con L60d1/sintesi_caldo.csv, `l60d1--sot223` (lo stesso blocco senza diodi).

L56 (NC-060): il blocco con ogni giunzione alla sua temperatura, per ogni variante.

Generalizza L53/temp/autoriscaldamento.py (limitations #55: SPICE non scalda i dispositivi),
iterando: la potenza di ogni dispositivo si legge a temperatura uniforme (passo 1), poi ogni passo
K rifa' l'`op` con ogni giunzione alla Tj del passo K-1, fino a che le Tj smettono di muoversi.
L53 si fermava al passo 1, assumendo che la potenza cambiasse poco col calore: NON e' cosi'. Il
generatore di coda (Q106) e il carico del VAS (Q125) stanno sullo stesso riferimento a diodi, che
resta all'aria mentre loro scaldano: la loro Vbe scende, la corrente sale (coda 4,51 -> 4,81 mA,
VAS 142 -> 161 mW al passo 2, aria 27). tj/<spec>.csv riporta l'ultimo passo e il precedente.

  Tj = Ta + P * R_thJA, R_thJA dai datasheet in vendor/ (still air), come L53:
    MMBT5401  Q122 (il VAS): 357 C/W con 15x15 mm di rame (variante «rame»), 403 piazzola minima;
              QE1 (l'inseguitore delle varianti ef_*): 403 sempre (nessun rame dichiarato)
    MMBT5551  417 (Q125 il carico del VAS, Q106 la coda, i cascode, Q127)
    LS350     doppio sullo stesso die: 233 C/W sulla somma delle due P
    LSK489    doppio: 250 C/W sulla somma
    MJE15032/33  TO-220 senza dissipatore: 62,5 C/W
  P = Ic * (Vc - Ve) per i BJT, Id * (Vd - Vs) per i JFET (come L53).

Le opzioni termiche, che non cambiano il circuito (spec = variante[--opzione...]):
  acc     i due diodi del riferimento (D102, D103) alla Tj di Q106, il generatore di coda:
          l'accoppiamento termico perfetto (rame comune nel layout). Limite superiore di quanto
          l'accoppiamento puo' dare.
  freddo  il VAS (Q122) e il suo carico (Q125) a meta' R_thJA: un package che scalda la meta'
          (SOT-89 / SOT-223 su rame). Sensibilita', senza un modello nuovo.

Le condizioni: u27 (27 gradi uniformi, il banco di L46b: il controllo), e t27/t57 (aria a 27 / 57
gradi) x rame/minima. Ogni deck di prova: THD 20 kHz (3 modi x sorgente 2,5 / 5,6 kOhm x 0,2 / 2
V, il banco di V4 di L53), IMD CCIF (genera.py di L46b, sorgente 2,5 kOhm), e il gradino della
coda (R107 da +10 % a -20 %, 0 dB, 2,5 kOhm, 0,2 / 2 V) su u27, t27_rame, t57_rame.

Uso:
  caldo.py op   <spec>...   -> deck/op_<spec>/op_p1.cir           (poi esegui.sh)
  caldo.py p<K> <spec>...   -> deck/op_<spec>/op_p<K>_<cond>.cir   (K = 2, 3, ...; poi esegui.sh)
  caldo.py deck<K> <spec>... -> dal passo K: inc/<spec>__<cond>.inc, tj/<spec>.csv, deck/<spec>/*.cir
Ogni fase scrive la lista dei deck in deck/lista_<fase>.txt.
"""
import csv
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LOTTO = os.path.dirname(QUI)
sys.path.insert(0, QUI)
import genera  # noqa: E402  (L46b: imd())

REL = os.path.relpath(LOTTO, genera.ROOT)
CALDE = [(27, "rame"), (27, "minima"), (57, "rame"), (57, "minima")]
RC_LS350 = 231.405      # models/bjt_pnp/ls350.lib
R107 = [150.7, 144, 137, 130.2, 123.3, 116.4, 109.6]

MODELLI = """.include @REPO@/models/jfet/lsk489.lib
.include @REPO@/models/bjt_npn/mmbt5551.lib
.include @REPO@/models/bjt_pnp/mmbt5401.lib
.include @REPO@/models/bjt_npn/mje15032.lib
.include @REPO@/models/bjt_pnp/mje15033.lib
.include @REPO@/models/diodes/1n4148.lib
.include @REPO@/models/bjt_pnp/ls350.lib
"""
BANCO = """
VPP VPLUS 0 DC 15
VMM VMINUS 0 DC -15
VS VSN 0 SIN(0 0.282843 20000)
RSRC VSN IN 2500
CSTRAY RG 0 15p
CSTRAY10 RG10 0 15p
RRG RG 0 1G
RRG10 RG10 0 1G
RISO OUT OUTA 47
COUT OUTA JACK 4.7u
RBLEED JACK 0 220k
RLOAD JACK 0 10k
.temp {ta}
.options reltol=1e-6 abstol=1e-15 vntol=1e-9
"""
CONTROL = """
.control
option itl1=1000
set numdgt=10
set fourgridsize=8192
set nfreqs=10
"""
THD = """alter rsrc = {rs}
alter rrg = {rrg}
alter rrg10 = {rrg10}
alter @vs[sin] = [ 0 {a} 20000 ]
save out vsn
tran 2e-08 0.0021 0 2e-08
echo "L46A_CASO modo={modo} livello={liv} freq=20000 ampin={a} rs={rs}"
fourier 20000 v(vsn) v(out)
destroy all
"""
CODA = """alter rsrc = 2500
alter rrg = 1G
alter rrg10 = 1G
alter r107 = {r}
op
echo "L56_CODA r107={r}"
print @q106[ic] v(out)
destroy all
alter @vs[sin] = [ 0 {a} 20000 ]
save out vsn
tran 2e-08 0.0021 0 2e-08
echo "L46A_CASO modo=0 livello={liv} freq=20000 ampin={a} rs=2500 r107={r}"
fourier 20000 v(vsn) v(out)
destroy all
"""
MODI = {0: ("1G", "1G", 1.0), 3: ("0.1", "1G", 1.4202), 10: ("0.1", "0.1", 3.1523)}
LIVELLI = (("lo", 0.282843), ("hi", 2.82843))


def parti(spec):
    v, *opz = spec.split("--")
    for o in opz:
        if o not in ("acc", "freddo", "sot223", "diodi"):
            sys.exit("opzione sconosciuta: %s" % o)
    return v, set(opz)


def inc_rel(nome):
    return "@REPO@/%s/inc/%s.inc" % (REL, nome)


def dispositivi(variante):
    """{nome: (tipo, [nodi], modello)} per Q, J, D dell'inc della variante."""
    d = {}
    for r in open(os.path.join(LOTTO, "inc", variante + ".inc")):
        p = r.split()
        if p and p[0][0] in "QJD":
            n = 3 if p[0][0] in "QJ" else 2
            d[p[0]] = (p[0][0], p[1:1 + n], p[1 + n])
    return d


def scrivi(p, testo):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(testo)
    return p


def deck_op(titolo, inc, temps, disp, marca):
    """Un `op` per temperatura dell'aria: tutti i nodi e la corrente di ogni Q/J."""
    corr = " ".join("@%s[%s]" % (n.lower(), "ic" if t == "Q" else "id")
                    for n, (t, _, _) in sorted(disp.items()) if t in "QJ")
    s = titolo + "\n* generato da L56/script/caldo.py\n" + MODELLI
    s += ".include %s\n" % inc + BANCO.format(ta=temps[0]).replace("VS VSN 0 SIN(0 0.282843 20000)", "VS VSN 0 DC 0")
    s += "\n.control\noption itl1=1000\n"   # L56: come i deck di distorsione (L46a)
    for ta in temps:
        s += "set temp = %d\nop\necho \"%s ta=%d\"\nprint all\nprint %s\ndestroy all\n" % (ta, marca, ta, corr)
    return s + ".endc\n.end\n"


def leggi_op(log, marca):
    t = open(log, errors="replace").read()
    # «source stepping failed»: ngspice stampa lo stesso una soluzione, non convergente (L56: il
    # passo 2 di adr067 a 57 gradi col rame, VPF a 0,94 V e correnti quasi nulle, letto per buono
    # finche' questo controllo non c'era). «gmin stepping failed» da solo e' normale: segue
    # un altro metodo.
    for x in ("Error", "aborted", "too many args", "source stepping failed"):
        if x in t:
            sys.exit("%s: %s" % (log, x))
    if marca not in t:
        sys.exit("%s: manca %s" % (log, marca))
    b = t.split(marca, 1)[1]
    b = re.split(r"L56_OP\S* ta=", b)[0]
    v = {"0": 0.0, "vplus": 15.0, "vminus": -15.0}
    for m in re.finditer(r"^(\S+) = ([-+0-9.eE]+)", b, re.M):
        k = re.sub(r"^v\((.*)\)$", r"\1", m.group(1).lower())
        v[k] = float(m.group(2))
    # seconda difesa: il punto di lavoro deve essere quello acceso (VPF ~0,15 V sotto V+, coda
    # oltre 3 mA)
    if not (v.get("vpf", 0) > 14.5 and v.get("@q106[ic]", 0) > 3e-3):
        sys.exit("%s %s: punto di lavoro spento (vpf %s, coda %s)"
                 % (log, marca, v.get("vpf"), v.get("@q106[ic]")))
    return v


def potenze(v, disp):
    p = {}
    for n, (t, nodi, _) in disp.items():
        if t == "D":
            continue
        i = v["@%s[%s]" % (n.lower(), "ic" if t == "Q" else "id")]
        a, _, e = nodi
        p[n] = abs(i * (v[a.lower()] - v[e.lower()]))
    return p


def tj(ta, var, opz, p, disp):
    t = {}
    for n, (k, _, mod) in disp.items():
        if k == "D" or n in ("Q121A", "Q121B", "JQ110A", "JQ110B"):
            continue
        if mod == "MMBT5401":
            r = (357 if var == "rame" else 403) if n == "Q122" else 403
        elif mod == "MMBT5551":
            r = 417
        elif mod.startswith("Qmje"):
            r = 62.5
        else:
            sys.exit("R_thJA sconosciuta per %s %s" % (n, mod))
        if "freddo" in opz and n in ("Q122", "Q125"):
            r /= 2
        if "sot223" in opz and n in ("Q122", "Q125"):
            # L56, dopo la scelta dell'utente (rimedio subito): DZT5401 / DZT5551, lo stesso die in
            # SOT-223 (modello del costruttore identico, file collettivo Transistors >100V).
            # 125 C/W sulla piazzola minima raccomandata: DZT5401 DS31218 Rev. 4-2, nota 5. Per il
            # DZT5551 il datasheet (DS31219 Rev. 4-2) da' solo 62,5 C/W su 50x50 mm di rame: la
            # stessa cifra del DZT5401 sulla piazzola minima e' un'IPOTESI dichiarata (stesso
            # package). Niente rame grande: la linguetta e' il collettore, su NX / NY.
            r = 125.0
        t[n] = ta + p[n] * r
    t["Q121A"] = t["Q121B"] = ta + (p["Q121A"] + p["Q121B"]) * 233
    t["JQ110A"] = t["JQ110B"] = ta + (p["JQ110A"] + p["JQ110B"]) * 250
    if "acc" in opz:
        t["D102"] = t["D103"] = t["Q106"]
    if "diodi" in opz:
        # L62b: i diodi di riserva (ADR-090) alla Tj del finale NPN
        for n in ("D154", "D155", "D156", "D157"):
            if n not in disp:
                sys.exit("opzione diodi: %s non e' nell'inc" % n)
            t[n] = t["Q132"]
    return t


def inc_caldo(variante, nome, t, nota):
    righe = []
    for r in open(os.path.join(LOTTO, "inc", variante + ".inc")):
        q = r.split()
        if q and q[0] in t:
            r = r.rstrip("\n") + " temp=%.1f\n" % t[q[0]]
        righe.append(r)
    return scrivi(os.path.join(LOTTO, "inc", nome + ".inc"),
                  "* L56 caldo.py: %s, %s\n" % (nome, nota) + "".join(righe))


def specchio(v):
    """Q121B: tensione emettitore-collettore ai morsetti e polarizzazione della giunzione
    base-collettore interna (positiva = diretta), con la caduta in RC del modello."""
    ic = abs(v["@q121b[ic]"])
    vec = v["nme2"] - v["nhi"]
    vbc_int = (v["nhi"] + ic * RC_LS350) - v["nmiri"]
    return ic, vec, vbc_int


def specchio_a(v):
    """Q121A, il lato a diodo: collettore su NMIRI (oggi) o su NMIRC (col transistor di aiuto).
    Senza aiuto la sua giunzione base-collettore interna e' diretta di Ic*RC, sempre."""
    ic = abs(v["@q121a[ic]"])
    return (v.get("nmirc", v["nmiri"]) + ic * RC_LS350) - v["nmiri"]


def deck_prova(spec, cond, ta, inc, coda):
    titolo = "%s - L56: THD 20 kHz, %s, %s" % (spec, cond, "aria %d gradi" % ta)
    s = "thd20k_" + titolo + "\n* generato da L56/script/caldo.py\n" + MODELLI
    s += ".include %s\n" % inc + BANCO.format(ta=ta) + CONTROL
    for m in (0, 3, 10):
        rrg, rrg10, g = MODI[m]
        for rs in (2500, 5600):
            for liv, a in LIVELLI:
                s += THD.format(rs=rs, rrg=rrg, rrg10=rrg10, a="%.6g" % (a / g), liv=liv, modo=m)
    out = {"thd20k_%s" % cond: s + ".endc\n.end\n"}
    nome_inc = inc.rsplit("/", 1)[1][:-4]
    im = genera.imd(nome_inc).replace(".options reltol", ".temp %d\n.options reltol" % ta, 1)
    im = im.replace("imd - L46b:", "imd - L56 (genera.py di L46b), %s, %s:" % (spec, cond), 1)
    out["imd_%s" % cond] = im
    if coda:
        c = "coda_" + titolo.replace("THD 20 kHz", "THD 20 kHz contro R107") + \
            "\n* generato da L56/script/caldo.py\n" + MODELLI + ".include %s\n" % inc + \
            BANCO.format(ta=ta) + CONTROL
        for r in R107:
            for liv, a in LIVELLI:
                c += CODA.format(r=r, a=a, liv=liv)
        out["coda_%s" % cond] = c + ".endc\n.end\n"
    return out


def main():
    fase, specs = sys.argv[1], sys.argv[2:]
    lista = []
    for spec in specs:
        var, opz = parti(spec)
        disp = dispositivi(var)
        dop = os.path.join(LOTTO, "deck", "op_" + spec)
        rop = os.path.join(LOTTO, "run", "op_" + spec)
        if fase == "op":
            lista.append(scrivi(os.path.join(dop, "op_p1.cir"),
                                deck_op("op_p1 - L56: %s a temperatura uniforme" % spec,
                                        inc_rel(var), (27, 57), disp, "L56_OP")))
            continue
        p1 = {ta: leggi_op(os.path.join(rop, "op_p1", "op_p1.log"), "L56_OP ta=%d" % ta)
              for ta in (27, 57)}

        def passo(k, ta, rv):
            """Il punto di lavoro del passo k (1: uniforme; k >= 2: alle Tj del passo k-1)."""
            if k == 1:
                return p1[ta]
            b = "op_p%d_t%d_%s" % (k, ta, rv)
            return leggi_op(os.path.join(rop, b, b + ".log"), "L56_OP%d ta=%d" % (k, ta))

        if fase.startswith("p"):
            # pK: i deck del passo K dalle Tj del passo K-1 (L56: un passo solo non converge,
            # la coda e il carico del VAS salgono col calore e scaldano di piu')
            k = int(fase[1:])
            for ta, rv in CALDE:
                t = tj(ta, rv, opz, potenze(passo(k - 1, ta, rv), disp), disp)
                nome = "%s__t%d_%s_p%d" % (spec, ta, rv, k - 1)
                inc_caldo(var, nome, t, "Tj del passo %d (aria %d, %s)" % (k - 1, ta, rv))
                lista.append(scrivi(os.path.join(dop, "op_p%d_t%d_%s.cir" % (k, ta, rv)),
                                    deck_op("op_p%d - L56: %s, Tj del passo %d, aria %d, %s"
                                            % (k, spec, k - 1, ta, rv),
                                            inc_rel(nome), (ta,), disp, "L56_OP%d" % k)))
            continue
        if not fase.startswith("deck"):
            sys.exit("fase: op | p<K> | deck<K>")
        k = int(fase[4:])
        tab = []
        for ta, rv in CALDE:
            v2 = passo(k, ta, rv)
            pa, pb = potenze(passo(k - 1, ta, rv), disp), potenze(v2, disp)
            ta1, tb2 = tj(ta, rv, opz, pa, disp), tj(ta, rv, opz, pb, disp)
            cond = "t%d_%s" % (ta, rv)
            nome = "%s__%s" % (spec, cond)
            inc_caldo(var, nome, tb2, "Tj del passo %d (aria %d, %s)" % (k, ta, rv))
            for d in sorted(tb2):
                tab.append({"aria": ta, "variante": rv, "disp": d,
                            "Pprec_mW": "%.1f" % (pa.get(d, 0) * 1e3), "Tjprec": "%.1f" % ta1[d],
                            "P_mW": "%.1f" % (pb.get(d, 0) * 1e3), "Tj": "%.1f" % tb2[d]})
            ic, vec, vbc = specchio(v2)
            tab.append({"aria": ta, "variante": rv, "disp": "SPECCHIO",
                        "Pprec_mW": "Ic=%.3fmA" % (ic * 1e3), "Tjprec": "Vec=%.3f" % vec,
                        "P_mW": "Vbc_int=%.3f A=%.3f" % (vbc, specchio_a(v2)), "Tj": "coda=%.3fmA" % (v2["@q106[ic]"] * 1e3)})
            for nome_d, testo in deck_prova(spec, cond, ta, inc_rel(nome), rv == "rame").items():
                lista.append(scrivi(os.path.join(LOTTO, "deck", spec, nome_d + ".cir"), testo))
        for ta in (27, 57):
            ic, vec, vbc = specchio(p1[ta])
            tab.append({"aria": ta, "variante": "uniforme", "disp": "SPECCHIO",
                        "Pprec_mW": "Ic=%.3fmA" % (ic * 1e3), "Tjprec": "Vec=%.3f" % vec,
                        "P_mW": "Vbc_int=%.3f A=%.3f" % (vbc, specchio_a(p1[ta])), "Tj": "coda=%.3fmA" % (p1[ta]["@q106[ic]"] * 1e3)})
        if not opz:
            for nome_d, testo in deck_prova(spec, "u27", 27, inc_rel(var), True).items():
                lista.append(scrivi(os.path.join(LOTTO, "deck", spec, nome_d + ".cir"), testo))
        os.makedirs(os.path.join(LOTTO, "tj"), exist_ok=True)
        with open(os.path.join(LOTTO, "tj", spec + ".csv"), "w", newline="") as fh:
            w = csv.DictWriter(fh, list(tab[0]))
            w.writeheader()
            w.writerows(tab)
        for r in tab:
            if r["disp"] in ("Q122", "Q125", "Q106", "QE1", "SPECCHIO"):
                print("%-22s %(aria)s %(variante)-8s %(disp)-8s %(Pprec_mW)s %(Tjprec)s %(P_mW)s %(Tj)s"
                      .replace("%-22s", spec[:22].ljust(22)) % r)
    p = os.path.join(LOTTO, "deck", "lista_%s.txt" % fase)
    scrivi(p, "\n".join(lista) + "\n")
    print("%d deck in %s" % (len(lista), p))


if __name__ == "__main__":
    main()
