# Prompt per la sessione successiva — L27

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L27** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato col lotto precedente

**L12 ha chiuso NC-002 e NC-021**: ogni istanza del blocco sta sopra i 60° di
ADR-019. Due decisioni, e ti riguardano entrambe.

1. **ADR-024 — dove si applica la sonda.** L'utente l'ha definita: è **il cavo**
   d'interconnessione, quindi sta **al jack**, dopo 47 Ω e 4,7 µF. Il verdetto
   è il **minimo sulla spazzata fino a 4,7 nF**, non il valore a 4,7 nF: al jack
   il margine non è monotono, e il minimo cade fra 2,2 e 3,3 nF. Il blocco A si
   giudica col suo cablaggio verso l'attenuatore, ≤ 1 nF.
2. **ADR-025 — il rimedio.** **C137, il C_f in parallelo a R_f, da 22 a
   330 pF C0G**, in tutte le otto istanze. Miller e 47 Ω invariati.

| Istanza, criterio ADR-024 | Minimo | Agli spigoli di tolleranza |
|---|---|---|
| Blocco B 0 dB | **61,21°** (attenuatore a metà corsa, 3,3 nF) | 60,73° |
| Blocco B +10 dB | 102,96° | — |
| Blocco A | 63,36° (sorgente phono, 1 nF) | 62,69° |
| Buffer delle fisse | 61,63° (Stax, 2,7 nF) | 61,16° |

**Perché questo lotto viene adesso.** Il C_f lavora contro la rete di
controreazione, e L27 la cambia: un secondo ramo di R_g verso massa. La cella
**B a +3 dB** di V1 è l'unica riga di stabilità ancora senza misura, oltre al
trim. **ADR-025 mette L27 fra i «da riaprire se»**, con una guardia di 0,7° sul
blocco B a 0 dB.

Voci: **17 aperte, 2 bloccanti** (NC-004, NC-017, entrambe di Fase 4).

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`**: ambiente, percorsi assoluti, trappole silenziose, chiusura.
2. **`docs/preamp/STATE.md`**: la voce di diario di L12 e «Prossimo passo
   concreto».
3. **`docs/preamp/NONCOMPLIANCE.md`**: **NC-022**, e la «Chiusura» di NC-021.
4. **Le ADR:**
   - **ADR-019** (i tre livelli, riposo a 0 dB), **ADR-004** (si commuta R_g,
     mai R_f);
   - **ADR-024** e **ADR-025**;
   - **ADR-012** e **ADR-021** (i relè di mute: poli e bobine sono condivisi).
5. **`REQUIREMENTS.md`**: E2, F5, V1 (coi paragrafi nuovi), V2.
6. **`reports/2026-09-14-L12-margine-di-fase.md`**: come si sono misurati i
   margini, lo slew rate, le tolleranze; e i due numeri che una griglia rada ha
   reso ottimisti.
7. **`circuits/preamp/gain_block.py`**: la rete di controreazione (R_F, R_G,
   C137) e il commento LOOP INTEGRITY in testa. **`preamp_audio.py`**: dove sta
   il relè del guadagno.
8. **`docs/limitations.md` #10, #24, #25, #26**.

## IL LOTTO: L27 — il terzo livello di guadagno

### Cosa fare

1. **Il dimensionamento.** Un secondo ramo commutato verso massa per il
   +3 dB, col principio di ADR-004: si commuta R_g, mai R_f, e **a relè
   diseccitati il guadagno è 0 dB** (ADR-019). Il valore esatto del gradino
   esce da due resistenze E96; se lo scarto è scomodo, ADR-019 dice che serve
   un'ADR sua.
2. **I relè.** Quanti, con quanti poli, come si combinano i due rami. Il
   budget di corrente delle bobine è un dato per `psu-engineer`.
3. **La stabilità, prima di tutto il resto.** V1 a +3 dB col criterio di
   ADR-024 e C_f 330 pF, con le stesse celle di L12: sorgente
   dell'attenuatore 1 mΩ / 1 k / 2,5 k, cavo al jack fino a 4,7 nF, carico
   100 k e 10 k. **E rimisura 0 e +10 dB**: se la rete cambia anche a 0 dB
   (capacità parassite del secondo contatto aperto su FB), cambia il margine
   di 61,21°.
4. **Se +3 dB non passa**, il rimedio va scelto coi numeri come in L12, e
   deve valere per tutte le istanze (T3 / ADR-006). Un rimedio diverso per
   ruolo è una decisione dell'utente.
5. **I deck.** Ogni `foreach` che spazza `0db / 10db` ne vuole tre. Contali con
   `grep` prima di cominciare. Attenzione ai `$var` nei nomi `wrdata` (#10) e
   ai nomi delle tabelle `echo` (#25).
6. **Il diagramma a blocchi.** Il «+10 dB» è calcolato da R_f/R_g e asserito
   contro E2: l'asserzione va estesa, non aggirata.
7. **V2**: il transitorio di commutazione fra 0, +3 e +10 dB, con rimbalzo.
   L'anello non deve aprirsi in nessuno stato dei contatti.

### I vincoli

- **ADR-004**: R_f mai commutata. **ADR-019**: riposo a 0 dB.
- **ADR-019 / ADR-024**: 60° al minimo della spazzata, ogni cella.
- **ADR-023 / T1**: classe A sui percorsi ascoltabili. **P7**.
- **T3 / ADR-006**: un solo blocco. **T7 / T8** su ogni parte nuova (relè
  compreso).
- **E5**: 9,90 µV al circuito; R_g in parallelo cambia il rumore a +3 dB.

## Cosa NON accettare

- **Un margine letto a 4,7 nF invece che come minimo della spazzata**, o su una
  griglia che salta 2,2–3,3 nF. In L12 il buffer dava 61,85° su 8 punti e
  61,63° su 11.
- **Un margine a +3 dB interpolato** fra 0 e +10 dB.
- **Un deck che include `gain_block_flat.inc` con un nodo che si chiama come un
  nodo del blocco** (#24).
- **Una `meas` il cui risultato non si è controllato nel log** (#26): celle
  vuote e righe `Error:` con ngspice a rc 0.
- **Un deck che esce 0 e che nessuno ha provato a far fallire.**
- **Un'ADR riscritta**, o un'aggiunta in coda a una esistente.
- **Una netlist o uno schematico modificati a mano**, e un `git diff` su un
  `.net` letto come prova di topologia: serve il confronto normalizzato o
  semantico (L3b, L12).

## NON fa parte di questo lotto

- **Il trim e il suo interlock (L16)**, anche se i relè del trim prendono il
  permissivo dal mute.
- **NC-029, il calore (L30)**; **NC-028 (L29)**.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti**, anche dei numeri di L12 qui sopra.
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
   ancora L27, lo script rifiuta;
3. committa, pusha, apri la PR;
4. `/bin/zsh scripts/chunk_close.sh L27`;
5. rimuovi il worktree coi due comandi che lo script stampa;
6. **fermati.**
