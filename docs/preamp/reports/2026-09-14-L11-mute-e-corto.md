# L11 — Mute tenuto e corto sulle uscite (2026-09-14)

Lotto **L11**. Chiude **NC-001** (bloccante). Registra **ADR-021** e
**ADR-022**, apre **NC-028**.

## Le decisioni che il lotto ha registrato

**Dell'utente, 2026-09-13** (parole esatte in NC-001):
- mute tenibile a tempo indefinito;
- ogni uscita regge un corto, requisito come esito e tecnica libera;
- operazionali e microcontrollore ammessi fuori dal percorso del segnale.

**Dell'utente, 2026-09-14,** chieste all'inizio del lotto perché il repo non
le aveva:
- **60 °C** di ambiente nel telaio chiuso;
- **Tj ≤ 125 °C** su ogni dispositivo;
- divisione condizionale del lotto: chiudere L11 intero se la baseline
  reggeva su tutte le vie. Ha retto.

**Proposte nel piano e approvate con esso**: le tre soglie di ADR-022, cioè
ΔZout ≤ 1 Ω, Δrisposta ≤ 0,01 dB e quota ausiliaria di rumore 1 µV RMS.

**Scritte:**
- ADR-021 e ADR-022;
- campo `Stato:` di ADR-003, ADR-009 e ADR-012, e nient'altro di quelle ADR;
- indice di `decisions/README.md`, con in più le righe 017-019 che mancavano;
- `REQUIREMENTS.md`: F6, F7, T1, **P7** e «Nota su P7».

## I numeri di ADR-021, letti dai datasheet in `vendor/`

| Parte | Fonte | RθJA | P ammessa a 60 °C per Tj ≤ 125 °C |
|---|---|---|---|
| MJE15032/33 | MJE15032/D p. 1 | 62,5 °C/W | 1,040 W |
| MMBT5401 | Diodes, Thermal Characteristics, nota 5 | 403 °C/W | 161,3 mW |
| MMBT5551 | Diodes, nota 5 | 417 °C/W | 155,9 mW |
| LS352 | LS350 series Rev A5: 250 mW, declassamento 2,3 mW/°C | 435 °C/W (ricavato) | 149,5 mW per lato |
| LSK489 | Rev A40: 300 mW, declassamento 2,4 mW/°C | 417 °C/W (ricavato) | 156,0 mW per lato |

**SOA delle MJE, guardata sulla pagina renderizzata (Fig. 2).** 16 A in piano
fino a circa 20 V. La curva più lunga pubblicata è quella da 250 ms, ed è
ancora dell'ordine dei 5 A a 28 V. Non c'è una curva DC, quindi oltre i 250 ms
decide il limite termico.

**Il contatto del G6K-2F-Y:** 2 A di conduzione nominale.

## Il deck: `spice/preamp/tb/tb_mute_corto.cir`

**Circuito.** Un canale intero dai due `GAINBLOCK` di `gain_block.subckt`:
- blocco A con attenuatore da 10 kΩ e le due fisse (47 Ω + 4,7 µF + 470 kΩ,
  Singxer 10 kΩ ipotizzato, Stax 50 kΩ);
- blocco B dal cursore, con 47 Ω + 4,7 µF + 220 kΩ e il cj da 100 kΩ.

**Il mute** è modellato come è cablato: **tre** interruttori comandati dallo
stesso segnale, e questo conta. Il mute mette a massa **entrambe** le fisse,
quindi il blocco A vede 47 ∥ 47 Ω. È il caso peggiore del progetto, e G0 non
l'aveva simulato perché aveva un blocco solo con un'uscita.

**Casi e parametri:**
- casi: normale, mute, corto 0,01 Ω a FIX1, a FIX2, a MAIN;
- modalità 0 e +10 dB, a 1 kHz e 20 kHz;
- a 0 dB, ampiezza d'ingresso spazzata 0 / 0,42 / 1,41 / 2,83 / 3,82 V pk;
- a +10 dB fondo scala, manopola spazzata a 0,25 / 0,5 / 0,79 / 1, perché il
  massimo in classe B sta a V_pk ≈ 2·V_cc/π e non al clipping;
