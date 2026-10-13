#!/usr/bin/env python3
"""L45b: la tabella dei guasti dei controlli (fmea_controlli.csv e .md). Solo stdlib.

Ogni riga e' un modo di guasto di una parte dei controlli della scheda audio, letta dal sorgente
(preamp_audio.py, gain_interlock.py, selector.py, trim.py; i piloti in psu.py). Le righe «sim»
prendono i numeri dalle corse (analisi_ctl.csv a vuoto, analisi_ctl_carico.csv coi carichi,
analisi_lunghe.csv fino a 6 s); le altre portano il ragionamento e il numero a cui rimandano.

Al jack: il gradino GREZZO (senza filtro, P10) in volt e in dB SPL di picco a 1 m con la formula
del PRB, 96 + 20 log10(V * 21,1 / 2,83); 0,87 V = 112,2 dB, il tetto di non-danno. Sulle fisse il
peggiore delle due in volt, e la Stax all'orecchio con la catena di NC-046 (101 + 20 log10(V * 10)).
P10 (ADR-069): il tempo sopra 0,87 V al jack senza filtro, a vuoto, dal guasto.
"""
import csv
import math
import os

QUI = os.path.dirname(os.path.abspath(__file__))
L45B = os.path.dirname(QUI)


def carica(nome):
    p = os.path.join(L45B, nome)
    return {r["modo"]: r for r in csv.DictReader(open(p))} if os.path.exists(p) else {}


VUOTO = carica("analisi_ctl.csv")
VUOTO.update(carica("analisi_rs.csv"))
VUOTO.update(carica("analisi_latenti.csv"))
CARICO = carica("analisi_ctl_carico.csv")
LUNGHE = {k.split("__", 1)[1]: v for k, v in carica("analisi_lunghe.csv").items()}


def virgola(x):
    return ("%.3g" % x).replace(".", ",")


def volt(v):
    v = abs(v)
    if v >= 1:
        return virgola(v) + " V"
    if v >= 1e-3:
        return virgola(v * 1e3) + " mV"
    if v >= 1e-6:
        return virgola(v * 1e6) + " µV"
    return "< 1 µV"


def db(v):
    return 96 + 20 * math.log10(max(abs(v), 1e-12) * 21.1 / 2.83)


def db_stax(v):
    return 101 + 20 * math.log10(max(abs(v), 1e-12) * 10)


def ms(r, k):
    return float(r.get(k + "_sopra_ms") or 0)


def da_sim(modo):
    """(principale, fisse, p10 a vuoto, p10 col carico) dalle corse."""
    r = VUOTO.get(modo)
    if r is None:
        return ("(corsa mancante)",) * 4
    m = float(r["main_grezzo_V"])
    f1, f2 = float(r["fix1_grezzo_V"]), float(r["fix2_grezzo_V"])
    princ = volt(m) + (" (%.0f dB SPL)" % db(m) if abs(m) >= 1e-6 else "")
    fisse = volt(max(f1, f2)) + ("; Stax %.0f dB SPL" % db_stax(f2) if abs(f2) >= 1e-6 else "")
    lung = LUNGHE.get(modo)
    sorg = lung if lung is not None else r

    def p10(rr, suff=""):
        parti = []
        for j, nome in (("main", "princ."), ("fix1", "Singxer"), ("fix2", "Stax")):
            t = ms(rr, j)
            if t > 0:
                ancora = rr.get("p10", "").find(j) >= 0 and "ancora" in rr.get("p10", "")
                parti.append("%s %s%.0f ms" % (nome, "≥ " if ancora else "", t))
        return ("; ".join(parti) or "0 ms") + suff

    pv = p10(sorg, " (6 s)" if lung is not None else "")
    rc = CARICO.get(modo)
    pc = p10(rc) if rc is not None else "—"
    return princ, fisse, pv, pc


