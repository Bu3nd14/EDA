#!/usr/bin/env python3
"""L68: what each part of the comparator timer does, its connectors and its test points, and the rates of
its modes (the classes of data/2026-10-14/L45c2/script/classi_l45c2.py, SN 29500 / IEC 61709 / FMD-2016
as L45c2 took them). Imported by fmea_l68.py. Solo stdlib.

The comparator: classi_l45c2.py's CMP is 12 FIT for the dual (TI SFFS282, SN 29500-2 table 4, a
TLV1812/1822's), with the per-channel shares cieco 0.20, basso 0.125, the pin 0.05 of the package. A
TLV1704 is taken as two duals (24 FIT): a channel blind 2.4 FIT, stuck low 1.5 FIT, the supply pin
1.2 FIT (the assumption, declared in the row). The PP film of C548 / C552 takes the ceramic's class
(no film class in the table: declared).
"""

# class: (FIT of the part, {mode key: share})
CLASSI = {
    "R": (0.5, {"aperto": 0.59, "deriva": 0.36, "corto": 0.05}),
    "C_cer": (1.0, {"corto": 0.49, "valore": 0.29, "aperto": 0.22}),
    "D_seg": (1.0, {"deriva": 0.58, "aperto": 0.24, "corto": 0.18}),
    "BJT": (2.0, {"corto": 0.73, "aperto": 0.27}),
    "CMP4": (24.0, {"cieco": 0.40 / 4, "basso": 0.25 / 4, "pin": 0.05}),
    "CONN": (0.5, {"aperto": 0.61, "intermittente": 0.23, "corto": 0.16}),
}
FONTE_CLASSE = {
    "R": "classi_l45c2.py R: 0,5 FIT (STIMA, film SMD)",
    "C_cer": "classi_l45c2.py C_cer: 1,0 FIT (STIMA, ceramico SMD)",
    "C_film": "classi_l45c2.py C_cer: 1,0 FIT (il film PP preso come il ceramico: nessuna classe film, dichiarato)",
    "D_seg": "classi_l45c2.py D_seg: 1,0 FIT (STIMA, diodo di segnale)",
    "BJT": "classi_l45c2.py BJT: 2,0 FIT (STIMA, bipolare di segnale)",
    "CMP4": "classi_l45c2.py CMP: 12 FIT il doppio (TI SFFS282, SN 29500-2 tab. 4); il TLV1704 come due doppi",
    "CONN": "classi_l45c2.py CONN: 0,5 FIT per contatto (STIMA)",
}


def classe(ref):
    if ref.startswith("U"):
        return "CMP4"
    if ref.startswith("Q"):
        return "BJT"
    if ref.startswith("D"):
        return "D_seg"
    if ref in ("C548", "C552"):
        return "C_film"
    if ref.startswith("C"):
        return "C_cer"
    if ref.startswith("R"):
        return "R"
    if ref.startswith("J"):
        return "CONN"
    return None


def fit(ref, chiave):
    """The FIT of one mode of one part; the BJT's «corto» split in two (C-E, B-E), as a share each."""
    k = classe(ref)
    if k is None:
        return None
    tot, quote = CLASSI["C_cer" if k == "C_film" else k]
    if k == "BJT" and chiave in ("ce", "be"):
        return tot * quote["corto"] / 2
    return tot * quote[chiave]


def classe_p(f):
    return 1 if f < 1 else 2 if f <= 10 else 3 if f <= 100 else 4


