#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L64b, l'alimentatore) fatto fallire.

    /usr/bin/python3 docs/preamp/data/2026-11-03/L64b/script/sabotaggi.py

Come L64a/script/sabotaggi.py: per ogni sabotaggio una sostituzione di testo (la prima occorrenza)
in UN file versionato, il generatore lanciato, il file rimesso com'era byte per byte. Il sabotaggio
e' «caduto» se il generatore esce != 0 e la sua uscita contiene il motivo atteso. Prima e dopo, il
generatore sui file veri deve uscire 0. Con PARTI = ("audio", "alimentatore") il generatore senza
--standalone non scrive niente. Il generatore gira a priorita' bassa (l'utente: «non caricare troppo
la CPU»). Gli scarti contro L51b, L54b2 e L54b3b (le tabelle «cosa è cambiato») si pubblicano e non
rifiutano: lì non c'e' niente da sabotare.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
D = "docs/preamp/data/"
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")
L = D + "2026-11-03/L64b/"
L58 = D + "2026-11-01/L58b/"

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB = [
    # 8. la potenza: i banchi della rete e dei guasti
    ("R512_a_220k_nel_log", L + "rete/tb_psu_rete.log", "@rr512[resistance] = 1.100000000000000e+05",
     "@rr512[resistance] = 2.200000000000000e+05", "(#34)"),
    ("deck_della_rete_diverso", L + "rete/tb_psu_rete.cir", "RR550 raw_p raw_pr 4.7",
     "RR550 raw_p raw_pr 4.8", "il circuito corso non e' quello di oggi"),
    ("caso_della_rete_rinominato", L + "rete/analisi.csv", "perdita_rete_nom,", "perdita_rete_nomx,",
     "analisi.csv: casi"),
    ("analisi_senza_3_secondi", L + "rete/analisi.csv", "perdita_rete_nom,,,,,,,,14.402,",
     "perdita_rete_nom,,,,,,,,1014.402,", "analizza.py senza 3.0"),
    ("giorno_di_oggi_spostato", "docs/preamp/dossier/build_dossier.py", 'PSU_DA = "2026-11-03"',
     'PSU_DA = "2026-11-04"', "non e' del 2026-11-04"),
    # il calore
    ("rail_della_rete_contro_il_calore", L + "rete/analisi.csv", "regime_nom,14.9854,",
     "regime_nom,14.9954,", "dai rail del banco della rete"),
    ("potenza_del_calore_riscritta", L + "termica/tb_calore.log", "CALORE regime_nom pt1=13.934 ",
     "CALORE regime_nom pt1=13.984 ", "il bilancio dei secondari"),
    ("stima_del_telaio_riscritta", L + "termica/stima_telaio_l64b.txt",
     "TOTALE                                17.68", "TOTALE                                17.78",
     "non ridà stima_telaio_l64b.txt"),
    ("carico_non_quello_di_tb_op", L + "carico.txt", "i_piu_mA   303.3288", "i_piu_mA   303.4288",
     "carico.txt di L64b"),
    # 9-11. le sequenze
    ("deck_di_una_sequenza_diverso", L + "seq/oggi/accensione/tb_psu_seq_accensione_g1.cir",
     "RR550 raw_p raw_pr 4.7", "RR550 raw_p raw_pr 4.8", "sequenza oggi/accensione"),
    ("log_di_una_sequenza_sporco", L + "seq/oggi/accensione/tb_psu_seq_accensione_g1.log",
     "Note: No compatibility mode selected!", "Error: timestep too small", "invalidano la corsa"),
    ("riga_di_oggi_riscritta", L + "an_l64b.csv", "oggi/perdita,1,1,1,1,1,17.4,",
     "oggi/perdita,1,1,1,1,1,17.9,", "confronta.py"),
    ("confronto_versionato_riscritto", L + "confronto_seq.csv",
     "v_sorgente/spegnimento_l,L54b3b,t_v106_ms,418.6,418.5,", "v_sorgente/spegnimento_l,L54b3b,t_v106_ms,418.7,418.5,",
     "confronta.py rieseguito"),
    ("riga_di_L58b_riscritta", L58 + "an_l58b.csv", "l58b_base/accensione,0,1,1,0,0,3.0,0.0,0.0,0.0,1209.3,",
     "l58b_base/accensione,0,1,1,0,0,3.0,0.0,0.0,0.0,1219.3,", "confronta.py"),
    ("soglia_del_permissivo_sparita", "docs/preamp/decisions/ADR-105-tolleranze-e-temperatura-del-temporizzatore.md",
     "il permissivo dopo il mute (≥ 16,9 ms)", "il permissivo dopo il mute (16,9 ms)", "la soglia perm"),
    # l'autodiagnosi e lo standby
    ("censimento_riscritto", L + "censimento_psu.csv", "oggi/f_q505_corto_accs,2.50-3.00,11.9911,",
     "oggi/f_q505_corto_accs,2.50-3.00,11.9811,", "censimento, f_q505_corto_accs"),
    ("standby_illeggibile", L + "consumo.txt", "2.500-3.000 s: T2 129.74 mW", "2.500-3.000 s: T2 = 129.74 mW",
     "consumo.txt: la riga"),
    ("standby_senza_sonda", L + "seq/consumo/accensione/ok.txt", "--sonda-t2", "--sonda-tx", "non ha --sonda-t2"),
    # 13. la catena al jack
    ("tabella_della_catena_riscritta", L + "tabella_nom.csv", "spegnimento_l,MAINJACK,3.542e-09,-55.6,",
     "spegnimento_l,MAINJACK,3.542e-09,-45.6,", "tabella.py rieseguito"),
    ("corsa_della_catena_non_finita", L + "corse/nom/tempi.txt", "rif_spegnimento_l_l41c rc=0 ",
     "rif_spegnimento_l_l41c rc=1 ", "non tutte rc=0"),
    ("deck_di_V2_della_catena_diverso", L + "deck/tb_v2_l41c_nom.cir", "RSRC SRC SELA 1.5",
     "RSRC SRC SELA 1.6", "il deck di V2 rigenerato oggi"),
]


def build(args=()):
    p = subprocess.run(["nice", "-n", "15", sys.executable, BUILD, *args],
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
        righe.append(f"{'CADE   ' if caduto else 'PASSA! '} {nome}: rc={rc}"
                     + ("" if caduto else f" ({out.strip()[-200:]!r})"))
    rc, out = build()
    righe.append(f"generatore sui file veri dopo i sabotaggi: rc={rc}")
    bad += rc != 0
    n = len(SAB)
    righe.append(f"{n - bad + (rc != 0)} sabotaggi su {n} cadono come devono")
    with open(os.path.join(HERE, "..", "sabotaggi.txt"), "w") as f:
        f.write("\n".join(righe) + "\n")
    print("\n".join(righe))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
