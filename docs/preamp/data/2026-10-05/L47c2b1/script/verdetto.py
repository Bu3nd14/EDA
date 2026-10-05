#!/usr/bin/env python3
"""L47c2b1: il verdetto di V2 da analisi.csv (v2_metodo.py analizza) e dal manifesto generato.
Copiato da data/2026-09-23/L29c/script/verdetto.py, con due cambi:
- S non c'e' piu' (ADR-062: il mute taglia);
- C2_ins / C2_rel (il clic del taglio) sono DICHIARATI: il peggiore sulle tre uscite si scrive,
  senza soglia ne' esito (ADR-062: l'utente non ha voluto un tetto). La tabella per uscita e
  tono la fa tabella_clic.py.
Verdetto: A e B2 <= 100 uV di picco (ADR-032); una A con finestra corta non accetta (v2_metodo).
CON LA MUSICA (ADR-063, scelta dell'utente: «Musica che passa davvero»): il residuo a mute
inserito si giudica su B2g (il jack grezzo nella finestra di B2) e su B1 del riferimento «sempre in
mute» della riga (rif_ins); B2 filtrato con la musica e' la coda del passa-alto dopo il taglio, e
si DICHIARA col clic.
Le corse di spegnimento (file off_*) sono escluse, come in L29d2 e L47b2b1: lo spegnimento vero e'
quello morbido dell'alimentatore (L30, L41c), e quelle sono diagnostica di L29c.

Uso: verdetto.py manifest.csv analisi.csv verdetto.csv
"""
import csv
import sys

man, ana, out = sys.argv[1:4]
SOGLIA = {"A_ins": 100e-6, "A_rel": 100e-6, "B2": 100e-6, "B2g": 100e-6, "B1": 100e-6}
DICHIARATE = ("C2_ins", "C2_rel", "B2_musica")
with open(man) as f:
    M = {r["cella"]: r for r in csv.DictReader(f)}
with open(ana) as f:
    AN = list(csv.DictReader(f))
peg = {}
mancanti = []
escluse = 0
for c, r in M.items():
    if r["file"].startswith("off_"):
        escluse += 1
        continue
    musica = float(r["amp"]) > 0
    conta = [x for x in r.get("conta", "").split(";") if x]
    if musica and "B2" in conta:
        if "B2g" not in conta:
            raise SystemExit("%s: riga con musica senza B2g (ADR-063): deck vecchio?" % c)
        # ADR-063: con la musica B2 filtrato va col clic; il verdetto e' B2g e B1 del «sempre»
        conta = [("B2_musica" if x == "B2" else x) for x in conta] + ["B1"]
    for g in conta:
        if g not in SOGLIA and g not in DICHIARATE:
            raise SystemExit("grandezza sconosciuta nel manifesto: %s (%s)" % (g, c))
        if g == "B1":
            sorgente = r["rif_ins"]
            vals = [a for a in AN if a["cella"] == sorgente and a["grandezza"] == "B1"]
        else:
            gg = "B2" if g == "B2_musica" else g
            vals = [a for a in AN if a["cella"] == c and a["grandezza"] == gg]
        if len(vals) != 3:
            mancanti.append("%s %s (%d uscite)" % (c, g, len(vals)))
            continue
        w = max(vals, key=lambda a: float(a["picco_V"]) if a["picco_V"] else float("inf"))
        esiti = {a["esito"] for a in vals}
        v = float(w["picco_V"]) if w["picco_V"] else None
        if g in DICHIARATE:
            soglia, esito = "-", "dichiarato"
        else:
            soglia = SOGLIA[g]
            ok = v is not None and v <= soglia and not any("non accetta" in e for e in esiti)
            esito = "regge" if ok else "NON REGGE"
        peg[(c, g)] = dict(cella=c, gruppo=r["gruppo"], variante=r["variante"], gm=r["gm"],
                           f_hz=r["f_hz"], amp=r["amp"], rl=r["rl"], grandezza=g, uscita=w["uscita"],
                           picco=w["picco_V"], t_picco=w["t_picco_s"], soglia=soglia,
                           esito=esito, esiti="|".join(sorted(esiti)))
with open(out, "w", newline="") as f:
    campi = ["cella", "gruppo", "variante", "gm", "f_hz", "amp", "rl", "grandezza", "uscita",
             "picco", "t_picco", "soglia", "esito", "esiti"]
    w = csv.DictWriter(f, campi)
    w.writeheader()
    w.writerows(peg.values())
print("%d righe -> %s (escluse %d celle di spegnimento off_*)" % (len(peg), out, escluse))
if mancanti:
    print("MANCANTI (%d): %s" % (len(mancanti), "; ".join(mancanti)))
per = {}
for p in peg.values():
    k = (p["gruppo"], p["grandezza"], "musica" if float(p["amp"]) > 0 else "senza segnale")
    if k not in per or float(p["picco"] or "inf") > float(per[k]["picco"] or "inf"):
        per[k] = p
for k in sorted(per):
    p = per[k]
    v = float(p["picco"]) * 1e6
    print("gruppo %s %-6s %-13s peggiore %10.3f uV  %-10s %s (%s, %s Hz, %s, %s)" % (
        k[0], k[1], k[2], v, p["esito"], p["cella"], p["uscita"], p["f_hz"], p["gm"], p["rl"]))
nr = [p for p in peg.values() if p["esito"] == "NON REGGE"]
nv = sum(1 for p in peg.values() if p["esito"] != "dichiarato")
print("NON REGGE: %d su %d verdetti" % (len(nr), nv))
for p in nr:
    print("   %s %s %s %s %s" % (p["cella"], p["grandezza"], p["uscita"], p["picco"], p["esiti"]))
sys.exit(1 if nr or mancanti else 0)
