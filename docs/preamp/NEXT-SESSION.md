# Prompt per la sessione successiva — L16

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L16** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**L27 ha chiuso NC-022**: il blocco B ha i tre guadagni di ADR-019.

1. **ADR-026 — la rete.** Due rami di R_g **in parallelo** verso massa:
   - **3,57 kΩ su K1** → +3,047 dB;
   - **866 Ω su K5**, chiuso solo con K1 → +9,972 dB.

   Nessuno stato dei contatti supera il +10 dB. K5 è un secondo G6K-2F-Y: le
   bobine, cinque eccitate, fanno **105,5 mA a 5 V**.
2. **V1 sul blocco B**, minimo della spazzata (ADR-024):

   | Blocco B | Minimo | Agli spigoli |
   |---|---|---|
   | 0 dB | 61,83° | 61,45° |
   | +3 dB | 69,79° | 68,67° |
   | +10 dB | 102,99° | — |

3. **Limitazione #27**: un nodo di contatto non terminato non dà errore. Un deck
   vecchio sull'include nuovo stampava +3 dB nel modo che chiama 10db. Il blocco
   **2g** ora lo rifiuta.
4. **NC-030** (minore, L31): `tb_noise_vectors.cir` non scrive dati.

Voci: **17 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

**Perché questo lotto viene adesso.** Le **tre posizioni del trim** sono l'ultima
riga di V1 senza misura. Il trim porta tre voci insieme:
- **NC-009**: l'headroom a +10 dB col K11 a fondo scala poggia su un trim che
  non esiste;
- **NC-005**: E3 va misurata al connettore in ogni posizione;
- **NC-023**: l'interlock elettrico col mute di ADR-019.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: la voce di diario di L27 e «Prossimo passo
   concreto».
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-005**, **NC-009** (le tre cifre di
   margine), **NC-023**, e la storia di **NC-014** (il contatto sbagliato del
   G6K-2F-Y).
4. **Le ADR:**
   - **ADR-011** col suo aggiornamento, **ADR-015**;
   - **ADR-019** §2 (il permissivo), **ADR-012** e **ADR-021** (i relè di mute
     riposano **in** mute);
   - **ADR-022** (se il comando passa da una logica), **ADR-026** (il budget
     delle bobine cresce);
   - **ADR-024** (il blocco A col suo cablaggio ≤ 1 nF).
5. **`REQUIREMENTS.md`**: **F2** contro **F8** (ponticello contro relè), E3 e la
   «Nota su E3», E5, E6, V1.
6. **`circuits/preamp/preamp_audio.py`**: la docstring dichiara selettore e trim
   **fuori** dal perimetro, e il cablaggio dei relè di mute.
7. **`scripts/check_relay_safe_state.py`**: i ruoli sono MUTE e GAIN, non TRIM.
8. **`docs/limitations.md` #22, #24, #27**.

## IL LOTTO: L16 — il trim entra nel progetto

### Cosa fare

1. **F2 contro F8, prima di disegnare.** F2 dice «a ponticello», F8 e ADR-019
   presuppongono relè comandati.
   - Allineare F2 è una modifica sostanziale solo se cambia l'insieme dei
     progetti conformi (il criterio di L15);
   - **«per ingresso»** di ADR-011 vuol dire 4 ingressi × 2 canali × 3
     posizioni: conta i relè e le bobine prima di sceglierlo;
   - **un trim solo dopo il selettore** cambierebbe ADR-011: è una decisione
     dell'utente, con una ADR sua.
2. **Il dimensionamento, coi due vincoli insieme:**
   - **attenuazione**: 0 / −6 / −12 dB, con −6 dB portante per il +10 dB
     (ADR-015);
   - **Zin**: minimo di |Zin| su 20 Hz–20 kHz ≥ 100 kΩ al connettore, `R_IN`
     compresa, in tutte e tre le posizioni.
3. **L'interlock (NC-023).** L'alimentazione delle bobine del trim passa per un
   contatto chiuso **in** mute. I poli dei relè di mute sono tutti occupati dal
   segnale: il contatto va trovato o aggiunto, e va aggiunto il ruolo al
   guardiano 2e.
   - **Provalo sulla netlist**: a mute rilasciato il comando del trim non deve
     raggiungere nessuna bobina;
   - **fallo fallire** col contatto sbagliato.
4. **Le misure, con un deck versionato:**
   - Zin AC nelle tre posizioni;
   - rumore (E5) del partitore visto dal blocco A, nei tre modi del blocco B;
   - V1 del blocco A con la sorgente del trim: tre posizioni, cablaggio ≤ 1 nF,
     minimo della spazzata;
   - l'headroom di NC-009 con **una** metrica dichiarata.
5. **Le tre cifre di margine di NC-009**: una sola pubblicata, con la sua
   metrica, e le altre etichettate.

### I vincoli

- **E3 / Nota su E3**: minimo sulla banda, non il valore a 1 kHz.
- **ADR-019**: 60° al minimo della spazzata; il trim funziona solo a mute
  inserito.
- **ADR-012 / ADR-021**: i relè di mute riposano in mute.
- **ADR-022**: niente integrati nel percorso del segnale.
- **E5**: 9,90 µV al circuito, il ripple ne ha 1 µV (ADR-020).
- **T3 / ADR-006**: un solo blocco. **T7 / T8** su ogni parte nuova.

## Cosa NON accettare

- **Una Zin letta a 1 kHz** invece che come minimo su 20 Hz–20 kHz, o
  **R1 + R2 = 100 kΩ** senza `R_IN` in parallelo: 50 k / 50 k fa 97,62 kΩ.
- **Un interlock mai fatto fallire**, o preso dal contatto che è chiuso a
  riposo: è la famiglia di NC-014.
- **Un deck che include `gain_block_flat.inc` senza terminare `RG` e `RG10`**
  (#27), o con un nodo che si chiama come un nodo del blocco (#24).
- **Una `meas` il cui risultato non si è controllato nel log** (#26).
- **Una cifra di rumore del partitore** calcolata e non simulata.
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.
- **Una netlist o uno schematico modificati a mano**, e un `git diff` su un
  `.net` letto come prova di topologia: serve il confronto semantico
  (`data/2026-09-14/L27/esplorazione/script/netcmp.py`).

## NON fa parte di questo lotto

- **Il selettore d'ingresso** oltre a ciò che il trim richiede.
- **NC-030 (L31)**, **NC-028 (L29)**, **NC-029 (L30)**, **NC-027 (L28)**.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri di L27 qui sopra.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in
  comandi composti.
  - `git` dentro un `python -c` viene rifiutato: esporta prima con `git show`
    su un file;
  - anche `python` con un heredoc e `awk` con un programma inline vengono
    rifiutati: scrivi lo script su file e lancialo.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L16, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L16`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
