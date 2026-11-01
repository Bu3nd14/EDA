# ADR-110 — L'autodiagnosi: Q501 in serie a Q509, i segni che ci sono già e una procedura col tester

Data: 2026-11-01 · Stato: accettata

**Rapporti con le decisioni precedenti.**

- **Chiude il lotto della diagnosi** (L58b) per le righe che ADR-100 gli aveva mandato: 46 righe latenti
  di ADR-071, ADR-076 e ADR-078, e la ritenuta cieca di ADR-109.
- **ADR-076**: il firmware che doveva leggere il mute non c'è più (ADR-102). Al suo posto, per Q501, la
  **ridondanza nel circuito** del suo «Da riaprire se», ma solo per metà: due transistor in serie sul
  comando del jack. I relè di mute restano singoli, e il loro contatto saldato è **accettato**.
- **ADR-071** e **ADR-100**, «Da riaprire se» («un guasto che non si può vedere a un costo
  ragionevole»): portati all'utente coi numeri. Tre restano invisibili e sono accettati.
- **ADR-078** punto 2: lo standby acceso non lo legge il firmware. Lo mostrano i LED che ci sono già, o
  resta accettato.
- **ADR-109 resta com'è** (l'utente: «R585 resta com'era»). In funzionamento AT_F sta a ~0 V, quindi
  il suo secondo «Da riaprire se» (la ritenuta cieca vista a ogni accensione) non scatta.
- **Il PRB non cambia**: nessun LED nuovo (PR-19), nessuna voce nuova.

## Contesto

L58b (`data/2026-11-01/L58b/`, report `reports/2026-11-01-L58b-autodiagnosi.md`) ha misurato, guasto
per guasto, che cosa mostrano le righe latenti. I banchi sono quelli di L58a e L45d2b3b2b2 sul sorgente
di oggi, e ciascuno ridà il suo caso noto alla cifra.

- **Lo standby** (`censimento_psu.csv`):
  - sei modi (Q505 / Q506 in corto, R540 / R536 aperte, R537 in corto, U508 B cieco) lasciano `VRELAY`
    a 12,0 V alla scheda audio a frontale spento, e **i LED del frontale restano accesi**;
  - Q503 in corto e K501 saldato tengono acceso il toroidale coi LED spenti, e la musica arriva a
    17,4 ms invece di 1209 ms.
- **Il mute** (`v2/analisi.csv`): con Q501 in corto D-S o G-D le bobine si eccitano 2,5 ms dopo il
  frontale, coi rail a 0 V. A ogni accensione il jack prende la salita dei rail: principale 70 mV
  (~90 dB SPL), fisse 0,64 / 0,66 V (~110 dB SPL), uguale a rete −10 / +10 %. Il contatto saldato di
  un relè di mute fa lo stesso su quell'uscita.
- **Il blocco** (`censimento_blocco.csv`, il blocco del sorgente):
  - 6 guasti spostano la continua al test point d'uscita di 15–226 mV;
  - 15 portano il riposo dei finali da 20,2 mA a 0, 9,5 o 0 / 39 mA;
  - 3 tolgono il +10 dB;
  - 3 non si vedono (R123 e R144 in corto, R147 aperta);
  - Q132 in corto base-emettitore porta l'uscita al rail, e la sua riga è di L66 (NC-076).
- **La coppia in serie** (`an_s1m.csv`, `an_s1m_rete.csv`, `cens_s1m.csv`): Q501 sopra (drain su
  MUTE_CMD) e Q509 sotto, ogni gate da MUTE_G attraverso la sua resistenza.
  - Con **10 kΩ su tutti e due** il corto gate-drain di Q501 rimanda la corrente delle bobine in MUTE_G
    (~5,6 V) e tiene acceso Q509: il jack si apre a 50 ms invece di 10, dopo il guadagno
    (`an_serie.csv`).
  - Con **1 MΩ sopra e 10 kΩ sotto**:
    - Q501 in corto D-S o G-D, Q509 in corto D-S e le due resistenze aperte danno le cifre della coppia
      sana nei sette eventi e all'inserimento;
    - Q509 in corto G-D lascia l'apparecchio muto;
    - la coppia sana è uguale alla base entro 0,2 ms, a rete −10 / 0 / +10 %.

## Decisione

Parole dell'utente (2026-11-01):

1. **Lo standby**: «si». Bastano i LED che restano accesi e il segno della musica che arriva subito;
   niente LED nuovo.
