#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L51b, l'alimentatore) fatto fallire.

    /usr/bin/python3 docs/preamp/data/2026-10-09/L51b/script/sabotaggi.py

Come L51a/script/sabotaggi.py: per ogni sabotaggio una sostituzione di testo in UN file
versionato (o tenuto accanto ai dati), il generatore lanciato, il file rimesso com'era byte per
byte. Il sabotaggio e' "caduto" se il generatore esce != 0 e la sua uscita contiene il motivo
atteso. Prima e dopo, il generatore sui file veri deve uscire 0. Senza --standalone e con le
parti incomplete il generatore non scrive niente: un sabotaggio che passasse non lascerebbe
tracce.

Un sabotaggio che non cade vuol dire un controllo che non controlla: esce 1. L'ultimo caso non
tocca file: --standalone dentro il repo con le parti incomplete deve essere rifiutato.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
BUILD = os.path.join(REPO, "docs", "preamp", "dossier", "build_dossier.py")
G = "docs/preamp/dossier/build_dossier.py"
O = "docs/preamp/data/2026-10-09/L51b/"
P = "docs/preamp/data/2026-10-09/L51b-prima/"

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB = [
    # la guardia del giorno: un lotto di prima come prima strada
    ("prima_strada_vecchia", G, 'L51B = os.path.join(DATAROOT, "2026-10-09", "L51b")',
     'L51B = os.path.join(DATAROOT, "2026-10-06", "L47c2b2")', "non e' del 2026-10-09"),
    # il carico
    ("carico_rail_non_tb_op", O + "carico.txt", "i_piu_mA   293.62", "i_piu_mA   293.72",
     "carico.txt di L51b: i_piu_mA"),
    ("carico_prima_non_l47c2a", P + "carico.txt", "resto_mA   42.4", "resto_mA   42.5",
     "L51b-prima/carico.txt non e' il carico di L47c2a"),
    ("metodo_u503", O + "carico.txt", "metodo_u503 gear", "metodo_u503 trap", "metodo trap"),
    # i banchi rete e guasti
    ("log_rete_errore", O + "rete/tb_psu_rete.log", "CASO regime_nom", "Error: sabotaggio\nCASO regime_nom",
     "il log ha"),
    ("r512_nel_log", O + "rete/tb_psu_rete.log", "@rr512[resistance] = 2.200000000000000e+05",
     "@rr512[resistance] = 2.200000000000000e+06", "(#34)"),
    ("deck_rete_oggi", O + "rete/tb_psu_rete.cir", "RRESTO vrelay rly_ret 233.01",
     "RRESTO vrelay rly_ret 233.02", "deck rete oggi"),
    ("rete_prima_non_l47c2a", P + "rete/analisi.csv", "61.097", "61.098", "rete prima contro L47c2a"),
    # le sequenze
    ("verdetto_seq_oggi", O + "seq/analisi_seq.txt", "VERDETTO: PASSA", "VERDETTO: FALLISCE",
     "L51b analisi_seq.txt: verdetto"),
    ("deck_seq_al_punto_fisso", O + "seq/perdita/tb_psu_seq_perdita_g3.cir", "RLOADP vplus 0 51.0864",
     "RLOADP vplus 0 51.0865", "sequenza perdita al giro 3"),
    ("log_seq_errore", O + "seq/guasto_u503/tb_psu_seq_guasto_u503_g2.log", "Circuit:",
     "Timestep too small\nCircuit:", "tb_psu_seq_guasto_u503_g2.log"),
    ("seq_prima_criterio", P + "seq/analisi_seq.txt", "MUTE_CMD rilasciato 10.10 ms",
     "MUTE_CMD rilasciato 10.20 ms", "L47c2b2, guasto_u501: il testo"),
    ("seq_prima_fatto", P + "seq/analisi_seq.txt", "   . t_mains: 0.021000", "   . t_mains: 0.021100",
     "L47c2a, accensione: il testo"),
    ("core_prima", P + "seq/rilascio/core_g2.csv", "2.021000,1,1,1,1,RILASCIO",
     "2.021100,1,1,1,1,RILASCIO", "rilascio: core_g2.csv"),
    ("ponte_prima", P + "ponte/perdita.json", '"giro": 2', '"giro": 3', "ponte perdita contro L47c2b2"),
    # il temporizzatore
    ("timer_prima_non_l47c2a", P + "timer/analisi_timer.txt", "potenza da T2 80.5 mW",
     "potenza da T2 80.6 mW", "contro L47c2a"),
    ("timer_oggi_non_rieseguito", O + "timer/analisi_timer.txt", "VRELAY < 9,6 V 35.87 ms",
     "VRELAY < 9,6 V 35.88 ms", "non ridà analisi_timer.txt"),
    ("log_timer_errore", O + "timer/tb_psu_timer_nom.log", "CASO micro_a_zero",
     "singular matrix\nCASO micro_a_zero", "tb_psu_timer_nom.log"),
    # il firmware
    ("falsi_host", O + "falsi/esito.txt", "== falsi: 19 su 19", "== falsi: 18 su 19",
     "falsi sull'host contro L47c2b2"),
    # i guasti al jack
    ("tabella_oggi", O + "tabella.csv", "0.0008149", "0.0008150", "oggi: tabella.py rieseguito"),
    ("corsa_fallita", O + "corse/tempi.txt", "rif_perdita_l41c rc=0", "rif_perdita_l41c rc=1",
     "non tutte rc=0"),
    ("deck_v2_oggi", O + "deck/tb_v2_l41c.cir", "* Prima riga = titolo (docs/limitations.md #10).",
     "* Prima riga = titolo (docs/limitations.md #10). sabotaggio", "il deck di V2 rigenerato"),
    ("scomposizione_db", O + "scomposizione.csv", ",-0.24,-0.55,", ",-0.24,-0.65,",
     "gli scarti in dB non tornano"),
    ("scomposizione_picco", O + "scomposizione.csv", "0.0008685,0.0008149", "0.0008685,0.0008148",
     "scomposizione.csv, guasto: picco_V_oggi"),
    # il calore
    ("stima_non_rieseguita", O + "termica/stima_telaio_l51b.txt", "10.7     57.2", "10.7     57.1",
     "non ridà stima_telaio_l51b.txt"),
    ("banco_audio", O + "termica/tb_calore.log", "paud=8.94685", "paud=9.94685",
     "il banco carica la scheda audio"),
    ("bilancio", O + "termica/tb_calore.log", "pt2=2.48711", "pt2=2.98711", "il bilancio dei secondari"),
    ("deck_calore", O + "termica/tb_calore.cir", ".options reltol=1e-4 abstol=1e-10 vntol=1e-6",
     ".options reltol=1e-3 abstol=1e-10 vntol=1e-6", "deck del calore"),
    ("ferro_non_dichiarato", O + "termica/stima_telaio_l51b.txt", "ferro di T2 (ipotesi)",
     "ferro di T2          ", "le voci in ipotesi"),
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
