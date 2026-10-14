#!/usr/bin/env python3
"""A readable A4 summary of L45d1's synthesis for the user: the decisions L45d2 must take, how many
rows each covers, then the rows decision by decision. Reads fmea_sintesi.csv. Solo stdlib.
Written after L45d1 at the user's request («mi serve un pdf leggibile»), versioned as the
intermediate step L45d2 refers to (scelte_L45d2.pdf).

    pdf_scelte.py <fmea_sintesi.csv> <out.html>
    stampa_pdf.sh <out.html> <scelte_L45d2.pdf>          (Chrome headless, A4)

Every high or medium row belongs to exactly one decision (DECISIONI, by the start of its remedy
text); the script refuses a row that fits none, and checks the groups add up to the rows.
"""
import csv
import html
import sys

rs = list(csv.DictReader(open(sys.argv[1])))
am = [r for r in rs if r["priorita"] in ("alta", "media")]

# decision: (prefix of the remedy text, title, what to choose)
DECISIONI = [
    ("riv", ("un rivelatore di continua sulle uscite dei blocchi",),
     "Il rivelatore di continua sulle uscite dei blocchi",
     "Un guasto del blocco di guadagno porta il blocco al rail: ~14,9 V al jack (~137 dB SPL col "
     "contratto), sopra il tetto per 0,56–3,1 s. Con un rivelatore che apra il mute il tempo scende "
     "a 0,2–10,1 ms, dentro il criterio dei 100 ms; il picco non cambia. In 21 righe c'è anche un "
     "secondo guasto per calore."),
    ("aut", ("un autotest all'accensione",),
     "I sorveglianti dei rail ciechi",
     "Un comparatore del sorvegliante che non vede più il suo rail. Oggi il firmware fa da riserva e "
     "muta in 2,2 ms, fuori dalla sola clausola di 1 ms. Scelta: un autotest all'accensione, o "
     "accettare la riserva del firmware."),
    ("gre", ("accettarlo (al jack <= 9,0 mV)",),
     "I corti sul lato non regolato dei rail",
     "Un serbatoio o un diodo del ponte in corto: il sorvegliante muta, ma il rail scende sotto "
     "10,6 V prima che il jack si apra. Al jack al più 9,0 mV (~72 dB SPL). Sul rail negativo il "
     "regolatore resta con l'uscita fino a 1,76 V sopra l'ingresso, oltre il suo massimo assoluto."),
    ("cmd", ("limitare la corrente sul comando", "un limitatore sulla V5"),
     "I sovraccarichi del comando e la sovratensione della logica",
     "Un diodo di bloccaggio in corto mette ~1 A in un piccolo MOSFET; il regolatore della logica in "
     "corto porta 12 V al micro. Nessun colpo al jack: sono parti oltre i loro limiti."),
    ("mut", ("rivelare il mute che non si inserisce", "un contatto in serie che il guasto non salda"),
     "Il mute che non si inserisce",
     "Il transistor che comanda il mute in corto, o il contatto di un relè di mute saldato: niente al "
     "guasto, ma allo spegnimento o alla perdita di rete il jack resta collegato (fino a 3,6 V se poi "
     "si spegne un regolatore). Il LED rosso non lo vede."),
    ("iso", ("un rele' con isolamento rinforzato",),
     "L'isolamento fra bobina e contatti dei relè",
     "Se cede, i 12 V della bobina vanno sul segnale: sul relè di mute 12 V di continua sul jack per "
     "sempre, anche a mute inserito. Raro; vedi la domanda 1 sotto."),
    ("del", ("un controllo di Delta a ogni mute", "accettarlo come il corto della linea a 12 V"),
     "Il ritardo fra mute e permesso che si perde",
     "I relè di guadagno cadono fino a 4,3 ms prima che il jack si apra: 6,44 mV al jack (~70 dB "
     "SPL), lo stesso colpo già accettato per il corto della linea a 12 V. Due guasti lo fanno "
     "perdere a ogni mute, senza segno."),
    ("fil", ("far leggere al sorvegliante il rail dal lato della scheda audio",),
     "Il filo del rail fra le due schede",
     "Il filo del rail positivo che si apre: 13,3 V al jack e nessun mute, perché il sorvegliante "
     "legge il rail dal lato dell'alimentatore."),
    ("dop", ("un guasto doppio",),
     "Il condensatore d'uscita in corto",
     "Da solo un colpo piccolo (3–7 mV), ma l'uscita resta accoppiata in continua: un guasto del "
     "blocco dopo non decade più."),
    ("cal", ("il secondo guasto per calore",),
     "Il secondo guasto per calore, da solo",
     "Una riga del blocco che non supera il tetto ma porta una parte oltre i suoi limiti termici."),
    ("ver", ("il fusibile dimensionato", "da verificare col cablaggio di G2"),
     "Da verificare al pre-layout, niente da scegliere ora",
     "Il fusibile del trasformatore piccolo che non apre; il filo di massa fra le schede aperto (non "
     "simulabile sul banco)."),
    ("vbe", ("il moltiplicatore di Vbe",),
     "Il moltiplicatore di Vbe: già nella sua non conformità (NC-062)",
     "Porta in silenzio i transistor d'uscita fino a 183 °C, o le loro resistenze d'emettitore a "
     "7,5 W. Si decide col suo lotto, non qui."),
    ("nes", ("nessuno",),
     "Righe senza rimedio: dentro il criterio",
     "28 guasti del blocco dentro i 100 ms, che la tabella mette in media solo perché nessuno li "
     "nota (vedi la domanda 2), e 4 righe già accettate o già in sicurezza."),
]


