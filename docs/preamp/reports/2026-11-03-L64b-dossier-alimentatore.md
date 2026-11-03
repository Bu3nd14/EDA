# L64b — il dossier rigenerato, l'alimentatore e il temporizzatore

Data: 2026-11-03 · Lotto: L64b (la seconda delle tre parti di L64) · Decisioni: nessuna ADR. Dati:
`data/2026-11-03/L64b/` (README). Nessuna non conformità aperta o chiusa; NC-050 aggiornata. Il
circuito non è cambiato: due commenti di `psu.py` riscritti per scelta dell'utente, `psu.net`
rigenerato uguale (solo le righe del sorgente e la data).

## In breve

- **Le scelte dell'utente**: in sessione, **«non caricare troppo la CPU se devi fare simulazioni, ci
  sono altre sessioni di claude running oggi»** (al più due corse insieme, a priorità bassa); sui
  commenti di `C_RAW` e `C_VRELAY` in `psu.py`, che davano per «di oggi» le cifre di L51b, **«Rewrite
  now»**.
- **Il generatore rifiutava 57 volte** con l'alimentatore acceso (`rifiuti_primo_giro.txt`): R512 a
  220 kΩ in ogni log di L51b (da ADR-094 è la metà di R_MD, 110 kΩ); il `genera_tb_psu.py` di L51b che
  non legge più la netlist (i test point di ADR-107); le 15 sequenze del firmware e i 4 deck del
  temporizzatore col micro, che non c'è più (ADR-102); il calore e il carico di prima di L66.
- **La pagina ha la scheda audio e l'alimentatore** (`PARTI = ("audio", "alimentatore")`), scritta solo
  fuori dal repo; passa: «OK: tutti i controlli incrociati sono passati». **Sabotaggi 21 su 21**.
- **Le cifre di oggi**, tutte lette dai dati:
  - la tenuta di `VRELAY_REG` dopo la perdita di rete **50,3 / 109,6 / 169,1 ms** (P9 ≥ 25);
  - il permissivo **39,6 ms** dopo il mute, il più corto delle sette corse del criterio (≥ 16,9);
  - la musica **612,8 ms** dopo un buco di 20 ms (≥ 500);
  - K501 **75,6 ms** dopo il permissivo allo spegnimento (≥ 50);
  - lo standby **115,8 / 129,7 / 143,8 mW** da T2;
  - al jack il guasto peggiore U501 spento **32,2 dB SPL** (86,96 µV); a rete −10 % la perdita di rete
    **+4,3 dB SPL**;
  - il calore **17,68 / 15,42 / 19,98 W**, **57,7 °C** a 3 cm nel caso peggiore, gioco minimo
    **2,0 cm** (L51b 1,5).

## Le corse

Tutte sul `psu.net` di oggi (quello di L58b) col carico di oggi (`tb_op` di L64a: 303,3288 / 311,5182 mA,
il selettore, K3 IM06TS), il banco di L58b con le sue opzioni (il comparatore tarato, la ritenuta e i
BAT54 del costruttore), due alla volta.

| Che cosa | Prima strada | Seconda strada |
|---|---|---|
| i banchi della rete e dei guasti | `rete/`, `guasti/` (`--timer sorgente --tss 3.0`) | i deck rigenerati; L51b accanto, ogni scarto pubblicato |
| il calore | `termica/` (le voci nuove: R550 / R551, gli SB340, i diodi inversi) | il deck rigenerato, la stima rieseguita, il bilancio (0,07 W di resto), la scheda audio contro `tb_op` e contro i rail del banco della rete (9,20964 / 9,20973 W) |
| le sequenze | **117 corse per 138 righe** di L54b3b e L58b, più lo standby | `confronta.py`: **4255 celle, 4002 identiche, 253 entro la tolleranza, 0 fuori**; i 107 deck di L58b uguali a quelli di oggi a meno del carico |
| lo standby | `--sonda-t2` alle tre reti | L54b2: 116,1 / 130,1 / 144,2 mW |
| la catena al jack | il ponte dalle sequenze di oggi, 18 corse per rete | `tabella.py` rieseguito, il deck di V2 rigenerato; L54b2 accanto, scarti ≤ 0,4 dB |

