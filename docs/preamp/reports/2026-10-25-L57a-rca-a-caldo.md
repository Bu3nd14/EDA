# L57a — l'RCA a caldo: il banco provato, i numeri di oggi, le strade, la scelta

Data: 2026-10-25 · Lotto: L57a (sessione «hi-fi preamp L57a») · Dati: `data/2026-10-25/L57a/` (README)
· Decisione: **ADR-101** · Non conformità: **NC-059 avanza**, si chiude in L57b.

All'inizio L57 è stato diviso dall'utente («Due parti»): **L57a** il banco, i numeri, le strade e la
scelta; **L57b** il rimedio nel sorgente e la regressione. Il circuito non cambia in L57a.

## 1. Il banco, provato prima dei numeri

Il generatore nuovo (`script/genera.py`) in modo `l53` ridà il testo di `L53/rca/rca.cir` e `gate.cir`
riga per riga, salvo l'include del blocco. Col blocco di L53 (`git show 96bacb07:…`, stesso hash del
blob, 8ef2b93) le due corse ridanno i CSV di L53: **88 celle su 88** entro lo 0,5 % / 1 mV
(`verifica_noto.py`).

Sul circuito di oggi (`spice/preamp/gain_block.subckt`, generato da `gain_block.py` con ADR-099; nessuna
copia vecchia, limitations #62) la catena di L53 coincide con `preamp_audio.py` nei valori; mancavano tre
resistenze, aggiunte e dichiarate: R_G 1 MΩ sul gate di B, le scariche lato condensatore (470 k sulla
fissa, 220 k sulla principale). `check_deck_refs.py` pulito; i nodi interni misurati (g1, g2, s1, d1n,
ncasc) verificati nel blocco di oggi.

## 2. I numeri di oggi, senza rimedio

Al jack principale, dB SPL di picco a 1 m (finale ×21,1, Heresy 96 dB / 1 W / 1 m, clip a 21,9 V,
~113,8 dB SPL; tetto di PR-23 0,87 V, 112,2 dB SPL). Uguali a L53 al decimo.

| Sorgente | Posizione d'ascolto, 0 / +10 dB | Volume in cima, 0 / +10 dB | Fisse sul K11 |
|---|---|---|---|
| a terra, 10 mV | 44,7 / 54,4 | 73,7 / 83,4 | −51,6 dB |
| a terra, 0,65 V | 81,0 / 90,6 | 110,0 / clip | −15,4 dB |
| classe II, 1 e 3,46 nF | 107,1 / **clip** | **clip** / **clip** | **+11,1 dB** |

La coppia d'ingresso col caso peggiore (3,46 nF), alle tre reti:

| Rete | Ingresso | Gate-gate (rottura ±30 V) | Gate-drain (60 V) |
|---|---|---|---|
| −10 % | 37,7 V | 23,8 V | −47,2 V |
| nominale | 41,9 V | 28,0 V | −51,4 V |
| **+10 %** | 46,1 V | **32,2 V — oltre** | −55,6 V |

L53 aveva corso solo la rete nominale (1,9 V di margine): a +10 % la parte è oltre il suo minimo.
Il gate-drain non era misurato.

**La corrente di gate** (29–39 mA di picco). Ho sospettato una conduzione della giunzione gate-drain
(l'ingresso a 14,8 V, il drain a ~9,2 V) e l'ho detto all'utente; la forma d'onda dice altro
(`rca/forma/forma.txt`): il picco cade a 60,0006 ms, all'istante del contatto della **massa**, e dura
meno di 1 µs; la giunzione gate-drain non va mai in avanti (al più 0,45 V), Q117 mai in inversa. È lo
spostamento capacitivo di un fronte, come leggeva L53, ma del fronte della massa.

## 3. Le strade

Tutte fra il contatto del selettore e l'ingresso del blocco A (dopo C_IN). Caso peggiore delle tre reti
e della sorgente in classe II (`sintesi.csv`); il costo col banco di §4.

| Strada | Gate-gate | Gate-drain | Diodi | Jack, ascolto 0 / +10 dB | In cima | Fisse | THD 20 kHz 0,2 / 2 V | E5 |
|---|---|---|---|---|---|---|---|---|
| nessuna | **32,2** | 55,6 | — | 107,1 / clip | clip | +11,1 | 0,000686 / 0,00685 % | 4,58 µV |
| 2,2 kΩ sola | 28,0 (nom.) | 51,4 | — | 107,1 / clip | clip | +11,1 | — | — |
| 1 kΩ, diodi ai rail | 8,1 | 25,1 | 0,14 mA | 107,1 / clip | clip | +11,1 | 0,000764 / 0,00765 | 4,92 |
| 2,2 kΩ, diodi ai rail | 6,8 | 25,1 | 0,14 | 107,1 / clip | clip | +11,1 | 0,000857 / 0,0086 | 5,31 |
| 4,7 kΩ, diodi ai rail | 5,0 | 25,1 | 0,14 | 107,1 / clip | clip | +11,1 | **0,00105** / **0,0105** | 6,02 |
| 10 kΩ, diodi ai rail | 2,8 (nom.) | 25,1 | 0,12 | 107,1 / clip | clip | +11,1 | **0,00142** / **0,0144** | 7,30 |
| **1 kΩ, limitatore ±5,6 V** | **4,3** | 14,7 | 1,1 | **99,8 / 109,8** | clip | **+3,4** | 0,000764 / 0,00765 | 4,92 |
| 2,2 kΩ, limitatore | 3,3 | 14,7 | 0,54 | 99,8 / 109,8 | clip | +3,4 | 0,000857 / 0,0086 | 5,31 |
| 1 kΩ, zener 12 V (AN-015) | 7,9 | 21,7 | 0,15 | 106,4 / clip | clip | +10,3 | 0,000764 / 0,00765 | 4,92 |
| 1,5 kΩ, zener 12 V (AN-015) | 7,3 | 21,7 | 0,15 | 106,4 / clip | clip | +10,3 | 0,000803 / 0,00805 | 5,09 |
| mute inserito, nessuna | **32,2** | 55,6 | — | 77,2 / 85,0 | 105,8 | −22,9 | — | — |
| mute inserito, limitatore | 4,3 | 14,7 | 1,1 | 77,0 / 82,5 | 105,3 | −23,6 | — | — |

Tetti: gate-gate 30 V, gate-drain 60 V, IG(F) 10 mA (la corrente di gate con una protezione ≤ 0,9 mA);
V4 THD a 20 kHz ≤ 0,001 % a 0,2 V RMS e ≤ 0,01 % a 2 V RMS; E5 ≤ 9,95 µV; il jack 112,2 dB SPL.

- **La resistenza da sola** toglie il picco di corrente, non la tensione.
- **La resistenza costa distorsione** per il meccanismo di NC-055 (più impedenza di sorgente davanti al
  JFET, la seconda armonica sale): da 4,7 kΩ si esce da V4.
- **I diodi verso i rail e gli zener da 12 V** proteggono la parte, ma il jack resta come oggi: clip a
  +10 dB alla posizione d'ascolto.
- **Il limitatore a ±5,6 V** è l'unico che porta il jack alla posizione d'ascolto sotto il tetto in
  entrambi i modi, e le fisse da +11,1 a +3,4 dB.
- **Col volume in cima** nessuna protezione dell'ingresso evita il clip: lo fa già la musica (3,82 V di
  picco di E6 contro 0,87 V). Solo il mute inserito lo tiene sotto (105,3–105,8 dB SPL).
- Un **mute automatico** (un rivelatore del sovraccarico che apra i relè in pochi ms) non è stato né
  progettato né misurato.

**La letteratura** (ricerca chiesta dall'utente): nessun rimedio specifico per l'apparecchio in classe II
inserito a caldo; il fenomeno è descritto (Wikipedia, «Floating ground»: il polo dell'RCA tocca prima
dello schermo, l'ingresso in saturazione); per la parte la soluzione è la protezione generica
dell'ingresso — Elliott Sound Products AN-015: almeno 1 kΩ (meglio 1,5 k), i soli diodi ai rail
«protezione finta» contro i guasti energetici (i rail gonfiati), preferiti diodi a bassa capacità in serie
a zener ~12 V —; per le casse, nei forum, spegnere o silenziare prima di collegare. Il testo di Douglas
Self non l'ho trovato. La variante di AN-015 è stata misurata su richiesta dell'utente.

## 4. Il costo al segnale, e due trappole del banco

Il banco (`script/dist.py`): sorgente 2,5 kΩ (V4), selettore, protezione, blocco A, trim a 0 dB, la fissa
del Singxer col carico di V4; THD col metodo di L46a (passo 1/(2500 f), 2 ms + due periodi,
fourgridsize 8192), rumore 20 Hz–20 kHz all'uscita del blocco A.

- **Un punto di lavoro falso.** Coi diodi, in diverse varianti ngspice ripiegava sul «transient op» e,
  nel banco del rumore, il ripiego dava un blocco **spento** (le sorgenti a −0,36 V, guadagno 0,0008): un
  rumore di 0,12 µV plausibile e falso. Un nodeset sui soli nodi d'ingresso e `rshunt` aiutavano a caso.
  Il rimedio: il punto di lavoro vivo del deck senza protezione (`nodeset.py`, 84 nodi, d1n 9,18 V) come
  nodeset di tutti; `leggi_costo.py` rifiuta un guadagno del blocco lontano da 1, e un'uscita della
  fissa lontana dalla sorgente. Il controllo del metodo: una 4,7 kΩ da sola dà 1,248 µV contro 1,25.
- **Un pavimento del banco.** A 1 kHz h3 e h5+ erano −101 dB in tutte le varianti: il transitorio
  d'avvio di C_IN (polo a 0,5 Hz) è una rampa nella finestra. Spostata la sorgente oltre C_IN: −103 dB,
  ora dal 4,7 µF della fissa; letta la fourier prima del 4,7 µF: −149 dB. La protezione e il 4,7 µF sono
  lineari nel modello: la misura non cambia di significato.
- **Il rumore aggiunto** è il termico della resistenza: 1 kΩ +0,574 µV (teoria 0,576), 2,2 kΩ +0,851,
  4,7 kΩ +1,24. E5 è stimato per eccesso (×3,152 in quadratura con 4,577 µV).
- **A pieno livello d'ingresso** (E6, 2,7 V RMS a 20 kHz; nessun tetto di V4 a quel livello) le armoniche
  dalla 5ª in su: senza −142,8 dB, diodi ai rail e AN-015 −142,1/−142,2, limitatore −137,6.

## 5. Le domande e la scelta

Una prima formulazione delle domande è stata fermata dall'utente per chiarire: che cos'è una sorgente in
classe II, che cosa vuol dire «volume in cima» e perché lì non si protegge, come risolvono letteratura e
rete. Dopo la ricerca, l'utente ha chiesto di misurare anche la variante di AN-015. Poi:

1. **«Limitatore ±5,6 V»** — 1 kΩ e due diodi verso ±5 V, i riferimenti comuni ai due canali.
2. **«Sì, mute prima»** — l'avviso nel manuale d'uso; il testo in ADR-101 finché un manuale non c'è.

**ADR-101.** NC-059 avanza; si chiude in L57b.

## 6. Per L57b

- Le parti: i diodi (bassa dispersione e bassa capacità; il 1N4148 è uno stand-in), i riferimenti a
  ±5 V a shunt (assorbono fino a ~1,1 mA per canale a rete +10 %; due canali). Il sorgente in
  `preamp_audio.py` (la protezione è del canale, non del blocco), le sigle esplicite (#22).
- Netlist, disegni (lo schematico completo e lo schema a blocchi), `run_tests.sh`.
- Il banco di L57a sul circuito generato (le stesse cifre di ADR-101 entro i «Da riaprire se»), il
  costo con le parti vere, la regressione V1, E5, V4 dove tocca l'ingresso; E3 non cambia (la
  protezione è in serie, dopo R_SEL).

## Limiti dichiarati

- Le ipotesi della sorgente sono quelle di L53 (10 ms, 1 / 3,46 nF, 0,25 mA).
- Diodi 1N4148, riferimenti e zener ideali.
- Le cifre di distorsione vengono dai modelli del costruttore (ADR-013 / L39); la misura sul prototipo
  vale sopra di esse.
- Il mute inserito usa 1 pF per il contatto aperto.
- `run_tests.sh` 15 / 0 a fine lotto (il circuito non è cambiato).