def decisione(r):
    for k, pref, *_ in DECISIONI:
        if any(r["rimedi"].startswith(p) for p in pref):
            return k
    raise SystemExit("riga senza decisione: %s" % r["rimedi"][:60])


gruppi = {k: [] for k, *_ in DECISIONI}
for r in am:
    gruppi[decisione(r)].append(r)
assert sum(len(v) for v in gruppi.values()) == len(am)

LOTTO = {"L45a": "blocco", "L45b": "controlli", "L45c1": "rail", "L45c2": "comando"}
SCELTE = [k for k in gruppi if k not in ("ver", "vbe", "nes")]
n_scelta = sum(len(gruppi[k]) for k in SCELTE)


def e(s):
    return html.escape(str(s))


def effetto(r):
    out = []
    if r["picco_V"]:
        v = float(r["picco_V"])
        out.append(("%.3g V" % v if v >= 0.1 else "%.3g mV" % (v * 1e3) if v >= 1e-4 else "%.2g µV" % (v * 1e6)).replace(".", ",")
                   + (" · %s dB SPL" % r["picco_dB"].replace(".", ",") if r["picco_dB"] else ""))
    if r["sopra_ms"] and float(r["sopra_ms"]) > 0:
        t = float(r["sopra_ms"])
        out.append("sopra il tetto fino alla fine della corsa (≥ %.0f ms)" % t if t >= 1990 else
                   "sopra il tetto %s ms" % r["sopra_ms"].replace(".", ","))
    return "<br>".join(out) or "—"


h = []
h.append("""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Guasti: le scelte di L45d2</title>
<style>
@page { size: A4; margin: 16mm 14mm 16mm 14mm; }
body { font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #1a1a1a; line-height: 1.4; }
h1 { font-size: 19pt; margin: 0 0 4pt; }
h2 { font-size: 14pt; margin: 20pt 0 6pt; border-bottom: 1.5pt solid #333; padding-bottom: 2pt; page-break-after: avoid; }
h3 { font-size: 12pt; margin: 16pt 0 4pt; page-break-after: avoid; }
p { margin: 4pt 0 8pt; }
.sub { color: #555; font-size: 10pt; margin-bottom: 14pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9pt; }
th, td { border: 0.5pt solid #bbb; padding: 3pt 4pt; vertical-align: top; text-align: left; }
th { background: #eee; }
tr { page-break-inside: avoid; }
td.n, th.n { text-align: right; white-space: nowrap; }
.big td { font-size: 10pt; }
.alta { background: #fde2e1; } .media { background: #fff3cd; }
.box { border: 1pt solid #999; background: #f7f7f7; padding: 6pt 9pt; margin: 8pt 0; }
.small { font-size: 8.5pt; color: #444; }
.nuova { page-break-before: always; }
</style></head><body>""")