## Trovato

- **Le 12 righe di Q501 di L58b (`f_q501_corto_*`, `f_q501_gd_*`) non sono guasti del circuito di oggi.**
  Erano del Q501 singolo di prima della coppia: sul deck di oggi «corto» cortocircuita MUTE_CMD sul
  ritorno, cioè la coppia intera (due guasti), e «gd» unisce due nodi che non sono gate e drain di
  nessun transistor. I guasti singoli di oggi sono quelli della coppia che L58b corse sulla variante
  (`lista_s1m`): ricorsi sul sorgente coi nomi di oggi (`modi.py` di L64b, la mappa di
  `sorgente_uguale.py`). **64 corse: 51 come la coppia sana, 6 col solo K501 spostato (al più 2,5 ms,
  dopo una perdita di rete), 7 col mute che resta inserito (Q509 gate-drain: la musica non arriva).**
- **K501 si apre 5 ms prima del permissivo con U503 spento** (`k_perm_ms` −5,0): la sua bobina sta su
  `VRELAY_REG`, che con U503 spento non c'è. Il margine di ADR-046 (≥ 50 ms) vale per lo spegnimento dal
  frontale (L54b3b, criterio 3), 75,6 ms; il jack è staccato a 17,9 ms e il guadagno a 45,1.
- **Dopo L51b i rail si muovono in due direzioni** alla perdita di rete a −10 %: il rail + arriva a
  13,5 V più tardi (65,5 → 92,4 ms), il rail − più presto (63,6 → 50,4 ms). Una causa sola è certa: lo
  Schottky dopo il regolatore (i rail a 14,985 / −14,972 V invece di 15,000 / −15,052). Il dossier dice
  i fatti e non le cause che non ho provato; il mute è rilasciato decine di millisecondi prima.
- **La riga in cima alla pagina** diceva ancora «deck corsi il 2026-10-09 (L51a) sul circuito di L48b»
  anche nella pagina di L64a: corretta (L64a, il circuito dopo L67).
- **La riga di «Cosa non dice» sul firmware** («il firmware non gira su un micro») era falsa: tolta, al
  suo posto il comparatore di comportamento tarato (ADR-103). L64c riscrive la sezione.
- **NC-050**, il dato di oggi: 50,3 / 109,6 / 169,1 ms, 25 ms sopra P9; resta aperta fino a G2.
- **Il colpo al jack all'accensione con le rampe vere** (`v2/` di L58b) non è nel dossier, come non lo
  era in L51b: con la coppia ogni guasto singolo tiene il mute dove deve (le sequenze), e la corsa sana
  di L58b dava ~2 nV al jack principale. Non ricorso.

## Errori

- La lista dei mancanti riscritta mentre `xargs` la leggeva: una riga arrivata tagliata («struttore»,
  la corsa rifiutata) e otto corse saltate; ricorse, e `controlla_ok.py` prova ogni `ok.txt` contro la
  sua riga.
- `psu/analizza.py` senza l'argomento dell'evento (2 s per difetto) dava i tempi spostati di 1000 ms;
  rifatto con 3.0, e il generatore rifiuta un tempo dall'evento fuori da 0–500 ms.
- La mia prima tolleranza su `on_min` (il minimo di `VRELAY_EN`, 1e-4 V) era stretta: il minimo letto
  dalla `.meas` sui punti del transitorio prende due valori (4,4533 / 4,4564 V lo stesso caso sano a
  rete nominale e a ±10 %); portata a 0,01 V come le altre tensioni, scritto nel README.
- Una frase mia («la 4,7 Ω e la partenza morbida rallentano la discesa dei rail») era vera per un rail
  solo: riscritta coi fatti.
