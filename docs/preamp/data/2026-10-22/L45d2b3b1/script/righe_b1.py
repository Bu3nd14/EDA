#!/usr/bin/env python3
"""L45d2b3b1: le righe di L45d2a da rifare (dove = L45d2b, piu' le 9 basse delle sovratensioni) con
l'effetto misurato sul circuito di oggi, riga per riga: l'ingresso della sintesi (L45d2b3b3). Solo
stdlib, /usr/bin/python3 -I. Scrive righe_b1.csv e stampa i conteggi.

Per ogni riga: il riferimento al modo misurato, l'effetto oggi (calore, jack, Stax, o le parti
dell'alimentatore), il verdetto di oggi contro il criterio di oggi, la fonte, e la destinazione dopo
questo lotto (ADR-097 / ADR-098). Le colonne «dopo il rimedio» di ADR-070 (gravita', probabilita',
priorita') NON si calcolano qui: sono della sintesi.

I criteri di oggi: il calore a 60 C d'aria (P7 di ADR-021: Tj 125 C, resistenze 0207 0,25 W, le 22 ohm
0,34 W); la Stax col suo carico entro 150 ms (ADR-081, ADR-086, ADR-089, ADR-098); la principale e la
fissa 1 senza durata (ADR-081: il trasformatore del finale, la protezione del Singxer).
"""
import csv
import os

L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.abspath(os.path.join(L, "..", ".."))
DEC = os.path.join(DATA, "2026-10-14", "L45d2a", "decisioni.csv")

# il modo testuale di L45a -> la sigla del banco (genera_canale.MODI_PER_TIPO)
SIGLA = {"corto C-E": "ce", "corto B-E": "be", "corto D-S": "ds", "corto G-S": "gs", "corto": "cc"}


def sigla(ref, modo):
    if modo in SIGLA:
        return "%s_%s" % (ref, SIGLA[modo])
    if modo == "aperto":
        return "%s_%s" % (ref, {"Q": "ae", "J": "as"}.get(ref[0], "ap"))
    raise SystemExit("RIFIUTATO: modo %r di %s senza sigla" % (modo, ref))