h.append("<h1>I guasti singoli del preamplificatore: che cosa resta da decidere</h1>")
h.append("<div class='sub'>Sintesi delle quattro analisi dei guasti (blocco di guadagno, controlli, rail audio, "
         "linea dei relè e comando), nella forma decisa il 14 ottobre: gravità, probabilità, quanto si nota, "
         "priorità, rimedi candidati. Fonte: <code>docs/preamp/data/2026-10-14/L45d1/fmea_sintesi.csv</code>. "
         "Ingresso della prossima sessione (L45d2). 14 ottobre 2026.</div>")

h.append("<h2>Quante righe dovremo affrontare</h2>")
tot = len(rs)
na = sum(1 for r in rs if r["priorita"] == "alta")
nm = sum(1 for r in rs if r["priorita"] == "media")
h.append("<p>Le quattro analisi hanno <b>%d modi di guasto</b>. A priorità bassa ce ne sono %d: non si "
         "affrontano uno per uno. Restano <b>%d righe</b>, %d ad alta priorità e %d a media.</p>"
         % (tot, tot - na - nm, len(am), na, nm))
h.append("<p>Molte righe hanno lo stesso rimedio, quindi <b>le %d righe diventano %d scelte</b> "
         "(%d righe). Altre %d righe non chiedono una scelta adesso: %d sono da verificare al "
         "pre-layout, %d appartengono al moltiplicatore di Vbe (già aperto per conto suo), %d non hanno "
         "rimedio.</p>"
         % (len(am), len(SCELTE), n_scelta, len(am) - n_scelta, len(gruppi["ver"]), len(gruppi["vbe"]),
            len(gruppi["nes"])))
h.append("<table class='big'><tr><th>#</th><th>Scelta</th><th class='n'>righe alte</th><th class='n'>medie</th><th>da</th></tr>")
for i, (k, _, tit, _) in enumerate(DECISIONI, 1):
    g = gruppi[k]
    a = sum(1 for r in g if r["priorita"] == "alta")
    lotti = ", ".join(LOTTO[l] for l in LOTTO if any(r["lotto"] == l for r in g))
    sep = " style='border-top:2pt solid #333'" if k == "ver" else ""
    h.append("<tr%s><td>%d</td><td>%s</td><td class='n'>%d</td><td class='n'>%d</td><td>%s</td></tr>"
             % (sep, i, e(tit), a, len(g) - a, e(lotti)))
h.append("<tr><th></th><th>totale</th><th class='n'>%d</th><th class='n'>%d</th><th></th></tr></table>" % (na, nm))
h.append("<p class='small'>Le scelte 1 e 8 (e la 9) potrebbero essere una sola: lo stesso rivelatore di continua sulle "
         "uscite coprirebbe anche il filo del rail che si apre e il condensatore d'uscita in corto. Fuori da "
         "queste righe, a priorità bassa, restano tre voci della lista: le sovratensioni dei rail che nessuno "
         "vede (9 righe), lo standby col trasformatore acceso (8) e il tetto delle uscite fisse, che non ha "
         "righe proprie.</p>")

h.append("<h2>Due domande prima delle scelte</h2>")
h.append("<div class='box'><b>1. L'isolamento dei relè di mute.</b> Se cede, sul jack restano 12 V di continua per "
         "sempre, anche a mute inserito. La tabella lo mette a priorità <b>media</b> solo perché è raro "
         "(meno di un guasto ogni miliardo di ore). Lo stesso guasto sui relè del selettore d'ingresso e del "
         "trim, che sono di più, esce ad <b>alta</b>. Li trattiamo insieme?</div>")
h.append("<div class='box'><b>2. I 28 guasti del blocco dentro il criterio.</b> Il colpo resta sotto il tetto, o "
         "lo supera per meno di 100 ms, e poi il blocco lavora degradato senza che nessuno lo noti. La tabella "
         "li mette a priorità <b>media</b> solo per questo. Nessuno ha un rimedio. Li accettiamo come sono?</div>")

