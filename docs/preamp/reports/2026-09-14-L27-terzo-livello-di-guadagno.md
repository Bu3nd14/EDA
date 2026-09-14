# L27 — Il terzo livello di guadagno (2026-09-14)

Lotto **L27**. Chiude **NC-022**. Registra **ADR-026**. Apre **NC-030**. Dati:
`data/2026-09-14/L27/` (vedi il suo `README.md`).

## 1. La baseline, verificata prima di toccare il circuito

`tb_loop.cir` di `main` rieseguito: la tabella è **byte-identica** a quella di
`L12/dopo/`, 132 righe, 0 righe `Error`, 0 celle vuote.
- 0 dB: **61,2055°** (2,5 kΩ, 3,3 nF);
- +10 dB: **102,959°** (2,5 kΩ, 4,7 nF).

## 2. La rete (ADR-026)

**Due rami di R_g in parallelo da FB verso massa**, ciascuno col proprio
contatto normalmente aperto:
- **R_g3 = 3,57 kΩ** su K1;
- **R_g10 = 866 Ω** su K5, un G6K-2F-Y nuovo con un polo per canale.

| Stato | Guadagno, calcolato dalla netlist |
|---|---|
| K1 e K5 aperti (riposo) | 0 dB |
| K1 | **+3,047 dB** |
| K1 + K5 | **+9,972 dB** (con 698 Ω era +9,963) |
| solo K5 (guasto di K1) | +8,730 dB |

La scelta è stata fatta **prima** di misurare, perché dipende da una proprietà
e non da un margine:
- con i rami in parallelo, nessuno stato dei contatti supera il +10 dB;
- con due rami esclusivi, un contatto saldato darebbe **+11,03 dB**.

La coppia E96 è quella che sposta meno il +10 dB esistente.

**Il budget delle bobine** per `psu-engineer` è in ADR-026. Il caso peggiore
sono cinque bobine eccitate: **105,5 mA a 5 V**, 45,5 mA a 12 V, 23,0 mA a
24 V. La tensione di `VRELAY` non è decisa.

## 3. La consegna

