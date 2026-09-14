# Prompt per la sessione successiva — L12

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L12** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**Ha chiuso NC-010 cambiando il circuito.** L'utente ha deciso il principio,
registrato come **ADR-023**: la classe A si giudica sui **percorsi
ascoltabili**. Un'uscita mutata, in corto o con un apparecchio spento a bassa
Zin può portare in classe B solo lo stadio che serve lei.

**La topologia.** Ogni uscita fissa ha ora il proprio buffer: il `GAINBLOCK`
a guadagno unitario, quattro istanze in più. Ogni canale ha **quattro
blocchi**: A, i due buffer delle fisse, B. Dati in `docs/preamp/data/2026-09-14/L17/`.

Tre cose ti riguardano direttamente:

1. **Le istanze sotto i 60° sono aumentate.** Il buffer ha l'anello del
   vecchio blocco A. Con la sonda da 4,7 nF:

   | Istanza | Sonda sul nodo | Sonda al jack |
   |---|---|---|
   | Blocco A, carico nuovo | **40,96°** | — (niente jack: pilota l'attenuatore) |
   | Buffer delle fisse | **40,98°** | **62,27°**, minimo 61,74° a 2,2 nF |
   | Blocco B a 0 dB (NC-021, L22) | — | **56,46°** |

2. **Il margine del blocco A non dipende dalle fisse.** Col carico canonico
   di ADR-008, come controllo, dà 41,02°; col carico nuovo 40,96°. Lo decide
   la sonda sul nodo.
3. **Ogni valore che cambi in `gain_block.py` cambia otto istanze.** Ciò che
   L17 ha misurato va tenuto:
   - classe A sui percorsi ascoltabili (`tb_mute_corto`,
     `tb_blockA_carichi`);
   - P7;
   - E4 ed E5 sulle fisse.

Voci: **19 aperte, 4 bloccanti**: NC-002 e NC-021 (questo lotto), NC-004,
NC-017 (Fase 4). **NC-029**, maggiore, è il calore (L30): non è tua, ma una
compensazione che alzi le correnti la peggiora.

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, regola di chiusura.
2. **`docs/preamp/STATE.md`**: la voce di diario di L17 e **«Prossimo passo
   concreto»**.
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-002** con l'aggiornamento del
   2026-09-14, **NC-021**, **NC-020** (la f_T del modello LS352 sta sotto il
   datasheet: i margini sono pessimistici di quantità ignota) e **NC-025**.
4. **Le ADR:**
   - **ADR-019** (60° ovunque, caso capacitivo compreso);
   - **ADR-023**;
   - **ADR-006** (un solo blocco);
   - **ADR-014**, **ADR-004**.
5. **`REQUIREMENTS.md`**: V1 (la matrice e la soglia), E5 con le quote,
   T3, T1.
6. **`reports/2026-09-14-L17-buffer-uscite-fisse.md`**: come si sono misurati i
   margini, e i due errori di deck trovati prima di registrare i numeri.
7. **`circuits/preamp/gain_block.py`**: la compensazione (Miller C124, 470 pF;
   C137, 22 pF su R_f) e il commento di riepilogo in fondo.
8. **`docs/limitations.md` #24 e #25**: le trappole nuove dei deck.

## IL LOTTO: L12 — portare ogni istanza del blocco sopra i 60°

### Cosa fare

1. **Chiedere all'utente dove si applica la sonda da 4,7 nF**, prima di
   progettare. ADR-019 dice «ovunque, caso peggiore capacitivo compreso», ma
   non dice **in che punto**, e per il buffer la risposta vale 21°:
   - **sul nodo d'uscita**, prima dei 47 Ω: il margine di prova più severo.
     Oggi falliscono blocco A e buffer;
   - **al jack**, dove un cavo sta davvero: il buffer oggi passa. Per il
     blocco A il «jack» non esiste, e sul suo nodo c'è solo il cablaggio verso
     l'attenuatore sul pannello.

   Presenta i numeri di tutte e due, non una raccomandazione travestita. Se la
   risposta cambia il testo di V1, è una ADR.
2. **Poi il rimedio, scelto coi numeri** fra le strade di NC-002 e NC-021:
   - più compensazione;
   - meno guadagno d'anello;
   - una rete d'isolamento d'uscita diversa.

   Per ciascuna misura:
   - **il margine su ogni istanza**: blocco A, buffer, B a 0 e a +10 dB;
   - **le celle della matrice V1** che L17 non copre;
   - **E5**: resta **9,90 µV** al circuito;
   - **la PSRR**, perché i limiti per tono di ADR-020 si ricalcolano se cambia;
   - **il clipping e il recupero** (V3), e la risposta a 20 kHz.
3. **Se un rimedio vale per un ruolo e non per gli altri**, per esempio una
   compensazione diversa fra blocco A e blocco B, è **T3 / ADR-006**. Dillo, e
   decidi con l'utente.
4. **Consegna:**
   - valori in `gain_block.py`, con commenti che puntano all'ADR;
   - rigenerazione di `gain_block.net`, `.subckt`, `_flat.inc` e
     `preamp_audio.net`;
   - blocco 2d verde: `gain_block.svg` e il suo manifesto;
   - margini versionati con i deck `tb_loop`, `tb_loop_blockA`,
     `tb_loop_bufferfissa`;
   - la non regressione di ciò che L17 ha misurato.

### I vincoli

- **ADR-019**: 60° su ogni cella di V1, blocco A e buffer compresi.
- **ADR-023 / T1**: ogni percorso ascoltabile resta in classe A. Una
  polarizzazione diversa lo cambia.
- **P7 / ADR-021**: Tj ≤ 125 °C a 60 °C, a regime e nel transitorio.
- **T3 / ADR-006**: un solo blocco.
- **T7 / T8**: nessuna parte nuova senza modello del costruttore o a fine
  vita.
- **E5**: 9,90 µV al circuito.

## Cosa NON accettare

- **Una cifra di `data/2026-09-09` usata senza dire che è del THAT320.**
- **Un margine misurato in una sola posizione della sonda** senza dire quale.
- **Un deck che include `gain_block_flat.inc` con un nodo che si chiama come
  un nodo del blocco** (`SRC`, `OUT`, `FB`, `IN`…): è la limitazione #24, e
  L17 ci è caduto.
- **Una tabella `echo` con lo stesso nome della conversione di un `wrdata`**
  (limitazione #25).
- **Un deck che esce 0 e che nessuno ha provato a far fallire.**
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.
- **Una netlist o uno schematico modificati a mano.**

## NON fa parte di questo lotto

- **NC-029, il calore (L30).**
- **NC-028 e il suo rimedio (L29).**
- **Il trim (L16)**, il terzo guadagno (L27), l'alimentatore, il dossier.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri di L17 qui sopra.
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
   ancora L12, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L12`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
