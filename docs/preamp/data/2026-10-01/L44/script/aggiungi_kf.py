#!/usr/bin/env python3
"""L44 (ADR-057) - aggiunge il flicker (KF/AF) ai quattro modelli del costruttore
copiati byte per byte in models/ (MMBT5551, MMBT5401, MJE15032, MJE15033).

NON tocca il blocco del costruttore: appende in CODA al file una sezione L44 con
una sola riga di continuazione '+ KF=.. AF=..'. ngspice unisce una riga '+' alla
scheda precedente saltando i commenti in mezzo, e un KF ripetuto vale l'ultimo:
verificato in L44 misurando il KF prodotto (sui MJE sovrascrive il KF=0 AF=1
del costruttore). La prova permanente e' il controllo [flicker] di
scripts/validate_models.py. Cosi' `diff` delle righe non di commento fra il file
del costruttore e models/ resta vuoto salvo questa riga.

ls350.lib e' una trascrizione a mano (non byte per byte): la riga KF/AF va dentro
la scheda, e la si scrive con Edit, non qui.

Idempotente: se la sezione c'e' gia', non scrive niente. Uso: /usr/bin/python3 aggiungi_kf.py
"""
import os

QUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(QUI, *[".."] * 6))
KF, AF = "1e-13", "1.4"
SEGNO = b"* L44 (ADR-057): FLICKER NOISE ADDED"

COMUNE = """*
* ------------------------------------------------------------------
* L44 (ADR-057): FLICKER NOISE ADDED - NOT FROM THE MANUFACTURER
* ------------------------------------------------------------------
* The '+' line at the very end CONTINUES the .MODEL card above: ngspice
* joins it to the last card and skips the comment lines in between, and
* when a parameter repeats the LAST value wins. Measured in L44, not
* assumed, and re-measured on every run by the [flicker] check in
* scripts/validate_models.py (base-current noise, KF read back from
* S(10 Hz) - S(10 kHz)). It sits OUTSIDE the vendor block so that the
* vendor bytes stay exactly as served: the non-comment diff against the
* file under vendor/ is this one line and nothing else.
*
* WHAT THE NUMBERS ARE. ngspice: i_n^2 = 2 q Ib + KF Ib^AF / f. KF = 1e-13
* with AF = 1.4 is a DECLARED UPPER BOUND for the small-signal bipolar
* class, not a fit to this part. Sources (PDFs and readings under vendor/,
* PROVENANCE files next to them):
*   - 2N5087, Motorola, Fig. 2 p. 3 (vendor/bjt_pnp/motorola/2N5087/):
*     AF = 1.35 consistent over 10 uA..1 mA, KF ~2e-14 at 10 Hz, ~5e-14
*     at 300 Hz;
*   - Linear Systems databook, "Solving the Noise Puzzle", Fig. 3 p. 329
*     (LS310/LS350 family): AF ~1.46, KF ~6e-14; worst case ~2x typical.
*   Typical class value 5e-14; the bound is 2x that.
*%s
* What it buys: E5 with this bound on every bipolar device is 5.53 uV
* worst case against 9.95 (5.1 dB margin); a bound 10x higher still gives
* 8.57 uV. data/2026-10-01/L44/, report 2026-10-01-L44-rumore-1f.md.
"""
PROPRIO = {
    "models/bjt_npn/mmbt5551.lib": """
* FOR THIS PART THERE IS NO CURVE: the L44 search found none for the
* 2N5551/MMBT5551 (NXP, Fairchild, Motorola sheets give a single NF
* figure). The NPN gets the PNP-class bound by DECLARED CHOICE; the
* nearest NPN curve found (2N5089, a very-high-gain type) is weaker
* evidence and was not used for a number.""",
    "models/bjt_pnp/mmbt5401.lib": """
* FOR THIS PART THERE IS NO CURVE (2N5401/MMBT5401: single NF figure
* only). As a small-signal PNP it is in the class the 2N5087 curves
* describe directly. In the gain block it is the VAS, the device whose
* flicker weighs most on E5 in the L44 scan.""",
    "models/bjt_npn/mje15032.lib": """
* FOR THIS PART THERE IS NO CURVE, and none was found for any power
* bipolar: the bound is applied by DECLARED CHOICE. The L44 scan shows it
* does not matter here - the output stage moves E5 by < 0.001 uV even
* with a 100 kHz 1/f corner. The vendor card's own KF=0 AF=1 is
* overridden by the line below.""",
    "models/bjt_pnp/mje15033.lib": """
* FOR THIS PART THERE IS NO CURVE, and none was found for any power
* bipolar: the bound is applied by DECLARED CHOICE. The L44 scan shows it
* does not matter here - the output stage moves E5 by < 0.001 uV even
* with a 100 kHz 1/f corner. The vendor card's own KF=0 AF=1 is
* overridden by the line below.""",
}


