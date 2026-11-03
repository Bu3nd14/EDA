# L64a — il dossier rigenerato, la scheda audio

Date: 2026-11-02/03 · Lotto: L64a (la prima delle tre parti di L64) · Decisioni: **ADR-113** (PR-24
riscritta). Dati: `data/2026-11-02/L64a/` (README). Nessuna non conformità aperta o chiusa. Il
circuito non è cambiato.

## In breve

- **Le scelte dell'utente**: all'inizio, **«Three parts, like last time»** (L64a la scheda audio,
  L64b l'alimentatore e il temporizzatore, L64c gli schemi, la FMEA, le schede di prova, «Cosa non
  dice», la consegna in PDF); le sedici righe `Stato:` proposte, **«Yes, use these sentences»**;
  PR-24, **«Rewrite the promise»** (ADR-113). In sessione: **«cerca di non caricare al massimo la
  CPU»** e, offerto di salire la notte, «lasciali così, è un Air senza ventole» (al più 3
  simulazioni insieme, a priorità bassa; in memoria).
- **Il generatore non girava** sul progetto di oggi: il contratto (ADR-087, 088, 089 fuori
  dall'indice; nove stati diversi fra file e indice), il deck V2 di L51a, il blocco della
  distorsione di L51c, e tutto l'alimentatore (R512 e i deck che non si rigenerano più: è L64b).
- **La pagina di L64a ha la sola scheda audio** (`PARTI = ("audio",)`), e il generatore la scrive
  solo fuori dal repo; passa: «OK: tutti i controlli incrociati sono passati». **Sabotaggi 24 su
  24** (`data/2026-11-02/L64a/sabotaggi.txt`); il primo giro ne ha fatto passare uno e ha trovato
  un buco: gli scatti contro L48b confrontavano il solo gradino peggiore, non il nominale. Corretto.
- **Le cifre di oggi**, tutte lette dai dati: V1 ≥ **64,87°** (64,11° col bilanciamento); E3 ≥
  **105,3 kΩ**; E5 ≤ **5,43 µV**; F1 **19,8 µV** fino a 100 mV di continua; PSRR peggiore **85,5 dB**
  a 10 kHz; Zout al jack 57,9 Ω a 1 kHz; V2 del mute **250 verdetti su 250**, il picco giudicato più
  alto 82,34 µV contro 100; V4 sul blocco a 27 °C THD 20 kHz **0,000447 %**, a caldo (57 °C d'aria)
  **0,000725 %**, sulla catena 0 fuori per blocco (margine 1,3 dB); P7 coi dissipatori ≤ **69,3 °C**
  a regime, **121 °C** sul peggiore dei 714 guasti del blocco; la Stax ≤ **124,5 ms** contro 150.

## Il contratto

Il controllo del punto 14 rifiutava dodici volte. Le sedici righe `Stato:` (le dodici più quattro
trovate leggendo: 072, 079 e 080, superate dal rivelatore che esce, ADR-081; 105, superata in una
parte da ADR-108), scritte uguali nel file e nell'indice da `script/stati.py`. ADR-087, 088 e 089
aggiunte all'indice col titolo del file.

Con ADR-049 «superata da ADR-102» il controllo ha trovato PR-24, che la citava da sola e prometteva
la sicurezza «con il micro bloccato o in reset»: un micro non c'è più. **ADR-113** riscrive la voce:
«La sicurezza non dipende da un programma. Non c'è un microcontrollore: accensione, ritardi e mute
sono fatti da comparatori e relè, e il guadagno non può cambiare con le uscite collegate.» F7 in
`REQUIREMENTS.md` dice ancora «senza firmware»: lo segna il «Da riaprire se» di ADR-113.

## Le corse e la seconda strada

| Che cosa | Prima strada, oggi | Seconda strada |
|---|---|---|
| i 21 deck veloci | `dopo/`, 24 su 24 rc 0 | le **10 503 misure** dei 20 deck uguali alla sesta cifra alla regressione di L66 sulla variante lim365 (il blocco uguale a quello di oggi a meno dei commenti) |
| `tb_mute_corto` | `dopo/` | il deck di L66 ricorso (`l66_mute/`): **32 200 misure su 32 200**; i CSV di oggi uguali (le potenze riga per riga). Le misure per occorrenza non bastavano: L66 ripete gli stessi nomi di `.meas` |
| il selettore, le due copie col bilanciamento | `dopo/` (le copie rigenerate dai deck di oggi: quelle di L48b non hanno il limitatore d'ingresso) | gli stessi deck col blocco dei file della variante di L66: byte per byte |
| la matrice di V2 | **intera**, 155 corse, 154 rc 0 (`off_r10m_d20_iii` abortisce, esclusa da L29d2), la guardia 154 su 155 | L60d2, cella per cella: **gli stessi esiti** |
| gli scatti del volume | il banco di L48b col limitatore, varianti 0 e 4 | L48b: entro lo 0,43 % sopra 100 µV, entro 0,02 µV sotto |
| i falsi del 2e | ricorsi sulla netlist di oggi: 10 su 10, 7 su 7 | — (il caso «main» di L48b esce: la netlist di prima non ha R179) |
| V4, il blocco a 27 °C | il banco di L46b sul blocco di oggi | L51c (il blocco di allora): gli scarti si scrivono, al più 4,9 dB sulla THD |
| V4 a caldo e sulla catena | L66, L67 | le 48 THD rifatte da L67; la regola di ADR-112 riscritta nel generatore |
| il limitatore, i guasti del blocco, la Stax | dopo-L57b, L66, L45d2b3b3 (eccezioni dichiarate) | il costo contro la sintesi; le Tj rifatte dalla potenza; i tempi della Stax coerenti |

## Trovato

- **22 celle della matrice di V2** (la dispersione, `dpminmax` e `dpmaxmax`) non trovano il punto di
  lavoro sul blocco di oggi in nessuna delle tre prove di `corri.sh` (rc=OPT); in L60d2 sì. È
  limitations #86. Coi `.nodeset` dei 36 nodi interni del blocco da solo (L67) convergono tutte. La
  prova su tre celle che convergono anche senza: le onde coincidono sotto 1 µV fino all'evento, poi
  lo scatto del contatto si sposta di un passo; **le grandezze di V2 si spostano al più di 0,64 µV**.
- **La continua propria del blocco A** è −2,888 mV (L48b −6,623 mV, ADR-056 −6,6): il blocco, non
  il limitatore (con 1 kΩ al posto del limitatore la stessa cifra).
- **B2g nelle celle del cambio di guadagno** si sposta da L60d2 a oggi fra il pavimento (~1 nV) e
  ~13 µV, nelle due direzioni (`gm3x10_20_iii_c` 12,7 µV → 0,6 nV; `gm0x3_20_iii_c` 0,7 nV →
  8,9 µV). Tutto ≥ 18 dB sotto il tetto; il picco più alto della matrice non cambia (82,35 →
  82,34 µV). Da guardare in L65.
- **L'eccezione dell'interblocco** di L51a aveva una ragione falsa («gain_interlock.py non è cambiato
  dopo L35»: L41a ha portato le bobine a 12 V). Riscritta: la corsa di L36 prova la struttura.
- **La colonna «p10» dei CSV della Stax** è giudicata contro 100 ms (`LIMITE_P10_MS` di L45b): il
  dossier legge il tetto, 150 ms, da `REQUIREMENTS.md`.
- **NC-075** (aperta): C145 in corto, R144 / R152 a 11,23 W, in tutte le posizioni; il dossier lo
  dice con la sua non conformità.
- Lo scatto del trim, a +10 dB, è ancora **86,1 dB SPL** di picco (come L48b): il trim si muove solo
  col mute inserito.

## Errori

- La matrice è partita a 7 corse insieme, sopra quello che l'utente voleva: fermate quattro corse e
  ripartita a 3.
- Alla ripresa dopo il riavvio, `seleziona.py` rifiutava la selezione senza i riferimenti e
  `corri.sh` è ripartito sulla lista intera (le 22 celle comprese): fermato subito, `resto_v2.py`
  ora nomina i riferimenti.
- Il primo confronto delle misure di `tb_mute_corto` accoppiava misure diverse (4523 «diverse»):
  era il metodo, non il circuito.
