# Prompt per la sessione successiva — L44 (il rumore 1/f fuori dalla coppia d'ingresso)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L44**, e si ferma. Non iniziarne un secondo.

## Perché questo lotto, e perché adesso

L'ordine dei rimedi scelto dall'utente il 2026-10-01 è **L46 → L44 → L47 → L48 → L49 → G1 → L45 →
L50**. L46 è chiuso: **L46a** (ADR-054, la compensazione) e **L46b** (ADR-056, la cella RC 10 Ω +
1000 µF su specchio e VAS, e R120 226 Ω). Il blocco su cui misurare è quello di ADR-056.

- **NC-004 (bloccante per G1)**: E5 e V4 senza evidenza piena. Dopo L39 tutti i dispositivi sono
  modelli del costruttore, ma **solo l'LSK489A porta KF**: specchio (LS352), VAS e pozzo
  (MMBT5401/5551), moltiplicatore di Vbe, MJE sono senza flicker. E5 oggi: **5,08 µV** peggiore
  (`tb_e3_e5_ldr.cir`, +10 dB, 430 Ω), 4,30 µV in `tb_noise_breakdown.cir`, contro 9,95 µV di
  budget del circuito (ADR-020 ne riserva 1 all'alimentazione): un **pavimento**, non una cifra.
- I contributori dominanti, da L22 in poi, sono lo **specchio** e le sue degenerazioni (220 /
  226 Ω), non i JFET: se il loro 1/f è grande, E5 può muoversi molto sotto 1 kHz.
- La cella di ADR-056 non aggiunge rumore visibile (il 10 Ω è shuntato dai 1000 µF), ma alimenta
  proprio specchio e VAS: un 1/f su quel nodo ora è filtrato, uno nei dispositivi no.

## Il mandato

1. **All'inizio, con l'utente** (le domande **per nome**, mai per sigle: «non ricordo sigle a
   memoria»; i livelli di rumore in **dB SPL** contro una stanza silenziosa, non in µV): **il modo**
   di dare il 1/f ai dispositivi che non ce l'hanno. Le strade, da mettere in tabella con quello che
   costano e quanto valgono come evidenza:
   - **KF/AF ricavati dai datasheet** (curve di rumore in funzione della frequenza, dove ci sono:
     LS352/LS350, MMBT5401/5551 e famiglie 2N5401/2N5551, MJE15032/33), con la provenienza scritta
     come per gli altri modelli (`validate_models.py`, ricette);
   - **un limite per eccesso dichiarato** (un angolo 1/f pessimista per classe di dispositivo),
     se i datasheet non bastano;
   - **la misura sul prototipo**, lasciando NC-004 aperta fino a lì (e allora G1 resta bloccato:
     chiederlo esplicitamente).
   La scelta è dell'utente; se cambia l'insieme dei progetti conformi o il modo di verificare E5,
   diventa una **ADR**.
2. **E5 rimisurato** col 1/f: `tb_e3_e5_ldr.cir` e `tb_noise_breakdown.cir` (e `tb_noise_vectors`
   per dispositivo), sul banco di L46b (`data/2026-10-01/L46b/script/`, README dentro: famiglia
   `psrr` = `tb_zout_psrr_noise` + `tb_noise_breakdown`; il controllo `ctrl` deve ridare L46b).
   Il breakdown per dispositivo a 100 Hz e 1 kHz dice chi domina.
3. **Se E5 non regge** (> 9,95 µV, o margine che l'utente giudica sottile): le leve vanno misurate
   e portate all'utente in tabella, non scelte da soli (degenerazione dello specchio, dispositivo
   dello specchio, corrente). Una modifica al blocco **ricorre anche le catene a valle** (la lezione
   di L46b, report §8): i 21 deck con `script/regressione.sh`, e la catena dei guasti di L41c coi
   comandi in `data/2026-10-01/L46b/README.md`.
4. **Tracciabilità**: ogni valore nuovo in `circuits/preamp/*.py` o in `models/` col commento che
   punta alla ADR o al lotto; provenienza dei modelli aggiornata e `validate_models.py
   --check-provenance` pulito.

## Prima di tutto

- `CLAUDE.md`, `docs/limitations.md` (le trappole che falliscono in silenzio: #22 rinumerazione, #24
  nodi del blocco, #33/#38 il «transient op», #37 le Note dentro le tabelle), e in
  `docs/preamp/STATE.md` «In breve» e le voci di diario di L46b, L46a, L39, L22.
- `NONCOMPLIANCE.md`: **NC-004** (tutta, con gli aggiornamenti di L24, L20, L39), NC-020 (f_T
  dell'LS352), NC-024/NC-025 (i MJE).
- `decisions/ADR-020*` (la quota e il budget di 9,95 µV), `decisions/ADR-056*`, il report
  `reports/2026-10-01-L46b-psrr-rail-positivo.md`.
- I `*.provenance.json` accanto ai modelli in `models/` e le ricette in
  `scripts/validate_models.py`: come entra un modello con provenienza (l'ultimo esempio sono i
  ZXT di L46a).

## I vincoli

- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script (anche
    `run_tests.sh` va lanciato da solo, senza redirezioni);
  - `awk` con programmi, i cicli con variabili e i percorsi calcolati a runtime;
  - gli heredoc;
  - un titolo di PR con l'apostrofo (`gh pr create`): il corpo va su file (`--body-file`).

  Si usano comandi semplici, **percorsi assoluti**, script scritti su file con Write, ed Edit per
  i testi. Il venv non è nel worktree: `/Users/roberto/EDA/env/venv/bin/python3`.
- Le cifre dai modelli sono cifre di modello: conta il trend, non il valore assoluto.
- Un deck con `tran` dopo un `alter` va guardato nel log: «Transient op started» invalida la corsa
  (#33, #38).
- `docs/preamp/data/` è versionato per regola (`!docs/preamp/data/**`): forme d'onda grosse vanno
  in `.gitignore` prima del commit (L46b ne ha escluse ~6,3 GB).

## NON fa parte di questo lotto

- la cella del mute, la VTL5C4 e S del mute (L47, che ricorre anche V2 del mute, non rieseguito né
  in L46a né in L46b); il selettore d'ingresso e la continua del blocco A (L48: con R120 226 Ω è
  −6,6 mV nominale, ma la dispersione resta); il placement e routing di prova (L49); la FMEA (L45);
  massa e terra (L50);
- la compensazione (ADR-054) e la cella (ADR-056): decise;
- rigenerare il dossier.

## CHIUSURA

1. `STATE.md` con L44 **fatto** e il prossimo lotto (L47) nella tabella.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L44`.
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
