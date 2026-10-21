# L63b — lo schematico completo della scheda audio (2026-10-21)

**Che cosa**: la seconda pagina della richiesta dell'utente a fine L45d2b2c, «lo schematico, due pagine,
ma complete (anche fosse A3) una per la scheda audio e una per l'alimentatore, complete senza blocchi
ripetuti». L'alimentatore è L63a; questa è la scheda audio, nella lettura dell'utente di «senza blocchi
ripetuti» (L63a): **«Blocco una volta, un canale»**.

**Il circuito non è stato toccato.** Nessuna ADR, nessuna non conformità aperta o chiusa. Disegnando non
si è trovato nessun errore nel sorgente: il kit ha confrontato ogni piedino delle 570 parti.

## Le due scelte dell'utente, all'inizio

Coi numeri: la pagina disegna circa 138 parti e 420 piedini, più una tabella di 59 righe per 8 istanze,
contro le 133 parti e i 349 piedini dell'alimentatore, che riempiono già un A3.

| Domanda | Risposta |
|---|---|
| Il formato | **«A3 first, A2 if it won't fit»**: provare A3 alla scala dell'alimentatore, passare ad A2 senza chiedere di nuovo se non entra |
| Una sessione o due | **«One session»** |

**È A2.** Alla densità dell'alimentatore, che va coi piedini, i 420 piedini sono ~1,2 A3 prima della
tabella. L'A2 (594 × 420 mm) è alla stessa scala: testo a 5 pt, resistenze di ~7 mm, le due pagine si
stampano uguali.

## La pagina

`docs/preamp/schematic/audio.pdf` (e `audio.svg`), A2 orizzontale, una pagina. In alto il canale sinistro,
lungo il segnale; in basso il blocco, la tabella e i comandi.

1. **Ingressi e selettore**: J101–J104, i condensatori d'ingresso C171–C174, R171–R178, i poli 1 di
   K13–K16 sul bus AL_IN.
2. **Il canale sinistro**:
   - il blocco AL;
   - le due uscite fisse, il buffer, 47 Ω, il condensatore, il deviatore di mute (K2, K3) e i bleed;
   - il trim, R901–R903 e i poli 1 di K7 / K8;
   - C265 e il volume J120;
   - il blocco BL coi rami del guadagno (poli 1 di K1 / K5);
   - l'uscita principale con K4 e J230.
   Le note dicono come si chiama il destro.
5. **Selettore**: SW4 coi tre poli (b e c liberi, con le croci), le bobine K13–K16 con D16–D19, i poli 2
   di K13–K16 sul canale destro (AR_IN, R_SEL1…4).
6. **Mute, permesso, connettori**: le bobine K2–K4 su MUTE_CMD e K6 su PERMIT_CMD, i due poli di K6
   (VRELAY → PERMIT_MID → VTRIM, VHOLD), D3, R3 e J7, J4, SW3, J1, J2, i poli 2 di K2–K4.
7. **Il blocco di guadagno, una volta**, da `circuits/preamp/gain_block.net` (il blocco con tutte le
   parti montate):
   - la coppia JFET cascodata;
   - lo specchio con l'aiuto, l'inseguitore e il VAS;
   - il moltiplicatore di V_be coi quattro diodi di riserva, i finali coi diodi di ADR-095, la
     controreazione con R138 / R143;
   - in un pannello a parte, i riferimenti NREF / NCASC / VPF e il disaccoppiamento.
8. **Le otto istanze**: una riga per ogni parte del blocco, una colonna per istanza (AL, BL, F1L, F2L,
   AR, BR, F1R, F2R) con la sua sigla vera, «—» dove non è montata, e le porte di ogni istanza.
9. **Guadagno**: SW2 coi quattro poli, D10–D15, le bobine K1 / K11 e K5 / K12, l'autoritenuta (poli 1 di
   K11 / K12), i LED del guadagno vero (poli 2, R2, J6), i poli 2 di K1 / K5 sul blocco BR.
