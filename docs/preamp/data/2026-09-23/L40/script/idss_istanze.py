#!/usr/bin/env python3
"""L40 - ADR-031 «da riaprire se» e' scattato in L39: la dispersione del gruppo
B di I_DSS su V1 va rimisurata sul circuito corretto, blocco A e buffer
compresi. tb_idss_loop.cir la misura solo sul blocco B; qui le stesse varianti
`altermod` (a_come_e, b_min, b_tip, b_max: Vto -2,086 / -2,557 / -2,976 di
ADR-031) sui deck d'anello del blocco A e del buffer, col criterio di V1:
  blocco A: carichi 1 e 2, sorgente 1 mohm e 430 ohm, cablaggio <= 1 nF;
  buffer:   carico 10 k e 50 k, sonda al jack (pos 1), cavo 1 fF - 4,7 nF.
Il circuito e' quello del deck versionato fino a .control, byte per byte.

MODELLI ALTERATI (limitations #29): il modello alterato si chiama ancora
LSK489A. Ogni variante stampa showmod di JQ110A; la prima variante e' il
modello com'e' pubblicato e deve ridare le tabelle del deck versionato. Nel deck
del blocco A anche i due buffer (il .subckt) usano LSK489A: si alterano
insieme, come in un apparecchio montato con coppie dello stesso gruppo.

Uso: /usr/bin/python3 idss_istanze.py <fase>   -> <fase>/tb_idss_blockA.cir,
     <fase>/tb_idss_buffer.cir
"""
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
L40 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L40, *[".."] * 5))
TB = os.path.join(ROOT, "spice", "preamp", "tb")
VAR = [("a_come_e", None), ("b_min", "-2.086"), ("b_tip", "-2.557"), ("b_max", "-2.976")]


def testa(deck, nome, cosa):
    r = open(os.path.join(TB, deck + ".cir")).read().split("\n")
    r = r[:r.index(".control")]
    r[0] = ("%s.cir - L40: V1 del %s al variare di I_DSS nel gruppo B (ADR-031), "
            "altermod su LSK489A; circuito di %s.cir, generato da idss_istanze.py"
            % (nome, cosa, deck))
    r.insert(1, "* ATTENZIONE (limitations #29): nel .control il modello LSK489A e' "
                "alterato; il nome resta quello del costruttore.")
    return r


def varianti(corpo, csv, intest):
    c = [".control", "alter r109 = 1G", "set units = degrees",
         'echo "%s" > %s' % (intest, csv)]
    for lbl, vto in VAR:
        if vto:
            c.append("altermod lsk489a vto = %s" % vto)
        c += ['echo "=== variante %s ==="' % lbl,
              "showmod jq110a : vto beta lambda"]
        c += [x.replace("@LBL@", lbl) for x in corpo]
    return c + [".endc", ".end", ""]


def main():
    fase = sys.argv[1]
    d = os.path.join(L40, fase)
    os.makedirs(d, exist_ok=True)
    corpo_a = [
        "foreach ld 1 2",
        "  if $ld = 1",
        "    alter rseln1 = 1m", "    alter rseln2 = 1m",
        "    alter rselv1 = 1e12", "    alter rselv2 = 1e12",
        "  else",
        "    alter rseln1 = 1e12", "    alter rseln2 = 1e12",
        "    alter rselv1 = 1m", "    alter rselv2 = 1m",
        "  end",
        "  foreach rs 1m 430",
        "    alter rsrca = $rs",
        "    foreach cw 1f 47p 100p 220p 470p 1n",
        "      alter cwire = $cw",
        "      ac dec 100 1 100meg",
        "      let T = v(fb)/v(g2)", "      let Tdb = db(T)", "      let Tph = ph(T)",
        "      meas ac fcross when Tdb=0", "      meas ac pmarg find Tph when Tdb=0",
        "      meas ac tdc find Tdb at=10",
        '      echo "@LBL@,$ld,$rs,$cw,$&fcross,$&pmarg,$&tdc" >> tb_idss_blockA.csv',
        "      destroy all", "    end", "  end", "end"]
    open(os.path.join(d, "tb_idss_blockA.cir"), "w").write("\n".join(
        testa("tb_loop_blockA", "tb_idss_blockA", "blocco A")
        + varianti(corpo_a, "tb_idss_blockA.csv", "var,carico,rsrc,cwire,fcross_hz,pm_deg,tdb_10hz")))
    corpo_f = [
        "foreach rl 10k 50k",
        "  alter rld = $rl",
        "  foreach cw 1f 47p 100p 220p 470p 1n 1.5n 2.2n 2.7n 3.3n 4.7n",
        "    alter cpj = $cw", "    alter cpn = 1f",
        "    ac dec 100 1 100meg",
        "    let T = v(fb)/v(g2)", "    let Tdb = db(T)", "    let Tph = ph(T)",
        "    meas ac fcross when Tdb=0", "    meas ac pmarg find Tph when Tdb=0",
        "    meas ac tdc find Tdb at=10",
        '    echo "@LBL@,$rl,$cw,$&fcross,$&pmarg,$&tdc" >> tb_idss_buffer.csv',
        "    destroy all", "  end", "end"]
    open(os.path.join(d, "tb_idss_buffer.cir"), "w").write("\n".join(
        testa("tb_loop_bufferfissa", "tb_idss_buffer", "buffer delle fisse")
        + varianti(corpo_f, "tb_idss_buffer.csv", "var,rld,cprobe,fcross_hz,pm_deg,tdb_10hz")))
    print("scritti in", d)


if __name__ == "__main__":
    main()
