#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L42a) fatto fallire.

    /usr/bin/python3 docs/preamp/data/2026-09-27/L42/script/sabotaggi.py

Per ogni sabotaggio: una sostituzione di testo in UN file versionato, il
generatore lanciato, il file rimesso com'era byte per byte. Il sabotaggio e'
"caduto" se il generatore esce != 0 e la sua uscita contiene il motivo atteso.
Prima e dopo, il generatore sui file veri deve uscire 0.

Un sabotaggio che non cade vuol dire un controllo che non controlla: esce 1.
Il generatore, quando rifiuta, non scrive niente; se un sabotaggio passasse
riscriverebbe la pagina, e la corsa finale sui file veri la riscrive giusta.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
D = "docs/preamp/data/"
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB = [
    ("log_di_oggi_diverso_da_L40", D + "2026-09-27/L42/dopo/tb_ac/tb_ac.log",
     "g1k = -7.00112e-03", "g1k = -7.00113e-03", "oggi e L40 differiscono"),
    ("tabella_di_L40_diversa", D + "2026-09-23/L40/dopo/tb_loop/tb_loop_margini.csv",
     "0db,1m,1,1f,429795,69.2568", "0db,1m,1,1f,429795,69.2569", "byte per byte"),
    ("verdetto_L29d2_riscritto", D + "2026-09-25/L29d2/matrice/verdetto.csv",
     "gm0x3_1k_iii_i,1,l29d2_iii,0a3,1000,3.818,100k,S_ins,MAINJACK,7.163",
     "gm0x3_1k_iii_i,1,l29d2_iii,0a3,1000,3.818,100k,S_ins,MAINJACK,7.100", "verdetto.csv"),
    ("soglia_di_S_nel_verdetto", D + "2026-09-25/L29d2/matrice/verdetto.csv",
     "S_ins,MAINJACK,7.163,6.040000,20.0,", "S_ins,MAINJACK,7.163,6.040000,30.0,", "soglia"),
    ("tabella_del_sorgente_L29e", D + "2026-09-25/L29e/tabella_sorgente.csv",
     "gm0x10_lz_iii_c,A_ins,MAINJACK,1.704e-07", "gm0x10_lz_iii_c,A_ins,MAINJACK,1.604e-07",
     "tabella_sorgente.csv"),
    ("analisi_del_mute_di_oggi", D + "2026-09-27/L42/mute/analisi.csv",
     "S_ins,MAINJACK,7.163,", "S_ins,MAINJACK,7.263,", "diverse da L29e"),
    ("curva_del_livello", D + "2026-09-27/L42/mute/profilo.csv",
     "6.003000,-43.360889", "6.003000,-13.360889", "dalla curva del livello"),
    ("corsa_L36_ricontata", D + "2026-09-25/L36/corsa/corsa.csv",
     "progetto,5.0,0.1,213.0,0.1,4.75,2.347417840375587,22.2587,22.2587,22.2587,22.2587,22.2587,True",
     "progetto,5.0,0.1,213.0,0.1,4.75,2.347417840375587,22.2587,22.2587,22.2587,22.2587,22.2587,False",
     "sintesi.txt"),
    ("falso_L35_che_passa", D + "2026-09-25/L35/falsi/esito.csv",
     "main_prima_di_L35,1,1,ok", "main_prima_di_L35,1,0,ok", "L35 falsi"),
    ("stima_termica_ritoccata", D + "2026-09-26/L30/termica/stima_telaio.txt",
     "TOTALE                                15.39", "TOTALE                                14.39",
     "stima_telaio"),
    ("rail_di_tb_op", D + "2026-09-27/L42/dopo/tb_op/tb_op.log",
     "i(vpp) = -3.25947e-02", "i(vpp) = -3.35947e-02", "calore"),
    ("e3_con_le_ldr", D + "2026-09-26/L41b2/e3_e5/tb_e3_e5_ldr_cima12mA_e3.csv",
     "gioco,0,22p,113.485,4.00037E+08,277605,", "gioco,0,22p,113.485,4.00037E+08,277705,",
     "tb_e3_e5_ldr_cima12mA_e3.csv"),
    ("cima_dei_led_a_12_mA_nel_deck", "spice/preamp/tb/tb_v2_casopeggiore.cir",
     "pwl(V(DEP), 0,-1.6990,", "pwl(V(DEP), 0,-1.9208,", "cima"),
    ("print_spezzata_non_ricucibile", D + "2026-09-27/L42/dopo/tb_e4_uscite/tb_e4_uscite.log",
     "Note: Source stepping completed\n.720894e-01", "Note: Source stepping completed\nx.720894e-01",
     "non si ricuce"),
    ("ausiliario_del_guadagno_sparito", "circuits/preamp/preamp_audio.net",
     '(value "G6K-2F-Y HOLD3")', '(value "G6K-2F-Y HOLDX")', "check_relay_safe_state"),
]


def build():
    p = subprocess.run([sys.executable, BUILD], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main():
    rc, out = build()
    if rc != 0:
        print("il generatore non passa sui file veri:\n" + out)
        return 1
    bad = 0
    for nome, rel, old, new, atteso in SAB:
        path = os.path.join(REPO, rel)
        with open(path, "rb") as f:
            orig = f.read()
        txt = orig.decode("utf-8")
        if txt.count(old) < 1:
            print(f"{nome:36s} NON APPLICABILE: il testo da sabotare non c'e'")
            bad += 1
            continue
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt.replace(old, new, 1))
            rc, out = build()
        finally:
            with open(path, "wb") as f:
                f.write(orig)
        ok = rc != 0 and atteso in out
        bad += not ok
        riga = next((ln.strip() for ln in out.splitlines() if atteso in ln), out.strip()[-120:])
        print(f"{nome:36s} {'caduto' if ok else 'NON CADUTO'}  rc={rc}  {riga[:150]}")
    rc, out = build()
    print(f"\ndi nuovo sui file veri: rc={rc}")
    print(f"{len(SAB) - bad} sabotaggi su {len(SAB)} caduti")
    return 1 if bad or rc else 0


if __name__ == "__main__":
    sys.exit(main())
