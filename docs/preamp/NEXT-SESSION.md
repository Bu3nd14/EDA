# Prompt per la sessione successiva — L18

Riprendo il progetto del preamplificatore hi-fi in questo repository. Il
lavoro è organizzato in LOTTI PICCOLI: questa sessione ne fa **UNO — L18** — e
si ferma. Non iniziarne un secondo.

## Cosa è cambiato, e perché il prossimo lotto è di nuovo un vincolo scritto

Il lotto precedente è **L15**, che ha scritto il vincolo di NC-005 senza toccare
un numero del circuito. Quattro cose di quel lotto ti riguardano:

1. **Esiste ora la forma di un vincolo scritto accanto al requisito.** È la
   «Nota su E3» in `REQUIREMENTS.md`: verbo verificabile, criterio di passaggio,
   i fatti che il dimensionamento dovrà conciliare, e dove la nota *non* sta e
   perché. NC-011 dice di sé «è la stessa forma di NC-005».
2. **Il criterio del «sostanziale» è scritto**: una modifica ai requisiti è
   sostanziale — e vuole una ADR — se **cambia l'insieme dei progetti
   conformi**. Per E3 la risposta era no. Per te probabilmente è sì: ripartire
   il budget di E5 fra ripple e resto è una scelta. Applicalo, non assumerlo.
3. **Le aggiunte in coda alle ADR non sono una forma ammessa.** L15 le ha lette
   col loro commit: sono tutte del 2026-09-08, e due su quattro (ADR-007,
   ADR-008) superano un valore senza ADR nuova. Il precedente dopo le regole è
   ADR-019, una ADR nuova. Vedi `reports/2026-09-13-L15-vincolo-e3.md` §2.
4. **NC-005 è rimasta aperta per metà**, la misura, che è di L16. Una voce che
   chiede «scrivere **e** fare» si chiude quando entrambe le cose sono fatte.

Voci: **19 aperte, 6 bloccanti** — NC-001 (L11), NC-002 e NC-021 (L12), NC-004,
NC-010 (L17), NC-017 (Fase 4).

## Leggi PRIMA, in quest'ordine, e non saltare

1. **`CLAUDE.md`** — ambiente, percorsi assoluti, trappole che falliscono in
   silenzio, e la regola di fine sessione (push prima di tutto)
2. **`docs/preamp/STATE.md`** — «Come si lavora da qui», la tabella dei lotti,
   la sezione **L15**, e **«Prossimo passo concreto»**, che contiene il mandato
   di questo lotto per esteso
3. **`docs/preamp/NONCOMPLIANCE.md`**, voce **NC-011** — quella che chiudi — e
   **NC-004**, che è E5 senza evidenza
4. **`docs/preamp/REQUIREMENTS.md`** — **E5** e la sua nota, **E7**, e la
   «Nota su E3» come esempio di forma
5. **`docs/preamp/decisions/README.md`** (le regole delle ADR),
   **`TEMPLATE.md`**, **ADR-010** (alimentatore a bordo) e **ADR-015** (rail
   ±15 V)
6. **`docs/preamp/reports/2026-09-10-L22-L23-specchio-ingresso.md`**, riga 355:
   il PSRR non è stato rimisurato dopo lo specchio LS352

## IL LOTTO: L18 — il vincolo PSRR scritto dove verrà letto

**Il difetto.** Il PSRR del rail positivo è pubblicato — a 10 kHz, +10 dB,
**29,76 dB**, contro 86,93 del rail negativo — ma nessun documento ne trae la
conseguenza. L'alimentatore non è progettato, e niente gli dice quanto ripple
può lasciare sul rail **+** nella banda in cui la reiezione è bassa, che è
proprio quella dove lavorano uno switching o un raddrizzatore.

**Cosa fare:**

1. **Rileggere le cifre dalla topologia di oggi.** I CSV
   `tb_zout_psrr_noise_psrr*.csv` esistono **solo** in `data/2026-09-09/`, cioè
   col THAT320. Riesegui `spice/preamp/tb/tb_zout_psrr_noise.cir` sul codice di
   oggi e confronta, come L14 ha fatto con `tb_op`. Se le cifre si muovono, il
   vincolo si scrive su quelle nuove e lo scarto si registra.
2. **Scrivere il vincolo** nella forma di NC-011: «il ripple residuo ammesso sul
   rail positivo, alle frequenze in cui il PSRR vale X dB, deve stare sotto Y»,
   con Y **ricavato da E5** e il ragionamento scritto accanto. Un vincolo senza
   verbo verificabile non chiude niente.