10. **Trim**: SW1 coi quattro poli a ponte H, le bobine K7 / K9 e K8 / K10 con le TVS D1 / D2, i LED (poli
   1 di K9 / K10, R1, J5), i poli 2 liberi di K9 / K10, i poli 2 di K7 / K8 sul canale destro.

| | |
|---|---|
| Parti disegnate | **138**: il blocco 59, la scheda 79 |
| Parti espanse | **491**: 454 nelle otto istanze, 37 del canale destro |
| Confronto con la netlist | **570 su 570**, nei due sensi |
| Terminali | 404; piedini e contatti liberi segnati con la croce: 41 |
| Reti | 123, disegnate in 236 pezzi; 165 nomi; 100 giunzioni |
| Testo | 5 pt (valori 4,5), le resistenze ~7 mm, come l'alimentatore |

**La tabella** (riquadro 8), ricavata e non trascritta:
- R113 (R_IN, 1 MΩ) solo in AL e AR;
- R138 (+3 dB) e R143 (+10 dB) solo in BL e BR;
- le quattro istanze buffer (F1L, F2L, F1R, F2R) senza nessuna delle tre;
- valori diversi dal blocco: **nessuno**, in nessuna istanza.

**Il canale destro** (le note del riquadro 2):
- le sigle +200 (R161 → R361, J101 → J301), il trim +10 (R901 → R911);
- le reti L_ → R_, AL_ → AR_, BL_ → BR_, F1L_ → F1R_, F2L_ → F2R_;
- un nome nella netlist non segue la regola, ed è scritto sulla pagina: **R_ATT_W si chiama BR_IN**, il
  cursore del volume destro (un nodo unito prende in SKiDL uno solo dei suoi nomi, come avverte
  `preamp_audio.py`).

## Come la pagina resta onesta

Il kit di L63a (`sheet_kit.py`) rifiutava già:
- un filo fra due reti, un corto, un filo sopra una parte;
- una rete in pezzi senza nome, un testo sopra un testo o un filo;
- una parte o un piedino non disegnati.

L63b gli aggiunge la **pagina ripiegata**.

- **Il modello**: `gain_block.net` entra sotto uno spazio dei nomi (`BLK:R108`) e si stampa senza.
- **`Sheet.fold()` ricava la tabella dalla numerazione di `gain_block()`** (un contatore da `base`, una
  parte saltata è un numero non usato):
  - per ogni scelta delle parti opzionali (R_IN, R_g, R_g10, trovate dalle loro reti nel modello),
    ogni parte t del modello va a `base + (t − 100) − (opzionali assenti sotto t)`;
  - una sola scelta deve dare esattamente le parti dell'istanza.
- **Poi la asserisce sulla netlist**:
  - stesso simbolo e stesso valore riga per riga; un valore diverso finisce stampato nella cella;
  - ogni rete del modello cade su una sola rete dell'istanza: un rail col suo nome, una porta (una rete
    che anche fuori dall'istanza tocca), o la rete interna col nome della regola, tag_X.
- **Il destro**:
  - ogni parte del sinistro ha il suo gemello con lo stesso simbolo e lo stesso valore (i connettori
    con _L → _R);
  - la corrispondenza fra le reti è una **biiezione letta sui piedini**: dove il nome della regola
    esiste deve coincidere, dove non esiste è un alias stampato.
