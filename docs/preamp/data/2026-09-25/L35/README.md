# L35 — comandi e LED a pannello nel sorgente, con ADR-045 (2026-09-25)

Dati del lotto L35 (ADR-045, ADR-028; NC-032, NC-028). Report:
`docs/preamp/reports/2026-09-25-L35-comandi-e-led-a-pannello.md`.

Niente simulazioni: L35 non tocca il segnale (il deck V2 si rigenera byte-identico) e l'ordine
di ADR-045 poggia sul rilascio massimo di 3 ms del datasheet contro Δ, non su un tempo simulato.

## Le cartelle

| File | Cosa |
|---|---|
| `falsi/genera_falsi.py` | il 2e esteso fatto fallire: 14 varianti sabotate più la netlist di `main` (prima di L35), un `.txt` per variante con l'uscita del 2e, `esito.csv` col primo problema trovato |
| `falsi/regressione_L16.py` | i falsi di L16 (trim) rifatti su una copia della radice; `bobina_K6_altra_net` si toglie perché da ADR-045 è il progetto |
| `falsi/regressione_L36.py` | i falsi di L36 (guadagno) rifatti sulla netlist di L35; `led_scambiati` non si applica più (D8/D9 usciti dalla scheda) |
| `falsi/regressione.txt` | gli esiti di L16, L29e e L36 col 2e nuovo |

## Come si rifà

```sh
# le netlist storiche: git show <rev>:circuits/preamp/preamp_audio.net in un file
#   main prima di L35 = 6e1c8fc, prima di L36 = 57708c5~1, prima di L29e = 1cb233a
/usr/bin/python3 falsi/genera_falsi.py <repo>/circuits/preamp/preamp_audio.net <tmp>/main.net <abs>/falsi
/usr/bin/python3 falsi/regressione_L16.py <repo> <tmp>/radice_L16
/usr/bin/python3 ../L29e/falsi/genera_falsi.py <repo>/circuits/preamp/preamp_audio.net <tmp>/pre_L29e.net <tmp>/reg_L29e
/usr/bin/python3 falsi/regressione_L36.py <repo>/circuits/preamp/preamp_audio.net <tmp>/pre_L36.net
```

## I risultati in breve

- **2e**: la netlist vera passa; le 14 varianti e `main` falliscono, ciascuna per la ragione
  voluta (colonna `prima_riga` di `esito.csv`).
- **Regressione**: L16 cinque cadono e `scala_fuori_finestra` passa per progetto, come allora;
  L29e uguale; L36 le stesse ragioni. Due falsi non si applicano più, e ognuno ha la sua
  versione di oggi fra i 14.
- **ERC**: 47 avvisi, come a L36. Le parti nuove (J4–J7, SW3, R3) sono collegate per intero.
- **Deck V2** (`genera_tb_v2_casopeggiore.py`, matrice `sorgente`): byte-identico.
