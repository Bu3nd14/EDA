#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L64a) fatto fallire.

    /usr/bin/python3 docs/preamp/data/2026-11-02/L64a/script/sabotaggi.py

Come L51a/script/sabotaggi.py: per ogni sabotaggio una sostituzione di testo (la prima
occorrenza) in UN file versionato, il generatore lanciato, il file rimesso com'era byte per byte.
Il sabotaggio e' «caduto» se il generatore esce != 0 e la sua uscita contiene il motivo atteso.
Prima e dopo, il generatore sui file veri deve uscire 0. Con PARTI = ("audio",) il generatore
senza --standalone non scrive niente: un sabotaggio che passasse non lascerebbe tracce.
L'ultimo caso non tocca file: --standalone dentro il repo deve essere rifiutato.
Il generatore gira a priorita' bassa (l'utente: «non caricare al massimo la CPU»).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
D = "docs/preamp/data/"
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")
L64 = D + "2026-11-02/L64a/"
L66 = D + "2026-11-02/L66/"
L67 = D + "2026-11-02/L67/"

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB = [
    # 15. la seconda strada sul circuito di oggi
    ("misura_di_L66_diversa", L66 + "regressione/misure_lim365.csv",
     "tb_ac,g100k#6,-0.0043064,-0.00422237,", "tb_ac,g100k#6,-0.0043064,-0.00422238,",
     "diverse da L66"),
    ("blocco_di_L66_diverso", L66 + "varianti/lim365/gain_block.subckt",
     "R123 VPF NVS 36.5", "R123 VPF NVS 36.6", "non e' quello di oggi"),
    ("mute_di_L66_ricorso_diverso", L64 + "l66_mute/tb_mute_corto_regime.csv", "0.", "1.",
     "byte per byte"),
    ("selettore_col_blocco_di_L66_diverso", L64 + "seconda/tb_f1_selettore/f1_selettore.csv",
     "99,0,trasf,", "99,0,trasfx,", "byte per byte"),
    ("guardia_del_giorno", "docs/preamp/dossier/build_dossier.py",
     'os.path.join(L36, "corsa"): "la corsa', 'os.path.join(L36, "corsax"): "la corsa',
     "prima del circuito di oggi"),
    # 16. il mute
    ("verdetto_di_oggi_riscritto", L64 + "v2/verdetto.csv", ",0.0001,regge,", ",0.0001,NON REGGE,",
     "verdetto.csv"),
    ("esito_di_L60d2_diverso", D + "2026-10-19/L60d2/v2/verdetto.csv",
     "B2g,FIXJACK2,2.713e-06,2.165625,0.0001,regge", "B2g,FIXJACK2,2.713e-06,2.165625,0.0001,NON REGGE",
     "esiti diversi"),
    ("corsa_del_mute_non_finita", L64 + "v2/tempi.txt", " rc=0 ", " rc=1 ", "rc=0"),
    ("guardia_dei_log_che_rifiuta", L64 + "v2/guardia.txt", "guardia: esce ", "guardia: esce 9",
     "la guardia"),
    ("sonda_vosb_senza_alter", L64 + "v2/sonda_vosb/alter.txt", ":1", ":0", "alter vosb"),
    ("deck_V2_rigenerato_diverso", L64 + "mute/tb_v2_casopeggiore_generato.cir", ".end", ".end ",
     "rigenerato oggi"),
    # il volume
    ("scatti_di_oggi_riscritti", L64 + "scatti/sintesi.csv", "4,finale,3,0,0,3112,",
     "4,finale,3,0,0,3113,", "rifatto oggi"),
    ("scatti_di_L48b_lontani", D + "2026-10-07/L48b/scatti/sintesi.csv", "4,finale,3,10,0,9403,",
     "4,finale,3,10,0,9900,", "scatti contro L48b"),
    # l'interblocco
    ("falsi_del_2e_non_tutti", L64 + "falsi_l48b/verdetti.txt", "7 falsi su 7", "6 falsi su 7",
     "falsi/verdetti.txt"),
    # 18. la distorsione
    ("blocco_della_distorsione_diverso", L64 + "distorsione/inc/oggi.inc", "R123 VPF NVS 36.5",
     "R123 VPF NVS 36.6", "il blocco corso"),
    ("caldo_di_L66_riscritto", L66 + "sintesi_caldo.csv",
     "lim365--sot223--diss,t57_rame,0,2.7,0.000725,", "lim365--sot223--diss,t57_rame,0,2.7,0.000735,",
     "THD rifatte da L67"),
    ("catena_di_L67_riscritta", L67 + "verifica_livello.csv",
     "l56,l56,bout,hi,0,cima,1.5,2,0.004878,0.01,6.2,", "l56,l56,bout,hi,0,cima,1.5,2,0.004878,0.01,7.2,",
     "verifica_livello.csv"),
    ("intermodulazione_della_catena", L67 + "imd_catena.csv", ",-121.3,11.3,", ",-121.3,12.3,",
     "imd_catena.csv"),
    # le sezioni nuove
    ("limitatore_sintesi_contro_costo", D + "2026-10-25/dopo-L57b/sintesi.csv",
     "lim,1.0,5.7,4.42,25.58,-14.9,45.1,0.16,5.62,100.1,110.0,113.8 clip,+3.6,0.000764,",
     "lim,1.0,5.7,4.42,25.58,-14.9,45.1,0.16,5.62,100.1,110.0,113.8 clip,+3.6,0.000765,", "costo.csv"),
    ("calore_del_blocco_riscritto", L66 + "calore_dopo.csv",
     "dopo,A,C104_ap,si,151.7,155.8,0.298,0.299,0.019,0.142,0.142,0.026,45,q106,34,34,29,78,q106,67,",
     "dopo,A,C104_ap,si,151.7,155.8,0.298,0.299,0.019,0.142,0.142,0.026,45,q106,34,34,29,78,q106,69,",
     "non tornano dalla potenza"),
    ("stax_tempi_incoerenti", L66 + "p10_stax.csv", "114.3,114.3,114.3,FUORI", "114.3,114.3,124.3,FUORI",
     "non tornano"),
    ("tetto_di_P10_sparito", "docs/preamp/REQUIREMENTS.md", "al più **150 ms**", "al più 150 ms",
     "tetto di P10"),
    # 14. il contratto: uno stato scelto in L64a
    ("stato_di_ADR-099_diverso", "docs/preamp/decisions/README.md",
     "accettata — il limitatore del VAS passa a 36,5 + 18,7 Ω (ADR-111); il resto vale",
     "accettata — il limitatore del VAS passa a 36,5 Ω (ADR-111); il resto vale", "ADR-099"),
]