h.append("<h2>Come leggere le tabelle</h2>")
h.append("<table class='big'><tr><th>Colonna</th><th>Che cosa vuol dire</th></tr>"
         "<tr><td><b>G</b>, gravità</td><td>1 niente di percepibile (≤ 33 dB SPL a 1 m); 2 una funzione persa, o un "
         "colpo ≤ 60 dB SPL; 3 un colpo udibile ma dentro il criterio (fino a ~112 dB SPL, o sopra per meno di "
         "100 ms); 4 il criterio non è rispettato: danno possibile alla catena a valle; 5 una parte oltre i suoi "
         "limiti</td></tr>"
         "<tr><td><b>P</b>, probabilità</td><td>dal tasso del guasto, in guasti per miliardo di ore: 1 meno di 1; "
         "2 da 1 a 10; 3 da 10 a 100; 4 oltre 100. Dieci per miliardo di ore è circa un apparecchio su 1100 in "
         "dieci anni sempre acceso. I tassi sono stime dichiarate (la tua scelta)</td></tr>"
         "<tr><td><b>N</b>, quanto si nota</td><td>1 il circuito lo vede e mette in sicurezza; 2 chi ascolta se ne "
         "accorge subito; 3 latente: non si vede finché non arriva un secondo evento</td></tr>"
         "<tr><td><b>Priorità</b></td><td>gravità 5: sempre alta. Gravità 4: alta, tranne se rara e visibile "
         "(media). Gravità 3: media se frequente o latente, altrimenti bassa. Gravità 1–2: bassa</td></tr>"
         "<tr><td><b>Effetto</b></td><td>il picco filtrato al jack peggiore, in volt e in dB SPL di picco a 1 m; "
         "«sopra il tetto» è il tempo sopra 0,87 V senza carico, che il criterio vuole entro 100 ms</td></tr>"
         "<tr><td><b>Dove</b></td><td>blocco = il blocco di guadagno; controlli = relè, commutatori, LED, "
         "condensatori del percorso; rail = l'alimentazione audio; comando = la linea dei relè, i sorveglianti, "
         "il temporizzatore</td></tr></table>")
for i, (k, _, tit, testo) in enumerate(DECISIONI, 1):
    g = gruppi[k]
    h.append("<h2%s>%d. %s</h2>" % (" class='nuova'" if i == 1 else "", i, e(tit)))
    h.append("<p>%s</p>" % e(testo))
    rim = list(dict.fromkeys(r["rimedi"] for r in g))
    h.append("<p class='small'><b>%s</b> (dalle tabelle): %s</p>" % (
        "Rimedio candidato" if len(rim) == 1 else "Rimedi candidati",
        "<br>— ".join([""] + [e(x) for x in rim])[5:] if len(rim) > 1 else e(rim[0])))
    h.append("<table><tr><th>Priorità</th><th>Dove</th><th>Parte</th><th>Guasto</th><th>Effetto al jack peggiore</th>"
             "<th class='n'>G</th><th class='n'>P</th><th class='n'>N</th><th class='n'>guasti per 10⁹ h</th></tr>")
    for r in g:
        h.append("<tr class='%s'><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                 "<td class='n'>%s</td><td class='n'>%s</td><td class='n'>%s</td><td class='n'>%s</td></tr>"
                 % (r["priorita"], r["priorita"], LOTTO[r["lotto"]], e(r["ref"]), e(r["modo"]), effetto(r),
                    r["G"], r["P"], r["R"], r["fit_modo"].replace(".", ",")))
    h.append("</table>")

h.append("</body></html>")
open(sys.argv[2], "w").write("\n".join(h))
print("righe alte+medie %d, scelte %d (%d righe), altre %d" % (len(am), len(SCELTE), n_scelta, len(am) - n_scelta))
for k, _, tit, _ in DECISIONI:
    print("  %3d  %s" % (len(gruppi[k]), tit))
