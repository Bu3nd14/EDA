# Prompt per la sessione successiva — L29c (il caso peggiore di V2 col mute reale)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è
organizzato in LOTTI PICCOLI: questa sessione fa **L29c** e si ferma. Non iniziarne un
secondo.

## Perché adesso

**NC-028 è l'ultima bloccante di V2**: manca il caso peggiore. Era rimandato perché
dipendeva dai modelli e dalla compensazione, e ora sono fermi entrambi:
- **L39** ha messo i modelli del costruttore;
- **L40** ha chiuso V1 (NC-034) col **Miller da 1 nF** e tenuto la corrente di riposo
  d'uscita a **~20,3 mA** (**ADR-042**).

La topologia e il guadagno minimo (0 dB, E1) non sono cambiati.

## Da dove si parte

- **I modelli.** Ogni dispositivo attivo è il modello del costruttore di `models/`
  (LSK489A, MMBT5551, MMBT5401, LS350, Qmje15032, Qmje15033, D1N914). Solo l'LSK489A
  ha KF; nessun modello porta la dispersione. Le cifre di V2 portano quell'etichetta.
- **Il circuito di L40** (ADR-042): C124 1 nF, R128 1,69 kΩ. Cosa cambia per V2:
  - la banda a 0 dB scende a 912 kHz, a +10 dB a 113 kHz;
  - lo slew in discesa è −1,68 V/µs: **una sinusoide a 20 kHz e 12 V di picco
    comincia a entrare in slew**, con +0,57 V di continua dietro lo stadio;
  - il recupero di V3 passa da 1,07 a 3,03 µs.

  Le corse a 20 kHz a fondo scala vanno lette sapendolo: un gradino o un residuo che
  compare solo lì può essere lo slew, non il mute.
- **La cella di riferimento di L40** (1 kHz, 100 k, principale, `data/2026-09-23/L40/`,
  `prima/` = 470 p, `dopo/` = 1 nF): S 7,163 / 5,32 dB (invariato), A senza segnale ≤ 3,75 µV, B2 0,33 µV; il fondo di distorsione della catena C_pav sale da 0,27 a **0,34 mV** (diagnostica). Rimisurare questa cella prima della matrice resta il primo controllo.
- **L'offset del blocco B** (criterio 3 di ADR-030): −15,45 mV, invariato da L40.
- **Il criterio (ADR-040).** Il taglio con musica si giudica su **S, il salto di
  livello: ≤ 20 dB in 100 ms**, contato sopra −70 dB. **C2 è diagnostica.** A e B
  restano a 100 µV, A senza segnale. Strumento: `scripts/v2_metodo.py`, righe `S_ins`
  e `S_rel`.
- **Il profilo del comando dei LED è la v4** (ADR-039, ADR-040). Td = 6 s, 10 nA di
  riposo, relè 0,5 s dopo d = 1.
- **Il guadagno si interblocca col mute come il trim** (ADR-041). L36 lo realizza,
  dopo questo lotto.
- **Il deck versionato** `spice/preamp/tb/tb_v2_mute_ldr.cir` è **generato** da
  `data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py`, e si divide con
  `data/2026-09-22/L29b2/pavimento/dividi.py`. Per una sola cella c'è
  `data/2026-09-23/L40/script/v2_cella.sh <fase>`.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**, in particolare #10, #22, #24, #26,
   #29, #30, #31 e **#32** (un corpo di `if` vuoto fa uscire ngspice con 139).
2. **`docs/preamp/STATE.md`**: le voci L40, L29b2 e L29b del diario, le righe L29c e
   L36.
3. **`reports/2026-09-22-L29b2-mute-ldr-sorgente.md`** (§8, i tempi delle corse) e
   **`reports/2026-09-23-L40-v1-costruttore.md`** (§5).
4. **ADR-030** (i tre criteri, il 3 in particolare), **ADR-035/036** (il metodo),
   **ADR-038/039/040** (il mute LDR e il criterio S), **ADR-041**, **ADR-042**.
5. **`NONCOMPLIANCE.md`**: NC-028 per intero.

## IL LAVORO, in ordine

Il caso peggiore di V2 col mute reale (LDR v4 più il relè al jack). **Prima della
matrice, pianifica le corse**: a 20 kHz con TMAX 0,5 µs valgono ore l'una. In L29b2
erano circa 4 ore, con 7 in parallelo su 10 core; in L39–L40 le corse a 1 kHz sono
durate 2,5–7 minuti l'una, 11 in parallelo. Scrivi il piano in `STATE.md` prima di
lanciare.

1. **I passaggi di guadagno**, 0↔+3, +3↔+10 e 0↔+10 dB nei due versi, **sotto mute**
   e seguiti dal rilascio. È il **criterio 3 di ADR-030**, da cui dipende L36. A e S
   devono stare nei limiti.
2. **Il trim** nelle tre posizioni, con lo stesso schema.
3. **La dispersione dell'LSK489** fino a ±20 mV di offset, in più posizioni
   dell'attenuatore. Il gruppo B si fa con `altermod` e sonda (limitations #29), come
   `tb_idss_*.cir` e `data/2026-09-23/L40/script/idss_istanze.py`.
4. **Mute breve e mute di almeno 2 s.**
5. **Accensione e spegnimento**, con le rampe dei rail.
6. **Le curve A–D** del modello della LDR: la dispersione delle parti, per canale.

**Esito**: NC-028 si chiude se A, B e S reggono in tutta la matrice. Report datato.

**Se non entra in una sessione, dividi**: prima 1 e 4, cioè ciò da cui dipende L36;
poi il resto. Scrivilo in `STATE.md`.

## I vincoli

- **Nessun cambio di topologia né di valore senza l'utente.**
- `set numdgt=15` prima di ogni `wrdata` (limitations #30); `pwl()` estrapola (#31).
- **Il manifesto non è l'elenco delle corse** (L39): `rele_*` rilegge i dati di `ev`,
  `pav_*` quelli di `evp`/`invp`. Una cella si estrae dalla colonna `file`.
- **I tempi degli strumenti.**
  - Un LED senza percorso DC fa fallire l'op in silenzio.
  - I comandi dei LED sono log-lineari.
  - `analizza` accetta eventi solo per t > 0,3 s, e su 11 corse a 1 kHz impiega
    decine di minuti.
  - `awk` col locale italiano non legge i `.dat`.
- `pkill -f` sul nome di uno script zsh prende anche i suoi subshell; `pgrep` con `\|`
  non vuol dire «oppure».
- Gli script zsh si lanciano da soli. `git` e i comandi con costrutti composti
  (`$(...)`, `cd … &&`, `for` con variabili, heredoc passati a comandi) vengono
  rifiutati nel worktree: comandi semplici e separati, script su file. Scipy non c'è;
  numpy c'è nel venv 3.13.
- Le forme d'onda rigenerabili (i `.dat` da ~400 MB) **non si committano**. Tieni
  riassunti e analisi.

## NON fa parte di questo lotto

- **L36** (viene dopo, e dipende dal punto 1), L35, L28, L30, il dossier.
- Ritoccare la compensazione: se lo slew a 20 kHz rende una cella fuori soglia, lo
  si scrive e si chiede all'utente (ADR-042, «Da riaprire se»).

## CHIUSURA

1. `STATE.md` con L29c **fatto** (o diviso) e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L29c`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