FUNZ = {
    "U513": "TLV1704: l'alimentazione buona (A il rail +, B il rail -, C VRELAY_REG su AT_PG) e la rete "
            "presente (D su AT_MD)",
    "U514": "TLV1704: il mute (A l'alimentazione buona da 1,1 s, B il tasto del mute, su AT_MRQ; C MUTE_REQ) "
            "e il permesso (D PERMIT_REQ)",
    "U515": "TLV1704: A il frontale (AT_ON), B K501 (MAINS_REQ), C / D l'innesco della ritenuta (AT_F: non "
            "armata, alimentazione buona)",
    "Q513": "BC847: la ritenuta (con Q514), il transistore NPN",
    "Q514": "BC857: la ritenuta (con Q513), il transistore PNP, emettitore su AT_ON",
    "D533": "BAT54: AT_PG svuotato quando la rete manca (AT_MD)",
    "D537": "BAT54: AT_MRQ svuotato quando il frontale si spegne (AT_ON)",
    "D538": "1N4148: AT_PRT svuotato da AT_MRQ (il permesso dopo il mute)",
    "D539": "1N4148: AT_MT caricato da AT_ON (K501)",
    "D540": "1N4148: AT_MT caricato da VR_G (K501 dopo il permesso)",
    "C545": "100 nF: il disaccoppiamento di U513 sui 5 V",
    "C546": "100 nF: il disaccoppiamento di U514 sui 5 V",
    "C547": "100 nF: il disaccoppiamento di U515 sui 5 V",
    "C548": "1 uF film PP: il ritardo dopo l'alimentazione buona (AT_PGT, ADR-105 / ADR-108)",
    "C549": "100 nF C0G: l'antirimbalzo del mute (AT_MRQ, ADR-105)",
    "C550": "10 nF C0G: il ritardo del permesso (AT_PRT, ADR-105)",
    "C551": "100 nF C0G: il ritardo di K501 (AT_MT, ADR-105)",
    "C552": "1 uF film PP: l'armamento della ritenuta (AT_T2S, ADR-105 / ADR-108)",
    "C553": "330 nF C0G: l'innesco della ritenuta (AT_F, ADR-108)",
    "C554": "1 nF: base-emettitore di Q513 (contro i fronti)",
    "C555": "1 nF: base-emettitore di Q514 (contro i fronti)",
    "R569": "100 kOhm: il pull-up di AT_MD (la rete presente)",
    "R570": "100 kOhm: il pull-up di AT_PG (l'alimentazione buona)",
    "R571": "1,1 MOhm: il ritardo dopo l'alimentazione buona (AT_PGT, ADR-105)",
    "R572": "100 kOhm: l'antirimbalzo del mute (AT_MRQ), la meta' verso i 5 V (con R588, ADR-116)",
    "R588": "100 kOhm: l'antirimbalzo del mute (AT_MRQ), la meta' verso AT_MRQ (con R572, ADR-116)",
    "R573": "10 kOhm: il pull-up di MUTE_REQ",
    "R574": "4,7 MOhm: il ritardo del permesso (AT_PRT)",
    "R575": "10 kOhm: il pull-up di PERMIT_REQ",
    "R576": "4,99 kOhm: il pull-up di AT_ON (VRELAY_EN, il frontale), la meta' verso i 5 V (con R589, ADR-116)",
    "R589": "4,99 kOhm: il pull-up di AT_ON (VRELAY_EN, il frontale), la meta' verso AT_ON (con R576, ADR-116)",
    "R577": "1 kOhm: AT_ON verso D539 (K501)",
    "R578": "1 MOhm: la scarica di AT_MT (il ritardo di K501)",
    "R579": "22 kOhm: il pull-up di MAINS_REQ",
    "R580": "2,7 MOhm: l'armamento della ritenuta (AT_T2S)",
    "R581": "100 kOhm: il pull-up di AT_F (l'innesco della ritenuta)",
    "R582": "47 kOhm: AT_F verso la base di Q513",
    "R583": "100 kOhm: base-emettitore di Q513",
    "R584": "100 kOhm: base-emettitore di Q514",
    "J4": "il cablaggio del temporizzatore verso la scheda audio: MUTE_CMD, PERMIT_CMD, MUTE_SW",
    "J508": "il cablaggio dell'interruttore frontale: FRONT_SW, RLY_RET",
    "J510": "l'ingresso di rete dal modulo IEC (L, N, dopo il suo fusibile)",
    "J511": "il primario di T2 (L, N)",
    "J512": "il primario di T1 (L, N)",
}
TP = {"TP501": "VPLUS", "TP502": "VMINUS", "TP503": "GND", "TP504": "VRELAY", "TP505": "VRELAY_REG",
      "TP506": "RLY_RET", "TP507": "V5", "TP508": "MUTE_G", "TP509": "PERMIT_G", "TP510": "PERMIT_T",
      "TP511": "RLY_RET", "TP512": "MUTE_CMD", "TP513": "PERMIT_CMD", "TP514": "MAINS_G",
      "TP515": "MAINS_COIL", "TP516": "VR_G", "TP517": "RLY_RET"}
for _t, _n in TP.items():
    FUNZ[_t] = "test point di %s (ADR-107)" % _n
