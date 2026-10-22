# ADR-096 — La retroazione dei regolatori dei rail resta sul piedino, prima del diodo in serie: misurata

Data: 2026-10-22 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Conferma il punto 2 di ADR-093** («La retroazione resta sul piedino») e con esso il punto 3 (la
  tensione impostata a ~15,3 V). ADR-093 non cambia. Aggiunge la misura che allora mancava: ADR-093
  scartava la retroazione sul rail per «un rischio di stabilità che il banco comportamentale non vede».
- La scelta è stata **riaperta dall'utente** (2026-10-22, «non sono certo sia la scelta giusta,
  indipendentemente da cosa dice l'ADR»), non da un «Da riaprire se» scattato.
- La soglia del margine di fase è quella di **PR-7** (≥ 60°), presa a prestito dal blocco di guadagno:
  il contratto non ne fissa una per i regolatori.

## Contesto

Dal banco di L45d2b3a (`data/2026-10-22/L45d2b3a/`, README).

- **Il modello del costruttore di TPS7A4701 ora gira.** L41a l'aveva lasciato «DO NOT USE», con
  l'uscita a ~1,0 V qualunque fosse la taratura. La causa: ngspice senza modo di compatibilità non legge
  `LIMIT` come PSpice (limitations #72). Con la terza patch il modello dà **15,294 V** a 0,3 A con la
  taratura di U501, e **3,34 mV** sul gradino della figura 5-19 (circa 5 mV di picco e circa 3 a regime
  sulla figura, letti a occhio). Il derivato sta in `models/ldo_regulator/` e `validate_models.py` lo
  controlla.
- **Ma nessuno dei due modelli del costruttore dice la banda del regolatore vero.** TPS7A4701:
  l'uscita vale V(NR) × V(OUT) / V(SENSE) dietro un ritardo di 1,6 µs e 4 mΩ. Con SENSE sull'uscita il
  rapporto vale 1 e **l'anello non c'è**; con SENSE altrove è un integratore che attraversa a ~94 kHz,
  e nessuna curva del datasheet lo conferma. TPS7A3301: la stessa forma senza nemmeno il ritardo,
  **nessun anello**: U502 non ha un numero del costruttore.
- **Quindi il margine si misura due volte**:
  - col modello di TI sul + (banda ~94 kHz);
  - con un regolatore generico a un polo su tutti e due i rail, la banda da 10 kHz a 1 MHz.

  La rete è quella vera, con le grandezze che non si conoscono fatte variare:
  - l'ESR della tenuta da 10 a 60 mΩ, quello della scheda audio 0,05 e 0,2 Ω per condensatore;
  - il cavo verso la scheda audio assente, o 20 mΩ e 200 nH;
  - il carico 0,3, 0,1 e 0,03 A, come generatore di corrente;
  - la temperatura 0, 25 e 60 °C.

  Lo strumento è stato provato su due anelli noti: 90,00° e 22,54° contro 22,55° calcolati a mano.

| | Sul piedino (oggi) | Sul rail, dopo il diodo |
|---|---|---|
| margine di fase, modello di TI, carico di regime (48 casi) | **90,1–90,9°** | **51,0–108,8°**, 9 sotto 60° |
| margine di fase, modello di TI, tutti i carichi (144 casi) | 88,8–90,9° | 20,6–108,8°, 82 sotto 60° |
| margine di fase, generico, carico di regime, banda 10 k / 100 k / 1 MHz | 90° (il piedino è pilotato) | 22–58° / 32–95° / 59–97° |
| margine di fase, caso nominale (TI / generico a 94 kHz) | 90,3° / 90° | 58,9° / 43,9° |
| il caso peggiore | — | condensatori a ESR bassa (10 mΩ), scheda calda |
| tensione del rail (TI, nominale) | 14,974 V (segue la Vf, ±0,03–0,05 V) | 14,995 V |
| impedenza del rail sotto 100 Hz (TI, nominale) | 0,13 Ω (0,05 a 1 kHz) | ~4 mΩ (la resistenza del modello) |
| gradino di 50 mA sul rail (TI, nominale) | 6,3 mV, fermo | 0,5 mV |
| rumore del regolatore sul rail | filtrato dal diodo con la tenuta: −8 dB a 1 kHz, −20 dB a 10 kHz | non filtrato fino alla banda dell'anello |
| calore e riserva del regolatore | invariati (il piedino a ~15,3 V in tutte e due) | invariati |

- **Il beneficio della forma sul rail non tocca nessun requisito.** La diafonia che passa per il rail è
  circa Z_rail / R_carico. Già con un carico di 1 kΩ, 0,13 Ω e nessuna reiezione del blocco fanno
  −78 dB. Con la reiezione del blocco (oltre 70 dB, ADR-056) si va sotto −140 dB, contro i −70 dB di
  PR-10. E il blocco è in classe A (PR-4): la corrente del rail segue poco il segnale.

## Decisione

Parole dell'utente (2026-10-22): **«Sul piedino»**.

1. **La retroazione dei due regolatori resta sul piedino d'uscita**, prima di D515 / D516: SENSE di U501
   su `VPLUS_REG`, il partitore R501 / R502 e C513 di U502 su `VMINUS_REG`. U501 resta a 15,3 V e R501
   a 120 kΩ. Il circuito non cambia.
2. **Il modello del costruttore di TPS7A4701 entra in `models/`** (`ldo_regulator/tps7a4701_ngspice.lib`):
   è buono per il punto di lavoro, l'accensione e la regolazione di carico. **Un margine di fase
   ricavato da lui è del modello, non della parte.**

## Perché

- **È la configurazione del costruttore**, e lì il margine non dipende da niente che il progetto non
  controlla: 89–91° in ogni caso col modello di TI.
- **La forma sul rail scende sotto i 60° proprio dove il progetto non ha presa**: con un ESR della tenuta
  basso, cioè con condensatori migliori o più caldi; e il margine dipende da una banda del regolatore
  che nessuno conosce. È un rischio che il prototipo non toglierebbe: un elettrolitico cambia ESR con la
  temperatura e con gli anni.
- **Quello che la forma sul rail guadagna non serve**: 15,00 V invece di 14,97 V, e un rail più rigido
  dove la diafonia è già 70 dB sotto il requisito. Il rumore va dalla parte opposta: col diodo fuori
  dall'anello la tenuta filtra il regolatore.

## Alternative scartate

- **La retroazione sul rail** (sopra).
- **Sul piedino, con due ponticelli per provare l'altra forma sul prototipo**: due parti e due piste per
  una misura che non può dire come cambierà l'ESR. Non scelta dall'utente.

## Da riaprire se

- Un requisito nuovo chiede la tensione del rail entro meno di ±0,05 V, o un'impedenza del rail sotto
  0,1 Ω nella banda audio.
- Il costruttore pubblica un modello con la dinamica d'anello vera di TPS7A4701 o TPS7A3301, o una nota
  applicativa sul rilevamento remoto attraverso un diodo: allora la forma sul rail si rimisura con quello.
- La misura dell'impedenza del rail sul prototipo (il «Da riaprire se» di ADR-093) dà diafonia o rumore
  fuori dal contratto.