- **`gain_block.py`**:
  - `R_G3`, `R_G10`, LOOP INTEGRITY a quattro stati, porte del subckt
    `IN OUT FB RG RG10 VPLUS VMINUS`;
  - R_g10 è aggiunta **in coda**, dopo il disaccoppiamento, così nessun
    riferimento esistente cambia numero (#22). Nel blocco è R143, sulla scheda
    R242/R442.
- **`preamp_audio.py`**: K5 «G6K-2F-Y GAIN10» su `GAIN10_CMD`, un polo per canale
  verso `RG10`, NO a GND.
- **Rigenerati `.net`, `.subckt`, `_flat.inc`**. I due file SPICE cambiano solo
  dove previsto: porte, `R138 698 → 3.57k`, `R143 FB RG10 866`.
- **Confronto semantico** della netlist (`esplorazione/script/netcmp.py`):
  - `preamp_audio.net` passa da 357 a 360 componenti. Aggiunti K5, R242, R442;
    R237 e R437 da 698 a 3.57k;
  - **tolti i componenti aggiunti, la partizione dei nodi è identica**. Il
    parser ha letto 872 nodi, non zero;
  - `gain_block.net` passa da 42 a 43 componenti, con la stessa proprietà;
  - ERC 0 errori.
- **16 deck** estesi. Sei spazzano ora tre modi; tutti terminano `RG10`.
  - `tb_loop` ha preso il carico da 10 k, che V1 e NEXT-SESSION chiedevano e
    che il deck non aveva;
  - `tb_switch_v2` è stato riscritto con due relè.
- **Disegni**:
  - `gain_block.svg` e il manifesto: 45 dispositivi, 102/102 terminali,
    `check_schematic.py` OK;
  - `preamp_blocks_draw.py` calcola e asserisce i tre guadagni e la connettività
    in parallelo. Corretta anche una frase ormai falsa: diceva «NON ANCORA
    CONFERMATO» quale contatto fosse NO, cosa chiusa da L21.

## 4. Una trappola nuova, e il guardiano che la ferma

**Un nodo di contatto lasciato su un solo terminale non dà errore.** Prima di
toccare i deck, i deck non aggiornati sono stati eseguiti sull'include nuovo:
- **`tb_op.cir`**: rc 0, 87 valori. Uno solo differisce, alla sesta cifra.
  `RG10` segue FB e basta;
- **`tb_ac.cir`**: la modalità che il deck chiama «10db» chiude solo `RG`, cioè
  il ramo da 3,57 k, e ha stampato **g1k = +3,037 dB** invece di +9,949. Il
  file si chiama ancora `tb_ac_10db_*`, e ngspice esce 0.

→ **limitazione #27**.

**Il guardiano**: `check_deck_refs.py` (blocco 2g) controlla ora due regole
aggiuntive, ricavate dai file generati e non da un elenco di nomi:
- **nodi pendenti**: un nodo esterno di un include flat che nel blocco tocca un
  solo terminale deve essere collegato dal deck;
- **porte**: ogni riga `X` deve passare tante porte quante il `.subckt` ne
  dichiara, e le porte pendenti devono essere collegate.

Provato in quattro direzioni:

| Prova | Esito |
|---|---|
| i 16 deck di `main` sull'include nuovo | **fallisce**, exit 1: 12 nodi `RG10` pendenti, 4 deck con 6 porte su 7 |
| i 16 deck aggiornati | passa, exit 0 |
| i 16 deck di `main` sull'include di `main`, in un repo di scratch | passa: nessun falso allarme sullo stato pre-L27 |
| una riga `X` con 7 nodi ma `RG10F1` scollegato | **fallisce** |

**Gli altri guardiani, fatti fallire:**
- `check_relay_safe_state.py` (2e) vede cinque relè, K5 come GAIN, OK. Con K5
  cablato su NC fallisce con 3 rilievi;
- le asserzioni nuove del diagramma a blocchi (2f):
  - R237 e R437 a 3.24k → «+3 dB entro 0,1 dB; … danno 3.30 dB»;
  - il COM di K5 spostato su K1 → «l'altro capo di R242 deve andare al solo
    K5»;
  - una R_g3 sola cambiata → cade la vecchia asserzione di uguaglianza fra
    canali.

## 5. V1, prima di tutto il resto

`dopo/tb_loop/`, criterio ADR-024. 396 righe, 0 righe `Error`, 0 celle vuote.

| Blocco B | Carico 100 k | Carico 10 k | A vuoto: margine, T a 10 Hz, attraversamento |
|---|---|---|---|
| 0 dB | **61,829°** (2,5 k, 3,3 nF) | 61,870° | 70,22°, 72,40 dB, 929 kHz |
| +3 dB | **69,799°** (2,5 k, 2,7 nF) | 69,851° | 77,43°, 69,10 dB, 915 kHz |
| +10 dB | **102,994°** (2,5 k, 4,7 nF) | 103,040° | 109,83°, 61,86 dB, 527 kHz |

- **Il guadagno d'anello a 10 Hz** a 0 dB vale 72,40 dB, come il controllo #24
  si aspetta.
- **Il margine a 0 dB sale di 0,62°**: sul nodo FB, a contatti aperti, due rami
  con i loro 15 pF pesano meno di uno da 698 Ω.
- **Sul nodo**, come informazione: 44,46° / 51,71° / 96,65°.
- **Griglia fitta**, 0,1 nF da 1,8 a 4,2 nF: 61,8289° a 0 dB e **69,7905°** a
  +3 dB (2,8 nF). La griglia versionata sbaglia di 0,009°, sotto la soglia di
  0,05° oltre cui la si sarebbe estesa.
- **Spigoli di tolleranza** (C124 e C137 ±5 %, R_iso ±1 %, come L12):
  **61,449°** a 0 dB (L12: 60,73°) e **68,671°** a +3 dB.

**Conforme su ogni cella**, e **nessun rimedio serve**.

## 6. V2, P7 e il resto della matrice

| Controllo | Esito |
|---|---|
| **V2** (`tb_switch_v2`) | Regime a +10 dB: +1,52176 / −1,62625 V. Nessuna finestra di transizione esce da quell'inviluppo, compresi 0→+10 con K5 per primo (+1,52178 / −1,62627 V) e +10→0 con K1 per primo. NX e NY entro ±2,63 V |
| **Controfattuale** | anello chiuso −0,0522 V; anello aperto **−13,773 V**. Falsifica ancora |
| **P7** a +3 dB (`tb_mute_corto`, sweep 1c) | MJE peggiore del blocco B **339,6 mW**, Tj **81,2 °C** (corto sul MAIN, 20 kHz); 47 Ω del MAIN **0,309 W**. A +10 dB 348,0 mW e 1,091 W, come L12 |
| **Classe A**, ADR-023 | 600 righe, 0 celle vuote. Sulle 440 righe di L12, **0** cambiano stato; ΔP massima di un MJE 1,28 mW. **0 righe ascoltabili fuori dalla classe A** in ogni modo |
| **E5** | +3 dB: 2,011 µV (2,5 k), 1,634 µV (430 Ω). Caso peggiore, +10 dB e 2,5 k: 4,229 µV (L12: 4,225) |
| **E4** | al nodo 1,036 / 1,470 / 3,262 Ω; al jack a 1 kHz 58,76 / 59,11 / 60,59 Ω |
| **PSRR** dal rail + | 100 Hz / 1 kHz / 10 kHz: 0 dB 72,12 / 59,57 / 39,78; **+3 dB 69,07 / 56,53 / 36,73**; +10 dB 62,16 / 49,61 / 29,82 dB. Il modo peggiore resta +10 dB, quindi i limiti per tono di **ADR-020** restano validi |
| **Risposta** (`tb_ac`), 1,5 Ω | +3 dB: g1k +3,037 dB, −0,013 dB a 20 kHz rispetto a 1 kHz, −3 dB a **537 kHz**. +10 dB: +9,958 dB, −0,053 dB, 183 kHz |
| **V3** | clipping +13,258 / −13,781 V come L12, continua finale al jack −4,93 mV (L12 −4,92). Le forme d'onda differiscono ≤ 31 mV, su griglie temporali diverse |
| `tb_op` | scarto relativo massimo 1,5·10⁻⁶ contro L12 |
| `tb_blockA_carichi` | 36 righe «XA / XF1 / XF2 min» contro L12: **0** col segno della corrente minima cambiato, scarto ≤ 0,25 % sulle correnti sopra 0,1 mA; buffer 14,548 mA |
| anelli del blocco A e del buffer | curve entro 1,2·10⁻⁴ relativo |
| `tb_uscite_fisse`, Zout a 200 kHz | +1,8 % relativo, per le capacità parassite dei due rami |

**Il transitorio del mute a +3 dB**: al rilascio con segnale il jack arriva a
**7,97 V** di picco, segnale compreso (0 dB 5,61 V, +10 dB 17,41 V). È il
gradino di **NC-028**: il +3 dB sta fra gli altri due, e la voce resta di L29.

## 7. Non conformità

- **NC-022 chiusa.**
- **NC-030 aperta** (minore): `tb_noise_vectors.cir` non scrive dati. Cita
  `onoise_q123`, `onoise_r121`, `onoise_jq110`, `onoise_jq111`, dispositivi che
  l'include di `main` non contiene; ngspice si ferma al primo e esce 0. Il 2g non
  lo vede, perché controlla i dispositivi citati con `@nome[` e `alter`, non i
  nomi dei vettori di rumore.
- **17 voci aperte, 2 bloccanti** (NC-004, NC-017).

## 8. Visto e non toccato

- **`tb_ac.cir`** chiama `fhi` l'angolo basso e `flo` quello alto: i numeri sono
  giusti, i nomi invertiti.
- **`tb_dc_headroom`, `tb_bias_sweep`, `tb_noise_vectors`, controfattuale**: nessun
  dato di L12 con cui confrontarli. Rieseguiti, non confrontati.
- **Il comando delle bobine** («K5 solo insieme a K1») non esiste ancora nel
  repo: sta fuori scheda, con l'alimentatore.
- **Lo slew rate** non è stato rimisurato: C124 e C137 non cambiano, e non esiste
  un deck di slew versionato.
- **Il dossier** legge ancora `data/2026-09-09`.