def build(args=()):
    p = subprocess.run(["nice", "-n", "10", sys.executable, BUILD, *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    rc, out = build()
    if rc != 0:
        print("il generatore sui file veri non esce 0: niente da sabotare\n" + out[-2000:])
        return 1
    bad, righe = 0, []
    for nome, rel_, old, new, atteso in SAB:
        path = os.path.join(REPO, rel_)
        with open(path, "rb") as f:
            orig = f.read()
        txt = orig.decode("utf-8")
        if old not in txt:
            righe.append(f"MANCA  {nome}: il testo da sabotare non c'e' in {rel_}")
            bad += 1
            continue
        try:
            with open(path, "wb") as f:
                f.write(txt.replace(old, new, 1).encode("utf-8"))
            rc, out = build()
        finally:
            with open(path, "wb") as f:
                f.write(orig)
        caduto = rc != 0 and atteso in out
        bad += not caduto
        righe.append(f"{'CADE   ' if caduto else 'PASSA! '} {nome}: rc={rc}")
    prova = os.path.join(REPO, "docs", "preamp", "dossier", "prova.html")
    rc, out = build(["--standalone", prova])
    caduto = rc != 0 and "sta dentro il repository" in out
    bad += not caduto
    righe.append(f"{'CADE   ' if caduto else 'PASSA! '} pagina_a_meta_nel_repo: rc={rc}")
    if os.path.exists(prova):
        os.remove(prova)
    rc, out = build()
    righe.append(f"generatore sui file veri dopo i sabotaggi: rc={rc}")
    bad += rc != 0
    n = len(SAB) + 1
    righe.append(f"{n - bad + (rc != 0)} sabotaggi su {n} cadono come devono")
    with open(os.path.join(HERE, "..", "sabotaggi.txt"), "w") as f:
        f.write("\n".join(righe) + "\n")
    print("\n".join(righe))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
