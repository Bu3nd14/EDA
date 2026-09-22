#!/usr/bin/env python3
"""L39 (NC-017): porta i deck di spice/preamp/tb/ dai segnaposto ai modelli del
costruttore. Solo le parti MECCANICHE, uguali in molti deck:

  1. la riga `.include @REPO@/spice/preamp/placeholder_devices.lib` diventa gli
     include diretti dei modelli di models/ che il blocco istanzia (diretti:
     provenance() di build_dossier.py non segue gli include annidati); un
     include gia' presente non si ripete;
  2. il blocco di commento standard L22/L33 (identico in 14 deck) diventa quello
     di L39;
  3. le due righe «PROVVISORIO SUI MODELLI» (identiche in 4 deck) diventano la
     riga dei modelli di L39;
  4. i nomi dei modelli MJE nell'elenco «NOMI DEI DISPOSITIVI».

Ogni sostituzione si conta: se un testo atteso non c'e' dove deve, lo script si
ferma e non scrive niente. Le frasi isolate si correggono a mano, dopo.
tb_v2_mute_ldr.cir si salta: e' generato (L29b2), si rigenera dal generatore.

Uso: /usr/bin/python3 porta_deck.py [--scrivi]      (senza: prova a secco)
"""
import glob
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
TB = os.path.join(ROOT, "spice", "preamp", "tb")
GENERATO = {"tb_v2_mute_ldr.cir"}

PH = ".include @REPO@/spice/preamp/placeholder_devices.lib"
MODELLI = [
    ".include @REPO@/models/jfet/lsk489.lib",
    ".include @REPO@/models/bjt_npn/mmbt5551.lib",
    ".include @REPO@/models/bjt_pnp/mmbt5401.lib",
    ".include @REPO@/models/bjt_npn/mje15032.lib",
    ".include @REPO@/models/bjt_pnp/mje15033.lib",
    ".include @REPO@/models/diodes/1n4148.lib",
]

STD_VECCHIO = """\
* L22: the input current mirror is no longer a placeholder. It is an
* LS352 (ADR-018) and this is its VENDOR model - the only one in this
* deck. L33 (NC-031): the LSK489 is not a vendor model here. Its halves
* are LSK489X, a hand-written placeholder with KF=0; the vendor model
* models/jfet/lsk489.lib is included by no deck (Fase 4, NC-017). Every
* OTHER device here is a hand-written placeholder too, and none has 1/f.
"""
STD_NUOVO = """\
* L39 (NC-017): every active device in this deck is a vendor model from
* models/, each next to its .provenance.json:
*   LSK489   - vendor model LSK489A, the published corner sample (I_DSS
*              2.59 mA, below the group-B window of ADR-031)
*   LS352    - vendor model LS350 (ADR-018), included on the next line
*   MMBT5551 - vendor model, Diodes Inc. (ADR-017)
*   MMBT5401 - vendor model, Diodes Inc. (ADR-017)
*   MJE15032 - vendor model Qmje15032, onsemi (NC-024, NC-025)
*   MJE15033 - vendor model Qmje15033, onsemi (NC-025)
*   1N4148   - vendor model D1N914, onsemi (docs/limitations.md #20)
* Only the LSK489A carries KF: 1/f noise is on the input pair and nowhere
* else. No model carries part-to-part spread.
"""

PROV_VECCHIO = """\
* PROVVISORIO SUI MODELLI: tutto tranne LS352 e' segnaposto, LSK489 compreso
* (LSK489X in placeholder_devices.lib, KF=0; NC-017, NC-031)."""
PROV_NUOVO = """\
* MODELLI (L39, NC-017): ogni dispositivo attivo e' il modello del costruttore
* in models/ - LSK489A, MMBT5551, MMBT5401, LS350, Qmje15032, Qmje15033, D1N914.
* Solo l'LSK489A ha KF (1/f); nessun modello porta la dispersione."""

MJE_VECCHIO = "*   Q132 NMJE15032 (NPN d'uscita)   Q133 PMJE15033 (PNP d'uscita)"
MJE_NUOVO = "*   Q132 Qmje15032 (NPN d'uscita)   Q133 Qmje15033 (PNP d'uscita)"


def porta(testo):
    conta = {}
    righe = testo.split("\n")
    if righe.count(PH) != 1:
        raise ValueError("%d righe include dei segnaposto, attesa 1" % righe.count(PH))
    presenti = set(r.strip() for r in righe)
    nuovi = [m for m in MODELLI if m not in presenti]
    i = righe.index(PH)
    righe[i:i + 1] = nuovi
    conta["include"] = len(nuovi)
    testo = "\n".join(righe)
    for nome, v, n in (("std", STD_VECCHIO, STD_NUOVO), ("prov", PROV_VECCHIO, PROV_NUOVO),
                       ("mje", MJE_VECCHIO, MJE_NUOVO)):
        k = testo.count(v)
        if k > 1:
            raise ValueError("%s: %d occorrenze" % (nome, k))
        conta[nome] = k
        testo = testo.replace(v, n)
    return testo, conta


def main():
    scrivi = "--scrivi" in sys.argv
    out = {}
    for f in sorted(glob.glob(os.path.join(TB, "*.cir"))):
        b = os.path.basename(f)
        if b in GENERATO:
            print("%-34s saltato: generato" % b)
            continue
        try:
            nuovo, conta = porta(open(f).read())
        except ValueError as e:
            sys.exit("%s: %s - niente scritto" % (b, e))
        out[f] = nuovo
        print("%-34s %s" % (b, " ".join("%s=%d" % kv for kv in sorted(conta.items()))))
    if scrivi:
        for f, t in out.items():
            open(f, "w").write(t)
        print("scritti %d deck" % len(out))


if __name__ == "__main__":
    main()