# (gruppo, parte, modo, effetto, sim o None, (principale, fisse, p10) se calcolo, requisiti, a chi)
G_SEL = "Selettore d'ingresso (K13–K16, SW4, D16–D19)"
G_GAIN = "Guadagno (K1, K5, ausiliari K11, K12, SW2, D10–D15)"
G_TRIM = "Permesso e trim (K6, K7–K10, SW1, D1–D3)"
G_MUTE = "Mute (K2–K4) e i suoi comandi (Q501, Q502)"
G_LED = "LED (R1–R3, J5–J7)"
G_PAS = "Condensatori, bleed e resistenze del percorso"
G_FW = "Firmware e micro (U509)"
ZERO = ("0 (nessun gradino)", "0", "0 ms")
ADR051 = ("≤ 29,7 mV (~83 dB SPL), ADR-051", "—", "0 ms")
RIGHE = [
    # ---------------- selettore
    (G_SEL, "K13–K16", "bobina aperta (l'ingresso scelto)", "il contatto si apre: l'ingresso tace, il "
     "blocco A resta sul suo R_IN 1 MΩ", "S_ap", None, "F1", "—"),
    (G_SEL, "K13–K16", "bobina in corto", "SW4 mette `VRELAY` in corto su `RLY_RET`: la linea dei relè "
     "crolla, il sorvegliante di `VRELAY` muta; è la classe di ADR-051 (corto della linea a 12 V)",
     None, ADR051, "P9 (b), ADR-051", "L45c"),
    (G_SEL, "K13–K16", "contatto NO saldato (un ingresso non scelto)", "due sorgenti in parallelo "
     "attraverso i loro C_IN; i due lati del preamp sono a 0 V (R_SEL), quindi nessuna continua: è il "
     "caso «due relè chiusi insieme» di ADR-064, 3,5 µV a 100 mV di continua della sorgente", None,
     ("≤ 20 µV (ADR-064)", "≤ 20 µV", "0 ms"), "F1, PR-14", "—"),
    (G_SEL, "K13–K16", "contatto aperto, o un polo sì e l'altro no", "un canale tace", "S_ap", None,
     "F1", "—"),
    (G_SEL, "K13–K16", "rimbalzo", "l'apertura per un istante del contatto: come il cambio d'ingresso "
     "di ADR-064 (il trasferimento di 1 ms misurato in L48a)", None,
     ("≤ 19,8 µV (L48a)", "≤ 6,3 µV", "0 ms"), "F1", "—"),
    (G_SEL, "K13–K16", "isolamento fra bobina e contatti che cede (la bobina scelta è a 12 V)",
     "12 V all'ingresso del blocco A: il blocco A va al rail, e con lui le due fisse (in continua) e il "
     "principale (attraverso C_T e il blocco B)", "I_K13", None, "**P10**, PR-30", "L45d"),
    (G_SEL, "K13–K16", "lo stesso, con 1 kΩ di percorso (a metà bobina)", "come sopra", "I_K13_1k",
     None, "**P10**, PR-30", "L45d"),
    (G_SEL, "D16–D19", "ricircolo in corto", "la bobina scelta in corto: come la bobina in corto",
     None, ADR051, "ADR-051", "L45c"),
    (G_SEL, "D16–D19", "ricircolo aperto", "il colpo induttivo della bobina sul contatto di SW4 a ogni "
     "cambio: usura del commutatore, nessun effetto al jack", None, ZERO, "—", "—"),
    (G_SEL, "SW4", "contatto saldato, o fermo fra due posizioni", "un ingresso fisso, o nessuno, o due "
     "insieme (come il NO saldato)", None, ("≤ 20 µV", "≤ 20 µV", "0 ms"), "F1", "—"),
    # ---------------- guadagno
    (G_GAIN, "K1 (o K11), K5 (o K12)", "bobina aperta durante l'ascolto, o l'ausiliario che cade "
     "(la tenuta si perde)", "il guadagno scende durante l'ascolto: +3 → 0, +10 → +3 o 0. Coi LED letti "
     "dall'ausiliario, se cade solo K1 il LED dice +3 col segnale a 0 (ADR-033)", "G_10a0", None,
     "PR-18 (cambia fuori mute, ma solo verso il basso)", "—"),
    (G_GAIN, "K1, K5, K11, K12", "bobina in corto", "il comando o la tenuta mette `VRELAY` in corto "
     "appena la bobina è alimentata; il guadagno torna a 0 dB", None, ADR051, "ADR-051", "L45c"),
    (G_GAIN, "K1 (un polo)", "contatto NO saldato", "a riposo quel canale resta a +3 dB (+10 per K5): "
     "il guadagno «a riposo» non è 0 dB, e i LED (dagli ausiliari) dicono 0. Al guasto nessun gradino: "
     "il contatto si salda quando è già chiuso", None, ZERO, "**PR-18** («mai più alto»), ADR-033",
     "L45d"),
    (G_GAIN, "K1 (un polo)", "contatto aperto", "quel canale perde il ramo: scende di 3 (o 10) dB "
     "durante l'ascolto, sbilanciato sull'altro", "G_3a0", None, "PR-18", "—"),
    (G_GAIN, "K1, K5", "rimbalzo (urto meccanico a contatto chiuso)", "il guadagno scende per un istante",
     "G_10a3", None, "—", "—"),
    (G_GAIN, "K1, K5", "isolamento fra bobina e contatti", "non fisico: quando la bobina è a 12 V il "
     "contatto è chiuso a massa (il ramo del blocco B va a massa), e quando il contatto è aperto la "
     "bobina è a 0 V. Il cedimento mette solo `VRELAY` a massa attraverso il contatto: ADR-051. La "
     "corsa con 12 V sul ramo (I_K1, ~0,9 s) è un limite che il circuito non raggiunge", None, ADR051,
     "ADR-051", "L45c"),
    (G_GAIN, "K11 (polo di tenuta)", "contatto NO saldato", "fuori mute `VHOLD` riporta su K1 anche se "
     "la manopola è a 0: al rilascio del mute il guadagno sale a +3, insieme al collegamento dei jack. "
     "I LED dicono +3 (vero)", "G_0a3", None, "**PR-18** (più alto della manopola)", "L45d"),
    (G_GAIN, "K11, K12 (polo dei LED)", "contatto saldato o aperto", "un LED sbagliato o spento; il "
     "segnale non cambia", None, ZERO, "PR-18 (LED), ADR-033", "—"),
    (G_GAIN, "D10, D11 (Schottky del comando)", "corto", "fuori mute, a +3 o +10, `G3_HI` ritorna su "
     "`VTRIM`: il **trim** si comanda fuori mute, e il LED rosso del mute si **accende con la musica**",
     "T_0a12", None, "**PR-17**, PR-19 (LED di mute)", "L45d"),
    (G_GAIN, "D10, D11", "aperto", "il guadagno non sale più: resta a 0 dB", None, ZERO, "F5", "—"),
    (G_GAIN, "D12, D13 (diodi della tenuta)", "corto", "in mute, passando da +10 a +3, `H3` tiene K5 "
     "attraverso `VHOLD`: resta +10 con la manopola a +3. Solo in mute; i LED dicono +10 (vero)", None,
     ZERO, "PR-18 (più alto della manopola, in mute)", "L45d"),
    (G_GAIN, "D12, D13", "aperto", "la tenuta (c) si perde: fuori mute K1 resta solo dal ponte, quindi "
     "girare la manopola fuori mute abbassa il guadagno durante l'ascolto", "G_10a0", None,
     "PR-18 (cambia fuori mute, verso il basso)", "—"),
    (G_GAIN, "D14, D15 (ricircolo)", "corto", "`G3_HI` in corto: comandarlo mette `VRELAY` in corto; il "
     "guadagno non sale", None, ADR051, "ADR-051", "L45c"),
    (G_GAIN, "D14, D15", "aperto", "il colpo induttivo sul contatto di SW2 e su quello di K11: usura, "
     "niente al jack", None, ZERO, "—", "—"),
    (G_GAIN, "SW2", "un polo saldato (il comando a)", "in mute K1 sale qualunque sia la manopola; i "
     "LED dicono il vero", None, ZERO, "PR-18 (in mute)", "—"),
    (G_GAIN, "SW2", "un polo aperto", "il guadagno non sale (o non resta fuori mute: come D12 aperto)",
     "G_3a0", None, "PR-18", "—"),
    # ---------------- permesso e trim
    (G_TRIM, "K6", "bobina aperta (o Q502 aperto)", "K6 non si eccita mai: `VTRIM` sempre viva, `VHOLD` "
     "morta. Trim **e** guadagno seguono la manopola **fuori mute**, a jack collegati; il LED rosso del "
     "mute resta **acceso con la musica**. È il «Da riaprire se» di ADR-027, in silenzio", "G_0a10",
     None, "**PR-17, PR-18**, PR-19 (LED di mute); ADR-027 «Da riaprire se»", "L45d"),
    (G_TRIM, "K6", "bobina in corto", "`PERMIT_CMD` mette `VRELAY` in corto attraverso Q502 al rilascio "
     "del mute: la linea dei relè crolla, il sorvegliante muta", None, ADR051, "ADR-051", "L45c, L54"),
    (G_TRIM, "K6", "un contatto NC saldato", "l'altro NC apre: l'interblocco regge (i due NC in serie, "
     "ADR-027). Latente: col secondo, il caso della bobina aperta", None, ZERO, "—", "—"),
    (G_TRIM, "K6", "NO (polo 1) saldato", "`VHOLD` sempre viva e `VTRIM` morta: trim e guadagno fermi "
     "anche in mute; il LED rosso non si accende mai (sbaglia verso il lato sicuro)", None, ZERO,
     "PR-17, PR-18 (non si cambiano più)", "—"),
    (G_TRIM, "K6", "contatto aperto", "`VTRIM` morta: il trim fermo, il guadagno non sale; LED rosso "
     "spento", None, ZERO, "PR-17", "—"),
    (G_TRIM, "D3 (ricircolo di VTRIM)", "corto", "in mute `VTRIM` va a massa: `VRELAY` in corto attraverso "
     "i NC di K6 a ogni inserzione, a jack già staccati", None, ("< 1 µV (jack staccati)", "—", "0 ms"),
     "ADR-051", "L45c"),
    (G_TRIM, "K7, K8 (bistabili del trim)", "bobina aperta", "il trim resta dov'è; lo spia (K9, K10) si "
     "muove e il LED dice uno stato che il segnale non ha (ADR-033)", None, ZERO,
     "PR-17 (LED), ADR-033", "—"),
    (G_TRIM, "K7, K8, D1, D2", "bobina o TVS in corto", "SW1 mette `VTRIM` in corto: solo in mute, a "
     "jack staccati", None, ("< 1 µV (jack staccati)", "—", "0 ms"), "ADR-051", "L45c"),
    (G_TRIM, "K7, K8", "contatto saldato (un polo)", "quel canale resta al suo trim: sbilanciamento fino "
     "a 12 dB fra i canali", None, ZERO, "PR-17", "—"),
    (G_TRIM, "K7", "comune aperto", "C_T appeso: il canale tace sul principale", "T_com_ap", None,
     "—", "—"),
    (G_TRIM, "K7, K8", "il bistabile che commuta da solo (urto, campo) durante l'ascolto", "il trim cambia "
     "fuori mute", "T_0a12", None, "PR-17", "—"),
    (G_TRIM, "K7, K8", "isolamento fra bobina e contatti", "la bobina è a 12 V solo in mute (`VTRIM`): "
     "durante l'ascolto il cedimento non porta niente. In mute spinge l'uscita del blocco A verso 12 V, "
     "a lati dei condensatori a massa; al rilascio `VTRIM` muore non dopo il collegamento dei jack, e "
     "l'uscita del blocco A torna a 0 con i condensatori carichi. La corsa I_K7 (12 V durante l'ascolto) "
     "è il limite superiore", "I_K7", None, "P10 (limite superiore)", "L45d"),
    (G_TRIM, "K9, K10 (spia)", "qualunque", "solo i LED (ADR-033)", None, ZERO, "PR-17 (LED)", "—"),
    (G_TRIM, "SW1", "contatto saldato o aperto", "il trim non si comanda; solo in mute", None, ZERO,
     "PR-17", "—"),
    # ---------------- mute e comandi
    (G_MUTE, "K2–K4", "bobina aperta durante l'ascolto (o il polo che si apre)", "quell'uscita si "
     "stacca: il deviatore apre il NO e chiude l'NC, come all'inserzione del mute", "K4_cade", None,
     "PR-21", "—"),
    (G_MUTE, "K2–K4", "bobina in corto", "`MUTE_CMD` mette `VRELAY` in corto attraverso Q501: Q501 o la "
     "linea cedono, il sorvegliante di `VRELAY` muta", None, ADR051, "ADR-051", "L45c, L54"),
    (G_MUTE, "K2–K4", "NO saldato", "quell'uscita non si stacca più: al guasto niente, ma lo spegnimento, "
     "la perdita di rete e il guasto dell'alimentatore la trovano **collegata**. Il LED rosso non lo "
     "vede (limite dichiarato, ADR-028). Le corse L_spegnimento e L_accensione", "L_spegnimento", None,
     "**PR-23** (latente), PR-21", "L45d"),
    (G_MUTE, "K2–K4", "NC saldato", "quell'uscita resta staccata, lato del condensatore a massa", None,
     ZERO, "—", "—"),
    (G_MUTE, "K2–K4", "NO aperto", "quell'uscita tace", "K4_no_ap", None, "—", "—"),
    (G_MUTE, "K2–K4", "rimbalzo del NO (0,5 ms)", "un'apertura per un istante", "K4_rimbalzo", None,
     "—", "—"),
    (G_MUTE, "K2–K4", "isolamento fra bobina e NO (il jack)", "la bobina è a 12 V sempre (pin 1 su "
     "`VRELAY`): **12 V in continua sul jack**, anche a mute inserito (il NO è il jack stesso). Lo toglie "
     "solo lo spegnimento di `VRELAY`", "I_K4_jack", None, "**P10**, PR-30, PR-23", "L45d"),
    (G_MUTE, "K2–K4", "lo stesso, 1 kΩ", "come sopra", "I_K4_jack_1k", None, "**P10**", "L45d"),
    (G_MUTE, "K2–K4", "isolamento fra bobina e comune (lato condensatore)", "12 V al jack durante "
     "l'ascolto; a mute inserito il comune va a massa sull'NC e il jack si stacca", "I_K4_com", None,
     "**P10**, PR-30", "L45d"),
    (G_MUTE, "K3 (la Stax)", "isolamento fra bobina e NO", "12 V in continua sul jack della Stax",
     "I_K3_jack", None, "**P10**, PR-30, NC-046", "L45d"),
    (G_MUTE, "Q501 (sink di `MUTE_CMD`)", "corto D-S", "i jack restano collegati **sempre**: il mute "
     "non si inserisce più, né dal frontale né dal sorvegliante (che agisce sul gate di Q501). Al guasto "
     "niente; latente come il NO saldato, su tutte e sei le uscite", "L_spegnimento", None,
     "**PR-23**, **PR-24** (latente)", "L45d, L54"),
    (G_MUTE, "Q501", "aperto", "sempre in mute", None, ZERO, "—", "—"),
    (G_MUTE, "Q502 (sink di `PERMIT_CMD`)", "corto D-S", "K6 sempre eccitato: trim e guadagno fermi, il "
     "LED rosso mai acceso; all'accensione i bistabili non vengono pilotati (il trim resta l'ultimo, "
     "non la manopola, ADR-027)", None, ZERO, "PR-17 (accensione)", "L54"),
    (G_MUTE, "Q502", "aperto", "come la bobina di K6 aperta", "G_0a10", None, "PR-17, PR-18", "L45d"),
    (G_MUTE, "D522 (MUTE_G ≤ PERMIT_G)", "corto", "`MUTE_G` legato a `PERMIT_G`: all'inserzione K6 cade "
     "insieme ai jack, Δ si perde, il residuo di L36 torna (il guadagno può muoversi a jack collegati, "
     "solo se la manopola è stata girata fuori mute)", None,
     ("≤ 29,7 mV (ADR-045 / ADR-051)", "—", "0 ms"), "PR-20", "L54"),
    (G_MUTE, "R513, R514, R516, R524–R526, C527", "aperto o corto", "il riposo dei comandi: un pull-down "
     "aperto da solo non cambia niente (c'è l'altro, o la resistenza di gate); un corto di C527 o R514 "
     "tiene il mute. Il dettaglio è del temporizzatore", None, ZERO, "PR-24", "L54"),
    # ---------------- LED
    (G_LED, "R1, R2, LED", "aperto", "i LED del trim o del guadagno spenti: lo stato non si legge", None,
     ZERO, "PR-17, PR-18 (LED)", "—"),
    (G_LED, "R3, LED rosso", "aperto", "il LED di mute spento in mute: sbaglia verso il lato sicuro", None,
     ZERO, "PR-19", "—"),
    (G_LED, "LED rosso", "acceso con la musica", "per K6 o Q502 aperti, o D10/D11 in corto (righe "
     "sopra): l'unico modo in cui un LED **dice «muto» con un jack collegato**", None, ZERO,
     "PR-19, ADR-028 punto 5", "L45d"),
    # ---------------- passivi del percorso
    (G_PAS, "C_OUT 4,7 µF (principale)", "corto", "il jack prende la continua del blocco B attraverso "
     "47 Ω; poi l'uscita è **accoppiata in continua**: un guasto successivo del blocco non decade più "
     "(P10 infinito, guasto doppio)", "Cout_main_cc", None, "— (latente per P10)", "L45d"),
    (G_PAS, "C_OUT 4,7 µF (fisse)", "corto", "lo stesso, dal buffer", "Cout_fix2_cc", None,
     "— (latente)", "L45d"),
    (G_PAS, "C_OUT", "aperto", "l'uscita tace", "Cout_main_ap", None, "—", "—"),
    (G_PAS, "C_T 10 µF", "corto", "la continua del blocco A attraverso trim e volume torna (NC-041): i "
     "passi del volume tornano a farsi sentire (fino a 19,5 mV, L48b)", "CT_cc_g10", None,
     "PR-20 (degrada)", "—"),
    (G_PAS, "C_T", "aperto", "il principale tace", "CT_ap", None, "—", "—"),
    (G_PAS, "C_IN 1 µF", "corto", "la continua della sorgente arriva al blocco A e alle fisse in "
     "continua; con una sorgente sana (≤ 0,65 V, ADR-064) sotto il tetto; con la sorgente a 0 V", "CIN_cc",
     None, "F1", "—"),
    (G_PAS, "R_SEL 470 kΩ", "aperto", "il lato del preamp di un ingresso non scelto deriva sulla perdita "
     "del condensatore: al cambio un gradino fino alla continua della sorgente (ADR-064)", None,
     ("≤ la continua della sorgente", "lo stesso", "0 ms per una sorgente sana"), "F1", "—"),
    (G_PAS, "R_J 10 MΩ", "aperto", "il jack d'ingresso vuoto non è più a 0 V: conta solo inserendo una "
     "sorgente", None, ZERO, "PR-14", "—"),
    (G_PAS, "bleed del jack (RBL)", "aperto", "a mute il jack non ha più ritorno: lo stato sicuro di "
     "ADR-044 si perde, latente", "RBLmain_ap", None, "ADR-044", "—"),
    (G_PAS, "bleed del lato condensatore (RBC)", "aperto", "conta solo nel ms del trasferimento",
     "RBCmain_ap", None, "—", "—"),
    (G_PAS, "47 Ω d'uscita", "corto", "il cavo sullo stadio, dentro l'anello: col gradino d'ingresso e "
     "fino a 10 nF di cavo nessuna oscillazione (squillo.py); la protezione dal corto (P7) perde la sua "
     "resistenza", "RSmain_cc_1n", None, "E4, P7", "L45d (P7)"),
    (G_PAS, "47 Ω d'uscita", "aperto", "l'uscita tace", "RSmain_ap", None, "—", "—"),
    (G_PAS, "scala del trim (845 / 464 / 464 Ω)", "corto o aperto", "un livello sbagliato o il silenzio "
     "a −6/−12 dB; il carico peggiore sul blocco A (R1 in corto) è 928 Ω, 4,1 mA di picco su ~20 mA "
     "di classe A", None, ZERO, "PR-17", "—"),
    # ---------------- firmware
    (G_FW, "LDR", "—", "non ci sono più (ADR-062): il caso di NC-042 «il firmware accende tutte e due "
     "le stringhe» non esiste", None, ZERO, "—", "—"),
    (G_FW, "U509", "firmware bloccato", "il watchdog (≤ 250 ms, timer_spec §4.8) lo resetta; in reset le "
     "uscite sono in alta impedenza e i pull-down le portano a riposo: il mute si inserisce, con Δ in "
     "hardware (PERMIT_T)", None, ZERO, "PR-24", "L54"),
    (G_FW, "U509", "`MUTE_REQ` bloccata alta (il pin, non il firmware)", "la musica resta: il "
     "commutatore del mute e lo spegnimento morbido non la tolgono; il sorvegliante e il rivelatore di "
     "rete sì (agiscono sul gate). PR-24 dice «resta muto»", None, ZERO, "**PR-24**", "L54"),
    (G_FW, "U509", "`MUTE_REQ` bassa, o un'uscita in alta impedenza", "mute", None, ZERO, "PR-24", "—"),
    (G_FW, "U509", "`PERMIT_REQ` bloccata alta", "K6 resta eccitato anche in mute: trim e guadagno non "
     "si cambiano", None, ZERO, "PR-17, PR-18", "L54"),
    (G_FW, "U509", "`MAINS_REQ` bloccata alta", "lo standby non spegne il trasformatore grande", None,
     ZERO, "PR-25", "L54"),
]


