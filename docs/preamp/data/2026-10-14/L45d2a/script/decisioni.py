#!/usr/bin/env python3
"""L45d2a: the user's decisions on the remedies, row by row. Reads L45d1's fmea_sintesi.csv (does
not rewrite it) and writes decisioni.csv and decisioni.md: for every high or medium row the choice
number of scelte_L45d2.pdf, the decision, its ADR, where it is carried out, and the priority after
ADR-071. Also the low rows that ADR-078 decides (the rail overvoltages, the standby left on).
Solo stdlib.

    decisioni.py <fmea_sintesi.csv> <outdir>            write the two files
    decisioni.py <fmea_sintesi.csv> --prova             only the check against the PDF; exit 1 if off

The grouping is the one of L45d1/script/pdf_scelte.py (prefix of the remedy text, same order, so
the same numbers 1-13). Before deciding anything the script recounts the PDF's table: the counts
per choice must be the ones printed in scelte_L45d2.pdf, or it stops.
"""
import csv
import os
import sys

# (number in the PDF, key, prefixes of the remedy text) - from pdf_scelte.py, same order
GRUPPI = [
    (1, "riv", ("un rivelatore di continua sulle uscite dei blocchi",)),
    (2, "aut", ("un autotest all'accensione",)),
    (3, "gre", ("accettarlo (al jack <= 9,0 mV)",)),
    (4, "cmd", ("limitare la corrente sul comando", "un limitatore sulla V5")),
    (5, "mut", ("rivelare il mute che non si inserisce", "un contatto in serie che il guasto non salda")),
    (6, "iso", ("un rele' con isolamento rinforzato",)),
    (7, "del", ("un controllo di Delta a ogni mute", "accettarlo come il corto della linea a 12 V")),
    (8, "fil", ("far leggere al sorvegliante il rail dal lato della scheda audio",)),
    (9, "dop", ("un guasto doppio",)),
    (10, "cal", ("il secondo guasto per calore",)),
    (11, "ver", ("il fusibile dimensionato", "da verificare col cablaggio di G2")),
    (12, "vbe", ("il moltiplicatore di Vbe",)),
    (13, "nes", ("nessuno",)),
]

# the table of scelte_L45d2.pdf: number -> (high, medium)
PDF = {1: (52, 6), 2: (10, 0), 3: (9, 1), 4: (8, 0), 5: (8, 2), 6: (3, 4), 7: (0, 10), 8: (0, 2),
       9: (0, 2), 10: (1, 0), 11: (1, 1), 12: (4, 0), 13: (0, 32)}

# the low rows ADR-078 decides (prefix of the remedy text)
BASSE = [
    ("sov", "un sorvegliante della sovratensione dei rail",
     "prima leggere le tensioni massime delle parti del blocco e la dissipazione dei finali col rail "
     "alto; il sorvegliante della sovratensione solo se qualcosa esce dai limiti", "ADR-078", "L45d2b"),
    ("stb", "accettarlo (e' consumo, non colpo)",
     "il firmware legge la linea dei rele' e il trasformatore grande in standby", "ADR-078", "L58"),
]

RIV = ("il rivelatore di continua apre il mute, toglie la linea dei rele' alla scheda audio e spegne "
       "i rail audio")


def gruppo(r):
    for n, k, pref in GRUPPI:
        if any(r["rimedi"].startswith(p) for p in pref):
            return n, k
    raise SystemExit("riga senza scelta: %s %s %s" % (r["lotto"], r["ref"], r["rimedi"][:60]))


