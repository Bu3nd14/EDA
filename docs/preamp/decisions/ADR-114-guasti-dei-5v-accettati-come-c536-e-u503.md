# ADR-114 — I guasti dei 5 V col temporizzatore di oggi: i pull-up degli interruttori in corto accettati come C536, i 5 V persi al jack accettati come il corto di U503

Data: 2026-11-03 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Estende ADR-097, punto 2** («Accettare la protezione»: i corti dei 5 V a massa affidati allo
  spegnimento termico del regolatore) a R517 e R518 in corto.
- **Estende ADR-051** (il corto della linea a 12 V dei relè accettato sotto il tetto, il colpo di
  `corto_u503`) ai guasti che tolgono i 5 V: C536 in corto, U512 spento.
- **Prende atto di ADR-102** (il micro esce): le righe della FMEA che lo nominavano sono riscritte
  dalle corse del circuito di oggi (L64c).

## Contesto

Rigenerando il dossier (L64c, 2026-11-03) la FMEA di oggi aveva ancora righe scritte col micro: le
dieci del sorvegliante dei rail accettate con ADR-073 (la riserva del firmware, superata da ADR-102),
le sedici «letture del micro» di L45c2 (R517, R518, R541, R542, C532, C533, R543, R544–R547), e C536
in corto e U512 spento («il micro si spegne»). L'utente: **«Riscriverle ora»**. Le corse sono quelle
del banco di L64b sul circuito di oggi (`data/2026-11-03/L64c/`): i dodici modi degli ingressi del
temporizzatore contro l'accensione, lo spegnimento dal frontale e il mute dal frontale (36 corse),
C536 in corto e U512 spento alle tre reti (6), i due canali ciechi del sorvegliante (2, uguali a
L64b colonna per colonna); la catena fino al jack di L64b per i 5 V persi e per i canali ciechi.

Due righe cambiano verso l'alto:

- **R517 in corto, R518 in corto** (i pull-up da 100 kΩ di `MUTE_SW` e `FRONT_SW`): con
  l'interruttore chiuso i 5 V vanno a massa attraverso 0,1 Ω e l'interruttore; U504 limita la
  corrente e dissipa **2,93 W, 241 °C** a calcolo (60 °C d'aria, 62 °C/W; `calore_5v.csv`), contro
  125 °C; R518 porta anche U512 a 128 °C. Il temporizzatore resta senza alimentazione: niente musica,
  K501 aperto, nessun colpo. È il caso di C536 in corto (2,99 W, 246 °C, rifatto qui uguale a
  L45d2b3b1), che ADR-097 aveva accettato. Gravità 5, priorità alta. Probabilità 1 (0,025 FIT).
- **I 5 V persi** (C536 in corto, U512 spento): i relè cadono tutti insieme, il guadagno si muove a
  3,5 ms e il jack si stacca a 6,6 ms, **3,1 ms col jack collegato**; al jack principale **6,51 mV,
  69,7 dB SPL di picco a 1 m**, uguale alle tre reti (`catena/tabella_l64c.csv`). Il controllo della
  catena, `corto_u503` di L64b, ridà i suoi 6,492 mV. Sopra l'obiettivo di ADR-046 (2 mV, ~60 dB),
  sotto il tetto (0,87 V, ~112 dB): gravità 3. La riga di U512 spento (probabilità 3) passa da bassa
  a media.

## Decisione

Le scelte dell'utente (2026-11-03, L64c):

1. **«Accettare come C536»**: R517 e R518 in corto restano «i 5 V persi», col regolatore che porta il
   corto protetto dallo spegnimento termico del costruttore (MCP1703A, 150 °C). La potenza e la
   temperatura si scrivono nella riga, che resta ad alta priorità e accettata.
2. **«Accettare come U503»**: il colpo dei 5 V persi, 69,7 dB SPL, è accettato sotto il tetto come
   quello della linea dei relè in corto (ADR-051).

Il circuito non cambia.

## Perché

- **Il meccanismo è quello già accettato.** Un corto dei 5 V a massa, da qualunque parte venga,
  porta U504 nel limite di corrente: C536 lo fa fra i due regolatori, R517 / R518 attraverso
  l'interruttore. Lo spegnimento termico è il modo in cui il regolatore è fatto per sopravvivere.
- **Lo stato sicuro tiene.** Senza 5 V i relè cadono: il mute si inserisce, K501 si apre.
- **Il colpo è quello di U503 in corto**, alla cifra: la stessa sequenza (tutti i relè giù insieme),
  lo stesso picco al jack.

## Alternative scartate

- **Una non conformità sui pull-up**, da chiudere con una resistenza in serie a ogni interruttore
  prima del layout: offerta, non scelta. Resta un'opzione al layout.
- **Una non conformità minore sul colpo dei 5 V persi**: offerta, non scelta.

## Da riaprire se

- La parte scelta per U504 / U512 non ha lo spegnimento termico, o il suo datasheet non lo garantisce
  in un corto continuo.
- Al layout la rete degli interruttori si allunga o esce dal pannello in un modo che rende probabile
  un corto dei pull-up (un cablaggio volante, un connettore).
- Il prototipo dà al jack un colpo dei 5 V persi sopra 0,87 V (~112 dB SPL).
