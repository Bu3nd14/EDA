#!/usr/bin/env python3
"""Costruisce il dossier del preamplificatore dai dati versionati.

    /usr/bin/python3 docs/preamp/dossier/build_dossier.py
    /usr/bin/python3 docs/preamp/dossier/build_dossier.py --standalone <file.html>

REGOLA CHE GOVERNA QUESTO FILE, ed e' la stessa del diagramma a blocchi di
L1: **nessuna cifra del dossier e' scritta a mano.** Ogni numero che
compare nella pagina viene letto dai file versionati sotto docs/preamp/data/
e calcolato qui.

L42a: la scheda audio del progetto di oggi. I 21 deck veloci sono stati
ricorsi il 2026-09-27 sul `main` di L28 (modelli del costruttore, Miller
1 nF di ADR-042) in data/2026-09-27/L42/dopo/, curve comprese: L40 le aveva
tolte prima del commit. **Nessun dato viene da un giorno in cui il blocco
simulava i segnaposto** (fino al 2026-09-21, e le cartelle `prima` di L39 e
L40): un percorso di dati che ne contiene uno fa rifiutare il generatore.
Gli SCRIPT di quei lotti (headroom_nc009.py di L16; e4.py di L13, copiato in
L42/script/e4_l42.py senza i numeri noti dei segnaposto) restano la
seconda strada, lanciati sui dati di oggi: passano da tool(), non da src().

La Zout di L27 fu misurata con la sorgente AC accesa (NC-033, limitations
#28): la guardia di L37 resta, anche se la data la copre gia'.

Ogni numero passa per una seconda strada indipendente, e se le due divergono
oltre la tolleranza dichiarata lo script **rifiuta e non scrive niente**, come
export_fab.sh sulla DRC:
  1. le curve CSV contro le `print` che ngspice ha stampato nel .log;
  2. le tabelle scritte con `echo` contro le `print` o le `meas` dello stesso
     log, riga per riga; una cella vuota e' un rifiuto (docs/limitations.md #26);
  3. la cifra di headroom di NC-009 contro quella che stampa
     data/2026-09-14/L16/esplorazione/script/headroom_nc009.py sugli stessi CSV;
  4. (L42a; da L51a e' il punto 15) ogni riga di risultato dei log di oggi
     contro la corsa di un altro worktree sullo stesso circuito, e le tabelle
     byte per byte;
  5. (L42a; da L51a e' il punto 16, senza S) il mute: i verdetti della matrice
     ricalcolati da analisi.csv e dal manifesto, e le celle peggiori rifatte;
  6. (L42a) l'interblocco: la corsa di L36 ricontata da corsa.csv contro
     sintesi.txt; il 2e rieseguito sulla netlist di oggi; da L51a i falsi sono
     quelli di L48a e L48b (il 2e di oggi), non piu' quelli di L35 e L36;
  7. (L42a; in L51a esce dalla pagina, in L51b torna rifatto) il calore: il
     deck del calore rigenerato dal deck della rete di oggi e uguale a quello
     corso, stima_telaio_l51b.py rieseguito contro il suo .txt, il bilancio dei
     secondari che torna, la scheda audio contro tb_op e contro il banco.

L42b, riscritto in L51b: l'alimentatore, la seconda scheda. La prima strada
e' la ricorsa del 2026-10-09 col carico di oggi (data/2026-10-09/L51b: i rail
di tb_op di L51a, la bobina del selettore di L48a); la seconda, gli stessi
script col carico di prima (L51b-prima), che ridanno L47c2a e L47c2b2 byte per
byte. ps() rifiuta come prima strada ogni dato di prima del 2026-10-09; i lotti
si rileggono solo da vecchio(). Ogni log si legge prima dei suoi dati
(limitations #33-#36), e ogni deck rigenerato oggi da psu.net deve essere
quello corso, a meno dei percorsi del worktree.
  8. la potenza: i banchi rete e guasti, coi due carichi; R512 caso per caso
     (#34); col carico di prima analisi e deck di L47c2a, controfattuale col
     carico di L41a compreso; ogni scarto col carico di oggi si pubblica;
  9. il sorvegliante e i guasti (i nove casi di L41c, L47c2b2): il deck al
     punto fisso di ogni caso rigenerato da psu.net e dalle uscite del core;
     col carico di prima il testo dell'analisi, i deck, le uscite del core e
     i JSON del ponte di L47c2b2;
 10. il temporizzatore: analizza_timer.py rieseguito sui log dei due carichi,
     i deck rigenerati; col carico di prima il testo di L47c2a;
 11. il firmware (L47c2a): le sei sequenze come in 9, contro L47c2a; i falsi
     sull'host di oggi uguali a quelli di L47c2b2;
 12. (il pilota delle LDR: tolto con ADR-062)
 13. spegnimento e guasti al jack: tabella.py rieseguito, il deck di V2
     rigenerato dal sorgente di oggi e dal ponte, le 18 corse rc=0, i dB SPL
     ricalcolati con la catena di NC-028; scomposizione.csv (L47c2b2, la
     scheda di oggi col carico di prima, oggi) contro le tre tabelle; le
     soglie di P9 lette da REQUIREMENTS.md.

L42d: il contratto. La sezione 0 e' il PRB, l'appendice A il registro delle
ADR, l'appendice B l'indice dei requisiti tecnici, tutti letti dai loro file
(contratto.py); i rimandi PR-n, ADR-0xx, E1...V5 del testo diventano link, anche
nel PDF di stampa_a4.py.
 14. il contratto (contratto.py, docstring): le voci del PRB contigue, con
     «Dettagli» e al piu' tre righe; ogni requisito, ADR, NC e PR che nominano
     esiste; una ADR superata viaggia con chi la supera; le ADR in biiezione con
     l'indice, e lo Stato del file UGUALE a quello dell'indice (le due strade);
     nel testo, un rimando a qualcosa che non esiste e' un rifiuto, e un token
     che e' anche un non-requisito (T2 il trasformatore, V5 il rail) deve essere
     marcato con des() o rid(); ogni ancora ha il suo id.

L51a: la scheda audio rigenerata sul progetto di oggi (dopo L48b, c098be70:
circuito, deck e modelli fermi). Diviso dall'utente in tre parti, «Tre parti»:
L51a la scheda audio, L51b l'alimentatore e il firmware, L51c le schede di prova
e l'assieme di L49, «Cosa non dice» e le righe Stato restanti. Finche' le tre
non ci sono tutte, PARTI dice quali sezioni la pagina ha, e il generatore NON
scrive accanto a se' (index.html, figure, summary): solo --standalone fuori dal
repo, per chi rilegge. Nessun dato della scheda audio da prima di AUDIO_DA, il
giorno del circuito di oggi, se non per un'eccezione nominata in AUDIO_PERMESSI.
 15. (L51a) i 21 deck veloci, il selettore e le due copie col bilanciamento
     ricorsi il 2026-10-09 (L51a/dopo) contro la corsa di L48b sullo stesso
     circuito (L48a per il selettore): ogni riga di risultato dei log uguale,
     ogni tabella byte per byte;
 16. (L51a) il mute coi soli rele' (ADR-062, ADR-063): i verdetti della matrice
     di L48b ricalcolati da analisi.csv e dal manifesto con la regola di
     verdetto.py di L47c2b1 scritta di nuovo, contro verdetto.csv; le celle
     peggiori di ogni gruppo ricorse oggi sul deck versionato, riga per riga
     contro L48b; il deck rigenerato oggi dal sorgente uguale a quello versionato;
     il clic, colonna C2, contro le righe di analisi.csv;
 17. (L51a) il selettore (F1, ADR-064) e il volume col bilanciamento (ADR-065):
     le tabelle contro il log; gli scatti del volume di L48b, analizza.py
     rieseguito contro sintesi.txt; il 2e rieseguito sulla netlist di oggi
     riconosce selettore e volume.

L51c: le schede di prova di L49 e la chiusura; PARTI e' completa e il generatore scrive
accanto a se' (index.html, figure, schemi, immagini, summary). --standalone resta sempre
fuori dal repo. «Cosa questo dossier non dice» riscritta sul progetto di oggi.
 18. (L51c) la distorsione, V4, sul blocco di oggi: il blocco corso uguale a
     gain_block_flat.inc di oggi, i deck uguali a quelli di L46b a meno del blocco; la
     THD stampata da ngspice nel log contro il CSV di leggi_four.py, caso per caso; le 24
     righe contro la variante scelta di L46b (DIST_UGUALI alla cifra); i tetti letti dalla
     tabella di V4 in REQUIREMENTS.md;
 19. (L51c) le schede di prova: la DRC rifatta oggi contro quella del 9 ottobre (stessa
     scheda, stesso kicad-cli, stessi conteggi); measure.json, placement.json e
     assembly.json incrociati (la stessa misura di scheda, nessuna sovrapposizione, la sola
     variante A dell'assieme che ci sta); i vincoli letti dai report di L49 numerati 1..n;
     le immagini PNG che esistono; sc() rifiuta i dati di prima del giorno di L49.

E la provenienza dei modelli non e' scritta a mano: e' letta dagli `.include`
di ogni deck e dai nomi di modello che il blocco istanzia.

Non ha flag di bypass.
"""

import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATAROOT = os.path.join(REPO, "docs", "preamp", "data")
# L42a: lo script e4_l42.py (codice, non dati: passa da tool()). L51a: i dati di L42,
# L40, L29d2, L29e e L35 della scheda audio non si leggono piu' (il circuito di oggi e'
# quello di L48b); la corsa di L36 si', come eccezione dichiarata in AUDIO_PERMESSI.
L42S = os.path.join(DATAROOT, "2026-09-27", "L42", "script")
L36 = os.path.join(DATAROOT, "2026-09-25", "L36")
L30 = os.path.join(DATAROOT, "2026-09-26", "L30")
# Gli script dei lotti vecchi: codice, non dati. Passano da tool().
L16X = os.path.join(DATAROOT, "2026-09-14", "L16", "esplorazione")
TB = os.path.join(REPO, "spice", "preamp", "tb")
NET = os.path.join(REPO, "circuits", "preamp", "preamp_audio.net")
SCHEM = os.path.join(REPO, "docs", "preamp", "schematic")
# L32b: i due schemi si COPIANO accanto a index.html e si collegano da li'.
# Un <img src="../schematic/..."> esce dalla cartella della pagina, e un
# visualizzatore che serve solo quella cartella li perdeva in silenzio,
# mentre le figure fig_*.svg accanto alla pagina restavano visibili.
SCHEMATICS = ("gain_block.svg", "preamp_blocks.svg", "psu_blocks.svg")
# L42a: i giorni in cui il blocco simulava i segnaposto (L39 li ha sostituiti il
# 2026-09-22), e le cartelle `prima` di L39 e L40, corse sul blocco di prima.
FORBIDDEN = ("2026-09-09", "2026-09-10", "2026-09-13", "2026-09-14", "2026-09-15",
             "2026-09-16", "2026-09-21", os.path.join("L39", "prima"),
             os.path.join("L40", "prima"),
             # L42b: i banchi di L41a corsero sul psu.py di L41a, che L41b1 ha
             # riscritto (il temporizzatore, Q505, il pilota delle LDR). Entrano
             # solo come seconda strada, da vecchio(); la prima e' la ricorsa
             os.path.join("L41a", "rete"), os.path.join("L41a", "guasti"),
             os.path.join("L41a", "varianti"))
# L51b: l'alimentatore di oggi. Il circuito e' quello di L47c2a (psu.py non e' cambiato
# dopo), il carico della scheda audio quello di oggi: i rail di tb_op di L51a e la bobina
# del selettore di L48a (l'utente, 2026-10-09: «Tutto col selettore», «Sì, i rail di
# oggi»). La prima strada e' la ricorsa del 2026-10-09 col carico di oggi (L51b); la
# seconda, gli stessi script col carico di prima (L51b-prima), che ridanno L47c2a e
# L47c2b2 byte per byte. I dati di L41a-L41c, L42b e L30 non si leggono piu'.
# L64b: l'alimentatore di oggi e' quello di L58b (6a8e626: psu.py non e' cambiato dopo), col
# temporizzatore a comparatori al posto del micro e del firmware (ADR-102), la coppia Q501 + Q509
# (ADR-110), e il carico della scheda audio di oggi (tb_op di L64a). La prima strada e' la corsa del
# 2026-11-03 (L64b): i banchi della rete e dei guasti, le sequenze del temporizzatore, il calore, la
# catena al jack. La seconda: L58b sullo stesso circuito (le righe e i deck), L54b3b e L58b prima
# della coppia con la tolleranza della variante, L54b2 per la catena al jack, L51b per i banchi e il
# calore, tutti da vecchio(). L51b-prima, L47c2a e L47c2b2 (il firmware) non si leggono piu'.
L51B = os.path.join(DATAROOT, "2026-10-09", "L51b")
L64B = os.path.join(DATAROOT, "2026-11-03", "L64b")
L58B = os.path.join(DATAROOT, "2026-11-01", "L58b")
L54B3B = os.path.join(DATAROOT, "2026-10-28", "L54b3b")
L54B2 = os.path.join(DATAROOT, "2026-10-28", "L54b2")
PSU_NET = os.path.join(REPO, "circuits", "preamp", "psu.net")
# le opzioni del banco di oggi (le sequenze di L58b: il comparatore tarato, ADR-103; la ritenuta e i
# BAT54 del costruttore, ADR-104; i 2N7002 del datasheet; --tss 3.0, l'evento a 3 s)
PSU_OPZ = ("--timer", "sorgente", "--tss", "3.0", "--n2n7002", "ds", "--comparatore", "tarato",
           "--ritenuta", "costruttore", "--bat54", "costruttore")
# Il giorno dell'alimentatore di oggi: nessun dato della prima strada da prima. Le cartelle
# dei lotti che la seconda strada rilegge passano da vecchio().
PSU_DA = "2026-11-03"

# L51a: la scheda audio di oggi. Il circuito e' quello di L48b (c098be70): dopo,
# circuito, deck e modelli non sono cambiati. La prima strada e' la ricorsa del
# 2026-10-09; la seconda, la corsa di L48b (L48a per il selettore, che L48b non ha
# ricorso). Il mute, il volume e il bilanciamento si leggono dalle cartelle di L48b.
L51A = os.path.join(DATAROOT, "2026-10-09", "L51a")
L51 = os.path.join(L51A, "dopo")
L51M = os.path.join(L51A, "mute")
L48B = os.path.join(DATAROOT, "2026-10-07", "L48b")
L48BR = os.path.join(L48B, "regressione", "dopo")
L48A = os.path.join(DATAROOT, "2026-10-06", "L48a")
L47C2B1 = os.path.join(DATAROOT, "2026-10-05", "L47c2b1")
# L64a: la scheda audio di oggi, dopo L66 (ADR-111) e L67 (il circuito non cambia). La prima
# strada e' la ricorsa del 2026-11-02 (L64a/dopo); la seconda, le misure della regressione di
# L66 sulla variante lim365 (il sorgente di oggi: blocco uguale a meno dei commenti), il deck del
# mute di L66 ricorso (L64a/l66_mute), e per selettore e copie col bilanciamento gli stessi
# deck col blocco della variante di L66 (L64a/seconda). Il mute: la matrice di V2 intera
# ricorsa oggi (L64a/v2), contro L60d2. Il volume: gli scatti di L48b sul circuito di oggi
# (L64a/scatti). I falsi del 2e di L48a e L48b, ricorsi sulla netlist di oggi.
L64A = os.path.join(DATAROOT, "2026-11-02", "L64a")
L64D = os.path.join(L64A, "dopo")
L66 = os.path.join(DATAROOT, "2026-11-02", "L66")
L67 = os.path.join(DATAROOT, "2026-11-02", "L67")
L60D2 = os.path.join(DATAROOT, "2026-10-19", "L60d2")
# Il giorno del circuito di oggi: nessun dato della scheda audio da prima, tranne
# questi, ciascuno con la sua ragione.
AUDIO_DA = "2026-11-02"
AUDIO_PERMESSI = {
    # L64a: la ragione di L51a («gain_interlock.py non è cambiato dopo L35») era falsa: L41a
    # (ADR-048) ha portato le bobine a 12 V e la resistenza dei LED a 4,99 k. La corsa di L36 ha
    # bobine da 5 V (237 ohm); quello che prova e' di struttura: col polo ponte la bobina non
    # perde mai l'alimentazione, qualunque siano R e L, che la corsa spazza.
    os.path.join(L36, "corsa"): "la corsa al rilascio di L36 simula soli bobine e contatti; le "
                                "bobine erano da 5 V e oggi sono da 12 V (ADR-048), ma quello che "
                                "la corsa prova è di struttura: col polo ponte la bobina non perde "
                                "mai l’alimentazione, per ogni resistenza e induttanza spazzata",
    # L64a: il limitatore d'ingresso (ADR-101) non e' cambiato dopo «dopo L57b»
    # (circuits/preamp/input_limiter.py e il subckt: ultimo commit 539970c28)
    os.path.join(DATAROOT, "2026-10-25", "dopo-L57b"): "il limitatore d’ingresso (ADR-101) non è "
        "cambiato dopo; il suo costo in distorsione è misurato sul blocco di allora",
    # L64a: la Stax, i modi che il limitatore del VAS di ADR-111 non tocca; L66 ha ricorso quelli
    # che tocca, e i Q132 / Q133 ce ridanno L45d2b3b2b2 alla cifra
    os.path.join(DATAROOT, "2026-10-24", "L45d2b3b3"): "i guasti sulla Stax che il limitatore del "
        "VAS (ADR-111) non tocca; quelli che tocca li ha ricorsi L66",
}
# L51c: la distorsione del blocco di oggi (l'utente, 2026-10-10: «Rifarla e mostrarla»). La
# prima strada e' la corsa del 2026-10-10 col banco di L46b (genera.py, esegui.sh,
# leggi_four.py copiati in L51c/distorsione/script/) sulla variante `oggi`, il
# gain_block_flat.inc di oggi senza modifiche; la seconda, la variante scelta di L46b
# (sv_r10_esr0_r120_226: il blocco di ADR-056 col condensatore ideale, come nel sorgente).
L51C = os.path.join(DATAROOT, "2026-10-10", "L51c")
L51CD = os.path.join(L51C, "distorsione")
L46B = os.path.join(DATAROOT, "2026-10-01", "L46b")
L46B_VAR = "sv_r10_esr0_r120_226"
DIST_DECKS = ("thd_1k", "thd_10k", "thd_20k", "imd")
# Uguali alla cifra stampata: queste. Il pavimento numerico (pavimento_*) e le armoniche
# sotto ~-190 dB sono il fondo del metodo e cambiano col percorso di Newton: di quelle si
# controlla solo che restino sotto il tetto di V4.
DIST_UGUALI = ("vout_pk", "thd_pct", "h2_db", "h3_db", "imd_d2_db", "imd_d3_db")

# L51c: le schede di prova di L49 (L49a la scheda audio, L49b l'alimentatore e l'assieme).
# La DRC e' rifatta il 2026-10-10 sulle copie nei dati (l'utente: «Rifarlo oggi»), e deve
# dare quello che dava il 9 ottobre. Nessun dato delle schede da prima di SCHEDE_DA, il
# giorno di L49; non ci sono eccezioni.
L49A = os.path.join(DATAROOT, "2026-10-09", "L49a")
L49B = os.path.join(DATAROOT, "2026-10-09", "L49b")
SCHEDE_DA = "2026-10-09"
# le immagini della sezione (l'utente: «Essenziale»): copiate accanto a index.html con
# questi nomi, come gli schemi; nella pagina autoconsistente, incorporate
IMMAGINI = {
    "scheda_audio_3d.png": (L49A, "placement_3d_top.png"),
    "scheda_audio_rame.png": (L49A, "routing_both.png"),
    "alimentatore_3d.png": (L49B, "psu", "placement_3d_top.png"),
    "alimentatore_rame.png": (L49B, "psu", "routing_both.png"),
    "assieme.png": (L49B, "assembly", "assembly_A_tutto_sul_fondo.png"),
}

# Le parti della pagina: la scheda audio (L51a), l'alimentatore (L51b), le schede di prova
# (L51c). Con tutte e tre il generatore scrive accanto a se'.
# L64a: la prima delle tre parti di L64 (l'utente, 2026-11-02: «Three parts, like last time»);
# finche' non ci sono tutte, il generatore scrive solo --standalone fuori dal repo.
PARTI = ("audio", "alimentatore")
PARTI_TUTTE = ("audio", "alimentatore", "schede")

MODES = ("0db", "3db", "10db")
MLAB = {"0db": "0 dB", "3db": "+3 dB", "10db": "+10 dB"}
MNOM = {"0db": 0.0, "3db": 3.0, "10db": 10.0}

PM_MIN = 60.0          # V1, ADR-019
E5_MAX = 10.0          # µV, E5
E6 = 2.7               # V RMS, E6 (FiiO K11 a fondo scala)
TA = 60.0              # °C nel telaio, ADR-021
RTH_MJE = 62.5         # °C/W, RθJA MJE15032/33 TO-220 senza dissipatore, ADR-021
# L64a: da ADR-099 i finali hanno il dissipatore a clip Ohmite WA-T220-101E: 20 °C/W a 1 W
# (la cifra peggiore della curva del costruttore) + 2,5 °C/W giunzione-case + 2 °C/W
# d'interfaccia (ipotesi dichiarata in ADR-099) = 24,5 °C/W
RTH_MJE_DISS = 20.0 + 2.5 + 2.0
TJ_MAX = 125.0         # °C, P7

sys.path.insert(0, HERE)
import svgplot as sp                                   # noqa: E402
import contratto as ct                                 # noqa: E402  (L42d)

FAILURES = []


def refuse(msg):
    FAILURES.append(msg)


ct.init(REPO, refuse)
des = ct.des      # un non-requisito nel testo (T2, V5): il linker lo salta


def rel(p):
    return os.path.relpath(p, REPO)


def src(root, *parts):
    """Ogni percorso di dati passa di qui: il guardiano del lotto L32."""
    p = os.path.join(root, *parts)
    for bad in FORBIDDEN:
        if bad in p:
            raise SystemExit(f"RIFIUTATO: {rel(p)} viene da {bad}, dati corsi su un circuito "
                             "che non e' quello di oggi (i modelli segnaposto, il blocco di "
                             "prima di ADR-042, o il psu.py di L41a). "
                             "Nessun file e' stato scritto.")
    return p


_DATA_DAY = re.compile(r"(?:^|/)docs/preamp/data/(\d{4}-\d{2}-\d{2})/")


def sa(root, *parts):
    """Ogni percorso di dati della scheda audio passa di qui (L51a): src(), e in piu'
    niente da un giorno prima di AUDIO_DA, il circuito di oggi, se non nominato in
    AUDIO_PERMESSI con la sua ragione."""
    p = src(root, *parts)
    m = _DATA_DAY.search(rel(p))
    if m and m.group(1) < AUDIO_DA and not any(
            p == k or p.startswith(k + os.sep) for k in AUDIO_PERMESSI):
        raise SystemExit(f"RIFIUTATO: {rel(p)} e' del {m.group(1)}, prima del circuito di oggi "
                         f"({AUDIO_DA}, L66 e L67), e non e' fra le eccezioni dichiarate. "
                         "Nessun file e' stato scritto.")
    return p


def ps(root, *parts):
    """Ogni percorso di dati dell'alimentatore, prima strada, passa di qui (L51b): src(), e
    niente da un giorno prima di PSU_DA. Non ci sono eccezioni: la catena intera e' stata
    ricorsa oggi (l'utente: «Tutto col selettore»)."""
    p = src(root, *parts)
    m = _DATA_DAY.search(rel(p))
    if not m or m.group(1) < PSU_DA:
        raise SystemExit(f"RIFIUTATO: {rel(p)} non e' del {PSU_DA} o dopo, il giorno della "
                         "ricorsa dell'alimentatore col carico di oggi (L51b). Come seconda "
                         "strada passa da vecchio(). Nessun file e' stato scritto.")
    return p


def sc(root, *parts):
    """Ogni percorso di dati delle schede di prova passa di qui (L51c): src(), e niente da un
    giorno prima di SCHEDE_DA, il giorno di L49. Non ci sono eccezioni."""
    p = src(root, *parts)
    m = _DATA_DAY.search(rel(p))
    if not m or m.group(1) < SCHEDE_DA:
        raise SystemExit(f"RIFIUTATO: {rel(p)} non e' del {SCHEDE_DA} o dopo, il giorno delle "
                         "schede di prova (L49). Nessun file e' stato scritto.")
    if not os.path.exists(p):
        raise SystemExit(f"RIFIUTATO: manca {rel(p)}. Nessun file e' stato scritto.")
    return p


def tool(root, *parts):
    """Uno script di un lotto vecchio, usato come seconda strada sui dati di oggi.
    Non e' un dato: non passa dal guardiano, ma deve esistere."""
    p = os.path.join(root, *parts)
    if not os.path.isfile(p):
        raise SystemExit(f"RIFIUTATO: manca lo script {rel(p)}. Nessun file e' stato scritto.")
    return p


# L37 (NC-033): tb_zout_psrr_noise.cir fino a L13 misurava la Zout con VSRC a
# 1 V AC. I suoi CSV _zout_ di L27 contengono il segnale (limitations #28).
ZOUT_FORBIDDEN = os.path.join("2026-09-14", "L27")


def zout_src(root, *parts):
    """Ogni percorso di dati di E4 passa di qui: niente Zout di L27."""
    p = sa(root, *parts)
    if ZOUT_FORBIDDEN in p:
        raise SystemExit(f"RIFIUTATO: la Zout di {rel(p)} e' stata misurata con la sorgente "
                         "AC accesa (NC-033, #28). E4 si legge da data/2026-09-15/L13/. "
                         "Nessun file e' stato scritto.")
    return p


# ---------------------------------------------------------------- dati ----
def load_csv(path):
    """Legge un CSV di run_simulation.sh (intestazione col0..colN)."""
    rows = []
    with open(path) as f:
        head = f.readline()
        if not head.startswith("col0"):
            raise SystemExit(f"intestazione inattesa in {rel(path)}: {head!r}")
        for line in f:
            line = line.strip()
            if line:
                rows.append([float(v) for v in line.split(",")])
    if not rows:
        raise SystemExit(f"{rel(path)} e' vuoto")
    return rows


def load_table(path, nrows):
    """Legge una tabella scritta da `echo` (intestazione con nomi).

    Rifiuta le celle vuote: e' la forma in cui una `meas` fallita in silenzio
    arriva in tabella (docs/limitations.md #26). E rifiuta un numero di righe
    diverso da quello che i cicli del deck producono."""
    with open(path) as f:
        rows = list(csv.DictReader(f))
    empty = [(i, k) for i, r in enumerate(rows) for k, v in r.items()
             if v is None or v.strip() == ""]
    if empty:
        refuse(f"{rel(path)}: {len(empty)} celle vuote, la prima alla riga "
               f"{empty[0][0] + 2}, colonna {empty[0][1]} (#26)")
    if nrows is not None and len(rows) != nrows:
        refuse(f"{rel(path)}: attese {nrows} righe, trovate {len(rows)}")
    if not rows:
        refuse(f"{rel(path)}: tabella vuota")
    return rows


def num(r, k):
    try:
        return float(r[k])
    except (TypeError, ValueError, KeyError):
        return float("nan")


def pair(rows, k):
    """La k-esima coppia (scala, valore) -> (xs, ys)."""
    return [r[2 * k] for r in rows], [r[2 * k + 1] for r in rows]


def interp(xs, ys, x):
    """Interpolazione lineare in log(x), la griglia `dec` dei deck."""
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(1, len(xs)):
        if xs[i] >= x:
            x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
            if x1 == x0:
                return y0
            t = (math.log10(x) - math.log10(x0)) / (math.log10(x1) - math.log10(x0))
            return y0 + t * (y1 - y0)
    return ys[-1]


def crossing(xs, ys, level=0.0):
    """Primo attraversamento di `level` scendendo. Ritorna (x, indice)."""
    for i in range(1, len(ys)):
        if (ys[i - 1] - level) >= 0 >= (ys[i] - level):
            y0, y1 = ys[i - 1] - level, ys[i] - level
            if y1 == y0:
                return xs[i], i
            t = y0 / (y0 - y1)
            lx = math.log10(xs[i - 1]) + t * (math.log10(xs[i]) - math.log10(xs[i - 1]))
            return 10 ** lx, i
    return None, None


def log_print(path, key):
    """Le occorrenze di `key = valore` stampate da `print`, in ordine.

    ngspice stampa una `meas` incolonnata (`z1k                 =  5.87602e+01`)
    e una `print` compatta (`z1k = 5.876022e+01`): qui solo la seconda, che ha
    piu' cifre. Prenderle entrambe raddoppierebbe i conteggi."""
    pat = re.compile(r"^" + re.escape(key) + r" = (\S+)\s*$")
    return _grep(path, pat)


def log_meas(path, key):
    """Le occorrenze di una `meas` incolonnata, per i deck che non fanno
    `print` e scrivono la tabella direttamente da `$&var`."""
    pat = re.compile(r"^" + re.escape(key) + r"\s{2,}=\s+(\S+)")
    return _grep(path, pat)


_CUT = re.compile(r"^(\S+ = [-+0-9.eE]*)((?:Note|Warning): .*)$")
_TAIL = re.compile(r"^[-+0-9.eE]+$")
_SPLICED = {}


def log_lines(path):
    """Le righe del log, con le `print` spezzate ricucite.

    L42a (docs/limitations.md #37): ngspice scrive le Note/Warning del gmin
    stepping su stderr senza buffer e le `print` su stdout con buffer; nel .log
    unito una Note puo' cadere DENTRO una print. In tb_e4_uscite si legge
    `zn20k = 5Note: Starting dynamic gmin stepping`, poi le Note, poi
    `.720894e-01`. Si ricuce esattamente: il prefisso della riga tagliata piu'
    la prima riga fatta solo di cifre dopo le Note. Il conteggio delle
    ricuciture si pubblica."""
    out, pend = [], None
    with open(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if pend is not None:
                if _TAIL.match(line):
                    out.append(pend + line)
                    _SPLICED.setdefault(path, set()).add(len(out))
                    pend = None
                    continue
                if line.startswith(("Note: ", "Warning: ")):
                    continue
                refuse(f"{rel(path)}: una print spezzata da una Note non si ricuce "
                       f"({pend!r} seguita da {line[:40]!r})")
                pend = None
            m = _CUT.match(line)
            if m:
                pend = m.group(1)
                continue
            out.append(line)
    if pend is not None:
        refuse(f"{rel(path)}: una print spezzata da una Note resta aperta a fine log")
    return out


def _grep(path, pat):
    out = []
    for line in log_lines(path):
        m = pat.match(line)
        if m:
            try:
                out.append(float(m.group(1)))
            except ValueError:
                pass
    return out


def at(lst, i):
    return lst[i] if i < len(lst) else None


def check(label, mine, theirs, rtol):
    """Confronta il mio numero con quello di ngspice. Registra, non alza."""
    if theirs is None:
        refuse(f"{label}: ngspice non ha stampato il valore di riferimento")
        return mine
    if mine is None:
        refuse(f"{label}: il valore non si ricava dal CSV")
        return theirs
    den = abs(theirs) if abs(theirs) > 1e-12 else 1.0
    err = abs(mine - theirs) / den
    if not err <= rtol:
        refuse(f"{label}: calcolato {mine:.6g}, ngspice {theirs:.6g} "
               f"(scarto relativo {err:.2e} > {rtol:.0e})")
    return theirs        # si pubblica il numero del simulatore, non il mio


def cross_table(label, rows, col, logvals, rtol=1e-5):
    """Una colonna di tabella `echo` contro i valori del log, riga per riga.

    La tabella e il log vengono dalla stessa variabile, quindi il controllo non
    prova il simulatore: prova che la tabella sia intera, allineata e non
    sovrascritta (docs/limitations.md #25, #26)."""
    if len(rows) != len(logvals):
        refuse(f"{label}: {len(rows)} righe in tabella, {len(logvals)} valori nel log")
        return
    for i, (r, v) in enumerate(zip(rows, logvals)):
        t = num(r, col)
        den = abs(v) if abs(v) > 1e-12 else 1.0
        if not abs(t - v) / den <= rtol:
            refuse(f"{label}: riga {i + 2}, colonna {col}: tabella {r.get(col)!r}, "
                   f"log {v:.7g}")
            return


def capval(s):
    """'4.7n' -> 4.7e-9. Solo i suffissi che i deck usano."""
    return float(s[:-1]) * {"f": 1e-15, "p": 1e-12, "n": 1e-9}[s[-1]]


# ---------------------------------------------------------- formattazione --
def fmt(v, nd=3, unit=""):
    if v is None:
        return "&mdash;"
    if abs(v) >= 1000 or (abs(v) < 0.01 and v != 0):
        s = f"{v:.{nd}g}"
    else:
        s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
        if s in ("", "-"):
            s = "0"
    return f"{s}{unit}"


def it(v, nd=3, unit=""):
    """Numero con la virgola decimale italiana."""
    return fmt(v, nd, unit).replace(".", ",")


def fx(v, nd=2):
    """Decimali fissi, virgola italiana, meno tipografico."""
    return f"{v:.{nd}f}".replace(".", ",").replace("-", "&minus;")


def sg(v, nd=2):
    """Come fx, col segno sempre esplicito."""
    return f"{v:+.{nd}f}".replace(".", ",").replace("-", "&minus;")


def it_sci(v, nd=3):
    """Numero piccolo come m·10^e in HTML, con la virgola italiana."""
    if v == 0:
        return "0"
    e = math.floor(math.log10(abs(v)))
    m = f"{v / 10 ** e:.{nd - 1}f}".replace(".", ",").replace("-", "&minus;")
    return f'{m}&middot;10<sup>{str(e).replace("-", "&minus;")}</sup>'


def pct(v, nd=3, tetto=False):
    """Una percentuale piccola in notazione posizionale, nd cifre significative (L51c, V4)."""
    if v != v or v == 0:
        return "&mdash;" if v != v else "0"
    dec = max(0, nd - 1 - math.floor(math.log10(abs(v))))
    s = f"{v:.{dec}f}"
    if tetto and "." in s:          # un tetto si scrive com'e' nel requisito: 0,001, non 0,00100
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def lab_c(s):
    """'2.611k' -> '2,611 kΩ', '3.3n' -> '3,3 nF': etichette dei cicli dei deck."""
    s = s.strip()
    if s[-1] in "fpn":
        return s[:-1].replace(".", ",") + " " + s[-1] + "F"
    if s[-1] == "k":
        return s[:-1].replace(".", ",") + " kΩ"
    if s[-1] == "m":
        return s[:-1].replace(".", ",") + " mΩ"
    return s.replace(".", ",") + " Ω"


def verdict(ok, yes="conforme", no="non conforme"):
    return f'<td class="{"ok" if ok else "no"}">{yes if ok else no}</td>'


# ------------------------------------------------------------ provenienza --
# Il nome della parte per ciascun modello istanziato. Sono nomi, non numeri:
# cio' che il dossier AFFERMA - costruttore o segnaposto, e con quale KF -
# viene dai file, non da questa tabella.
# LSK489A (L20): the vendor model of models/jfet/lsk489.lib. Without this line a
# deck simulating it names a part "LSK489A" that no comment says, and the claims
# about "LSK489" read as claims about a part the deck does not simulate.
# L39 (NC-017): the manufacturer models the source instantiates since Fase 4.
# The part of MMBT5551/MMBT5401 is the MMBT, not the 2N (ADR-017); D1N914 is
# onsemi's model of the 1N4148 DO-35 (docs/limitations.md #20). The placeholder
# names stay: the dated decks under docs/preamp/data/ still simulate them.
PART = {"LSK489X": "LSK489", "LSK489A": "LSK489", "LS350": "LS352", "NSS2N5551": "2N5551",
        "PSS2N5401": "2N5401", "NMJE15032": "MJE15032", "PMJE15033": "MJE15033",
        "D1N4148": "1N4148",
        "MMBT5551": "MMBT5551", "MMBT5401": "MMBT5401", "QMJE15032": "MJE15032",
        "QMJE15033": "MJE15033", "D1N914": "1N4148"}
PLACEHOLDER_LIB = "spice/preamp/placeholder_devices.lib"


def _models_in(path):
    """{NOME: testo della .model, righe di continuazione comprese}.

    L51a: come ngspice, una riga di commento o vuota fra due righe di una .model
    non la chiude. L44 (ADR-057) ha messo il tetto del rumore 1/f in una riga «+»
    in coda al file, dopo il proprio commento: chiudendo la .model al commento,
    il dossier leggeva KF = 0 su MMBT5401, MMBT5551 e sui MJE, che il controllo
    [flicker] di validate_models.py rilegge a 1e-13 dal rumore."""
    out, cur = {}, None
    with open(path) as f:
        for ln in f:
            s = ln.strip()
            if s.lower().startswith(".model"):
                name = s.split()[1].split("(")[0].upper()
                out[name] = s
                cur = name
            elif s.startswith("+") and cur:
                out[cur] += " " + s[1:]
            elif s.startswith("*") or not s:
                continue
            else:
                cur = None
    return out


def _resolve_include(arg):
    if arg.startswith("@REPO@/"):
        return arg[len("@REPO@/"):]
    for root in ("spice/", "models/"):
        k = arg.find("/" + root)
        if os.path.isabs(arg) and k >= 0:
            return arg[k + 1:]
    return None


_PROV_CACHE = {}


def provenance(deckpath):
    """I modelli che un deck simula davvero, e da dove vengono.

    Legge gli `.include` del deck; i modelli definiti in ciascun file incluso;
    i nomi di modello istanziati (righe Q/J/D) dagli `.inc`/`.subckt` del
    blocco. Un modello e' «del costruttore» se sta in models/ con la sua
    .provenance.json, «segnaposto» se sta in placeholder_devices.lib. KF assente
    vale 0 in ngspice, e cosi' e' riportato."""
    if deckpath in _PROV_CACHE:
        return _PROV_CACHE[deckpath]
    incs = []
    with open(deckpath) as f:
        for ln in f:
            m = re.match(r"^\.include\s+(\S+)", ln.strip(), re.I)
            if m:
                r = _resolve_include(m.group(1))
                if r is None or not os.path.exists(os.path.join(REPO, r)):
                    refuse(f"provenienza {rel(deckpath)}: include non risolvibile {m.group(1)}")
                    continue
                incs.append(r)
    defined, used = {}, set()
    for inc in incs:
        p = os.path.join(REPO, inc)
        for name, text in _models_in(p).items():
            defined.setdefault(name, (inc, text))
        if inc.endswith((".inc", ".subckt")):
            with open(p) as f:
                for ln in f:
                    t = ln.split()
                    if t and t[0][0].upper() in "QJD" and len(t) >= 4:
                        used.add(t[-1].upper())
    out = []
    for name in sorted(used):
        if name not in defined:
            refuse(f"provenienza {rel(deckpath)}: il modello {name} non e' definito "
                   "da nessun file incluso")
            continue
        inc, text = defined[name]
        vendor = (inc.startswith("models/") and os.path.exists(
            os.path.join(REPO, os.path.splitext(inc)[0] + ".provenance.json")))
        placeholder = inc == PLACEHOLDER_LIB
        if not (vendor or placeholder):
            refuse(f"provenienza {rel(deckpath)}: {name} viene da {inc}, che non e' "
                   "ne' models/ con provenance ne' il file dei segnaposto")
            continue
        # L51a: un parametro ripetuto vale l'ULTIMO (ngspice; i MJE hanno KF=0 nella
        # riga del costruttore e il tetto di ADR-057 dopo)
        kfs = re.findall(r"\bKF\s*=\s*([0-9.eE+-]+)", text, re.I)
        out.append({"model": name, "part": PART.get(name, name), "file": inc,
                    "vendor": vendor, "kf": float(kfs[-1]) if kfs else 0.0})
    if not out:
        refuse(f"provenienza {rel(deckpath)}: nessun modello istanziato trovato")
    _PROV_CACHE[deckpath] = out
    return out


def prov_line(deck, datadir, deckdir=TB, note=""):
    ms = provenance(os.path.join(deckdir, deck))
    ven = sorted({m["part"] for m in ms if m["vendor"]})
    ph = sorted({m["part"] for m in ms if not m["vendor"]})
    return (f'<p class="prov">Deck <code>{html_escape(rel(os.path.join(deckdir, deck)))}</code>'
            f' &middot; dati <code>{html_escape(rel(datadir))}/</code>{note}<br>'
            f'Modelli del costruttore: <strong>{", ".join(ven) or "nessuno"}</strong>'
            f' &middot; segnaposto scritti a mano: <strong>{", ".join(ph) or "nessuno"}</strong>'
            f' &middot; {kf_phrase(ms)}</p>')


# ADR-057 (L44): il tetto dichiarato del rumore 1/f dei bipolari, KF e AF. Il
# dossier lo riconosce nelle .model, non lo assume: un bipolare con un KF diverso
# e' detto col suo numero.
KF_TETTO = 1e-13


def kf_phrase(ms):
    """Chi porta il rumore 1/f, letto dalle .model (L51a: da L44 tutti i bipolari al
    tetto di ADR-057; l'LSK489 col KF del costruttore)."""
    with_kf = sorted({m["part"] for m in ms if m["kf"] != 0})
    tetto = sorted({m["part"] for m in ms if m["kf"] == KF_TETTO})
    senza = sorted({m["part"] for m in ms if m["kf"] == 0})
    if not with_kf:
        return "tutti KF = 0: nessun rumore 1/f"
    altri = [p for p in with_kf if p not in tetto]
    s = "rumore 1/f: "
    s += "; ".join(x for x in (
        f'<strong>{", ".join(altri)}</strong> col KF del costruttore' if altri else "",
        f'<strong>{", ".join(tetto)}</strong> al tetto di ADR-057' if tetto else "",
        f'KF = 0 su {", ".join(senza)}' if senza else "") if x)
    return s


# ------------------------------------------- seconda corsa: L48b -----
_RESULT = re.compile(r"^([A-Za-z_][\w().\[\]#-]*)\s*=\s+([-+0-9.eE]+)\s*$")


def _results(path):
    """Le righe di risultato di un log, nell'ordine: `print` compatte e `meas`
    incolonnate. Il resto (avanzamento, gmin stepping) dipende dai buffer."""
    out = []
    for line in log_lines(path):
        m = _RESULT.match(line)
        if m:
            try:
                out.append((m.group(1), float(m.group(2))))
            except ValueError:
                pass
    return out


# L64a: le misure dei log lette come le legge la regressione di L66 (misure() di
# data/2026-10-22/L45d2b3b1/script/misure_regressione.py, scritta di nuovo qui): le righe
# «nome = valore» con un nome a inizio riga, la k-esima ripetizione di un nome chiamata nome#k.
_MISURA = re.compile(r"^([A-Za-z_@][^\s=]*)\s+=\s+([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)", re.M)


def misure_log(path):
    out, visti = {}, {}
    with open(path, errors="replace") as f:
        for nome, val in _MISURA.findall(f.read()):
            k = visti.get(nome, 0)
            visti[nome] = k + 1
            out["%s#%d" % (nome, k) if k else nome] = float(val)
    return out


def _senza_commenti(path, swap=None):
    righe = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln in f:
            s = ln.rstrip("\n")
            if swap:
                s = s.replace(swap, "@REPO@/spice/preamp/")
            if s.strip() and not s.lstrip().startswith("*"):
                righe.append(re.sub(r"\s+;.*$", "", s))
    return righe


def seconda_strada():
    """L64a, la seconda strada dei deck della scheda audio, sul circuito di oggi.
      a. il blocco della variante lim365 di L66 (varianti/lim365/) uguale, a meno dei
         commenti, a spice/preamp/gain_block_flat.inc e gain_block.subckt di oggi; i deck
         di L66 (regressione/deck_lim365/) uguali a quelli di oggi a meno del percorso del
         blocco, dei commenti e delle righe save (tb_mute_corto: anche delle sue .meas ed echo
         delle potenze, che hanno gli stessi nomi di quelle di oggi);
      b. i 20 deck veloci tranne tb_mute_corto: ogni misura dei log di oggi, alla sesta cifra,
         uguale alla colonna lim365 di L66/regressione/misure_lim365.csv, e nessuna misura da
         una parte sola;
      c. tb_mute_corto: il deck di L66 ricorso oggi (L64a/l66_mute) ridà tutte le sue misure di
         misure_lim365.csv, e i suoi CSV versionati sono quelli di oggi (byte per byte; la
         tabella delle potenze riga per riga: L66 accoda una riga in piu' per caso);
      d. il selettore e le due copie col bilanciamento, gli stessi deck col blocco della
         variante di L66 (L64a/seconda): ogni riga di risultato dei log, ogni CSV byte per byte.
    """
    out = {"decks": [], "n_res": 0, "n_tab": 0, "senza": [], "n_mis": 0, "n_mute": 0}
    var = "@REPO@/docs/preamp/data/2026-11-02/L66/varianti/lim365/"
    for f in ("gain_block_flat.inc", "gain_block.subckt"):
        if (_senza_commenti(os.path.join(REPO, "spice", "preamp", f))
                != _senza_commenti(sa(L66, "varianti", "lim365", f))):
            refuse(f"il blocco della variante lim365 di L66 ({f}) non e' quello di oggi")
    d66 = sa(L66, "regressione", "deck_lim365")
    for d in sorted(os.listdir(d66)):
        oggi = _senza_commenti(os.path.join(TB, d))
        loro = _senza_commenti(os.path.join(d66, d), swap=var)
        manca = [x for x in oggi if x not in loro]
        extra = [x for x in loro if x not in oggi]
        ok_extra = all(x.startswith("save ") or (d == "tb_mute_corto.cir" and (
            x.lstrip().startswith(("meas tran pp_", "meas tran px_", "echo "))))
                       for x in extra)
        if manca or not ok_extra:
            refuse(f"{d}: il deck di oggi non e' quello della regressione di L66 "
                   f"({len(manca)} righe solo oggi)")
    ref = {}
    for r in _csv(sa(L66, "regressione", "misure_lim365.csv")):
        if r["lim365"] != "":
            ref.setdefault(r["deck"], {})[r["misura"]] = r["lim365"]
    for deck in sorted(ref):
        if deck == "tb_mute_corto":
            continue
        log = os.path.join(sa(L64D, deck), deck + ".log")
        m = misure_log(log)
        mine = {k: "%.6g" % v for k, v in m.items()}
        if set(mine) != set(ref[deck]):
            refuse(f"{deck}: misure solo oggi {len(set(mine) - set(ref[deck]))}, solo in L66 "
                   f"{len(set(ref[deck]) - set(mine))}")
        diverse = [k for k in ref[deck] if k in mine and mine[k] != ref[deck][k]]
        if diverse:
            k = diverse[0]
            refuse(f"{deck}: {len(diverse)} misure diverse da L66 alla sesta cifra, la prima "
                   f"{k} {mine[k]} contro {ref[deck][k]}")
        out["n_mis"] += len(ref[deck])
        out["decks"].append((deck, len(ref[deck]), 0, rel(os.path.join(L66, "regressione"))))
    # c. tb_mute_corto
    dm = sa(L64A, "l66_mute")
    m = misure_log(os.path.join(dm, "tb_mute_corto.log"))
    rm = ref.get("tb_mute_corto", {})
    if not rm or any("%.6g" % m.get(k, float("nan")) != v for k, v in rm.items()):
        refuse("tb_mute_corto: il deck di L66 ricorso oggi non ridà misure_lim365.csv")
    out["n_mute"] = len(rm)
    tabs = sorted(f for f in os.listdir(dm) if f.endswith(".csv"))
    for t_ in tabs:
        a_, b_ = os.path.join(L64D, "tb_mute_corto", t_), os.path.join(dm, t_)
        if t_ == "tb_mute_corto_parti.csv":
            with open(a_) as fa, open(b_) as fb:
                ra = fa.read().split("\n")
                rb = [r for r in fb.read().split("\n") if r.count(",") == ra[0].count(",")]
            # l'intestazione di L66 ha 14 colonne: rb sono le sole righe di dati a 24
            if not rb or ra[1:-1] != rb:
                refuse("tb_mute_corto_parti.csv: le righe di oggi non sono quelle di L66")
        else:
            stessi_byte(f"tb_mute_corto/{t_}", a_, b_)
    out["decks"].append(("tb_mute_corto", len(rm), len(tabs), rel(dm)))
    out["n_tab"] += len(tabs)
    # d. selettore e bilanciamento contro il blocco di L66
    coppie = [(os.path.join(L64D, "tb_f1_selettore"), sa(L64A, "seconda", "tb_f1_selettore"),
               "tb_f1_selettore")]
    for b_ in ("tb_e5_bilanciamento", "tb_loop_bilanciamento"):
        coppie.append((os.path.join(L64D, "bilanciamento", b_), sa(L64A, "seconda", b_), b_))
    for oggi, prima, b_ in coppie:
        if not os.path.isdir(oggi):
            refuse(f"{b_}: manca la corsa di oggi in {rel(oggi)}")
            continue
        x, y = _results(os.path.join(oggi, b_ + ".log")), _results(os.path.join(prima, b_ + ".log"))
        if x != y:
            refuse(f"{b_}: le righe di risultato di oggi e di {rel(prima)} non coincidono")
        tabs = sorted(f for f in os.listdir(prima) if f.endswith(".csv"))
        for t_ in tabs:
            stessi_byte(f"{b_}/{t_}", os.path.join(oggi, t_), os.path.join(prima, t_))
        out["n_res"] += len(x)
        out["n_tab"] += len(tabs)
        out["decks"].append((b_, len(x), len(tabs), rel(prima)))
    out["spliced"] = sum(len(v) for p_, v in _SPLICED.items() if p_.startswith(L64D))
    return out


# --------------------------------------------------------------- misure ---
RS_AC = ("1.5", "430", "2500", "10k")
AC_ORDER = [(m, r) for m in MODES for r in RS_AC]


def measure_response():
    """Risposta in frequenza, tb_ac di L27: 3 modi x 4 sorgenti."""
    d = sa(L64D, "tb_ac")
    log = os.path.join(d, "tb_ac.log")
    keys = {k: log_print(log, k) for k in ("g1k", "g20", "g20k", "g100k")}
    for nm, lst in keys.items():
        if len(lst) != len(AC_ORDER):
            refuse(f"tb_ac.log: attese {len(AC_ORDER)} occorrenze di {nm}, trovate {len(lst)}")
    out = {}
    for key in [(m, r) for m in MODES for r in ("1.5", "2500")]:
        idx = AC_ORDER.index(key)
        rows = load_csv(os.path.join(d, f"tb_ac_{key[0]}_{key[1]}.csv"))
        f, gdb = pair(rows, 0)
        tag = f"tb_ac {key[0]}/{key[1]}"
        out[key] = {"f": f, "gdb": gdb}
        for k, fr in (("g20", 20), ("g1k", 1000), ("g20k", 20000), ("g100k", 100000)):
            out[key][k] = check(f"{tag} @{fr} Hz", interp(f, gdb, fr),
                                at(keys[k], idx), 2e-3)
    rows = load_csv(os.path.join(d, "tb_ac.csv"))
    f, gdb = pair(rows, 0)
    out["lf"] = {"f": f, "gdb": gdb}
    for k, lk, fr in (("g1k", "g1kb", 1000), ("g20", "g20b", 20), ("g5", "g5b", 5)):
        out["lf"][k] = check(f"tb_ac LF @{fr} Hz", interp(f, gdb, fr),
                             at(log_print(log, lk), 0), 2e-3)
    return out


def adr014(resp):
    """NC-007: `shape` e' la claim di ADR-014 (20 kHz riferito a 1 kHz, sorgente
    2500 contro 1,5 ohm); `level` e' lo scarto assoluto, cioe' il partitore fra
    la sorgente e la Zin."""
    shape, level = {}, {}
    for m in MODES:
        hi, lo = resp[(m, "2500")], resp[(m, "1.5")]
        shape[m] = (hi["g20k"] - hi["g1k"]) - (lo["g20k"] - lo["g1k"])
        level[m] = {f: hi[f] - lo[f] for f in ("g1k", "g20k")}
    return shape, level


def _loop_table(d, name, nrows, logname):
    tab = load_table(os.path.join(d, name), nrows)
    log = os.path.join(d, logname)
    for col, key in (("fcross_hz", "fcross"), ("pm_deg", "pmarg"), ("tdb_10hz", "tdc")):
        cross_table(f"{rel(os.path.join(d, name))} [{col}]", tab, col, log_print(log, key))
    return tab


def pm(r):
    return num(r, "pm_deg")


def measure_v1():
    """V1 come la vuole ADR-024: sonda al jack, minimo della spazzata fino a
    4,7 nF; blocco A col cablaggio <= 1 nF."""
    v = {}
    # --- blocco B, col trim (L16): sorgenti fino a (10 k + 442)/4 = 2,611 k
    d = sa(L64D, "tb_loop")
    tab = _loop_table(d, "tb_loop_margini.csv", 660, "tb_loop.log")
    v["B_dir"] = d
    B = {}
    for m in MODES:
        jack = [r for r in tab if r["mode"] == m and r["pos"] == "1"]
        node = [r for r in tab if r["mode"] == m and r["pos"] == "2"]
        w = min(jack, key=pm)
        wn = min(node, key=pm)
        same = lambda r: r["rsrc"] == w["rsrc"] and r["rload"] == w["rload"]  # noqa: E731
        curve = sorted([r for r in jack if same(r)], key=lambda r: capval(r["cprobe"]))
        curve_n = sorted([r for r in node if same(r)], key=lambda r: capval(r["cprobe"]))
        at47 = [r for r in curve if r["cprobe"] == "4.7n"]
        B[m] = {"min": pm(w), "w": w, "node_min": pm(wn), "wn": wn, "n": len(jack),
                "curve": ([capval(r["cprobe"]) for r in curve], [pm(r) for r in curve]),
                "curve_n": ([capval(r["cprobe"]) for r in curve_n], [pm(r) for r in curve_n]),
                "at47": pm(at47[0]) if at47 else None}
    v["B"] = B

    # --- Bode: il deck scrive le curve alla sorgente di 2,5 k e carico 100 k
    # (L42a: la stessa scelta di L27, che le aveva sole; ora le righe a 2,5 k
    # stanno nella tabella di 660 insieme alle sorgenti del trim).
    bode = {}
    for m in MODES:
        cand = [r for r in tab if r["mode"] == m and r["pos"] == "1"
                and r["rsrc"] == "2.5k" and r["rload"] == "100k"]
        w = min(cand, key=pm)
        rows = load_csv(os.path.join(d, f"tb_loop_att2k5_{m}_{w['cprobe']}.csv"))
        f, tdb = pair(rows, 0)
        _, tph = pair(rows, 1)
        fc, _ = crossing(f, tdb, 0.0)
        # G2 e' l'ingresso INVERTENTE: il margine e' |fase| dove |T| = 0 dB.
        pmv = abs(interp(f, tph, fc)) if fc else None
        bode[m] = {"f": f, "tdb": tdb, "tph": tph, "C": w["cprobe"],
                   "fcross": check(f"Bode {m} {w['cprobe']} f_incrocio", fc,
                                   num(w, "fcross_hz"), 5e-3),
                   "pmarg": check(f"Bode {m} {w['cprobe']} margine", pmv,
                                  abs(pm(w)), 5e-3),
                   "tdc": check(f"Bode {m} {w['cprobe']} |T| a 10 Hz",
                                interp(f, tdb, 10), num(w, "tdb_10hz"), 2e-3)}
    v["bode"] = bode
    v["bode_dir"] = d

    # --- blocco A (L16): senza trim e col partitore, scala 2 (845/464/464)
    d = sa(L64D, "tb_loop_blockA")
    base = load_table(os.path.join(d, "tb_loop_blockA.csv"), 32)
    trim = load_table(os.path.join(d, "tb_loop_blockA_trim.csv"), 96)
    log = os.path.join(d, "tb_loop_blockA.log")
    for col, k in (("fcross_hz", "fcross"), ("pm_deg", "pmarg"), ("tdb_10hz", "tdc")):
        cross_table(f"tb_loop_blockA + _trim [{col}]", base + trim, col, log_print(log, k))
    A = {"notrim": min([r for r in base if r["carico"] == "1"
                        and capval(r["cwire"]) <= 1e-9], key=pm)}
    for pos in ("0", "6", "12"):
        A[pos] = min([r for r in trim if r["cand"] == "2" and r["pos"] == pos
                      and capval(r["cwire"]) <= 1e-9], key=pm)
        A[pos + "_all"] = min([r for r in trim if r["cand"] == "2" and r["pos"] == pos],
                              key=pm)
    v["A"] = A
    v["A_dir"] = d

    # --- buffer delle fisse (L27)
    d = sa(L64D, "tb_loop_bufferfissa")
    tab = _loop_table(d, "tb_loop_bufferfissa.csv", 44, "tb_loop_bufferfissa.log")
    v["F"] = min([r for r in tab if r["pos"] == "1"], key=pm)
    v["Fn"] = min([r for r in tab if r["pos"] == "2"], key=pm)
    v["F_dir"] = d
    # L42a: gli spigoli di tolleranza (toll_L16) erano un deck d'esplorazione
    # sui segnaposto e non sono stati rifatti coi modelli del costruttore. Non
    # si leggono: la pagina lo dice in «Cosa questo dossier non dice».

    inst = [(f"Blocco B &middot; {MLAB[m]}", B[m]["min"]) for m in MODES]
    inst += [(f"Blocco A &middot; trim {t}", pm(A[p]))
             for p, t in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB"))]
    inst += [("Buffer delle fisse", pm(v["F"]))]
    v["inst"] = inst
    v["min"] = min(x for _, x in inst)
    v["min_where"] = min(inst, key=lambda t: t[1])[0]
    return v


def count_errors(path):
    """Righe `Error` di un log: ngspice esce 0 anche con quelle (#26)."""
    with open(path) as f:
        return sum(1 for ln in f if "Error" in ln)


# L37, la firma di #28. La sezione Zout inietta 1 A AC; VSRC, se resta accesa,
# vale 1 V AC. Il segnale aggiunge allora al nodo OUT circa G_lin x (1 V / 1 A):
# 1,0355 Ω a 0 dB nei dati di L27, contro 0,0386 Ω veri. NON si riconosce dal
# fatto che "scala col guadagno": la Zout vera del blocco scala anch'essa col
# guadagno del modo (il guadagno d'anello cala), 0,0387 Ω x G_lin in tutti e tre
# i modi. Si riconosce dalla grandezza.
ZSIG_FRAC = 0.5


def measure_zout(resp):
    """Le curve di Zout: tb_zout_psrr_noise corretto in L13 (sorgente spenta)."""
    d = zout_src(L64D, "tb_zout_psrr_noise")
    log = os.path.join(d, "tb_zout_psrr_noise.log")
    n_err = count_errors(log)
    if n_err:
        refuse(f"{rel(log)}: {n_err} righe 'Error' (#26)")
    keys = ("z20", "z1k", "z20k", "za20", "za1k", "za20k", "za100k")
    lv = {k: log_print(log, k) for k in keys}
    for k in keys:
        if len(lv[k]) != 3:
            refuse(f"tb_zout_psrr_noise.log: attese 3 occorrenze di {k}, trovate {len(lv[k])}")
    out = {"dir": d}
    for idx, m in enumerate(MODES):
        rows = load_csv(os.path.join(d, f"tb_zout_psrr_noise_zout_{m}.csv"))
        f, z = pair(rows, 0)
        _, za = pair(rows, 1)
        r = {"f": f, "z": z, "za": za, "z100k": interp(f, z, 100000)}
        for k, fr in (("20", 20), ("1k", 1000), ("20k", 20000)):
            r["z" + k] = check(f"Zout {m} @{fr} Hz", interp(f, z, fr), at(lv["z" + k], idx), 2e-3)
            r["za" + k] = check(f"Zout(OUT) {m} @{fr} Hz", interp(f, za, fr),
                                at(lv["za" + k], idx), 2e-3)
        r["za100k"] = check(f"Zout(OUT) {m} @100 kHz", interp(f, za, 100000),
                            at(lv["za100k"], idx), 2e-3)
        r["glin"] = 10 ** (resp[(m, "1.5")]["g1k"] / 20)
        if not r["za1k"] < ZSIG_FRAC * r["glin"]:
            refuse(f"Zout(OUT) {m} @1 kHz: {r['za1k']:.5g} Ω non sta sotto {ZSIG_FRAC} x G_lin "
                   f"= {ZSIG_FRAC * r['glin']:.5g} Ω: la Zout al nodo contiene il segnale del "
                   "modo, sorgente AC accesa durante l'iniezione (NC-033, #28)")
        out[m] = r
    return out


E4_OUTS = ("main", "fix1", "fix2")
E4_COLS = ("zrmax", "zr20", "zr1k", "zr20k", "zm20", "zm1k", "zn1k", "zn20k")
E4_MAX = 100.0         # Ω, E4
E4_COSTANZA = 1.0      # Ω, lettura di L13 (e4.py): E4 non da' tolleranza


def _markers(log, pat):
    return [m.groups() for m in (re.match(pat, ln) for ln in log_lines(log)) if m]


def measure_e4(z):
    """E4 sulle tre uscite e a manopola che gira: tb_e4_uscite di L13."""
    d = zout_src(L64D, "tb_e4_uscite")
    log = os.path.join(d, "tb_e4_uscite.log")
    n_err = count_errors(log)
    if n_err:
        refuse(f"{rel(log)}: {n_err} righe 'Error' (#26)")
    tab = load_table(os.path.join(d, "tb_e4_uscite_tab.csv"), 135)
    gain = load_table(os.path.join(d, "tb_e4_uscite_guadagno.csv"), 45)

    # le righe delle tabelle nell'ordine dei marcatori del log, poi colonna per colonna
    for label, rows, cols, pat in (
            ("tb_e4_uscite_tab.csv", tab, ("out", "trim", "att", "mode"),
             r"^CELL out=(\w+) trim=(\d+) att=(\d+) mode=(\w+)$"),
            ("tb_e4_uscite_guadagno.csv", gain, ("trim", "att", "mode"),
             r"^GAIN trim=(\d+) att=(\d+) mode=(\w+)$")):
        mine = [tuple(r.get(c) for c in cols) for r in rows]
        theirs = _markers(log, pat)
        if mine != theirs:
            i = next((i for i, (a, b) in enumerate(zip(mine, theirs)) if a != b),
                     min(len(mine), len(theirs)))
            refuse(f"{label}: l'ordine delle righe non e' quello del log dalla riga {i + 2} "
                   f"({len(mine)} righe, {len(theirs)} marcatori)")
    for c in E4_COLS:
        cross_table(f"tb_e4_uscite_tab.csv [{c}]", tab, c, log_print(log, c))
    cross_table("tb_e4_uscite_guadagno.csv [g1k_db]", gain, "g1k_db", log_print(log, "g1k"))

    out = {"dir": d, "groups": []}
    for o, ms in [("main", (m,)) for m in MODES] + [(o, MODES) for o in ("fix1", "fix2")]:
        sel = [r for r in tab if r.get("out") == o and r.get("mode") in ms]
        if not sel:
            refuse(f"tb_e4_uscite_tab.csv: nessuna riga per {o} {'+'.join(ms)}")
            continue
        g = {"out": o, "modes": ms, "n": len(sel)}
        for c in ("zrmax", "zr1k", "zm1k", "zn1k"):
            vs = [num(r, c) for r in sel]
            g[c + "_min"], g[c + "_max"] = min(vs), max(vs)
            g[c + "_disp"] = max(vs) - min(vs)
        g["disp"] = max(g[c + "_disp"] for c in ("zrmax", "zr1k", "zm1k"))
        out["groups"].append(g)

    # stessa grandezza da due deck diversi: il flat corretto e la catena in subckt
    for m in MODES:
        for r in tab:
            if r.get("out") != "main" or r.get("mode") != m:
                continue
            bad = [(zk, tk) for zk, tk in (("za1k", "zn1k"), ("z1k", "zm1k"))
                   if not abs(z[m][zk] - num(r, tk)) <= 1e-3 * abs(num(r, tk))]
            if bad:
                zk, tk = bad[0]
                refuse(f"Zout {m}: tb_zout_psrr_noise {zk} {z[m][zk]:.6g} Ω, tb_e4_uscite main "
                       f"trim {r['trim']} att {r['att']} {tk} {num(r, tk):.6g} Ω "
                       "(scarto > 1e-3): i due deck non misurano la stessa impedenza")
                break

    # la stessa cifra dal verificatore di L13, sugli stessi file
    script = tool(L42S, "e4_l42.py")
    proc = subprocess.run([sys.executable, script, d], capture_output=True, text=True)
    if proc.returncode != 0:
        tail = " | ".join(proc.stdout.strip().splitlines()[-3:])
        refuse(f"e4.py esce {proc.returncode}: {tail[-300:]}")
        return out
    got = {}
    for ln in proc.stdout.splitlines():
        t = ln.replace("..", " ").split()
        if len(t) == 11 and t[0] in E4_OUTS:
            got[(t[0], t[1])] = [float(x) for x in t[2:]]
    for g in out["groups"]:
        key = (g["out"], "+".join(g["modes"]))
        if key not in got:
            refuse(f"e4.py: manca la riga {' '.join(key)}")
            continue
        n, zrmax, r1a, r1b, m1a, m1b, na, nb, dsp = got[key]
        mine = (g["n"], g["zrmax_max"], g["zr1k_min"], g["zr1k_max"], g["zm1k_min"],
                g["zm1k_max"], g["zn1k_min"], g["zn1k_max"], g["zrmax_disp"])
        # lo script stampa 4 decimali, 5 al nodo, 3 cifre per la dispersione
        tol = (0, 5.1e-5, 5.1e-5, 5.1e-5, 5.1e-5, 5.1e-5, 5.1e-6, 5.1e-6, 5.1e-8 + 5e-4 * dsp)
        for name, a, b, tl in zip(("celle", "Re(Z)max", "Re(Z)1k min", "Re(Z)1k max",
                                   "|Z|1k min", "|Z|1k max", "nodo min", "nodo max",
                                   "dispersione Re(Z)max"),
                                  mine, (n, zrmax, r1a, r1b, m1a, m1b, na, nb, dsp), tol):
            if not abs(a - b) <= tl:
                refuse(f"E4 {' '.join(key)} {name}: dossier {a:.6g}, e4.py {b:.6g}")
    out["script"] = rel(script)
    return out


PSRR_ORDER = [("p", m) for m in MODES] + [("m", m) for m in MODES]


def measure_psrr():
    d = sa(L64D, "tb_zout_psrr_noise")
    log = os.path.join(d, "tb_zout_psrr_noise.log")
    keys = ("p100", "p1k", "p10k", "p100k")
    lv = {k: log_print(log, k) for k in keys}
    for k in keys:
        if len(lv[k]) != len(PSRR_ORDER):
            refuse(f"tb_zout_psrr_noise.log: attese 6 occorrenze di {k}, trovate {len(lv[k])}")
    out = {}
    for idx, (rail, m) in enumerate(PSRR_ORDER):
        rows = load_csv(os.path.join(d, f"tb_zout_psrr_noise_psrr{rail}_{m}.csv"))
        f, p = pair(rows, 0)
        tag = f"PSRR{'+' if rail == 'p' else '-'} {m}"
        r = {"f": f, "p": p}
        for k, fr in (("p100", 100), ("p1k", 1000), ("p10k", 10000), ("p100k", 100000)):
            r[k] = check(f"{tag} @{fr} Hz", interp(f, p, fr), at(lv[k], idx), 2e-3)
        out[(rail, m)] = r
    return out


def integrate_noise(f, s):
    """sqrt(integrale di s(f)^2 df), trapezi sulla griglia del deck."""
    tot = 0.0
    for i in range(1, len(f)):
        tot += 0.5 * (s[i] ** 2 + s[i - 1] ** 2) * (f[i] - f[i - 1])
    return math.sqrt(tot)


def measure_noise():
    """E5 del blocco: spettri integrati contro `onoise_total` stampato."""
    out = {}
    d = sa(L64D, "tb_zout_psrr_noise")
    tot = log_print(os.path.join(d, "tb_zout_psrr_noise.log"), "onoise_total")
    if len(tot) != 5:
        refuse(f"tb_zout_psrr_noise.log: attese 5 occorrenze di onoise_total, trovate {len(tot)}")
    zp = []
    for i, (fname, lab) in enumerate((
            ("tb_zout_psrr_noise_noise_0db.csv", "0 dB &middot; sorgente 430 Ω (phono)"),
            ("tb_zout_psrr_noise_noise_3db.csv", "+3 dB &middot; sorgente 430 Ω"),
            ("tb_zout_psrr_noise_noise_10db.csv", "+10 dB &middot; sorgente 430 Ω"),
            ("tb_zout_psrr_noise_noise_intrinsic.csv", "0 dB &middot; sorgente 1 Ω (intrinseco)"),
            ("tb_zout_psrr_noise.csv", "+10 dB &middot; sorgente 2500 Ω &mdash; caso peggiore"))):
        f, s = pair(load_csv(os.path.join(d, fname)), 0)
        val = check(f"E5 {fname}", integrate_noise(f, s), at(tot, i), 1e-2)
        zp.append((lab, val))
    out["zout"] = zp
    out["zout_dir"] = d

    d = sa(L64D, "tb_noise_breakdown")
    tot = log_print(os.path.join(d, "tb_noise_breakdown.log"), "onoise_total")
    if len(tot) != 5:
        refuse(f"tb_noise_breakdown.log: attese 5 occorrenze di onoise_total, trovate {len(tot)}")
    nb = []
    for i, (fname, lab) in enumerate((
            ("tb_noise_breakdown_a_0db_1r.csv", "A) 0 dB, sorgente 1 Ω &mdash; blocco A intrinseco"),
            ("tb_noise_breakdown_b_0db_430r.csv", "B) 0 dB, sorgente 430 Ω &mdash; blocco A sul phono"),
            ("tb_noise_breakdown_c_0db_2500r.csv", "C) 0 dB, sorgente 2500 Ω &mdash; blocco B"),
            ("tb_noise_breakdown_e_3db_2500r.csv", "E) +3 dB, sorgente 2500 Ω &mdash; blocco B"),
            ("tb_noise_breakdown_d_10db_2500r.csv", "D) +10 dB, sorgente 2500 Ω &mdash; blocco B, caso peggiore"))):
        # l'ordine delle print nel log e' A, B, C, D, E (foreach cfg 1..5)
        li = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}[fname.split("_")[3]]
        f, s = pair(load_csv(os.path.join(d, fname)), 0)
        nb.append((lab, check(f"E5 {fname}", integrate_noise(f, s), at(tot, li), 1e-2)))
    out["nb"] = nb
    out["nb_dir"] = d
    return out


def measure_trim():
    """ADR-027: attenuazione, E3 al connettore, E5 della catena (tb_trim di L16)."""
    d = sa(L64D, "tb_trim")
    log = os.path.join(d, "tb_trim.log")
    e3 = load_table(os.path.join(d, "tb_trim_e3.csv"), 24)
    for col, k in (("zmin_ohm", "zmin"), ("z20_ohm", "z20"), ("z1k_ohm", "z1k"),
                   ("z20k_ohm", "z20k"), ("att1k_db", "att1k")):
        cross_table(f"tb_trim_e3.csv [{col}]", e3, col, log_print(log, k))
    e5 = load_table(os.path.join(d, "tb_trim_e5.csv"), 96)
    cross_table("tb_trim_e5.csv [onoise_uv]", e5, "onoise_uv", log_print(log, "onu"))

    c2 = [r for r in e3 if r["cand"] == "2"]
    scale = "/".join(c2[0][k] for k in ("r1", "r2", "r3")) if c2 else "?"
    att = {}
    for pos in ("99", "0", "6", "12"):
        vals = [num(r, "att1k_db") for r in c2 if r["pos"] == pos]
        if not vals or max(vals) - min(vals) > 1e-6:
            refuse(f"tb_trim_e3: l'attenuazione della posizione {pos} dipende da CSEL")
        att[pos] = vals[0] if vals else float("nan")
    zmin = {(r["pos"], r["csel"]): num(r, "zmin_ohm") for r in c2}
    e3min = min(v for (p, _), v in zmin.items() if p in ("0", "6", "12"))
    e3min_cs = min(((p, c) for (p, c) in zmin if p in ("0", "6", "12")), key=lambda k: zmin[k])[1]

    c25 = [r for r in e5 if r["cand"] == "2"]
    e5w = {pos: max([r for r in c25 if r["pos"] == pos], key=lambda r: num(r, "onoise_uv"))
           for pos in ("99", "0", "6", "12")}
    e5max = max(num(e5w[p], "onoise_uv") for p in ("0", "6", "12"))
    return {"dir": d, "scale": scale, "att": att, "zmin": zmin, "e3min": e3min,
            "e3min_cs": e3min_cs, "e5w": e5w, "e5max": e5max}


def m1_window(vin, vout):
    """La finestra di M1, con lo stesso algoritmo di headroom_nc009.py:
    il guadagno locale entro l'1 % del valore a 0 V, bordi ai campioni."""
    n = len(vin)
    i0 = min(range(n), key=lambda i: abs(vin[i]))
    g = [(vout[i + 1] - vout[i - 1]) / (vin[i + 1] - vin[i - 1]) for i in range(1, n - 1)]
    g0 = g[i0 - 1]
    lo = hi = i0 - 1
    while lo - 1 >= 0 and abs(g[lo - 1] - g0) / abs(g0) <= 0.01:
        lo -= 1
    while hi + 1 < len(g) and abs(g[hi + 1] - g0) / abs(g0) <= 0.01:
        hi += 1
    return g0, vin[lo + 1], vin[hi + 1], vout[lo + 1], vout[hi + 1]


def db20(x):
    return 20 * math.log10(x)


def measure_headroom(trim):
    """NC-009, una cifra con la sua metrica (M1, scelta in L16).

    M1: limite lineare (uscita ai bordi della finestra all'1 %, bordo minore,
    come seno RMS) contro 2,7 V RMS x guadagno misurato x attenuazione del
    trim misurata. M2 (ADR-015) e M3 (dossier fino a L32) sono etichettate."""
    d = sa(L64D, "tb_dc_headroom")
    names = {"0db": "tb_dc_headroom.csv", "3db": "tb_dc_headroom_3db.csv",
             "10db": "tb_dc_headroom_10db.csv"}
    att = {"0": 0.0, "6": trim["att"]["6"], "12": trim["att"]["12"]}
    out = {"dir": d, "att": att, "modes": {}}
    for m in MODES:
        vin, vout = pair(load_csv(os.path.join(d, names[m])), 0)
        g0, vi_lo, vi_hi, vo_lo, vo_hi = m1_window(vin, vout)
        lin = min(abs(vo_lo), abs(vo_hi)) / math.sqrt(2)
        sat = min(abs(max(vout)), abs(min(vout))) / math.sqrt(2)
        r = {"vin": vin, "vout": vout, "gain": g0, "vi_lo": vi_lo, "vi_hi": vi_hi,
             "vo_lo": vo_lo, "vo_hi": vo_hi, "lin": lin, "sat": sat,
             "vout_max": max(vout), "vout_min": min(vout), "trim": {}}
        for tpos, tnom in (("0", 0), ("6", -6), ("12", -12)):
            req = E6 * abs(g0) * 10 ** (att[tpos] / 20)
            req_nom = E6 * 10 ** (MNOM[m] / 20) * 10 ** (tnom / 20)
            r["trim"][tpos] = {"req": req, "M1": db20(lin / req),
                               "M2": db20(sat / req_nom), "M3": db20(lin / req_nom)}
        out["modes"][m] = r

    # la stessa cifra dallo script di L16, sugli stessi CSV e le stesse attenuazioni
    script = tool(L16X, "script", "headroom_nc009.py")
    proc = subprocess.run([sys.executable, script] +
                          [os.path.join(d, names[m]) for m in MODES] +
                          [repr(att["6"]), repr(att["12"])],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        refuse(f"headroom_nc009.py esce {proc.returncode}: {proc.stderr.strip()[-200:]}")
        return out
    got, mode = {}, None
    mmap = {"0": "0db", "+3": "3db", "+10": "10db"}
    for ln in proc.stdout.splitlines():
        mm = re.match(r"^== modo (\S+) dB", ln)
        if mm:
            mode = mmap.get(mm.group(1))
            continue
        mt = re.match(r"^\s+trim\s+(-?\d+) dB .*M1 ([+-]\d+\.\d+) dB \| "
                      r"M2 ([+-]\d+\.\d+) dB \| M3 ([+-]\d+\.\d+) dB", ln)
        if mt and mode:
            got[(mode, mt.group(1).lstrip("-"))] = [float(mt.group(i)) for i in (2, 3, 4)]
    if len(got) != 9:
        refuse(f"headroom_nc009.py: attese 9 righe M1/M2/M3, lette {len(got)}")
    for (m, tpos), vals in got.items():
        mine = out["modes"][m]["trim"][tpos]
        for name, theirs in zip(("M1", "M2", "M3"), vals):
            # lo script stampa due decimali: lo scarto ammesso e' l'arrotondamento
            if not abs(mine[name] - theirs) <= 0.0051:
                refuse(f"NC-009 {m} trim -{tpos} dB {name}: dossier {mine[name]:+.4f} dB, "
                       f"headroom_nc009.py {theirs:+.2f} dB")
    out["script"] = rel(script)
    return out


def measure_counterfactual():
    """I tre stati del controfattuale di ADR-004. col1 = v(OUT), col3 = v(FB)."""
    d = sa(L64D, "tb_switch_v2_counterfactual")
    files = [("A", "contatto CHIUSO, R_f = 1,50 kΩ", "tb_switch_v2_counterfactual.csv"),
             ("B", "contatto APERTO, R_f = 1e12 Ω", "tb_switch_v2_counterfactual_open.csv"),
             ("C", "richiuso, controprova di B", "tb_switch_v2_counterfactual_reclosed.csv")]
    out = []
    for tag, desc, name in files:
        rows = load_csv(os.path.join(d, name))
        out.append({"tag": tag, "desc": desc, "vout": rows[0][1], "vfb": rows[0][3]})
    if abs(out[0]["vout"] - out[2]["vout"]) > 1e-6:
        refuse("controfattuale: A e C non coincidono, la controprova non regge")
    if abs(out[1]["vout"] - out[0]["vout"]) < 1.0:
        refuse("controfattuale: B non differisce da A, l'anello non si e' aperto")
    return {"dir": d, "rows": out}


V2_WINDOWS = [("regime_0db", "s0", "regime a 0 dB"), ("regime_3db", "s3", "regime a +3 dB"),
              ("regime_10db", "s10", "regime a +10 dB"),
              ("regime_10db_bis", "s10b", "regime a +10 dB, seconda volta"),
              ("trans_0_3", "t03", "0 &rarr; +3 dB (K1)"),
              ("trans_3_10", "t310", "+3 &rarr; +10 dB (K5)"),
              ("trans_10_3", "t103", "+10 &rarr; +3 dB (K5)"),
              ("trans_3_0", "t30", "+3 &rarr; 0 dB (K1)"),
              ("trans_0_10_k5_prima", "t010", "0 &rarr; +10 dB, K5 per primo"),
              ("trans_10_0_k1_prima", "t100", "+10 &rarr; 0 dB, K1 per primo")]


def measure_v2():
    """V2: le finestre di tb_switch_v2 contro l'inviluppo del regime a +10 dB."""
    d = sa(L64D, "tb_switch_v2")
    log = os.path.join(d, "tb_switch_v2.log")
    tab = load_table(os.path.join(d, "tb_switch_v2_finestre.csv"), len(V2_WINDOWS))
    rows = []
    for (fin, pre, lab), r in zip(V2_WINDOWS, tab):
        if r["finestra"] != fin:
            refuse(f"tb_switch_v2_finestre.csv: attesa la finestra {fin}, trovata {r['finestra']}")
        for col, suf in (("vmax", "max"), ("vmin", "min")):
            lv = log_meas(log, pre + suf)
            if len(lv) != 1:
                refuse(f"tb_switch_v2.log: attesa una meas {pre + suf}, trovate {len(lv)}")
            else:
                cross_table(f"tb_switch_v2_finestre.csv {fin} [{col}]", [r], col, lv)
        rows.append({"fin": fin, "lab": lab, "vmax": num(r, "vmax"), "vmin": num(r, "vmin")})
    reg = [x for x in rows if x["fin"].startswith("regime_10db")]
    env_hi = max(x["vmax"] for x in reg)
    env_lo = min(x["vmin"] for x in reg)
    tol = 1e-4       # V: le tabelle hanno sei cifre significative
    for x in rows:
        x["inside"] = x["vmax"] <= env_hi + tol and x["vmin"] >= env_lo - tol
    gmax, gmin = at(log_print(log, "vmax"), 0), at(log_print(log, "vmin"), 0)
    check("tb_switch_v2 estremo positivo su 70 ms", max(x["vmax"] for x in rows), gmax, 1e-4)
    check("tb_switch_v2 estremo negativo su 70 ms", min(x["vmin"] for x in rows), gmin, 1e-4)
    return {"dir": d, "rows": rows, "env_hi": env_hi, "env_lo": env_lo,
            "gmax": gmax, "gmin": gmin, "all_inside": all(x["inside"] for x in rows)}


def measure_v3():
    """V3, tb_v3_overload: v(SRCN), v(OUT), v(JACK), v(NX). Il deck non fa
    `print`: questi numeri hanno solo il CSV, e la pagina lo dice."""
    d = sa(L64D, "tb_v3_overload")
    rows = load_csv(os.path.join(d, "tb_v3_overload.csv"))
    vout = [r[3] for r in rows]
    return {"dir": d, "vmax": max(vout), "vmin": min(vout), "jack_end": rows[-1][5],
            "t_end": rows[-1][2], "n": len(rows)}


# ADR-023: i percorsi ascoltabili per caso, dall'intestazione di tb_mute_corto.cir.
LISTEN = {"0": {"A", "F1", "F2", "B"}, "1": set(), "2": {"A", "F2", "B"},
          "5": {"A", "F2", "B"}, "6": {"A", "F2", "B"}, "3": {"A", "F1", "B"},
          "4": {"A", "F1", "F2"}}


def measure_p7():
    """P7 (ADR-021): MJE peggiore per blocco e modo, Tj = 60 °C + P·RθJA."""
    d = sa(L64D, "tb_mute_corto")
    log = os.path.join(d, "tb_mute_corto.log")
    tab = load_table(os.path.join(d, "tb_mute_corto_regime.csv"), 600)
    cross_table("tb_mute_corto_regime.csv [p_q132]", tab, "p_q132", log_meas(log, "pq132"))
    cross_table("tb_mute_corto_regime.csv [p_q133]", tab, "p_q133", log_meas(log, "pq133"))
    worst = {}
    for blk in ("A", "F1", "F2", "B"):
        for m in ("0", "3", "10"):
            rows = [r for r in tab if r["blk"] == blk and r["modo_db"] == m]
            if not rows:
                refuse(f"tb_mute_corto: nessuna riga per {blk} a {m} dB")
                continue
            w = max(rows, key=lambda r: max(num(r, "p_q132"), num(r, "p_q133")))
            p = max(num(w, "p_q132"), num(w, "p_q133"))
            worst[(blk, m)] = {"p": p, "tj": TA + p * RTH_MJE_DISS, "caso": w["caso"],
                               "f": w["f_hz"]}
    classA = lambda r: num(r, "icmin_q132") > 0 and num(r, "icmax_q133") < 0  # noqa: E731
    listen = [r for r in tab if r["blk"] in LISTEN.get(r["caso"], set())]
    bad = [r for r in listen if not classA(r)]
    rsep = {m: max(num(r, "p_rsep") for r in tab if r["blk"] == "B" and r["modo_db"] == m)
            for m in ("0", "3", "10")}
    return {"dir": d, "worst": worst, "n_listen": len(listen), "n_bad": len(bad),
            "rsep": rsep, "tjmax": max(x["tj"] for x in worst.values())}


def measure_oppoint():
    """Punti di lavoro dal log di tb_op di L27."""
    d = sa(L64D, "tb_op")
    rails, cur = {}, {}
    with open(os.path.join(d, "tb_op.log")) as f:
        lines = [ln.rstrip("\n") for ln in f]
    for ln in lines:
        s = ln.strip()
        for key in ("i(vpp)", "i(vmm)"):
            if s.lower().startswith(key):
                try:
                    rails[key] = float(s.split("=")[1].strip())
                except (IndexError, ValueError):
                    pass
        if s.startswith("@"):
            try:
                lhs, rhs = s.split("=", 1)
                val = float(rhs.strip())
            except ValueError:
                continue
            dev, _, par = lhs.strip()[1:].partition("[")
            cur.setdefault(dev, {})[par.rstrip("]")] = val
    devices = [(dev, cur[dev]) for dev in sorted(cur, key=lambda d: (d[0], d))
               if any(k in cur[dev] for k in ("ic", "id"))]
    if not devices or len(rails) != 2:
        refuse("tb_op.log: punti di lavoro o correnti dei rail non trovati")
    # L51a: la continua d'uscita del blocco a ingresso a massa (ADR-056), quella che
    # attraversa il trim e che C_T ferma prima del volume (ADR-065, NC-041)
    vout = log_print(os.path.join(d, "tb_op.log"), "v(out)")
    if len(vout) != 1:
        refuse(f"tb_op.log: attesa una v(out), trovate {len(vout)}")
    return {"dir": d, "rails": rails, "devices": devices, "vout": at(vout, 0)}


# ------------------------------------------------------------ il mute -----
# L51a: il mute taglia coi soli rele' al jack (ADR-062), geometria iii (ADR-044).
# V2 si giudica con A e B (ADR-032) e, con la musica, sul jack grezzo e sul
# riferimento sempre in mute (ADR-063); S non c'e' piu'; il clic del taglio si
# misura e si dichiara, senza soglia (ADR-062). La regola del verdetto e' quella di
# data/2026-10-05/L47c2b1/script/verdetto.py, scritta di nuovo qui.
V2_SOGLIA = {"A_ins": 100e-6, "A_rel": 100e-6, "B2": 100e-6, "B2g": 100e-6, "B1": 100e-6}
V2_DICHIARATE = ("C2_ins", "C2_rel", "B2_musica")
V2_GRUPPI = {"1": "cambio di guadagno", "2": "cambio di trim", "3": "dispersione dell&rsquo;LSK489",
             "4": "durata del mute", "5": "accensione", "6": "scatto del volume"}
# le colonne della tabella di sintesi: (etichetta, grandezze, con la musica?)
V2_COLONNE = (("A", ("A_ins", "A_rel"), False), ("B2", ("B2",), False),
              ("B2g", ("B2g",), True), ("B1", ("B1",), True))
V2_ESCLUSA = "off_r10m_d20_iii"     # abortisce, esclusa come da L29d2 (L48b README)


def _csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def v2_verdetti(man_path, ana_path):
    """I verdetti di V2 ricalcolati da analisi.csv e dal manifesto (ADR-032, ADR-063):
    per cella e grandezza il peggiore sulle tre uscite; regge se sta sotto 100 µV e
    nessuna uscita ha la finestra corta. Con la musica B2 filtrato va col clic
    (dichiarato) e il verdetto e' B2g piu' B1 del riferimento sempre in mute; le
    corse di spegnimento off_* sono escluse (lo spegnimento vero e' quello morbido
    dell'alimentatore). Ritorna (verdetti, escluse)."""
    man = {r["cella"]: r for r in _csv(man_path)}
    ana = {}
    for a in _csv(ana_path):
        ana.setdefault((a["cella"], a["grandezza"]), []).append(a)
    out, escluse = {}, 0
    for c, r in man.items():
        if r["file"].startswith("off_"):
            escluse += 1
            continue
        conta = [x for x in r.get("conta", "").split(";") if x]
        if float(r["amp"]) > 0 and "B2" in conta:
            if "B2g" not in conta:
                refuse(f"{rel(man_path)}: {c} ha la musica e B2 senza B2g (ADR-063)")
            conta = [("B2_musica" if x == "B2" else x) for x in conta] + ["B1"]
        for g in conta:
            if g not in V2_SOGLIA and g not in V2_DICHIARATE:
                refuse(f"{rel(man_path)}: grandezza sconosciuta {g} in {c}")
                continue
            if g == "B1":
                vals = ana.get((r["rif_ins"], "B1"), [])
            else:
                vals = ana.get((c, "B2" if g == "B2_musica" else g), [])
            if len(vals) != 3:
                refuse(f"{rel(ana_path)}: {c} {g} ha {len(vals)} uscite, attese 3")
                continue
            w = max(vals, key=lambda a: float(a["picco_V"]) if a["picco_V"] else float("inf"))
            v = float(w["picco_V"]) if w["picco_V"] else None
            dich = g in V2_DICHIARATE
            ok = (dich or (v is not None and v <= V2_SOGLIA[g]
                           and not any("non accetta" in a["esito"] for a in vals)))
            out[(c, g)] = {"cella": c, "g": g, "gruppo": r["gruppo"], "amp": float(r["amp"]),
                           "f": r["f_hz"], "gm": r["gm"], "rl": r["rl"], "uscita": w["uscita"],
                           "v": v, "ok": ok, "dich": dich,
                           # la cella i cui dati danno il valore: per B1, il riferimento
                           "src": r["rif_ins"] if g == "B1" else c}
    return out, escluse


def measure_mute():
    """Il mute coi soli rele' (ADR-062, ADR-063, ADR-044). L64a: la matrice intera ricorsa il
    2026-11-02 sul circuito di oggi (L64a/v2); 22 celle della dispersione coi .nodeset del blocco
    da solo (limitations #86, la prova in L64a/prova_nodeset). Seconda strada: la matrice di
    L60d2 sul blocco di allora, cella per cella (gli stessi esiti, gli scarti si scrivono)."""
    out = {}
    # --- 1. la matrice di oggi: verdetto.csv contro il ricalcolo
    d = sa(L64A, "v2")
    man_f, ana_f = os.path.join(d, "manifest_finale.csv"), os.path.join(d, "analisi.csv")
    mine, escluse = v2_verdetti(man_f, ana_f)
    # il manifesto finale e' quello delle corse meno la sola corsa esclusa, dichiarata
    sel = {r["cella"]: r for r in _csv(os.path.join(d, "manifest_sel.csv"))}
    fin = {r["cella"]: r for r in _csv(man_f)}
    via = sorted(set(sel) - set(fin))
    if set(fin) - set(sel) or any(sel[c]["file"] != V2_ESCLUSA + ".dat" for c in via):
        refuse(f"L64a V2 manifest_finale.csv non e' manifest_sel.csv meno {V2_ESCLUSA}: {via}")
    theirs = _csv(os.path.join(d, "verdetto.csv"))
    if len(theirs) != len(mine):
        refuse(f"L64a V2 verdetto.csv: {len(theirs)} righe, il ricalcolo ne da' {len(mine)}")
    for t in theirs:
        m = mine.get((t["cella"], t["grandezza"]))
        if m is None:
            refuse(f"L64a V2 verdetto.csv: {t['cella']} {t['grandezza']} non viene dal ricalcolo")
            continue
        if m["dich"]:
            ok_s = t["soglia"] == "-" and t["esito"] == "dichiarato"
        else:
            ok_s = (abs(float(t["soglia"]) - V2_SOGLIA[t["grandezza"]]) <= 1e-12
                    and (t["esito"] == "regge") == m["ok"])
        if not ok_s or t["uscita"] != m["uscita"] or float(t["picco"]) != m["v"]:
            refuse(f"L64a V2 verdetto.csv: {t['cella']} {t['grandezza']} scritto {t['picco']} "
                   f"{t['uscita']} {t['esito']}, ricalcolato {m['v']} {m['uscita']} "
                   f"{'dichiarato' if m['dich'] else ('regge' if m['ok'] else 'NON REGGE')}")
    giud = [m for m in mine.values() if not m["dich"]]
    out.update(mat_dir=d, n=len(giud), n_fuori=sum(1 for m in giud if not m["ok"]),
               n_dich=len(mine) - len(giud), escluse=escluse, via=via,
               n_corse=len({r["file"] for r in sel.values()}))
    rows = []
    for gr in sorted(V2_GRUPPI):
        sg_ = [m for m in giud if m["gruppo"] == gr]
        row = {"gruppo": gr, "lab": V2_GRUPPI[gr], "n": len(sg_),
               "fuori": sum(1 for m in sg_ if not m["ok"])}
        for lab, gs, _ in V2_COLONNE:
            cand = [m for m in sg_ if m["g"] in gs]
            row[lab] = max(cand, key=lambda m: m["v"]) if cand else None
        rows.append(row)
    if sum(r["n"] for r in rows) != len(giud):
        refuse(f"L64a V2: {len(giud)} verdetti, i gruppi 1-6 ne contano {sum(r['n'] for r in rows)}")
    out["rows"] = rows

    # --- 2. il deck e le corse; la seconda strada, L60d2
    stessi_byte("il deck V2 rigenerato oggi dal sorgente",
                sa(L64A, "mute", "tb_v2_casopeggiore_generato.cir"),
                os.path.join(TB, "tb_v2_casopeggiore.cir"))
    corse = [c.strip() for c in open(os.path.join(d, "corse_sel.txt")) if c.strip()]
    tempi = {}
    for ln in open(os.path.join(d, "tempi.txt")):
        x = ln.split()
        if len(x) >= 2 and (x[1] == "rc=0" or x[0] not in tempi):
            tempi[x[0]] = (x[1], " ".join(x[4:]))
    male = [c for c in corse if tempi.get(c, ("",))[0] != "rc=0" and c != V2_ESCLUSA]
    if male:
        refuse(f"L64a V2: corse non finite con rc=0: {male[:5]}{' ...' if len(male) > 5 else ''}")
    with open(os.path.join(d, "guardia.txt")) as f:
        g = f.read()
    m_ = re.search(r"guardia: esce (\d+)", g)
    if not m_ or int(m_.group(1)) > 1:
        refuse(f"L64a V2: la guardia di L47b2b1 rifiuta {m_.group(1) if m_ else '?'} corse "
               f"(attesa al piu' {V2_ESCLUSA})")
    nb = sorted(c for c, (rc, nota) in tempi.items() if rc == "rc=0" and "nodeset_blocco" in nota)
    out.update(src_dir=d, src_corse=len(corse), nodeset=nb)
    v60 = {(r["cella"], r["grandezza"]): r for r in _csv(vecchio(L60D2, "v2", "verdetto.csv"))}
    # gli scarti in µV, non in dB: le celle del cambio di guadagno (B2g) stanno fra il pavimento
    # del metodo (~1 nV) e ~13 µV, in tutte e due le direzioni, e un rapporto fra quei due non dice
    # niente; contano lo scarto assoluto e il picco piu' alto contro il tetto
    cambi, scarto, picco_oggi, picco_60 = [], 0.0, 0.0, 0.0
    for t_ in theirs:
        o = v60.get((t_["cella"], t_["grandezza"]))
        if o is None:
            cambi.append(f"{t_['cella']} {t_['grandezza']} non c'e' in L60d2")
            continue
        if o["esito"] != t_["esito"]:
            cambi.append(f"{t_['cella']} {t_['grandezza']}: {o['esito']} -> {t_['esito']}")
        a_, b_ = float(t_["picco"]), float(o["picco"])
        if t_["esito"] != "dichiarato" and max(a_, b_) >= 1e-6:
            scarto = max(scarto, abs(a_ - b_))
        if t_["esito"] != "dichiarato":
            picco_oggi, picco_60 = max(picco_oggi, a_), max(picco_60, b_)
    out.update(l60d2_cambi=cambi, l60d2_scarto_v=scarto, l60d2_n=len(v60),
               l60d2_picco_oggi=picco_oggi, l60d2_picco=picco_60)
    if cambi:
        refuse(f"L64a V2 contro L60d2: {len(cambi)} esiti diversi, il primo {cambi[0]}")

    # --- 3. il clic del taglio, dichiarato (ADR-062): clic.csv contro analisi.csv
    clic = _csv(os.path.join(d, "clic.csv"))
    ana = {(a["cella"], a["grandezza"], a["uscita"]): a for a in _csv(ana_f)}
    usc = {"principale": "MAINJACK", "fissa 1": "FIXJACK1", "fissa 2": "FIXJACK2"}
    f = nc028_formula()
    for r in clic:
        g = "C2_ins" if r["evento"] == "inserimento" else "C2_rel"
        c = r["cella"]
        altra = c.replace("_r10k_iii", "_iii") if "_r10k_" in c else c.replace("_iii", "_r10k_iii")
        for lab, cc, col in (("c2_V", c, "c2_V"), ("altro_c2_V", altra, "altro_c2_V")):
            a = ana.get((cc, g, usc[r["uscita"]]))
            if a is None or not abs(float(r[col]) - float(a["picco_V"])) <= 5e-4 * float(a["picco_V"]):
                refuse(f"L64a V2 clic.csv: {r['uscita']} {r['tono']} {r['evento']} {lab} {r[col]}, "
                       f"analisi.csv {a['picco_V'] if a else 'manca'} ({cc} {g})")
        if f and not abs(f["db"](float(r["c2_V"])) - float(r["dB_SPL_1m"])) <= 0.051:
            refuse(f"L64a V2 clic.csv: {r['uscita']} {r['tono']} {r['evento']} {r['dB_SPL_1m']} dB SPL, "
                   f"la catena di NC-028 da' {f['db'](float(r['c2_V'])):.2f}")
    if len(clic) != 18:
        refuse(f"L64a V2 clic.csv: {len(clic)} righe, la tabella intera ne ha 18")
    out["clic"] = sorted(clic, key=lambda r: -float(r["c2_V"]))

    # --- 4. il gruppo 6 col difetto noto del banco tolto (VOSB = 0, limitations #44)
    with open(sa(L64A, "v2", "sonda_vosb", "alter.txt")) as f:
        if [ln.strip().endswith(":1") for ln in f if ln.strip()] != [True, True]:
            refuse("L64a sonda_vosb: alter vosb dc = 0 non e' in tutte e due le corse")
    vz = [a for a in _csv(os.path.join(sa(L64A, "v2", "sonda_vosb"), "analisi.csv"))
          if a["cella"] == "vol_g10_iii" and a["grandezza"] == "A_ins"]
    if len({a["uscita"] for a in vz}) != 3:
        refuse("L64a sonda_vosb: attese le tre uscite di vol_g10_iii A_ins")
    out["vosb0"] = max(float(a["picco_V"]) for a in vz) if vz else float("nan")
    return out


# ------------------------------------------------ E3 ed E5 all'ingresso -----
def measure_e3e5():
    """E3 ed E5 sull'ingresso di oggi (tb_e3_e5.cir, L48a e L48b): la rete di ADR-064
    (R_J, C_IN, R_SEL, il contatto del selettore) davanti al blocco A, E3 letta al
    jack, C_T e il bilanciamento al centro nella catena (ADR-065)."""
    d = sa(L64D, "tb_e3_e5")
    log = os.path.join(d, "tb_e3_e5.log")
    e3 = load_table(os.path.join(d, "tb_e3_e5_e3.csv"), 9)
    e5 = load_table(os.path.join(d, "tb_e3_e5_e5.csv"), 36)
    cross_table("tb_e3_e5_e3.csv [zmin_ohm]", e3, "zmin_ohm", log_print(log, "zmin"))
    cross_table("tb_e3_e5_e5.csv [onoise_uv]", e5, "onoise_uv", log_print(log, "onu"))
    n_err = count_errors(log)
    if n_err:
        refuse(f"{rel(log)}: {n_err} righe 'Error' (#26)")
    csels = sorted({r["csel"] for r in e3}, key=capval)
    z = {(r["pos"], r["csel"]): num(r, "zmin_ohm") for r in e3}
    w5 = max(e5, key=lambda r: num(r, "onoise_uv"))
    return {"dir": d, "csels": csels, "z": z, "e3min": min(z.values()),
            "e5max": num(w5, "onoise_uv"), "w5": w5}


# L42b: le cartelle di L41b2, lette dalle sezioni dell'alimentatore (L51b)
L41B2 = os.path.join(DATAROOT, "2026-09-26", "L41b2")

# ------------------------------------------------------ l'interblocco -----
def measure_interlock():
    """Il guadagno interbloccato (ADR-041, L36) e i comandi a pannello (ADR-045, L35)."""
    out = {}
    # --- la corsa al rilascio del mute: corsa.csv ricontato contro sintesi.txt
    d = sa(L36, "corsa")       # L51a: dato della scheda audio, eccezione dichiarata
    rows = _csv(os.path.join(d, "corsa.csv"))
    cnt = {}
    for r in rows:
        v = cnt.setdefault(r["variante"], {"n": 0, "ril": 0, "ins": 0, "bad": 0})
        v["n"] += 1
        v["ril"] += r["tiene_al_rilascio"] != "True"
        v["ins"] += r["tiene_all_inserimento"] != "True"
        v["bad"] += not (r["rc"] == "0" and r["corsa"] == "ok")
    with open(os.path.join(d, "sintesi.txt")) as f:
        sint = f.read()
    for var in ("ingenua", "progetto"):
        m = re.search(r"== " + var + r": (\d+) celle\n\s+cade al rilascio del mute:\s+(\d+)\n"
                      r"\s+cade all'inserimento del mute:\s+(\d+)", sint)
        if not m or var not in cnt:
            refuse(f"L36 sintesi.txt: manca il blocco della variante {var}")
            continue
        got = tuple(int(x) for x in m.groups())
        mine = (cnt[var]["n"], cnt[var]["ril"], cnt[var]["ins"])
        if got != mine:
            refuse(f"L36 {var}: sintesi.txt {got}, corsa.csv ricontato {mine}")
    if any(v["bad"] for v in cnt.values()):
        refuse("L36 corsa.csv: corse non andate a buon fine")
    out["corsa"] = cnt
    out["corsa_n"] = len(rows)
    out["corsa_dir"] = d

    # --- il 2e rieseguito sulla netlist di oggi
    proc = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "check_relay_safe_state.py"),
                           NET], capture_output=True, text=True)
    if proc.returncode != 0:
        refuse(f"check_relay_safe_state.py esce {proc.returncode} sulla netlist di oggi")
    txt = proc.stdout
    relays = re.findall(r"^\s+(K\d+)\s+'([^']+)'\s+ruolo=(\w+)$", txt, re.M)
    m = re.search(r"(\d+) componenti, (\d+) rele' noti", txt)
    if not m or int(m.group(2)) != len(relays):
        refuse("2e: il numero di relè dichiarato non coincide con quelli elencati")
    out["relays"] = relays
    out["n_comp"] = int(m.group(1)) if m else None
    mi = re.search(r"interblocco: .*?(\d+) stati provati", txt)
    mg = re.search(r"interblocco del guadagno: (.*?); (\d+) coppie stato/posizione.*?(\d+) trasferimenti", txt)
    if not (mi and mg):
        refuse("2e: le righe dell'interblocco non si leggono nell'uscita")
    out["stati_trim"] = int(mi.group(1)) if mi else None
    out["guad"] = (mg.group(1), int(mg.group(2)), int(mg.group(3))) if mg else None
    out["net"] = rel(NET)
    # L51a: il selettore (ADR-064) e il volume (ADR-065), come il 2e li legge oggi
    out["ingressi"] = re.findall(r"^\s+ingresso (IN\d_[LR]): (J\d+) -> (C\d+) (\S+) \(R_J (R\d+); "
                                 r"R_SEL (R\d+)\) -> (K\d+) NO", txt, re.M)
    out["volume"] = re.findall(r"^\s+volume (VOL_[LR]): K7 COM \((\w+)\) -> (C\d+) (\S+) -> "
                               r"(J\d+) pin 1; cursore (\w+) con R_G (R\d+) a GND$", txt, re.M)
    if len(out["ingressi"]) != 8 or len(out["volume"]) != 2:
        refuse(f"2e: {len(out['ingressi'])} ingressi e {len(out['volume'])} volumi letti, "
               "attesi 8 e 2 (ADR-064, ADR-065)")
    if not re.search(r"^selettore: SW\d, 4 posizioni", txt.replace("          ", ""), re.M):
        refuse("2e: la riga del selettore non si legge nell'uscita")

    # --- i falsi del 2e di oggi: L48a (il selettore) e L48b (il volume, col 2f).
    # Ogni riga dice se il controllo cade come deve; la netlist vera passa.
    # L64a: gli script dei falsi di L48a e L48b ricorsi oggi sulla netlist di oggi
    # (L64a/falsi_l48a, falsi_l48b). Il caso «main» di L48b (la netlist di prima di L48b) esce:
    # sul sorgente di oggi il 2f si ferma prima, su R179 del limitatore d'ingresso (ADR-101);
    # lo stesso difetto sulla netlist di oggi e' ct_cortocircuitato_L / _R. Restano 7.
    fz = {}
    for lot, root, attesi, pat, cade in (
            ("L48a", "falsi_l48a", 10,
             r"^(\d+) falsi su (\d+) cadono per il motivo giusto; controlli OK$", r"^CADE\s+rc=1"),
            ("L48b", "falsi_l48b", 7, r"^(\d+) falsi su (\d+) cadono dove devono; netlist vera passa$",
             r"^\S+\s+2e rc=1 CADE COME DEVE")):
        d = sa(L64A, root)
        with open(os.path.join(d, "verdetti.txt")) as f:
            vt = f.read()
        m = re.search(pat, vt, re.M)
        male = [ln for ln in vt.splitlines() if "NON " in ln or "ATTESO" in ln]
        if len(re.findall(cade, vt, re.M)) != attesi:
            male.append(f"{len(re.findall(cade, vt, re.M))} righe che cadono")
        if not m or m.group(1) != m.group(2) or int(m.group(2)) != attesi or male:
            refuse(f"{lot} falsi/verdetti.txt: attesi {attesi} falsi su {attesi} e la netlist "
                   f"vera che passa; letto {m.group(0) if m else 'niente'}")
        fz[lot] = {"n": int(m.group(2)) if m else 0, "dir": d}
    # (main_audio.net dei falsi e' la netlist di PRIMA del lotto, il falso «main»; che
    # quella di oggi passi lo dice il 2e rieseguito qui sopra)
    out["falsi"] = fz
    return out


# --------------------------------------------- il selettore e il volume -----
F1_MAX = 100e-6       # V di picco su ogni uscita, F1 / PR-14 (~33 dB SPL)
F1_MODI = (("0", "0 dB"), ("3", "+3 dB"), ("10", "+10 dB"))


def measure_selector():
    """F1 sul banco (tb_f1_selettore.cir, L48a, ADR-064): il cambio d'ingresso fra due
    sorgenti a continue diverse, picco dello scostamento in su e in giu' sul jack fisso
    e sul principale. modo 99 e' il controfattuale (l'ingresso di prima di L48a)."""
    d = sa(L64D, "tb_f1_selettore")
    log = os.path.join(d, "tb_f1_selettore.log")
    tab = load_table(os.path.join(d, "f1_selettore.csv"), 24)
    for col, k in (("jf_su_uv", "fu"), ("jf_giu_uv", "fd"), ("jm_su_uv", "mu"), ("jm_giu_uv", "md")):
        cross_table(f"f1_selettore.csv [{col}]", tab, col, log_print(log, k))
    if count_errors(log):
        refuse(f"{rel(log)}: righe 'Error' (#26)")
    marks = _markers(log, r"^F1 modo=(\d+) caso=(\d)$")
    if [m for m, _ in marks] != [r["modo"] for r in tab]:
        refuse("f1_selettore.csv: l'ordine dei modi non e' quello del log")
    cells = {}
    for r in tab:
        v = max(num(r, c) for c in ("jf_su_uv", "jf_giu_uv", "jm_su_uv", "jm_giu_uv")) * 1e-6
        cells[(r["modo"], r["vb"], r["trasf"])] = {
            "v": v, "jf": max(num(r, "jf_su_uv"), num(r, "jf_giu_uv")) * 1e-6,
            "jm": max(num(r, "jm_su_uv"), num(r, "jm_giu_uv")) * 1e-6}
    vbs = sorted({r["vb"] for r in tab}, key=float)
    # la regola di ADR-064: un gradino di fondo (quello del contatto, uguale fino a 100 mV)
    # piu' la perdita del condensatore, lineare nella continua: il limite al principale a
    # +10 dB e' dove la somma tocca F1_MAX
    r0, r1 = cells[("10", "0", "trasf")]["jm"], cells[("10", "1", "trasf")]["jm"]
    lim = (F1_MAX - r0) / (r1 - r0)
    regge = [vb for vb in vbs if all(cells[(m, vb, t)]["v"] <= F1_MAX
                                     for m, _ in F1_MODI for t in ("trasf", "sovrap")
                                     if (m, vb, t) in cells)]
    cf = {vb: cells[("99", vb, "trasf")] for vb in vbs}
    if not cf["0.01"]["jm"] > 100 * F1_MAX:
        refuse("F1: il controfattuale (l'ingresso di prima) non fallisce: il banco non distingue")
    return {"dir": d, "cells": cells, "vbs": vbs, "lim": lim, "r0": r0, "r1": r1,
            "regge": regge, "cf": cf}


def measure_volume(e3e5):
    """Il volume a potenziometro col bilanciamento (ADR-065, L48b): E5 col bilanciamento
    girato di 3 dB e V1 con la sorgente che volume e bilanciamento presentano al blocco B
    (le copie dei deck canonici di L48b, ricorse oggi); gli scatti del cursore sul banco
    di L48b, analizza.py rieseguito contro sintesi.csv e sintesi.txt."""
    out = {}
    d = sa(L64D, "bilanciamento", "tb_e5_bilanciamento")
    log = os.path.join(d, "tb_e5_bilanciamento.log")
    e5 = load_table(os.path.join(d, "tb_e3_e5_e5.csv"), 36)
    cross_table("tb_e5_bilanciamento [onoise_uv]", e5, "onoise_uv", log_print(log, "onu"))
    out["e5_dir"] = d
    out["e5_girato"] = max(num(r, "onoise_uv") for r in e5)
    out["e5_centro"] = e3e5["e5max"]

    d = sa(L64D, "bilanciamento", "tb_loop_bilanciamento")
    tab = _loop_table(d, "tb_loop_margini.csv", 528, "tb_loop_bilanciamento.log")
    out["v1_dir"] = d
    out["v1"] = []
    for rs in sorted({r["rsrc"] for r in tab}, key=lambda s: float(s.replace("k", "e3"))):
        sel = [r for r in tab if r["rsrc"] == rs and r["pos"] == "1"]
        w = min(sel, key=pm)
        out["v1"].append((rs, w, len(sel)))
    out["v1_min"] = min(pm(w) for _, w, _ in out["v1"])

    # gli scatti: analizza.py su copie dei CSV, in una cartella temporanea
    import tempfile
    dz = sa(L64A, "scatti")
    tmp = tempfile.mkdtemp(prefix="l51a_scatti_")
    os.mkdir(os.path.join(tmp, "deck"))
    shutil.copy(tool(dz, "analizza.py"), tmp)
    for f in sorted(os.listdir(os.path.join(dz, "deck"))):
        if f.startswith("scatti_v") and f.endswith(".csv"):
            shutil.copy(os.path.join(dz, "deck", f), os.path.join(tmp, "deck"))
    proc = subprocess.run([sys.executable, os.path.join(tmp, "analizza.py")],
                          capture_output=True, text=True, cwd=tmp)
    if proc.returncode != 0:
        refuse(f"scatti/analizza.py esce {proc.returncode}: {proc.stderr.strip()[-200:]}")
    for f in ("sintesi.csv", "sintesi.txt"):
        stessi_byte(f"scatti/{f} rifatto oggi", os.path.join(tmp, f), os.path.join(dz, f))
    rows = _csv(os.path.join(dz, "sintesi.csv"))
    fin = [r for r in rows if r["var"] == "4"]
    if not fin or {r["cap"] for r in fin} != {"finale"}:
        refuse("scatti/sintesi.csv: manca la variante 4, il circuito finale")
    vol = [r for r in fin if r["evento"] in ("1", "2")]
    tri = [r for r in fin if r["evento"] in ("3", "4")]
    out["scatti_dir"] = dz
    out["vol_max"] = max(float(r["peggiore_uv"]) for r in vol) * 1e-6
    out["vol_max_m1"] = max(float(r["peggiore_uv"]) for r in vol if r["modo"] == "1") * 1e-6
    out["oggi_max"] = max(float(r["peggiore_uv"]) for r in rows
                          if r["var"] == "0" and r["evento"] in ("1", "2")) * 1e-6
    out["trim_max"] = max(float(r["peggiore_uv"]) for r in tri) * 1e-6
    out["n_fin"] = len(fin)
    # L64a, la seconda strada: lo stesso banco di L48b (prima del limitatore d'ingresso e dei
    # cambi del blocco; la continua propria del blocco A era -6,62 mV, oggi -2,89), riga per
    # riga sulle varianti 0 e 4: entro l'1 % dove il gradino supera 100 uV, entro 1 uV dove
    # sta al pavimento del metodo
    key = lambda r: (r["var"], r["evento"], r["guad_db"] if "guad_db" in r else r.get("g"),  # noqa: E731
                     r.get("modo"))
    l48 = {key(r): r for r in _csv(vecchio(L48B, "scatti", "sintesi.csv")) if r["var"] in ("0", "4")}
    rel_max, abs_max, n2 = 0.0, 0.0, 0
    for r in rows:
        if r["var"] not in ("0", "4"):
            continue
        s = l48.get(key(r))
        if s is None:
            refuse(f"scatti: la riga {key(r)} non c'e' in L48b")
            continue
        n2 += 1
        # tutte e due le colonne: il gradino nominale e il peggiore (L64a: un sabotaggio sul solo
        # nominale passava)
        for col in ("nominale_uv", "peggiore_uv"):
            a_, b_ = float(r[col]), float(s[col])
            if max(a_, b_) >= 100:
                rel_max = max(rel_max, abs(a_ - b_) / b_)
            else:
                abs_max = max(abs_max, abs(a_ - b_))
    if not (rel_max <= 0.01 and abs_max <= 1.0) or n2 != len(l48):
        refuse(f"scatti contro L48b: {n2} righe su {len(l48)}, scarto {rel_max:.2%} sopra 100 uV, "
               f"{abs_max:.3f} uV sotto")
    out.update(l48b_rel=rel_max, l48b_abs_uv=abs_max, l48b_n=n2)
    return out


# ------------------------------------------------------------ il calore ---
def v4_soglie():
    """I tetti di V4 (ADR-055), letti dalla tabella di REQUIREMENTS.md, non scritti qui."""
    with open(os.path.join(REPO, "docs", "preamp", "REQUIREMENTS.md")) as f:
        rows = [ln for ln in f if ln.startswith("| ") and "**≤ " in ln]

    def tetto(pred, k):
        r = [ln for ln in rows if pred(ln)]
        m = re.search(r"\*\*≤ (−?[\d,]+) (?:%|dB)\*\*", r[0]) if len(r) == 1 else None
        if not m:
            refuse(f"REQUIREMENTS.md, tabella di V4: non trovo una sola riga col tetto {k}")
            return float("nan")
        return float(m.group(1).replace(",", ".").replace("−", "-"))
    return {"thd20_lo": tetto(lambda ln: "non cresce verso gli acuti" in ln, "della THD a 20 kHz"),
            "h5": tetto(lambda ln: "dalla 5ª in su" in ln, "delle armoniche dalla 5ª"),
            "imd": tetto(lambda ln: "intermodulazione" in ln, "dell'intermodulazione"),
            "thd20_hi": tetto(lambda ln: "prova di stress" in ln, "della prova di stress")}


def measure_distortion():
    """V4 sul blocco di oggi, in tre parti (L64a).
      1. il blocco a 27 °C col banco di L46b, ricorso oggi (L64a/distorsione, come L51c): il
         blocco corso uguale a gain_block_flat.inc di oggi; i deck uguali a quelli di L46b a meno
         del blocco incluso; la THD che ngspice stampa nel log contro il CSV di leggi_four.py,
         caso per caso. La seconda strada e' la corsa di L51c sullo stesso banco col blocco di
         allora: gli scarti si pubblicano, non si chiede l'uguaglianza (il blocco e' cambiato);
      2. il blocco a caldo, ogni giunzione alla sua temperatura (L66, la variante lim365 che e'
         il sorgente di oggi): L66/sintesi_caldo.csv contro le 48 THD del deck di L66 che L67 ha
         rifatto (L67/noto_caldo.csv, colonna thd_piatto_pct), massimo per condizione e livello;
      3. la catena (L67, ADR-112): ogni blocco al suo livello, tetto(L) = 0,001 % x L / 0,2 V con
         L = max(livello del blocco A, livello alla principale), scritto di nuovo qui e applicato
         ai catena_<blocco>.csv, contro verifica_livello.csv riga per riga; l'intermodulazione
         sulla catena (imd_catena.csv) contro il tetto di V4 letto da REQUIREMENTS.md.
    I tetti di V4 sono letti da REQUIREMENTS.md."""
    dd = sa(L64A, "distorsione")
    inc = sa(dd, "inc", "oggi.inc")
    with open(inc) as f:
        head, body = f.read().split("\n", 1)
    with open(os.path.join(REPO, "spice", "preamp", "gain_block_flat.inc")) as f:
        if f.read() != body or not head.startswith("*"):
            refuse(f"{rel(inc)}: non e' spice/preamp/gain_block_flat.inc di oggi con una riga di "
                   "commento in testa: il blocco corso non e' quello del sorgente")
    for d in DIST_DECKS:
        stesso_deck(f"distorsione, {d}", sa(dd, "deck", "oggi", d + ".cir"),
                    vecchio(L46B, "deck", L46B_VAR, d + ".cir"),
                    swap=(("variante oggi", "variante " + L46B_VAR),
                          ("data/2026-11-02/L64a/distorsione/inc/oggi.inc",
                           f"data/2026-10-01/L46b/inc/{L46B_VAR}.inc")))
    esiti = {}
    with open(sa(dd, "run", "esiti.tsv")) as f:
        for ln in f:
            c = ln.rstrip("\n").split("\t")
            if len(c) == 4 and c[0] == "oggi":
                esiti[c[1]] = c[2]
    rows = rows_of(sa(dd, "run", "oggi", "distorsione.csv"))
    for d in DIST_DECKS:
        if esiti.get(d) != "0":
            refuse(f"distorsione, {d}: run_simulation.sh ha dato rc {esiti.get(d)} (esiti.tsv)")
        log = sa(dd, "run", "oggi", d, d + ".log")
        log_pulito(log)
        if d == "imd":
            continue
        with open(log, errors="replace") as f:
            text = f.read()
        casi = re.findall(r"^L46A_CASO modo=(\S+) livello=(\S+)", text, re.M)
        thd = re.findall(r"Fourier analysis for v\(out\):\s*\n\s*No\. Harmonics: \d+, THD: "
                         r"([-+0-9.eE]+) %", text)
        if len(casi) != 6 or len(thd) != len(casi):
            refuse(f"distorsione, {d}: {len(casi)} casi e {len(thd)} THD di v(out) nel log, "
                   "invece di 6 e 6")
            continue
        for (modo, liv), t_ in zip(casi, thd):
            r = [x for x in rows if x["deck"] == d and x["modo"] == modo and x["livello"] == liv]
            if len(r) != 1 or not math.isclose(float(r[0]["thd_pct"]), float(t_), rel_tol=1e-3):
                refuse(f"distorsione, {d} modo {modo} {liv}: la THD del log ({t_} %) non e' quella "
                       f"del CSV ({r[0]['thd_pct'] if len(r) == 1 else 'assente'})")
    # la seconda strada: L51c, lo stesso banco col blocco del 2026-10-10; gli scarti in dB
    old = {(r["deck"], r["modo"], r["livello"]): r
           for r in rows_of(vecchio(L51CD, "run", "oggi", "distorsione.csv"))}
    new = {(r["deck"], r["modo"], r["livello"]): r for r in rows}
    if set(old) != set(new) or len(new) != 24:
        refuse(f"distorsione: {len(new)} casi oggi, {len(old)} in L51c, non gli stessi 24")
    scarto_thd = max((abs(db20(float(new[k]["thd_pct"]) / float(old[k]["thd_pct"])))
                      for k in new if k in old and new[k]["thd_pct"] and old[k]["thd_pct"]),
                     default=float("nan"))
    scarto_imd = max((abs(float(new[k]["imd_d2_db"]) - float(old[k]["imd_d2_db"]))
                      for k in new if k in old and new[k]["imd_d2_db"] and old[k]["imd_d2_db"]),
                     default=float("nan"))

    def mx(col, deck, liv, rr=rows):
        v = [float(r[col]) for r in rr if r["livello"] == liv and r["deck"].startswith(deck)
             and r[col] != ""]
        return max(v) if v else float("nan")
    out = {"dir": dd, "rows": rows, "soglie": v4_soglie(),
           "thd_lo": {f: mx("thd_pct", f"thd_{f}", "lo") for f in ("1k", "10k", "20k")},
           "h5_lo": mx("h5su_db", "thd", "lo"), "imd_lo": mx("imd_d2_db", "imd", "lo"),
           "thd_hi_20k": mx("thd_pct", "thd_20k", "hi"), "imd_hi": mx("imd_d2_db", "imd", "hi"),
           "h5_lo_l46b": mx("h5su_db", "thd", "lo", list(old.values())),
           "l51c_dir": L51CD, "scarto_thd_db": scarto_thd, "scarto_imd_db": scarto_imd,
           "thd_20k_l51c": mx("thd_pct", "thd_20k", "lo", list(old.values()))}
    s = out["soglie"]
    out["ok"] = {"thd20_lo": out["thd_lo"]["20k"] <= s["thd20_lo"],
                 "h5": out["h5_lo"] <= s["h5"],
                 "imd": out["imd_lo"] <= s["imd"], "thd20_hi": out["thd_hi_20k"] <= s["thd20_hi"]}

    # 2. a caldo (L66), contro le 48 THD rifatte da L67
    sc = [r for r in _csv(sa(L66, "sintesi_caldo.csv")) if r["spec"] == "lim365--sot223--diss"]
    noto = _csv(sa(L67, "noto_caldo.csv"))
    caldo = []
    for r in sc:
        nn = [x for x in noto if x["cond"] == r["cond"]]
        if len(nn) != 12:
            refuse(f"L67/noto_caldo.csv: {len(nn)} casi per {r['cond']}, attesi 12")
            continue
        for liv, col in (("lo", "thd_lo_max_pct"), ("hi", "thd_hi_max_pct")):
            m = max(float(x["thd_piatto_pct"]) for x in nn if f"livello={liv}" in x["caso"])
            if "%.3g" % m != "%.3g" % float(r[col]):
                refuse(f"a caldo, {r['cond']} {liv}: L66 scrive {r[col]} %, le THD rifatte da L67 "
                       f"danno {m:.6g} %")
            if any(float(x["diff_rel"]) != 0 for x in nn):
                refuse(f"L67/noto_caldo.csv: il blocco avvolto non ridà L66 in {r['cond']}")
        caldo.append({"cond": r["cond"], "fuori": int(r["thd_fuori"]),
                      "margine": float(r["thd_margine_min_dB"]), "thd_lo": float(r["thd_lo_max_pct"]),
                      "thd_hi": float(r["thd_hi_max_pct"]), "imd": float(r["imd_lo_max_dB"])})
    if len(caldo) != 4:
        refuse(f"L66/sintesi_caldo.csv: {len(caldo)} condizioni per lim365, attese 4")
    out["caldo"] = caldo
    out["caldo_dir"] = L66

    # 3. la catena (L67, ADR-112)
    liv_main = {"lo": 0.2, "hi": 2.0}
    ver = _csv(sa(L67, "verifica_livello.csv"))
    blocchi = sorted({r["blocco"] for r in ver})
    cat = {}
    for bl in blocchi:
        mine = []
        for r in _csv(sa(L67, f"catena_{bl}.csv")):
            if r["freq"] != "20000":
                continue
            L_ = max(float(r["livello_A_V"]), liv_main[r["livello"]])
            tetto = s["thd20_lo"] * L_ / 0.2
            mine.append((r["griglia"], r["uscita"], r["livello"], r["modo"], r["vol"], r["rs"],
                         20 * math.log10(tetto / float(r["thd_pct"])), r["verdetto"]))
        theirs = [(r["griglia"], r["uscita"], r["livello"], r["modo"], r["vol"], r["rs"],
                   float(r["margine_dB"]), r["verdetto_v4"]) for r in ver if r["blocco"] == bl]
        if len(mine) != len(theirs) or any(
                a_[:6] != b_[:6] or abs(a_[6] - b_[6]) > 0.051 or a_[7] != b_[7]
                for a_, b_ in zip(mine, theirs)):
            refuse(f"L67, la catena {bl}: la regola di ADR-112 rifatta qui non ridà verifica_livello.csv")
        cat[bl] = {"n": len(mine), "fuori": sum(1 for x in mine if x[6] < 0),
                   "margine": min(x[6] for x in mine),
                   "fuori_v4": sum(1 for x in mine if x[7] != "dentro")}
    out["catena"] = cat
    imd = _csv(sa(L67, "imd_catena.csv"))
    for r in imd:
        if abs((s["imd"] - float(r["imd_d2_db"])) - float(r["margine_dB"])) > 0.051:
            refuse(f"L67/imd_catena.csv: margine {r['margine_dB']} dB, il tetto di V4 da' "
                   f"{s['imd'] - float(r['imd_d2_db']):.1f}")
    out["imd_catena"] = {"n": len(imd), "fuori": sum(1 for r in imd if r["verdetto"] != "dentro"),
                         "margine": min(float(r["margine_dB"]) for r in imd)}
    out["catena_dir"] = L67
    # V1 sulla dispersione di I_DSS del blocco scelto (L46b): per «Cosa non dice»
    idss = [r for r in rows_of(vecchio(L46B, "idss.csv")) if r["variante"] == L46B_VAR]
    out["v1_idss"] = (min(float(idss[0][c]) for c in ("B_pubbl_min", "A_pubbl_min", "buf_pubbl_min"))
                      if len(idss) == 1 else None)
    if out["v1_idss"] is None:
        refuse(f"L46b/idss.csv: la riga {L46B_VAR} non c'e'")
    return out


# ------------------------------------------- le sezioni nuove di L64a -----
RTH_VAS = 125.0        # °C/W, il VAS in SOT-223 (ADR-068), la cifra dei banchi del calore di L66


def p10_soglia_ms():
    """Il tetto di P10 sulla Stax, letto da REQUIREMENTS.md (ADR-086), non scritto qui."""
    with open(os.path.join(REPO, "docs", "preamp", "REQUIREMENTS.md")) as f:
        r = [ln for ln in f if ln.startswith("| P10 |")]
    m = re.search(r"al più \*\*(\d+) ms\*\*", r[0]) if len(r) == 1 else None
    if not m:
        refuse("REQUIREMENTS.md: non trovo il tetto di P10 in ms")
        return float("nan")
    return float(m.group(1))


def measure_limitatore():
    """Il limitatore d'ingresso (ADR-101, «dopo L57b»): l'RCA collegato a caldo e il costo.
    Seconda strada: le cifre di THD ed E5 di sintesi.csv uguali a quelle di costo/costo.csv."""
    d = sa(DATAROOT, "2026-10-25", "dopo-L57b")
    rows = _csv(os.path.join(d, "sintesi.csv"))
    lim = [r for r in rows if r["variante"] == "lim"]
    mute = [r for r in rows if r["variante"] == "mute_lim"]
    if len(lim) != 3 or len(mute) != 3:
        refuse("dopo-L57b/sintesi.csv: attese tre reti per lim e per mute_lim")
        return {}
    costo = _csv(os.path.join(d, "costo", "costo.csv"))

    def c(var, f, liv, col):
        r = [x for x in costo if x["variante"] == var and x["freq"] == f and x["livello"] == liv]
        return float(r[0][col]) if len(r) == 1 and r[0][col] else float("nan")
    for r in lim:
        for col, f, liv, cc in (("thd20k_02v_pct", "20000", "lo", "thd_pct"),
                                ("thd20k_2v_pct", "20000", "hi", "thd_pct"),
                                ("e5_stima_uv", "1000", "lo", "e5_stima_uv")):
            if float(r[col]) != c("lim", f, liv, cc):
                refuse(f"dopo-L57b: {col} {r[col]} in sintesi.csv, {c('lim', f, liv, cc)} in costo.csv")
    w = max(lim, key=lambda r: float(r["ain_pk_v"]))
    return {"dir": d, "ain": float(w["ain_pk_v"]), "gg_m": min(float(r["gg_margine_v"]) for r in lim),
            "gd_m": min(float(r["gd_margine_v"]) for r in lim),
            "k11_0": max(float(r["k11_0db_dbspl"]) for r in lim),
            "k11_10": max(float(r["k11_10db_dbspl"]) for r in lim),
            "mute_0": max(float(r["k11_0db_dbspl"]) for r in mute),
            "mute_10": max(float(r["k11_10db_dbspl"]) for r in mute),
            "thd_senza": c("senza", "20000", "lo", "thd_pct"), "thd_lim": c("lim", "20000", "lo", "thd_pct"),
            "e5_senza": c("senza", "1000", "lo", "e5_stima_uv"), "e5_lim": c("lim", "1000", "lo", "e5_stima_uv")}


def measure_guasti_blocco():
    """I guasti del blocco sul sorgente di oggi, col dissipatore sui finali (L66, calore_dopo.csv:
    714 modi, quattro posizioni). Seconda strada: la temperatura dei finali e del VAS rifatta qui
    dalla potenza, 60 °C d'aria, RTH_MJE_DISS e RTH_VAS, entro l'arrotondamento al grado."""
    rows = _csv(sa(L66, "calore_dopo.csv"))
    male = 0
    for r in rows:
        for dev, rth in (("q132", RTH_MJE_DISS), ("q133", RTH_MJE_DISS)):
            if abs(TA + float(r[f"P_{dev}_W"]) * rth - float(r[f"Tj_{dev}_60"])) > 0.6:
                male += 1
        if float(r["Tj_max_60"]) < TA + float(r["P_q122_W"]) * RTH_VAS - 0.6:
            male += 1
    if male:
        refuse(f"L66/calore_dopo.csv: {male} temperature non tornano dalla potenza")
    w = max(rows, key=lambda r: float(r["Tj_max_60"]))
    fin = max(rows, key=lambda r: max(float(r["Tj_q132_60"]), float(r["Tj_q133_60"])))
    oltre = [r for r in rows if float(r["Tj_max_60"]) > TJ_MAX]
    tj = _csv(sa(L66, "tj", "lim365--sot223--diss.csv"))
    # le righe di nota del file (Tj = «coda=...») non sono temperature
    riposo = {(r["aria"], r["variante"], r["disp"]): float(r["Tj"]) for r in tj
              if re.fullmatch(r"[-+0-9.eE]+", r["Tj"] or "")}
    return {"dir": L66, "n": len(rows), "w": w, "tjmax": float(w["Tj_max_60"]),
            "fin": fin, "fin_tj": max(float(fin["Tj_q132_60"]), float(fin["Tj_q133_60"])),
            "oltre": len(oltre), "oltre_flag": sum(1 for r in rows if r["oltre_i_limiti_60C"]),
            # le parti oltre i loro limiti (non le giunzioni): C145 in corto, NC-075
            "oltre_txt": sorted({(r["modo"], r["oltre_i_limiti_60C"]) for r in rows
                                 if r["oltre_i_limiti_60C"]}),
            "riposo_fin_57": max(v for (a, v_, d), v in riposo.items()
                                 if a == "57" and d.upper() in ("Q132", "Q133")),
            "riposo_max_57": max(v for (a, v_, d), v in riposo.items() if a == "57")}


def measure_stax():
    """La Stax (fissa 2) contro P10 (ADR-086), il tetto letto da REQUIREMENTS.md: il tempo sopra
    0,87 V sul jack della Stax (fix2_sopra_ms). I modi che il limitatore di ADR-111 tocca, sul
    sorgente di oggi (L66/p10_stax.csv); gli altri modi nuovi di L45d2b3b3. La colonna «p10»
    dei CSV e' giudicata contro 100 ms (LIMITE_P10_MS di L45b, prima di ADR-086): non si legge.
    Seconda strada: fix2_sopra_ms <= fix2_ultimo_ms riga per riga, e p10_sopra_ms_max >= ogni
    colonna _sopra_ms."""
    soglia = p10_soglia_ms()
    out = {"soglia": soglia, "parti": []}
    for lab, path in (("oggi (L66)", sa(L66, "p10_stax.csv")),
                      ("modi nuovi (L45d2b3b3)", sa(DATAROOT, "2026-10-24", "L45d2b3b3",
                                                     "p10_stax_nuove.csv")),
                      ("controllo (L45d2b3b3)", sa(DATAROOT, "2026-10-24", "L45d2b3b3",
                                                    "p10_stax_controllo.csv"))):
        rows = _csv(path)
        for r in rows:
            s_ = [float(r[k]) for k in ("main_sopra_ms", "fix1_sopra_ms", "fix2_sopra_ms")]
            if float(r["fix2_sopra_ms"]) > float(r["fix2_ultimo_ms"]) + 0.05 or \
                    abs(float(r["p10_sopra_ms_max"]) - max(s_)) > 0.05:
                refuse(f"{rel(path)}: {r['modo']}, i tempi sopra 0,87 V non tornano")
        w = max(rows, key=lambda r: float(r["fix2_sopra_ms"]))
        out["parti"].append({"lab": lab, "path": path, "n": len(rows),
                             "fuori": sum(1 for r in rows if float(r["fix2_sopra_ms"]) > soglia),
                             "max": float(w["fix2_sopra_ms"]), "modo": w["modo"]})
    out["max"] = max(x["max"] for x in out["parti"])
    return out



# I report delle schede di prova: i vincoli per il progetto stanno li', in un elenco numerato
# col titolo in grassetto. Si leggono, non si riscrivono (sono testo, non numeri dei JSON).
L49A_REPORT = os.path.join(REPO, "docs", "preamp", "reports", "2026-10-09-L49a-scheda-audio-prova.md")
L49B_REPORT = os.path.join(REPO, "docs", "preamp", "reports", "2026-10-09-L49b-alimentatore-assieme.md")


def vincoli_l49(path):
    """[(numero, titolo in grassetto)] dalla sezione «I vincoli che tornano al progetto»."""
    if not os.path.isfile(path):
        refuse(f"manca il report {rel(path)}")
        return []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^## I vincoli che tornano al progetto\n(.*?)(?=^## )", text, re.M | re.S)
    if not m:
        refuse(f"{rel(path)}: non trovo la sezione «I vincoli che tornano al progetto»")
        return []
    items = re.findall(r"^(\d+)\. \*\*(.+?)\*\*", m.group(1), re.M)
    if not items or [int(n) for n, _ in items] != list(range(1, len(items) + 1)):
        refuse(f"{rel(path)}: i vincoli non sono numerati 1..n ({[n for n, _ in items]})")
    return [(int(n), t) for n, t in items]


def measure_boards():
    """Le schede di prova di L49 (L51c): la DRC rifatta oggi contro quella del 9 ottobre, le
    misure dai JSON di L49 incrociate fra loro, l'assieme, i vincoli dai report."""
    def drc_n(j):
        return tuple(len(j.get(k, [])) for k in ("violations", "unconnected_items", "schematic_parity"))
    out = {"boards": {}}
    for key, base, sub, pcb, drc in (("audio", L49A, (), "audio_routed", "drc_audio_routed.json"),
                                     ("psu", L49B, ("psu",), "psu_routed", "drc_psu_routed.json")):
        d = sc(base, *sub)
        with open(sc(L51C, "drc", drc)) as f:
            oggi = json.load(f)
        with open(sc(base, *sub, drc)) as f:
            prima = json.load(f)
        for lab, j in (("oggi", oggi), ("9 ottobre", prima)):
            if j.get("source") != pcb + ".kicad_pcb":
                refuse(f"DRC {key} ({lab}): la scheda e' {j.get('source')}, non {pcb}.kicad_pcb")
        if oggi.get("kicad_version") != prima.get("kicad_version"):
            refuse(f"DRC {key}: kicad-cli {oggi.get('kicad_version')} oggi, "
                   f"{prima.get('kicad_version')} il 9 ottobre: le due DRC non sono la stessa prova")
        if drc_n(oggi) != drc_n(prima):
            refuse(f"DRC {key}: oggi {drc_n(oggi)} (violazioni, aperte, parita'), il 9 ottobre "
                   f"{drc_n(prima)}")
        if not oggi.get("date", "").startswith(L51C.split(os.sep)[-2]):
            refuse(f"DRC {key}: il rapporto di oggi e' del {oggi.get('date')}")
        sc(base, *sub, pcb + ".kicad_pro")      # le classi stanno li' (limitations #52)
        with open(sc(base, *sub, "measure.json")) as f:
            meas = json.load(f)
        with open(sc(base, *sub, "placement.json")) as f:
            pl = json.load(f)
        if pl.get("board_mm") != meas.get("board_mm") or pl.get("courtyard_overlaps"):
            refuse(f"scheda {key}: placement.json e measure.json non danno la stessa scheda "
                   f"({pl.get('board_mm')} / {meas.get('board_mm')}), o ci sono sovrapposizioni")
        with open(sc(base, *sub, "freerouting.log"), errors="replace") as f:
            fr = re.search(r"Freerouting (v[\d.]+)", f.read())
        out["boards"][key] = {"dir": d, "pcb": os.path.join(d, pcb + ".kicad_pcb"),
                              "drc": drc_n(oggi), "kicad": oggi.get("kicad_version"),
                              "kicad_prima": prima.get("kicad_version"),
                              "meas": meas, "pl": pl, "freerouting": fr.group(1) if fr else None}
        if not fr:
            refuse(f"scheda {key}: la versione di Freerouting non si legge dal log")
    with open(sc(L49B, "assembly", "assembly.json")) as f:
        asm = json.load(f)
    if (asm.get("audio_board_mm") != out["boards"]["audio"]["meas"]["board_mm"]
            or asm.get("supply_board_mm") != out["boards"]["psu"]["meas"]["board_mm"]):
        refuse("assembly.json: le schede dell'assieme non sono quelle misurate")
    fits = [k for k, v in asm["variants"].items() if v.get("fits")]
    if fits != ["A_tutto_sul_fondo"]:
        refuse(f"assembly.json: le varianti che ci stanno sono {fits}, non la sola A")
    out["asm"] = asm
    out["fit"] = asm["variants"].get("A_tutto_sul_fondo", {})
    out["vincoli"] = {"audio": vincoli_l49(L49A_REPORT), "psu": vincoli_l49(L49B_REPORT)}
    for name, parts in IMMAGINI.items():
        p = sc(*parts)
        with open(p, "rb") as f:
            if f.read(8) != b"\x89PNG\r\n\x1a\n":
                refuse(f"{rel(p)}: non e' un PNG")
    out["pdf"] = {k: rel(os.path.join(b["dir"], "routing_both.pdf")) for k, b in out["boards"].items()}
    out["pdf"]["asm"] = rel(os.path.join(L49B, "assembly", "assembly_A_tutto_sul_fondo.pdf"))
    for p in out["pdf"].values():
        if not os.path.isfile(os.path.join(REPO, p)):
            refuse(f"manca {p}")
    return out


def measure_heat(op, pw):
    """Il calore del telaio (P5, ADR-021, ADR-047), L51b e poi L64b: il modello del telaio e del vano
    di L30 / L41a, le potenze dal banco dell'alimentatore di oggi (tb_calore, dal deck della rete di
    L64b), la scheda audio da tb_op di oggi. CALCOLATA; il ferro dei trasformatori e' un'ipotesi
    dichiarata. L64b: tre voci nuove dal banco, le 4,7 ohm davanti ai regolatori (ADR-092), gli SB340
    dopo (ADR-093), i diodi inversi (ADR-094) nel resto; la scheda audio sul banco del calore
    contro i rail del banco della rete (due corse diverse dello stesso circuito)."""
    d = ps(L64B, "termica")
    # il deck del calore si rigenera dal deck della rete di oggi e dev'essere quello corso
    deck = os.path.join(d, "tb_calore.cir")
    _, tmp = in_tmp(tool(d, "genera_calore.py"), [], ["--uscita", "@TMP@/tb_calore.cir"],
                    cwd_files=False)
    stesso_deck("deck del calore", os.path.join(tmp, "tb_calore.cir"), deck)
    log = os.path.join(d, "tb_calore.log")
    log_pulito(log)
    bench = {}
    for ln in open(log, errors="replace"):
        m = re.match(r"CALORE (regime_\w+) (.*)$", ln.strip())
        if m:
            bench[m.group(1)] = {k: float(v) for k, v in (x.split("=") for x in m.group(2).split())}
    if sorted(bench) != ["regime_m10", "regime_nom", "regime_p10"]:
        refuse(f"{rel(log)}: casi a regime {sorted(bench)}")
    script = os.path.join(d, "stima_telaio_l64b.py")
    proc = subprocess.run([sys.executable, "-I", script], capture_output=True, text=True)
    with open(os.path.join(d, "stima_telaio_l64b.txt")) as f:
        saved = f.read()
    if proc.returncode != 0 or proc.stdout != saved:
        refuse("stima_telaio_l64b.py rieseguito non ridà stima_telaio_l64b.txt")
    P = re.findall(r"^(.+?)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)$", saved, re.M)
    P = [(k.strip(), float(a), float(b), float(c)) for k, a, b, c in P]
    tot = [p for p in P if p[0] == "TOTALE"]
    parts = [p for p in P if p[0] != "TOTALE"]
    if len(tot) != 1 or not all(abs(sum(p[i] for p in parts) - tot[0][i]) <= 0.02 for i in (1, 2, 3)):
        refuse("stima_telaio.txt: le voci non sommano al totale")
    V = re.findall(r"^(\S+(?: cm)?|all'aria)\s+(nominale|peggiore)\s+(\d+\.\d)\s+(\d+\.\d)\s+"
                   r"(\d+\.\d)\s+(\d+\.\d)$", saved, re.M)
    gm = re.search(r"gioco minimo del vano chiuso per 60 C nel caso peggiore: ([\d.]+) cm", saved)
    if not V or not gm:
        refuse("stima_telaio.txt: la tabella del vano non si legge")
    # la seconda strada della scheda audio: la stima contro i rail di tb_op di oggi (stampata a due
    # decimali: lo scarto ammesso e' l'arrotondamento), e il banco, che la carica con le stesse
    # correnti a V+ e V- invece che a 15 V tondi (lo 0,5 %)
    audio = [p for p in parts if p[0].startswith("scheda audio")]
    p_blk = 15.0 * (abs(op["rails"].get("i(vpp)", 0)) + abs(op["rails"].get("i(vmm)", 0)))
    if len(audio) != 1 or not abs(8 * p_blk - audio[0][1]) <= 0.005:
        refuse(f"calore: la scheda audio della stima vale {audio[0][1] if audio else '?'} W, "
               f"8 x 15 V x i(rail) di tb_op di oggi da' {8 * p_blk:.4f} W")
    car = leggi_carico(L64B)
    ip, im = float(car["i_piu_mA"]) * 1e-3, float(car["i_meno_mA"]) * 1e-3
    for c, b in bench.items():
        if not abs(b["paud"] - 8 * p_blk) <= 0.005 * 8 * p_blk:
            refuse(f"calore, {c}: il banco carica la scheda audio con {b['paud']:.4f} W, "
                   f"tb_op ne da' {8 * p_blk:.4f}")
        # L64b: lo stesso circuito nel banco della rete (un'altra corsa): V+ x I+ + |V-| x I- dai
        # rail a regime di analisi.csv (quattro decimali: 0,1 mV x 0,6 A, il decimo di mW)
        rr = pw["oggi"].get(c, {})
        try:
            p_rete = float(rr["vplus"]) * ip + abs(float(rr["vminus"])) * im
        except (KeyError, ValueError):
            p_rete = float("nan")
        if not abs(b["paud"] - p_rete) <= 2e-4:
            refuse(f"calore, {c}: la scheda audio {b['paud']:.5f} W sul banco del calore, "
                   f"{p_rete:.5f} W dai rail del banco della rete")
        # il bilancio dei secondari: tutto quello che esce dai trasformatori e' nelle voci, a meno
        # dei partitori, delle ESR, dei diodi inversi e delle correnti di riposo (positivi e piccoli)
        res = (b["pt1"] + b["pt2"] - b["cu1"] - b["cu2"] - b["dbr1"] - b["dbr2"] - b["rpre"]
               - b["reg1"] - b["reg2"] - b["dsch"] - b["reg3"] - b["paud"] - b["pvr"])
        if not 0 <= res <= 0.1:
            refuse(f"calore, {c}: il bilancio dei secondari non torna, resto {res:.4f} W")
    ipotesi = [p for p in parts if "(ipotesi)" in p[0]]
    if len(ipotesi) != 2:
        refuse(f"calore: le voci in ipotesi sono {[p[0] for p in ipotesi]}, attese due (il ferro)")
    # la seconda strada di prima: L51b (il micro, la scheda audio di L48b), lo scarto si scrive
    l51 = re.findall(r"^(.+?)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)$",
                     open(vecchio(L51B, "termica", "stima_telaio_l51b.txt")).read(), re.M)
    l51 = {k.strip(): (float(a), float(b), float(c)) for k, a, b, c in l51}
    g51 = re.search(r"gioco minimo del vano chiuso per 60 C nel caso peggiore: ([\d.]+) cm",
                    open(vecchio(L51B, "termica", "stima_telaio_l51b.txt")).read())
    return {"dir": d, "parts": parts, "tot": tot[0] if tot else None,
            "vano": [(g, c, float(p), float(a), float(b), float(t)) for g, c, p, a, b, t in V],
            "gioco": float(gm.group(1)) if gm else None, "p_blk": p_blk, "bench": bench,
            "ipotesi": ipotesi, "car": car, "l51b": l51,
            "gioco_l51b": float(g51.group(1)) if g51 else float("nan")}

# ================================================================ L51b ===
# L'alimentatore (L42b, riscritto in L51b). La prima strada e' la ricorsa del
# 2026-10-09 col carico di oggi (data/2026-10-09/L51b); la seconda, gli stessi
# script col carico di prima (L51b-prima), che deve ridare L47c2a e L47c2b2 byte
# per byte. Ogni deck si rigenera oggi da psu.net e dev'essere quello corso: se
# non lo e', il circuito misurato non e' quello di oggi.

# ngspice esce 0 su tutto questo (limitations #29, #33, #35, #36): il log si
# legge prima dei dati
LOG_GUARD = re.compile(r"error|singular|no such|too many args|transient op|"
                       r"timestep too small|aborted", re.I)
# i percorsi assoluti di un deck (il worktree in cui e' stato scritto) non sono
# il circuito: si tolgono prima del confronto
_ROOTP = re.compile(r"/Users/\S*?/(?=(?:circuits|models|docs|firmware|spice)/)")


def log_pulito(path):
    """Un log di ngspice senza nessuna delle righe che invalidano una corsa."""
    bad = [ln.strip() for ln in open(path, errors="replace") if LOG_GUARD.search(ln)]
    if bad:
        refuse(f"{rel(path)}: il log ha {len(bad)} righe che invalidano la corsa, "
               f"la prima: {bad[0][:80]!r}")
    return not bad


def rows_of(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def stessi_byte(label, a, b):
    # L51c: come stesso_deck(), un file che un generatore non ha scritto perche' ha rifiutato
    # e' un rifiuto, non un'eccezione (il sabotaggio del rele' del selettore di L51a,
    # rieseguito con l'alimentatore nella pagina, cadeva in un FileNotFoundError)
    for x in (a, b):
        if not os.path.isfile(x):
            refuse(f"{label}: {rel(x)} non c'e' (il generatore che lo scrive ha rifiutato?)")
            return False
    with open(a, "rb") as fa, open(b, "rb") as fb:
        if fa.read() != fb.read():
            refuse(f"{label}: {rel(a)} e {rel(b)} non sono uguali byte per byte")
            return False
    return True


def deck_norm(path, swap=()):
    """Le righe di un deck, coi percorsi assoluti ridotti a @/ e le cartelle
    delle ricorse riportate a quelle dei lotti."""
    with open(path) as f:
        text = f.read()
    for a, b in swap:
        text = text.replace(a, b)
    return _ROOTP.sub("@/", text)


def stesso_deck(label, a, b, swap=()):
    # L51b: un generatore che rifiuta non scrive il deck; e' un rifiuto, non un'eccezione
    if not os.path.isfile(a):
        refuse(f"{label}: il deck rigenerato oggi non c'e' (il generatore ha rifiutato)")
        return False
    if deck_norm(a, swap) != deck_norm(b, swap):
        refuse(f"{label}: {rel(a)} non e' {rel(b)} (a meno dei percorsi del worktree): "
               "il circuito corso non e' quello di oggi")
        return False
    return True


def in_tmp(script, files, args, cwd_files=True):
    """Esegue uno script di un lotto su COPIE dei suoi file d'ingresso, in una
    cartella temporanea: alcuni scrivono accanto ai dati (analizza_timer.py,
    analizza_ldr.py), e il generatore non scrive mai nelle cartelle versionate.
    Ritorna (stdout, cartella)."""
    import tempfile
    d = tempfile.mkdtemp(prefix="l42b_")
    for f in files:
        shutil.copy(f, d)
    a = [x.replace("@TMP@", d) for x in args]
    proc = subprocess.run([sys.executable, script] + a, capture_output=True, text=True,
                          cwd=d if cwd_files else REPO)
    if proc.returncode not in (0, 1):
        refuse(f"{rel(script)} {' '.join(args)}: rc {proc.returncode} ({proc.stderr.strip()[-120:]})")
    return proc.stdout, d


def p9_soglie():
    """Le soglie di P9, lette dalla sua riga di REQUIREMENTS.md, non scritte qui."""
    with open(os.path.join(REPO, "docs", "preamp", "REQUIREMENTS.md")) as f:
        row = next((ln for ln in f if ln.startswith("| P9 |")), "")
    pats = {"entro_ms": r"rilascia `MUTE_CMD` entro (\d+) ms",
            "vrelay_ms": r"`VRELAY` resta in tolleranza per ≥ (\d+) ms",
            "margine_ms": r"≥ (\d+) ms di margine",
            "tetto_V": r"\*\*tetto di non-danno\*\* è ([\d,]+) V",
            "obiettivo_mV": r"\*\*obiettivo\*\* è ≤ (\d+) mV",
            "soglia_V": r"sotto \\\|(\d+,\d+) V\\\|"}
    out = {}
    for k, p in pats.items():
        m = re.search(p, row)
        if not m:
            refuse(f"REQUIREMENTS.md, riga di P9: non trovo {k} ({p})")
            out[k] = float("nan")
        else:
            out[k] = float(m.group(1).replace(",", "."))
    return out


def nc028_formula():
    """La catena di NC-028 (finale e diffusore), letta da NONCOMPLIANCE.md: la
    seconda strada dei dB SPL che le tabelle di L30 e L41c scrivono."""
    with open(os.path.join(REPO, "docs", "preamp", "NONCOMPLIANCE.md")) as f:
        m = re.search(r"(\d+) \+ 20·log\((\d+,\d+)·ΔV / (\d+,\d+)\) dB SPL", f.read())
    if not m:
        refuse("NONCOMPLIANCE.md: la formula di NC-028 non si legge")
        return None
    spl, g, v = (float(x.replace(",", ".")) for x in m.groups())
    return {"spl": spl, "g": g, "v1w": v, "db": lambda dv: spl + 20 * math.log10(g * dv / v)}


# ---- potenza, VRELAY, sorvegliante sul lato alimentatore (L41a, ricorsa L42b)
# le colonne di analisi.csv di L41a; la ricorsa ne ha tre in piu' (vrelay_reg e
# la tenuta a J1). Tolleranze della ricorsa col carico di L41a contro L41a:
# 0,5 ms o l'1 % sui tempi, 10 mV sulle tensioni (i regolatori di oggi hanno la
# corrente di riposo per parte, L41b1; L41a caricava 1 mA a tutti).
T_COLS = ("t_off_ms", "t_md_ms", "t_p135_ms", "t_p106_ms", "t_m135_ms", "t_m106_ms",
          "trip_after_135_ms", "vr_hold_ms", "vr80_hold_ms")
V_COLS = ("vplus", "vminus", "vrelay", "v5", "raw_p_min", "raw_m_min_abs", "raw_v_min",
          "vplus_at_off", "vminus_at_off")


def _cella(r, k):
    s = (r.get(k) or "").strip()
    if not s:
        return None
    return (">", float(s[1:])) if s.startswith(">") else ("=", float(s))


def _uguali(k, a, b):
    if a is None or b is None:
        return a is None and b is None
    if a[0] != b[0]:
        return False
    # le tensioni lette ALL'ISTANTE dello scatto ereditano la tolleranza del
    # tempo: il rail scende di 265 mA / 1760 uF ~ 0,15 V/ms, e 0,3 ms sono 50 mV
    tol = (max(0.5, 0.01 * abs(b[1])) if k in T_COLS else
           0.050 if k.endswith("_at_off") else 0.010)
    return abs(a[1] - b[1]) <= tol


def _psu_log(path, r512):
    """I casi di un deck rete / guasti, e R512 com'era in ciascuno: la guardia
    di limitations #34 (ogni caso rimette R512 prima delle sue alterazioni)."""
    casi, cur = [], None
    for ln in open(path, errors="replace"):
        m = re.match(r"@rr512\[resistance\] = (\S+)", ln.strip())
        if m:
            cur = float(m.group(1))
        m = re.match(r"CASO (\S+)", ln.strip())
        if m:
            casi.append((m.group(1), cur))
            cur = None
    for nome, r in casi:
        want = 1e15 if "senza_rivelatore" in nome else r512
        if r is None or abs(r - want) > 1e-6 * want:
            refuse(f"{rel(path)}: nel caso {nome} R512 vale {r}, atteso {want:g} (#34)")
    return [c for c, _ in casi]


def leggi_carico(lot):
    """carico.txt di un lotto: le correnti della scheda audio sul banco e il metodo dei due
    casi di U503 (L51b)."""
    car = {}
    for ln in open(os.path.join(lot, "carico.txt")):
        x = ln.split("#")[0].split()
        if len(x) == 2:
            car[x[0]] = x[1]
    if set(car) != {"i_piu_mA", "i_meno_mA", "resto_mA", "metodo_u503"}:
        refuse(f"{rel(lot)}/carico.txt: chiavi {sorted(car)}")
    return car


def carico_di_oggi(op):
    """L64b: carico.txt di L64b e' quello di tb_op di oggi (8 blocchi, i due rail), il resto di
    VRELAY quello di L48a (51,5 mA), il metodo dei casi di U503 gear (L51b, L58b)."""
    car = leggi_carico(L64B)
    for k, n in (("i_piu_mA", "i(vpp)"), ("i_meno_mA", "i(vmm)")):
        if not abs(float(car.get(k, "nan")) - 8000 * abs(op["rails"].get(n, 0))) <= 1e-3:
            refuse(f"carico.txt di L64b: {k} {car.get(k)}, 8 x {n} di tb_op "
                   f"{8000 * abs(op['rails'].get(n, 0)):.4f}")
    if car.get("resto_mA") != "51.5" or car.get("metodo_u503") != "gear":
        refuse(f"carico.txt di L64b: resto {car.get('resto_mA')} mA (atteso 51,5, L48a), "
               f"metodo {car.get('metodo_u503')}")
    return car


def measure_psu_power():
    """Potenza, VRELAY e guasti sul lato alimentatore (L41a, L42b, L47c2a, L51b), L64b: i banchi
    della rete e dei guasti di genera_tb_psu.py sull'alimentatore di oggi (il temporizzatore a
    comparatori del sorgente, ADR-102; --tss 3.0, l'evento a 3 s), col carico di oggi. Il deck si
    rigenera da psu.net e dev'essere quello corso; R512 caso per caso (#34: R512 e' la meta' di R_MD
    da ADR-094, 110 k); i casi dell'analisi quelli del log. La seconda strada: L51b, da vecchio(),
    ogni scarto si pubblica (il circuito e il carico sono cambiati)."""
    net = open(PSU_NET).read()
    m = re.search(r'\(ref "R512"\)\s*\(value "([\d.]+)k"\)', net)
    r512 = float(m.group(1)) * 1e3 if m else float("nan")
    gen = tool(L64B, "psu", "genera_tb_psu.py")
    rows = {}
    for nome in ("rete", "guasti"):
        dd = ps(L64B, nome)
        deck = os.path.join(dd, f"tb_psu_{nome}.cir")
        log = deck[:-4] + ".log"
        log_pulito(log)
        casi = _psu_log(log, r512)
        _, tmp = in_tmp(gen, [], ["--nome", nome, *PSU_OPZ, "--uscita", "@TMP@"], cwd_files=False)
        stesso_deck(f"deck {nome}", os.path.join(tmp, os.path.basename(deck)), deck, swap=((tmp, dd),))
        rr = rows_of(os.path.join(dd, "analisi.csv"))
        if sorted(r["file"] for r in rr) != sorted(casi):
            refuse(f"{rel(dd)}/analisi.csv: casi {sorted(r['file'] for r in rr)}, il log {sorted(casi)}")
        rows.update({r["file"]: r for r in rr})
    # l'evento e' a 3 s (--tss 3.0): analizza.py ha preso 3.0, e i tempi sono dall'evento
    tl = re.findall(r"alter @venv\[pwl\] = \[ 0 [\d.]+ ([\d.]+) [\d.]+ [\d.]+ 0 1000 0 \]",
                    open(os.path.join(L64B, "rete", "tb_psu_rete.log"), errors="replace").read()
                    + open(os.path.join(L64B, "rete", "tb_psu_rete.cir")).read())
    if not tl or any(abs(float(x) - 3.0) > 1e-9 for x in tl):
        refuse(f"il banco della rete: la rete si perde a {sorted(set(tl))} s, non a 3")
    for c, r in rows.items():
        t = _cella(r, "t_off_ms")
        if t is not None and not 0 < t[1] < 500:
            refuse(f"analisi del banco, {c}: MUTE_CMD a {t[1]} ms dall'evento (analizza.py senza 3.0?)")
    # la seconda strada: L51b (il micro, il carico di prima di L66), ogni colonna che si sposta
    l51 = {}
    for nome in ("rete", "guasti"):
        l51.update({r["file"]: r for r in rows_of(vecchio(L51B, nome, "analisi.csv"))})
    if sorted(l51) != sorted(rows):
        refuse(f"i casi dei banchi: oggi {sorted(rows)}, L51b {sorted(l51)}")
    scarti = []
    for caso, rp in l51.items():
        ro = rows.get(caso, {})
        for k in T_COLS + V_COLS + ("vrelay_reg",):
            if not _uguali(k, _cella(ro, k), _cella(rp, k)):
                scarti.append((caso, k, rp.get(k), ro.get(k)))
    return {"dir": ps(L64B), "oggi": rows, "l51b": l51, "scarti": scarti, "r512": r512}


PSU_PROV = {}


def prov_psu(deck, datadir, note=""):
    """La provenienza di un deck dell'alimentatore: i file inclusi (dagli `.include`) e i
    sottocircuiti comportamentali che il deck definisce. L64b: i modelli del costruttore che il
    deck include (i transistor del comando, il BAV199 al posto del BAS416, ADR-104) si dicono
    per nome; i regolatori e i comparatori sono comportamentali (il comparatore tarato sul
    modello di TI, ADR-103)."""
    incs, subs = [], []
    for ln in open(deck):
        m = re.match(r"^\.include\s+(\S+)", ln.strip(), re.I)
        if m:
            r = _resolve_include(m.group(1))
            if r is None or not os.path.exists(os.path.join(REPO, r)):
                refuse(f"provenienza {rel(deck)}: include non risolvibile {m.group(1)}")
                continue
            incs.append(r)
        m = re.match(r"^\.subckt\s+(\S+)", ln.strip(), re.I)
        if m:
            subs.append(m.group(1))
    if not incs or not subs:
        refuse(f"provenienza {rel(deck)}: include {incs}, sottocircuiti {subs}")
    PSU_PROV[rel(deck)] = (incs, subs)        # L51c: per la sezione della provenienza
    return (f'<p class="prov">Deck <code>{html_escape(rel(deck))}</code>'
            f' &middot; dati <code>{html_escape(rel(datadir))}/</code>{note}<br>'
            f'Inclusi: {", ".join(f"<code>{i}</code>" for i in incs)}'
            f' &middot; comportamentali: <strong>{", ".join(subs)}</strong> &middot; '
            'i regolatori e i comparatori sono modelli dichiarati, il comparatore tarato sul '
            'modello di TI (ADR-103)</p>')


def vecchio(root, *parts):
    """I dati di un lotto di prima, SOLO come seconda strada (L42b per L41a; L51b per L47c2a e
    L47c2b2; L64b per L51b, L54b2, L54b3b, L58b): non passano da ps(), che li rifiuta come prima
    strada."""
    p = os.path.join(root, *parts)
    if not os.path.exists(p):
        raise SystemExit(f"RIFIUTATO: manca {rel(p)}. Nessun file e' stato scritto.")
    return p


# ---- L64b: le sequenze del temporizzatore a comparatori (corri_an.sh, analizza_mc.py) -------
# I casi e i loro nomi per la pagina. I nove casi di L41c (i guasti dell'alimentatore, come in L51b)
SEQ_GUASTI = ("spegnimento_l", "perdita", "perdita_min", "guasto", "guasto_u501", "guasto_u503",
              "guasto_u503_min", "cf_nodelta", "corto_u503")
# il temporizzatore: l'accensione, i buchi, la ritenuta (L54b1, L54b3b)
SEQ_TIMER = ("accensione", "fredda", "rilascio", "inserimento", "buco20", "buco200",
             "ritenuta_frontale", "accensione_u501", "fredda_u501")
SEQ_LAB = {"spegnimento_l": "spegnimento dal frontale", "perdita": "perdita di rete",
           "perdita_min": "idem, Δ all&rsquo;angolo minimo", "guasto": "U502 (rail −) spento",
           "guasto_u501": "U501 (rail +) spento", "guasto_u503": "U503 (<code>VRELAY_REG</code>) spento",
           "guasto_u503_min": "idem, angolo minimo", "cf_nodelta": "controfattuale senza Δ",
           "corto_u503": "corto dell&rsquo;uscita di U503",
           "accensione": "accensione dallo standby", "fredda": "accensione a freddo",
           "rilascio": "il frontale rilasciato subito", "inserimento": "il mute dal frontale",
           "buco20": "un buco di rete di 20 ms", "buco200": "un buco di 200 ms",
           "ritenuta_frontale": "la ritenuta col frontale", "accensione_u501": "accensione con U501 spento",
           "fredda_u501": "idem, a freddo"}


def lista_seq():
    """Le corse di lista_l64b.txt (e lista_consumo.txt): {(etichetta, caso): [opzioni]}."""
    out = {}
    for f in ("lista_l64b.txt", "lista_consumo.txt"):
        for ln in open(os.path.join(L64B, f)):
            x = ln.split()
            if x:
                if x[2] != "sorgente":
                    refuse(f"{f}: {x[0]} col temporizzatore {x[2]}")
                out[(x[1], x[0])] = x[3:]
    return out


def measure_seq():
    """L64b: le sequenze sull'alimentatore di oggi. Ogni corsa di lista_l64b.txt ha il suo ok.txt
    e un log pulito, e il suo deck si rigenera da psu.net (genera_tb_psu.py di L64b con le opzioni
    della riga) uguale a quello corso. an_l64b.csv ha una riga per corsa. La seconda strada:
    script/confronta.py rieseguito ridà confronto_seq.csv, con zero celle fuori dalla tolleranza
    (contro L58b sullo stesso circuito, contro L54b3b e L58b prima della coppia con la tolleranza
    della variante) e i deck di oggi uguali a quelli di L58b a meno del carico."""
    corse = lista_seq()
    gen = tool(L64B, "psu", "genera_tb_psu.py")
    for (lab, c), opz in sorted(corse.items()):
        cd = ps(L64B, "seq", lab, c)
        if not os.path.isfile(os.path.join(cd, "ok.txt")):
            refuse(f"{rel(cd)}: la corsa non ha ok.txt")
            continue
        deck = os.path.join(cd, f"tb_psu_seq_{c}_g1.cir")
        log_pulito(deck[:-4] + ".log")
        ang = "min" if c.endswith("_min") else "nom"
        _, tmp = in_tmp(gen, [], ["--uscita", "@TMP@", "--nome", "seq", "--caso", c, "--giro", "1",
                                  "--angolo", ang, "--timer", "sorgente", *opz], cwd_files=False)
        stesso_deck(f"sequenza {lab}/{c}", os.path.join(tmp, os.path.basename(deck)), deck,
                    swap=((tmp, cd),))
    an = {r["caso"]: r for r in rows_of(ps(L64B, "an_l64b.csv"))}
    attese = sorted(f"{lab}/{c}" for lab, c in corse if not lab.startswith("consumo"))
    if sorted(an) != attese:
        refuse(f"an_l64b.csv: {len(an)} righe, attese le {len(attese)} corse di lista_l64b.txt")
    for k, r in an.items():
        if r.get("esito") != "letto":
            refuse(f"an_l64b.csv, {k}: esito {r.get('esito')}")
    return {"dir": ps(L64B, "seq"), "an": an, "corse": corse, "l2": seconda_seq()}


def seconda_seq():
    """La seconda strada delle sequenze: confronta.py su una COPIA dei dati (scrive
    confronto_seq.csv accanto a se'), il suo confronto uguale a quello versionato, e zero celle
    fuori dalla tolleranza. Il riassunto si legge dalla sua stampa."""
    import tempfile
    # la struttura che confronta.py si aspetta: <dati>/<giorno>/<lotto>; i dati di oggi copiati, le
    # corse e i lotti di prima collegati (si leggono soltanto)
    data = os.path.join(tempfile.mkdtemp(prefix="l64b_"), "data")
    L = os.path.join(data, os.path.basename(os.path.dirname(L64B)), "L64b")
    os.makedirs(os.path.join(L, "script"))
    for f in ("an_l64b.csv", "mappa.csv"):
        shutil.copy(os.path.join(L64B, f), L)
    shutil.copy(os.path.join(L64B, "script", "confronta.py"), os.path.join(L, "script"))
    os.symlink(os.path.join(L64B, "seq"), os.path.join(L, "seq"))
    for lot in (L58B, L54B3B):
        day = os.path.join(data, os.path.basename(os.path.dirname(lot)))
        os.makedirs(day, exist_ok=True)
        os.symlink(lot, os.path.join(day, os.path.basename(lot)))
    proc = subprocess.run([sys.executable, "-I", os.path.join(L, "script", "confronta.py")],
                          capture_output=True, text=True)
    stessi_byte("confronta.py rieseguito", os.path.join(L, "confronto_seq.csv"),
                ps(L64B, "confronto_seq.csv"))
    m = re.search(r"(\d+) righe dei lotti, (\d+) celle confrontate: (\d+) identiche, (\d+) entro la "
                  r"tolleranza, (\d+) fuori", proc.stdout)
    md = re.search(r"deck di oggi contro L58b: (\d+) righe di L58b, (\d+) diversi oltre il carico",
                   proc.stdout)
    if proc.returncode != 0 or not m or not md or int(m.group(5)) or int(md.group(2)):
        refuse(f"confronta.py: rc {proc.returncode}, {proc.stdout.strip()[-300:]!r}")
        return {}
    n = {k: int(v) for k, v in zip(("righe", "celle", "identiche", "entro", "fuori"), m.groups())}
    n["deck_l58b"] = int(md.group(1))
    # le celle diverse, per la pagina: dal CSV versionato
    n["diverse"] = rows_of(ps(L64B, "confronto_seq.csv"))
    if len(n["diverse"]) != n["celle"] - n["identiche"]:
        refuse(f"confronto_seq.csv: {len(n['diverse'])} righe, {n['celle'] - n['identiche']} celle diverse")
    return n


def measure_censimento():
    """Lo standby a regime e le bobine del mute (psu/censimento.py di L58b, sulle corse di oggi):
    censimento_psu.csv ha una riga per corsa di seq/oggi; contro L58b (censimento_psu.csv, lo
    stesso circuito salvo la coppia) le righe comuni uguali alla cifra stampata o di un'unita'."""
    rr = {r["caso"]: r for r in rows_of(ps(L64B, "censimento_psu.csv"))}
    oggi = sorted(f"oggi/{c}" for lab, c in lista_seq() if lab == "oggi")
    if sorted(rr) != oggi:
        refuse(f"censimento_psu.csv: {len(rr)} righe, {len(oggi)} corse in seq/oggi")
    l58 = {r["caso"].split("/", 1)[1]: r for r in rows_of(vecchio(L58B, "censimento_psu.csv"))
           if r["caso"].startswith(("l58b/", "l58b_base/"))}
    scarti = []
    for c, rp in l58.items():
        ro = rr.get(f"oggi/{c}")
        if ro is None:
            continue
        for k, v in rp.items():
            if k in ("caso",) or ro.get(k) == v:
                continue
            try:
                d = abs(float(ro.get(k)) - float(v))
            except (TypeError, ValueError):
                d = float("inf")
            tol = 0.2 + 1e-9 if k.endswith("_ms") else 0.002 + 1e-9
            if d > tol:
                scarti.append((c, k, v, ro.get(k)))
    for c, k, a, b in scarti:
        refuse(f"censimento, {c}: {k} {b} oggi, {a} in L58b")
    return {"rows": rr, "l58b": l58}


def measure_consumo():
    """Lo standby da T2 (psu/potenza_t2.py di L54a sulle corse con --sonda-t2, 2,5-3,0 s, L54b2):
    consumo.txt, tre righe (rete -10 / nominale / +10 %). La seconda strada: L54b2 (116,14 / 130,08 /
    144,21 mW, il sorgente di prima di ADR-104, 105, 110), scarto pubblicato."""
    out = {}
    if not os.path.isfile(ps(L64B, "consumo.txt")):
        refuse(f"manca {rel(ps(L64B, 'consumo.txt'))}: lo standby non e' stato misurato")
        return {**{k: {"t2": float("nan"), "t1": float("nan")} for k in ("m10", "nom", "p10")},
                "l54b2": (float("nan"),) * 3}
    righe = [ln for ln in open(ps(L64B, "consumo.txt")) if ln.strip()]
    if len(righe) != 3:
        refuse(f"consumo.txt: {len(righe)} righe, attese tre (le tre reti, in quest'ordine)")
    for ln, (r, lab) in zip(righe, (("consumo", "nom"), ("consumo_m10", "m10"), ("consumo_p10", "p10"))):
        m = re.match(r"tb_psu_seq_accensione_g1_out\.txt 2\.500-3\.000 s: T2 ([\d.]+) mW, T1 ([\d.]+) mW", ln)
        if not m:
            refuse(f"consumo.txt: la riga di {r} non si legge: {ln.strip()!r}")
            continue
        out[lab] = {"t2": float(m.group(1)), "t1": float(m.group(2))}
        cd = ps(L64B, "seq", r, "accensione")
        log_pulito(os.path.join(cd, "tb_psu_seq_accensione_g1.log"))
        if "--sonda-t2" not in open(os.path.join(cd, "ok.txt")).read():
            refuse(f"{rel(cd)}: la corsa dello standby non ha --sonda-t2")
    sb = re.search(r"\*\*([\d,]+) / ([\d,]+) / ([\d,]+) mW\*\*, lo stesso di L54b1",
                   open(vecchio(L54B2, "README.md")).read())
    if not sb:
        refuse("README di L54b2: lo standby non si legge")
    out["l54b2"] = tuple(float(x.replace(",", ".")) for x in sb.groups()) if sb else (float("nan"),) * 3
    return out


def soglie_timer():
    """Le soglie dei criteri di L54b3b, lette dalle decisioni che le scrivono: K501 dopo il permissivo
    e il permissivo dopo il mute (ADR-105), la musica dopo un buco di 20 ms (ADR-104), la base della
    ritenuta (ADR-103)."""
    t105 = open(next(os.path.join(REPO, "docs", "preamp", "decisions", f) for f in
                     os.listdir(os.path.join(REPO, "docs", "preamp", "decisions"))
                     if f.startswith("ADR-105-"))).read()
    t104 = open(next(os.path.join(REPO, "docs", "preamp", "decisions", f) for f in
                     os.listdir(os.path.join(REPO, "docs", "preamp", "decisions"))
                     if f.startswith("ADR-104-"))).read()
    t103 = open(next(os.path.join(REPO, "docs", "preamp", "decisions", f) for f in
                     os.listdir(os.path.join(REPO, "docs", "preamp", "decisions"))
                     if f.startswith("ADR-103-"))).read()
    pats = {"k501": (t105, r"K501 dopo il permissivo \(≥ (\d+) ms\)"),
            "perm": (t105, r"il permissivo dopo il mute \(≥ (\d+,\d) ms\)"),
            "mus": (t104, r"la musica dopo un buco di 20 ms \(≥ (\d+) ms\)"),
            "base": (t103, r"la base dell'NPN della ritenuta ≤ (\d,\d+) V")}
    out = {}
    for k, (t, p) in pats.items():
        m = re.search(p, t)
        if not m:
            refuse(f"la soglia {k} non si legge ({p})")
        out[k] = float(m.group(1).replace(",", ".")) if m else float("nan")
    return out


def _num(r, k):
    s = (r.get(k) or "").strip()
    return float(s) if s else None


def verdetti_timer(an, s):
    """I criteri di L54b3b (il suo README, «I criteri, scritti prima delle corse») sulle corse di
    oggi, alle tre reti: (1) il permissivo >= s["perm"] dopo il mute nello spegnimento, nella perdita
    e nel guasto (C2 e C3 veri; nel guasto la ritenuta scattata e K501 aperto); (2) la musica >=
    s["mus"] dopo la rete in un buco di 20 ms, senza ritenuta e con un solo ritorno della musica; (3)
    K501 >= s["k501"] dopo il permissivo nello spegnimento dal frontale; (4) all'accensione la
    ritenuta armata dopo l'alimentazione buona, che non scatta, la base <= s["base"], la musica alla
    fine; con U501 spento all'accensione la ritenuta scatta e K501 si apre. Una riga per criterio e
    corsa: (criterio, corsa, valore, soglia, esito)."""
    out = []

    def r_(k):
        r = an.get(k)
        if r is None:
            refuse(f"an_l64b.csv: manca {k}")
        return r or {}
    for suf in ("", "_m10", "_p10"):
        for c in ("spegnimento_l", "perdita", "guasto"):
            k = f"oggi{suf}/{c}"
            if k not in an:
                continue
            r = r_(k)
            v = _num(r, "d_perm_ms")
            ok = v is not None and v >= s["perm"] and r["C2"] == "1" and r["C3"] == "1"
            if c == "guasto":
                ok = ok and r["ritenuta"] == "1" and r["k501_end"] == "0"
            out.append(("perm", k, v, s["perm"], ok))
        r = r_(f"oggi{suf}/buco20")
        v = _num(r, "dmus_ms")
        out.append(("mus", f"oggi{suf}/buco20", v, s["mus"],
                    v is not None and v >= s["mus"] and r["ritenuta"] == "0" and r["n_su"] == "1"))
    r = r_("oggi/spegnimento_l")
    v = _num(r, "k_perm_ms")
    out.append(("k501", "oggi/spegnimento_l", v, s["k501"], v is not None and v >= s["k501"]))
    for k in ("oggi/accensione", "oggi_m10/accensione", "oggi_p10/accensione", "oggi/fredda"):
        r = r_(k)
        a, b = _num(r, "arm_pg_ms"), _num(r, "bn_max")
        out.append(("arm", k, a, 0.0, (a is None or a > 0) and r["ritenuta"] == "0" and r["mus_end"] == "1"))
        out.append(("base", k, b, s["base"], b is not None and b <= s["base"] and r["ritenuta"] == "0"))
    for k in ("oggi/accensione_u501", "oggi/fredda_u501"):
        r = r_(k)
        out.append(("u501", k, None, None, r["ritenuta"] == "1" and r["k501_end"] == "0"))
    return out


# le coppie (guasto latente, evento) della coppia del mute e dello standby (modi.py di L58b): il caso
# sano dello stesso evento contro cui si legge
EVENTI_DIAG = {"accs": "accensione", "freds": "fredda", "guas": "guasto", "b20s": "buco20",
               "perds": "perdita", "spls": "spegnimento_l", "u501s": "accensione_u501",
               "inss": "inserimento"}
DIAG_COL = ("musica_TE", "C2", "C3", "r41", "s41", "t_jack_ms", "t_gain_ms", "t_k501_ms", "t_mus_ms",
            "mus_end", "k501_end", "ritenuta")


def measure_diag(an, cs):
    """L'autodiagnosi (ADR-110, DIAGNOSI.md) sul circuito di oggi: ogni guasto latente della coppia
    del mute (lista_s1m di L58b, coi nomi di oggi) e dello standby (lista_l58b) contro il caso sano
    dello stesso evento. Per ogni (guasto, evento) le colonne di DIAG_COL che si spostano oltre
    l'unita' della cifra (0,1 ms; le bandierine uguali), e dal censimento le bobine del mute
    all'accensione e lo standby a regime."""
    righe = []
    for k, r in sorted(an.items()):
        lab, c = k.split("/", 1)
        m = re.match(r"^(f_\w+?)_(accs|freds|guas|b20s|perds|spls|u501s|inss)$", c)
        if not m or not c.startswith(("f_q50", "f_rq50", "f_r5", "f_u508b")):
            continue
        sano = an.get(f"{lab}/{EVENTI_DIAG[m.group(2)]}")
        if sano is None:
            refuse(f"autodiagnosi, {k}: manca il caso sano {lab}/{EVENTI_DIAG[m.group(2)]}")
            continue
        diff = []
        for col in DIAG_COL:
            a, b = (r.get(col) or "").strip(), (sano.get(col) or "").strip()
            if a == b:
                continue
            if col.endswith("_ms") and a and b and abs(float(a) - float(b)) <= 0.1 + 1e-9:
                continue
            diff.append((col, a, b))
        righe.append({"caso": k, "guasto": m.group(1), "evento": m.group(2), "lab": lab,
                      "diff": diff, "cens": cs["rows"].get(k, {})})
    return righe


def measure_chain():
    """Spegnimento e guasti al jack, L64b: la catena di L54b2 (il ponte dalle sequenze di oggi,
    il deck di V2 --matrice l41c, 18 corse per rete) sulla scheda audio di oggi, alle tre reti. Il
    deck si rigenera dal sorgente di oggi e dal ponte; tabella.py si riesegue sull'analisi; i dB SPL
    si ricalcolano con la catena di NC-028. La seconda strada: le tabelle di L54b2 (vecchio()), lo
    scarto pubblicato (la scheda audio di L66 e l'alimentatore di ADR-104, 105, 110)."""
    f = nc028_formula()
    gen_v2 = tool(DATAROOT, "2026-09-23", "L29c", "deck", "genera_tb_v2_casopeggiore.py")
    out = {}
    manca = [p for r in ("nom", "m10", "p10") for p in (
        ps(L64B, f"tabella_{r}.csv"), ps(L64B, "corse", r, "analisi.csv"), ps(L64B, "corse", r, "fallite.txt"),
        ps(L64B, "corse", r, "tempi.txt"), ps(L64B, "deck", f"tb_v2_l41c_{r}.cir")) if not os.path.isfile(p)]
    if manca:
        refuse(f"la catena al jack: mancano {len(manca)} file, il primo {rel(manca[0])}")
        return {"rows": [], "m10": [], "p10": [], "l54b2": {"nom": [], "m10": [], "p10": []}, "f": f}
    for r in ("nom", "m10", "p10"):
        d = ps(L64B, "corse", r)
        t = ps(L64B, f"tabella_{r}.csv")
        ins = [os.path.join(d, "analisi.csv"), os.path.join(d, "fallite.txt")]
        if open(ins[1]).read().strip():
            refuse(f"{rel(ins[1])}: corse fallite")
        tempi = [ln.split() for ln in open(os.path.join(d, "tempi.txt")) if ln.strip()]
        if len(tempi) != 18 or any(x[1] != "rc=0" for x in tempi):
            refuse(f"{rel(d)}/tempi.txt: {len(tempi)} corse, non tutte rc=0")
        _, tmp = in_tmp(tool(L64B, "script", "tabella.py"), ins,
                        [os.path.basename(ins[0]), os.path.basename(ins[1]), "tabella.csv"])
        stessi_byte(f"catena {r}: tabella.py rieseguito", os.path.join(tmp, "tabella.csv"), t)
        _, tmp = in_tmp(gen_v2, [], ["--matrice", "l41c", "--ponte", ps(L64B, "ponte", r),
                                     "--uscita", f"@TMP@/tb_v2_l41c_{r}.cir"], cwd_files=False)
        stessi_byte(f"catena {r}: il deck di V2 rigenerato oggi", os.path.join(tmp, f"tb_v2_l41c_{r}.cir"),
                    ps(L64B, "deck", f"tb_v2_l41c_{r}.cir"))
        rows = rows_of(t)
        for x in rows:
            v, db = x.get("picco_V", "-"), x.get("dB_SPL_picco_1m", "-")
            if v in ("-", "") or f is None:
                continue
            if abs(f["db"](float(v)) - float(db)) > 0.05:
                refuse(f"catena {r}, {x.get('caso')}: {db} dB SPL in tabella, la formula di NC-028 "
                       f"da' {f['db'](float(v)):.2f}")
        out[r] = rows
        out[f"l54b2_{r}"] = rows_of(vecchio(L54B2, f"tabella_{r}.csv"))
        if [x["caso"] for x in out[f"l54b2_{r}"]] != [x["caso"] for x in rows]:
            refuse(f"catena {r}: i casi non sono quelli di L54b2")
    return {"rows": out["nom"], "m10": out["m10"], "p10": out["p10"],
            "l54b2": {r: out[f"l54b2_{r}"] for r in ("nom", "m10", "p10")}, "f": f}

def mcol(m, alt=False):
    return {"0db": (sp.C_0DB, sp.C_0DB_ALT), "3db": (sp.C_3DB, sp.C_3DB_ALT),
            "10db": (sp.C_10DB, sp.C_10DB_ALT)}[m][1 if alt else 0]


def fig_response(resp):
    W, H = 900, 440
    ax = sp.Axes(72, 46, W - 130, H - 160, (10, 100000), (-1, 11),
                 xlabel="frequenza [Hz]", ylabel="|v(JACK)| [dB]",
                 title="Risposta in frequenza, i tre modi di guadagno")
    for m in MODES:
        ax.line(resp[(m, "1.5")]["f"], resp[(m, "1.5")]["gdb"], mcol(m),
                f"{MLAB[m]} · sorgente 1,5 Ω", None)
        ax.line(resp[(m, "2500")]["f"], resp[(m, "2500")]["gdb"], mcol(m, True),
                f"{MLAB[m]} · sorgente 2500 Ω", "5,3")
    ax.vline(20000)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L51a tb_ac_*.csv · linea verticale = 20 kHz")


def fig_response_adr014(resp):
    W, H = 900, 420
    ax = sp.Axes(72, 46, W - 130, H - 160, (10, 100000), (-0.15, 0.03),
                 xlabel="frequenza [Hz]", ylabel="scostamento da 1 kHz [dB]",
                 title="ADR-014: la risposta non deve muoversi con la manopola del volume")
    for m in MODES:
        for rs, alt, dash in (("1.5", False, None), ("2500", True, "5,3")):
            r = resp[(m, rs)]
            ax.line(r["f"], [g - r["g1k"] for g in r["gdb"]], mcol(m, alt),
                    f"{MLAB[m]} · {rs.replace('.', ',')} Ω", dash)
    ax.vline(20000)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Normalizzato a 1 kHz: l'impedenza della sorgente "
                       "non sposta la banda passante.")


def fig_v1(v1):
    W, H = 900, 460
    ax = sp.Axes(72, 46, W - 130, H - 160, (0, 4.8), (20, 110), xlog=False,
                 xlabel="capacità del cavo [nF]", ylabel="margine di fase [gradi]",
                 title="V1, blocco B: il margine contro la capacità del cavo (ADR-024)")
    for m in MODES:
        b = v1["B"][m]
        w = b["w"]
        xs, ys = b["curve"]
        ax.line([x * 1e9 for x in xs], ys, mcol(m),
                f"{MLAB[m]} · al jack · {lab_c(w['rsrc'])}, {lab_c(w['rload'])}", None)
        xs, ys = b["curve_n"]
        ax.line([x * 1e9 for x in xs], ys, mcol(m, True),
                f"{MLAB[m]} · sul nodo (informazione)", "5,3")
        ax.annot(capval(w["cprobe"]) * 1e9, b["min"], f"min {fx(b['min'])}°", 8, -8)
    ax.hline(PM_MIN, sp.C_REQ, "soglia 60° (ADR-019)", left=True)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L51a tb_loop_margini.csv · il verdetto è il "
                       "minimo della curva al jack, non il valore a 4,7 nF")


def fig_loop(v1):
    W, H = 900, 620
    xlim = (1, 1e8)
    axm = sp.Axes(72, 46, W - 130, 230, xlim, (-40, 80), ylabel="|T| [dB]",
                  title="Guadagno d'anello del blocco B alla capacità del minimo "
                        "(sorgente 2,5 kΩ, carico 100 kΩ)")
    axp = sp.Axes(72, 330, W - 130, 190, xlim, (0, 180),
                  xlabel="frequenza [Hz]", ylabel="fase di T [gradi]")
    for m in MODES:
        b = v1["bode"][m]
        lab = f"{MLAB[m]} · cavo {lab_c(b['C'])}"
        axm.line(b["f"], b["tdb"], mcol(m), lab, None)
        axp.line(b["f"], b["tph"], mcol(m), None, None)
        axp.annot(b["fcross"], b["pmarg"], f"{fx(b['pmarg'])}°".replace("&minus;", "-"), 8, -8)
    axm.hline(0, sp.C_REQ, "0 dB")
    body = (axm.render(show_xlabels=False) + "\n" + axp.render() + "\n" +
            axm.legend(80, H - 42, cols=3, colw=270))
    return sp.document(W, H, body, "Dati: L51a tb_loop_att2k5_*.csv · margine = |fase| "
                       "dove |T| attraversa 0 dB (G2 è l'ingresso invertente)")


def fig_psrr(psrr):
    W, H = 900, 440
    ax = sp.Axes(72, 46, W - 130, H - 160, (20, 200000), (0, 120),
                 xlabel="frequenza [Hz]", ylabel="PSRR [dB] — più grande è meglio",
                 title="Reiezione dell'alimentazione, i due rail nei tre modi")
    for m in MODES:
        ax.line(psrr[("p", m)]["f"], psrr[("p", m)]["p"], mcol(m), f"rail + · {MLAB[m]}", None)
        ax.line(psrr[("m", m)]["f"], psrr[("m", m)]["p"], mcol(m, True), f"rail − · {MLAB[m]}", "5,3")
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L51a tb_zout_psrr_noise_psrr*.csv · 1 V AC in "
                       "serie a ciascun rail, ingresso silenziato")


def fig_zout(z):
    W, H = 900, 450
    # L37: da 0,01 Ω, perche' il nodo OUT a sorgente spenta sta a ~0,04 Ω (NC-033)
    ax = sp.Axes(72, 46, W - 130, H - 160, (20, 200000), (0.01, 5000), ylog=True,
                 xlabel="frequenza [Hz]", ylabel="|Z| [Ω]",
                 title="Impedenza d'uscita: al jack e al nodo OUT")
    for m in MODES:
        ax.line(z[m]["f"], z[m]["z"], mcol(m), f"al jack · {MLAB[m]}", None)
        ax.line(z[m]["f"], z[m]["za"], mcol(m, True), f"al nodo OUT · {MLAB[m]}", "5,3")
    ax.hline(100, sp.C_REQ, "E4: < 100 Ω")
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=270)
    return sp.document(W, H, body, "Dati: L51a tb_zout_psrr_noise_zout_*.csv, sorgente spenta · "
                       "la salita sotto 200 Hz è la reattanza del 4,7 µF, non lo stadio")


def fig_headroom(hr):
    W, H = 900, 430
    ax = sp.Axes(72, 46, W - 130, H - 140, (-14, 14), (-15, 15), xlog=False,
                 xlabel="v(IN) [V]", ylabel="v(OUT) [V]",
                 title="Escursione in continua e saturazione, i tre modi")
    for m in MODES:
        r = hr["modes"][m]
        ax.line(r["vin"], r["vout"], mcol(m), MLAB[m], None)
        ax.annot(r["vi_hi"], r["vo_hi"],
                 f"limite M1 {fx(r['lin'])} V RMS".replace("&minus;", "-"),
                 -8 if m == "10db" else 8, -8 if m == "10db" else 16)
    body = ax.render() + "\n" + ax.legend(80, ax.y0 + ax.h + 58, cols=3, colw=175)
    return sp.document(W, H, body, "Dati: L51a tb_dc_headroom*.csv · spazzata in continua; "
                       "il punto segna il bordo positivo della finestra all'1 %")


def fig_counterfactual(cf, hr):
    """I tre stati del controfattuale: barre, non curve. Il valore di B va
    VISTO accanto ai rail: e' tutto il senso della meta' falsificabile di V2."""
    W, H = 900, 440
    ax = sp.Axes(150, 52, W - 300, H - 130, (0.4, 3.6), (-18, 18), xlog=False,
                 ylabel="v(OUT) [V]",
                 title="Controfattuale ADR-004: cosa farebbe il relè nel ramo sbagliato",
                 xticks=[(1, "A · contatto chiuso"), (2, "B · contatto APERTO"),
                         (3, "C · richiuso")])
    colors = [sp.C_0DB, sp.C_10DB, sp.C_0DB]
    for i, (r, col) in enumerate(zip(cf["rows"], colors), start=1):
        ax.bar(i, 0.0, r["vout"], col)
        dy = 18 if r["vout"] < 0 else -12
        ax.annot(i, r["vout"], f'{r["vout"]:.4f} V'.replace(".", ","), 12, dy)
    ax.hline(15, sp.C_REQ, "rail +15 V")
    ax.hline(-15, sp.C_REQ, "rail −15 V")
    vmin = hr["modes"]["0db"]["vout_min"]
    ax.hline(vmin, sp.C_10DB_ALT, "saturazione dello stadio a 0 dB, "
             + f"{vmin:.4f}".replace(".", ",") + " V", "2,3", left=True)
    ax.hline(0, sp.C_AXIS, None, "1,3")
    return sp.document(W, H, ax.render(), "Dati: L51a tb_switch_v2_counterfactual*.csv · "
                       "con R_f aperto l'anello è rotto e l'uscita si appoggia al rail")


# L51a: il mute taglia (ADR-062), non c'e' piu' un profilo da disegnare: la sezione ha la
# tabella del clic. fig_mute (il profilo v4 di L42a) e' tolta.
# L51b: neanche il pilota delle LDR c'e' piu' (ADR-062): fig_ldr_drive (L42b) e' tolta.

# ----------------------------------------------------------------- pagina --
CSS = """
:root{
  --paper:#f6f7f9; --surface:#ffffff; --ink:#161a1f; --muted:#5b6472;
  --rule:#d8dde4; --rule-soft:#e9edf2; --accent:#1f5c99; --accent2:#a8452a;
  --ok:#1c6b3c; --warn-ink:#7a4a12; --warn-bg:#fdf4e6; --warn-rule:#c98b2e;
  --chip:#eef1f5; --plate:#ffffff;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#101317; --surface:#181c22; --ink:#e6e9ed; --muted:#98a2b0;
  --rule:#2a3038; --rule-soft:#22272e; --accent:#7fb3e0; --accent2:#e09880;
  --ok:#5fbb85; --warn-ink:#e6b878; --warn-bg:#23200f; --warn-rule:#8a6a28;
  --chip:#20252c; --plate:#ffffff;
}}
:root[data-theme="dark"]{
  --paper:#101317; --surface:#181c22; --ink:#e6e9ed; --muted:#98a2b0;
  --rule:#2a3038; --rule-soft:#22272e; --accent:#7fb3e0; --accent2:#e09880;
  --ok:#5fbb85; --warn-ink:#e6b878; --warn-bg:#23200f; --warn-rule:#8a6a28;
  --chip:#20252c; --plate:#ffffff;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Sans","Helvetica Neue",Helvetica,Arial,sans-serif;
  font-size:16px; line-height:1.62; font-weight:400;
}
.wrap{max-width:1000px;margin:0 auto;padding:40px 24px 96px}
.col{max-width:68ch}

.eyebrow{
  font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:11.5px; letter-spacing:.14em; text-transform:uppercase;
  color:var(--muted); margin:0 0 10px;
}
h1{
  font-size:clamp(28px,4.2vw,40px); line-height:1.12; letter-spacing:-.021em;
  font-weight:600; margin:0 0 10px; text-wrap:balance;
}
.lede{font-size:18px; color:var(--muted); margin:0 0 4px; max-width:60ch}

h2{
  font-size:22px; font-weight:600; letter-spacing:-.012em; line-height:1.25;
  margin:64px 0 14px; padding-top:20px; border-top:1px solid var(--rule);
  display:flex; gap:14px; align-items:baseline; text-wrap:balance;
}
h2 .secno{
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:13px; font-weight:500; color:var(--accent);
  letter-spacing:.04em; flex:none; padding-top:2px;
}
h3{font-size:16.5px;font-weight:600;margin:30px 0 8px;letter-spacing:-.008em}
p{margin:12px 0;max-width:68ch}
ul{margin:12px 0;padding-left:20px;max-width:68ch}
li{margin:9px 0}
strong{font-weight:600}
em{font-style:italic}

code,.mono{
  font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:.86em;
}
code{background:var(--chip); padding:1.5px 5px; border-radius:3px;
  border:1px solid var(--rule-soft);}

/* Tavole grafiche: lastre su bianco, come in un datasheet. Gli SVG sono
   file versionati a parte e non possono leggere i token del tema, quindi
   stanno su fondo bianco in entrambi i temi - scelta, non svista. */
.plate{
  background:var(--plate); border:1px solid var(--rule); border-radius:3px;
  padding:8px; margin:20px 0; overflow-x:auto;
}
.plate img,.plate svg{display:block;max-width:100%;height:auto;margin:0 auto}

.tablewrap{overflow-x:auto;margin:18px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
caption{
  caption-side:top; text-align:left; color:var(--muted); padding-bottom:8px;
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:11.5px; letter-spacing:.08em; text-transform:uppercase;
}
th,td{
  border-bottom:1px solid var(--rule-soft); padding:8px 14px 8px 0;
  text-align:left; white-space:nowrap; vertical-align:baseline;
}
th{
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
  font-weight:500; color:var(--muted); border-bottom:1px solid var(--rule);
}
tbody tr:last-child td{border-bottom:1px solid var(--rule)}
td.num{
  text-align:right; font-variant-numeric:tabular-nums;
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace; font-size:13px;
}
th.num{text-align:right}

/* Quadro sinottico: i numeri di testa, non tessere giganti. */
.synopsis{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:0; margin:26px 0 6px; border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule);
}
.synopsis div{padding:14px 18px 14px 0}
.synopsis dt{
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  font-size:11px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); margin:0 0 5px;
}
.synopsis dd{
  margin:0; font-size:21px; font-weight:600; letter-spacing:-.015em;
  font-variant-numeric:tabular-nums;
}
.synopsis dd .u{display:block;font-size:12.5px;font-weight:400;color:var(--muted);
  letter-spacing:0;line-height:1.4;margin-top:2px}

.note{
  background:var(--warn-bg); border-left:3px solid var(--warn-rule);
  padding:14px 18px; margin:22px 0; max-width:68ch;
}
.note strong{color:var(--warn-ink)}

/* Provenienza sotto ogni titolo di sezione: deck, dati, modelli. */
.prov{
  color:var(--muted); font-size:12.5px; line-height:1.55; max-width:none;
  margin:4px 0 16px; padding-left:10px; border-left:2px solid var(--rule);
}
.prov code{font-size:.92em}

nav.toc{margin:26px 0 0;border-top:1px solid var(--rule);padding-top:16px}
nav.toc ol{
  list-style:none; margin:0; padding:0; max-width:none;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  gap:2px 26px; counter-reset:toc;
}
nav.toc li{margin:0;counter-increment:toc}
nav.toc a{
  color:var(--ink); text-decoration:none; display:block; padding:4px 0;
  border-bottom:1px solid transparent; font-size:14.5px;
}
nav.toc a::before{
  content:attr(data-n) "  ";
  font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  color:var(--accent); font-size:12px;
}
nav.toc a:hover{border-bottom-color:var(--rule)}
a{color:var(--accent)}
a:focus-visible,nav.toc a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.ok{color:var(--ok);font-weight:600}
.no{color:var(--accent2);font-weight:600}
.na{color:var(--muted)}
.meta{color:var(--muted);font-size:13.5px;max-width:68ch}
hr.end{border:0;border-top:1px solid var(--rule);margin:56px 0 0}
@media (max-width:640px){
  .wrap{padding:28px 16px 72px}
  h2{flex-direction:column;gap:2px}
}
"""


def html_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# L42d: il PRB e' la sezione 0, le appendici sono A e B. L51a: ogni sezione dice a
# quale parte appartiene (PARTI); la pagina ha solo quelle delle parti rigenerate, e i
# numeri si contano su quelle. Il testo cita le sezioni con secno(), mai a mano.
SECTIONS_TUTTE = (
    ("s0", "Il contratto: il Product Requirements Book", "audio"),
    ("s1", "Il blocco di guadagno", "audio"), ("s2", "Il preamplificatore intero", "audio"),
    ("ssel", "Il selettore d&rsquo;ingresso: F1", "audio"),
    ("slim", "Il limitatore d&rsquo;ingresso", "audio"),
    ("s3", "Punti di lavoro", "audio"), ("s4", "Risposta in frequenza", "audio"),
    ("s5", "Stabilità: la matrice V1", "audio"),
    ("s6", "Il trim e l&rsquo;impedenza d&rsquo;ingresso", "audio"),
    ("svol", "Il volume col bilanciamento", "audio"),
    ("s7", "Rumore in uscita", "audio"), ("s8", "Escursione e headroom", "audio"),
    ("s9", "Reiezione dell&rsquo;alimentazione", "audio"),
    ("s10", "Impedenza d&rsquo;uscita", "audio"),
    ("sdist", "Distorsione: V4", "audio"),
    ("s11", "I relè di guadagno: V2", "audio"),
    ("smute", "Il mute: i relè al jack, V2", "audio"),
    ("sint", "Il guadagno interbloccato e i comandi", "audio"),
    ("s12", "Sovraccarico e corto: V3, P7", "audio"),
    ("sprot", "Il blocco di oggi: i guasti e il calore", "audio"),
    ("sstax", "La Stax: il condensatore e i guasti lunghi, P10", "audio"),
    ("sheat", "Il calore del telaio", "alimentatore"),
    ("spsu", "L&rsquo;alimentatore: schema e decisioni", "alimentatore"),
    ("spow", "Potenza, rail e VRELAY", "alimentatore"),
    ("ssup", "Il sorvegliante e i guasti, sul circuito", "alimentatore"),
    ("stim", "Il temporizzatore a comparatori e lo standby", "alimentatore"),
    ("sdiag", "L&rsquo;autodiagnosi: la coppia del mute e i guasti dello standby", "alimentatore"),
    ("soff", "Spegnimento e failsafe al jack", "alimentatore"),
    ("sbrd", "Le schede di prova e l&rsquo;assieme", "schede"),
    ("s13", "Requisiti a fronte del misurato", "audio"),
    ("s14", "Cosa questo dossier non dice", "schede"),
    ("s15", "Provenienza", "audio"),
    ("appA", "Appendice: il registro delle ADR", "audio"),
    ("appB", "Appendice: l&rsquo;indice dei requisiti tecnici", "audio"))
SECTIONS = tuple((a, lab) for a, lab, p in SECTIONS_TUTTE if p in PARTI)
SECNO = {"s0": "0", "appA": "A", "appB": "B"}


def secno(anchor):
    if anchor in SECNO:
        return SECNO[anchor]
    return str([a for a, _ in SECTIONS if a not in SECNO].index(anchor) + 1)


def sez(anchor):
    """«sezione N», col link: il numero cambia con le parti presenti."""
    return f'<a href="#{anchor}">sezione {secno(anchor)}</a>'


def build_page(M, inline=False):
    resp, v1, z, psrr, hr, cf = M["resp"], M["v1"], M["z"], M["psrr"], M["hr"], M["cf"]
    trim, noise, v2, v3, p7, op = M["trim"], M["noise"], M["v2"], M["v3"], M["p7"], M["op"]
    e4, ee, sel, vol = M["e4"], M["e3e5"], M["sel"], M["vol"]
    dist = M["dist"]
    e4_main = max(g["zrmax_max"] for g in e4["groups"] if g["out"] == "main")
    e4_fix = max(g["zrmax_max"] for g in e4["groups"] if g["out"] != "main")
    e4_disp = max(g["disp"] for g in e4["groups"])
    e4_ok = all(g["zrmax_max"] < E4_MAX and g["disp"] < E4_COSTANZA for g in e4["groups"])
    nc = nc028_formula()

    def dbspl(v):
        """Di picco a 1 m con la catena di NC-028; sotto la soglia d'udito si dice cosi'."""
        if not nc or v <= 0:
            return "&mdash;"
        d = nc["db"](v)
        return f"{fx(d, 1)} dB SPL" if d >= 0 else "sotto 0 dB SPL"

    def uv(v, nd=3):
        """Una tensione piccola nella sua unita', virgola italiana, meno tipografico."""
        for k, u in ((1, "V"), (1e-3, "mV"), (1e-6, "µV"), (1e-9, "nV")):
            if abs(v) >= k:
                return f"{it(v / k, nd)} {u}".replace("-", "&minus;")
        return f"{it(v / 1e-9, nd)} nV".replace("-", "&minus;")

    def figure(svgfile, alt):
        if svgfile in IMMAGINI:
            # L51c: le immagini delle schede di prova, PNG
            if inline:
                import base64
                with open(os.path.join(*IMMAGINI[svgfile]), "rb") as f:
                    src_ = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
            else:
                src_ = svgfile
            return (f'<div class="plate"><img src="{src_}" alt="{html_escape(alt)}" '
                    'loading="lazy"></div>')
        if inline:
            if svgfile in M["figs"]:
                body = M["figs"][svgfile]
            else:
                with open(os.path.join(SCHEM, svgfile)) as f:
                    body = f.read()
            return f'<div class="plate">{body.split("?>", 1)[-1]}</div>'
        return (f'<div class="plate"><img src="{svgfile}" '
                f'alt="{html_escape(alt)}" loading="lazy"></div>')

    def marca(s):
        """L51c: un testo letto da un JSON o da un report, coi non-requisiti (T2, V5, ...)
        marcati per il linker."""
        for tok in M["ct"]["nonreq"]:
            s = re.sub(rf"(?<![\w>-]){re.escape(tok)}(?![\w<])", des(tok), s)
        return s

    def h2(anchor):
        lab = dict(SECTIONS)[anchor]
        return f'<h2 id="{anchor}"><span class="secno">{secno(anchor)}</span><span>{lab}</span></h2>'

    allm = [m for deck in M["decks"] for m in provenance(deck)]
    vendors = sorted({m["part"] for m in allm if m["vendor"]})
    placeholders = sorted({m["part"] for m in allm if not m["vendor"]})
    con_tetto = sorted({m["part"] for m in allm if m["kf"] == KF_TETTO})
    con_kf = sorted({m["part"] for m in allm if m["kf"] not in (0, KF_TETTO)})
    senza_kf = sorted({m["part"] for m in allm if m["kf"] == 0})
    psu = "alimentatore" in PARTI

    h = []
    A = h.append
    mu, il, l2 = M["mute"], M["il"], M["l2"]
    e3w = min(trim["e3min"], ee["e3min"])
    e5w = max(trim["e5max"], ee["e5max"], vol["e5_girato"])
    v1w = min(v1["min"], vol["v1_min"])
    v1w_where = v1["min_where"] if v1["min"] <= vol["v1_min"] else "blocco B &middot; sorgente del bilanciamento"
    sel_w = max(c["v"] for k, c in sel["cells"].items() if k[0] != "99" and float(k[1]) <= 0.1)

    A('<div class="wrap">')
    # L64b: la riga diceva ancora L51a e L48b (la pagina di L64a corre sul circuito dopo L67)
    A('<p class="eyebrow">Scheda audio &middot; deck corsi il 2026-11-02 (L64a) sul circuito dopo '
      'L67 &middot; seconda strada: la regressione di L66 &middot; mute dalla matrice di V2 intera '
      'ricorsa (L64a), contro L60d2 &middot; interblocco da L36'
      + (' &middot; alimentatore corso il 2026-11-03 (L64b) col carico di oggi; seconda strada: '
         'L58b sullo stesso circuito, L54b3b, L54b2 e L51b' if psu else '')
      + (' &middot; distorsione corsa il 2026-10-10 (L51c); seconda strada: L46b &middot; schede di '
         'prova di L49a e L49b, DRC rifatta il 2026-10-10' if "schede" in PARTI else '') + '</p>')
    A('<h1>Dossier di misura del preamplificatore di linea</h1>')
    A('<p class="lede">Classe A pura a componenti discreti, senza operazionali nel '
      'percorso del segnale. Quattro ingressi a relè con un condensatore ciascuno, guadagno '
      '0 / +3 / +10 dB, trim 0 / &minus;6 / &minus;12 dB sull&rsquo;uscita variabile, volume a '
      'potenziometro col bilanciamento, mute coi soli relè al jack.'
      + (' Le due schede: la scheda audio, poi l&rsquo;alimentatore, coi rail lineari, il '
         'sorvegliante in hardware e il temporizzatore che ordina mute, guadagno e rete.'
         if psu else '')
      + (' Le due schede sono state piazzate e sbrogliate per prova, e l&rsquo;assieme sta nel '
         f'contenitore ({sez("sbrd")}).' if "schede" in PARTI else '') + '</p>')

    shape, level = adr014(resp)
    worst_shape = max(shape.values(), key=abs)
    weak_psrr = min(r["p10k"] for r in psrr.values())
    nc9 = hr["modes"]["10db"]["trim"]["6"]["M1"]
    gains = " · ".join(sg(resp[(m, "1.5")]["g1k"]) if m != "0db"
                       else fx(resp[(m, "1.5")]["g1k"]) for m in MODES)
    tiles = [
        ("Guadagni a 1 kHz", gains, "dB &middot; 0 / +3 / +10 &middot; sorgente 1,5 Ω"),
        ("V1, margine minimo", f"{fx(v1w)}°",
         f"soglia 60° &middot; guardia {fx(v1w - PM_MIN)}° &middot; {v1w_where}"),
        ("Headroom, NC-009", f"{sg(nc9)} dB", "metrica M1 &middot; +10 dB col trim a &minus;6 dB"),
        ("E3, min |Z<sub>in</sub>|", f"{fx(e3w / 1000, 1)} kΩ",
         "al jack d&rsquo;ingresso, col selettore, ogni posizione del trim"),
        ("E5, catena peggiore", f"{fx(e5w)} µV",
         "bilanciamento girato di 3 dB compreso &middot; 1/f al tetto di ADR-057"),
        ("F1, cambio d&rsquo;ingresso", uv(sel_w),
         "il peggiore sulle uscite con sorgenti fino a 100 mV di continua"),
        ("V2, mute", f"{mu['n'] - mu['n_fuori']} su {mu['n']}",
         "verdetti che reggono &middot; il clic del taglio dichiarato"),
        ("Scarto ADR-014", it_sci(worst_shape), "dB a 20 kHz rif. 1 kHz &middot; peggiore dei 3 modi"),
        ("V4, THD a 20 kHz", f"{pct(dist['thd_lo']['20k'])} %",
         f"0,2 V &middot; tetto {pct(dist['soglie']['thd20_lo'], tetto=True)} % &middot; cifra di modello"),
        ("PSRR, peggiore", f"{fx(weak_psrr)} dB", "a 10 kHz"),
        ("E4, Re(Z<sub>out</sub>) max", f"{fx(max(e4_main, e4_fix))} Ω",
         "al jack &middot; 20 Hz–20 kHz &middot; 3 uscite, costante col volume")]
    if psu:
        off_db = [M["off"]["f"]["db"](float(r["picco_V"])) for r in M["off"]["rows"]
                  if r["criterio"].startswith("<= 0.002")]
        perm_w = min(v for c, k, v, s_, ok in M["vt"] if c == "perm" and v is not None)
        tiles += [("Δ, il più corto", f"{fx(perm_w, 1)} ms",
                   f"il permissivo dopo il mute, tre reti &middot; soglia {it(M['st']['perm'], 3)} ms "
                   "(ADR-045, ADR-105)"),
                  ("Guasto dell&rsquo;alimentatore, al jack",
                   f"{fx(max(off_db), 1)} dB SPL" if off_db else "&mdash;",
                   "il peggiore sul circuito, col carico di oggi &middot; di picco a 1 m")]
    A('<dl class="synopsis">')
    for lab, val, unit in tiles:
        A(f'<div><dt>{lab}</dt><dd>{val}<span class="u">{unit}</span></dd></div>')
    A('</dl>')

    A('<div class="note"><strong>Leggere prima questo.</strong> '
      + (f'Dei {len(vendors) + len(placeholders)} dispositivi attivi che questi deck '
         f'simulano, <strong>{len(vendors)} usano il modello del costruttore</strong> '
         f'({", ".join(vendors)})'
         + (f' e {len(placeholders)} sono segnaposto scritti a mano ({", ".join(placeholders)})'
            if placeholders else ', nessuno è un segnaposto') + '. ')
      + ((f'<strong>Il rumore 1/f è nei modelli</strong>: '
          + "; ".join(x for x in (
              f'{", ".join(con_kf)} col KF del costruttore' if con_kf else "",
              f'{", ".join(con_tetto)} a un tetto dichiarato, il doppio del tipico delle curve '
              'pubblicate (ADR-057)' if con_tetto else "",
              f'senza 1/f solo {", ".join(senza_kf)}' if senza_kf else "") if x)
          + ': le cifre di E5 sono un limite per eccesso, non un pavimento. ')
         if con_tetto or con_kf else
         '<strong>Nessun modello simulato ha rumore 1/f</strong>: ogni cifra di rumore è un '
         'pavimento termico e shot. ')
      + f'Le cifre di distorsione ({sez("sdist")}) sono di modello, sul blocco da solo: dove la '
      'misura sul prototipo diverge, vale la misura. La provenienza è scritta '
      'sotto ogni titolo di sezione, ed è letta dagli <code>.include</code> dei deck, non '
      'dichiarata.</div>')

    A('<p>Il progetto sostituisce un Technics SU-9070 la cui struttura di guadagno '
      'richiede <strong>46 dB di attenuazione</strong>, causa misurabile della mancanza '
      'di dinamica lamentata. La topologia canonica è in <code>circuits/preamp/</code>; i '
      'banchi di prova in <code>spice/preamp/tb/</code>; i dati dei deck in '
      f'<code>{rel(L64D)}/</code>, corsi oggi sul circuito di <code>main</code>; quelli del '
      'mute, del volume e dell&rsquo;interblocco nelle cartelle dei loro lotti, nominate sotto '
      'ogni sezione.</p>')

    A('<nav class="toc" aria-label="Indice"><ol>')
    for anchor, label in SECTIONS:
        n = secno(anchor)
        A(f'<li><a href="#{anchor}" data-n="{n.zfill(2) if n.isdigit() else n + " "}">{label}</a></li>')
    A('</ol></nav>')

    A('<p class="meta">Nessuna cifra di questa pagina è scritta a mano. Le curve sono '
      'ricontrollate contro le <code>print</code> che ngspice ha stampato nei log '
      'versionati; le tabelle, riga per riga, contro le <code>print</code> o le '
      '<code>meas</code> dello stesso log, e una cella vuota è un rifiuto; la cifra di '
      'headroom contro lo script di L16 che l&rsquo;ha scelta. Se una strada diverge, il '
      'generatore rifiuta di produrre la pagina.</p>')
    A(f'<p class="meta"><strong>La seconda strada.</strong> Il blocco di oggi è quello che L66 '
      'ha corso e misurato come variante prima di portarlo nel sorgente (ADR-111), e i deck sono '
      f'i suoi: le {l2["n_mis"]} misure dei log dei 20 deck veloci coincidono alla sesta cifra con '
      f'quelle della regressione di L66 (<code>{rel(os.path.join(L66, "regressione"))}/</code>); il '
      f'deck del mute di L66, ricorso oggi, ridà le sue {l2["n_mute"]} misure e le tabelle di oggi. '
      'Il selettore e le due copie col bilanciamento non hanno una corsa precedente sul circuito '
      'di oggi: la loro seconda strada sono gli stessi deck col blocco preso dai file della '
      f'variante di L66, e le {l2["n_res"]} righe di risultato coincidono una per una; in tutto '
      f'{l2["n_tab"]} tabelle coincidono byte per byte. '
      + (f'Senza questa strada: {", ".join(l2["senza"])}, che non stampa risultati né tiene '
         'tabelle. ' if l2["senza"] else '')
      + ((f'{l2["spliced"]} <code>print</code> spezzate nei log da una Note del gmin stepping '
          'sono state ricucite (limitations #37). ' if l2["spliced"] > 1 else
          'Una <code>print</code> spezzata nel log da una Note del gmin stepping è stata '
          'ricucita (limitations #37). ') if l2["spliced"] else '')
      + f'Nessun dato della scheda audio è di prima del {AUDIO_DA}, il giorno del circuito di '
      'oggi, tranne: ' + "; ".join(f'<code>{html_escape(rel(k))}/</code>, {html_escape(v)}'
                                    for k, v in AUDIO_PERMESSI.items()) + '.</p>')

    # --- 0 il contratto (L42d) ---
    A(h2("s0"))
    A(ct.section_prb(M["ct"]["prb"]))

    # --- 1-2 schemi ---
    A(h2("s1"))
    A('<p>Il blocco è uno solo (ADR-006) e il prodotto lo usa otto volte: per canale, '
      'il blocco A (buffer d&rsquo;ingresso), i due buffer delle uscite fisse (ADR-023) e '
      'il blocco B (uscita variabile). È l&rsquo;oggetto da giudicare. La compensazione è '
      'quella di ADR-054 (il VAS a corrente più alta e il Miller più piccolo, per la '
      'distorsione verso gli acuti); una cella RC per blocco alimenta specchio d&rsquo;ingresso '
      'e VAS dal rail positivo (ADR-056).</p>')
    A(figure("gain_block.svg", "Schema del blocco di guadagno"))
    A(h2("s2"))
    A('<p>Per canale: il selettore a quattro ingressi, ciascuno col suo condensatore '
      f'({sez("ssel")}); il blocco A; le due uscite fisse coi loro buffer; il trim, poi '
      'C<sub>T</sub>, poi il volume a potenziometro col bilanciamento '
      f'({sez("svol")}); il blocco B; il mute coi relè al jack su tutte e tre le uscite '
      f'({sez("smute")}).</p>')
    A(figure("preamp_blocks.svg", "Diagramma a blocchi del preamplificatore"))

    # --- il selettore ---
    A(h2("ssel"))
    A(prov_line("tb_f1_selettore.cir", sel["dir"]))
    A(f'<p><strong>F1</strong> (PR-14): senza musica, cambiare sorgente lascia sulle uscite al '
      f'più {uv(F1_MAX, 3)} di picco (~{dbspl(F1_MAX)}); ogni ingresso, anche non selezionato, '
      'sta a 0 V. Il selettore di ADR-064 dà a ogni ingresso un condensatore in serie, una '
      'resistenza a massa dal lato del preamp e una sul jack, e un relè monostabile '
      'dalla manopola: a ogni cambio un contatto si apre e un altro si chiude, senza mute. Il '
      'banco cambia da una sorgente a 0 V a una alla continua V<sub>B</sub>, col trasferimento '
      'del relè (il nuovo si chiude 1 ms dopo) o con la sovrapposizione (1 ms prima: '
      'l&rsquo;ordine di due monostabili non è garantito).</p>')
    A('<div class="tablewrap"><table><tr><th>V<sub>B</sub></th><th>Contatti</th>'
      '<th class="num">fissa</th>'
      + "".join(f'<th class="num">principale {lab}</th>' for _, lab in F1_MODI)
      + '<th>Esito</th></tr>')
    for t, tl in (("trasf", "trasferimento"), ("sovrap", "sovrapposizione")):
        for vb in sel["vbs"]:
            if ("10", vb, t) not in sel["cells"]:
                continue
            row = [sel["cells"][(m, vb, t)] for m, _ in F1_MODI]
            ok = all(c["v"] <= F1_MAX for c in row)
            A(f'<tr><td>{uv(float(vb)) if float(vb) else "0 V"}</td><td>{tl}</td>'
              f'<td class="num">{uv(row[0]["jf"])}</td>'
              + "".join(f'<td class="num">{uv(c["jm"])}</td>' for c in row)
              + verdict(ok, "regge", "oltre F1") + '</tr>')
    A('</table></div>')
    cf10 = sel["cf"]["0.01"]
    A(f'<p>Fino a 100 mV di continua il gradino è quello del contatto stesso, lo stesso con due '
      f'sorgenti a 0 V: al principale a +10 dB {uv(sel["r0"])} (~{dbspl(sel["r0"])}). Cresce con '
      'V<sub>B</sub> per la perdita del condensatore sulla resistenza dell&rsquo;ingresso non '
      f'scelto (il poliestere peggiore, 10 000 s): a 1 V {uv(sel["r1"])}. Col gradino di fondo '
      f'più la parte che cresce con la continua, il principale a +10 dB tocca F1 a '
      f'<strong>~{it(sel["lim"], 2)} V</strong> di continua della sorgente: è il limite che '
      'ADR-064 dichiara, arrotondato per difetto, e che i «Dettagli» di PR-14 riportano. Il '
      'controfattuale, l&rsquo;ingresso di prima del selettore, con 10 mV dà '
      f'<strong>{uv(cf10["jf"])}</strong> sul fisso e <strong>{uv(cf10["jm"])}</strong> sul '
      'principale: il banco distingue.</p>')
    A(f'<p class="prov">Netlist <code>{html_escape(il["net"])}</code> &middot; il 2e di '
      '<code>run_tests.sh</code>, rieseguito da questa pagina</p>')
    A('<div class="tablewrap"><table><tr><th>Ingresso</th><th>Jack</th><th>Condensatore</th>'
      '<th>R sul jack</th><th>R lato preamp</th><th>Relè (NO)</th></tr>')
    for ing, j, c, cv, rj, rs, k in il["ingressi"]:
        A(f'<tr><td>{ing}</td><td>{j}</td><td>{c} {html_escape(cv)}</td><td>{rj}</td>'
          f'<td>{rs}</td><td>{k}</td></tr>')
    A('</table></div>')

    # --- 3 punti di lavoro ---
    # --- il limitatore d'ingresso (L64a: ADR-101, «dopo L57b») ---
    li = M["lim"]
    A(h2("slim"))
    A(f'<p class="prov">Dati <code>{html_escape(rel(li["dir"]))}/</code> &middot; il limitatore non è '
      'cambiato dopo (ADR-101; il modello del BAV199 è del costruttore, Diodes Incorporated)</p>')
    A('<p>Fra il contatto del selettore e il gate del blocco A ci sono 1 kΩ in serie e una coppia '
      'di diodi BAV199 verso due riferimenti a ±5 V (ADR-101): un cavo RCA collegato a caldo, o una '
      'sorgente guasta, non porta il gate oltre quello che il JFET regge.</p>')
    A('<div class="tablewrap"><table><tr><th>Grandezza</th><th class="num">Valore</th></tr>')
    A(f'<tr><td>picco sul gate, RCA collegato a caldo (reti −10 / 0 / +10 %)</td><td class="num">'
      f'{fx(li["ain"], 1)} V</td></tr>')
    A(f'<tr><td>margine sul massimo gate-gate del JFET</td><td class="num">{fx(li["gg_m"], 1)} V</td></tr>')
    A(f'<tr><td>margine sul massimo gate-drain</td><td class="num">{fx(li["gd_m"], 1)} V</td></tr>')
    A(f'<tr><td>il colpo alla principale, 0 / +10 dB</td><td class="num">{fx(li["k11_0"], 1)} / '
      f'{fx(li["k11_10"], 1)} dB SPL</td></tr>')
    A(f'<tr><td>lo stesso col mute inserito</td><td class="num">{fx(li["mute_0"], 1)} / '
      f'{fx(li["mute_10"], 1)} dB SPL</td></tr>')
    A('</table></div>')
    A(f'<p>Il costo nel suono, sul blocco del giorno della prova: la THD a 20 kHz, 0,2 V, passa da '
      f'{pct(li["thd_senza"])} a {pct(li["thd_lim"])} % ({fx(db20(li["thd_lim"] / li["thd_senza"]), 1)} dB), '
      f'e il rumore stimato al jack da {fx(li["e5_senza"], 2)} a {fx(li["e5_lim"], 2)} µV. Per questo il '
      'manuale chiede di collegare i cavi d&rsquo;ingresso col mute inserito.</p>')
    A('<p class="meta">Seconda strada: le cifre di THD e di rumore della sintesi tornano, rete per '
      'rete, nella tabella del costo dello stesso lotto.</p>')

    A(h2("s3"))
    A(prov_line("tb_op.cir", op["dir"]))
    A('<p>Corrente dai rail e punto di lavoro di ogni dispositivo attivo, a ingresso a '
      f'massa. L&rsquo;uscita del blocco sta a {uv(op["vout"], 4)} (ADR-056): nel blocco A '
      'questa continua attraversa il trim, e C<sub>T</sub> la ferma prima del volume; '
      'R<sub>G</sub> tiene a massa il cursore, cioè il gate del blocco B (ADR-065).</p>')
    A('<div class="tablewrap"><table><tr><th>Grandezza</th><th class="num">Valore</th></tr>')
    A(f'<tr><td>Corrente dal rail +15 V</td><td class="num">{it(abs(op["rails"].get("i(vpp)", 0)) * 1000, 4)} mA</td></tr>')
    A(f'<tr><td>Corrente dal rail −15 V</td><td class="num">{it(abs(op["rails"].get("i(vmm)", 0)) * 1000, 4)} mA</td></tr>')
    A(f'<tr><td>Uscita del blocco, v(OUT)</td><td class="num">{uv(op["vout"], 4)}</td></tr>')
    A('</table></div>')
    A('<div class="tablewrap"><table><tr><th>Dispositivo</th><th class="num">I<sub>C</sub> / I<sub>D</sub> [mA]</th>'
      '<th class="num">V<sub>BE</sub> / V<sub>GS</sub> [V]</th><th class="num">V<sub>BC</sub> [V]</th></tr>')
    for dev, par in op["devices"]:
        ic = par.get("ic", par.get("id"))
        vbe = par.get("vbe", par.get("vgs"))
        vbc = par.get("vbc")
        A(f'<tr><td>{html_escape(dev.upper())}</td>'
          f'<td class="num">{it(ic * 1000, 4) if ic is not None else "&mdash;"}</td>'
          f'<td class="num">{it(vbe, 4) if vbe is not None else "&mdash;"}</td>'
          f'<td class="num">{it(vbc, 4) if vbc is not None else "&mdash;"}</td></tr>')
    A('</table></div>')

    # --- 4 risposta ---
    A(h2("s4"))
    A(prov_line("tb_ac.cir", sa(L64D, "tb_ac")))
    A(figure("fig_response.svg", "Risposta in frequenza"))
    A('<div class="tablewrap"><table><tr><th>Curva</th><th class="num">20 Hz</th>'
      '<th class="num">1 kHz</th><th class="num">20 kHz</th><th class="num">100 kHz</th></tr>')
    for m in MODES:
        for rs, lab in (("1.5", "sorgente 1,5 Ω (K11)"), ("2500", "sorgente 2500 Ω (volume a metà)")):
            r = resp[(m, rs)]
            A(f'<tr><td>{MLAB[m]} &middot; {lab}</td>'
              + "".join(f'<td class="num">{fx(r[k], 4)} dB</td>' for k in ("g20", "g1k", "g20k", "g100k"))
              + '</tr>')
    A('</table></div>')
    A('<h3>La claim falsificabile di ADR-014</h3>')
    A('<p>Il volume ha un&rsquo;impedenza d&rsquo;uscita che varia con la manopola. Se il '
      'cascode d&rsquo;ingresso fa il suo lavoro, <strong>la forma della risposta non si '
      'muove</strong>: la risposta a 20 kHz <em>riferita a quella a 1 kHz</em> resta la stessa '
      'con la sorgente a 1,5 Ω e a 2500 Ω, in ogni modo.</p>')
    A(figure("fig_response_adr014.svg", "ADR-014: risposta contro impedenza di sorgente"))
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">scarto assoluto a 1 kHz</th>'
      '<th class="num">scarto assoluto a 20 kHz</th><th class="num">20 kHz riferito a 1 kHz &mdash; la claim</th></tr>')
    for m in MODES:
        A(f'<tr><td>{MLAB[m]}</td><td class="num">{fx(level[m]["g1k"], 5)} dB</td>'
          f'<td class="num">{fx(level[m]["g20k"], 5)} dB</td>'
          f'<td class="num"><strong>{it_sci(shape[m])} dB</strong></td></tr>')
    A('</table></div>')
    A('<p>Ogni scarto è «sorgente 2500 Ω meno sorgente 1,5 Ω». Le colonne di scarto '
      '<em>assoluto</em> coincidono a 1 kHz e a 20 kHz perché sono una perdita di livello '
      'a banda larga, il partitore fra la sorgente e la Zin del blocco: non misurano la '
      'claim. La claim è l&rsquo;ultima colonna.</p>')
    lf = resp["lf"]
    A('<h3>Il taglio in bassa, col carico da 50 kΩ</h3>')
    A(f'<p>Con il carico Stax-like da 50 kΩ: {fx(lf["g1k"], 4)} dB a 1 kHz, '
      f'{fx(lf["g20"], 4)} dB a 20 Hz, {fx(lf["g5"], 4)} dB a 5 Hz. Il polo è quello '
      'del condensatore d&rsquo;uscita da 4,7 µF (E8, ADR-007).</p>')

    # --- 5 V1 ---
    B = v1["B"]
    A(h2("s5"))
    A(prov_line("tb_loop.cir", v1["B_dir"], note=" (blocco B)"))
    A(prov_line("tb_loop_blockA.cir", v1["A_dir"], note=" (blocco A)"))
    A(prov_line("tb_loop_bufferfissa.cir", v1["F_dir"], note=" (buffer delle fisse)"))
    A('<p><strong>Soglia: 60° su ogni combinazione della matrice</strong> (ADR-019). '
      '<strong>Dove si applica la sonda</strong> lo dice ADR-024: la sonda capacitiva è '
      'il cavo d&rsquo;interconnessione e sta <em>al jack</em>, dopo i 47 Ω e il 4,7 µF, '
      'sul blocco B e sui buffer delle fisse; il verdetto è il <strong>minimo sulla '
      'spazzata</strong> fino a 4,7 nF, non il valore a 4,7 nF. Il blocco A pilota il '
      'cablaggio interno fino al volume e si giudica con una capacità realistica, ≤ 1 nF. '
      'La sonda sul nodo d&rsquo;uscita resta come informazione.</p>')
    A('<p>Iniezione di tensione al gate del JFET invertente: quel nodo non assorbe '
      'corrente e la rete di controreazione lo pilota a bassa impedenza, quindi '
      'l&rsquo;iniezione semplice è esatta. I relè commutano la rete di controreazione, '
      'quindi <strong>il margine è diverso nei tre modi</strong>, e l&rsquo;impedenza del '
      'volume cambia con la manopola: per questo si spazza tutto.</p>')
    A('<div class="tablewrap"><table><tr><th>Istanza</th><th>Dove cade il minimo</th>'
      '<th class="num">Minimo della spazzata</th><th class="num">A 4,7 nF</th>'
      '<th class="num">Sonda sul nodo</th><th>Esito</th></tr>')
    for m in MODES:
        b, w = B[m], B[m]["w"]
        A(f'<tr><td>Blocco B &middot; {MLAB[m]}</td>'
          f'<td>sorgente {lab_c(w["rsrc"])} &middot; carico {lab_c(w["rload"])} &middot; cavo {lab_c(w["cprobe"])}</td>'
          f'<td class="num"><strong>{fx(b["min"], 3)}°</strong></td>'
          f'<td class="num">{fx(b["at47"], 3)}°</td>'
          f'<td class="num">{fx(b["node_min"], 3)}°</td>{verdict(b["min"] >= PM_MIN)}</tr>')
    for p, t in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        w = v1["A"][p]
        A(f'<tr><td>Blocco A &middot; trim {t}</td>'
          f'<td>sorgente {lab_c(w["rsrc"])} &middot; cablaggio {lab_c(w["cwire"])}</td>'
          f'<td class="num"><strong>{fx(pm(w), 3)}°</strong></td><td class="num">&mdash;</td>'
          f'<td class="num">&mdash;</td>{verdict(pm(w) >= PM_MIN)}</tr>')
    w, wn = v1["F"], v1["Fn"]
    A(f'<tr><td>Buffer delle fisse</td>'
      f'<td>carico {lab_c(w["rld"])} &middot; cavo {lab_c(w["cprobe"])}</td>'
      f'<td class="num"><strong>{fx(pm(w), 3)}°</strong></td><td class="num">&mdash;</td>'
      f'<td class="num">{fx(pm(wn), 3)}°</td>{verdict(pm(w) >= PM_MIN)}</tr>')
    rsw, ww, _ = min(vol["v1"], key=lambda t: pm(t[1]))
    A(f'<tr><td>Blocco B &middot; sorgente del bilanciamento</td>'
      f'<td>sorgente {lab_c(rsw)} &middot; {MLAB[ww["mode"]]} &middot; carico {lab_c(ww["rload"])} '
      f'&middot; cavo {lab_c(ww["cprobe"])}</td>'
      f'<td class="num"><strong>{fx(pm(ww), 3)}°</strong></td><td class="num">&mdash;</td>'
      f'<td class="num">&mdash;</td>{verdict(pm(ww) >= PM_MIN)}</tr>')
    A('</table></div>')
    na = v1["A"]["notrim"]
    A(f'<p>Blocco B: {B["0db"]["n"]} righe per modo al jack, sorgenti del volume da 1 mΩ a '
      '(10 kΩ + Thévenin del trim)/4, carichi 100 kΩ e 10 kΩ; la compensazione è quella di '
      'ADR-054. Col bilanciamento il blocco B vede sorgenti più alte: l&rsquo;ultima riga è il '
      f'minimo fino a {lab_c(vol["v1"][-1][0])} ({sez("svol")}). '
      f'Blocco A: scala {trim["scale"].replace("/", " / ")} Ω; senza trim il minimo è '
      f'{fx(pm(na), 3)}° (sorgente {lab_c(na["rsrc"])}, {lab_c(na["cwire"])}). Con 4,7 nF sul '
      f'cablaggio, che ADR-024 non chiede, il blocco A a trim 0 dB scende a '
      f'{fx(pm(v1["A"]["0_all"]), 2)}°.</p>')
    A(figure("fig_v1.svg", "Margine di fase contro capacità del cavo"))
    b0 = B["0db"]
    A(f'<p>Il verdetto è il minimo della curva al jack, non il valore a 4,7 nF: a 0 dB il '
      f'minimo, {fx(b0["min"], 2)}°, cade a {lab_c(b0["w"]["cprobe"])}, e a 4,7 nF la stessa '
      f'curva vale {fx(b0["at47"], 2)}°. Sul nodo, dove nessun cavo vero sta, lo stesso blocco '
      f'scende a {fx(b0["node_min"], 2)}°.</p>')
    A('<h3>Il guadagno d&rsquo;anello</h3>')
    A(figure("fig_loop.svg", "Guadagno d'anello"))
    A('<div class="tablewrap"><table><tr><th>Blocco B, sorgente 2,5 kΩ, carico 100 kΩ</th>'
      '<th class="num">|T| a 10 Hz</th><th class="num">frequenza d&rsquo;incrocio</th>'
      '<th class="num">margine</th></tr>')
    for m in MODES:
        bb = v1["bode"][m]
        A(f'<tr><td>{MLAB[m]} &middot; cavo {lab_c(bb["C"])}</td>'
          f'<td class="num">{fx(bb["tdc"], 2)} dB</td>'
          f'<td class="num">{it(bb["fcross"] / 1000, 4)} kHz</td>'
          f'<td class="num">{fx(bb["pmarg"], 3)}°</td></tr>')
    A('</table></div>')
    A(f'<p class="meta">Il deck scrive le curve solo alla sorgente di 2,5 kΩ col carico da '
      f'100 kΩ (<code>{rel(v1["bode_dir"])}/</code>); le sorgenti che il trim aggiunge stanno '
      'nella tabella dei margini qui sopra, non in queste figure.</p>')

    # --- 6 trim, E3 ---
    A(h2("s6"))
    A(prov_line("tb_trim.cir", trim["dir"]))
    A('<p>Il trim è uno solo, fra l&rsquo;uscita del blocco A e il volume (ADR-027): le '
      'uscite fisse prendono il segnale prima di lui e restano copia fedele della sorgente. '
      f'Scala per canale {trim["scale"].replace("/", " / ")} Ω, a relè bistabili. '
      'L&rsquo;attenuazione è misurata col carico che ha davanti: C<sub>T</sub>, il volume e '
      'il bilanciamento al centro (ADR-065).</p>')
    A('<div class="tablewrap"><table><tr><th>Posizione</th><th class="num">Attenuazione a 1 kHz</th></tr>')
    for p, lab in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        A(f'<tr><td>{lab}</td><td class="num">{fx(trim["att"][p], 4)} dB</td></tr>')
    A('</table></div>')
    A('<p><strong>E3</strong> chiede ≥ 100 kΩ al connettore d&rsquo;ingresso <em>in ogni '
      'posizione del trim</em>, sul minimo di |Z<sub>in</sub>| fra 20 Hz e 20 kHz '
      '(«Nota su E3»). Il connettore vede la rete dell&rsquo;ingresso (ADR-064) e il blocco A; '
      'la capacità del selettore e del cablaggio è spazzata.</p>')
    csels = sorted({c for _, c in trim["zmin"]}, key=capval)
    A('<div class="tablewrap"><table><tr><th>Posizione del trim</th>'
      + "".join(f'<th class="num">selettore {lab_c(c)}</th>' for c in csels) + '<th>Esito</th></tr>')
    for p, lab in (("99", "senza trim (riferimento)"), ("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        vals = [trim["zmin"].get((p, c)) for c in csels]
        ok = all(x is not None and x >= 1e5 for x in vals)
        A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{it(x / 1000, 4)} kΩ</td>' for x in vals)
          + (verdict(ok) if p != "99" else '<td class="na">&mdash;</td>') + '</tr>')
    A('</table></div>')
    A('<h3>Il deck canonico di E3 ed E5</h3>')
    A(prov_line("tb_e3_e5.cir", ee["dir"]))
    A('<p>Lo stesso ingresso, letto al jack, nel deck che porta E3 ed E5 dalla rete di ADR-064 '
      'alla catena col volume:</p>')
    A('<div class="tablewrap"><table><tr><th>Posizione del trim</th>'
      + "".join(f'<th class="num">selettore {lab_c(c)}</th>' for c in ee["csels"])
      + '<th>Esito</th></tr>')
    for p, lab in (("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        vals = [ee["z"][(p, c)] for c in ee["csels"]]
        A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{it(x / 1000, 4)} kΩ</td>' for x in vals)
          + verdict(all(x >= 1e5 for x in vals)) + '</tr>')
    A('</table></div>')

    # --- il volume col bilanciamento ---
    A(h2("svol"))
    A(prov_line("tb_e5_bilanciamento.cir", vol["e5_dir"], deckdir=sa(L64A, "bilanciamento"),
                note=" &middot; <strong>copia del deck</strong> col bilanciamento girato di 3 dB "
                     "(L48b), ricorsa oggi"))
    A(prov_line("tb_loop_bilanciamento.cir", vol["v1_dir"], deckdir=sa(L64A, "bilanciamento"),
                note=" &middot; <strong>copia di tb_loop.cir</strong> con le sorgenti del "
                     "bilanciamento (L48b), ricorsa oggi"))
    A('<p>Il volume è un potenziometro, non più un attenuatore a scatti, con un bilanciamento '
      'davanti (ADR-065, PR-16): fra il trim e il volume c&rsquo;è C<sub>T</sub>, che ferma la '
      'continua del blocco A (NC-041), e R<sub>G</sub> tiene a massa il cursore, il gate del '
      'blocco B. Senza C<sub>T</sub> la continua del blocco A attraversava trim e volume, e '
      'ogni movimento del cursore la portava al jack come un gradino.</p>')
    A(f'<p class="prov">Banco <code>{html_escape(rel(os.path.join(vol["scatti_dir"], "genera_scatti.py")))}</code>'
      f' &middot; dati <code>{html_escape(rel(vol["scatti_dir"]))}/</code> &middot; '
      '<code>analizza.py</code> rieseguito da questa pagina, uguale byte per byte</p>')
    A('<p>Il banco di L48b muove il cursore del volume a passi di 2 dB, in cima alla corsa e '
      'verso il fondo, e legge il gradino al jack: col cursore che chiude il punto nuovo prima '
      'di aprire il vecchio, e con quello che resta aperto 1 ms fra i due.</p>')
    A('<div class="tablewrap"><table><tr><th>Evento</th><th class="num">al jack, il peggiore</th>'
      '<th class="num">di picco a 1 m</th></tr>')
    for lab, v in (("un passo del cursore, il circuito di prima (senza C<sub>T</sub>)", vol["oggi_max"]),
                   ("un passo del cursore, oggi, contatto che chiude prima di aprire", vol["vol_max_m1"]),
                   ("un passo del cursore, oggi, contatto aperto per 1 ms", vol["vol_max"]),
                   ("il cambio del trim fuori mute, oggi (limite per eccesso)", vol["trim_max"])):
        A(f'<tr><td>{lab}</td><td class="num">{uv(v)}</td><td class="num">{dbspl(v)}</td></tr>')
    A('</table></div>')
    A(f'<p>«Il peggiore» è il peggiore delle continue del blocco A del banco, la nominale e i '
      f'±30 mV della dispersione dei pezzi, sui tre guadagni e sui due eventi del volume. Il '
      'cambio del trim fuori mute è un limite per eccesso: il trim si cambia solo a mute '
      'inserito (ADR-027), e il caso vero è il gruppo 2 della matrice di V2 '
      f'({sez("smute")}).</p>')
    A('<div class="tablewrap"><table><tr><th>Sorgente del blocco B</th><th>Dove cade il minimo</th>'
      '<th class="num">V1, minimo</th><th>Esito</th></tr>')
    for rs, w, n in vol["v1"]:
        A(f'<tr><td>{lab_c(rs)}</td><td>{MLAB[w["mode"]]} &middot; carico {lab_c(w["rload"])} '
          f'&middot; cavo {lab_c(w["cprobe"])} &middot; {n} celle</td>'
          f'<td class="num"><strong>{fx(pm(w), 3)}°</strong></td>{verdict(pm(w) >= PM_MIN)}</tr>')
    A('</table></div>')
    A(f'<p><strong>E5</strong> col bilanciamento al centro {fx(vol["e5_centro"], 3)} µV, girato di '
      f'3 dB <strong>{fx(vol["e5_girato"], 3)} µV</strong>, contro 10 µV.</p>')
    A('<div class="tablewrap"><table><tr><th>Canale</th><th>Dal trim</th><th>C<sub>T</sub></th>'
      '<th>Al volume</th><th>Cursore</th><th>R<sub>G</sub></th></tr>')
    for v_, trimn, c, cv, j, cur, rg in il["volume"]:
        A(f'<tr><td>{v_}</td><td>{trimn}</td><td>{c} {html_escape(cv)}</td><td>{j}</td>'
          f'<td>{cur}</td><td>{rg}</td></tr>')
    A('</table></div>')
    A('<p class="meta">La tabella dei componenti è quella che il 2e legge oggi sulla netlist '
      f'(<code>{html_escape(il["net"])}</code>).</p>')

    # --- 7 E5 ---
    A(h2("s7"))
    A(prov_line("tb_zout_psrr_noise.cir", noise["zout_dir"]))
    A(prov_line("tb_noise_breakdown.cir", noise["nb_dir"]))
    A('<p><strong>E5</strong> chiede meno di 10 µV RMS in uscita fra 20 Hz e 20 kHz, non '
      'pesati, e di questi 1 µV è la quota dell&rsquo;alimentazione (ADR-020). '
      + ('Il rumore 1/f dei bipolari è al tetto di ADR-057, il doppio del tipico delle curve '
         'pubblicate: <strong>queste cifre sono un limite per eccesso</strong>. ' if con_tetto
         else '')
      + 'Ogni totale è ricontrollato integrando lo spettro versionato.</p>')
    A('<div class="tablewrap"><table><tr><th>Blocco da solo, uscita al jack</th>'
      '<th class="num">Rumore 20 Hz–20 kHz</th></tr>')
    for lab, val in noise["nb"]:
        A(f'<tr><td>{lab}</td><td class="num">{fx(val * 1e6, 3)} µV</td></tr>')
    for lab, val in noise["zout"][:3]:
        A(f'<tr><td>{lab}</td><td class="num">{fx(val * 1e6, 3)} µV</td></tr>')
    A('</table></div>')
    A('<p><strong>La catena col trim</strong>: blocco A, trim, C<sub>T</sub>, volume, blocco B, '
      'sorgente phono (430 Ω) o K11 (1,5 Ω), volume al massimo o a metà corsa, tre modi. Per '
      'ogni posizione del trim la cella peggiore:</p>')
    A('<div class="tablewrap"><table><tr><th>Trim</th><th>Cella peggiore</th>'
      '<th class="num">Rumore</th><th>Esito contro 10 µV</th></tr>')
    for p, lab in (("99", "senza trim (riferimento)"), ("0", "0 dB"), ("6", "&minus;6 dB"), ("12", "&minus;12 dB")):
        w = trim["e5w"][p]
        val = num(w, "onoise_uv")
        A(f'<tr><td>{lab}</td><td>{MLAB[w["mode"]]} &middot; volume '
          f'{"al massimo" if w["att"] == "max" else "a metà"} &middot; sorgente {lab_c(w["rsrc"])}</td>'
          f'<td class="num"><strong>{fx(val, 3)} µV</strong></td>'
          + (verdict(val < E5_MAX, "sotto soglia", "sopra soglia") if p != "99"
             else '<td class="na">&mdash;</td>') + '</tr>')
    A('</table></div>')
    A(f'<p>Col deck canonico di E3 ed E5 il peggiore è {fx(ee["e5max"], 3)} µV '
      f'({MLAB.get(ee["w5"]["mode"], html_escape(ee["w5"]["mode"]))}, '
      f'sorgente {lab_c(ee["w5"]["rsrc"])}); col bilanciamento girato di 3 dB '
      f'{fx(vol["e5_girato"], 3)} µV ({sez("svol")}).</p>')

    # --- 8 headroom ---
    A(h2("s8"))
    A(prov_line("tb_dc_headroom.cir", hr["dir"]))
    A(figure("fig_headroom.svg", "Escursione in continua"))
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">Guadagno a 0 V</th>'
      '<th class="num">Finestra all&rsquo;1 % in ingresso</th><th class="num">v(OUT) ai bordi</th>'
      '<th class="num">Limite lineare</th><th class="num">Saturazione</th></tr>')
    for m in MODES:
        r = hr["modes"][m]
        A(f'<tr><td>{MLAB[m]}</td><td class="num">{fx(r["gain"], 5)} ×</td>'
          f'<td class="num">{fx(r["vi_lo"], 2)} … {fx(r["vi_hi"], 2)} V</td>'
          f'<td class="num">{fx(r["vo_lo"], 3)} … {fx(r["vo_hi"], 3)} V</td>'
          f'<td class="num">{fx(r["lin"], 4)} V RMS</td>'
          f'<td class="num">{fx(r["sat"], 4)} V RMS</td></tr>')
    A('</table></div>')
    A('<p>I modi non saturano allo stesso livello, e la differenza non sta nello stadio '
      'd&rsquo;uscita: a guadagno unitario v(FB) insegue v(OUT), il modo comune della '
      'coppia d&rsquo;ingresso sale con l&rsquo;uscita e si ferma per primo; con più guadagno '
      'v(FB) è una frazione di v(OUT) e l&rsquo;uscita arriva più in alto. È una proprietà '
      'della topologia; i valori esatti dipendono dai modelli.</p>')
    A('<h3>NC-009: una cifra, con la sua metrica</h3>')
    A('<p>Il caso che preoccupa è E6 × E2: il FiiO K11 a fondo scala dà 2,7 V RMS, e '
      'con rail a ±15 V (ADR-015) il +10 dB non ha quasi margine senza trim. La cifra '
      'pubblicata usa <strong>una</strong> metrica, <strong>M1</strong>, scelta in L16:</p>')
    A('<ul><li><strong>limite lineare</strong>: l&rsquo;uscita ai bordi della finestra in '
      'cui il guadagno locale dV<sub>out</sub>/dV<sub>in</sub> resta entro l&rsquo;1 % del '
      'valore a 0 V, il bordo minore in modulo, come seno RMS;</li>'
      '<li><strong>richiesto</strong>: 2,7 V RMS × il guadagno <em>misurato</em> a 0 V × '
      f'l&rsquo;attenuazione del trim <em>misurata</em> ({sez("s6")});</li>'
      '<li><strong>margine</strong> = 20·log<sub>10</sub>(limite / richiesto).</li></ul>')
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">trim 0 dB</th>'
      '<th class="num">trim &minus;6 dB</th><th class="num">trim &minus;12 dB</th></tr>')
    for m in MODES:
        cells = []
        for p in ("0", "6", "12"):
            val = hr["modes"][m]["trim"][p]["M1"]
            s = f"{sg(val)} dB"
            cells.append(f'<td class="num">{"<strong>" + s + "</strong>" if (m, p) == ("10db", "6") else s}</td>')
        A(f'<tr><td>M1 &middot; {MLAB[m]}</td>{"".join(cells)}</tr>')
    A('</table></div>')
    t10 = hr["modes"]["10db"]["trim"]
    A(f'<p><strong>La cifra per NC-009 è {sg(t10["6"]["M1"])} dB</strong>: +10 dB, trim a '
      f'&minus;6 dB, metrica M1. Il caso raggiungibile per errore, +10 dB col trim a 0 dB, '
      f'lascia <strong>{sg(t10["0"]["M1"])} dB</strong>; il LED del trim (ADR-027) lo rende '
      'visibile.</p>')
    A('<p>Le altre due cifre che circolavano misurano cose diverse, e restano solo '
      'etichettate:</p>')
    A('<div class="tablewrap"><table><tr><th>+10 dB</th><th class="num">trim 0 dB</th>'
      '<th class="num">trim &minus;6 dB</th><th class="num">trim &minus;12 dB</th></tr>')
    for name, lab in (("M1", "<strong>M1</strong> &mdash; 1 % contro il richiesto misurato &mdash; <strong>la cifra</strong>"),
                      ("M2", "M2 &mdash; saturazione contro il richiesto nominale (ADR-015)"),
                      ("M3", "M3 &mdash; 1 % contro il richiesto nominale (dossier fino a L32)")):
        A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{sg(t10[p][name])} dB</td>'
                                          for p in ("0", "6", "12")) + '</tr>')
    A('</table></div>')
    A(f'<p class="meta">Ricontrollata su tutte le nove celle contro '
      f'<code>{hr.get("script", "headroom_nc009.py")}</code>, lanciato sugli stessi CSV e '
      'con le stesse attenuazioni. Il richiesto nominale è 2,7 V RMS × 10<sup>(G+T)/20</sup> '
      'coi valori di targa del modo e del trim.</p>')

    # --- 9 PSRR ---
    A(h2("s9"))
    A(prov_line("tb_zout_psrr_noise.cir", sa(L64D, "tb_zout_psrr_noise")))
    A(figure("fig_psrr.svg", "PSRR"))
    A('<div class="tablewrap"><table><tr><th>Rail e modo</th><th class="num">100 Hz</th>'
      '<th class="num">1 kHz</th><th class="num">10 kHz</th><th class="num">100 kHz</th></tr>')
    for rail in ("p", "m"):
        for m in MODES:
            r = psrr[(rail, m)]
            A(f'<tr><td>rail {"+" if rail == "p" else "−"} &middot; {MLAB[m]}</td>'
              + "".join(f'<td class="num">{fx(r[k], 2)} dB</td>' for k in ("p100", "p1k", "p10k", "p100k"))
              + '</tr>')
    A('</table></div>')
    wk = min(psrr, key=lambda k: psrr[k]["p10k"])
    A(f'<p>Il lato debole è il rail {"positivo" if wk[0] == "p" else "negativo"} a '
      f'{MLAB[wk[1]]}: <strong>{fx(psrr[wk]["p10k"], 2)} dB a 10 kHz</strong>. Sul rail '
      'positivo la cella RC per blocco (ADR-056) filtra specchio e VAS. La quota di ripple '
      'che l&rsquo;alimentatore può lasciare si ricava da queste curve («Nota su E5 — la '
      'quota del ripple», ADR-020).</p>')

    # --- 10 Zout ---
    A(h2("s10"))
    A(prov_line("tb_e4_uscite.cir", e4["dir"]))
    A('<p><strong>E4</strong> chiede un&rsquo;impedenza d&rsquo;uscita &lt; 100 Ω in banda '
      'passante, misurata escludendo la reattanza del condensatore d&rsquo;accoppiamento, e '
      'costante con la posizione del volume. Il deck porta la catena intera in subckt: blocco A, '
      'buffer delle fisse, trim, volume, blocco B. Inietta 1 A AC in un jack per volta, '
      'a sorgente spenta, in ogni cella di trim &times; volume &times; modo. «Escludendo la '
      'reattanza» si legge come Re(Z) al jack: il condensatore in serie è reattanza pura, e '
      'nella parte reale resta lo scarico in parallelo, che pesa a 20 Hz.</p>')
    A('<div class="tablewrap"><table><tr><th>Uscita</th><th class="num">Celle</th>'
      '<th class="num">Re(Z) max, 20 Hz–20 kHz</th><th class="num">Re(Z) 1 kHz</th>'
      '<th class="num">|Z| 1 kHz</th><th class="num">nodo, 1 kHz</th>'
      '<th class="num">dispersione su trim &times; volume</th><th>Esito</th></tr>')
    olab = {"main": "principale", "fix1": "fissa 1", "fix2": "fissa 2"}
    for g in e4["groups"]:
        mlab = MLAB[g["modes"][0]] if len(g["modes"]) == 1 else "tre modi"

        def rng(c, nd=4):
            lo, hi = it(g[c + "_min"], nd), it(g[c + "_max"], nd)
            return lo if lo == hi else f"{lo}&ndash;{hi}"
        A(f'<tr><td>{olab[g["out"]]} &middot; {mlab}</td><td class="num">{g["n"]}</td>'
          f'<td class="num">{it(g["zrmax_max"], 4)} Ω</td><td class="num">{rng("zr1k")} Ω</td>'
          f'<td class="num">{rng("zm1k")} Ω</td><td class="num">{rng("zn1k")} Ω</td>'
          f'<td class="num">{it_sci(g["disp"], 2)} Ω</td>'
          f'{verdict(g["zrmax_max"] < E4_MAX and g["disp"] < E4_COSTANZA)}</tr>')
    A('</table></div>')
    A(f'<p class="meta">La soglia di costanza, {it(E4_COSTANZA, 0)} Ω, è la lettura di L13: E4 '
      'non dà tolleranza, e il termine di confronto è il passivo di ADR-002, che a metà corsa '
      'porta in uscita un quarto della sua resistenza. La dispersione è il massimo su Re(Z) max, '
      'Re(Z) e |Z| a 1 kHz. Le tabelle coincidono col log riga per riga; lo stesso esito lo dà '
      f'<code>{html_escape(e4.get("script", ""))}</code> sugli stessi file; la Zout al nodo e al '
      'jack del deck qui sotto coincide con quella della principale entro 10<sup>&minus;3</sup>.</p>')
    A(prov_line("tb_zout_psrr_noise.cir", z["dir"]))
    A(figure("fig_zout.svg", "Impedenza d'uscita"))
    A('<div class="tablewrap"><table><tr><th>Punto di misura</th><th class="num">20 Hz</th>'
      '<th class="num">1 kHz</th><th class="num">20 kHz</th><th class="num">100 kHz</th></tr>')
    for m in MODES:
        r = z[m]
        A(f'<tr><td>al jack &middot; {MLAB[m]}</td>' + "".join(
            f'<td class="num">{it(r[k], 4)} Ω</td>' for k in ("z20", "z1k", "z20k", "z100k")) + '</tr>')
    for m in MODES:
        r = z[m]
        A(f'<tr><td>al nodo OUT &middot; {MLAB[m]}</td>' + "".join(
            f'<td class="num">{it(r[k], 4)} Ω</td>' for k in ("za20", "za1k", "za20k", "za100k")) + '</tr>')
    A('</table></div>')
    A(f'<div class="note"><strong>Tensione fra E4 ed E8, segnalata e non aggirata.</strong> '
      f'E4 chiede &lt; 100 Ω in banda passante. Al jack a 20 Hz la |Z| vale '
      f'{it(z["0db"]["z20"], 4)} Ω, ma quella <em>è la reattanza del condensatore '
      f'd&rsquo;uscita da 4,7 µF</em>: al nodo OUT la stessa frequenza dà '
      f'{it(z["0db"]["za20"], 3)} Ω, e la parte reale al jack resta ≤ '
      f'{it(max(e4_main, e4_fix), 4)} Ω. Per questo il requisito dice «misurata escludendo la '
      'reattanza del condensatore d&rsquo;accoppiamento».</div>')

    # --- la distorsione, V4 (L51c: l'utente, «Rifarla e mostrarla») ---
    A(h2("sdist"))
    A(prov_line("thd_20k.cir", os.path.join(dist["dir"], "run", "oggi"),
                deckdir=os.path.join(dist["dir"], "deck", "oggi"),
                note=' &middot; il banco di L46a e L46b, sul blocco di oggi'))
    ds = dist["soglie"]
    A('<p><strong>V4</strong> chiede che la distorsione non abbia niente di aspro, con tetti in '
      'numeri (ADR-055). Il banco è quello con cui L46a e L46b hanno scelto la compensazione: il '
      'blocco di guadagno da solo nei tre modi, sorgente 2,5 kΩ, carico 47 Ω + 4,7 µF + 10 kΩ, '
      'a due livelli d&rsquo;uscita: 0,2 V RMS, il livello musicale scelto dall&rsquo;utente '
      '(&minus;20 dB), e 2 V RMS, la prova di stress. È stato corso di nuovo il '
      '2026-11-02 sul blocco che il sorgente genera oggi, a 27 °C uniformi; le cifre a caldo e '
      'quelle sulla catena sono sotto.</p>')
    A('<div class="tablewrap"><table><tr><th>Clausola</th><th class="num">Tetto</th>'
      '<th class="num">Il blocco di oggi, il peggiore sui tre modi</th><th>Esito</th></tr>')
    for k, lab, val, tet in (
            ("thd20_lo", "la distorsione non cresce verso gli acuti: THD a 20 kHz, 0,2 V",
             f'{pct(dist["thd_lo"]["20k"])} %', f'{pct(ds["thd20_lo"], tetto=True)} %'),
            ("h5", "le armoniche dalla 5ª in su, 0,2 V, 1 / 10 / 20 kHz",
             f'{fx(dist["h5_lo"], 1)} dB', f'{fx(ds["h5"], 0)} dB'),
            ("imd", "l&rsquo;intermodulazione, 19 + 20 kHz, il prodotto a 1 kHz, 0,2 V",
             f'{fx(dist["imd_lo"], 1)} dB', f'{fx(ds["imd"], 0)} dB'),
            ("thd20_hi", "prova di stress: THD a 20 kHz, 2 V",
             f'{pct(dist["thd_hi_20k"])} %', f'{pct(ds["thd20_hi"], tetto=True)} %')):
        A(f'<tr><td>{lab}</td><td class="num">≤ {tet}</td><td class="num">{val}</td>'
          f'{verdict(dist["ok"][k])}</tr>')
    A('</table></div>')
    A('<div class="tablewrap"><table><tr><th>Modo</th><th class="num">THD 1 kHz</th>'
      '<th class="num">THD 10 kHz</th><th class="num">THD 20 kHz</th>'
      '<th class="num">intermodulazione</th><th class="num">THD 20 kHz a 2 V</th></tr>')
    for modo in ("0", "3", "10"):
        def cell(deck, liv, col):
            r = [x for x in dist["rows"] if x["deck"] == deck and x["modo"] == modo
                 and x["livello"] == liv]
            return float(r[0][col]) if len(r) == 1 else float("nan")
        A(f'<tr><td>{MLAB[modo + "db"]}</td>'
          + "".join(f'<td class="num">{pct(cell(d, "lo", "thd_pct"))} %</td>'
                    for d in ("thd_1k", "thd_10k", "thd_20k"))
          + f'<td class="num">{fx(cell("imd", "lo", "imd_d2_db"), 1)} dB</td>'
          f'<td class="num">{pct(cell("thd_20k", "hi", "thd_pct"))} %</td></tr>')
    A('</table></div>')
    A(f'<p class="meta">Tre controlli. La THD che ngspice stampa nel log, caso per caso, coincide '
      'con la tabella di <code>leggi_four.py</code>. Il blocco corso è '
      '<code>spice/preamp/gain_block_flat.inc</code> di oggi, uguale byte per byte, e i deck sono '
      'quelli di L46b a meno del blocco incluso. La seconda strada è la corsa di L51c sullo stesso '
      f'banco col blocco del 2026-10-10 (<code>{html_escape(rel(os.path.join(dist["l51c_dir"], "run", "oggi")))}/</code>): '
      'il blocco è cambiato, quindi le cifre non coincidono e lo scarto si scrive. La THD a 20 kHz, '
      f'0,2 V, era {pct(dist["thd_20k_l51c"])} % ed è {pct(dist["thd_lo"]["20k"])} %; '
      f'fra i 24 casi la THD si sposta al più di {fx(dist["scarto_thd_db"], 1)} dB e '
      f'l&rsquo;intermodulazione al più di {fx(dist["scarto_imd_db"], 1)} dB.</p>')
    A('<h3>A caldo: ogni giunzione alla sua temperatura</h3>')
    A(f'<p class="prov">Dati <code>{html_escape(rel(os.path.join(dist["caldo_dir"], "sintesi_caldo.csv")))}</code> '
      '(L66, la variante che ADR-111 ha portato nel sorgente)</p>')
    A('<p>Lo stesso banco col blocco a caldo: ogni dispositivo alla temperatura che raggiunge '
      'col proprio calore, a 27 °C e a 57 °C d&rsquo;aria, col rame del layout o col rame minimo. '
      'Il tetto della THD a 20 kHz è quello di V4 al livello del caso.</p>')
    A('<div class="tablewrap"><table><tr><th>Aria, rame</th><th class="num">Fuori</th>'
      '<th class="num">Margine minimo</th><th class="num">THD 20 kHz, 0,2 V</th>'
      '<th class="num">THD 20 kHz, 2 V</th><th class="num">Intermodulazione</th></tr>')
    for c in dist["caldo"]:
        aria, rame = c["cond"].split("_")
        A(f'<tr><td>{aria[1:]} °C, {"rame del layout" if rame == "rame" else "rame minimo"}</td>'
          f'<td class="num">{c["fuori"]} su 12</td><td class="num">{fx(c["margine"], 1)} dB</td>'
          f'<td class="num">{pct(c["thd_lo"])} %</td><td class="num">{pct(c["thd_hi"])} %</td>'
          f'<td class="num">{fx(c["imd"], 1)} dB</td></tr>')
    A('</table></div>')
    A('<p class="meta">Seconda strada: le 48 THD del deck di L66 rifatte da L67 col blocco avvolto '
      f'in un sottocircuito (<code>{html_escape(rel(os.path.join(dist["catena_dir"], "noto_caldo.csv")))}</code>) '
      'ridanno i massimi di questa tabella alla cifra.</p>')
    A('<h3>Sulla catena: ogni blocco al suo livello</h3>')
    A(f'<p class="prov">Dati <code>{html_escape(rel(dist["catena_dir"]))}/</code> (L67, ADR-112)</p>')
    cg = dist["catena"]
    A('<p>Il blocco da solo non dice tutto: sulla catena di un canale il blocco prima del volume '
      'lavora al livello della sorgente, che può essere più alto di quello all&rsquo;uscita. Per '
      'decisione dell&rsquo;utente (ADR-112, «Ogni blocco al suo livello») la THD a 20 kHz si '
      'giudica al livello a cui ogni blocco lavora: il tetto scala da '
      f'{pct(ds["thd20_lo"], tetto=True)} % a 0,2 V a {pct(ds["thd20_lo"] * 10, tetto=True)} % a 2 V, '
      'e alla principale vale il livello più alto lungo il percorso.</p>')
    A('<div class="tablewrap"><table><tr><th>Il blocco, la temperatura</th><th class="num">Casi</th>'
      '<th class="num">Fuori, ogni blocco al suo livello</th><th class="num">Margine minimo</th>'
      '<th class="num">Fuori, V4 letto alla lettera</th></tr>')
    nomi = {"l56": "il blocco di L56", "oggi": "il blocco di oggi, 27 °C",
            "caldo_t27_rame": "a caldo, 27 °C, rame del layout", "caldo_t27_minima": "a caldo, 27 °C, rame minimo",
            "caldo_t57_rame": "a caldo, 57 °C, rame del layout", "caldo_t57_minima": "a caldo, 57 °C, rame minimo"}
    for k in ("oggi", "caldo_t27_rame", "caldo_t27_minima", "caldo_t57_rame", "caldo_t57_minima", "l56"):
        if k in cg:
            x = cg[k]
            A(f'<tr><td>{nomi[k]}</td><td class="num">{x["n"]}</td><td class="num">{x["fuori"]}</td>'
              f'<td class="num">{fx(x["margine"], 1)} dB</td><td class="num">{x["fuori_v4"]}</td></tr>')
    A('</table></div>')
    ic = dist["imd_catena"]
    A(f'<p>L&rsquo;intermodulazione sulla catena: <strong>{ic["fuori"]} casi su {ic["n"]}</strong> '
      f'oltre il tetto di {fx(ds["imd"], 0)} dB, margine minimo {fx(ic["margine"], 1)} dB.</p>')
    A('<p class="meta">Seconda strada: la regola di ADR-112 è scritta di nuovo in questo generatore '
      'e applicata alle corse della catena; dà, riga per riga, i margini e i verdetti di '
      '<code>verifica_livello.csv</code>. I margini dell&rsquo;intermodulazione tornano dal tetto '
      'letto in <code>REQUIREMENTS.md</code>.</p>')
    A('<div class="note"><strong>Cifre di modello, non misure.</strong> I dispositivi usano i '
      f'modelli del costruttore ({sez("s15")}); dove la misura sul prototipo diverge, vale la '
      'misura. Il banco è il blocco da solo: il selettore, il trim, il volume e i buffer delle '
      'uscite fisse non ci sono, e il tetto complessivo di THD+N si fissa con l&rsquo;utente sulle '
      'prime misure del prototipo.</div>')

    # --- 11 V2 ---
    A(h2("s11"))
    A(prov_line("tb_switch_v2.cir", v2["dir"]))
    A('<p><strong>V2</strong>: l&rsquo;anello non si apre mai commutando. Il deck modella '
      'K1 e K5 come contatti veri, con rimbalzi in chiusura e in apertura, e percorre '
      'ogni passaggio fra 0, +3 e +10 dB, compresi i due ordini in cui una coppia di relè '
      'può arrivare sul salto diretto. La previsione falsificabile: v(OUT) resta '
      'nell&rsquo;inviluppo del regime a +10 dB in ogni istante.</p>')
    A('<div class="tablewrap"><table><tr><th>Finestra</th><th class="num">v(OUT) max</th>'
      '<th class="num">v(OUT) min</th><th>Dentro l&rsquo;inviluppo del +10 dB</th></tr>')
    for x in v2["rows"]:
        A(f'<tr><td>{x["lab"]}</td><td class="num">{fx(x["vmax"], 4)} V</td>'
          f'<td class="num">{fx(x["vmin"], 4)} V</td>{verdict(x["inside"], "sì", "no")}</tr>')
    A('</table></div>')
    A(f'<p>Inviluppo del regime a +10 dB: {sg(v2["env_hi"], 4)} / {sg(v2["env_lo"], 4)} V. '
      f'Estremi sull&rsquo;intera corsa di 70 ms, rimbalzi compresi: {sg(v2["gmax"], 4)} / '
      f'{sg(v2["gmin"], 4)} V. La forma d&rsquo;onda non è versionata; le finestre sono '
      'confrontate con le <code>meas</code> del log.</p>')
    A('<h3>Il controfattuale: il relè nel ramo sbagliato</h3>')
    A(prov_line("tb_switch_v2_counterfactual.cir", cf["dir"]))
    A('<p>ADR-004 ha <strong>scartato</strong> il contatto in serie a R<sub>f</sub>. Una '
      'decisione porta informazione solo se la disposizione scartata è mostrata '
      '<em>fallire</em>: con R<sub>f</sub> aperto non esiste più controreazione, e '
      f'l&rsquo;uscita va a <strong>{fx(cf["rows"][1]["vout"], 4)} V</strong>, dove lo stadio '
      'non amplifica più niente.</p>')
    A(figure("fig_counterfactual.svg", "Controfattuale del relè di guadagno"))
    A('<div class="tablewrap"><table><tr><th>Stato</th><th>Configurazione</th>'
      '<th class="num">v(OUT)</th><th class="num">v(FB)</th></tr>')
    for r in cf["rows"]:
        A(f'<tr><td><strong>{r["tag"]}</strong></td><td>{html_escape(r["desc"])}</td>'
          f'<td class="num"><strong>{fx(r["vout"], 6)} V</strong></td>'
          f'<td class="num">{fx(r["vfb"], 6)} V</td></tr>')
    A('</table></div>')
    A('<p>C esiste per escludere che B sia un artefatto del solutore: A e C coincidono. '
      'La disposizione scelta commuta R<sub>g</sub> verso massa, e i due rami di ADR-026 '
      'stanno in parallelo: a contatti aperti il guadagno è 1 e <strong>l&rsquo;anello non '
      'si apre mai</strong>.</p>')

    # --- il mute ---
    A(h2("smute"))
    A(prov_line("tb_v2_casopeggiore.cir", mu["mat_dir"],
                note=f" &middot; la matrice intera, {mu['n_corse']} corse, ricorsa il 2026-11-02"))
    A('<p>Il mute taglia coi soli relè al jack (ADR-062, PR-21): con la musica il silenzio '
      'arriva di colpo, e al rilascio la musica torna di colpo al livello di prima. Un relè per '
      'uscita, geometria iii (ADR-044): comune sul lato del condensatore, NO sul jack, NC a '
      'massa, uno scarico su entrambi i lati. Guadagno, trim e volume si cambiano col jack '
      f'staccato ({sez("sint")}).</p>')
    A('<p>V2 si giudica (ADR-032, ADR-063) con <strong>A</strong>, il gradino senza musica '
      'all&rsquo;inserzione e al rilascio, e <strong>B2</strong>, il residuo al jack a mute '
      'inserito senza musica; con la musica, il residuo è la musica che passa davvero: '
      '<strong>B2g</strong>, il jack grezzo nella finestra del mute, e <strong>B1</strong>, il '
      'riferimento sempre in mute. Soglia 100 µV di picco per tutte (~'
      f'{dbspl(100e-6)}). Il clic del taglio non ha soglia: si misura e si dichiara '
      '(ADR-062).</p>')
    A('<h3>La matrice, peggiore per gruppo</h3>')
    A('<div class="tablewrap"><table><tr><th>Gruppo</th><th class="num">Verdetti</th>'
      + "".join(f'<th class="num">{lab}, peggiore</th>' for lab, _, _ in V2_COLONNE)
      + '<th>Esito</th></tr>')

    def cellv(m):
        if m is None:
            return '<td class="num">&mdash;</td>'
        return (f'<td class="num"><strong>{uv(m["v"])}</strong><br><span class="na">'
                f'{html_escape(m["cella"])} &middot; {m["uscita"].lower()}</span></td>')
    for r in mu["rows"]:
        A(f'<tr><td>{r["gruppo"]} &middot; {r["lab"]}</td><td class="num">{r["n"]}</td>'
          + "".join(cellv(r[lab]) for lab, _, _ in V2_COLONNE)
          + verdict(r["fuori"] == 0, "regge", f'{r["fuori"]} fuori') + '</tr>')
    A('</table></div>')
    A(f'<p><strong>{mu["n"] - mu["n_fuori"]} verdetti su {mu["n"]} reggono</strong>; altre '
      f'{mu["n_dich"]} grandezze sono dichiarate (il clic e, con la musica, la coda del filtro '
      'dopo il taglio). Ogni verdetto è il peggiore sulle tre uscite; il dossier li ricalcola da '
      '<code>analisi.csv</code> e dal manifesto, con la regola di <code>verdetto.py</code> '
      f'scritta di nuovo, e li confronta con <code>verdetto.csv</code> uno per uno. Le '
      f'{mu["escluse"]} corse di spegnimento sono escluse come in L29d2 (lo spegnimento vero è '
      'quello morbido dell&rsquo;alimentatore), e '
      + ", ".join(f'<code>{html_escape(c)}</code>' for c in mu["via"])
      + ' manca dal manifesto finale perché la corsa abortisce. '
      f'La seconda strada è la matrice di L60d2, corsa il 2026-10-19 sul blocco di allora: '
      f'gli esiti coincidono uno per uno. Il picco giudicato più alto è {uv(mu["l60d2_picco_oggi"])} '
      f'oggi e {uv(mu["l60d2_picco"])} in L60d2, e da una matrice all&rsquo;altra un picco si sposta '
      f'al più di {uv(mu["l60d2_scarto_v"])}: sono le celle del cambio di guadagno, B2g, che '
      'stanno fra il pavimento del metodo e pochi µV, in tutte e due le direzioni. '
      f'{len(mu["nodeset"])} celle della dispersione non trovano il punto di lavoro sul blocco di '
      'oggi, in nessuna delle tre prove del banco: sono corse col punto di partenza del blocco da '
      'solo (limitations #86), che non cambia la soluzione dove il punto di lavoro si trova anche '
      'senza (provato su tre celle: le grandezze di V2 si spostano al più di 0,64 µV)'      + '. Il deck rigenerato oggi dal sorgente è uguale byte per byte a quello versionato.</p>')
    A(f'<p>Il gruppo 6, lo scatto del volume nel banco di V2, porta il difetto noto del banco '
      '(l&rsquo;offset del primo stadio davanti a R<sub>IN</sub>, limitations #44): con '
      f'quell&rsquo;offset tolto lo stesso evento vale {uv(mu["vosb0"])}.</p>')
    A('<h3>Il clic del taglio, dichiarato</h3>')
    A('<div class="tablewrap"><table><tr><th>Uscita</th><th>Tono</th><th>Evento</th>'
      '<th class="num">Carico</th><th class="num">C2, picco</th><th class="num">di picco a 1 m</th>'
      '<th class="num">taglio ideale</th><th class="num">circuito meno ideale</th></tr>')
    for r in mu["clic"]:
        A(f'<tr><td>{html_escape(r["uscita"])}</td><td>{html_escape(r["tono"])}</td>'
          f'<td>{html_escape(r["evento"])}</td><td class="num">{lab_c(r["carico"])}</td>'
          f'<td class="num">{uv(float(r["c2_V"]))}</td><td class="num">{dbspl(float(r["c2_V"]))}</td>'
          f'<td class="num">{uv(float(r["ideale_V"]))}</td>'
          f'<td class="num">{sg(float(r["circuito_meno_ideale_dB"]))} dB</td></tr>')
    A('</table></div>')
    A('<p>Il clic è la differenza fra la musica prima e dopo il taglio, letta con lo stesso C2 '
      'di <code>v2_metodo.py</code>, sul carico peggiore dei due di V2. Su un taglio netto C2 '
      'vale quanto la musica che sparisce, ed è per questo che i dB SPL sono quelli della '
      'musica stessa. Accanto, il taglio ideale: la stessa musica tagliata in zero tempo. Il '
      'clic vero è l&rsquo;ultima colonna, quello che il circuito '
      'aggiunge o toglie: all&rsquo;inserimento quasi niente, al rilascio a 1 kHz i rimbalzi '
      'del contatto che chiude, a 20 Hz il condensatore riporta la musica piano. La colonna C2 '
      'è ricontrollata contro <code>analisi.csv</code>, i dB SPL contro la catena di NC-028; '
      'il taglio ideale viene dalle forme d&rsquo;onda, che non sono versionate, e ha una sola '
      'strada.</p>')

    # --- l'interblocco ---
    A(h2("sint"))
    A('<p>Guadagno e trim si cambiano solo a mute inserito, e il guadagno si tiene da sé '
      '(ADR-041, strada B di ADR-030): due relè ausiliari in autoritenuta sui relè del '
      'guadagno, un polo ponte per bobina sul rotativo, i LED dagli ausiliari. Il permissivo '
      'ha un comando proprio, sfasato dopo i jack (ADR-045); comandi e LED stanno su header '
      'verso il pannello (ADR-028).</p>')
    A(f'<p class="prov">Netlist <code>{html_escape(il["net"])}</code> &middot; '
      '<code>scripts/check_relay_safe_state.py</code> (il 2e di <code>run_tests.sh</code>), '
      'rieseguito da questa pagina</p>')
    A('<div class="tablewrap"><table><tr><th>Relè</th><th>Parte e sigla</th><th>Ruolo</th></tr>')
    for k, part, role in il["relays"]:
        A(f'<tr><td>{k}</td><td>{html_escape(part)}</td><td>{role.lower()}</td></tr>')
    A('</table></div>')
    g = il["guad"]
    A(f'<p>Sulla netlist di oggi il 2e prova per raggiungibilità: {il["stati_trim"]} stati dei '
      f'bistabili del trim fuori mute, nella finestra del permissivo e in mute; per il guadagno '
      f'({html_escape(g[0]) if g else "?"}) {g[1] if g else "?"} coppie stato/posizione e '
      f'{g[2] if g else "?"} trasferimenti con la manopola allo stato; e riconosce i '
      f'{len(il["ingressi"])} ingressi del selettore e i {len(il["volume"])} volumi. Che il '
      'controllo sappia cadere lo dicono i falsi: '
      + "; ".join(f'{lot}, {v["n"]} netlist sabotate, tutte respinte per la ragione voluta'
                  for lot, v in il["falsi"].items())
      + ' (quelli di L48b sulla netlist di oggi).</p>')
    A('<h3>La corsa al rilascio del mute</h3>')
    A(f'<p class="prov">Dati <code>{html_escape(rel(il["corsa_dir"]))}/</code> &middot; un deck '
      'ngspice per cella, scritto da <code>corsa.py</code>: bobine, contatti e ausiliari, '
      'nessun transistor; il modello del relè è dichiarato nel suo docstring</p>')
    A('<div class="tablewrap"><table><tr><th>Variante</th><th class="num">Celle</th>'
      '<th class="num">Cade al rilascio</th><th class="num">Cade all&rsquo;inserimento</th></tr>')
    vlab = {"ingenua": "senza polo ponte", "progetto": "<strong>il progetto</strong>, col polo ponte"}
    for var in ("progetto", "ingenua"):
        c = il["corsa"].get(var, {})
        A(f'<tr><td>{vlab[var]}</td><td class="num">{c.get("n", "?")}</td>'
          f'<td class="num">{c.get("ril", "?")}</td><td class="num">{c.get("ins", "?")}</td></tr>')
    A('</table></div>')
    A(f'<p>{il["corsa_n"]} corse: induttanza della bobina, buco del permissivo, resistenza, soglia '
      'di rilascio e tensione dei relè spazzate. La corsa è chiusa <em>per struttura</em>, dal '
      'polo ponte: il datasheet non dà la dinamica della bobina, e il modello del relè è '
      'dichiarato, non del costruttore. I conteggi sono ricontati da <code>corsa.csv</code> e '
      'confrontati con <code>sintesi.txt</code>. La corsa è di L36: l&rsquo;interblocco del '
      'guadagno non è cambiato da allora.</p>')

    # --- 12 V3, P7 ---
    A(h2("s12"))
    A(prov_line("tb_v3_overload.cir", v3["dir"]))
    A('<p><strong>V3</strong>, recupero dalla saturazione: +10 dB, 1 kHz, pilotato oltre '
      'il clipping per alcuni cicli e poi riportato a un livello basso.</p>')
    A('<div class="tablewrap"><table><tr><th>Grandezza</th><th class="num">Valore</th></tr>')
    A(f'<tr><td>v(OUT) massima, in clipping</td><td class="num">{sg(v3["vmax"], 3)} V</td></tr>')
    A(f'<tr><td>v(OUT) minima, in clipping</td><td class="num">{sg(v3["vmin"], 3)} V</td></tr>')
    A(f'<tr><td>v(JACK) a fine corsa, {fx(v3["t_end"] * 1000, 0)} ms</td>'
      f'<td class="num">{sg(v3["jack_end"] * 1000, 2)} mV</td></tr>')
    A('</table></div>')
    A('<p class="meta">Questi tre numeri hanno una sola strada: il deck non stampa '
      '<code>print</code>, quindi vengono dal CSV senza controllo incrociato. La cifra '
      '<code>.four</code> del deck non è riportata: è presa in saturazione, e la distorsione '
      f'si giudica nella {sez("sdist")}.</p>')
    A('<h3>P7: ogni uscita regge un corto, il mute si tiene a tempo indefinito</h3>')
    A(prov_line("tb_mute_corto.cir", p7["dir"]))
    A(f'<p>Criterio di ADR-021: Tj = {it(TA, 3)} °C + P<sub>media</sub> · R<sub>θJA</sub> ≤ '
      f'{it(TJ_MAX, 3)} °C, con R<sub>θJA</sub> = {it(RTH_MJE_DISS, 3)} °C/W per i MJE col '
      'dissipatore di ADR-099 (20 °C/W del dissipatore a 1 W, 2,5 giunzione-case, 2 '
      f'd&rsquo;interfaccia, ipotesi; senza dissipatore sarebbero {it(RTH_MJE, 3)}). '
      'Casi: normale, mute, corto su ciascuna uscita, apparecchio spento su una fissa; '
      'manopola e ampiezza spazzate, 1 kHz e 20 kHz. Il dispositivo d&rsquo;uscita peggiore '
      'per blocco e modo:</p>')
    A('<div class="tablewrap"><table><tr><th>Blocco</th>'
      + "".join(f'<th class="num">{MLAB[m]}</th>' for m in MODES) + '<th>Esito</th></tr>')
    for blk, lab in (("A", "Blocco A"), ("F1", "Buffer fissa 1"), ("F2", "Buffer fissa 2"), ("B", "Blocco B")):
        ws = [p7["worst"].get((blk, m)) for m in ("0", "3", "10")]
        A(f'<tr><td>{lab}</td>' + "".join(
            f'<td class="num">{it(w["p"] * 1000, 4)} mW &middot; {fx(w["tj"], 1)} °C</td>' if w else
            '<td class="num">&mdash;</td>' for w in ws)
          + verdict(all(w and w["tj"] <= TJ_MAX for w in ws)) + '</tr>')
    A('</table></div>')
    A(f'<p>Classe A sui percorsi ascoltabili (ADR-023): <strong>{p7["n_bad"]} righe su '
      f'{p7["n_listen"]}</strong> ne escono. La 47 Ω dell&rsquo;uscita principale dissipa al '
      f'massimo {it(p7["rsep"]["0"], 3)} / {it(p7["rsep"]["3"], 3)} / {it(p7["rsep"]["10"], 3)} W '
      'a 0 / +3 / +10 dB, e va dimensionata di conseguenza.</p>')

    # --- il blocco di oggi: i guasti e il calore (L64a: L66, ADR-099, ADR-111) ---
    gb = M["gb"]
    A(h2("sprot"))
    A(f'<p class="prov">Dati <code>{html_escape(rel(os.path.join(gb["dir"], "calore_dopo.csv")))}</code> '
      '(L66, sul sorgente di oggi)</p>')
    A('<p>Da L51 il blocco è cambiato per i suoi guasti, non per il suono: l&rsquo;inseguitore '
      'davanti al VAS con la sua resistenza (ADR-067, ADR-087), quattro diodi di riserva al '
      'moltiplicatore e un diodo sulla base di ciascun finale (ADR-090, ADR-095), R153 sdoppiata '
      '(ADR-097), quattro rimedi del calore e un dissipatore sui finali (ADR-099), e il limitatore '
      'del VAS a 36,5 + 18,7 Ω (ADR-111). Ogni guasto singolo di ogni parte del blocco, in ognuna '
      f'delle posizioni, è stato simulato col blocco di oggi: <strong>{gb["n"]} modi</strong>.</p>')
    w = gb["w"]
    A('<div class="tablewrap"><table><tr><th>Con 60 °C d&rsquo;aria</th><th class="num">Valore</th>'
      '<th>Esito</th></tr>')
    A(f'<tr><td>la giunzione più calda, su tutti i modi ({html_escape(w["Tj_max_disp_60"].upper())}, '
      f'{html_escape(w["modo"])}, blocco {html_escape(w["posizione"])})</td>'
      f'<td class="num">{fx(gb["tjmax"], 0)} °C</td>{verdict(gb["tjmax"] <= TJ_MAX)}</tr>')
    A(f'<tr><td>il finale più caldo, col dissipatore ({html_escape(gb["fin"]["modo"])})</td>'
      f'<td class="num">{fx(gb["fin_tj"], 0)} °C</td>{verdict(gb["fin_tj"] <= TJ_MAX)}</tr>')
    A(f'<tr><td>modi oltre {it(TJ_MAX, 3)} °C (P7)</td><td class="num">{gb["oltre"]}</td>'
      f'{verdict(gb["oltre"] == 0)}</tr>')
    A(f'<tr><td>a riposo, 57 °C d&rsquo;aria: il finale / la giunzione più calda</td>'
      f'<td class="num">{fx(gb["riposo_fin_57"], 1)} / {fx(gb["riposo_max_57"], 1)} °C</td><td></td></tr>')
    A('</table></div>')
    if gb["oltre_txt"]:
        modi = sorted({m for m, _ in gb["oltre_txt"]})
        A(f'<p>Oltre i loro limiti vanno parti che non sono giunzioni, in {gb["oltre_flag"]} modi '
          f'({html_escape(", ".join(modi))}): '
          + "; ".join(html_escape(x) for x in sorted({f for _, f in gb["oltre_txt"]}))
          + '. È la non conformità NC-075, aperta, che si chiude con la scelta della parte.</p>')
    A(f'<p class="meta">Seconda strada: la temperatura dei finali e del VAS rifatta qui dalla potenza '
      f'di ogni modo ({it(TA, 3)} °C + P · {it(RTH_MJE_DISS, 3)} °C/W per i finali, '
      f'{it(RTH_VAS, 3)} °C/W per il VAS) torna, al grado, quella del file.</p>')

    # --- la Stax (L64a: ADR-081, ADR-085, ADR-086, P10) ---
    st = M["stax"]
    A(h2("sstax"))
    A('<p>La fissa 2 alimenta le cuffie elettrostatiche Stax: il suo condensatore d&rsquo;uscita è '
      'da 1 µF film (ADR-081), prima del relè di mute (ADR-084), e il relè ha l&rsquo;isolamento '
      'supplementare fra bobina e contatti (ADR-085). Un guasto singolo della scheda audio '
      f'mentre si ascolta può tenere il jack sopra 0,87 V al più <strong>{fx(st["soglia"], 0)} ms</strong> '
      '(P10, ADR-086), col carico della Stax.</p>')
    A('<div class="tablewrap"><table><tr><th>I guasti</th><th class="num">Modi</th>'
      '<th class="num">Il più lungo sulla Stax</th><th>Esito</th></tr>')
    for x in st["parti"]:
        A(f'<tr><td>{html_escape(x["lab"])}: <code>{html_escape(rel(x["path"]))}</code></td>'
          f'<td class="num">{x["n"]}</td><td class="num">{fx(x["max"], 1)} ms '
          f'({html_escape(x["modo"])})</td>{verdict(x["fuori"] == 0)}</tr>')
    A('</table></div>')
    A('<p class="meta">I modi che il limitatore del VAS tocca sono ricorsi sul sorgente di oggi; gli '
      'altri vengono dal lotto che li ha introdotti, prima del limitatore. La colonna «p10» di '
      'quei file è giudicata contro 100 ms, una soglia di prima di ADR-086: qui il tetto è letto '
      'da <code>REQUIREMENTS.md</code>. Seconda strada: per ogni riga il tempo sopra la soglia non '
      'supera l&rsquo;ultimo istante sopra la soglia, e il massimo delle tre uscite è quello '
      'dichiarato.</p>')

    if psu:
        heat = M["heat"]
        # --- il calore (L51b: le potenze dal banco di oggi, l'utente: «Sì, così») ---
        A(h2("sheat"))
        A(f'<p class="prov">Script <code>{html_escape(rel(os.path.join(heat["dir"], "stima_telaio_l64b.py")))}</code>'
          f' &middot; le potenze dal banco <code>{html_escape(rel(os.path.join(heat["dir"], "tb_calore.cir")))}</code>,'
          ' rigenerato da questa pagina dal deck della rete di oggi e uguale a quello corso &middot; '
          '<strong>stima calcolata</strong>, il ferro dei trasformatori è un&rsquo;ipotesi; rieseguita '
          'da questa pagina</p>')
        A('<p>P5 e ADR-021 chiedono 60 °C nel telaio, dentro un vano di libreria chiuso, con la '
          'stanza a 35 °C. La scheda audio non è sola nel telaio: la stima somma tutto '
          'l&rsquo;apparecchio (ADR-047). Il modello del telaio e del vano è quello di L30; le '
          'potenze non sono più stimate a mano. Il banco dell&rsquo;alimentatore di oggi, col '
          'carico di oggi, a regime con la musica e ogni bobina dello stato accesa, dà la potenza '
          'che esce dai secondari e dove va: il rame degli avvolgimenti, i due ponti, i tre '
          'regolatori, quello che la linea a 12 V consegna alle bobine. Le tre colonne sono la rete '
          'nominale, −10 % e +10 %.</p>')
        A('<div class="tablewrap"><table><tr><th>Dissipazione</th><th class="num">nominale</th>'
          '<th class="num">rete −10 %</th><th class="num">rete +10 %</th></tr>')
        for k, a, b, c in heat["parts"] + ([heat["tot"]] if heat["tot"] else []):
            strong = k == "TOTALE"
            cells = "".join(f'<td class="num">{"<strong>" if strong else ""}{fx(x, 2)} W'
                            f'{"</strong>" if strong else ""}</td>' for x in (a, b, c))
            # il trasformatore piccolo si chiama come il requisito T2: des()
            lab = html_escape(k).replace("T2", des("T2"))
            A(f'<tr><td>{"<strong>totale</strong>" if strong else lab}</td>{cells}</tr>')
        A('</table></div>')
        A('<div class="tablewrap"><table><tr><th>Gioco del vano</th><th>Caso</th>'
          '<th class="num">P</th><th class="num">salto del telaio</th><th class="num">salto del vano</th>'
          '<th class="num">aria nel telaio</th><th>60 °C</th></tr>')
        for gio, caso, p_, dtt, dtv, tin in heat["vano"]:
            A(f'<tr><td>{html_escape(gio.replace(".", ","))}</td><td>{caso}</td>'
              f'<td class="num">{fx(p_, 1)} W</td><td class="num">{fx(dtt, 1)} °C</td>'
              f'<td class="num">{fx(dtv, 1)} °C</td><td class="num"><strong>{fx(tin, 1)} °C</strong></td>'
              f'{verdict(tin <= TA)}</tr>')
        A('</table></div>')
        bn = heat["bench"].get("regime_nom", {})
        resto_w = next((p[1] for p in heat["parts"] if p[0].startswith("il resto")), float("nan"))
        h3 = next((v for v in heat["vano"] if v[0] == "3 cm" and v[1] == "peggiore"), None)
        k_w = (h3[3] + h3[4]) / h3[2] if h3 else float("nan")
        ferro = sum(p[3] for p in heat["ipotesi"])
        A(f'<p>Il vano chiuso regge i 60 °C nel caso peggiore con almeno '
          f'<strong>{it(heat["gioco"], 3)} cm</strong> di gioco per lato. Il bilancio torna: a rete '
          f'nominale dai secondari escono {it(bn.get("pt1", 0) + bn.get("pt2", 0), 4)} W, e le voci li '
          f'nominano tutti tranne {it(resto_w, 2)} W (i partitori, le resistenze serie dei condensatori, '
          'le correnti di riposo). La scheda audio della stima coincide coi rail di <code>tb_op</code> '
          f'di oggi, 8 &times; 15 V &times; (|i<sub>+</sub>| + |i<sub>&minus;</sub>|) = '
          f'{it(8 * heat["p_blk"], 4)} W; il banco la carica con le stesse correnti ai rail veri, '
          f'{it(bn.get("paud", float("nan")), 4)} W. Il ferro dei due trasformatori non è nel banco (una '
          f'sorgente ideale con la resistenza e l&rsquo;induttanza in serie): {fx(ferro, 2)} W nel caso '
          'peggiore, un&rsquo;ipotesi dichiarata nello script; ogni watt in più vale '
          f'~{it(k_w, 2)} °C nel vano a 3 cm. La conferma è la temperatura nel telaio del prototipo '
          '(ADR-021, «Da riaprire se»).</p>')
        # L64b: l'ultimo dossier (L51b) contro oggi, dai due file della stima
        t51 = heat["l51b"].get("TOTALE", (float("nan"),) * 3)
        A(f'<p>L&rsquo;ultimo dossier (L51b, il micro e la scheda audio di prima di L66) dava '
          f'{fx(t51[0], 2)} / {fx(t51[1], 2)} / {fx(t51[2], 2)} W e {it(heat["gioco_l51b"], 2)} cm di '
          f'gioco minimo; oggi {fx(heat["tot"][1], 2)} / {fx(heat["tot"][2], 2)} / {fx(heat["tot"][3], 2)} W '
          f'e {it(heat["gioco"], 2)} cm. La scheda audio pesa {fx(heat["parts"][0][1] - heat["l51b"].get("scheda audio (8 blocchi)", (0,))[0], 2)} W '
          'in più (il limitatore del VAS di L66); la dissipazione dei regolatori si divide ora con la 4,7 Ω '
          'davanti e lo Schottky dopo (ADR-092, ADR-093).</p>')

    if psu:
        # ============================================== L64b: l'alimentatore ===
        pw, sq, cs, sb, off, p9, st = M["pw"], M["sq"], M["cs"], M["sb"], M["off"], M["p9"], M["st"]
        an, vt, dg, car = sq["an"], M["vt"], M["dg"], M["car"]
        dbf = off["f"]["db"]

        def volt(v):
            """Una tensione piccola nella sua unita', virgola italiana."""
            for k, u in ((1, "V"), (1e-3, "mV"), (1e-6, "µV"), (1e-9, "nV")):
                if abs(v) >= k:
                    return f"{it(v / k, 3)} {u}"
            return f"{it(v / 1e-9, 3)} nV"

        def spl(v):
            return f"{fx(dbf(v), 1)} dB SPL <span class=\"na\">({volt(v)})</span>"

        def cella(r, k, u=""):
            """Una cella di un CSV: '>x' e' un limite (la corsa finisce prima), vuota e' «non si
            applica»; il meno e' tipografico."""
            s = (r.get(k) or "").strip()
            if not s:
                return "&mdash;"
            v = ("&gt; " + it(float(s[1:]), 4)) if s.startswith(">") else it(float(s), 4)
            return v.replace("-", "&minus;") + (f" {u}" if u else "")

        today = pw["oggi"]
        rete = {"m10": "−10 %", "nom": "nominale", "p10": "+10 %"}
        offl = {r["caso"]: r for r in off["rows"]}
        vr_m10 = float(today.get("perdita_rete_m10", {}).get("vr_hold_ms") or "nan")
        vr_m10_51 = float(pw["l51b"].get("perdita_rete_m10", {}).get("vr_hold_ms") or "nan")
        vtd = {(c, k): (v, s_, ok) for c, k, v, s_, ok in vt}
        acc, fr = an.get("oggi/accensione", {}), an.get("oggi/fredda", {})
        sl = an.get("oggi/spegnimento_l", {})
        l2 = sq["l2"]

        A(h2("spsu"))
        A(f'<p class="prov">Disegno <code>docs/preamp/schematic/psu_blocks_draw.py</code>, ogni cifra '
          f'letta da <code>{rel(PSU_NET)}</code> e asserita &middot; sorgente '
          '<code>circuits/preamp/psu.py</code></p>')
        A('<p>La seconda scheda. Porta i rail audio, <code>VRELAY</code> per le bobine della scheda '
          'audio (il mute, il guadagno, il trim, il selettore) e la logica a 5 V; decide <em>quando</em> '
          'il mute si inserisce e si rilascia, e lo fa in un ordine che sta nell&rsquo;hardware. Non '
          'c&rsquo;è un microcontrollore né un programma (ADR-102): l&rsquo;accensione, i ritardi, il '
          'mute e lo standby li fanno dodici canali di comparatore, delle reti RC e una ritenuta a due '
          'transistor. Il diagramma è a blocchi: le soglie e le costanti di tempo stampate sono '
          'calcolate dai valori della netlist, le cifre misurate stanno nelle sezioni che seguono.</p>')
        A(figure("psu_blocks.svg", "Diagramma a blocchi dell'alimentatore"))
        A('<div class="tablewrap"><table><tr><th>Decisione</th><th>Che cosa</th>'
          '<th>La cifra che la regge, dai dati</th></tr>')
        pn = today.get("perdita_rete_nom", {})
        rn = today.get("regime_nom", {})
        A(f'<tr><td>ADR-048</td><td>rail lineari (nessuno switching), <code>VRELAY</code> da un '
          'trasformatore proprio, il sorvegliante in hardware sul gate del sink di '
          '<code>MUTE_CMD</code></td>'
          f'<td class="num">alla perdita di rete <code>MUTE_CMD</code> rilasciato a '
          f'{cella(pn, "t_off_ms", "ms")}, coi rail ancora a '
          f'{cella(pn, "vplus_at_off")} / {cella(pn, "vminus_at_off", "V")}</td></tr>')
        A(f'<tr><td>ADR-091, ADR-092</td><td>la partenza morbida dei regolatori (C507, C508) e la '
          '4,7 Ω davanti a ciascuno (R550, R551)</td>'
          f'<td class="num">a freddo la musica a {cella(fr, "t_mus_ms", "ms")}, dallo standby a '
          f'{cella(acc, "t_mus_ms", "ms")} &middot; R550 + R551 '
          f'{fx(M["heat"]["bench"]["regime_nom"]["rpre"], 2)} W</td></tr>')
        A(f'<tr><td>ADR-093, ADR-096</td><td>lo Schottky dopo ogni regolatore, la retroazione sul '
          'piedino (15,3 V impostati)</td>'
          f'<td class="num">i rail a regime {cella(rn, "vplus")} / {cella(rn, "vminus", "V")} '
          f'&middot; i due SB340 {fx(M["heat"]["bench"]["regime_nom"]["dsch"], 2)} W</td></tr>')
        if "corto_u503" in offl:
            A(f'<tr><td>ADR-051</td><td>il corto della linea a 12 V dei relè accettato sotto il '
              'tetto (guasto singolo)</td>'
              f'<td class="num">{spl(float(offl["corto_u503"]["picco_V"]))} al jack &middot; tetto '
              f'{fx(dbf(p9["tetto_V"]), 1)} dB SPL</td></tr>')
        A(f'<tr><td>ADR-064</td><td>il selettore: una bobina sempre accesa su <code>VRELAY</code></td>'
          f'<td class="num">tenuta di <code>VRELAY_REG</code> a rete −10 % {it(vr_m10, 4)} ms '
          f'(P9: ≥ {fx(p9["vrelay_ms"], 0)})</td></tr>')
        A(f'<tr><td>ADR-102, ADR-103</td><td>il temporizzatore a comparatori, lo standby, R585 sul nodo '
          'della ritenuta</td>'
          f'<td class="num">il permissivo ≥ {it(min(v for (c, k), (v, s_, ok) in vtd.items() if c == "perm" and v is not None), 3)} '
          f'ms dopo il mute &middot; lo standby {fx(sb["nom"]["t2"], 1)} mW da {des("T2")}</td></tr>')
        A(f'<tr><td>ADR-104, ADR-105, ADR-108</td><td>i diodi a bassa perdita, R571, i '
          'condensatori dei ritardi in C0G e in film</td>'
          f'<td class="num">la musica {it(min(v for (c, k), (v, s_, ok) in vtd.items() if c == "mus" and v is not None), 4)} '
          f'ms dopo un buco di 20 ms (≥ {fx(st["mus"], 0)}), la peggiore delle tre reti</td></tr>')
        A(f'<tr><td>ADR-110</td><td>la coppia Q501 + Q509 in serie sul mute, la procedura '
          'col tester (<code>DIAGNOSI.md</code>)</td>'
          f'<td class="num">{sum(1 for r in dg if r["guasto"].startswith(("f_q50", "f_rq50")) and not r["diff"])} '
          f'su {sum(1 for r in dg if r["guasto"].startswith(("f_q50", "f_rq50")))} guasti singoli della '
          f'coppia come la coppia sana ({sez("sdiag")})</td></tr>')
        A('</table></div>')

        # --- potenza ---
        A(h2("spow"))
        A(prov_psu(os.path.join(pw["dir"], "rete", "tb_psu_rete.cir"), pw["dir"],
                   " &middot; corso il 2026-11-03 sul <code>psu.net</code> di oggi, col carico di oggi; "
                   "deck rigenerati da questa pagina e uguali a quelli corsi"))
        A('<p><strong>Il carico di oggi.</strong> La scheda audio pesa sul banco come la misura '
          f'<code>tb_op</code> di oggi: {it(float(car["i_piu_mA"]), 7)} mA sul rail + e '
          f'{it(float(car["i_meno_mA"]), 7)} mA sul −, otto blocchi (ADR-054; L51b ne caricava 293,62 '
          'e 301,79, il blocco di prima di L66). Su <code>VRELAY</code>, oltre alle bobine del mute e '
          f'del guadagno, {it(float(car["resto_mA"]), 3)} mA del resto della scheda, con la bobina '
          'del selettore sempre accesa (L48a). Il banco è quello di L51b sull&rsquo;alimentatore di '
          'oggi: i casi a regime e la perdita di rete a 3 s, quando l&rsquo;accensione a freddo ha '
          f'già dato la musica ({cella(fr, "t_mus_ms", "ms")}).</p>')
        A('<h3>A regime</h3>')
        A('<div class="tablewrap"><table><tr><th>Rete</th><th class="num">V+</th><th class="num">V−</th>'
          '<th class="num">VRELAY_REG</th><th class="num">VRELAY a J1</th><th class="num"><span class="des">V5</span></th>'
          '<th class="num">valle del grezzo +</th><th class="num">valle −</th>'
          '<th class="num">valle di VRELAY</th></tr>')
        for f_, lab in rete.items():
            r = today.get(f"regime_{f_}", {})
            A(f'<tr><td>{lab}</td>' + "".join(f'<td class="num">{cella(r, k)} V</td>' for k in (
                "vplus", "vminus", "vrelay_reg", "vrelay", "v5", "raw_p_min", "raw_m_min_abs",
                "raw_v_min")) + '</tr>')
        A('</table></div>')
        rm = today.get("regime_m10", {})
        valle = min(float(rm.get("raw_p_min") or "nan"), float(rm.get("raw_m_min_abs") or "nan"))
        A(f'<p>A rete −10 % la valle del grezzo più bassa è {it(valle, 4)} V. Fra il grezzo e il rail '
          'ci sono ora la 4,7 Ω, il regolatore e lo Schottky: i regolatori sono impostati a 15,3 V perché '
          'il rail resti a ~15 V dietro il diodo (ADR-093). È il margine del raddrizzatore col '
          'toroidale di ADR-048 (2 &times; 15 V, 50 VA), misurato sul banco col carico di oggi; il '
          'trasformatore vero va confermato sul pezzo.</p>')
        A('<h3>La perdita di rete, col rivelatore</h3>')
        A('<div class="tablewrap"><table><tr><th>Rete</th><th class="num">MUTE_CMD rilasciato</th>'
          '<th class="num">rivelatore</th><th class="num">rail + a 13,5 / 10,6 V</th>'
          '<th class="num">rail al rilascio</th>'
          f'<th class="num">VRELAY_REG ≥ 11,4 V dopo</th><th>P9: ≥ {fx(p9["vrelay_ms"], 0)} ms</th></tr>')
        for f_, lab in rete.items():
            r = today.get(f"perdita_rete_{f_}", {})
            vh = float(r.get("vr_hold_ms") or "nan")
            A(f'<tr><td>{lab}</td><td class="num">{cella(r, "t_off_ms")} ms</td>'
              f'<td class="num">{cella(r, "t_md_ms")} ms</td>'
              f'<td class="num">{cella(r, "t_p135_ms")} / {cella(r, "t_p106_ms")} ms</td>'
              f'<td class="num">{cella(r, "vplus_at_off")} / {cella(r, "vminus_at_off")} V</td>'
              f'<td class="num">{cella(r, "vr_hold_ms")} ms</td>{verdict(vh >= p9["vrelay_ms"])}</tr>')
        A('</table></div>')
        A('<h3>Un regolatore che cede, e il rivelatore guasto</h3>')
        A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">MUTE_CMD rilasciato</th>'
          f'<th class="num">dopo lo scatto a |{fx(p9["soglia_V"], 1)} V|</th>'
          '<th class="num">rail al rilascio</th><th class="num">VRELAY_REG ≥ 11,4 / ≥ 9,6 V</th>'
          f'<th>P9: entro {fx(p9["entro_ms"], 0)} ms</th></tr>')
        for c, lab in (("guasto_u501", "U501 (rail +) spento"), ("guasto_u502", "U502 (rail −) spento"),
                       ("guasto_u503", "U503 (<code>VRELAY_REG</code>) spento"),
                       ("perdita_senza_rivelatore_m10", "perdita di rete, rivelatore guasto, −10 %"),
                       ("perdita_senza_rivelatore_nom", "idem, nominale"),
                       ("perdita_senza_rivelatore_p10", "idem, +10 %")):
            r = today.get(c, {})
            tr = (r.get("trip_after_135_ms") or "").strip()
            ok = (float(tr) <= p9["entro_ms"]) if tr else None
            A(f'<tr><td>{lab}</td><td class="num">{cella(r, "t_off_ms")} ms</td>'
              f'<td class="num">{cella(r, "trip_after_135_ms", "ms")}</td>'
              f'<td class="num">{cella(r, "vplus_at_off")} / {cella(r, "vminus_at_off")} V</td>'
              f'<td class="num">{cella(r, "vr_hold_ms")} / {cella(r, "vr80_hold_ms")} ms</td>'
              + (verdict(ok) if ok is not None else '<td class="na">scatta su VRELAY_REG</td>') + '</tr>')
        A('</table></div>')
        A('<p>Un tempo negativo dopo lo scatto vuol dire che il mute è già rilasciato prima che un rail '
          'arrivi alla soglia. Col rivelatore di rete guasto il caso è doppio (la rete persa e il '
          'rivelatore rotto), come L41a lo dichiarò: scatta il sorvegliante dei rail. Il rivelatore '
          f'guasto è R512 aperta: è la metà di R_MD (ADR-094), {it(pw["r512"] / 1e3, 3)} kΩ nella '
          'netlist e in ogni caso del log, salvo quello che la apre.</p>')
        A('<h3>Cosa è cambiato dall&rsquo;ultimo dossier (L51b)</h3>')
        A('<p>L51b correva il micro, il carico della scheda audio di prima di L66 e l&rsquo;alimentatore '
          'di prima di ADR-091…094: la partenza morbida, la 4,7 Ω, lo Schottky, R_MD sdoppiata, i 5 V '
          'in serie. Ogni cifra che si sposta oltre la tolleranza della ricorsa (0,5 ms o l&rsquo;1 % '
          'sui tempi, 10 mV sulle tensioni, 50 mV su quelle prese all&rsquo;istante dello scatto):</p>')
        A('<div class="tablewrap"><table><tr><th>Caso</th><th>Grandezza</th>'
          '<th class="num">L51b</th><th class="num">oggi</th></tr>')
        names = {"vr_hold_ms": "VRELAY_REG ≥ 11,4 V [ms]", "vr80_hold_ms": "VRELAY_REG ≥ 9,6 V [ms]",
                 "raw_v_min": "valle di VRELAY [V]", "t_off_ms": "MUTE_CMD rilasciato [ms]",
                 "trip_after_135_ms": "dopo lo scatto a 13,5 V [ms]", "vplus_at_off": "V+ al rilascio [V]",
                 "vminus_at_off": "V− al rilascio [V]", "t_p135_ms": "rail + a 13,5 V [ms]",
                 "t_p106_ms": "rail + a 10,6 V [ms]", "t_m135_ms": "rail − a 13,5 V [ms]",
                 "t_m106_ms": "rail − a 10,6 V [ms]", "raw_p_min": "valle del grezzo + [V]",
                 "raw_m_min_abs": "valle del grezzo − [V]", "vrelay": "VRELAY a J1 [V]",
                 "vrelay_reg": "VRELAY_REG [V]", "vplus": "V+ [V]", "vminus": "V− [V]",
                 "v5": "V5 [V]", "t_md_ms": "rivelatore [ms]"}
        caso_lab = {**{f"regime_{f}": f"a regime, rete {v}" for f, v in rete.items()},
                    **{f"perdita_rete_{f}": f"perdita di rete, {v}" for f, v in rete.items()},
                    **{f"perdita_senza_rivelatore_{f}": f"rivelatore guasto, rete {v}"
                       for f, v in rete.items()},
                    "guasto_u501": "U501 (rail +) spento", "guasto_u502": "U502 (rail −) spento",
                    "guasto_u503": "U503 (<code>VRELAY_REG</code>) spento"}
        num_c = lambda s: html_escape((s or "").replace(".", ",")).replace("-", "&minus;")
        for caso, k, a, b in pw["scarti"]:
            A(f'<tr><td>{caso_lab.get(caso, html_escape(caso))}</td>'
              f'<td>{names.get(k, html_escape(k)).replace("V5", des("V5"))}</td>'
              f'<td class="num">{num_c(a)}</td><td class="num"><strong>{num_c(b)}</strong></td></tr>')
        A('</table></div>')
        A(f'<p>Le cause si leggono. Lo Schottky dopo il regolatore porta i rail da 15,000 / −15,052 V a '
          f'{cella(rn, "vplus")} / {cella(rn, "vminus")} V. La 4,7 Ω e la partenza morbida rallentano '
          'la discesa dei rail alla perdita di rete (i tempi a 13,5 e 10,6 V salgono). A rete −10 % la '
          f'tenuta di <code>VRELAY_REG</code> passa da {it(vr_m10_51, 4)} a <strong>{it(vr_m10, 4)} '
          f'ms</strong>, contro ≥ {fx(p9["vrelay_ms"], 0)}.</p>')

        # --- sorvegliante ---
        A(h2("ssup"))
        A(prov_psu(os.path.join(sq["dir"], "oggi", "perdita", "tb_psu_seq_perdita_g1.cir"), sq["dir"],
                   f" &middot; {len(sq['corse'])} corse il 2026-11-03 sul <code>psu.net</code> di oggi, col "
                   "carico di oggi, ognuna col suo deck rigenerato da questa pagina e uguale a quello corso "
                   f"&middot; seconda strada: <code>{rel(os.path.join(L64B, 'script', 'confronta.py'))}</code>, "
                   "rieseguito"))
        A('<p>Le sequenze dell&rsquo;alimentatore col temporizzatore del sorgente, una corsa per caso: '
          'non c&rsquo;è più un programma da iterare col circuito. I relè sono presi all&rsquo;angolo '
          'peggiore del G6K: il jack staccato <em>il più tardi possibile</em>, il guadagno a 0 dB '
          '<em>il più presto possibile</em>. I criteri: C2, il mute eccitato solo col permissivo '
          'eccitato; C3, ogni rilascio del mute seguito da quello del permissivo almeno '
          f'{it(st["perm"], 3)} ms dopo (Δ, ADR-045); r41, il jack staccato prima che il guadagno si '
          'muova; s41, il jack staccato prima che il rail + scenda sotto 10,6 V. Dove un criterio non '
          'si applica (all&rsquo;accensione il jack non si stacca) la cella è vuota.</p>')
        A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">jack, tardi</th>'
          '<th class="num">guadagno, presto</th><th class="num">Δ</th><th class="num">V+ &lt; 10,6 V</th>'
          '<th class="num">K501</th><th>Criteri</th></tr>')
        for c in SEQ_GUASTI:
            r = an.get(f"oggi/{c}")
            if r is None:
                refuse(f"an_l64b.csv: manca oggi/{c}")
                continue
            cr = {k: r[k] for k in ("C2", "C3", "r41", "s41")}
            if c == "cf_nodelta":
                ok = cr["C3"] == "0" and cr["r41"] == "0"
                esito = (f'<td class="{"ok" if ok else "no"}">'
                         f'{"C3 e r41 cadono, come devono" if ok else "NON cade"}</td>')
            else:
                esito = verdict(all(v == "1" for v in cr.values()), "4 su 4")
            A(f'<tr><td>{SEQ_LAB[c]}</td><td class="num">{cella(r, "t_jack_ms", "ms")}</td>'
              f'<td class="num">{cella(r, "t_gain_ms", "ms")}</td><td class="num">{cella(r, "d_perm_ms", "ms")}</td>'
              f'<td class="num">{cella(r, "t_v106_ms", "ms")}</td><td class="num">{cella(r, "t_k501_ms", "ms")}</td>'
              f'{esito}</tr>')
        A('</table></div>')
        A('<p>I tempi sono dall&rsquo;evento: il frontale per lo spegnimento, la rete o il regolatore '
          'per gli altri. K501 stacca il toroidale: con U503 spento la sua bobina resta senza '
          'alimentazione e si apre per prima, e il margine di ADR-046 (K501 ≥ '
          f'{fx(st["k501"], 0)} ms dopo il permissivo) vale per lo spegnimento dal frontale, '
          f'{cella(sl, "k_perm_ms", "ms")}.</p>')
        fm = [k for k in sorted(an) if k.startswith("oggi/f_u50") or k.startswith("oggi/f_c509")
              or k.startswith("oggi/f_k501")]
        A('<h3>I guasti del temporizzatore (L54b3b)</h3>')
        A('<div class="tablewrap"><table><tr><th>Guasto e evento</th><th class="num">jack</th>'
          '<th class="num">guadagno</th><th class="num">la musica</th><th>ritenuta</th><th>K501 alla fine</th></tr>')
        for k in fm:
            r = an[k]
            A(f'<tr><td><code>{html_escape(k.split("/", 1)[1])}</code></td>'
              f'<td class="num">{cella(r, "t_jack_ms", "ms")}</td><td class="num">{cella(r, "t_gain_ms", "ms")}</td>'
              f'<td class="num">{cella(r, "t_mus_ms", "ms")}</td>'
              f'<td>{"scattata" if r["ritenuta"] == "1" else "no"}</td>'
              f'<td>{"chiuso" if r["k501_end"] == "1" else "aperto"}</td></tr>')
        A('</table></div>')
        A(f'<p><strong>La seconda strada.</strong> {l2.get("righe", 0)} righe di L54b3b e L58b, '
          f'rappresentate da {len([1 for lab, c in sq["corse"] if not lab.startswith("consumo")])} corse '
          f'di oggi: {l2.get("celle", 0)} celle confrontate, <strong>{l2.get("identiche", 0)} identiche</strong>, '
          f'{l2.get("entro", 0)} entro la tolleranza, {l2.get("fuori", 0)} fuori. La tolleranza è '
          'l&rsquo;unità della cifra stampata (0,1 ms, 0,01 V) contro L58b, che correva lo stesso '
          '<code>psu.py</code>; contro le corse di prima della coppia Q501 + Q509 (L54b3b e le righe di '
          'L58b sul sorgente di prima) in più lo scarto che L58b misurò fra il sorgente nuovo e la '
          f'variante, 0,1 ms. I {l2.get("deck_l58b", 0)} deck di L58b sono quelli di oggi a meno del '
          'carico della scheda audio (la coppia letta con i nomi della variante, o tolta per le corse '
          'di prima della coppia).</p>')

        # --- temporizzatore ---
        A(h2("stim"))
        A(prov_psu(os.path.join(sq["dir"], "oggi", "accensione", "tb_psu_seq_accensione_g1.cir"),
                   sq["dir"], " &middot; le stesse corse della sezione sopra"))
        A('<p>Il temporizzatore a comparatori fa quello che faceva il micro: con l&rsquo;alimentazione '
          'buona (i rail e la rete sopra soglia) rilascia il permissivo e poi il mute; a una perdita '
          'o a un guasto li inserisce nell&rsquo;ordine giusto; a un guasto lungo arma una ritenuta '
          'che apre K501 e tiene spento finché non si spegne il frontale. I criteri sono quelli di '
          'L54b3b, scritti prima delle corse, e le soglie si leggono dalle decisioni che le hanno '
          'fissate.</p>')
        A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">rete −10 %</th>'
          '<th class="num">nominale</th><th class="num">+10 %</th></tr>')
        for c, col, lab in (("accensione", "t_mus_ms", "accensione dallo standby: la musica"),
                            ("fredda", "t_mus_ms", "accensione a freddo: la musica"),
                            ("buco20", "dmus_ms", "un buco di 20 ms: la musica dopo la rete"),
                            ("buco200", "dmus_ms", "un buco di 200 ms: la musica dopo la rete"),
                            ("perdita", "t_jack_ms", "perdita di rete: il jack"),
                            ("accensione", "t_arm_ms", "accensione: la ritenuta armata")):
            cells = []
            for suf in ("_m10", "", "_p10"):
                r = an.get(f"oggi{suf}/{c}")
                cells.append(f'<td class="num">{cella(r, col, "ms") if r else "&mdash;"}</td>')
            A(f'<tr><td>{lab}</td>{"".join(cells)}</tr>')
        A('</table></div>')
        crit = {"perm": f"il permissivo ≥ {it(st['perm'], 3)} ms dopo il mute",
                "mus": f"la musica ≥ {fx(st['mus'], 0)} ms dopo la rete, un buco di 20 ms",
                "k501": f"K501 ≥ {fx(st['k501'], 0)} ms dopo il permissivo, dal frontale",
                "arm": "la ritenuta armata dopo l&rsquo;alimentazione buona, e non scatta",
                "base": f"la base della ritenuta ≤ {it(st['base'], 3)} V all&rsquo;accensione",
                "u501": "con U501 spento all&rsquo;accensione la ritenuta scatta e K501 si apre"}
        A('<div class="tablewrap"><table><tr><th>Criterio</th><th>Corse</th><th class="num">il peggiore</th>'
          '<th>Esito</th></tr>')
        for k, lab in crit.items():
            rr = [x for x in vt if x[0] == k]
            vals = [x[2] for x in rr if x[2] is not None]
            w = (max(vals) if k == "base" else min(vals)) if vals else None
            ok = all(x[4] for x in rr)
            u = " V" if k == "base" else " ms"
            A(f'<tr><td>{lab}</td><td>{len(rr)}</td>'
              f'<td class="num">{"&mdash;" if w is None else it(w, 4) + u}</td>'
              f'{verdict(ok, f"{sum(x[4] for x in rr)} su {len(rr)}")}</tr>')
        A('</table></div>')
        A(f'<p><strong>Lo standby.</strong> Con l&rsquo;interruttore frontale spento il toroidale è '
          f'staccato (K501 aperto) e resta acceso solo {des("T2")}, che alimenta la logica a 5 V: '
          f'{fx(sb["m10"]["t2"], 1)} / {fx(sb["nom"]["t2"], 1)} / {fx(sb["p10"]["t2"], 1)} mW dal suo '
          'secondario (rete −10 % / nominale / +10 %, la media su 2,5–3,0 s di una corsa '
          f'd&rsquo;accensione prima del frontale). L54b2, sul sorgente di prima di ADR-104, 105 e 110, '
          f'dava {" / ".join(fx(x, 1) for x in (sb["l54b2"][1], sb["l54b2"][0], sb["l54b2"][2]))} mW. '
          'Le perdite a vuoto del trasformatore non sono qui: si leggono sul pezzo.</p>')

        # --- autodiagnosi ---
        A(h2("sdiag"))
        A(prov_psu(os.path.join(sq["dir"], "oggi", "f_q509_gd_accs", "tb_psu_seq_f_q509_gd_accs_g1.cir"),
                   sq["dir"], " &middot; i guasti di L58b (<code>psu/modi.py</code>) coi nomi del "
                   "sorgente di oggi &middot; procedura: <code>docs/preamp/DIAGNOSI.md</code>"))
        A('<p>Un guasto che non si vede finché un secondo guasto non lo rende pericoloso è latente: '
          'ADR-110 li manda a una procedura col tester (<code>DIAGNOSI.md</code>) e, per il mute, mette '
          'in serie al transistor che lo comanda un secondo transistor (Q501 + Q509): uno in corto lascia '
          'l&rsquo;altro a fare il lavoro. Ogni guasto singolo, latente dall&rsquo;accensione, contro '
          'otto eventi, letto contro la corsa sana dello stesso evento: «come sano» vuol dire le stesse '
          'bandierine e gli stessi tempi entro 0,1 ms.</p>')
        ev_lab = {"accs": "accensione", "freds": "a freddo", "guas": "U502 spento", "b20s": "buco 20 ms",
                  "perds": "perdita", "spls": "spegnimento", "u501s": "U501 spento", "inss": "mute dal frontale"}
        gl = sorted({r["guasto"] for r in dg})
        A('<div class="tablewrap"><table><tr><th>Guasto</th>'
          + "".join(f'<th>{v}</th>' for v in ev_lab.values()) + '</tr>')
        idx = {(r["guasto"], r["evento"]): r for r in dg if r["lab"] == "oggi"}
        for g in gl:
            cells = []
            for e in ev_lab:
                r = idx.get((g, e))
                if r is None:
                    cells.append('<td class="na">&mdash;</td>')
                elif not r["diff"]:
                    cells.append('<td class="ok">come sano</td>')
                else:
                    cells.append('<td class="no">' + "; ".join(
                        f'{html_escape(col)} {html_escape(a or "—")} (sano {html_escape(b or "—")})'
                        for col, a, b in r["diff"][:3]) + '</td>')
            A(f'<tr><td><code>{html_escape(g)}</code></td>{"".join(cells)}</tr>')
        A('</table></div>')
        A('<p>Una cella rossa non è un verdetto: dice che il guasto <em>si vede</em> in quell&rsquo;evento, '
          'ed è quello che la procedura cerca. Le righe dello standby (Q505, Q506, R540, R536, R537, '
          'U508 B, Q503) cambiano lo standby a regime, non le sequenze: il censimento qui sotto.</p>')
        A('<div class="tablewrap"><table><tr><th>Corsa</th><th class="num">VRELAY alla scheda in standby</th>'
          '<th class="num">LED</th><th>K501 in standby</th><th class="num">le bobine del mute</th>'
          '<th class="num">la musica</th></tr>')
        for k, r in sorted(cs["rows"].items()):
            if not (k.endswith("_accs") or k == "oggi/accensione") or "q501" in k or "q509" in k:
                continue
            A(f'<tr><td><code>{html_escape(k.split("/", 1)[1])}</code></td>'
              f'<td class="num">{cella(r, "vrelay_sb", "V")}</td><td class="num">{cella(r, "i_led_mA", "mA")}</td>'
              f'<td>{"chiuso" if r.get("k501_sb") == "1.0" else "aperto"}</td>'
              f'<td class="num">{cella(r, "t_coil_ms", "ms")}</td><td class="num">{cella(r, "t_rail_ms", "ms")}</td></tr>')
        A('</table></div>')

        # --- spegnimento e guasti al jack ---
        A(h2("soff"))
        A(f'<p class="prov">Scheda audio <code>{rel(os.path.join(L64B, "deck", "tb_v2_l41c_nom.cir"))}</code> '
          '(e <code>_m10</code>, <code>_p10</code>), dal sorgente di oggi e dal ponte delle sequenze di '
          'oggi, rigenerato da questa pagina e uguale a quello corso &middot; il metodo di V2, il contatto '
          'col fronte di 4,55 µs (ADR-063) &middot; <code>tabella.py</code> rieseguito sull&rsquo;analisi '
          f'&middot; i dB SPL ricalcolati con la catena di NC-028 (finale ×{it(off["f"]["g"], 3)}, '
          f'{fx(off["f"]["spl"], 0)} dB con {it(off["f"]["v1w"], 3)} V): un limite superiore, di picco, a 1 m</p>')
        A(f'<p>Un gradino al jack, detto contro una stanza silenziosa (25–35 dB(A), un livello pesato '
          f'contro un picco): V2 è {fx(dbf(1e-4), 1)} dB SPL, l&rsquo;obiettivo di P9 '
          f'{fx(dbf(p9["obiettivo_mV"] * 1e-3), 1)} dB, il tetto di non-danno {fx(dbf(p9["tetto_V"]), 1)} dB. '
          'A rete −10 % e +10 % corrono dalle loro sequenze lo spegnimento e le due perdite; le altre '
          'righe sono quelle nominali.</p>')
        A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">rete −10 %</th>'
          '<th class="num">nominale</th><th class="num">+10 %</th><th>Criterio</th><th>Esito</th></tr>')
        om, op_ = ({r["caso"]: r for r in off["m10"]}, {r["caso"]: r for r in off["p10"]})
        tre = ("spegnimento_l", "perdita", "perdita_min")
        for r in off["rows"]:
            c = r["caso"]

            def v_(x):
                v = (x or {}).get("picco_V", "-")
                return spl(float(v)) if v not in ("-", "") else "&mdash;"
            good = all(x.get("esito", "").startswith(("sotto", "fallisce, come deve", "tetto sotto"))
                       for x in ([r] + ([om.get(c, {}), op_.get(c, {})] if c in tre else [])))
            A(f'<tr><td>{SEQ_LAB.get(c, html_escape(c))}</td>'
              f'<td class="num">{v_(om.get(c)) if c in tre else "&mdash;"}</td>'
              f'<td class="num">{v_(r)}</td>'
              f'<td class="num">{v_(op_.get(c)) if c in tre else "&mdash;"}</td>'
              f'<td>{html_escape(r["criterio"].replace("<=", "≤").replace(".", ","))}</td>'
              f'<td class="{"ok" if good else "no"}">{html_escape(r["esito"])}</td></tr>')
        A('</table></div>')
        A('<h3>Cosa è cambiato da L54b2</h3>')
        A('<p>L54b2 corse la stessa catena sul temporizzatore a comparatori di allora; da lì sono cambiati '
          'l&rsquo;alimentatore (ADR-104, 105, 108, 110) e la scheda audio (L66, ADR-111). I picchi '
          'nominali, uno accanto all&rsquo;altro:</p>')
        A('<div class="tablewrap"><table><tr><th>Caso</th><th class="num">L54b2</th><th class="num">oggi</th>'
          '<th class="num">scarto</th></tr>')
        old = {r["caso"]: r for r in off["l54b2"]["nom"]}
        for r in off["rows"]:
            a, b = old.get(r["caso"], {}).get("picco_V", "-"), r.get("picco_V", "-")
            if a in ("-", "") or b in ("-", ""):
                continue
            A(f'<tr><td>{SEQ_LAB.get(r["caso"], html_escape(r["caso"]))}</td><td class="num">{volt(float(a))}</td>'
              f'<td class="num"><strong>{volt(float(b))}</strong></td>'
              f'<td class="num">{sg(20 * math.log10(float(b) / float(a)), 1)} dB</td></tr>')
        A('</table></div>')
        A('<p>I casi ai nanovolt si muovono di molti dB nelle due direzioni: sono il fondo del metodo, '
          'migliaia di volte sotto V2.</p>')

    if "schede" in PARTI:
        # --- le schede di prova e l'assieme (L49a, L49b; L51c: «Essenziale», «Rifarlo oggi») ---
        bd = M["brd"]
        ba, bp, asm = bd["boards"]["audio"], bd["boards"]["psu"], bd["asm"]
        ma, mp = ba["meas"], bp["meas"]
        ch = asm["chassis_mm"]
        A(h2("sbrd"))
        A(f'<p class="prov">Schede <code>{html_escape(rel(ba["pcb"]))}</code> e '
          f'<code>{html_escape(rel(bp["pcb"]))}</code>, piazzate e sbrogliate da L49a e L49b '
          f'(Freerouting {html_escape(ba["freerouting"] or "?")}) &middot; DRC rifatta il 2026-10-10 '
          f'con kicad-cli {html_escape(ba["kicad"] or "?")}, in <code>{html_escape(rel(os.path.join(L51C, "drc")))}/</code>, '
          'uguale a quella del 9 ottobre &middot; i numeri dai <code>measure.json</code>, '
          '<code>placement.json</code> e <code>assembly.json</code> dei due lotti</p>')
        A('<p>Una prova di fattibilità, non il layout. Le due schede sono state piazzate e '
          'sbrogliate dalle netlist di oggi per sapere se il progetto si può costruire, se ci sta '
          f'nel contenitore (Modushop Pesante 3U, interni {it(ch[0], 4)} × {it(ch[1], 4)} × '
          f'{it(ch[2], 4)} mm) e cosa chiede al pre-layout (G2). Il circuito non è cambiato per '
          'farcele stare.</p>')
        A('<div class="tablewrap"><table><tr><th>Scheda</th><th class="num">Misura</th>'
          '<th class="num">Impronte sulla superficie</th><th class="num">Rame</th>'
          '<th class="num">Vie</th><th class="num">DRC oggi: violazioni / aperte</th></tr>')
        for lab, b in (("audio", ba), ("alimentatore", bp)):
            m = b["meas"]
            drc_s = "%d / %d" % b["drc"][:2]
            A(f'<tr><td>{lab}</td><td class="num">{it(m["board_mm"][0], 4)} × {it(m["board_mm"][1], 4)} mm</td>'
              f'<td class="num">{fx(m["fill"] * 100, 0)} %</td><td class="num">{it(m["tracks_m"], 3)} m</td>'
              f'<td class="num">{m["vias"]}</td>'
              + verdict(b["drc"][:2] == (0, 0), drc_s, drc_s) + '</tr>')
        A('</table></div>')
        outs = ma["main_output_nets_mm"]
        longest = ma["longest_signal_nets_mm"][0]
        nk = mp["necks"]
        A('<h3>La scheda audio</h3>')
        A(f'<p>I relè condivisi fra i canali stanno in una spina al centro: <strong>'
          f'{ma["n_nets_crossing_spine"]} reti di segnale</strong> passano da un canale all&rsquo;altro. '
          'Il prezzo è la lunghezza: ogni segnale va al centro e torna, le uscite principali sono '
          f'lunghe {" e ".join(f"{it(v, 4)} mm" for v in sorted(outs.values()))}, la rete più lunga '
          f'(<code>{html_escape(longest[0])}</code>) {it(longest[1], 4)} mm. Per G2 i connettori '
          'delle uscite vanno vicino alla spina.</p>')
        A(figure("scheda_audio_3d.png", "La scheda audio di prova, render dall'alto"))
        A(figure("scheda_audio_rame.png", "La scheda audio di prova, i due strati di rame"))
        A('<h3>L&rsquo;alimentatore</h3>')
        A(f'<p>La rete sta in colonna su un bordo: sul rame la distanza minima fra rete e bassa '
          f'tensione è <strong>{it(mp["mains_to_low_voltage_mm"], 4)} mm</strong>, fra fase e neutro '
          f'{it(mp["mains_L_to_N_mm"], 3)} mm. I rail sono larghi; si stringono in '
          f'{nk["count"]} tratti, larghi almeno {it(nk["min_width_mm"], 3)} mm e lunghi al più '
          f'{it(nk["max_length_mm"], 3)} mm, attorno ai piedini fini dei regolatori e delle altre parti '
          f'({", ".join(nk["parts"])}); {len(nk["not_on_a_pad"])} di questi non toccano un piedino '
          'a nessuna delle due estremità. Freerouting non è '
          'ripetibile: i file sono quelli della corsa consegnata, copiati.</p>')
        A(figure("alimentatore_3d.png", "L'alimentatore di prova, render dall'alto"))
        A(figure("alimentatore_rame.png", "L'alimentatore di prova, i due strati di rame"))
        fit = bd["fit"]
        A('<h3>L&rsquo;assieme nel contenitore</h3>')
        tor = fit.get("toroid_distances_mm", {})
        A(f'<p><strong>{html_escape(fit.get("title", ""))}</strong>: ci sta. '
          + " ".join(marca(re.sub(r"(\d)\.(\d)", r"\1,\2", html_escape(n))) for n in fit.get("notes", []))
          + ' I trasformatori stanno lontani dal segnale: '
          # il nome del trasformatore (T1, T2) e' una parte, non il requisito T1: si marca
          + "; ".join(f'{des(t.split()[0])} {html_escape(t.split(" ", 1)[1])} a '
                      f'{it(d["ingressi_RCA"], 4)} mm dagli ingressi e '
                      f'{it(d["volume_bilanciamento"], 4)} mm dal volume'
                      for t, d in tor.items() if d.get("volume_bilanciamento") is not None)
          + f'. Le altre {len(asm["variants"]) - 1} disposizioni provate non ci stanno.</p>')
        A(figure("assieme.png", "L'assieme nel contenitore, pianta e sezione"))
        A(f'<p class="meta">I disegni vettoriali, da ingrandire: <code>{html_escape(bd["pdf"]["audio"])}</code>, '
          f'<code>{html_escape(bd["pdf"]["psu"])}</code>, <code>{html_escape(bd["pdf"]["asm"])}</code>.</p>')
        A('<h3>Cosa chiedono al pre-layout</h3>')
        A('<p>I vincoli che le due prove restituiscono al progetto, coi titoli dei report di L49a e '
          'L49b (letti da lì, non riscritti); il dettaglio di ciascuno sta nel report. Nessuno '
          'cambia il circuito.</p>')
        A('<div class="tablewrap"><table><tr><th>Prova</th><th class="num">N.</th><th>Vincolo</th></tr>')
        for lab, key, rep in (("scheda audio", "audio", L49A_REPORT), ("alimentatore e assieme", "psu", L49B_REPORT)):
            for n, t in bd["vincoli"][key]:
                t = marca(re.sub(r"`([^`]+)`", r"<code>\1</code>", html_escape(t)))
                A(f'<tr><td>{lab}</td><td class="num">{n}</td><td>{t}</td></tr>')
        A('</table></div>')
        A(f'<p class="meta">Report: <code>{html_escape(rel(L49A_REPORT))}</code>, '
          f'<code>{html_escape(rel(L49B_REPORT))}</code>.</p>')

    # --- 13 requisiti ---
    A(h2("s13"))
    A('<p>Solo i requisiti che queste misure toccano. Il resto non è qui perché non è '
      'ancora stato misurato, non perché sia soddisfatto.</p>')
    g = {m: resp[(m, "1.5")]["g1k"] for m in MODES}
    A('<div class="tablewrap"><table><tr><th>Req.</th><th>Chiede</th><th>Misurato</th><th>Esito</th></tr>')
    A(f'<tr><td>E1</td><td>guadagno nominale 0 dB</td><td class="num">{fx(g["0db"], 4)} dB a 1 kHz</td>'
      f'{verdict(abs(g["0db"]) < 0.1)}</tr>')
    ok2 = abs(g["3db"] - 3.0) <= 0.1 and 9.5 <= g["10db"] <= 10.5
    A(f'<tr><td>E2</td><td>+3 dB (±0,1) e +10 dB (9,5–10,5)</td>'
      f'<td class="num">{sg(g["3db"], 4)} / {sg(g["10db"], 4)} dB a 1 kHz</td>{verdict(ok2)}</tr>')
    A(f'<tr><td>E3</td><td>≥ 100 kΩ al connettore, ogni posizione del trim</td>'
      f'<td class="num">min {it(e3w / 1000, 4)} kΩ, col selettore e la sua rete</td>'
      f'{verdict(e3w >= 1e5)}</tr>')
    A(f'<tr><td>E4</td><td>Z<sub>out</sub> &lt; 100 Ω in banda, esclusa la reattanza del cap, '
      'costante col volume</td>'
      f'<td class="num">Re(Z) max al jack {it(e4_main, 4)} Ω principale &middot; {it(e4_fix, 4)} Ω '
      f'fisse &middot; dispersione su trim &times; volume ≤ {it_sci(e4_disp, 2)} Ω</td>'
      f'{verdict(e4_ok, "conforme su tre uscite, ogni posizione di trim e volume")}</tr>')
    A(f'<tr><td>E5</td><td>rumore in uscita &lt; 10 µV RMS</td>'
      f'<td class="num">catena ≤ {fx(e5w, 3)} µV, bilanciamento girato compreso</td>'
      f'{verdict(e5w < E5_MAX, "conforme, col 1/f al tetto di ADR-057")}</tr>')
    A(f'<tr><td>E6×E2</td><td>2,7 V RMS d&rsquo;ingresso a +10 dB</td>'
      f'<td class="num">M1 {sg(t10["6"]["M1"])} dB col trim a &minus;6 dB &middot; '
      f'{sg(t10["0"]["M1"])} dB a trim 0</td>'
      f'<td class="{"ok" if t10["6"]["M1"] > 0 else "no"}">margine col trim (ADR-015, ADR-027); '
      'legenda di pannello ancora da fare (NC-009)</td></tr>')
    A(f'<tr><td>F1</td><td>il cambio d&rsquo;ingresso ≤ {uv(F1_MAX, 3)} di picco sulle uscite</td>'
      f'<td class="num">{uv(sel_w)} con sorgenti fino a 100 mV di continua &middot; tocca F1 a '
      f'~{it(sel["lim"], 2)} V</td>'
      f'{verdict(sel_w <= F1_MAX, "conforme fino al limite di ADR-064")}</tr>')
    A(f'<tr><td>V1</td><td>margine ≥ 60° su tutta la matrice (ADR-019, ADR-024)</td>'
      f'<td class="num">minimo {fx(v1w, 3)}° &middot; {v1w_where}</td>'
      f'{verdict(v1w >= PM_MIN)}</tr>')
    okv2 = v2["all_inside"] and abs(cf["rows"][1]["vout"]) > 1.0
    A(f'<tr><td>V2</td><td>l&rsquo;anello non si apre mai commutando</td>'
      f'<td class="num">{sum(x["inside"] for x in v2["rows"])} finestre su {len(v2["rows"])} '
      f'nell&rsquo;inviluppo &middot; controfattuale a {fx(cf["rows"][1]["vout"], 3)} V</td>'
      f'{verdict(okv2)}</tr>')
    A(f'<tr><td>V2</td><td>il mute: A, B2, B2g e B1 ≤ 100 µV di picco (ADR-032, ADR-063); il clic '
      'dichiarato (ADR-062)</td>'
      f'<td class="num">{mu["n"] - mu["n_fuori"]} verdetti su {mu["n"]} &middot; il clic, il '
      'circuito contro il taglio ideale, al più '
      f'{sg(max(float(r["circuito_meno_ideale_dB"]) for r in mu["clic"]))} dB</td>'
      f'{verdict(mu["n_fuori"] == 0)}</tr>')
    A(f'<tr><td>V3</td><td>recupero dalla saturazione</td>'
      f'<td class="num">clipping {sg(v3["vmax"], 3)} / {sg(v3["vmin"], 3)} V &middot; '
      f'{sg(v3["jack_end"] * 1000, 2)} mV al jack a fine corsa</td>'
      '<td class="na">impaginato dal CSV, senza controllo incrociato</td></tr>')
    A(f'<tr><td>P7</td><td>corto e mute a tempo indefinito, Tj ≤ 125 °C</td>'
      f'<td class="num">Tj massima {fx(p7["tjmax"], 1)} °C &middot; {p7["n_bad"]} righe '
      'ascoltabili fuori classe A</td>'
      f'{verdict(p7["tjmax"] <= TJ_MAX and p7["n_bad"] == 0)}</tr>')
    if psu:
        heat = M["heat"]
        hv = [v for v in heat["vano"] if v[1] == "peggiore" and v[0] != "all'aria"]
        hworst = max(hv, key=lambda v: v[5]) if hv else None
        if hworst:
            A(f'<tr><td>P5</td><td>60 °C nel telaio, vano chiuso, stanza a 35 °C (ADR-021, ADR-047)</td>'
              f'<td class="num">{fx(hworst[5], 1)} °C col gioco di {html_escape(hworst[0].replace(".", ","))} '
              f'&middot; {fx(heat["tot"][3], 2)} W</td>'
              f'<td class="{"ok" if hworst[5] <= TA else "no"}">stima calcolata, da confermare sul '
              'prototipo</td></tr>')

    if psu:
        # L42b: P9, dall'alimentatore. L64b: i tempi dalle sequenze del temporizzatore di oggi
        sp_l = offl.get("spegnimento_l")
        k501 = _num(sl, "k_perm_ms")
        if sp_l:
            okp9a = float(sp_l["picco_V"]) <= 1e-4 and (k501 or 0) >= p9["margine_ms"]
            A(f'<tr><td>P9 (a)</td><td>spegnimento morbido: V2 al jack, K501 ≥ {fx(p9["margine_ms"], 0)} ms '
              'dopo il permissivo (ADR-046, ADR-048)</td>'
              f'<td class="num">{spl(float(sp_l["picco_V"]))} &middot; K501 a {it(k501 or float("nan"), 3)} ms</td>'
              f'{verdict(okp9a)}</tr>')
        gv = [r for r in off["rows"] if r["criterio"].startswith("<= 0.002")]
        gw = max(gv, key=lambda r: float(r["picco_V"])) if gv else None
        trips = [float(today[c]["trip_after_135_ms"]) for c in ("guasto_u501", "guasto_u502")
                 if today.get(c, {}).get("trip_after_135_ms")]
        vrmin = min(float(today[f"perdita_rete_{x}"]["vr_hold_ms"]) for x in ("m10", "nom", "p10")
                    if today.get(f"perdita_rete_{x}", {}).get("vr_hold_ms"))
        if gw and trips:
            okp9b = (float(gw["picco_V"]) <= p9["obiettivo_mV"] * 1e-3 and max(trips) <= p9["entro_ms"]
                     and vrmin >= p9["vrelay_ms"])
            A(f'<tr><td>P9 (b)</td><td>perdita di rete e guasto: <code>MUTE_CMD</code> entro '
              f'{fx(p9["entro_ms"], 0)} ms dallo scatto, <code>VRELAY</code> ≥ {fx(p9["vrelay_ms"], 0)} ms, '
              f'al jack ≤ {fx(p9["obiettivo_mV"], 0)} mV</td>'
              f'<td class="num">scatto {sg(max(trips), 3)} ms al peggio &middot; VRELAY {it(vrmin, 4)} ms &middot; '
              f'{spl(float(gw["picco_V"]))} ({SEQ_LAB.get(gw["caso"], gw["caso"])})</td>'
              f'{verdict(okp9b, "conforme col carico di oggi, il selettore compreso")}</tr>')
        pw_ = [x for x in vt if x[0] == "perm"]
        A(f'<tr><td>ADR-045</td><td>Δ ≥ {it(st["perm"], 3)} ms fra il mute e il permissivo, in hardware '
          '(ADR-102: senza un programma)</td>'
          f'<td class="num">{it(min(x[2] for x in pw_ if x[2] is not None), 4)} ms, il più corto di '
          f'{len(pw_)} corse alle tre reti</td>{verdict(all(x[4] for x in pw_))}</tr>')
        A(f'<tr><td>NC-037</td><td>standby ≤ 0,5 W alla presa, un obiettivo del progetto (P9 (a), ADR-053)</td>'
          f'<td class="num">{fx(sb["nom"]["t2"], 1)} mW dal secondario di {des("T2")}</td>'
          '<td class="na">aperta: mancano le perdite a vuoto di <span class="des">T2</span> (giro BOM) e la misura</td></tr>')
    A(f'<tr><td>V4</td><td>niente di aspro: THD a 20 kHz ≤ {pct(dist["soglie"]["thd20_lo"], tetto=True)} % a '
      f'0,2 V, dalla 5ª in su ≤ {fx(dist["soglie"]["h5"], 0)} dB, intermodulazione ≤ '
      f'{fx(dist["soglie"]["imd"], 0)} dB, a 2 V ≤ {pct(dist["soglie"]["thd20_hi"], tetto=True)} % (ADR-055)</td>'
      f'<td class="num">{pct(dist["thd_lo"]["20k"])} % &middot; {fx(dist["h5_lo"], 1)} dB &middot; '
      f'{fx(dist["imd_lo"], 1)} dB &middot; {pct(dist["thd_hi_20k"])} %, il blocco da solo</td>'
      + (verdict(all(dist["ok"].values()), "conforme, cifre di modello; THD+N da fissare sul prototipo")
         if all(dist["ok"].values()) else verdict(False)) + '</tr>')
    A('</table></div>')

    if "schede" in PARTI:
        # --- 14 limiti ---
        A(h2("s14"))
        # L51c: riscritta sul progetto di oggi; ogni cifra e' letta dai dati
        co = M["car"]
        ferro = sum(p[3] for p in M["heat"]["ipotesi"])
        A('<ul>')
        A(f'<li><strong>La distorsione è di modello</strong> ({sez("sdist")}): il blocco di '
          'guadagno da solo, coi modelli del costruttore, nessuna misura su un prototipo. Il tetto '
          'complessivo di THD+N di V4 non è ancora fissato: si fissa sulle prime misure.</li>')
        if placeholders:
            A(f'<li><strong>{len(placeholders)} dispositivi attivi su '
              f'{len(vendors) + len(placeholders)} sono segnaposto</strong> ({", ".join(placeholders)}).</li>')
        if con_tetto:
            A(f'<li><strong>Il rumore 1/f è un limite per eccesso.</strong> {", ".join(con_tetto)} '
              'portano un tetto dichiarato, il doppio del tipico letto sulle poche curve pubblicate '
              'trovate (ADR-057), non il rumore di ciascuna parte. E5 non è un pavimento: è un '
              'massimo.</li>')
        A('<li><strong>V1 agli spigoli di tolleranza</strong> di resistenze e condensatori non è '
          'misurato: qui c&rsquo;è V1 ai valori nominali. Sulla dispersione di I<sub>DSS</sub> dei '
          f'JFET, sullo stesso blocco, L46b dà ≥ {fx(dist["v1_idss"], 2)}° '
          f'(<code>{html_escape(rel(os.path.join(L46B, "idss.csv")))}</code>), fuori da questa '
          'pagina.</li>')
        A('<li><strong>Le forme d&rsquo;onda dei transitori</strong> non sono versionate: di V2 del '
          'guadagno ci sono le finestre, della matrice del mute le analisi, di V3 il CSV.</li>')
        A('<li><strong>Il relè nella corsa dell&rsquo;interblocco</strong> è un modello dichiarato, '
          'non del costruttore: il datasheet non dà la dinamica della bobina.</li>')
        A('<li><strong>L&rsquo;alimentatore è simulato con modelli dichiarati</strong>, nessuno del '
          'costruttore: regolatori e comparatori comportamentali (il modello TI del TPS7A4701 dà un '
          'punto di lavoro sbagliato, quello del TLV1701 non commuta in ngspice); al posto del '
          'micro, le uscite del firmware vero eseguito sull&rsquo;host, iterate col circuito fino al '
          f'punto fisso; i due trasformatori ({des("T1")}, {des("T2")}) come generatori ideali con '
          'una resistenza e un&rsquo;induttanza in serie, da confermare sui pezzi. '
          '<strong>Niente PSRR né rumore dei regolatori nei modelli</strong>: la quota di rumore '
          'dell&rsquo;alimentazione regge su un limite per eccesso letto dai datasheet (L46b, '
          'ADR-056), non su una simulazione (NC-011, aperta fino alla misura sul prototipo).</li>')
        A('<li><strong>Il carico della scheda audio sull&rsquo;alimentatore</strong> è un carico '
          f'dichiarato: {fx(float(co["i_piu_mA"]), 1)} / {fx(float(co["i_meno_mA"]), 1)} mA sui '
          f'rail, dal punto di lavoro di oggi ({sez("spow")}), e le bobine dei relè come resistenze '
          'senza induttanza. La catena dei guasti va dall&rsquo;alimentatore alla scheda audio, mai '
          'indietro.</li>')
        A(f'<li><strong>Il calore è una stima calcolata</strong> ({sez("sheat")}), con coefficienti '
          'da letteratura, non una simulazione termica. L&rsquo;unica ipotesi fra le potenze è il '
          f'ferro dei trasformatori, {fx(ferro, 2)} W nel caso peggiore.</li>')
        A('<li><strong>Le schede di prova non sono il layout</strong> '
          f'({sez("sbrd")}): la massa è una rete di tracce, in attesa del lavoro su massa e terra; '
          'connettori, contenitore e frontale si decidono al pre-layout; le distanze di rete vengono '
          'da fonti secondarie, perché la norma non è stata letta; Freerouting non ripete la stessa '
          'scheda due volte.</li>')
        # L64b: il micro e il firmware non ci sono piu' (ADR-102); la riga di L51c che li diceva
        # sarebbe falsa. L64c riscrive la sezione intera.
        A('<li><strong>I comparatori del temporizzatore sono di comportamento</strong> '
          f'({sez("stim")}): il modello di TI non passa l&rsquo;accensione sul banco, e il banco usa '
          'un comparatore tarato sulle sue cifre (ADR-103), dichiarato come taratura.</li>')
        A('<li><strong>Nessuno qui giudica come suona.</strong> La simulazione copre '
          'stabilità, risposta, rumore, PSRR e impedenze; non copre l&rsquo;ascolto.</li>')
        A('</ul>')

    # --- 15 provenienza ---
    A(h2("s15"))
    A('<p>Ogni sezione dichiara il deck, la cartella dei dati e i modelli, e questi ultimi '
      'sono letti dagli <code>.include</code> del deck: un modello è «del costruttore» se '
      'sta in <code>models/</code> con la sua <code>.provenance.json</code>, «segnaposto» '
      'se sta in <code>spice/preamp/placeholder_devices.lib</code>.</p>')
    A('<div class="tablewrap"><table><tr><th>Modello istanziato</th><th>Parte</th>'
      '<th>File</th><th>Tipo</th><th class="num">KF</th></tr>')
    seen = {}
    for mm in allm:
        seen.setdefault(mm["model"], mm)
    for name in sorted(seen):
        mm = seen[name]
        A(f'<tr><td><code>{name}</code></td><td>{mm["part"]}</td><td><code>{mm["file"]}</code></td>'
          f'<td class="{"ok" if mm["vendor"] else "na"}">{"costruttore" if mm["vendor"] else "segnaposto"}</td>'
          f'<td class="num">{it(mm["kf"], 3)}</td></tr>')
    A('</table></div>')
    if PSU_PROV:
        # L51c: l'alimentatore, letto dai deck che le sue sezioni hanno dichiarato
        subs = sorted({s for _, ss in PSU_PROV.values() for s in ss})
        incs = sorted({i for ii, _ in PSU_PROV.values() for i in ii})
        A(f'<p><strong>L&rsquo;alimentatore</strong>: i {len(PSU_PROV)} deck che le sue sezioni '
          'nominano, generati da '
          '<code>circuits/preamp/psu.net</code>. Nessun modello del costruttore: i sottocircuiti '
          f'sono comportamentali e dichiarati ({", ".join(f"<code>{html_escape(s)}</code>" for s in subs)}), '
          f'e i file inclusi sono generici ({", ".join(f"<code>{html_escape(i)}</code>" for i in incs)}).</p>')
    if "schede" in PARTI:
        bd = M["brd"]
        A('<p><strong>Le schede di prova</strong>: le netlist di <code>circuits/preamp/</code>, '
          'i sorgenti di <code>layout/preamp/audio/</code>, <code>layout/preamp/psu/</code> e '
          '<code>layout/preamp/assembly/</code> (L49a, L49b), Freerouting '
          f'{html_escape(bd["boards"]["audio"]["freerouting"] or "?")}; la DRC di oggi con kicad-cli '
          f'{html_escape(bd["boards"]["audio"]["kicad"] or "?")}, la stessa versione del 9 ottobre '
          f'({html_escape(bd["boards"]["audio"]["kicad_prima"] or "?")}).</p>')
    A('<p class="meta">Rigenerare questa pagina: '
      '<code>/usr/bin/python3 docs/preamp/dossier/build_dossier.py'
      + ('' if all(p in PARTI for p in PARTI_TUTTE) else ' --standalone &lt;file fuori dal repo&gt;')
      + '</code>. Rieseguire una '
      'misura: <code>/bin/zsh scripts/run_simulation.sh spice/preamp/tb/&lt;deck&gt;.cir '
      'results/preamp/&lt;deck&gt;</code>.</p>')
    # --- appendici (L42d) ---
    A(h2("appA"))
    A(ct.section_adr(M["ct"]["adrs"]))
    A(h2("appB"))
    A(ct.section_req(M["ct"]["req"], M["ct"]["used"]))
    A('<hr class="end">')

    # e. i rimandi PR-n, ADR-0xx, E1...V5 diventano link (L42d)
    body, M["ct"]["rimandi"] = ct.linkify("\n".join(h), M["ct"]["prb"], M["ct"]["req"],
                                          M["ct"]["adrs"], M["ct"]["nonreq"])
    A('</div>')

    return ('<meta charset="utf-8">\n<title>Dossier del preamp di linea</title>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
            'family=IBM+Plex+Mono:wght@400;500&'
            'family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&'
            'display=swap">\n'
            f"<style>{CSS}{ct.CSS}</style>\n" + body)


def contratto():
    """14. (L42d) il PRB, le ADR, i requisiti e le NC, letti e controllati."""
    req = ct.read_requirements()
    adrs = ct.read_adrs()
    ncs = ct.read_nc_ids()
    prb = ct.read_prb()
    used = ct.check_prb(prb, req, adrs, ncs)
    return {"req": req, "adrs": adrs, "prb": prb, "used": used, "nonreq": ct.non_req(req)}


# ------------------------------------------------------------------ main ---
DECKS = ["tb_op.cir", "tb_ac.cir", "tb_loop.cir", "tb_loop_blockA.cir",
         "tb_loop_bufferfissa.cir", "tb_trim.cir", "tb_zout_psrr_noise.cir",
         "tb_noise_breakdown.cir", "tb_dc_headroom.cir", "tb_switch_v2.cir",
         "tb_switch_v2_counterfactual.cir", "tb_v3_overload.cir", "tb_mute_corto.cir",
         "tb_e4_uscite.cir"]


def main():
    standalone = None
    if "--standalone" in sys.argv:
        standalone = os.path.abspath(sys.argv[sys.argv.index("--standalone") + 1])
    completa = all(p in PARTI for p in PARTI_TUTTE)
    # L51a: finche' le parti non ci sono tutte, niente accanto al generatore. L51c: la
    # pagina autoconsistente resta solo fuori dal repo anche con la pagina completa (come
    # stampa_a4.py): accanto a index.html sarebbe una seconda copia, una seconda verita'.
    if standalone and os.path.commonpath([standalone, REPO]) == REPO:
        print(f"RIFIUTATO: {standalone} sta dentro il repository"
              + ("" if completa else f", e la pagina ha solo le parti {', '.join(PARTI)}")
              + ". La pagina autoconsistente si scrive altrove. Nessun file e' stato scritto.",
              file=sys.stderr)
        return 1

    M = {"ct": contratto(),
         "resp": measure_response(), "v1": measure_v1(),
         "psrr": measure_psrr(), "noise": measure_noise(), "trim": measure_trim(),
         "cf": measure_counterfactual(), "v2": measure_v2(), "v3": measure_v3(),
         "p7": measure_p7(), "op": measure_oppoint(),
         "mute": measure_mute(), "il": measure_interlock(), "e3e5": measure_e3e5(),
         "sel": measure_selector()}
    M["vol"] = measure_volume(M["e3e5"])
    M["z"] = measure_zout(M["resp"])
    M["e4"] = measure_e4(M["z"])
    M["hr"] = measure_headroom(M["trim"])
    M["l2"] = seconda_strada()
    M["dist"] = measure_distortion()
    M.update({"lim": measure_limitatore(), "gb": measure_guasti_blocco(), "stax": measure_stax()})
    if "schede" in PARTI:
        M["brd"] = measure_boards()
    if "alimentatore" in PARTI:
        # L64b: il banco della rete prima del calore (il calore lo usa come seconda strada)
        M["car"] = carico_di_oggi(M["op"])
        M["pw"] = measure_psu_power()
        M["heat"] = measure_heat(M["op"], M["pw"])
        M.update({"sq": measure_seq(), "cs": measure_censimento(), "sb": measure_consumo(),
                  "off": measure_chain(), "p9": p9_soglie(), "st": soglie_timer()})
        M["vt"] = verdetti_timer(M["sq"]["an"], M["st"])
        M["dg"] = measure_diag(M["sq"]["an"], M["cs"])
    M["decks"] = ([os.path.join(TB, d) for d in DECKS]
                  + [os.path.join(TB, "tb_v2_casopeggiore.cir"), os.path.join(TB, "tb_e3_e5.cir"),
                     os.path.join(TB, "tb_f1_selettore.cir"),
                     os.path.join(L64A, "bilanciamento", "tb_e5_bilanciamento.cir"),
                     os.path.join(L64A, "bilanciamento", "tb_loop_bilanciamento.cir")]
                  + [os.path.join(L51CD, "deck", "oggi", d + ".cir") for d in DIST_DECKS])
    for deck in M["decks"]:
        provenance(deck)
    for name in SCHEMATICS:
        if not os.path.isfile(os.path.join(SCHEM, name)):
            refuse(f"schema mancante: {rel(os.path.join(SCHEM, name))}")

    if FAILURES:
        print("RIFIUTATO: il dossier non coincide con la propria evidenza.", file=sys.stderr)
        for f in FAILURES:
            print(f"  - {f}", file=sys.stderr)
        print("Nessun file e' stato scritto.", file=sys.stderr)
        return 1

    figs = {
        "fig_response.svg": fig_response(M["resp"]),
        "fig_response_adr014.svg": fig_response_adr014(M["resp"]),
        "fig_v1.svg": fig_v1(M["v1"]),
        "fig_loop.svg": fig_loop(M["v1"]),
        "fig_psrr.svg": fig_psrr(M["psrr"]),
        "fig_zout.svg": fig_zout(M["z"]),
        "fig_headroom.svg": fig_headroom(M["hr"]),
        "fig_counterfactual.svg": fig_counterfactual(M["cf"], M["hr"]),
    }
    # L51a: la pagina autoconsistente incorpora le figure di QUESTA corsa, non i file
    # rimasti su disco dalla corsa prima
    M["figs"] = figs
    page = build_page(M, inline=False)
    spage = build_page(M, inline=True) if standalone else None
    if FAILURES:          # la provenienza delle sezioni passa anche da build_page
        print("RIFIUTATO:", *FAILURES, sep="\n  - ", file=sys.stderr)
        print("Nessun file e' stato scritto.", file=sys.stderr)
        return 1

    v1, hr, trim, mu, ee = M["v1"], M["hr"], M["trim"], M["mute"], M["e3e5"]
    summary = {
        "parti": list(PARTI),
        "dati": [rel(L64D), rel(mu["mat_dir"]), rel(mu["src_dir"]), rel(M["il"]["corsa_dir"]),
                 rel(M["vol"]["scatti_dir"])],
        "controlli_incrociati": "tutti superati",
        "seconda_strada_L66": {"deck": len(M["l2"]["decks"]), "misure": M["l2"]["n_mis"],
                               "misure_mute": M["l2"]["n_mute"], "righe": M["l2"]["n_res"],
                               "tabelle": M["l2"]["n_tab"]},
        "guadagno_1kHz_dB": {m: M["resp"][(m, "1.5")]["g1k"] for m in MODES},
        "adr014_scarto_20kHz_rif_1kHz_dB_peggiore": max(adr014(M["resp"])[0].values(), key=abs),
        "v1_minimo_gradi": v1["min"],
        "v1_minimo_bilanciamento_gradi": M["vol"]["v1_min"],
        "v1_minimo_per_istanza_gradi": {html_escape(k).replace("&amp;middot;", "·")
                                        .replace("&amp;minus;", "−"): x for k, x in v1["inst"]},
        "headroom_nc009_M1_dB_10db_trim_-6": hr["modes"]["10db"]["trim"]["6"]["M1"],
        "headroom_nc009_M1_dB_10db_trim_0": hr["modes"]["10db"]["trim"]["0"]["M1"],
        "trim_attenuazione_dB": {p: trim["att"][p] for p in ("0", "6", "12")},
        "e3_min_zin_ohm": min(trim["e3min"], ee["e3min"]),
        "e5_catena_peggiore_uV": max(trim["e5max"], ee["e5max"], M["vol"]["e5_girato"]),
        "f1_selettore_peggiore_fino_a_100mV_V": max(
            c["v"] for k, c in M["sel"]["cells"].items() if k[0] != "99" and float(k[1]) <= 0.1),
        "f1_limite_continua_V": M["sel"]["lim"],
        "volume_scatto_peggiore_V": M["vol"]["vol_max"],
        "v2_mute_verdetti": {"totale": mu["n"], "fuori": mu["n_fuori"], "dichiarate": mu["n_dich"]},
        "v2_mute_clic_peggiore_V": float(mu["clic"][0]["c2_V"]),
        "interblocco_corsa_cadute_al_rilascio": {k: v["ril"] for k, v in M["il"]["corsa"].items()},
        "psrr_peggiore_10kHz_dB": min(r["p10k"] for r in M["psrr"].values()),
        "zout_jack_1kHz_ohm_0db": M["z"]["0db"]["z1k"],
        "e4_rez_max_ohm": {f'{g["out"]} {"+".join(g["modes"])}': g["zrmax_max"]
                           for g in M["e4"]["groups"]},
        "e4_dispersione_volume_ohm": max(g["disp"] for g in M["e4"]["groups"]),
        "p7_tj_massima_C": M["p7"]["tjmax"],
        "contratto": {"voci_prb": len(M["ct"]["prb"]["voci"]), "adr": len(M["ct"]["adrs"]),
                      "requisiti": len(M["ct"]["req"]), "rimandi": M["ct"]["rimandi"]},
    }
    if "alimentatore" in PARTI:
        summary.update({
            "calore_totale_W": {"nominale": M["heat"]["tot"][1], "massimo": M["heat"]["tot"][3]},
            "psu_tenuta_vrelay_ms": {f: float(M["pw"]["oggi"][f"perdita_rete_{f}"]["vr_hold_ms"])
                                     for f in ("m10", "nom", "p10")},
            "permissivo_dopo_il_mute_ms_minimo": min(v for c, k, v, s_, ok in M["vt"]
                                                     if c == "perm" and v is not None),
            "musica_dopo_buco_20ms_ms_minima": min(v for c, k, v, s_, ok in M["vt"]
                                                   if c == "mus" and v is not None),
            "criteri_del_temporizzatore": f'{sum(x[4] for x in M["vt"])} su {len(M["vt"])}',
            "standby_mW_da_T2": {k: M["sb"][k]["t2"] for k in ("m10", "nom", "p10")},
            "sequenze_corse": len(M["sq"]["corse"]),
            "seconda_strada_celle": {k: M["sq"]["l2"].get(k) for k in ("celle", "identiche", "entro", "fuori")},
            "calore_peggiore_vano_3cm_C": next((v[5] for v in M["heat"]["vano"]
                                                if v[0] == "3 cm" and v[1] == "peggiore"), None),
            "calore_gioco_minimo_cm": M["heat"]["gioco"],
            "guasti_al_jack_V": {r["caso"]: float(r["picco_V"]) for r in M["off"]["rows"]
                                 if r.get("picco_V") not in ("-", "")},
            "carico_del_banco": M["car"]})
        summary["dati"] += [rel(L64B)]
    d = M["dist"]
    summary["dati"].append(rel(L51CD))
    summary["v4_distorsione"] = {"thd_20kHz_0p2V_pct": d["thd_lo"]["20k"],
                                 "armoniche_5_in_su_0p2V_dB": d["h5_lo"],
                                 "imd_ccif_0p2V_dB": d["imd_lo"],
                                 "thd_20kHz_2V_pct": d["thd_hi_20k"],
                                 "tetti": d["soglie"], "conforme": all(d["ok"].values())}
    if "schede" in PARTI:
        b = M["brd"]
        summary["dati"] += [rel(L49A), rel(L49B), rel(os.path.join(L51C, "drc"))]
        summary["schede_di_prova"] = {
            k: {"mm": v["meas"]["board_mm"], "drc_oggi_violazioni_aperte": list(v["drc"][:2]),
                "kicad": v["kicad"]} for k, v in b["boards"].items()}
        summary["schede_di_prova"]["assieme"] = b["fit"].get("title")

    if completa:
        for name, body in figs.items():
            with open(os.path.join(HERE, name), "w") as f:
                f.write(body)
            print(f"   scritto {name} ({len(body)} byte)")
        for name in SCHEMATICS:
            shutil.copyfile(os.path.join(SCHEM, name), os.path.join(HERE, name))
            print(f"   copiato {name} da {rel(SCHEM)}/")
        for name, parts in IMMAGINI.items():
            shutil.copyfile(os.path.join(*parts), os.path.join(HERE, name))
            print(f"   copiato {name} da {rel(os.path.join(*parts))}")
        with open(os.path.join(HERE, "index.html"), "w") as f:
            f.write(page)
        print(f"   scritto index.html ({len(page)} byte)")
        with open(os.path.join(HERE, "dossier.summary.json"), "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("   scritto dossier.summary.json")
    else:
        print(f"   la pagina ha le parti {', '.join(PARTI)} su {', '.join(PARTI_TUTTE)}: "
              "niente e' scritto accanto al generatore")
    if standalone:
        with open(standalone, "w") as f:
            f.write(spage)
        print(f"   scritto {standalone} (autoconsistente, {len(spage)} byte)")
        if not completa:
            with open(os.path.splitext(standalone)[0] + ".summary.json", "w") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                f.write("\n")
    print("OK: tutti i controlli incrociati sono passati.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
