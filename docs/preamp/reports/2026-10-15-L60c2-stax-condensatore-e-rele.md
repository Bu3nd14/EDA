# L60c2 — La Stax ha il suo condensatore nel sorgente, K3 un relè a isolamento supplementare (2026-10-15/16)

Seconda parte di **L60c** («la Stax ha il suo condensatore»), dopo la prova di L60c1. Sessione «hi-fi
preamp L60c2».

**Il risultato.**
- **Il condensatore da 1 µF della fissa 2 è nel sorgente, prima del relè di mute K3**, al posto del
  4,7 µF (ADR-081, ADR-084).
- **K3 è un TE Axicom IM06TS**, con isolamento **supplementare** fra bobina e contatti dichiarato dal
  costruttore (**ADR-085**). La scelta 6 su K3 è chiusa.
- **Sulla Stax** reggono la risposta a 20 Hz (E9), l'inserimento a caldo, V2 e il blocco al rail.
- **P10 ha trovato quattro guasti del blocco** che il condensatore non ferma, perché l'uscita oscilla
  o deriva lenta. Il peggiore, R109 aperta, tiene la Stax sopra il tetto per 0,4–1,2 s. L'utente ha
  scelto la ridondanza nel blocco, in un lotto suo, e il tetto della Stax a 150 ms (**ADR-086**,
  **NC-069**).
- **V2 sulla principale** non regge col blocco di L56, per una causa che non viene da questo lotto
  (**NC-070**, proposta).

## 1. Le decisioni dell'utente, nell'ordine

1. **«Accetta il supplementare».** Cercando il relè, i relè di segnale a due deviatori (TE Axicom IM e
   P2, Panasonic TX) dichiarano al più l'isolamento supplementare; il rinforzato di ADR-084 sta sui
   relè di potenza (Finder 40.52, Schrack RT2, Omron G2RL-2), con bobine da 3–4 volte la corrente,
   più grandi, a fori passanti.
2. **«TE Axicom IM06TS»**, sui numeri del datasheet (§ 2).
3. Su P10 (§ 4): **«Fermati, decidiamo il rimedio»**, poi **«Ridondanza nel blocco»**. Alla domanda
   «ma perché non modifichiamo solo il blocco STAX?»: il blocco A alimenta F2, quindi servono almeno A
   e F2; poi **«Tutti e otto i blocchi»**, **«Lotto suo, dopo»**, e per il contratto **«Tetto a 150
   ms»**.

## 2. Il relè

`vendor/relays/te/IM/ENG_DS_108-98001_K.pdf`: TE 108-98001 Rev. K. Il sito di TE rifiuta lo
scaricamento automatico (HTTP 403), quindi la copia viene da Farnell, con la provenienza in
`PROVENANCE.json`. Le revisioni successive non si sono potute leggere: vanno rilette prima
dell'ordine.

| | G6K-2F-Y (K2, K4) | IM06TS (K3) |
|---|---|---|
| Isolamento bobina-contatti | base, 1500 V | **supplementare** IEC/EN 60950 (p. 3); 1800 V efficaci, 2500 V impulsivi (p. 22) |
| Contatto aperto | 0,1 pF | **al più 1 pF** (p. 23); ~0,2 pF dall'isolamento a 100 MHz. Il limite di ADR-044 è ~2,4 pF |
| Intervento e rilascio | 3 ms | 3 ms senza diodo; la bobina si scarica su uno zener (`psu.py`) |
| Contatti | dorati, biforcati | PdRu dorati, biforcati, < 50 mΩ |
| Bobina a 12 V | 9,1 mA | **11,7 mA** (1029 Ω) |
| Piedinatura | 1/8, COM 3/6, NC 2/7, NO 4/5 | **la stessa**, con la bobina **polarizzata**: + sul pin 1 |

