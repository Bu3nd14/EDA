# L54b1 — il temporizzatore a comparatori nel sorgente (2026-10-26)

**Mandato**: ADR-102, punto 3 — il temporizzatore di L54a nel sorgente, il micro e il firmware fuori,
il controllo dei relè, i disegni, il banco sul sorgente. **L54b diviso dall'utente all'inizio, «Tre
parti»**: L54b1 (questo) il sorgente, i guardiani, i disegni e il banco col suo caso noto; L54b2 il
modello del costruttore dei comparatori, lo standby, la catena al jack; L54b3 la robustezza al banco.
Dati `data/2026-10-26/L54b1/` (README).

## Sintesi

- **Il sorgente**: `circuits/preamp/psu.py` ha il temporizzatore di ADR-102 coi valori di `TIMER_AN`,
  ognuno col suo commento verso ADR-102; U509, C534, J515, R543–R547 sono fuori. 166 parti.
- **Il caso noto strutturale**: ogni elemento del banco di L54a ha la sua parte nella netlist e
  viceversa, 47 / 47. **Le reti per piedini**: nessuna rete sopravvissuta cambia piedini o nome.
- **Il firmware è uscito** (`firmware/preamp_timer/`), e con lui il blocco 2k di `run_tests.sh`.
- **I guardiani riscritti** (il controllo dei relè `--timer`, il controllo del cablaggio): 23 falsi su
  23 falliscono, ognuno per la sua regola.
- **I disegni**: lo schematico completo (166 / 166 parti, controllato contro la netlist nei due
  sensi) e il diagramma a blocchi.
- **Il caso noto numerico**: le 34 corse di L54a coi comparatori rifatte sul sorgente tornano — i
  verdetti tutti uguali, gli istanti uguali alla risoluzione del banco, le energie uguali, lo standby
  uguale a quello che il deck di L54a dà oggi.
