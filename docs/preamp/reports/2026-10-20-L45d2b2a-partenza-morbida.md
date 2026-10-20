# L45d2b2a — La partenza morbida dei regolatori dei rail, e il loro calore a regime

Data: 2026-10-20 · Lotto: L45d2b2a (prima parte di L45d2b2) · Dati: `data/2026-10-20/L45d2b2a/`
(README) · Decisioni: **ADR-091**, **ADR-092** · Non conformità: **NC-063 chiusa**, **NC-072 aperta**

## In breve

- **L45d2b2 in tre parti** («Tre parti», l'utente all'inizio):
  - questa, la partenza morbida;
  - L45d2b2b, i diodi della tenuta, il regolatore negativo, il comando e i 5 V;
  - L45d2b2c, i massimi del blocco.
- **Prima di partire, la domanda rimasta da L62b**: i diodi di riserva del moltiplicatore portano
  94–177 µA, non «qualche µA». L'utente: **«Conta il limite in mA»**. La clausola di ADR-090 non è
  scattata.
- **Coi 10 µF di prima il firmware andava in GUASTO a ogni accensione**: il rail − in 12 s, contro i
  2 s che il firmware concede. Il banco ora lo riproduce: 1,25 V/s, GUASTO a 2,0 s.
- **C507 4,7 µF, C508 470 nF** («+ 4,7 µF, − 470 nF», ADR-091):
  - i due rail insieme in ~0,6 s, assestati prima che i jack si chiudano (0,71 s);
  - MUSICA a 0,72 s, anche a rete −10 %;
  - V2 all'accensione con le rampe vere: 4,9 µV al jack principale, ~15 dB SPL a 1 m.
- **Trovato, rispondendo all'utente**: i due regolatori dei rail a regime fanno **136–137 °C** a rete
  +10 % con 60 °C d'aria, oltre i 125 °C. Rimedio scelto («4,7 Ω + rame al layout», ADR-092): R550 /
  R551 nel sorgente (122 °C) e il rame sotto il pad al layout (≤ 27 °C/W). **NC-072**, maggiore,
  prima del congelamento.
- **`run_tests.sh` 13 / 0**; la netlist dell'alimentatore passa da 118 a 120 parti.

## Il banco dell'alimentatore

