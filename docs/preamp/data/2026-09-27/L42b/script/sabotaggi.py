#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L42b) fatto fallire,
piu' i 15 di L42a, rieseguiti.

    /usr/bin/python3 docs/preamp/data/2026-09-27/L42b/script/sabotaggi.py

Il meccanismo e' quello di L42a (data/2026-09-27/L42/script/sabotaggi.py, da
cui si importano i suoi 15): una sostituzione di testo in UN file versionato,
il generatore lanciato, il file rimesso com'era byte per byte. Il sabotaggio
e' "caduto" se il generatore esce != 0 e la sua uscita contiene il motivo
atteso. Prima e dopo, il generatore sui file veri deve uscire 0.

In piu', i sabotaggi del disegnatore dell'alimentatore
(docs/preamp/schematic/psu_blocks_draw.py): una COPIA sabotata di psu.net,
passata con PSU_NET, e lo SVG in una cartella temporanea. Caduto se il
disegnatore esce != 0 col motivo atteso.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
D = "docs/preamp/data/"
B = D + "2026-09-27/L42b/"
BC = D + "2026-09-27/L42b-L41c/"
BB2 = D + "2026-09-27/L42b-L41b2/"
DRAW = os.path.join(REPO, "docs", "preamp", "schematic", "psu_blocks_draw.py")
VENV = os.path.join(REPO, "env", "venv", "bin", "python3")
if not os.path.exists(VENV):
    VENV = "/Users/roberto/EDA/env/venv/bin/python3"

_spec = importlib.util.spec_from_file_location(
    "sab_l42a", os.path.join(REPO, D, "2026-09-27", "L42", "script", "sabotaggi.py"))