def main():
    righe = []
    for n, (g, parte, modo, eff, sim, calc, req, chi) in enumerate(RIGHE, 1):
        if sim:
            princ, fisse, pv, pc = da_sim(sim)
            fonte = "simulato (`%s`)" % sim
        else:
            princ, fisse, pv = calc
            pc = "—"
            fonte = "calcolo"
        righe.append({"n": n, "gruppo": g, "parte": parte, "modo": modo, "effetto": eff,
                      "principale": princ, "fisse": fisse, "p10_vuoto": pv, "p10_carico": pc,
                      "fonte": fonte, "requisiti": req, "a_chi": chi})
    campi = list(righe[0])
    with open(os.path.join(L45B, "fmea_controlli.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi)
        w.writeheader()
        w.writerows(righe)
    out = ["# L45b — la tabella dei guasti dei controlli\n",
           "Generata da `script/tabella_controlli.py`. Al jack il gradino **grezzo** (senza filtro), in "
           "dB SPL di picco a 1 m con la formula del PRB (0,87 V = 112,2 dB, il tetto di non-danno); "
           "sulle fisse il peggiore delle due, e la Stax all'orecchio con la catena di NC-046. **P10**: "
           "il tempo sopra 0,87 V al jack senza filtro, a vuoto (e coi carichi di oggi accanto); «≥» "
           "quando il jack è ancora sopra alla fine della corsa. In grassetto i requisiti che il modo "
           "rompe.\n"]
    gruppo = None
    for r in righe:
        if r["gruppo"] != gruppo:
            gruppo = r["gruppo"]
            out.append("\n## %s\n" % gruppo)
            out.append("| # | Parte | Modo | Effetto | Principale | Fisse | P10 a vuoto | P10 coi carichi "
                       "| Fonte | Requisiti | A chi |")
            out.append("|---|---|---|---|---|---|---|---|---|---|---|")
        out.append("| %s |" % " | ".join(str(r[k]) for k in campi if k != "gruppo"))
    with open(os.path.join(L45B, "fmea_controlli.md"), "w") as f:
        f.write("\n".join(out) + "\n")
    print("righe: %d" % len(righe))


if __name__ == "__main__":
    main()
