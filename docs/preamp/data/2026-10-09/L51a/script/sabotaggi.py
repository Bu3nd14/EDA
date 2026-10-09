#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L51a) fatto fallire.

    /usr/bin/python3 docs/preamp/data/2026-10-09/L51a/script/sabotaggi.py

Come L42/script/sabotaggi.py: per ogni sabotaggio una sostituzione di testo in UN
file versionato, il generatore lanciato, il file rimesso com'era byte per byte. Il
sabotaggio e' "caduto" se il generatore esce != 0 e la sua uscita contiene il motivo
atteso. Prima e dopo, il generatore sui file veri deve uscire 0. In L51a il
generatore senza --standalone non scrive niente (PARTI incomplete): un sabotaggio
che passasse non lascerebbe tracce.

Un sabotaggio che non cade vuol dire un controllo che non controlla: esce 1.
L'ultimo caso non tocca file: --standalone dentro il repo con le parti incomplete
deve essere rifiutato.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
D = "docs/preamp/data/"
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")
L51 = D + "2026-10-09/L51a/"
L48B = D + "2026-10-07/L48b/"
L48A = D + "2026-10-06/L48a/"

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB = [
    # 15. la seconda strada
    ("log_di_L48b_diverso", L48B + "regressione/dopo/tb_ac/tb_ac.log",
     "g1k = -7.14497e-03", "g1k = -7.14498e-03", "differiscono fino a"),
    ("tabella_di_L48b_diversa", L48B + "regressione/dopo/tb_loop/tb_loop_margini.csv",
     "0db,1m,1,1f,865284,74.2686,", "0db,1m,1,1f,865284,74.2687,", "byte per byte"),
    ("selettore_di_L48a_diverso", L48A + "misure/tb_f1_selettore/f1_selettore.csv",
     "99,0,trasf,9.23513,", "99,0,trasf,9.23514,", "byte per byte"),
    ("bilanciamento_di_L48b_diverso", L48B + "e5_bilanciamento/out/tb_e3_e5_e5.csv",
     "0,0db,max,1.5,1.87291", "0,0db,max,1.5,1.87292", "byte per byte"),
    ("guardia_del_giorno", "docs/preamp/dossier/build_dossier.py",
     'os.path.join(L36, "corsa"): "la corsa', 'os.path.join(L36, "corsax"): "la corsa',
     "prima del circuito di oggi"),
    # 16. il mute
    ("verdetto_L48b_riscritto", L48B + "v2/matrice/verdetto.csv",
     "A_ins,FIXJACK2,2.795e-11,", "A_ins,FIXJACK2,2.795e-12,", "verdetto.csv"),
    ("soglia_nel_verdetto", L48B + "v2/matrice/verdetto.csv",
     "B2g,FIXJACK1,5.398e-06,1.160781,0.0001,regge", "B2g,FIXJACK1,5.398e-06,1.160781,0.001,regge",
     "verdetto.csv"),
    ("esito_nel_verdetto", L48B + "v2/matrice/verdetto.csv",
     "B2g,FIXJACK1,5.398e-06,1.160781,0.0001,regge", "B2g,FIXJACK1,5.398e-06,1.160781,0.0001,NON REGGE",
     "verdetto.csv"),
    ("manifesto_finale_senza_una_cella", L48B + "v2/matrice/manifest_finale.csv",
     "vol_g10_iii,vol_g10_iii.dat,", "vol_g10_iiix,vol_g10_iii.dat,", "manifest_finale.csv"),
    ("analisi_del_mute_di_oggi", L51 + "mute/corse/analisi.csv",
     ",A_ins,MAINJACK,", ",A_ins,MAINJACKX,", "diverse da L48b"),
    ("corsa_del_mute_non_finita", L51 + "mute/corse/tempi.txt",
     "vol_g10_iii rc=0", "vol_g10_iii rc=1", "rc=0"),
    ("deck_V2_rigenerato_diverso", L51 + "mute/tb_v2_casopeggiore_generato.cir",
     ".end", ".end ", "rigenerato oggi"),
    ("clic_C2_riscritto", L48B + "v2/matrice/clic.csv",
     "principale,1 kHz,rilascio,100k,11.48,", "principale,1 kHz,rilascio,100k,11.58,", "clic.csv"),
    ("clic_dB_SPL_riscritto", L48B + "v2/matrice/clic.csv",
     "rilascio,100k,11.48,134.6,", "rilascio,100k,11.48,135.6,", "catena di NC-028"),
    ("sonda_vosb_senza_un_uscita", L48B + "v2/sonda_vosb/analisi.csv",
     "A_ins,FIXJACK1,1.594e-11", "A_ins,FIXJACK2,1.594e-11", "sonda_vosb"),
    # 17. il selettore e il volume
    ("tabella_del_selettore", L51 + "dopo/tb_f1_selettore/f1_selettore.csv",
     "10,0.1,trasf,6.28357,6.6269E-06,19.8176,", "10,0.1,trasf,6.28357,6.6269E-06,19.9176,",
     "f1_selettore.csv"),
    ("sintesi_degli_scatti", L48B + "scatti/sintesi.csv",
     "4,finale,1,10,0,0.04774,0.04832,", "4,finale,1,10,0,0.04774,0.04932,", "rifatto oggi"),
    ("corsa_degli_scatti", L48B + "scatti/deck/scatti_v4.csv",
     "4,finale,-6.6,0,1,0,-6.60002,-2.78417E-05,0.015235", "4,finale,-6.6,0,1,0,-6.60002,-2.78417E-05,0.025235",
     "rifatto oggi"),
    ("e5_col_bilanciamento", L51 + "dopo/bilanciamento/tb_e5_bilanciamento/tb_e3_e5_e5.csv",
     "0,0db,max,1.5,1.87291", "0,0db,max,1.5,1.87391", "tb_e5_bilanciamento"),
    ("v1_col_bilanciamento", L51 + "dopo/bilanciamento/tb_loop_bilanciamento/tb_loop_margini.csv",
     "0db,2.611k,1,1f,865007,73.5629,", "0db,2.611k,1,1f,865007,73.5639,", "tb_loop_margini.csv"),
    ("e3_del_deck_canonico", L51 + "dopo/tb_e3_e5/tb_e3_e5_e3.csv",
     "0,1f,309822,", "0,1f,309823,", "tb_e3_e5_e3.csv"),
    ("continua_del_blocco_sparita", L51 + "dopo/tb_op/tb_op.log",
     "v(out) = -6.62320e-03", "v(oux) = -6.62320e-03", "attesa una v(out)"),
    ("rele_del_selettore_sparito", "circuits/preamp/preamp_audio.net",
     '(value "G6K-2F-Y SEL1")', '(value "G6K-2F-Y SELX")', "check_relay_safe_state"),
    ("falsi_L48b_che_non_cadono", L48B + "falsi/verdetti.txt",
     "8 falsi su 8 cadono dove devono", "7 falsi su 8 cadono dove devono", "L48b falsi"),
    ("falsi_L48a_che_non_cadono", L48A + "falsi/verdetti.txt",
     "10 falsi su 10 cadono per il motivo giusto", "9 falsi su 10 cadono per il motivo giusto",
     "L48a falsi"),
    # 14. il contratto: la ADR nuova
    ("stato_di_ADR066_diverso_dall_indice",
     "docs/preamp/decisions/ADR-066-pr14-dettagli-selettore-progettato.md",
     "Data: 2026-10-09 · Stato: accettata", "Data: 2026-10-09 · Stato: accettata ma", "ADR-066"),
]