- **`finish()` espande il disegno** nel manifesto di tutte le 570 parti:
  - il modello nelle otto istanze, con le reti prese dal disegno (l'isola del modello rinominata con
    la regola, le porte dal riquadro dell'istanza);
  - il sinistro nel destro.
  - `scripts/check_schematic.py`, invariato, lo confronta con `preamp_audio.net` (blocco 2d).
- **La copertura** diventa «ogni parte disegnata o espansa, una volta sola»; ogni piedino del simbolo di
  un relè, di un rotativo o di un duale deve essere un terminale o una croce.
- **I simboli nuovi**: PNP, i duali LSK489 / LS352 (dai simboli del progetto, `library/preamp.kicad_sym`),
  i deviatori dei relè (S / R sui bistabili), i poli dei rotativi, l'interruttore del mute, la TVS, il
  riquadro di un'istanza.

**Il blocco 2f** disegna la pagina, e vuole il manifesto generato uguale a quello versionato.

## I sabotaggi

`data/2026-10-21/L63b/script/sabotaggi.py`: **22 su 22 presi**.

- **Sul manifesto espanso**:
  - un piedino del destro spostato;
  - una parte di un'istanza tolta.
- **Sul ripiegamento, sulla pagina vera**:
  - due sigle scambiate nella tabella: la pagina si disegna e il 2d la rifiuta, DISCORDE R311 / R312;
  - la base di un'istanza sbagliata;
  - la regola del destro sbagliata di uno;
  - una parte opzionale non dichiarata;
  - su copie della netlist rotte apposta: un pezzo del destro ricablato (R363 su R_FIXC1), un valore
    del destro diverso, un'istanza senza una parte del nucleo.
  - E un valore diverso in un'istanza (R533 a 33 Ω) **non** è un errore: finisce nella tabella, e il
    sabotaggio lo verifica.
- **Sul kit**:
  - una parte disegnata che il ripiegamento espande;
  - una parte del sinistro, una del blocco, il riquadro di un'istanza non disegnati;
  - un deviatore sul contatto sbagliato;
  - una posizione del rotativo sulla rete sbagliata;
  - un riquadro senza una porta;
  - un relè con la sola bobina;
  - un testo sopra una massa.
- **I 14 di L63a**, sul kit esteso.

## Guardata a 300 dpi, a pezzi

Il controllo dei testi del kit dice «nessun testo sopra un altro»; a 300 dpi la pagina ha mostrato tre
cose che non vedeva.

- **Le masse sopra le etichette**: la massa del piedino 2 di J110, J111 e J230 copriva le etichette di
  R163, R166 e R263. Il controllo non guardava i simboli. Ora sì: ogni simbolo lascia un'impronta, e un
  testo sopra un'impronta è un rifiuto (limitations #71).
  - Rieseguito sull'alimentatore di L63a, il controllo nuovo ne ha trovate quattro: J2, J508, J515 e il
    «−» del ponte D503.
  - Corrette spostando i simboli e facendo dei sottotitoli di J508 / J515 il titolo del connettore.
  - **Il manifesto dell'alimentatore è uguale a quello di L63a, byte per byte**: nessuna parte né
    connessione cambiata.
- **Il testo sotto il simbolo di un rail verso il basso** era attraversato dalla barra, anche
  sull'alimentatore: ora sta più in basso.
- **Le etichette delle bobine K13–K16 attaccate** alle sigle dei diodi accanto: le bobine lì portano la
  sola sigla, e il valore dei diodi sta in una nota.

E il kit ha preso, senza che lo si cercasse, una resistenza (R123) disegnata attaccata al rail VPF ma a
1e-7 da esso: le coordinate degli ancoraggi di schemdraw non sono esatte. Era «VPF in 3 pezzi senza
nome»; ora c'è un filo esplicito (limitations #71).

## Suite

`run_tests.sh` **15 passed / 0 failed** (dal worktree):
- il 2d controlla anche `audio.manifest.json`, 570 su 570;
- il 2f ha un controllo in più, la pagina della scheda audio e il suo manifesto;
- il manifesto dell'alimentatore resta uguale.

## Resta

- Niente, per L63. Il prossimo lotto è **L45d2b3**, i guasti rifatti e la sintesi (prompt in
  `NEXT-SESSION.md`).
- **Ogni cambio al circuito**, da qui, ridisegna anche le due pagine complete: il 2f lo pretende.
