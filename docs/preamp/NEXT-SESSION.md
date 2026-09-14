# Prompt per la sessione successiva — L32

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L32** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**Il lotto precedente ha chiuso NC-005 e NC-023**: il trim è nel progetto.

1. **ADR-027 — dove sta il trim.** È uno solo, **fra il blocco A e
   l'attenuatore**. Le uscite fisse prendono il segnale prima di lui e restano
   copia fedele della sorgente.
   - Scala **845 / 464 / 464 Ω**: −6,003 / −11,939 dB col carico
     dell'attenuatore.
   - Relè bistabili **G6KU-2F-Y**: K7 e K8 sul segnale, K9 e K10 per i LED.
   - Permissivo **K6** sul comando del mute.
2. **Perché lì.** All'ingresso del blocco A nessun partitore rispetta E3 ed E5
   insieme: 10,12 µV con la scala più piccola consentita, contro 9,90.
3. **Le misure, tutte conformi** (`data/2026-09-14/L16/dopo/`):

   | Grandezza | Valore |
   |---|---|
   | E3, min \|Zin\| | 121,1 kΩ con 68 pF, identica nelle tre posizioni |
   | E5, catena | ≤ 4,92 µV |
   | V1 blocco B, 0 dB, sorgente 2,611 k | **61,80°**, agli spigoli **61,42°** |
   | V1 blocco B, +3 dB | 69,77°, agli spigoli 68,64° |
   | V1 blocco B, +10 dB | 102,98° |
   | V1 blocco A col partitore | 63,50° |

4. **NC-009, una cifra.** Metrica **M1** (limite lineare all'1 % contro il
   richiesto col guadagno e il trim misurati): **+6,58 dB** a +10 dB col trim a
   −6 dB, +0,58 dB a 0 dB. Le altre due, etichettate:
   - M2 (ADR-015): +6,79 / +0,79 dB;
   - M3 (dossier): +6,55 / +0,55 dB.

   Pubblicarla è di **questo** lotto.

Voci: **15 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

**Perché questo lotto viene adesso.** Il dossier è l'unico artefatto che l'utente
legge per giudicare il progetto, e oggi racconta un altro circuito:
`build_dossier.py` legge ancora `data/2026-09-09` (THAT320, C_f 22 pF, due soli
guadagni). L'utente ha deciso di rifarlo subito dopo L16, sui dati di L27 e L16.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: le voci di diario di L16 e L27, «Prossimo passo
   concreto» e la riga L32 della tabella dei lotti.
3. **`docs/preamp/dossier/build_dossier.py`**, intero.
   - Oggi conosce solo `0db` e `10db` (`AC_ORDER`, `LOOP_ORDER`, `PSRR_ORDER`,
     l'headroom).
   - Guarda da dove legge ogni numero.
4. **`docs/preamp/data/2026-09-14/L27/README.md`** e
   **`docs/preamp/data/2026-09-14/L16/README.md`**: quali deck, quali file, in
   quale modo.
5. **`docs/preamp/NONCOMPLIANCE.md`**: NC-009 (la metà del dossier), NC-004 e
   NC-017 (la provenienza dei modelli da scrivere accanto ai numeri).
6. **Le ADR**:
   - **ADR-024**: V1 al minimo della spazzata, sonda al jack, blocco A ≤ 1 nF;
   - **ADR-026**: tre modi di guadagno;
   - **ADR-027**: il trim.
7. **`docs/preamp/REQUIREMENTS.md`**: V1 (soglia 60°, stato), E3, E5 e le quote.
8. **`docs/limitations.md` #10, #25, #26**: nomi `wrdata`, tabelle `echo` e `meas`
   vuote.

## IL LOTTO: L32 — il dossier rigenerato sui dati di oggi

### Cosa fare

1. **Punta il dossier ai dati vigenti**:
   - `data/2026-09-14/L27/dopo/` per risposta, E4, PSRR, E5 del blocco, P7,
     V2 e V3;
   - `data/2026-09-14/L16/dopo/` per il trim, E3, E5 della catena, V1 con il
     trim e l'headroom.

   Nessun numero da `data/2026-09-09`.
2. **Tre modi di guadagno** (0 / +3 / +10 dB) ovunque il dossier ne mostrava
   due.
3. **V1 come la vuole ADR-024.** Il margine è il **minimo della spazzata** al
   jack, non il valore a 4,7 nF; il blocco A col cablaggio ≤ 1 nF. La KPI è
   riferita a **60°** (il residuo di L19).
4. **NC-009**: pubblica **una** cifra di headroom, **M1 +6,58 dB** col trim a
   −6 dB. Dì quale metrica usa, ed etichetta le altre due (o toglile). Rifalla
   dai CSV con `data/2026-09-14/L16/esplorazione/script/headroom_nc009.py`, non
   copiarla da qui.
5. **Il trim entra nel dossier**: E3 nelle tre posizioni ed E5 della catena.
6. **Provenienza accanto a ogni numero**: quali modelli sono ancora segnaposto
   (NC-004, NC-017). Nessuna cifra di THD come se fosse vera.
7. **Rigenera** e controlla che ogni numero stampato torni dal CSV da cui dice
   di venire.

### I vincoli

- **Nessun avviso di obsolescenza**: il dossier lo legge solo l'utente, deciso il
  2026-09-14.
- **Il dossier impagina dati, non ne produce.** Se un numero manca, lo si misura
  con un deck versionato, non lo si stima.
- **Un controllo mai fatto fallire non è un controllo**: se aggiungi asserzioni,
  falle cadere una volta.

## Cosa NON accettare

- **Un margine di fase letto a 4,7 nF** invece che come minimo della spazzata.
- **Un numero dai dati del 2026-09-09.**
- **Una cifra di headroom senza metrica**, o tre cifre senza dire quale è quale.
- **Una `meas` il cui risultato non si è controllato nel log** (#26).
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.
- **Una netlist o uno schematico modificati a mano.**

## NON fa parte di questo lotto

- **NC-030 (L31)**, **NC-028 (L29**, aspetta una soglia dell'utente su V2),
  **NC-029 (L30)**, **NC-027 (L28)**.
- **Il selettore d'ingresso**, l'alimentatore, `VRELAY`.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri qui sopra.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in comandi
  composti.
  - `git` dentro un `python -c` viene rifiutato: esporta prima con `git show`
    su un file;
  - anche `python` con un heredoc e `awk` con un programma inline vengono
    rifiutati: scrivi lo script su file e lancialo;
  - un ciclo di shell con modificatori di variabile (`${f:t}`) o un comando
    con valori calcolati in posizione di opzione viene rifiutato: scrivi uno
    script su file.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L32, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L32`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
