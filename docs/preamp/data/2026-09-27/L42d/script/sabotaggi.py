#!/usr/bin/env python3
"""sabotaggi.py : ogni controllo nuovo di build_dossier.py (L42d, il contratto)
fatto fallire, piu' tutti quelli di L42a e L42b, rieseguiti.

    /usr/bin/python3 docs/preamp/data/2026-09-27/L42d/script/sabotaggi.py

Il meccanismo e' quello di L42a e L42b: una sostituzione di testo in UN file
versionato, il generatore lanciato, il file rimesso com'era byte per byte. Il
sabotaggio e' "caduto" se il generatore esce != 0 e la sua uscita contiene il
motivo atteso. Prima i sabotaggi di L42b (che importa quelli di L42a) col suo
main(), poi quelli di L42d; alla fine il generatore sui file veri deve uscire 0.
"""
import glob
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))
PRB = "docs/preamp/PRB.md"
DEC = "docs/preamp/decisions/"
BUILD = "docs/preamp/dossier/build_dossier.py"
CT = "docs/preamp/dossier/contratto.py"

_spec = importlib.util.spec_from_file_location(
    "sab_l42b", os.path.join(REPO, "docs", "preamp", "data", "2026-09-27", "L42b", "script",
                             "sabotaggi.py"))
L42B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L42B)
L42A = L42B.L42A


def _rel(p):
    return os.path.relpath(p, REPO)


def _adr(n):
    (p,) = glob.glob(os.path.join(REPO, DEC, f"ADR-{n}-*.md"))
    return p


def _riga(path, pat):
    with open(path, encoding="utf-8") as f:
        return next(ln for ln in f.read().split("\n") if re.match(pat, ln))


# le due righe che dipendono dal testo di oggi si leggono, non si copiano
STATO_030 = _riga(_adr("030"), r"^Data: ")
INDICE_052 = _riga(os.path.join(REPO, DEC, "README.md"), r"^\| \[052\]")

# (nome, file, vecchio, nuovo, frammento atteso nel rifiuto)
SAB_L42D = [
    # a.-c. il PRB
    ("prb_requisito_inesistente", PRB, "*Dettagli: E1, E3b ·", "*Dettagli: E1, E3c ·",
     "PR-1 nomina E3c, che REQUIREMENTS.md non ha"),
    ("prb_adr_inesistente", PRB, "*Dettagli: V4 · ADR-053:", "*Dettagli: V4 · ADR-054:",
     "PR-8 nomina ADR-054"),
    ("prb_nc_inesistente", PRB, "ADR-027 · NC-009.*", "ADR-027 · NC-099.*",
     "PR-6 nomina NC-099"),
    ("prb_voce_duplicata", PRB, "**PR-10 · I due canali", "**PR-9 · I due canali",
     "PR-9 compare due volte"),
    ("prb_voce_di_quattro_righe", PRB,
     "amplifica per default. I due livelli in più servono a una sorgente debole.",
     "amplifica per default.\nI due livelli in più servono\na una sorgente debole.",
     "PR-3 ha 4 righe di corpo"),
    ("prb_voce_senza_dettagli", PRB, "*Dettagli: F4 · ADR-009.*", "Dettagli: F4 · ADR-009.",
     "PR-16 senza la riga"),
    ("prb_superata_senza_successora", PRB, "ADR-008, ADR-009, ADR-023.*", "ADR-008, ADR-009.*",
     "PR-13 cita ADR-008, superata da ADR-023, senza citare ADR-023"),
    # d. le ADR
    ("adr_senza_stato", _rel(_adr("001")), "Data: 2026-09-08 · Stato: accettata",
     "Data: 2026-09-08", "manca la riga «Data: ... · Stato: ...»"),
    ("adr_030_stato_rimasto_indietro", _rel(_adr("030")), STATO_030,
     "Data: 2026-09-15 · Stato: accettata", "ADR-030: lo Stato del file"),
    ("adr_052_fuori_dall_indice", DEC + "README.md", INDICE_052 + "\n", "",
     "ADR-052: il file esiste ma l'indice"),
    ("adr_superata_da_inesistente", DEC + "README.md",
     "| superata da ADR-023 (un buffer", "| superata da ADR-093 (un buffer",
     "nomina ADR-093, che non esiste"),
    # e. i rimandi nel testo
    ("t2_nudo_nel_testo", BUILD, 'mW da {des("T2")}', "mW da T2", "rimando ambiguo: «T2»"),
    ("v5_nudo_nel_testo", BUILD, '<span class="des">V5</span> la scarica', "V5 la scarica",
     "rimando ambiguo: «V5»"),
    ("pr_inesistente_nel_testo", BUILD, "Solo i requisiti che queste misure toccano.",
     "Solo i requisiti che queste misure toccano (PR-30).", "PR-30, che il PRB non ha"),
    ("adr_inesistente_nel_testo", BUILD, "Il blocco è uno solo (ADR-006)",
     "Il blocco è uno solo (ADR-096)", "ADR-096, che decisions/ non ha"),
    ("requisito_inesistente_nel_testo", BUILD, "A(f'<tr><td>E1</td>", "A(f'<tr><td>E14</td>",
     "E14, che REQUIREMENTS.md non ha"),
    ("ancora_rotta", CT, '<tr id="req-{r.lower()}">', '<tr id="rq-{r.lower()}">',
     "ancora rotta"),
]


def main():
    rc_prima = L42B.main()
    print("---- L42d")
    bad = 0
    for nome, rel, old, new, atteso in SAB_L42D:
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
    rc, out = L42A.build()
    n = len(SAB_L42D)
    print(f"\ndi nuovo sui file veri: generatore rc={rc}")
    print(f"L42d: {n - bad} sabotaggi su {n} caduti; quelli di L42a e L42b: "
          f"{'tutti caduti' if rc_prima == 0 else 'NON tutti caduti'} (sopra)")
    return 1 if bad or rc or rc_prima else 0


if __name__ == "__main__":
    tee = L42B._Tee(sys.stdout)
    sys.stdout = tee
    rc = main()
    sys.stdout = tee.s
    with open(os.path.join(HERE, "sabotaggi.txt"), "w", encoding="utf-8") as f:
        f.write(re.sub(r"\x1b\[[0-9;]*m", "", "".join(tee.buf)))
    sys.exit(rc)