Copiato da L45d2b1 in `psu/` (l'intestazione di `genera_tb_psu.py` elenca le modifiche).

**Controllato prima di cambiarlo, su tre casi noti** (`controllo/`):
- tolte solo le righe del rivelatore, sulla netlist di prima, `accensione` e `perdita` danno il CSV
  del firmware al punto fisso **identico byte per byte** a L45d2b1 e a L56;
- col generatore completo e le opzioni che rimettono il banco di prima (`--ss no --cap-audio no
  --bobine g6k`) l'accensione è di nuovo identica;
- con la bobina di K3 IM06TS (401,17 Ω per le tre bobine del mute) la tenuta di `VRELAY_REG` a
  rete −10 % è **46,367 ms** (L60c2: 46,372).

**Le aggiunte:**
- **la partenza morbida** in `REGPSS` / `REGMSS`. Il riferimento parte quando l'ingresso supera la
  soglia di sottotensione:
  - nel positivo si carica a RC verso VSET + 5 V con τ = 100 kΩ · C_NR (riproduce l'eq. 5 di
    SBVS204G);
  - nel negativo sale lineare in 1,2 ms/nF (l'eq. 1 di SBVS169D);
  - la forma prima del punto finale è un'ipotesi dichiarata, i datasheet danno solo il tempo;
- **i condensatori della scheda audio sui rail**, che i banchi di prima non avevano
  (`capacita_rail.py`): 800,8 µF per rail, più sul + le otto celle da 1000 µF dietro 10 Ω;
- **il carico di oggi** (tb_op di L62b: 303,4 / 311,5 mA).

**Lo strumento** (`verifica_ss.py`):
- 14 rampe entro **lo 0,22 %** dalle due equazioni;
- il caso con 1 µF sul positivo, in limite di corrente, è più lento dell'eq. 5, come deve;
- i sabotaggi (C_NR +10 %, l'eq. 5 senza i 5 V) fanno cadere 14 e 6 controlli.

## La scelta dei condensatori

`accensione.csv`, `termico_avvio.csv`. I tempi sono da `MAINS_REQ`; le soglie sono quelle del
firmware (ADC_SUP_P > 2,55 V, cioè +13,82 V; ADC_SUP_M < 1,20 V, cioè −14,1 V).

| | + alla soglia | − alla soglia | jack | musica | U501 all'avvio |
|---|---|---|---|---|---|
| oggi, 10 / 10 µF | 1178 ms | mai | — | **GUASTO a 2,0 s** | 4,4 W, 0,36 A |
| **4,7 µF / 470 nF** | 556 ms | 534 ms | 707 ms, rail assestati | **717 ms** | 7,4 W, 0,45 A |
| 10 µF / 1 µF | 1178 ms | 1131 ms | 1329 ms, + a 14,69 V | 1339 ms | 4,4 W, 0,36 A |
| 1 µF / 1 µF | 171 ms | 1131 ms | 1282 ms | 1292 ms | **1,0 A, 16,4 W, in limite** |

Rete −10 %: tempi uguali.

**L'utente ha chiesto se la partenza più rapida accorci la vita del regolatore** o lo rischi.
- Il datasheet non dà l'impedenza termica nel tempo. La stima è una rete a due nodi sul profilo di
  potenza simulato: R_JC(bot) 1,7 °C/W, il resto fino a 32,5 °C/W verso l'aria; 0,04 J/K il
  contenitore e 0,3–1 J/K la scheda sotto il pad (ipotesi).
- Risultato: **+10…18 °C** all'avvio, partendo dall'aria (dallo standby il regolatore è freddo),
  contro i +40–54 °C che fa a regime per ore. L'energia dell'avvio (la carica dei ~9,6 mF a valle)
  non dipende dalla velocità; la rampa rapida la concentra in 0,65 s invece di 1,4.
- **L'avvio non è il problema; il regime sì** (sotto).

**Il rumore di ADR-020 non si rimisura.** Il limite per eccesso è costruito sulle curve a C_NR 1 µF
(il +) e 10 nF (il −), e un NR più grande filtra di più il riferimento.

## Il calore a regime (NC-072)

`rpre.csv`, `rete_sorgente.csv`. Regola del progetto per le parti attive (ADR-021): 60 °C + P ·
R_thJA ≤ 125 °C, con i 32,5 °C/W del costruttore (scheda JEDEC; il TPS7A3301 ha lo stesso
contenitore).

| Davanti al regolatore | Rete −10 % | Nominale | **Rete +10 %** | Nella resistenza | Riserva a −10 % | Jack prima del rail, perdita a −10 % |
|---|---|---|---|---|---|---|
| niente | 92 °C | 114 °C | **136–137 °C** | — | 2,88 / 2,79 V | 51 ms |
| 2,2 Ω | 85 °C | 107 °C | 129–130 °C | 0,20 / 0,22 W | 2,21 / 2,10 V | 46 ms |
| 3,3 Ω | 82 °C | 104 °C | 126–127 °C | 0,31 / 0,32 W | 1,88 / 1,76 V | 44 ms |
| **4,7 Ω** | 77 °C | 99 °C | **122 °C** | 0,44 / 0,46 W | 1,45 / 1,32 V | 40 ms |
| 5,6 Ω | 74 °C | 97 °C | 119 °C | 0,52 / 0,55 W | 1,18 / 1,04 V | 38 ms |

- **La resistenza da sola non basta.** Fra rete −10 % e +10 % il grezzo cambia di ~4,5 V, e il
  regolatore li assorbe; la resistenza toglie la stessa caduta a tutte e due le reti, e a −10 % la
  riserva non può scendere sotto 1 V (la quota di reiezione di ADR-020 la suppone).
- L'utente: **«4,7 Ω + rame al layout»** (ADR-092). Sul sorgente: 121,7 / 122,2 °C a rete +10 %;
  ~112 °C con ≤ 27 °C/W.
- **Severità**: «Maggiore, prima del congelamento».

## Il sorgente

`psu.py`:
- **C507 / C508**: 4,7 µF / 470 nF;
- **R550 / R551**: 4,7 Ω, assiali da 2 W, fra il serbatoio e i nodi nuovi `RAW_PR` / `RAW_MR`, dove
  stanno anche l'ingresso, l'abilitazione, C509 / C510 e D510 / D511;
- netlist **118 → 120 parti**, cambiata solo lì (il confronto per contenuto);
- il disegno a blocchi mostra le resistenze e lo asserisce: rifiuta la netlist di prima
  (`falsi/psu_senza_r550_r551.net`).

Altri file:
- il commento della cella RC in `gain_block.py` (la rampa e la corrente di U501);
- `run_tests.sh` **13 passed / 0 failed**.

Sul sorgente, senza opzioni (`corri_finale.sh`), il banco ridà le cifre dell'opzione scelta: 650 /
563 ms, jack a 707 ms, MUSICA a 717 ms.

## V2 all'accensione con le rampe vere

La matrice di V2 (L29c) supponeva rampe lineari di 10 o 300 ms e il mute rilasciato 2,5 s dopo
l'inizio. Col firmware il rilascio arriva **0,70 s** dopo l'inizio delle rampe.
`v2/genera_v2_accensione.py` copia il caso d'accensione della matrice versionata (geometria iii,
+10 dB, senza segnale) con le rampe campionate dal banco:
- **nominale**, e coi due condensatori a **±20 % in senso opposto** (+ lento / − veloce e il
  contrario);
- col rilascio del firmware (`on_ss_*`) e con quello di L29c (`on_ssl_*`), perché il verdetto vuole
  ≥ 2 s di finestra per giudicare la rampa.

La prima prova è stata scartata, ed è diventata limitations #66. Con 500 punti la riga `alter` non
è entrata («too many args»), ngspice ha finito lo stesso coi rail di prima, e l'ha presa la guardia
di V2. `controlla_rampe.py` ora verifica che le rampe simulate siano quelle del banco (entro 0,06 V),
e che il caso di L29c risulti diverso.

| | rilascio (A_rel), il peggiore | rampa (A_ins), il peggiore |
|---|---|---|
| L29c, 300 ms, rilascio a 2,5 s | 0,04 nV | 0,26 µV |
| **rampe vere, rilascio del firmware** | **4,9 µV** al principale, ~15 dB SPL a 1 m | (finestra corta) |
| rampe vere, rilascio a 2,5 s | 0,04 nV | 0,31 µV, ~−9 dB SPL |

- Il tetto è 100 µV, cioè ~41 dB SPL a 1 m; una stanza silenziosa sta a 25–30 dB SPL.
- Il rilascio arriva più vicino alla rampa, e il colpo passa da 0,04 nV a 4,9 µV. Resta 26 dB sotto
  il tetto.
- I tre «non regge» di `verdetto.py` sono la finestra corta della rampa con il rilascio del firmware
  (0,70–0,81 s contro 2 s). Le stesse rampe con la finestra intera danno lo stesso picco allo stesso
  istante (0,27 s), sotto il tetto.

## Limiti dichiarati

- **I regolatori sono comportamentali.** La forma della partenza morbida prima del suo punto finale
  è un'ipotesi; i datasheet danno t_SS di un esemplare tipico, senza minimo né massimo. La
  tolleranza è coperta a ±20 % sui condensatori.
- **Il calore è stimato**: R_thJA della scheda JEDEC, rete termica dell'avvio con capacità ipotizzate.
  La conferma è la misura sul prototipo.
- **I condensatori della scheda audio** sono nominali, senza ESR.
- **V2 all'accensione** è sulla geometria iii a +10 dB senza segnale, come in L29c; le rampe sono a
  segmenti di 30 ms.

## Che cosa resta, e a chi

- **L45d2b2b**: i diodi della tenuta e U502 (ADR-074), il comando e i 5 V (ADR-075), sul banco di
  questo lotto. R550 / R551 cambiano il lato grezzo: in un corto del serbatoio la tenuta si scarica
  attraverso 4,7 Ω.
- **L45d2b2c**: le tensioni massime del blocco e la dissipazione dei finali (ADR-078).
- **G2**: il rame sotto i due regolatori (NC-072), la temperatura misurata.
- **Trovato e non toccato**: l'indice delle decisioni non ha ancora le righe di ADR-087…089 (deriva
  già segnalata in L62a).
