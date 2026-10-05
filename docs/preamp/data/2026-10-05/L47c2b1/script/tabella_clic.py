#!/usr/bin/env python3
"""L47c2b1: la tabella del clic del taglio (ADR-062: misurato e dichiarato, senza soglia).

Scelta dell'utente all'inizio del lotto: «Tabella intera» - le tre uscite x 20 Hz / 1 kHz /
20 kHz x inserimento / rilascio, 18 valori, in picco e in dB SPL a 1 m, il peggiore in cima.

Per ogni cella: C2 di v2_metodo (analisi.csv della matrice), il peggiore fra i due carichi di V2
(100 k e 10 k, il carico detto), sulle corse del mute tenuto 1 s (0,5 s a 20 kHz): mev_<tono>_iii
(100 k, gruppo 4 e clic()) e mev_<tono>_r10k_iii (10 k, clic()).

ACCANTO, IL TAGLIO IDEALE (CALCOLATO). Su un taglio netto C2 conta il taglio stesso: il fit di un
tono a ampiezza costante su 10 ms non regge dove la musica sparisce (v2_metodo, T11). Il numero da
solo non separa «la musica che si ferma» dal clic del contatto. Il taglio ideale e' costruito con
le forme d'onda del circuito: il riferimento «mai in mute» fino all'istante del contatto, poi il
riferimento «sempre in mute» (al rilascio il contrario), letto con lo stesso C2 e lo stesso
riferimento di analizza. Stessa ampiezza, fase e continua del jack vero, commutazione in zero
tempo. La differenza fra le due colonne e' quello che il circuito aggiunge (o toglie) al taglio.
Istanti del contatto (genera_tb_v2_casopeggiore.py, geometria iii): all'inserimento il contatto
in serie si apre al tasto + T_ATT; al rilascio si chiude al tasto + T_ATT + TT.

dB SPL di picco a 1 m con la formula di NC-028: 100 uV = 33,45 dB, poi 20 log10 del rapporto
(un limite superiore, come data/2026-09-26/L41c/script/tabella.py). La stessa formula sulle tre
uscite, dichiarata: e' quella della principale verso il finale e i diffusori.

Uso: tabella_clic.py manifest.csv DATADIR analisi.csv OUT.csv
"""
import csv
import math
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import v2_metodo as vm  # noqa: E402

T_ATT = 0.024   # tasto -> contatto in serie: MUTE_CMD 21 ms (L47c2a) + 3 ms del G6K
TT = 1e-3       # il trasferimento fra i contatti della geometria iii
DB0, V0 = 33.45, 100e-6
NOMI = {"MAINJACK": "principale", "FIXJACK1": "fissa 1", "FIXJACK2": "fissa 2"}
TONI = {"20": "20 Hz", "1000": "1 kHz", "20000": "20 kHz"}


def db_spl(v):
    return DB0 + 20 * math.log10(v / V0)


def celle_clic(M):
    out = []
    for c, r in M.items():
        if r["tipo"] != "evento" or "C2_ins" not in r.get("conta", ""):
            continue
        if not c.startswith("mev_") or c.startswith("mev_lz"):
            continue
        out.append(r)
    return out