**La piedinatura è letta in tre modi che concordano**, come per il G6K:
- la pagina 5 resa a 450 dpi;
- le coordinate vettoriali (`script/im_pinmap_svg.py`): l'àncora attraversa il contatto 2/7 a x =
  100,9 pt, dentro i suoi 96,2–104,0, e resta a 9,8 pt dal 4/5;
- le polilinee del simbolo KiCad `Relay:IM00`.

**La bobina interviene anche calda.** Dalla curva a p. 24, l'intervento sicuro è al ~75 % della
tensione nominale a 23 °C, ~84 % a 60 °C, ~92 % a 85 °C. `VRELAY` a −5 % dà il 95 %.

## 3. Il sorgente e i controlli

- **`circuits/preamp/preamp_audio.py`**:
  - il condensatore della fissa 2 a `1u`, col commento di ADR-007 riscritto (ADR-081, ADR-084) e lo
    schema in testa al file aggiornato;
  - K3 come parte propria, `Relay:IM06` su `Relay_SMD:Relay_DPDT_AXICOM_IMSeries_JLeg`, valore
    `IM06TS MUTE2`;
  - il bilancio delle bobine aggiornato: il caso peggiore passa da ~88 a ~88,5 mA, perché K3 è
    acceso solo fuori mute.
- **La netlist confrontata per significato** (`script/confronta_netlist.py`). Cambiano tre cose:
  C165 e C365 a 1u, e K3. Le connessioni sono uguali, 320 gruppi di pin. Cinque reti fuse hanno solo
  cambiato nome (limitations #23).
- **`scripts/check_relay_safe_state.py`** (il controllo 2e):
  - la piedinatura dell'IM06 come dato, con la sua citazione;
  - la bobina polarizzata asserita;
  - **un relè della libreria Relay che il controllo non conosce è ora un rilievo**: prima veniva
    saltato in silenzio, e cambiare una sola parte l'avrebbe tolta da ogni prova.

  **7 sabotaggi su 7** fanno fallire il controllo, ciascuno col suo rilievo (`falsi/verdetti.txt`).
- **Il disegno a blocchi** legge a parte il condensatore della Stax e K3, e asserisce che siano
  diversi da quelli delle altre uscite.
- **ERC**: 0 errori e 65 avvisi, gli stessi avvisi del sorgente di prima, rigenerato per confronto.
- **Il generatore del deck di V2** (`L29c/deck/genera_tb_v2_casopeggiore.py`) legge ora dalla netlist
  anche il condensatore d'uscita e la parte del relè di ciascuna uscita. Il deck versionato cambia in
  due punti: `CFIX2 1u`, e il contatto aperto di K3 a 1 pF in ogni corsa.
- **`psu.py`**: il commento di `C_VRELAY` aggiornato con la tenuta nuova (§ 6).

## 4. P10 sulla Stax

Il banco di L60c1 è importato: la sua G0 è il circuito di L60c2, e il generatore la verifica sulla
netlist prima di scrivere. Le prove sono a C nominale e +5 % (`p10_stax.csv`, `script/sintesi_p10.py`).

**I casi di L60c1 rifatti** ridanno gli stessi numeri: il blocco al rail **118 / 124 ms**, un pin aperto
dei due di un rail 0.

**Ogni guasto del blocco di L45a** sulle posizioni A e F2 che a vuoto portava la Stax sopra 0,87 V
(`p10_blocco.csv` di L45b, 107 modi): a C nominale 99 stanno dentro 125 ms, contando Q122 in corto
rifatta col gear (sotto). Questi non ci stanno:

| Guasto (A e F2) | Che cosa fa | Sopra 0,87 V |
|---|---|---|
| R109 aperta (gate della JFET, lato retroazione) | l'anello si apre; il buffer commuta da −14,5 a +13,7 V ogni ~80 ms; fronti fino a 28 V | **1182 / 1217 ms** (F2), ≥ 775 ms (A, la corsa si ferma a 1,77 s) |
| R112 aperta, o la source di JQ110B aperta | l'uscita salta a +12 V e torna in ~300 ms | 140–149 ms |
| Q133 in corto collettore-emettitore | l'uscita scende lenta verso −7 V | 127–135 ms |
| R144 aperta | l'uscita scivola al rail in ~1 s | 130 ms (solo a +5 %) |

Le forme d'onda sono in `onde_fuori.txt`. Q122 in corto in A si fermava a 6 ms, anche in L45b; col
metodo gear finisce, a 118 / 124 ms (`p10_ricorse.csv`).

**Col tetto di ADR-086 (150 ms)** l'unico modo fuori è **R109 aperta** (NC-069), che la ridondanza di
L60d toglie.

## 5. E9, l'inserimento a caldo, V2

- **E9** (`e9.csv`): 0,147 / 0,161 / 0,178 dB a C +5 % / nominale / −5 %, contro 0,2 dB.
- **L'inserimento a caldo** del jack della Stax: nullo.
- **V2 A sul banco**: 0, come in L60c1. Il banco non ha la capacità del contatto aperto: la ha la
  matrice.
- **La matrice di V2** (`v2/`): il deck versionato rigenerato, 155 corse.
  - **Corse e analisi.** 149 corse passano la guardia. 6 si fermano per «Timestep too small» sulla
    JFET del blocco A, all'istante in cui si muovono i contatti del jack.
  - **Le 6 corse ferme non dipendono dal contatto di K3**: col contatto a 0,1 pF si fermano lo stesso.
  - **Rifatte col gear**, coi riferimenti anch'essi col gear: il gear e il default differiscono di
    ~49 µV sul jack della Stax, quindi non si mescolano (`v2/gear/`). Tre finiscono: mh01, mev e
    gm10x0.
  - **Non misurate**: gm10x3, gm3x10 e off_r10m_d20. L'ultima mancava anche in L48b.
  - **Sulla Stax regge: 45 verdetti su 45.** Il peggiore è l'accensione, 14,7 µV; la musica a mute
    inserito 1,2 µV; B2g 4,7 µV. Sulla Singxer i numeri sono quelli di L48b.
  - **Sulla principale: 16 verdetti fuori** (B1 fino a 174,6 µV, B2g fino a 499 µV), dove L48b ne
    aveva 0. Nel riferimento «sempre in mute» il jack principale sale a 0,58 mV da ~0,2 s. **Non viene
    da L60c2**: la stessa corsa con le due righe di L60c2 tolte dà lo stesso valore alla quarta cifra
    (`v2/controllo_principale/`), e col gear è uguale. Dopo L48b il blocco è cambiato solo in L56, e
    la matrice non era più stata corsa. → **NC-070**, maggiore proposta: la decide l'utente.

## 6. La tenuta di `VRELAY`

Sul banco della rete di L51b le tre bobine di mute sono una resistenza sola: da 438,3 Ω (tre G6K) a
401,2 Ω col K3 nuovo (`rete/`). Il deck invariato ridà L51b (48,3 / 121,7 / 195,4 ms). Col K3 nuovo:
**46,4 / 119,7 / 193,3 ms** a rete −10 / nom / +10 %, contro i 25 ms di P9 (NC-050 aggiornata).

## 7. Non conformità

- **Aperta NC-069**: R109 aperta, maggiore; il rimedio è L60d.
- **Aperta NC-070**: V2 sulla principale, maggiore *proposta*.
- **NC-042 avanza**: la scelta 6 è chiusa.
- **NC-050 aggiornata.**

In tutto **21 voci aperte, 2 bloccanti** (NC-062 per G1, NC-044 per G2).

## 8. Che cosa resta

- **L60d**: la ridondanza nel blocco (ADR-086), il prossimo lotto.
- Poi **L45d2b2**: il suo prompt pronto è in `data/2026-10-15/L60c2/NEXT-SESSION-L45d2b2.md`.
- **NC-070** ha bisogno di un lotto suo, o di entrare in L60d, che rimisura il blocco: lo decide
  l'utente.
