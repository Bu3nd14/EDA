# Prompt per la sessione successiva — L29c (il caso peggiore di V2 col mute reale)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è
organizzato in LOTTI PICCOLI: questa sessione fa **L29c** e si ferma. Non iniziarne un
secondo.

## Da dove si parte

L29b2 ha chiuso il mute graduale a monte **nel sorgente** e ha cambiato il criterio del
taglio, per scelta dell'utente.
- **Il criterio (ADR-040).** Il taglio con musica si giudica su **S, il salto di
  livello: ≤ 20 dB in 100 ms**, contato sopra −70 dB. Il dato è dell'utente: il
  pseudo-mute del Technics cala di 20 dB di colpo e non gli ha mai dato fastidio.
  **C2 è diagnostica**: si calcola e si riporta, non decide. A e B restano a 100 µV,
  A senza segnale. Lo strumento è `scripts/v2_metodo.py`, righe `S_ins` e `S_rel`.
- **Il profilo del comando dei LED è la v4** (ADR-039, ADR-040). Serie: 20 mA → 0,2 mA
  (d 0–0,1) → 4,5 µA (0,45) → **0,19 µA (0,75)** → 10 nA (0,8). Derivazione: 10 nA →
  20 mA log-lineare su d 0,5–1. Td = 6 s, 10 nA di riposo, relè 0,5 s dopo d = 1. Il
  contratto sta accanto a J3 in `circuits/preamp/preamp_audio.py`.
- **Il deck versionato** `spice/preamp/tb/tb_v2_mute_ldr.cir` è **generato** da
  `docs/preamp/data/2026-09-22/L29b2/deck/genera_tb_v2_mute_ldr.py`. Non si edita a
  mano. Si divide con `data/2026-09-22/L29b2/pavimento/dividi.py` e si corre in
  parallelo.
- **Cosa è misurato con la v4** (modello comportamentale dal datasheet, con
  estrapolazione dichiarata): S ≤ 7,2 dB a 20 Hz e 1 kHz su tre uscite e due carichi;
  20 kHz a 100 kΩ nel report di L29b2; A ≤ 3,9 µV, B2 ≤ 10 µV; E3 ≥ 111,6 kΩ,
  E5 ≤ 4,957 µV.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`**, **`docs/limitations.md`**, in particolare **#30** (`set numdgt=15`
   prima di ogni `wrdata`) e **#31** (`pwl()` estrapola).
2. **`docs/preamp/STATE.md`**: la voce L29b2 del diario e le righe L29c e L36.
3. **`docs/preamp/reports/2026-09-22-L29b2-mute-ldr-sorgente.md`** per intero.
4. **ADR-040**, **ADR-041**, **ADR-039**, **ADR-038**; poi ADR-030 (criterio 3), ADR-032, ADR-035,
   ADR-036.
5. **`docs/preamp/REQUIREMENTS.md`**: V2 per intero, col caso peggiore.
6. **`docs/preamp/NONCOMPLIANCE.md`**: NC-028, l'aggiornamento del 2026-09-22.

## IL LAVORO

Il caso peggiore di V2, col mute reale (le LDR della v4 più il relè al jack), dal
testo di V2:
1. **I passaggi di guadagno** 0↔+3, +3↔+10, 0↔+10 dB nei due versi, **sotto mute**,
   seguiti dal rilascio. Guadagno e trim si cambiano solo col jack a massa (ADR-038), e
   la forma è decisa: **interblocco da premere come il trim**, niente mute automatico,
   LED anche per il guadagno (ADR-041). L36 la realizza dopo L29c.
   È il **criterio 3 di ADR-030**, da cui dipende **L36**: il cambio sotto mute e il
   rilascio devono dare A e S nei limiti.
2. **Il trim** nelle tre posizioni, con lo stesso schema.
3. **La dispersione dell'LSK489** fino a ±20 mV, in più posizioni dell'attenuatore.
4. **Mute breve e mute di almeno 2 s**. Il rilascio dopo un mute lungo parte dalla
   serie più buia.
5. **Accensione e spegnimento** con le rampe dei rail (A contro il regime, sorgente a
   zero).
6. **Le celle A–D** del modello della LDR: la dispersione delle parti, per canale.

Poi l'esito: **NC-028 si chiude** se A, B e S reggono in tutta la matrice; altrimenti
resta aperta con le celle che cadono. Report datato.

**Se non entra in una sessione, dividi** in `STATE.md` e chiudine una parte.

## I vincoli

- **I tempi veri a 20 kHz.** Una corsa di 17,5 s con TMAX 0,5 µs vale **8–15 ore**, non
  2: il ritmo dei primi minuti inganna. Pianificale prima, e parlane con l'utente se
  servono. RAM: ~0,5 GB l'una a un quarto della corsa, e cresce coi punti salvati (stima ~2 GB a
  fine corsa); con 24 GB, 7 in parallelo su 10 core hanno retto.
- **`set numdgt=15`** in ogni deck che scrive forme d'onda da sottrarre (#30).
- **Il pavimento di C2 si misura e si riporta** anche se C2 è diagnostica.
- **Ogni cifra sulla LDR** porta «modello comportamentale dal datasheet, con
  estrapolazione dichiarata».
- **Trappole già pagate:**
  - un LED senza percorso DC fa fallire l'op in silenzio (il 10 M del banco);
  - col trapezio un gradino sul LED fa oscillare la cella: i comandi sono log-lineari;
  - `analizza` accetta eventi solo per t > 0,3 s;
  - `awk` col locale italiano non legge i `.dat`: si usa Python;
  - **`pkill -f` sul nome di uno script zsh prende anche i suoi subshell**;
  - **`pgrep` con `\|` non vuol dire «oppure»**: controlla i processi con `ps`.
- **Nessun cambio di tecnica o di criterio senza l'utente.**
- Gli script zsh si lanciano da soli. `git` e i comandi con variabili di shell composte
  vengono rifiutati nel worktree: comandi semplici e separati, script su file. Scipy non
  c'è; numpy c'è nel venv 3.13.

## NON fa parte di questo lotto

- **L36** (la forma dell'interblocco del guadagno), L35, L28, L30, il dossier.
- Rifare i deck di L29a con `numdgt=15`.
- I file in `vendor/` non si toccano.

## CHIUSURA

1. `STATE.md` con L29c **fatto** e il successivo come prossimo.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L29c`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