L42A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L42A)

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB_L42B = [
    # 8. la potenza
    ("log_rete_con_un_errore", B + "rete/tb_psu_rete.log",
     "Using SPARSE 1.3 as Direct Linear Solver", "Error: singular matrix", "invalidano la corsa"),
    ("r512_non_rimessa_a_posto", B + "guasti/tb_psu_guasti.log",
     "@rr512[resistance] = 1.000000000000000e+15", "@rr512[resistance] = 2.200000000000000e+05",
     "(#34)"),
    ("un_caso_perso_dall_analisi", B + "rete/analisi.csv",
     "regime_p10,", "regime_p11,", "analisi.csv: casi"),
    ("deck_rete_non_da_psu_net", B + "rete/tb_psu_rete.cir",
     "RR512 v5 md 220k", "RR512 v5 md 230k", "non e' quello di oggi"),
    ("carico_l41a_non_ridice_L41a", B + "carico_l41a/rete/analisi.csv",
     "perdita_rete_m10,,,,,,,,14.225,", "perdita_rete_m10,,,,,,,,15.225,", "carico di L41a"),
    ("raddrizzatore_ricorso_diverso", B + "scelte/raddrizzatore.csv",
     "12,30,0.9,265,14.264,", "12,30,0.9,265,14.265,", "raddrizzatore"),
    ("L41a_rete_come_prima_strada", "docs/preamp/dossier/build_dossier.py",
     'rows_of(vecchio(L41A, nome, "analisi.csv"))', 'rows_of(src(L41A, nome, "analisi.csv"))',
     "viene da"),
    # 9. il sorvegliante (L41c)
    ("L41c_verdetto_riscritto", D + "2026-09-26/L41c/seq/analisi_seq.txt",
     "VERDETTO: PASSA", "VERDETTO: FALLISCE", "verdetto FALLISCE"),
    ("L41c_ricorsa_diversa", BC + "seq/analisi_seq.txt",
     "MUTE_CMD rilasciato 14.40 ms dopo", "MUTE_CMD rilasciato 14.50 ms dopo", "L41c: analisi_seq.txt"),
    ("L41c_deck_al_punto_fisso", BC + "seq/perdita/tb_psu_seq_perdita_g3.cir",
     "RR534 permit_t rly_ret 332k", "RR534 permit_t rly_ret 330k", "L41c, perdita"),
    ("L41c_uscite_del_core", BC + "seq/perdita/core_g3.csv",
     "0.000000,1,1,1,1,1,3221,1191,MUSICA", "0.000000,1,1,1,1,1,3222,1191,MUSICA", "core_g3.csv"),
    ("L41c_ponte", BC + "ponte/perdita.json",
     '"t_jack": 1.0174', '"t_jack": 1.0184', "ponte perdita"),
    # 10. il temporizzatore (L41b1)
    ("timer_testo_ritoccato", D + "2026-09-26/L41b1/timer/analisi_timer.txt",
     "D = 16.91 ms", "D = 17.91 ms", "non ridà analisi_timer.txt"),
    ("timer_corso_oggi_diverso", B + "timer/tb_psu_timer_min.log",
     "t_mute              =  2.00147e+00", "t_mute              =  2.00157e+00", "corsi oggi"),
    ("timer_deck_non_da_psu_net", D + "2026-09-26/L41b1/timer/tb_psu_timer_nom.cir",
     "CC528 permit_t rly_ret 100n", "CC528 permit_t rly_ret 110n", "deck del temporizzatore nom"),
    ("timer_log_con_singular", D + "2026-09-26/L41b1/timer/tb_psu_timer_nom.log",
     "Doing analysis at TEMP = 27.000000 and TNOM = 27.000000",
     "singular matrix at TEMP = 27.000000 and TNOM = 27.000000", "singular"),
    # 11. il firmware (L41b2)
    ("L41b2_ricorsa_diversa", BB2 + "seq/analisi_seq.txt",
     "MUTE_CMD eccitato 49.4 ms dopo", "MUTE_CMD eccitato 49.5 ms dopo", "L41b2: analisi_seq.txt"),
    ("falsi_host_ricorsi_diversi", B + "falsi/esito.txt",
     "== falsi: 21 su 21", "== falsi: 21 su 22", "falsi sull'host"),
    ("falsi_host_sintesi_falsa", D + "2026-09-26/L41b2/falsi/esito.txt",
     "== falsi: 21 su 21", "== falsi: 20 su 21", "esito.txt dei falsi"),
    ("falso6_sul_criterio_sbagliato", D + "2026-09-26/L41b2/falsi/seq_falso6_guasto.txt",
     "   n   NO    MUTE_REQ", "   n   ok    MUTE_REQ", "criteri caduti"),
    # 12. le LDR (L41b2)
    ("ldr_csv_non_da_analizza", D + "2026-09-26/L41b2/ldr/tb_psu_ldr_cal_cima12mA.log.csv",
     "comp,S,d0,15,0.012,3156,0.009433626893244,-2.090051009173111",
     "comp,S,d0,15,0.012,3156,0.009433626893244,-2.190051009173111", "dalle correnti"),
    ("ldr_corse_oggi_diverse", B + "ldr/tb_psu_ldr_cima12mA.log.csv",
     "comp,S,d0,15,0.012,3156,0.009433626893244", "comp,S,d0,15,0.012,3156,0.009433626893245",
     "LDR corse oggi"),
    ("calibrazione_ricorsa_diversa", B + "ldr/cal_cima12mA.json",
     '"r_ohm": 0.6327367441513251', '"r_ohm": 0.6327367441513252', "calibrazione"),
    # 13. spegnimento e failsafe al jack
    ("tabella_L30_ritoccata", D + "2026-09-26/L30/tabella.csv",
     "f_c470p_l30,f,MAINJACK,0.001773,58.4", "f_c470p_l30,f,MAINJACK,0.001773,57.4",
     "tabella.py rieseguito"),
    ("formula_di_nc028", "docs/preamp/NONCOMPLIANCE.md",
     "96 + 20·log(21,1·ΔV / 2,83)", "97 + 20·log(21,1·ΔV / 2,83)", "formula di NC-028"),
    ("L30_corse_oggi_diverse", B + "l30/corse/analisi.csv",
     "MAINJACK,6.896e-11,", "MAINJACK,6.897e-11,", "analisi.csv corso oggi"),
    ("L41c_tabella_corsa_oggi", BC + "tabella.csv",
     "guasto,MAINJACK,0.001372,56.2", "guasto,MAINJACK,0.001373,56.2", "tabella corsa oggi"),
    ("deck_L30_rigenerato_diverso", B + "l30/tb_v2_l30.cir",
     "* IL PROFILO v4, Td 6 s", "* IL PROFILO v4, Td 7 s", "deck di L30 rigenerato"),
    ("soglia_di_P9_illeggibile", "docs/preamp/REQUIREMENTS.md",
     "rilascia `MUTE_CMD` entro 1 ms", "rilascia `MUTE_CMD` entro un ms", "non trovo entro_ms"),
]

