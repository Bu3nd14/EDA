# Prompt per la sessione successiva — L17

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L17** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato con L11

**L11 ha chiuso NC-001 senza toccare il circuito.** Ha registrato:
- **ADR-021**: mute tenibile a tempo indefinito; ogni uscita regge un corto,
  requisito **P7**; classe B ammessa **solo** a mute inserito e in corto;
- **ADR-022**: operazionali e microcontrollore fuori dal percorso del segnale,
  con una definizione verificabile di percorso.

Poi ha misurato mute e corto su tutte e tre le uscite
(`spice/preamp/tb/tb_mute_corto.cir`, `docs/preamp/data/2026-09-14/`). La
topologia di oggi **passa** il criterio termico senza protezione e senza
dissipatore:
- MJE peggiore 484 mW, Tj 90,2 °C a 60 °C ambiente;
- limite Tj ≤ 125 °C, deciso dall'utente.

Tre cose di L11 ti riguardano:

1. **Il corto su una fissa è conforme.** NC-010 non è più «il corto», è
   l'**apparecchio spento**: una Zin bassa ma non nulla a valle porta il
   blocco A in classe B fuori dalle condizioni di ADR-021, e questo è T1.
2. **Il caso peggiore del blocco A è il mute**, che mette a massa entrambe
   le fisse insieme. Un buffer sulle fisse cambia anche quello.
3. **NC-028**, nuova: il rilascio del mute con segnale porta sul jack un
   gradino (5,37 V a +10 dB, τ 0,32 s; 1,72 V e 46 ms sulle fisse). Non è di
   L17, ma se il suo rimedio sarà un mute in serie cambia il cablaggio delle
   uscite che L17 tocca.

Voci: **19 aperte, 5 bloccanti**: NC-002 e NC-021 (L12), NC-004, NC-010
(L17), NC-017 (Fase 4).

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, regola di chiusura.
2. **`docs/preamp/STATE.md`**: la voce di diario di L11 e **«Prossimo passo
   concreto»**.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-010** con l'aggiornamento del
   2026-09-14, **NC-002** (blocco A a 41,98°) e **NC-028**.
4. **Le ADR:**
   - **ADR-008** (buffer unico; il suo «Da riaprire se» è scattato);
   - **ADR-006** (un solo blocco);
   - **ADR-021**, **ADR-022**, **ADR-003**.
5. **`REQUIREMENTS.md`**: T1 (definizione ed eccezione), P7 con la sua nota,
   E4, E5.
6. **`reports/2026-09-14-L11-mute-e-corto.md`**: come si è misurato, e le tre
   prove che il deck non passa sempre.
7. **`circuits/preamp/preamp_audio.py`**: le fisse (righe 136-172), le liste
   `k_mute`, il cablaggio del mute.

## IL LOTTO: L17 — le uscite fisse con un apparecchio spento a valle

**Il difetto.** Il blocco A pilota le due fisse e l'attenuatore dallo stesso
nodo, che è anche il nodo di controreazione. Un apparecchio spento con Zin
bassa su una fissa porta lo stadio in classe B. Da `tb_blockA_carichi`,
rieseguito da L11 sulla topologia di oggi:

| Impedenza a valle | I_C(Q132) min |
|---|---|
| 100 Ω | 2,40 mA |
| 10 Ω | −0,23 µA |

### Cosa fare

1. **Chiedere all'utente quale strada**, prima di progettare. È una scelta di
   prodotto su T1:
   - **(a) un'ADR** che estenda l'eccezione di ADR-021 all'apparecchio spento
     a valle. La termica è già provata: il corto è il caso peggiore ed è
     conforme. Costo: una frase di T1, nessun componente;
   - **(b) buffer sulle fisse**, con un'ADR che superi ADR-008. Costo: un
     secondo stadio discreto per uscita, o per coppia di uscite, da
     progettare, validare e misurare.

   Presenta i numeri di entrambe, non una raccomandazione travestita.
2. **Se (a):**
   - l'ADR col verbo (quale Zin a valle, quale condizione);
   - T1 aggiornato in `REQUIREMENTS.md`;
   - la dimostrazione termica, citando `data/2026-09-14/`, **ricontrollata**
     e non ricopiata;
   - NC-010 chiusa.
3. **Se (b):**
   - la topologia in `circuits/preamp/preamp_audio.py`, con commenti che
     puntano all'ADR;
   - la netlist rigenerata e il guardiano 2e verde, **dopo averlo fatto
     fallire**;
   - `tb_blockA_carichi.cir` e `tb_mute_corto.cir` estesi ai buffer;
   - il margine di fase del blocco A col carico nuovo, perché L12 parte da lì;
   - E4 ed E5 sulle fisse nuove.

### I vincoli

- **T3 / ADR-006**: un buffer diverso dal `GAINBLOCK` è un secondo progetto.
  Dillo.
- **T1 / ADR-022**: nessun integrato nel percorso del segnale.
- **T7 / T8**: modello del costruttore, nessuna parte a fine vita.
- **P7 / ADR-021**: le uscite nuove reggono corto e mute, a regime e nel
  transitorio.
- **E5**: al circuito restano 9,90 µV (ADR-020 e ADR-022 ne riservano 1 + 1).

## Cosa NON accettare

- **Una cifra di `data/2026-09-09` usata senza dire che è del THAT320.** Le
  fisse sono state rimisurate il 2026-09-14.
- **Un nome di dispositivo copiato da un log vecchio.** `@q134` di G0 non
  esiste più: le MJE sono Q132/Q133.
- **Un deck che esce 0 e che nessuno ha provato a far fallire.**
- **Un'ADR riscritta**, o un'aggiunta in coda a una ADR esistente: ADR-008 si
  supera con una ADR nuova.
- **Una netlist o uno schematico modificati a mano.**
- **Una scelta fra (a) e (b) fatta senza l'utente.**

## NON fa parte di questo lotto

- **Il margine di fase come rimedio (L12)**, anche se L17 lo misura.
- **NC-028 e il suo rimedio (L29).**
- **Il trim (L16)**, il terzo guadagno (L27), l'alimentatore, il dossier.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri di L11 qui sopra.
- **Un controllo mai fatto fallire non è un controllo.**
- **Niente cifre non eseguite.**
- **Un lotto per volta, mai due agenti in parallelo.**
- **Lavora in un worktree.** Gli script zsh si lanciano da soli, non in
  comandi composti. Anche `git` dentro un `python -c` viene rifiutato: esporta
  prima con `git show` su un file.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo;
2. **riscrivi QUESTO file per il lotto successivo**: se il titolo nomina
   ancora L17, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L17`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