def decidi(n, k, r):
    """(decision, ADR, where, priority after ADR-071)"""
    pri = r["priorita"]
    if k == "riv":
        d = RIV
        if "secondo guasto per calore" in r["rimedi"]:
            d += "; col calore: i rail spenti tolgono anche il secondo guasto (scelta 10)"
        return d, "ADR-072", "L45d2b", pri
    if k == "aut":
        return ("accettata la riserva del firmware (muta in 2,2 ms invece di 1 ms)", "ADR-073",
                "accettata", pri)
    if k == "gre":
        return ("rivedere D510 / D511 e proteggere U502 dall'uscita sopra l'ingresso; il fusibile "
                "di rete resta a G2", "ADR-074", "L45d2b", pri)
    if k == "cmd":
        if r["rimedi"].startswith("un limitatore sulla V5"):
            return "un limitatore sulla linea a 5 V della logica", "ADR-075", "L45d2b", pri
        return "limitare la corrente sul comando", "ADR-075", "L45d2b", pri
    if k == "mut":
        return ("rivelato dal firmware (legge il comando del mute e stacca la linea dei rele' alla "
                "scheda audio)", "ADR-076", "L58", pri)
    if k == "iso":
        if r["lotto"] == "L45b" and r["ref"].startswith(("K2", "K3")):
            pri = "alta"            # ADR-071: i rele' di mute con selettore e trim
        return ("il rivelatore toglie la linea dei rele' alla scheda audio: la bobina non porta piu' "
                "12 V sul segnale", "ADR-072", "L45d2b", pri)
    if k == "del":
        return "accettato come il corto della linea a 12 V (ADR-051)", "ADR-077", "accettata", pri
    if k in ("fil", "dop"):
        return "coperto dal rivelatore di continua, da verificare", "ADR-072", "L45d2b", pri
    if k == "cal":
        return ("il rivelatore spegne i rail audio: il calore dura quanto il suo ritardo",
                "ADR-072", "L45d2b", pri)
    if k == "ver":
        return "niente da scegliere: si verifica al pre-layout", "", "G2", pri
    if k == "vbe":
        return "nel lotto del moltiplicatore di Vbe", "", "NC-062", pri
    if k == "nes":
        if r["lotto"] == "L45a":
            return ("accettato per il colpo (dentro i 100 ms); il degrado silenzioso va alla "
                    "diagnosi", "ADR-071", "L58", pri)
        return "invariato: " + r["rimedi"], "", "accettata", pri
    raise AssertionError(k)


