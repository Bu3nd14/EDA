#!/usr/bin/env python3
"""L33 - annota in coda i README datati che danno per «del costruttore» l'LSK489.

    /usr/bin/python3 annota.py <radice-del-repo>

Un README datato e' l'output di un'esecuzione: il suo testo non si riscrive. Si
aggiunge una nota IN CODA, e basta. Rifiuta, senza scrivere niente, se la frase
citata dalla nota non c'e' piu' nel README o se la nota c'e' gia'. Che il diff
abbia solo righe aggiunte lo prova `git diff`, non questo script.
"""

import os
import sys

HEAD = "## Nota di L33 (2026-09-15) — la provenienza dell'LSK489"

FACTS = """\
- L'LSK489 simulato è **`LSK489X`**, il segnaposto scritto a mano di
  `spice/preamp/placeholder_devices.lib`, con `KF = 0`. Il modello del
  costruttore, `models/jfet/lsk489.lib` (`LSK489A`), non l'ha mai incluso
  nessun deck, né oggi né alla data di questi dati:
  `git log -S "jfet/lsk489.lib" -- spice circuits` è vuoto.
- L'unico modello del costruttore simulato è l'**LS352**
  (`models/bjt_pnp/ls350.lib`), che non ha `KF`. Quindi **nessun dispositivo
  simulato ha rumore 1/f**.
- **Nessun numero cambia**, cambia cosa se ne crede: ogni cifra di rumore qui è
  un pavimento senza flicker, JFET compresi (NC-004, NC-031)."""


def note(quote, extra=""):
    return (f"\n{HEAD}\n\nIl testo sopra resta com'era: è l'output di un'esecuzione "
            f"datata. **Una sua frase non è vera**: {quote}.\n\n{FACTS}\n{extra}")


DATA = "docs/preamp/data"
NOTES = {
    f"{DATA}/2026-09-14/L12/README.md":
        ("segnaposto più LS352 e LSK489 vendor",
         note("«Modelli: segnaposto più LS352 e LSK489 vendor»")),
    f"{DATA}/2026-09-14/L27/README.md":
        ("segnaposto più LS352 e LSK489 vendor",
         note("«Modelli: segnaposto più LS352 e LSK489 vendor»")),
    f"{DATA}/2026-09-14/L16/README.md":
        ("segnaposto più LS352 e LSK489 vendor",
         note("«Modelli: segnaposto più LS352 e LSK489 vendor»")),
    f"{DATA}/2026-09-14/L17/README.md":
        ("tranne LS352 e LSK489",
         note("«Ogni dispositivo è un segnaposto […], tranne LS352 e LSK489»")),
    f"{DATA}/2026-09-10/README.md":
        ("solo lo specchio e l'LSK489 hanno un modello del",
         note("«nel percorso di segnale solo lo specchio e l'LSK489 hanno un modello "
              "del costruttore»",
              "- Due frasi che ne discendono vanno lette così:\n"
              "  - «Nel repo solo l'LSK489 ha flicker» è vera della libreria "
              "`models/`, non di\n    questi dati;\n"
              "  - «il contributo del JFET qui è conservativo» (NC-013) non si "
              "applica: il\n    modello d'angolo di NC-013 è `LSK489A`, che qui "
              "non è simulato.\n")),
    f"{DATA}/2026-09-13/README.md":
        ("ogni altro dispositivo ancora segnaposto",
         note("«LSK489 fuso in una Part, specchio LS352 a 220 Ω, ogni altro "
              "dispositivo ancora segnaposto», che si legge come se l'LSK489 non "
              "fosse un segnaposto. Lo è")),
    f"{DATA}/2026-09-14/README.md":
        ("Ogni altro dispositivo è ancora un segnaposto",
         note("«(LSK489 fuso in una Part, specchio LS352 a 220 Ω). Ogni altro "
              "dispositivo è ancora un segnaposto», che si legge come se l'LSK489 "
              "non fosse un segnaposto. Lo è")),
}


def main():
    root = os.path.abspath(sys.argv[1])
    out, errors = {}, []
    for relp, (must, text) in NOTES.items():
        path = os.path.join(root, relp)
        with open(path) as fh:
            body = fh.read()
        flat = " ".join(body.split())
        if " ".join(must.split()) not in flat:
            errors.append(f"{relp}: la frase «{must}» non c'e'")
        if HEAD in body:
            errors.append(f"{relp}: la nota di L33 c'e' gia'")
        out[path] = body + ("" if body.endswith("\n") else "\n") + text
    if errors:
        print("RIFIUTATO, nessun file scritto:", *errors, sep="\n  ")
        return 1
    for path, body in out.items():
        with open(path, "w") as fh:
            fh.write(body)
        print(f"   annotato {os.path.relpath(path, root)}")
    print(f"{len(out)} README annotati")
    return 0


if __name__ == "__main__":
    sys.exit(main())
