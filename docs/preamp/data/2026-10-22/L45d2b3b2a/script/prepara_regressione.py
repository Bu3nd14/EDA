#!/usr/bin/env python3
"""L45d2b3b2a: i 21 deck veloci (la regressione di L40, regressione.sh di L45d2b3b1) per una
variante del blocco. Solo stdlib, /usr/bin/python3 -I.

Uso: prepara_regressione.py <variante> [...]   -> regressione/deck_<v>/<tb>.cir

- I due include del blocco (gain_block.subckt, gain_block_flat.inc di spice/preamp/) puntati a
  varianti/<v>/. Un deck che non include il blocco si copia com'e' (e si dice).
- P7 (tb_mute_corto): il deck scrive la potenza di R123 e R126 come i^2 * 56 ohm (scritto a mano):
  il 56 si sostituisce col valore della variante. In piu', per ogni blocco, in
  tb_mute_corto_parti.csv: potenza media e massima di Q146, Q148, R123, R126 e di ogni parte che la
  variante aggiunge (lette da @<dev>[p], senza moltiplicatori). P7 di ADR-021: Tj <= 125 C a 60 C
  d'aria, le 0207 <= 0,25 W.
"""
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L, "..", "..", "..", "..", ".."))
REL = os.path.relpath(L, ROOT)
SP = os.path.join(ROOT, "spice", "preamp")
TB = ("tb_ac", "tb_bias_sweep", "tb_blockA_carichi", "tb_dc_headroom", "tb_e3_e5", "tb_e4_uscite",
      "tb_idss_loop", "tb_idss_op_noise", "tb_loop_blockA", "tb_loop_bufferfissa", "tb_loop",
      "tb_mute_corto", "tb_noise_breakdown", "tb_noise_vectors", "tb_op",
      "tb_switch_v2_counterfactual", "tb_switch_v2", "tb_trim", "tb_uscite_fisse", "tb_v3_overload",
      "tb_zout_psrr_noise")
BLK = ("a", "f1", "f2", "b")


def corpo(p):
    t = open(p).read().splitlines()
    i0 = next(i for i, r in enumerate(t) if r.startswith(".subckt GAINBLOCK"))
    i1 = next(i for i, r in enumerate(t) if r.startswith(".ends"))
    return {r.split()[0]: r.split() for r in t[i0 + 1:i1] if r.split() and not r.startswith("*")}


def valore(v):
    x = v.lower()
    for s, m in (("k", 1e3), ("meg", 1e6)):
        if x.endswith(s):
            return float(x[:-len(s)]) * m
    return float(x)


def p7(t, parti, var):
    for r in ("r123", "r126"):
        righe = re.findall(r"let x%s = @r\.x\w+\.%s\[i\] \* @r\.x\w+\.%s\[i\] \* 56\n" % (r[1:], r, r), t)
        if len(righe) != 4:
            sys.exit("RIFIUTATO: %s: %d righe x%s" % (var, len(righe), r[1:]))
        ohm = valore(parti[r.upper()][3])
        t = re.sub(r"(let x%s = @r\.x\w+\.%s\[i\] \* @r\.x\w+\.%s\[i\] \* )56\n" % (r[1:], r, r),
                   lambda m: m.group(1) + "%g\n" % ohm, t)
    oggi = corpo(os.path.join(SP, "gain_block.subckt"))
    nuove = sorted(k for k in parti if k not in oggi)
    guardate = ["Q146", "Q148", "R123", "R126"] + nuove
    vett = {b: ["@%s.x%s.%s[p]" % (k[0].lower(), b, k.lower()) for k in guardate] for b in BLK}
    save = "\n".join("save " + " ".join(vett[b]) for b in BLK)
    testa = 'echo "blk,modo_db,f_hz,vin_pk,k_att,caso,%s" > tb_mute_corto_parti.csv' % ",".join(
        "p_%s,pmax_%s" % (k.lower(), k.lower()) for k in guardate)
    mis = []
    for b in BLK:
        eco = []
        for k, x in zip(guardate, vett[b]):
            mis += ["  meas tran pp_%s AVG %s from=4m to=8m" % (k.lower(), x),
                    "  meas tran px_%s MAX %s from=4m to=8m" % (k.lower(), x)]
            eco.append("$&pp_%s,$&px_%s" % (k.lower(), k.lower()))
        mis.append('  echo "%s,$gm,$f,$a,$k,$c,%s" >> tb_mute_corto_parti.csv' % (b.upper(), ",".join(eco)))
    ancora = "  * --- blocco A ---"
    if t.count(ancora) != 1:
        sys.exit("RIFIUTATO: %s: ancora del blocco A %d volte" % (var, t.count(ancora)))
    t = t.replace(ancora, "\n".join(mis) + "\n" + ancora)
    a2 = "\nforeach sweep 1 2 3\n"
    if t.count(a2) != 1:
        sys.exit("RIFIUTATO: %s: foreach sweep %d volte" % (var, t.count(a2)))
    return t.replace(a2, "\n" + save + "\n" + testa + "\n" + a2.lstrip("\n"))


def main(varianti):
    for v in varianti:
        d = os.path.join(L, "varianti", v)
        parti = corpo(os.path.join(d, "gain_block.subckt"))
        senza = []
        for k in TB:
            t = open(os.path.join(SP, "tb", k + ".cir")).read()
            n = 0
            for f in ("gain_block.subckt", "gain_block_flat.inc"):
                a = "@REPO@/spice/preamp/%s" % f
                n += t.count(a)
                t = t.replace(a, "@REPO@/%s/varianti/%s/%s" % (REL, v, f))
            if not n:
                senza.append(k)
            if any("spice/preamp/gain_block" in r for r in t.splitlines() if not r.lstrip().startswith("*")):
                sys.exit("RIFIUTATO: %s/%s include ancora il blocco di spice/preamp" % (v, k))
            if k == "tb_mute_corto":
                t = p7(t, parti, v)
            p = os.path.join(L, "regressione", "deck_" + v, k + ".cir")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(t)
        print("%s: %d deck%s" % (v, len(TB), (", senza il blocco: " + " ".join(senza)) if senza else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