3. **Decidere dove, e scrivere perché.** `REQUIREMENTS.md`, una ADR nuova, o
   entrambi. Applica il criterio di L15 e scrivi la risposta. Una ADR nuova
   segue `TEMPLATE.md` e va nell'indice di `decisions/README.md`, che oggi si
   ferma ad ADR-016: aggiungere la riga della tua **non** autorizza a sistemare
   le altre tre.
4. **Decidere quale metà della voce è tua.** NC-011 chiede anche la **scelta del
   rimedio** (regolatore a bassissimo rumore, o cella a moltiplicatore di
   capacità per gli stadi d'ingresso). Se non è di L18, dillo come L15 l'ha
   detto per la misura di NC-005, e lascia la voce aperta.

### Quello che il repo ti consegna già — usalo invece di riscoprirlo

- **La suite è a 8 blocchi**, 8 passed a fine L15.
- **Il difetto `setplot`** di `tb_zout_psrr_noise.cir` (L3d) è corretto in L5.
- **E5 ha già una nota** che traduce 10 µV in SPL sulle Heresy: il budget è
  ampio ma «non illimitato».
- **Cerca se qualcuno ha già deciso**: ADR-010 e ADR-015 parlano
  dell'alimentatore; la voce è del 2026-09-09.

## Cosa NON accettare

- **Una cifra di PSRR della topologia col THAT320** usata senza dirlo.
- **Un vincolo senza verbo verificabile.** «Il ripple va tenuto basso» non si
  misura.
- **Un'ADR riscritta**, o un'aggiunta in coda a una ADR esistente.
- **Un alimentatore progettato.** Non è questo lotto.

## NON fa parte di questo lotto

- **Progettare o simulare l'alimentatore**: è `psu-engineer`, dopo.
- **NC-004** (rumore e distorsione senza evidenza): è bloccante e ha il suo
  percorso.
- **Il trim** (L16), il mute (L11), il margine di fase (L12).
- **L'indice di `decisions/README.md`** oltre alla riga della tua ADR, e il
  diagramma «0/+10 dB» in `REQUIREMENTS.md`: annotati da L15, non tuoi.
- **Il percorso cablato di `testbenches/01_op.cir`**: annotato, non tuo.
- **Non toccare i file già in `vendor/`.**

## Come lavoriamo

- **Verifica invece di fidarti.** Se un subagente riporta dei numeri,
  rieseguili tu prima di riferirmeli.
- **Verifica alla fonte anche ciò che il lotto precedente ti ha scritto.** L15
  ha trovato una frase di NC-009 che diceva il contrario del vero.
- **Un controllo mai fatto fallire non è un controllo.** L15 ha applicato il
  verbo del vincolo a un caso che doveva fallire prima di fidarsene.
- **Cerca se qualcuno ha già deciso, prima di aprire una voce.**
- **Niente cifre non eseguite.**
- **Diffida degli script che dichiarano di aver verificato qualcosa.**
  `export_fab.sh` (riga 28) e `setup.sh` (riga 24) hanno ancora `ROOT` cablato
  su `/Users/roberto/EDA`. Se il tuo lotto ne tocca uno, correggilo lì.
- **Un lotto per volta, mai due agenti in parallelo**: il vincolo è il cap di
  token del piano.
- **Lavora in un worktree.** I commit non pushati dentro `.claude/worktrees/`
  spariscono col worktree, ed è già successo. Nel worktree, lancia gli script
  zsh **da soli**, non in comandi composti: il guardiano di isolamento li
  rifiuta. Una simulazione rieseguita da un worktree legge il circuito del
  worktree **solo** se il deck usa la convenzione di percorso di L2-L3: verificalo
  sul deck prima di fidarti del confronto.

## CHIUSURA

Non è una lista da ricordare, è uno script che rifiuta. Nell'ordine:

1. aggiorna `docs/preamp/STATE.md` segnando il lotto **fatto** e il successivo
   come prossimo (la tabella deve dire **fatto**)
2. **riscrivi QUESTO file per il lotto successivo** — se il titolo nomina
   ancora L18, lo script rifiuta, ed è il controllo che esiste apposta
3. committa, pusha, apri la PR
4. `/bin/zsh scripts/chunk_close.sh L18` — verifica tutto, merghia, riallinea
   il checkout dell'utente e rilegge da lì per provare il riallineo. Se
   rifiuta, ha ragione: sistema e rilancia
5. rimuovi il worktree con i due comandi che lo script stampa
6. **fermati.** Non iniziare il lotto dopo.