def f(x, d=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


calore = {r["modo"]: r for r in csv.DictReader(open(os.path.join(L, "sintesi_calore.csv")))}
# R120 in corto: sul blocco di prima la corsa di 2,3 s non e' finita (limitations #75); si legge da
# quella corta (0,6 s) sul blocco di ADR-097 (genera_dopo097.py), se c'e'
_d = os.path.join(L, "sintesi_calore_dopo097.csv")
if os.path.exists(_d):
    for r in csv.DictReader(open(_d)):
        if r["modo"] in calore and "MANCA" in calore[r["modo"]]["stato"]:
            calore[r["modo"]] = r
for m, r in calore.items():
    if "MANCA" in r["stato"]:
        print("ATTENZIONE: %s senza corse finite" % m)
# la Stax: il peggiore su A / F2 e sui due condensatori; il blocco dopo ADR-097 dove rifatto
stax = {}
for r in csv.DictReader(open(os.path.join(L, "p10_stax.csv"))):
    if r["posizione"] in ("A", "F2"):
        stax[r["modo"]] = max(stax.get(r["modo"], 0.0), f(r["stax_sopra_ms"]))
for r in csv.DictReader(open(os.path.join(L, "stax_lunghi.csv"))):
    stax[r["modo"]] = max(f(r["dopo_ms"]), 0.0) if r["modo"] not in stax else max(stax[r["modo"]], f(r["dopo_ms"]))
rele = {r["modo"]: r for r in csv.DictReader(open(os.path.join(L, "analisi_rele.csv")))}
CALORE_LOTTO = {m for m, r in calore.items() if r["oltre_i_limiti_60C"] or r["diodi_oltre_60C"]}


def rele_ms(*casi):
    return "; ".join("%s Stax %s / princ. %s / fissa 1 %s ms" % (
        c, rele[c]["fix2_sopra_ms"], rele[c]["main_sopra_ms"], rele[c]["fix1_sopra_ms"]) for c in casi)


ALTRE = {
    "3": ("L45d2b2b1/analisi_sorgente.csv, L45d2b2b2/analisi_s074.csv",
          "24 righe su 24 col jack prima del crollo, ~32 dB SPL al jack (ADR-093)", "entro", "sintesi"),
    "4": ("L45d2b2b2/riassunto_sorgente.csv; i modi nuovi: L45d2b3b1/riassunto_nuove.csv",
          "171 righe dentro; R552 a ~0,2 s alla scelta della parte (NC-073); i corti dei 5 V a massa "
          "affidati allo spegnimento termico del regolatore (ADR-097)", "entro", "sintesi"),
    "8": ("L60c1 (un pin), L45d2b3b1/analisi_rele.csv (il filo intero)",
          "due pin per rail (ADR-083): un pin aperto <= 0,2 uV; il filo intero aperto e' un doppio guasto",
          "entro", "sintesi"),
    "9": ("L45d2b3b1/analisi_rele.csv (Cout_fix2_cc)",
          "da solo %s V alla Stax; col blocco al rail poi e' un doppio guasto accettato (ADR-082)"
          % rele["Cout_fix2_cc"]["fix2_fine_V"], "entro", "sintesi"),
    "bassa": ("L45d2b2c/rail_alto.csv, massimi_blocco.csv, p7_cbe.csv",
              "il rail fino a +20,05 / -19,97 V: 272 massimi del blocco dentro, P7 dentro coi diodi di "
              "ADR-095", "entro", "sintesi"),
}
RELE6 = {"K13–K16": ("I_K13", "I_K13_1k"), "K7, K8": ("I_K7", "I_K7_1k"),
         "K2–K4": ("I_K2_jack", "I_K4_jack", "I_K4_com"), "K3 (la Stax)": ("I_K3_jack", "I_K3_com")}


def main():
    out = []
    for r in csv.DictReader(open(DEC)):
        if not (r["dove"] == "L45d2b" or (r["scelta"] == "bassa" and r["lotto"] == "L45c1")):
            continue
        base = {"scelta": r["scelta"], "lotto": r["lotto"], "ref": r["ref"], "modo": r["modo"],
                "G_prima": r["G"], "P_prima": r["P"], "R_prima": r["R"], "adr_prima": r["adr"]}
        if r["lotto"] == "L45a":
            m = sigla(r["ref"].split(",")[0].strip(), r["modo"])
            c = calore[m]
            s = stax.get(m, 0.0)
            caldo = m in CALORE_LOTTO
            fuori_stax = s > 150.0
            # C145 in corto: coi rail ideali del banco gli 11,2 W durano per sempre; sull'alimentatore
            # vero il rail crolla e resta l'impulso (~1,3 J in ~0,25 s), che va alla parte (NC-075)
            impulso = m == "C145_cc"
            base.update({
                "caso": m,
                "effetto_oggi": "Tj max a 60 C %s C (%s)%s; principale %s V (%s dB SPL), fissa 1 %s V; "
                                "Stax %.1f ms sopra 0,87 V" % (
                                    c["Tj_max_60_C"], c["Tj_max_disp"],
                                    "; oltre: " + c["oltre_i_limiti_60C"] if c["oltre_i_limiti_60C"] else "",
                                    c["main_A_V"], c["main_dB_SPL"], c["fix1_A_V"], s),
                "verdetto_oggi": "FUORI (impulso in R144 / R152, NC-075)" if impulso else
                ("FUORI (calore)" if caldo else ("FUORI (Stax)" if fuori_stax else "entro")),
                "fonte": "L45d2b3b1/sintesi_calore.csv, p10_stax.csv, stax_lunghi.csv" +
                         (", seq/cella/ (energia_cella.py)" if impulso else ""),
                "dopo": "scelta della parte (NC-075, ADR-097)" if impulso else
                ("L45d2b3b2 (il calore, ADR-097 / ADR-098)" if caldo else "sintesi")})
        elif r["scelta"] == "6":
            casi = RELE6[r["ref"]]
            k3 = r["ref"].startswith("K3")
            base.update({"caso": "+".join(casi), "effetto_oggi": rele_ms(*casi),
                         "verdetto_oggi": "entro" if not k3 else "escluso (K3 a isolamento rinforzato, ADR-085)",
                         "fonte": "L45d2b3b1/analisi_rele.csv", "dopo": "sintesi"})
        else:
            fonte, eff, v, dopo = ALTRE[r["scelta"]]
            base.update({"caso": "", "effetto_oggi": eff, "verdetto_oggi": v, "fonte": fonte, "dopo": dopo})
        out.append(base)
    with open(os.path.join(L, "righe_b1.csv"), "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    n = len(out)
    if n != 97:
        raise SystemExit("RIFIUTATO: %d righe, attese 88 + 9 = 97" % n)
    from collections import Counter
    print("righe %d; verdetto oggi %s; dopo %s" % (n, dict(Counter(x["verdetto_oggi"] for x in out)),
                                                   dict(Counter(x["dopo"] for x in out))))


if __name__ == "__main__":
    main()
