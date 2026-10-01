#!/usr/bin/env python3
"""L44 (ADR-057) - aggiorna i .provenance.json dei cinque modelli bipolari: la frase
"NO KF/AF" nelle note diventa il tetto dichiarato, e "changes" dice la riga aggiunta.
Sostituzione di testo sul file grezzo (il JSON non si riformatta); idempotente;
alla fine ogni file si rilegge con json.load. Uso: /usr/bin/python3 provenienza_kf.py
"""
import json
import os

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, *[".."] * 6))
SEGNO = "L44 (ADR-057)"

VECCHIA = ("NO KF/AF, therefore NO 1/f noise - in this repo only models/jfet/lsk489.lib has "
           "flicker noise, which is why NC-004 does not close when the real models arrive. Any "
           "noise figure computed with this device is a floor without flicker and must say so "
           "next to the number.")
VECCHIA_LS = ("NO KF/AF, therefore NO 1/f noise - same gap as every other model in this repo "
              "except the LSK489 (NC-004).")
NUOVA = ("NO KF/AF FROM THE MANUFACTURER. Since L44 (ADR-057) the model carries a DECLARED UPPER "
         "BOUND, KF = 1e-13 AF = 1.4, read from published curves of the class (2N5087, Motorola, "
         "Fig. 2; LS310/LS350 family, Linear Systems databook Fig. 3 p. 329), not fitted to this "
         "part%s. Noise figures with this device are bounds with flicker, no longer floors without "
         "it; the [flicker] check of scripts/validate_models.py reads KF and AF back from the noise.")
SPEC = {
    "models/bjt_pnp/ls350.lib": (VECCHIA_LS, " - for the LS35x family itself the curve exists but its "
                                 "caption does not say LS310 or LS350",
                                 "the KF/AF line is the last line of the hand-transcribed card, "
                                 "inside the parenthesis; every vendor value is unchanged"),
    "models/bjt_pnp/mmbt5401.lib": (VECCHIA, " - no curve exists for the 2N5401/MMBT5401",
                                    "one '+ KF=1e-13 AF=1.4' line APPENDED at the end of the file, "
                                    "outside the vendor block, which stays byte for byte (CRLF "
                                    "included); the non-comment diff against the vendor file is that "
                                    "one line"),
    "models/bjt_npn/mmbt5551.lib": (VECCHIA, " - no curve exists for the 2N5551/MMBT5551: the NPN "
                                    "gets the PNP-class bound by declared choice",
                                    "one '+ KF=1e-13 AF=1.4' line APPENDED at the end of the file, "
                                    "outside the vendor block, which stays byte for byte (CRLF "
                                    "included); the non-comment diff against the vendor file is that "
                                    "one line"),
    "models/bjt_npn/mje15032.lib": (VECCHIA, " - no curve exists for any power bipolar: applied by "
                                    "declared choice, and the L44 scan shows the output stage moves "
                                    "E5 by < 0.001 uV even at a 100 kHz corner",
                                    "one '+ KF=1e-13 AF=1.4' line APPENDED at the end of the file, "
                                    "outside the vendor block, which stays byte for byte; it "
                                    "overrides the vendor's KF=0 AF=1 (the last value wins, measured)"),
    "models/bjt_pnp/mje15033.lib": (VECCHIA, " - no curve exists for any power bipolar: applied by "
                                    "declared choice, and the L44 scan shows the output stage moves "
                                    "E5 by < 0.001 uV even at a 100 kHz corner",
                                    "one '+ KF=1e-13 AF=1.4' line APPENDED at the end of the file, "
                                    "outside the vendor block, which stays byte for byte; it "
                                    "overrides the vendor's KF=0 AF=1 (the last value wins, measured)"),
}


def main():
    for rel, (vecchia, parte, come) in SPEC.items():
        p = os.path.join(ROOT, rel[:-4] + ".provenance.json")
        t = open(p).read()
        if SEGNO in t:
            print("gia' fatto:", rel)
            continue
        if t.count(vecchia) != 1:
            raise SystemExit("%s: frase da sostituire trovata %d volte" % (p, t.count(vecchia)))
        t = t.replace(vecchia, NUOVA % parte)
        d = json.loads(t)
        coda = (" %s: %s. Source readings and the bound: vendor/bjt_pnp/motorola/2N5087/PROVENANCE.json, "
                "vendor/bjt_pnp/linear_systems/LS350/PROVENANCE-L44-addendum.json, "
                "docs/preamp/decisions/ADR-057*." % (SEGNO, come))
        vecchio_ch = json.dumps(d["changes"], ensure_ascii=False)
        if t.count(vecchio_ch) != 1:
            vecchio_ch = json.dumps(d["changes"])
        if t.count(vecchio_ch) != 1:
            raise SystemExit("%s: campo changes non trovato una volta sola" % p)
        t = t.replace(vecchio_ch, json.dumps(d["changes"] + coda, ensure_ascii=vecchio_ch.isascii()))
        json.loads(t)
        open(p, "w").write(t)
        print("scritto:", p)


if __name__ == "__main__":
    main()