- `run_tests.sh` **14 passed / 0 failed** (erano 15: il blocco del firmware non c'è più).

## 1. Il sorgente

| Funzione (ADR-102 p. 2) | Parti |
|---|---|
| alimentazione buona: quattro canali sulle soglie del sorvegliante | U513 (A rail +, B rail −, C `VRELAY_REG`, D rete); R569, R570, D533–D535 |
| il rilascio dopo 0,57 s (820 kΩ · 1 µF) | R571, C548, D536 |
| il tasto e il frontale: il nodo filtrato (200 kΩ · 100 nF) | U514 A (alimentazione buona), B (SW3); R572, C549, D537 |
| `MUTE_REQ`, `PERMIT_REQ` ~24 ms dopo (4,7 MΩ · 10 nF) | U514 C, D; R573, R574, R575, C550, D538 |
| il frontale = `VRELAY_EN` (il nodo «acceso») | U515 A; R576 |
| K501 ~84 ms dopo il permissivo (1 MΩ · 100 nF) | U515 B; R577, R578, R579, C551, D539, D540 |
| armato (2,7 MΩ · 1 µF), il timeout dei 2 s | R580, C552, D541 |
| il guasto (100 kΩ · 330 nF) e la ritenuta a tiristore | U515 C, D; R581–R584, C553–C555, Q513 (BC847), Q514 (BC857) |
| il disaccoppiamento dei tre TLV1704 | C545–C547 |

- **Il simbolo**: KiCad non ha il TLV1704; il simbolo LM339 è il suo pinout piedino per piedino (il
  contenitore PW, SBOS589D p. 5, letto dal PDF in `vendor/`), come l'LM2903 sta per il TLV1702 di
  U505–U508. Impronta TSSOP-14 (il TLV1704 c'è solo in quella). Il TLV170x regge 40 V sui 5 V: il
  commento di U504 lo dice (prima c'erano i 6 V dell'ATtiny).
- **AT_ON è `VRELAY_EN`**: il banco li univa con 1 Ω (`RATve`) solo per sondarli.
- **I numeri dei riferimenti**: i primi scelti (C537…, R556…, Q507 / Q508) erano già stati usati
  sulla scheda dal pilota delle fotoresistenze fino a L47c1, e i report vecchi li nominano per altre
  parti. `riferimenti_storici.py` legge ogni versione di `psu.net` in git: le parti nuove stanno su
  numeri mai usati (U513–U515, C545–C555, R569–R584, D533–D541, Q513 / Q514).
- **I dielettrici** non sono decisi: i condensatori dei ritardi sono 1206, perché un C0G ci stia
  dove il Monte Carlo di L54b3 lo chiederà.
- ERC: 19 avvisi (−6 piedini liberi e −1 massa del micro, +3 masse dei TLV1704), i 2 «errori» noti.

## 2. I guardiani

`check_relay_safe_state.py --timer`: la condizione 1 di ADR-022 resta (col temporizzatore spento
ogni relè a riposo), le regole cambiano soggetto.

| Regola | Cosa chiede |
|---|---|
| T0 | nessun micro sulla scheda; ogni comparatore è di un simbolo che il controllo sa leggere (limitations #68) |
| T1 | ogni MOSFET di comando ha la sua resistenza gate-source (come prima) |
| T2 | ogni richiesta c'è, ha il pull-down, ed è pilotata solo da uscite open-drain di comparatore (o dalla ritenuta); nessun'altra alimentazione la raggiunge sotto 1 MΩ |
| T3, T3b | i ritardi Δ e Δ₂ su RC; nessuna richiesta scavalca il suo RC (come prima, con le richieste al posto dei piedini del micro) |
| T4, T5 | `MUTE_G` ≤ `PERMIT_G`; `PERMIT_T` carico da `MUTE_REQ`, `VR_T` da `PERMIT_T` (come prima) |
| T6 | la ritenuta: una coppia NPN / PNP a tiristore, l'anodo su `VRELAY_EN`, resistenza e condensatore su ogni base-emettitore, l'innesco da un'uscita di comparatore della logica di guasto, non da una richiesta |

`check_psu_harness.py`: le quattro richieste da uscite di comparatore, nessun micro. `falsi/
verdetti.txt`: il micro rimesso, un comparatore sconosciuto, un operazionale al posto di un TLV1704,
i pull-down tolti, un pull-up da `VRELAY_REG`, una richiesta oltre il suo RC, la ritenuta spezzata,
l'anodo su V5, i condensatori base-emettitore tolti, l'innesco da `MUTE_REQ`… 23 su 23 falliscono.
Il falso dell'innesco da `MUTE_REQ` ha fatto correggere T6 mentre lo scrivevo: `MUTE_REQ` è anche
lei un'uscita di comparatore, e la prima versione l'avrebbe accettata.

## 3. I disegni

Lo schematico completo (`docs/preamp/schematic/psu_draw.py`): il pannello 5 è il temporizzatore in
tre colonne (U513 e i suoi diodi, poi il frontale e SW3; U514 e le richieste, poi K501 e l'armamento;
U515, il guasto e la ritenuta disegnata a tiristore); il pannello 4 è più stretto senza le riletture
del micro, la legenda è passata nel pannello 1. Il disegno passa i rifiuti del kit (nessun corto,
nessun filo su una parte, un nome su ogni isola, nessun testo sopra un altro) e il manifesto
corrisponde alla netlist nei due sensi. `PREVIEW_PNG` scrive ora l'anteprima anche prima dei
controlli, per guardare una pagina rifiutata. Il diagramma a blocchi asserisce che non c'è un micro
e che le quattro richieste escono dai TLV1704.

## 4. Il banco sul sorgente e il suo caso noto

`genera_tb_psu.py --timer sorgente` prende il temporizzatore da `psu.net` (LM339 → quattro `CMPOD`,
gli stessi di `TIMER_AN`). Le modalità di L54a rifiutano una netlist col temporizzatore, che
raddoppierebbero; coi vecchi argomenti il deck è quello di L54a byte per byte. I criteri sono stati
scritti nel README prima delle corse.

| | L54a | sorgente |
|---|---|---|
| sequenza, 24 casi | — | 21 identici; 3 a rete −10 % col guadagno a 55,4 invece di 55,5 ms |
| guasti, 7 casi | — | 7 identici |
| R550, corto davanti al regolatore + (rete 0 / +10 %) | 7,65 / 9,35 J | 7,651 / 9,347 J |
| R552, bobina di K501 in corto | 0,47 / 0,54 J | 0,473 / 0,539 J |
| standby da T2 (−10 / 0 / +10 %) | 116,7 / 130,1 / 145,1 mW | 116,14 / 130,08 / 144,21 mW |

- **I 0,1 ms del guadagno** sono fuori dal limite di 0,05 ms che avevo scritto: **il limite era sotto
  la risoluzione del banco**, che scrive le forme d'onda ogni 100 µs. Sulla griglia di 10 µs il deck di
  L54a e quello del sorgente danno gli stessi istanti (guadagno 55,4 / 55,4 ms, jack 17,31 / 17,31,
  K501 162,13 / 162,14).
- **Lo standby a ±10 %** è fuori dallo 0,5 % che avevo scritto (−0,61 % a +10 %). Il deck di L54a,
  rifatto oggi sulla netlist di prima, dà **116,14 / 130,08 / 144,21 mW**, gli stessi del sorgente: a
  non tornare sono le cifre stampate da L54a e riportate nella tabella di ADR-102, di al più 0,9 mW.
  Nessuna decisione ne dipende (il «Da riaprire se» di ADR-102 è a 0,5 W); **lo standby di partenza
  per L54b2 è 116,1 / 130,1 / 144,2 mW**.

Con quelle due spiegazioni, il caso noto torna: il sorgente è il temporizzatore che L54a ha provato.
Questo vale anche come i casi di L54a «rifatti sul sorgente» che il prompt di L54b chiedeva, col
modello comportamentale dei comparatori; quello del costruttore è di L54b2.

## 5. Cosa resta fuori, e dove va

- **L54b2**: i comparatori col modello del costruttore contro il comportamentale sui casi della
  sicurezza; i pull-up delle uscite tenute basse alimentati solo da acceso (NC-037); la catena al jack
  dello spegnimento dal frontale e della perdita di rete, in dB SPL.
- **L54b3**: la robustezza al banco (sotto, parola per parola).
- **L58**: le righe della FMEA delle parti nuove e la diagnosi in hardware.
- Non toccati: la scheda audio, il PRB, i requisiti, le non conformità (NC-037 resta aperta, la sua
  cifra si muove in L54b2).

## Per L54b3

Il punto 7 del prompt di L54b (richiesta dell'utente dopo L54a, 2026-10-26), parola per parola:

> 7. **La robustezza del temporizzatore, al banco e non al prototipo** (richiesta dell'utente dopo L54a,
>    2026-10-26: «il prototipo è molto costoso, dobbiamo cercare di accorgerci al banco delle simulazioni
>    dei problemi, il primo prototipo deve essere usabile»; ADR-102 lasciava al prototipo l'immunità ai
>    disturbi). I criteri si scrivono prima delle corse; per ognuno: niente scatto a vuoto
>    dell'accensione, del mute o della ritenuta, e lo scatto quando deve:
>    - **la rete**: cali lenti (brown-out) a −15 / −20 / −30 % per 0,1–2 s; buchi di ½, 1, 3, 10 periodi;
>      una sovratensione +15 %; la rete che torna mentre i rail scendono; tutto alle tre reti;
>    - **i disturbi veloci**: fronti ripidi su `VRELAY_REG` e su V5 (K501 che chiude, i relè della scheda
>      audio che commutano, il carico di `VRELAY` a gradino): la ritenuta a due transistor non si innesca
>      da sola; il suo 1 nF base-emettitore dimensionato coi numeri, non a sentimento;
>    - **i rimbalzi** del frontale e di SW3 con forme di rimbalzo vere (treni di 1–5 ms);
>    - **le tolleranze**: un Monte Carlo sugli RC dei ritardi (resistenze ±1 %, condensatori secondo il
>      dielettrico, ±5 % C0G / ±20 % X7R con la tensione) e sulle soglie e gli offset dei comparatori:
>      ogni tempo nei suoi limiti (il permissivo ≥ 16,9 ms dopo il mute, la musica ≥ 500 ms dopo la
>      rete, K501 ≥ 50 ms dopo il permissivo, il timeout ~2 s, la ritenuta armata), col caso peggiore
>      dichiarato;
>    - **la temperatura** a 0 e 60 °C, coi transistor della ritenuta e i comparatori del costruttore;
>    - al prototipo resta solo ciò che non si simula (i disturbi irradiati, il layout), detto per nome.
>    Se una prova fallisce, il rimedio si porta all'utente coi numeri prima di cambiare il circuito.

Nel sorgente i due 1 nF base-emettitore della ritenuta sono C554 (Q513) e C555 (Q514).