# L'intestazione NOSTRA (LF) di ogni file diceva "nessun flicker": si corregge qui,
# sui byte. MAI con un editor che riscrive il file: normalizza i CRLF del blocco
# del costruttore e rompe il diff (e' successo in L44, prima di questo script).
INTESTAZIONE = {
    "models/bjt_npn/mmbt5551.lib": (
        "* NO FLICKER NOISE: no KF, no AF. In this repo only models/jfet/lsk489.lib\n"
        "* has 1/f noise, so every noise figure that leans on this device is a\n"
        "* floor without flicker (NC-004), and that belongs next to the number.\n",
        "* NO FLICKER NOISE FROM THE MANUFACTURER: the vendor line has no KF, no\n"
        "* AF. Until L44 every noise figure that leaned on this device was a floor\n"
        "* without flicker (NC-004). Since L44 (ADR-057) a declared upper bound,\n"
        "* KF = 1e-13 AF = 1.4, is appended at the END of this file, outside the\n"
        "* vendor block - read the L44 section there before quoting a noise figure.\n"),
    "models/bjt_pnp/mmbt5401.lib": (
        "* NO FLICKER NOISE: no KF, no AF anywhere in the line. Same gap as the\n"
        "* two MJE models, the 1N4148, the LS350, the THAT320 vendor models and\n"
        "* the hand-written placeholders - in this repo ONLY models/jfet/lsk489.lib\n"
        "* has 1/f noise. NC-004 stays open for this reason, and any noise figure\n"
        "* computed with this device is a floor without flicker, which must be\n"
        "* written next to the number rather than left implicit.\n",
        "* NO FLICKER NOISE FROM THE MANUFACTURER: no KF, no AF anywhere in the\n"
        "* vendor line. Until L44 every noise figure computed with this device was\n"
        "* a floor without flicker (NC-004). Since L44 (ADR-057) a declared upper\n"
        "* bound, KF = 1e-13 AF = 1.4, is appended at the END of this file, outside\n"
        "* the vendor block - read the L44 section there before quoting a noise\n"
        "* figure.\n"),
    "models/bjt_npn/mje15032.lib": (
        "* NO FLICKER NOISE. The line carries KF=0 and AF=1 explicitly, which is\n"
        "* the same thing as having none: the flicker term is multiplied by KF.\n"
        "* In this repo only models/jfet/lsk489.lib has 1/f noise (NC-004).\n",
        "* NO FLICKER NOISE FROM THE MANUFACTURER. The vendor line carries KF=0\n"
        "* and AF=1 explicitly, which is the same thing as having none. Since L44\n"
        "* (ADR-057) a declared upper bound, KF = 1e-13 AF = 1.4, is appended at\n"
        "* the END of this file, outside the vendor block, and overrides it.\n"),
    "models/bjt_pnp/mje15033.lib": (
        "* NO FLICKER NOISE: KF=0, AF=1, which is the same thing as having none.\n"
        "* In this repo only models/jfet/lsk489.lib has 1/f noise (NC-004).\n",
        "* NO FLICKER NOISE FROM THE MANUFACTURER: KF=0, AF=1 in the vendor line,\n"
        "* which is the same thing as having none. Since L44 (ADR-057) a declared\n"
        "* upper bound, KF = 1e-13 AF = 1.4, is appended at the END of this file,\n"
        "* outside the vendor block, and overrides it.\n"),
}


def main():
    for rel, testo in PROPRIO.items():
        p = os.path.join(ROOT, rel)
        b = open(p, "rb").read()
        if SEGNO in b:
            print("gia' presente:", rel)
            continue
        vecchio, nuovo = (s.encode() for s in INTESTAZIONE[rel])
        if b.count(vecchio) != 1:
            raise SystemExit("%s: intestazione da correggere trovata %d volte" % (rel, b.count(vecchio)))
        b = b.replace(vecchio, nuovo)
        coda = COMUNE % testo + "+ KF=%s AF=%s\n" % (KF, AF)
        sep = b"" if b.endswith(b"\n") else b"\n"
        open(p, "wb").write(b + sep + coda.encode())
        print("scritto:", rel)


if __name__ == "__main__":
    main()