2. **Il mute**: «accetterei il bump all'accensione, ma mi devi ricordare i dB prima di avere conferma».
   Poi, coi dB: «misura il transistor in serie»; e sulla coppia misurata **«si, metti la coppia nel
   sorgente»**, e sul contatto saldato coi suoi dB **«si»**.
3. **Il blocco**: «si». Una procedura col tester in un documento di diagnosi, e i tre invisibili
   accettati, dichiarati.
4. **R585**: «R585 resta com'era».

Quindi:

- **Q501 in serie a Q509** (2N7002) in `psu.py`: il gate di Q501 da MUTE_G attraverso **R586, 1 MΩ**,
  quello di Q509 attraverso **R587, 10 kΩ**. Tre parti in più. I guardiani (`check_relay_safe_state.py
  --timer`, `check_psu_harness.py`) riconoscono la coppia e chiedono ≥ 1 MΩ sopra; 29 falsi su 29
  (`data/2026-11-01/L58b/falsi/`).
- **Il contatto saldato di K2–K4** resta accettato, dichiarato. Si rivela col mute che non zittisce
  quell'uscita e col colpo all'accensione (~90 / ~110 dB SPL). Il colpo del primo spegnimento dopo il
  guasto resta quello di ADR-076: ~102 dB SPL, fino a ~125 dB SPL se manca la rete o cade un
  regolatore.
- **`docs/preamp/DIAGNOSI.md`**: i segni, il controllo del mute su ogni uscita, la procedura col
  tester (la continua e il riposo di ogni blocco, annotati da nuovo e confrontati), R585 all'ohmmetro a
  scheda spenta.
- **La FMEA**: `data/2026-11-01/L58b/fmea_l58b.csv`, 60 righe; le alte da 9 (8 del mute e R585) a 5
  (K2–K4 e R585, accettate).

## Perché

- **Un guasto di Q501 non dava segni prima del colpo.** Il colpo all'accensione arriva solo dopo il
  primo spegnimento, che dà già ~102 dB SPL. Due parti più una resistenza tolgono il guasto singolo:
  per il colpo ne servono due.
- **1 MΩ e non 10 kΩ**, misurato. Il ritardo che aggiunge non è nel modello del banco (il MOSFET
  generico non ha capacità): dal datasheet (Ciss ≤ 50 pF, la carica di Miller) è ≤ ~0,2 ms, e solo
  quando Q501 spegne da solo con Q509 già in corto. Il sorvegliante ha 1 ms.
- **I relè di mute in più costano tre relè**, ed erano già stati scartati in ADR-076. Il contatto
  saldato si vede al primo uso del mute sull'uscita che si ascolta.
- **Il confronto col valore annotato da nuovo** toglie dal conto la tolleranza della continua, che non
  è mai stata misurata (NC-028). Il calore la sposta di ~0,6 mV, i guasti di ≥ 15 mV.

## Alternative scartate

- **Un LED di «acceso»** dai rail, che avrebbe mostrato Q503 / K501: cambia PR-19. Non scelto.
- **Un rivelatore della continua dei blocchi in hardware** (otto finestre di comparatore): è il
  rivelatore che ADR-081 ha tolto. Non proposto.
- **La coppia con 10 kΩ su tutti e due i gate**: misurata, fallisce col corto gate-drain di Q501.
- **Il comparatore che legge MUTE_CMD contro il comando** e stacca la linea dei relè: nessun canale
  libero sui tre TLV1704, una parte in più da collaudare; la coppia toglie il guasto invece di
  rivelarlo.
- **4 × 10 kΩ per R585** (ADR-109): l'utente l'ha lasciato com'era.

## Da riaprire se

- Il prototipo mostra che il gate di Q501 attraverso 1 MΩ raccoglie disturbi (il mute che sfarfalla), o
  che il ritardo di spegnimento con Q509 in corto supera 1 ms: si torna all'utente con un gate più basso
  e un diodo di blocco verso MUTE_G (misurato prima).
- La lettura in circuito di R585 all'ohmmetro non distingue il corto: la riga resta latente come oggi.
- Sul prototipo la continua o il riposo di un blocco derivano nel tempo più delle soglie di
  `DIAGNOSI.md`: le soglie si rifanno con l'utente.
- L66 rifà la riga di Q132 in corto base-emettitore, o cambia il blocco: le righe del blocco di
  `fmea_l58b.csv` si rileggono sul blocco nuovo.