- finestra di 4-8 ms dopo 4 ms, e stazionarietà controllata sulle due metà
  (scarto massimo 1,39 %).

**Meccanica provata prima di scriverlo:**
- `@q.xa.q1[p]` dentro un subckt;
- `alter @vin[sin]`;
- `set lista = ( … )` usata da `foreach`;
- `echo … >> file.csv`, che il secondo passaggio di `run_simulation.sh` non
  tocca perché converte solo i `.txt`.

Il `@q1[p]` di ngspice coincide a tutte le cifre con (Vc−Ve)·Ic + (Vb−Ve)·Ib
su un circuito di prova.

`check_deck_refs.py`: 151 citazioni, 75 dispositivi, OK.

## Risultati (topologia di oggi, segnaposto, senza protezione né dissipatore)

| Dispositivo | Caso peggiore | P | Tj |
|---|---|---|---|
| MJE15032/33, blocco A | mute (due fisse a massa), 20 kHz fondo scala | **483,7 mW** | **90,2 °C** |
| MJE15032/33, blocco A | corto su una fissa, 20 kHz fondo scala | 299,5 mW | 78,7 °C |
| MJE15032/33, blocco B | corto MAIN, +10 dB, 20 kHz, k = 0,5 | 347,8 mW | 81,7 °C |
| Q125 carico VAS (MMBT5551) | mute | 87,4 mW | **96,5 °C**, il più caldo |
| Q122 VAS (MMBT5401) | normale | 86,9 mW | 95,0 °C |
| LSK489 per lato | corto MAIN | 20,6 mW | 68,6 °C |

**Tutti dentro.** Il VAS **non** va in saturazione distruttiva: la sua
corrente resta sotto i 4,4 mA, mentre il corto lo carica solo attraverso la
coppia d'uscita.

**Picchi e contatti:**
- I_C di picco: blocco A 160 mA (mute), blocco B 203 mA (corto MAIN e mute a
  +10 dB);
- potenza istantanea massima sulle MJE: 1,55 W, all'inserzione del mute a
  +10 dB, contro 1,44 W a mute tenuto;
- contatti di mute ≤ 153 mA RMS contro 2 A.

**Resistenze → vincoli di distinta:**

| Resistenza | Potenza massima |
|---|---|
| 47 Ω dell'uscita principale | **1,10 W** |
| 22 Ω d'emettitore del blocco B | 0,27 W |
| 22 Ω del blocco A | 0,145 W |
| 47 Ω delle fisse | 0,155 W |
| 10 Ω di base e 91 Ω del VAS | < 6 mW |

**Riposo:** I_C 14,556-14,557 mA, contro 14,557 di
`data/2026-09-10/tb_op-LS352.log`. Classe A in tutte le righe normali.

### Confronto con G0 (topologia THAT320)

Nella stessa configurazione di G0 (blocco B, un mute, 1 kHz, 3,818 V pk):

| | G0 | Oggi |
|---|---|---|
| 0 dB, mute | 65,07 mA | 65,063 mA |
| +10 dB, mute | 203,21 mA | 203,017 mA |
| 0 dB, normale | 14,589 / 14,524 mA | 14,589 / 14,524 mA |
| +10 dB, normale | 17,37 mA | 17,357 mA |

Il nome `@q134` di G0 non esiste più. `tb_blockA_carichi.cir`, rieseguito,
coincide coi dati del 2026-09-09 a quattro cifre (0,01 Ω: 65,456 mA).

## Le tre prove che il risultato non è un deck che passa sempre

