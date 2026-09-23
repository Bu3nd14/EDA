#!/usr/bin/env python3
"""L40, ESPLORAZIONE - nessun file di models/ ne' del sorgente cambia.

Perche' V1 e' caduto in L39? Per il blocco B a 0 dB (la cella peggiore di
ADR-024: sorgente 2,611 k, cavo al jack) si rimette UNA famiglia di modelli alla
volta al suo segnaposto di prima di L39 (spice/preamp/placeholder_devices.lib),
con gli stessi parametri ma sotto il NOME del costruttore, cosi' il blocco
generato non cambia di un byte. Il controllo e' la variante `tutti_segnaposto`:
deve ridare i 61,80 gradi di L39/prima/tb_loop (0db/1).

Famiglie (segnaposto -> nome usato dal blocco):
  jfet   LSK489X  -> LSK489A
  mmbt   NSS2N5551 -> MMBT5551, PSS2N5401 -> MMBT5401
  mje    NMJE15032 -> Qmje15032, PMJE15033 -> Qmje15033
  diodo  D1N4148  -> D1N914
Lo specchio (Q121A/B) NON e' una famiglia: gia' prima di L39 era l'LS350 del
costruttore (L39/prima/gain_block_flat_L29b2.inc); il PTHAT320 della libreria
dei segnaposto non era piu' usato dal blocco.

Non e' `altermod` (limitations #29): la sostituzione e' un .include diverso,
visibile nell'intestazione del deck; ogni deck stampa comunque `showmod` sui
dispositivi della famiglia e la corrente di riposo, e il guadagno d'anello a
10 Hz dice da solo quale VAF gira (~72 dB segnaposto, ~81 costruttore).

Scrive cause/modelli_segnaposto_<fam>.lib e cause/tb_loop_<variante>.cir.
Uso: /usr/bin/python3 separa_cause.py
"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
L40 = os.path.dirname(QUI)
ROOT = os.path.abspath(os.path.join(L40, *[".."] * 5))
SRC = os.path.join(ROOT, "spice", "preamp", "tb", "tb_loop.cir")
PH = os.path.join(ROOT, "spice", "preamp", "placeholder_devices.lib")
OUT = os.path.join(L40, "cause")

FAM = {
    "jfet": {"LSK489X": "LSK489A"},
    "mmbt": {"NSS2N5551": "MMBT5551", "PSS2N5401": "MMBT5401"},
    "mje": {"NMJE15032": "Qmje15032", "PMJE15033": "Qmje15033"},
    "diodo": {"D1N4148": "D1N914"},
}
# l'include del costruttore che ogni famiglia rimpiazza
INC = {
    "jfet": ["models/jfet/lsk489.lib"],
    "mmbt": ["models/bjt_npn/mmbt5551.lib", "models/bjt_pnp/mmbt5401.lib"],
    "mje": ["models/bjt_npn/mje15032.lib", "models/bjt_pnp/mje15033.lib"],
    "diodo": ["models/diodes/1n4148.lib"],
}
# un dispositivo del blocco per famiglia, per showmod
SONDA = {"jfet": "jq110a", "mmbt": "q127 q122",
         "mje": "q132 q133", "diodo": "d102"}
PAR = {"jfet": "vto beta lambda cgs cgd", "mmbt": "vaf cje cjc tf",
       "mje": "vaf cje cjc tf", "diodo": "is n cjo"}


def modelli(fam):
    """Il testo .model del segnaposto, rinominato col nome del costruttore."""
    testo = open(PH).read().split("\n")
    out, dentro = [], False
    for r in testo:
        m = re.match(r"\.model\s+(\S+)", r, re.I)
        if m:
            dentro = m.group(1) in FAM[fam]
            if dentro:
                r = r.replace(m.group(1), FAM[fam][m.group(1)], 1)
        elif not r.startswith("+"):
            dentro = False
        if dentro:
            out.append(r)
    assert len(out) >= len(FAM[fam]), (fam, out)
    return out


VARIANTI = [("tutti_costruttore", [])] + [("seg_" + f, [f]) for f in FAM] \
    + [("tutti_segnaposto", list(FAM))]


def main():
    righe = open(SRC).read().split("\n")
    testa = righe[:righe.index(".control")]
    os.makedirs(OUT, exist_ok=True)
    for f in FAM:
        p = os.path.join(OUT, "modelli_segnaposto_%s.lib" % f)
        open(p, "w").write("* L40: segnaposto di placeholder_devices.lib, rinominati "
                           "col nome del costruttore (separa_cause.py)\n"
                           + "\n".join(modelli(f)) + "\n")
    for nome, fams in VARIANTI:
        via = [i for f in fams for i in INC[f]]
        corpo = []
        for r in testa[1:]:
            m = re.match(r"\.include @REPO@/(\S+)", r)
            if m and m.group(1) in via:
                corpo.append("* L40: tolto, al suo posto il segnaposto -> " + r)
                continue
            corpo.append(r)
        extra = ["* L40: segnaposto sotto il nome del costruttore"] + [
            ".include @REPO@/docs/preamp/data/2026-09-23/L40/cause/modelli_segnaposto_%s.lib" % f
            for f in fams]
        tit = ("tb_loop_%s.cir - L40 ESPLORAZIONE: V1 blocco B 0 dB, famiglie al "
               "segnaposto: %s. Circuito di tb_loop.cir, generato da separa_cause.py"
               % (nome, ",".join(fams) or "nessuna"))
        ctl = [".control", "alter r109 = 1G", "set units = degrees",
               "alter rrg = 1G", "alter rrg10 = 1G", "alter rload = 100k"]
        for f in FAM:
            ctl.append("showmod %s : %s" % (SONDA[f].split()[0], PAR[f]))
            if len(SONDA[f].split()) > 1:
                ctl.append("showmod %s : %s" % (SONDA[f].split()[1], PAR[f]))
        ctl += ["op", "print @q132[ic] @q133[ic] @q122[ic] v(nx)-v(ny)", "destroy all",
                'echo "variante,rsrc,cprobe,fcross_hz,pm_deg,tdb_10hz" > tb_loop_%s.csv' % nome,
                "foreach rs 1m 2.611k", "  alter rsrcb = $rs",
                "  foreach cab 1f 470p 1n 1.5n 2.2n 2.7n 3.3n 4.7n",
                "    alter ccable = $cab", "    alter cnode = 1f",
                "    ac dec 100 1 100meg",
                "    let T = v(fb)/v(g2)", "    let Tdb = db(T)", "    let Tph = ph(T)",
                "    meas ac fcross when Tdb=0", "    meas ac pmarg find Tph when Tdb=0",
                "    meas ac tdc find Tdb at=10",
                '    echo "%s,$rs,$cab,$&fcross,$&pmarg,$&tdc" >> tb_loop_%s.csv' % (nome, nome),
                "    destroy all", "  end", "end", ".endc", ".end", ""]
        # gli .include extra prima di quello del blocco
        i = max(k for k, r in enumerate(corpo) if r.startswith(".include"))
        corpo = corpo[:i] + extra + corpo[i:]
        open(os.path.join(OUT, "tb_loop_%s.cir" % nome), "w").write(
            "\n".join([tit] + corpo + ctl))
    print("scritti", len(VARIANTI), "deck in", OUT)


if __name__ == "__main__":
    main()