def main():
    rs = list(csv.DictReader(open(sys.argv[1])))
    am = [r for r in rs if r["priorita"] in ("alta", "media")]

    # 1. the known case: the PDF's table
    conta = {n: [0, 0] for n in PDF}
    for r in am:
        n, _ = gruppo(r)
        conta[n][0 if r["priorita"] == "alta" else 1] += 1
    diverse = [(n, tuple(conta[n]), PDF[n]) for n in PDF if tuple(conta[n]) != PDF[n]]
    print("righe alte e medie: %d (PDF 156)" % len(am))
    for n in PDF:
        print("  scelta %2d: %2d alte, %2d medie (PDF %d / %d)" % (n, conta[n][0], conta[n][1], *PDF[n]))
    if diverse or len(am) != 156:
        print("DIVERSE dal PDF: %s" % diverse)
        sys.exit(1)
    if sys.argv[2] == "--prova":
        return

    out = []
    for r in am:
        n, k = gruppo(r)
        d, adr, dove, pri = decidi(n, k, r)
        out.append(dict(scelta=n, lotto=r["lotto"], ref=r["ref"], funzione=r["funzione"],
                        modo=r["modo"], G=r["G"], P=r["P"], R=r["R"], priorita=r["priorita"],
                        priorita_adr071=pri, decisione=d, adr=adr, dove=dove,
                        picco_V=r["picco_V"], picco_dB=r["picco_dB"], sopra_ms=r["sopra_ms"]))
    for key, pref, d, adr, dove in BASSE:
        for r in rs:
            if r["priorita"] == "bassa" and r["rimedi"].startswith(pref):
                out.append(dict(scelta="bassa", lotto=r["lotto"], ref=r["ref"], funzione=r["funzione"],
                                modo=r["modo"], G=r["G"], P=r["P"], R=r["R"], priorita=r["priorita"],
                                priorita_adr071=r["priorita"], decisione=d, adr=adr, dove=dove,
                                picco_V=r["picco_V"], picco_dB=r["picco_dB"], sopra_ms=r["sopra_ms"]))

    # 2. the checks on the decisions
    am2 = [o for o in out if o["scelta"] != "bassa"]
    na = sum(1 for o in am2 if o["priorita_adr071"] == "alta")
    nm = sum(1 for o in am2 if o["priorita_adr071"] == "media")
    alzate = [o for o in am2 if o["priorita_adr071"] != o["priorita"]]
    blocco_nes = [o for o in am2 if o["scelta"] == 13 and o["lotto"] == "L45a"]
    nsov = sum(1 for o in out if o["scelta"] == "bassa" and o["adr"] and o["dove"] == "L45d2b")
    nstb = sum(1 for o in out if o["scelta"] == "bassa" and o["dove"] == "L58")
    print("dopo ADR-071: %d alte, %d medie; %d righe alzate; %d guasti del blocco alla diagnosi"
          % (na, nm, len(alzate), len(blocco_nes)))
    print("basse decise da ADR-078: %d sovratensioni, %d standby" % (nsov, nstb))
    assert (na, nm, len(alzate), len(blocco_nes)) == (100, 56, 4, 28), "conteggi inattesi"
    assert all(o["dove"] for o in out)

    os.makedirs(sys.argv[2], exist_ok=True)
    campi = list(out[0])
    with open(os.path.join(sys.argv[2], "decisioni.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        w.writerows(out)

    # 3. the readable summary
    dove_tot = {}
    for o in am2:
        dove_tot[o["dove"]] = dove_tot.get(o["dove"], 0) + 1
    m = ["# Le decisioni sui rimedi, riga per riga (L45d2a)", "",
         "Dalla sintesi di L45d1 (`../L45d1/fmea_sintesi.csv`, non riscritta) e dalle scelte di "
         "`../L45d1/scelte_L45d2.pdf`, coi numeri del PDF. Generato da `script/decisioni.py`.", "",
         "**Righe alte e medie: 156.** Dopo ADR-071: **%d alte, %d medie** (i 4 modi d'isolamento "
         "dei relè di mute passano ad alta). I 28 guasti del blocco dentro il criterio vanno alla "
         "diagnosi." % (na, nm), "",
         "| Dove si realizza | righe |", "|---|---|"]
    for k in sorted(dove_tot):
        m.append("| %s | %d |" % (k, dove_tot[k]))
    m += ["", "| Scelta | Decisione | ADR | Dove | alte | medie (dopo ADR-071) |", "|---|---|---|---|---|---|"]
    for n, k, _ in GRUPPI:
        rr = [o for o in am2 if o["scelta"] == n]
        ds = sorted({(o["decisione"], o["adr"], o["dove"]) for o in rr})
        for i, (d, adr, dove) in enumerate(ds):
            sub = [o for o in rr if (o["decisione"], o["adr"], o["dove"]) == (d, adr, dove)]
            m.append("| %s | %s | %s | %s | %d | %d |" % (
                n if i == 0 else "", d.replace("|", "/"), adr or "—", dove,
                sum(1 for o in sub if o["priorita_adr071"] == "alta"),
                sum(1 for o in sub if o["priorita_adr071"] == "media")))
    m += ["", "Le righe a bassa priorità decise da ADR-078: %d sovratensioni dei rail (L45d2b, prima "
          "i massimi) e %d standby acceso per guasto (L58). Il dettaglio riga per riga è nel CSV."
          % (nsov, nstb), ""]
    open(os.path.join(sys.argv[2], "decisioni.md"), "w").write("\n".join(m))
    print("scritti decisioni.csv (%d righe) e decisioni.md" % len(out))


main()