def build(args=()):
    p = subprocess.run([sys.executable, BUILD, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    rc, out = build()
    if rc != 0:
        print("il generatore non passa sui file veri:\n" + out)
        return 1
    bad = 0
    righe = []
    for nome, rel, old, new, atteso in SAB:
        path = os.path.join(REPO, rel)
        with open(path, "rb") as f:
            orig = f.read()
        txt = orig.decode("utf-8", errors="surrogateescape")
        if txt.count(old) < 1:
            righe.append(f"NON APPLICABILE {nome}: «{old}» non c'e' in {rel}")
            bad += 1
            continue
        with open(path, "wb") as f:
            f.write(txt.replace(old, new, 1).encode("utf-8", errors="surrogateescape"))
        try:
            rc, out = build()
        finally:
            with open(path, "wb") as f:
                f.write(orig)
        caduto = rc != 0 and atteso in out
        if not caduto:
            bad += 1
        motivo = next((ln.strip() for ln in out.splitlines() if atteso in ln), out.strip()[-120:])
        righe.append(f"{'CADE   ' if caduto else 'PASSA! '} {nome}: rc={rc} | {motivo[:150]}")
    # l'ultimo: la pagina a meta' dentro il repo
    rc, out = build(["--standalone", os.path.join(REPO, "docs", "preamp", "dossier", "prova.html")])
    caduto = rc != 0 and "sta dentro il repository" in out
    if not caduto:
        bad += 1
    righe.append(f"{'CADE   ' if caduto else 'PASSA! '} pagina_a_meta_nel_repo: rc={rc}")
    if os.path.exists(os.path.join(REPO, "docs", "preamp", "dossier", "prova.html")):
        righe.append("ERRORE: prova.html e' stato scritto nel repo")
        bad += 1
    rc, out = build()
    righe.append(f"generatore sui file veri dopo i sabotaggi: rc={rc}")
    if rc != 0:
        bad += 1
    n = len(SAB) + 1
    righe.append(f"{n - bad} sabotaggi su {n} cadono come devono")
    with open(os.path.join(HERE, "..", "sabotaggi.txt"), "w") as f:
        f.write("\n".join(righe) + "\n")
    print("\n".join(righe))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