# i sabotaggi del disegnatore: (nome, vecchio, nuovo, frammento atteso)
SAB_DRAW = [
    ("soglia_del_rail_piu", '(ref "R506")\n      (value "44.2k")',
     '(ref "R506")\n      (value "34.2k")', "soglie dei rail"),
    ("q505_fuori_da_vrelay", '(ref "Q505")\n        (pin "3")',
     '(ref "Q505")\n        (pin "9")', "Q505"),
    ("u506_non_tira_mute_g", '(ref "U506")\n        (pin "7")',
     '(ref "U506")\n        (pin "77")', "U506"),
]


def draw(net):
    env = dict(os.environ, PSU_NET=net,
               PSU_BLOCKS_SVG=os.path.join(tempfile.gettempdir(), "psu_blocks_sab.svg"))
    p = subprocess.run([VENV, DRAW], capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def main():
    rc, out = L42A.build()
    if rc != 0:
        print("il generatore non passa sui file veri:\n" + out)
        return 1
    bad = 0
    tutti = L42A.SAB + SAB_L42B
    for i, (nome, rel, old, new, atteso) in enumerate(tutti):
        if i == len(L42A.SAB):
            print("---- L42b")
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
            rc, out = L42A.build()
        finally:
            with open(path, "wb") as f:
                f.write(orig)
        ok = rc != 0 and atteso in out
        bad += not ok
        riga = next((ln.strip() for ln in out.splitlines() if atteso in ln), out.strip()[-120:])
        print(f"{nome:36s} {'caduto' if ok else 'NON CADUTO'}  rc={rc}  {riga[:150]}")
    print("---- il disegnatore dell'alimentatore")
    net = os.path.join(REPO, "circuits", "preamp", "psu.net")
    rc, out = draw(net)
    if rc != 0:
        print("il disegnatore non passa sulla netlist vera:\n" + out)
        return 1
    src = open(net, encoding="utf-8").read()
    for nome, old, new, atteso in SAB_DRAW:
        if src.count(old) < 1:
            print(f"{nome:36s} NON APPLICABILE: il testo da sabotare non c'e'")
            bad += 1
            continue
        tmp = os.path.join(tempfile.mkdtemp(prefix="sab_psu_"), "psu.net")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(src.replace(old, new, 1))
        rc, out = draw(tmp)
        ok = rc != 0 and atteso in out
        bad += not ok
        riga = next((ln.strip() for ln in out.splitlines() if atteso in ln), out.strip()[-120:])
        print(f"{nome:36s} {'caduto' if ok else 'NON CADUTO'}  rc={rc}  {riga[:150]}")
    rc, out = L42A.build()
    rcd, _ = draw(net)
    n = len(tutti) + len(SAB_DRAW)
    print(f"\ndi nuovo sui file veri: generatore rc={rc}, disegnatore rc={rcd}")
    print(f"{n - bad} sabotaggi su {n} caduti ({len(L42A.SAB)} di L42a, "
          f"{len(SAB_L42B) + len(SAB_DRAW)} di L42b)")
    return 1 if bad or rc or rcd else 0


class _Tee:
    """Quello che si stampa va anche in sabotaggi.txt, accanto a questo file,
    senza i colori ANSI dei traceback."""

    def __init__(self, s):
        self.s, self.buf = s, []

    def write(self, x):
        self.s.write(x)
        self.buf.append(x)

    def flush(self):
        self.s.flush()


if __name__ == "__main__":
    import re
    tee = _Tee(sys.stdout)
    sys.stdout = tee
    rc = main()
    sys.stdout = tee.s
    with open(os.path.join(HERE, "sabotaggi.txt"), "w", encoding="utf-8") as f:
        f.write(re.sub(r"\x1b\[[0-9;]*m", "", "".join(tee.buf)))
    sys.exit(rc)