1. **Il deck fatto fallire.** Copia senza le tre righe `SMUTE`: le 36 righe di
   mute sono identiche alle normali (0 su 36 differiscono di più dello 0,1 %
   su p_q132), contro 32 su 36 nella baseline, dove lo scarto arriva al
   127 %. Le 4 uguali sono quelle a segnale zero.
2. **Controprova indipendente della potenza.** Stesso caso (corto MAIN,
   +10 dB, 20 kHz), calcolata da tensioni e correnti invece che da `@q[p]` e
   `@r[i]`:
   - Q132: 253,8 contro 253,2 mW;
   - VAS: 52,66 contro 52,57 mW;
   - la 47 Ω: 1,0970 W contro 1,0969 W.
3. **Il deck ha letto la topologia di oggi**: riposo a 14,557 mA come
   `tb_op-LS352`, e l'LS352 compare nel log.

## Sensibilità ai modelli (non di record)

Stesso deck coi modelli vendor di MJE15032/33 e MMBT5401/5551 al posto dei
segnaposto:
- **la corrente di riposo sale a 20,1 mA**. È l'effetto che `gain_block.py`
  prevede: R128 è tarata su Vbe segnaposto;
- MJE peggiore **496 mW** (Tj 91,0 °C);
- Q125 a 97,0 °C;
- la 47 Ω principale a 1,105 W.

**Verdetto invariato.** Il margine resta ampio, ma la cifra va ripetuta quando
la Fase 4 ritara la polarizzazione. NC-024 e NC-025 dicono che i modelli MJE
sono sotto i minimi del datasheet in h_FE e f_T. Qui l'effetto è piccolo
perché le correnti di corto le fissano carico e resistenze, non il guadagno.

## Il transitorio del mute, e la voce che apre (NC-028)

**Inserzione.** Nessun sovraccarico oltre il regime: 1,55 W di picco contro
1,44 W a mute tenuto. Con Zθ(1 ms) ≈ 0,15 × 2,5 °C/W vale meno di +1 °C.

**Rilascio con segnale.** Il 4,7 µF si è caricato durante il mute e il jack
riceve un **gradino**:
- **5,37 V** a +10 dB (picco 17,39 V contro 11,99 V), che decade con
  **τ = 0,320 s** misurata (calcolata 0,323 s);
- **1,79 V** a 0 dB;
- **1,72 V** sulle fisse, con τ = 46 ms.

**Rilascio senza segnale:** picovolt. L'accensione è pulita.

Non è termica, è **V2**, e V2 non ha soglia: da qui **NC-028**, maggiore, con
la domanda all'utente e le forme di rimedio note, non valutate.

## Correzioni di testo

- **`gain_block.py`, commento dello stadio d'uscita.** «Class A is guaranteed»
  diventa «holds under the loads V1 lists», con l'eccezione di ADR-021 e le
  cifre, più il vincolo sulle 22 Ω. AST identico a HEAD (648 → 658 righe); il
  controllo fallisce su una copia con 22 → 22.1.
- **`preamp_audio.py`.** Tre commenti: vincoli sulle 47 Ω, e mute a tempo
  indefinito che non è una protezione. AST identico (281 → 295 righe).
- **`gain_block_draw.py` → `gain_block.svg`.** «Classe A garantita» diventa
  «Classe A coi carichi V1», più «A mute o in corto: classe B (ADR-021)».
  Rigenerato e guardato in anteprima: 44 dispositivi, 100/100 terminali, il
  manifesto non cambia.

## Visto e non toccato

- **I file dati del dossier** leggono ancora `data/2026-09-09`.
- **La R_IN da 1 MΩ nel subckt del blocco B**, dove `preamp_audio.py` non la
  monta: effetto 0,25 % sull'ingresso, dichiarato nel deck. È una differenza
  fra `gain_block.subckt` e il circuito montato, da tenere presente per V5.
- **Le due righe «model type mismatch»** sono preesistenti, dalla riga
  dell'LS350: le ha anche `tb_op-LS352.log`.