def main():
    man, datadir, ana, outp = sys.argv[1:5]
    with open(man) as f:
        M = {r["cella"]: r for r in csv.DictReader(f)}
    with open(ana) as f:
        AN = {(a["cella"], a["grandezza"], a["uscita"]): a for a in csv.DictReader(f)}
    righe = {}
    for r in celle_clic(M):
        f = float(r["f_hz"])
        tmax, t_fine = float(r["tmax"]), float(r["t_fine"])
        t_ins, t_rel, tg = float(r["t_ins"]), float(r["t_rel"]), float(r["t_grad"])
        rif_s, rif_m = M[r["rif_ins"]], M[r["rif_rel"]]
        xs, _ = vm.leggi_wrdata(os.path.join(datadir, rif_s["file"]), tmax / 5, t_fine)
        xm, _ = vm.leggi_wrdata(os.path.join(datadir, rif_m["file"]), tmax / 5, t_fine)
        for k, u in enumerate(vm.USCITE):
            s, m = xs[k], xm[k]
            n = min(len(s), len(m))
            for ev, te, tc, prima, dopo, rif in (
                    ("inserimento", t_ins, t_ins + T_ATT, m, s, s),
                    ("rilascio", t_rel, t_rel + T_ATT + TT, s, m, m)):
                ic = int(round(tc * vm.FS))
                ideale = prima[:ic] + dopo[ic:n]
                (vi, _), = vm.c2_picchi(ideale, rif[:n], f, [te], tg)[0]
                g = "C2_ins" if ev == "inserimento" else "C2_rel"
                a = AN.get((r["cella"], g, u))
                if a is None or not a["picco_V"]:
                    raise SystemExit("manca %s %s %s in %s" % (r["cella"], g, u, ana))
                v = float(a["picco_V"])
                fase = math.degrees((math.pi / 2 + 2 * math.pi * f * tc) % (2 * math.pi))
                chiave = (u, r["f_hz"], ev)
                # ADR-063: con la musica la coda del filtro dopo il taglio (B2) va col clic, e il
                # jack grezzo nel mute (B2g) e' il verdetto; si leggono sulla riga d'inserimento
                coda = grezzo = ""
                if ev == "inserimento":
                    b2 = AN.get((r["cella"], "B2", u))
                    b2g = AN.get((r["cella"], "B2g", u))
                    coda = b2["picco_V"] if b2 else ""
                    grezzo = b2g["picco_V"] if b2g else ""
                riga = dict(uscita=NOMI[u], tono=TONI[r["f_hz"]], evento=ev, carico=r["rl"],
                            cella=r["cella"], c2_V=v, ideale_V=vi, fase=fase,
                            t_picco=a["t_picco_s"], coda=coda, grezzo=grezzo)
                righe.setdefault(chiave, []).append(riga)
    if len(righe) != 18:
        raise SystemExit("attese 18 celle (3 uscite x 3 toni x 2 eventi), trovate %d" % len(righe))
    tab = []
    for chiave, rr in righe.items():
        if len(rr) != 2:
            raise SystemExit("%s: attesi i due carichi, trovati %s" % (chiave, [x["carico"] for x in rr]))
        w = max(rr, key=lambda x: x["c2_V"])
        altro = [x for x in rr if x is not w][0]
        tab.append(dict(w, altro_carico=altro["carico"], altro_V=altro["c2_V"],
                        altro_ideale_V=altro["ideale_V"]))
    tab.sort(key=lambda x: -x["c2_V"])
    campi = ["uscita", "tono", "evento", "carico", "c2_V", "dB_SPL_1m", "ideale_V",
             "dB_SPL_ideale", "circuito_meno_ideale_dB", "fase_sorgente_gradi", "t_picco_s",
             "altro_carico", "altro_c2_V", "altro_ideale_V", "coda_filtro_B2_V",
             "jack_grezzo_B2g_V", "cella"]
    with open(outp, "w", newline="") as fo:
        wr = csv.writer(fo)
        wr.writerow(campi)
        for x in tab:
            wr.writerow([x["uscita"], x["tono"], x["evento"], x["carico"], "%.4g" % x["c2_V"],
                         "%.1f" % db_spl(x["c2_V"]), "%.4g" % x["ideale_V"],
                         "%.1f" % db_spl(x["ideale_V"]),
                         "%.2f" % (20 * math.log10(x["c2_V"] / x["ideale_V"])),
                         "%.0f" % x["fase"], x["t_picco"], x["altro_carico"],
                         "%.4g" % x["altro_V"], "%.4g" % x["altro_ideale_V"], x["coda"],
                         x["grezzo"], x["cella"]])
    print("# il clic del taglio - SIMULATO (C2) e CALCOLATO (taglio ideale); dB SPL di picco a 1 m,"
          " formula di NC-028 (limite superiore)")
    print("%-10s %-6s %-11s %-5s %10s %7s %10s %7s %7s %5s" % (
        "uscita", "tono", "evento", "rl", "C2 V", "dB SPL", "ideale V", "dB SPL", "c-i dB", "fase"))
    for x in tab:
        print("%-10s %-6s %-11s %-5s %10.4g %7.1f %10.4g %7.1f %7.2f %5.0f" % (
            x["uscita"], x["tono"], x["evento"], x["carico"], x["c2_V"], db_spl(x["c2_V"]),
            x["ideale_V"], db_spl(x["ideale_V"]), 20 * math.log10(x["c2_V"] / x["ideale_V"]),
            x["fase"]))
    print("%d righe -> %s" % (len(tab), outp))


if __name__ == "__main__":
    main()
