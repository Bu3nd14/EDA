# Prompt per la sessione successiva — L30 (lo spegnimento, il failsafe e il calore del telaio)

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il lavoro è organizzato in
LOTTI PICCOLI: questa sessione fa **L30** e si ferma. Non iniziarne un secondo. **Se L30 non entra
in una sessione, si divide** (L30a, L30b…), e la divisione si scrive nella tabella dei lotti di
`STATE.md` prima di chiudere.

## Il mandato

**NC-028** (bloccante, solo per lo spegnimento) e **NC-029** (maggiore). È il lotto che sta sul
cammino di G1: finché NC-028 è aperta, G1 non si concede.

Tre cose, che vanno insieme perché nascono tutte dall'alimentatore:
1. **Lo spegnimento normale** (ADR-043 §1). I rail audio restano sopra la soglia a cui il blocco
   perde la regolazione (~10 V misurati in L29c, da rimisurare) finché il mute non è completo:
   mute graduale e relè al jack. Servono un supervisore della rete e una tenuta dei rail.
2. **Il failsafe per il guasto dell'alimentatore** (ADR-043 §2), che non deve dipendere
   dall'alimentatore sano. Con la **nota di ADR-045**: alla caduta di `VRELAY` lo sfasamento di K6
   sparisce, e K1/K5 tornano a 0 dB insieme allo stacco dei jack. Il failsafe deve rilasciare
   `MUTE_CMD` per primo e tenere K6, K1/K5 e K11/K12 almeno Δ dopo, oppure provare un'altra via.
3. **Il calore del telaio con otto blocchi** (NC-029): 6,45 W a riposo della sola scheda audio
   contro i 3–4 W che P5 prevede per l'apparecchio intero. O P5 aggiornato al numero vero, o
   ventilazione e montaggio con una ADR, o ADR-021 riaperta se i 60 °C non reggono.

## Prima di tutto: le due domande che ADR-043 lascia all'utente

- **La forma del failsafe**: ADR-043 non sceglie nessuna tecnica, «la progetta L30, con
  l'utente».
- **La soglia in caso di guasto**: V2 per intero (100 µV), oppure una soglia di non-danno per il
  finale e i diffusori.

Si chiedono **conversando**, con le cifre davanti, non con un questionario a scelta multipla.
**I bump si dicono in dB SPL contro il silenzio di una stanza, non in mV** (preferenza
dell'utente): soglia V2 ~33 dB di picco a 1 m, stanza silenziosa ~25–35 dB(A). I casi di guasto
di L29c portavano al jack **8,9–17,5 V** col relè in ritardo, e 11 mV / 0,24 mV col relè già
chiuso. Il calcolo in dB lo fa la formula di NC-028.

## Leggi PRIMA, in quest'ordine

1. **`CLAUDE.md`** e **`docs/limitations.md`**.
2. **`docs/preamp/STATE.md`**: le voci di diario di L35 e di L29c, e le righe L30 e L35.
3. **ADR-043** (spegnimento e failsafe), **ADR-045** (la nota per il failsafe), **ADR-012** (lo
   stato sicuro del mute), **ADR-021** (i 60 °C), **ADR-020** (il ripple ammesso), **ADR-032**
   (V2 accensione e spegnimento compresi).
4. **Il report di L29c** (`reports/2026-09-23-L29c-v2-caso-peggiore.md`, sezione dello
   spegnimento) e il **report di L35**, sezioni 1 e 7: il contratto del temporizzatore accanto a
   J4 e il budget delle bobine.
5. **`circuits/preamp/preamp_audio.py`**, il blocco di J4, e **NC-028** e **NC-029** in
   `NONCOMPLIANCE.md`.

## Quello che L35 ti consegna

- **Il contratto del temporizzatore**, accanto a J4 in `preamp_audio.py`:
  - `MUTE_CMD` e `PERMIT_CMD` sfasati di Δ (nominale 20 ms, ≥ 10 ms);
  - l'OR di F10 con l'interruttore SW3 (aperto = mute);
  - i 13 ms dopo `VRELAY` valida su `PERMIT_CMD`.

  L'alimentatore lo realizza, oppure lo cambia con una ADR.
- **Il budget di `VRELAY`**:
  - bobine 168,8 mA a 5 V a +10 dB (72,8 a 12 V, 36,8 a 24 V);
  - LED ~4 mA fuori mute e ~6 mA in mute, cioè ~175 mA nel caso peggiore;
  - `VRELAY` − V_F(Schottky, 42 mA) ≥ 80 % della tensione nominale, a −5 % e a caldo.
- **Il deck di V2** `spice/preamp/tb/tb_v2_casopeggiore.cir`, generato dalla netlist (punto 5 di
  ADR-043: lo spegnimento si verifica lì o su un suo derivato).

## I vincoli

- **Nessuna tecnica di failsafe senza l'utente.** Se il failsafe chiede un elemento in serie al
  segnale, o un cambio dello stato sicuro di ADR-012, è una modifica di topologia e torna
  all'utente (ADR-043, «Da riaprire se»).
- **La logica di interblocco di trim e guadagno non si tocca.** Il deck V2 si rigenera dalla
  netlist: se L30 non tocca la scheda audio, deve restare **byte-identico**.
- Nel worktree `git` vengono rifiutati:
  - i comandi composti, e le pipe o i `;` attorno a comandi che eseguono script;
  - `awk -v`;
  - i `sed` con più `-e` o con `a\`;
  - i percorsi calcolati a runtime (anche `$CLAUDE_JOB_DIR` dentro un comando).

  Si usano comandi semplici, **percorsi assoluti**, script su file, ed Edit per i testi.
  `git show --output=` lascia un file vuoto: per estrarre una netlist storica serve uno script
  Python che chiami `git show` e scriva il file.

## NON fa parte di questo lotto

- **L28** (SS dell'LSK489, NC-027): va fatto prima di G2, ma è un altro lotto;
- il dossier;
- la proposta per il trim col ponte, se l'utente non la sceglie;
- il PCB e il contenitore (entro G2).

## CHIUSURA

1. `STATE.md` con L30 (o la parte fatta) **fatto** e il prossimo lotto.
2. Riscrivi QUESTO file per il lotto successivo.
3. Commit, push, PR.
4. `/bin/zsh scripts/chunk_close.sh L30` (o il nome della parte).
5. Rimuovi il worktree coi comandi che lo script stampa.
6. **Fermati.**
