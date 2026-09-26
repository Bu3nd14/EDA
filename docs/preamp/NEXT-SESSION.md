# Prompt per la sessione successiva — L41 (il circuito dell'alimentatore)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L41** e si ferma. Non iniziarne un secondo. **L41 è grande
(L) e quasi certamente si divide** (L41a, L41b…). La divisione si scrive nella tabella dei lotti
di `STATE.md` prima di chiudere.

## Il mandato

**NC-036** (bloccante per G2): l'alimentatore non esiste in `circuits/`, e P9 è verificato solo
con un alimentatore comportamentale. Il lotto porta nel sorgente il circuito che realizza **P9**
(ADR-046) e i contratti già scritti sulla scheda audio:
- **J1**: ±15 V e `VRELAY`, con la tenuta dei rail;
- **J3**: il comando delle LDR, profilo v4, Td = 6 s (ADR-039/040);
- **J4**: `MUTE_CMD`, `PERMIT_CMD`, SW3, Δ, i 13 ms di ADR-027 e il contratto di ADR-046.

Le parti, tutte fuori dal percorso del segnale:
1. **Trasformatore toroidale, raddrizzatore, regolatori ±15 V** (P3, P4), con la **tenuta dopo i
   regolatori ≥ 1500 µF effettivi per rail** (2200 µF nominali, −20 %). A 265 mA per rail il
   rail + deve impiegare ≥ 16 ms da 13,5 a 10,6 V.
2. **`VRELAY`** (175 mA a 5 V nel caso peggiore, L35; vincolo Schottky di L36), tenuta in
   tolleranza **≥ 25 ms** dallo scatto del sorvegliante.
3. **Il relè di rete e l'interruttore morbido**: l'interruttore è un ingresso del
   temporizzatore; diseccitato = rete staccata; il relè si rilascia ≥ 50 ms dopo il mute completo.
4. **Il sorvegliante**: rilascia `MUTE_CMD` entro 1 ms quando un rail scende sotto |13,5 V|,
   senza dissolvenza. Il comando è attivo-per-la-musica: senza alimentazione, mute.
5. **Il temporizzatore**: il profilo delle LDR, `MUTE_CMD` 0,5 s dopo d = 1, `PERMIT_CMD` Δ dopo
   (20 ms nominali, ≥ 10 ms), l'accensione (ADR-027), l'OR con SW3. Si alimenta dalla tenuta di
   `VRELAY`.

**La verifica**: il banco di L30 (`data/2026-09-26/L30/`, README) col circuito vero al posto delle
rampe PWL, col metodo di V2:
- lo spegnimento morbido sotto V2 (100 µV);
- la perdita di rete, un regolatore aperto, un rail solo e `VRELAY` persa sotto l'obiettivo di
  2 mV (tetto 0,87 V);
- il controfattuale senza Δ che fallisce.

## Prima di tutto

- **Dove sta l'alimentatore nel sorgente.** Un file nuovo, per esempio
  `circuits/preamp/psu.py`, con la sua netlist, sul secondo PCB (P4). È una scelta di struttura:
  **proponila all'utente prima di scriverla**.
- **Le scelte che toccano l'utente si chiedono conversando**, con i numeri davanti, non con un
  questionario:
  - la tensione di `VRELAY` (5, 12 o 24 V; il budget di L35 le ha tutte e tre);
  - la tecnica del sorvegliante (comparatore, supervisore integrato, discreto);
  - il trasformatore.
- **I bump si dicono in dB SPL di picco a 1 m contro il silenzio di una stanza**, non in mV.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**.
2. **`docs/preamp/STATE.md`**: la voce di diario di L30, e le righe L30 e L41.
3. **ADR-046** (spegnimento e failsafe), **ADR-047** (P5, il calore), **ADR-010** (alimentatore
   a bordo, P1–P5), **ADR-020** (il ripple ammesso), **ADR-027** (i 13 ms), **ADR-039** (il
   contratto delle LDR), **ADR-045** (Δ).
4. **Il report di L30** (`reports/2026-09-26-L30-spegnimento-failsafe-calore.md`) e il README
   dei suoi dati: come si genera e si corre il banco, e le guardie.
5. **`circuits/preamp/preamp_audio.py`**, i blocchi di J1, J3 e J4; **NC-036** in
   `NONCOMPLIANCE.md`; **P2** e **P9** in `REQUIREMENTS.md`.

## Quello che L30 ti consegna

- **Il banco** `data/2026-09-26/L30/deck/tb_v2_l30.cir`, generato con
  `genera_tb_v2_casopeggiore.py --matrice l30`. È da estendere perché accetti il circuito
  dell'alimentatore al posto delle PWL `@vpp` / `@vmm` / `@vpwl` e degli istanti dei contatti.
- **Le cifre di riferimento**:
  - spegnimento morbido ≤ 2,7 µV;
  - guasto ≤ 1,77 mV;
  - senza Δ 69 mV;
  - regolazione persa col rail + a ~10,6 V.
- **Le trappole**:
  - un'`alter` su un dispositivo che manca dà «no such device» ed exit 0: prima di fidarti di un
    giro, `grep -l 'no such device' corse/*.log` deve essere vuoto;
  - un contatto netto che commuta col blocco fuori regolazione ferma il JFET su «Timestep too
    small»: per K1/K5 c'è il gemello comportamentale;
  - SKiDL non dà nomi stabili alle net fuse: un diff di netlist si legge sulle connessioni.

## I vincoli

- **La scheda audio non si tocca.** Il deck V2 `spice/preamp/tb/tb_v2_casopeggiore.cir`
  rigenerato deve restare **byte-identico**. Se un contratto di J1, J3 o J4 non si può
  rispettare, si cambia con una ADR, all'utente.
- **Sicurezza di rete (P2)**: tutto ciò che tocca la rete va annotato per l'analisi di
  sicurezza. La sua assenza è un BLOCK automatico a G3.
- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - i cicli con variabili calcolate a runtime;
  - `awk -v`;
  - i `sed` con più `-e` o con `a\`;
  - i percorsi calcolati a runtime (anche `$CLAUDE_JOB_DIR` dentro un comando).

  Si usano comandi semplici, **percorsi assoluti**, script su file, ed Edit per i testi.

## NON fa parte di questo lotto

- **NC-004** (il rumore 1/f, bloccante per G1): è un altro lotto;
- **L28** (SS dell'LSK489, NC-027);
- il dossier;
- il layout dei PCB e il contenitore (G2).

## CHIUSURA

1. `STATE.md` con L41 (o la parte fatta) **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L41` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
