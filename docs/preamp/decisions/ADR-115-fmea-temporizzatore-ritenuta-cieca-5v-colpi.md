# ADR-115 — La FMEA del temporizzatore a comparatori: la ritenuta cieca accettata come R585, i 5 V a massa come C536, i colpi da test point e da J4 sotto il tetto

Data: 2026-11-03 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Estende ADR-109** (R585 in corto, la ritenuta cieca, accettata in P9 (e)) ai 31 guasti singoli del
  temporizzatore che fanno la stessa cosa. **P9 (e)** si allarga a quei guasti.
- **Estende ADR-114** (e ADR-097, punto 2: i corti dei 5 V a massa affidati allo spegnimento termico del
  regolatore) a C545, C546, C547 in corto e al test point dei 5 V (TP507) a massa.
- **Estende ADR-051** (il colpo della linea dei relè in corto accettato sotto il tetto) ai colpi al jack di
  un pin di J4 aperto e dei test point in corto verso la massa vicina.
- **Non decide R572 / R576 in corto**: l'utente li ha mandati a una non conformità (**NC-079**, maggiore,
  prima di G1).
- Chiude il lavoro di **NC-078** (L68).

## Contesto

L64c ha trovato che la FMEA non aveva righe per 37 parti del temporizzatore a comparatori (ADR-102), 5
connettori e 17 test point dell'alimentatore (NC-078). L68 (`data/2026-11-03/L68/`, report
`reports/2026-11-03-L68-fmea-temporizzatore.md`) le ha scritte dal banco di L64c sul circuito di oggi, che
non cambia: 79 simulazioni distinte del temporizzatore contro i sette eventi e il mute dal frontale (632
corse), 4 dei connettori, 13 test point in musica, la catena al jack su 20 casi (il controllo `corto_u503`
ridà 6,492 mV), il calore dei regolatori dei 5 V su tutte le corse. 125 righe, 34 alte.

Tre gruppi di righe stanno fuori dal criterio:

1. **La ritenuta cieca, 31 righe.** U513 canali A e B ciechi e la sua alimentazione persa; U514 canale D
   cieco e la sua alimentazione persa; U515 canale B cieco, canali C e D bloccati bassi; Q513 e Q514 aperti
   e in corto base-emettitore (con R583 / C554, R584 / C555 in corto); D533, C552, C553 in corto; R569,
   R574, R578, R580, R581, R582 aperte; R570, R571, R573, R575, R579, R582 in corto. Ognuna, da sola, lascia
   **K501 chiuso** dopo un guasto di un rail con la rete presente (in musica o all'accensione), mentre il
   mute si inserisce come nella corsa sana e il jack resta muto. È P9 (b) non rispettato, come **R585 in
   corto** (ADR-109). Gravità 4; probabilità 1 (2 per i canali dei comparatori); rilevabilità 3, latente, o
   2 dove il guasto si vede anche senza un rail che cade (lo standby che non spegne). 28 alte, 3 medie.
2. **I 5 V a massa**: C545, C546, C547 in corto (U504 2,99 W, 245 °C a calcolo; non si accende) e una sonda
   da TP507 a massa in musica (U504 232 °C, U512 132 °C; i relè cadono insieme, 69,7 dB SPL). Il meccanismo
   di C536 in corto. Gravità 5, alte.
3. **I colpi al jack sopra l'obiettivo** (2 mV, ~60 dB SPL), tutti sotto il tetto (0,87 V, ~112 dB SPL):
   **69,7 dB SPL** (6,49–6,51 mV, il colpo di U503 in corto) quando si stacca il pin PERMIT_CMD di J4 in
   musica, o una sonda mette a massa VRELAY, VRELAY_REG, PERMIT_G, PERMIT_T, VR_G (TP504, TP505, TP509,
   TP510, TP516); **97,0 dB SPL all'uscita fissa 1** (0,15 V) con una sonda sul rail − (TP502), e per
   simmetria sul rail + (TP501: la corsa si ferma 4 ms dopo il corto, dichiarato). Gravità 3, basse.

## Decisione

Le scelte dell'utente (2026-11-03, L68):

1. **«Accettare come R585»**: le 31 righe della ritenuta cieca sono accettate in **P9 (e)**, come R585 in
   corto. Restano alte (o medie), accettate.
2. **«Accettare come C536»**: i 5 V a massa da C545–C547 e da TP507 restano «i 5 V persi» col regolatore
   protetto dallo spegnimento termico del costruttore (MCP1703A, 150 °C).
3. **«Accettare tutti»**: i colpi a 69,7 dB SPL come quello di U503 in corto (ADR-051); i 97 dB SPL del rail
   a massa da un test point come guasto di servizio sotto il tetto, dichiarato.
4. **R572 / R576 in corto: «Non conformità maggiore»** (NC-079).

Il circuito non cambia.

## Perché

- **La ritenuta ha un canale solo**: ADR-102 l'ha fatta con un innesco (AT_F), un'armatura (AT_T2S) e due
  transistori, senza ridondanza; R585 in corto (ADR-109) era il primo caso trovato, non l'unico. Il mute,
  che è ciò che protegge il jack, ha la sua strada (il sorvegliante su MUTE_G) e regge in tutti i 31 casi.
- **I 5 V a massa sono un meccanismo già accettato**, da qualunque parte venga il corto (ADR-114).
- **I colpi sono sotto il tetto** e hanno la cifra di un caso già accettato (U503 in corto); i 97 dB SPL
  richiedono una sonda sul rail, cioè l'apparecchio aperto durante la musica.

## Alternative scartate

- **Una non conformità sulla ritenuta cieca** (maggiore, con un rimedio prima di G1, per esempio una seconda
  via per K501; o minore): offerte, non scelte.
- **Una non conformità sui 5 V a massa** o **sui colpi**: offerte, non scelte.

## Da riaprire se

- Il prototipo mostra un guasto della ritenuta più probabile dei tassi di tabella (ADR-070), o il layout
  rende probabile un corto fra AT_F, AT_T2S, AT_MT e la massa.
- La parte scelta per U504 / U512 non ha lo spegnimento termico (come ADR-114).
- Al layout i test point dei rail stanno accanto a un punto di massa su cui una sonda scivola facilmente:
  allora i 97 dB SPL tornano all'utente.
- Il rimedio di NC-079 cambia la ritenuta: le 31 righe si rifanno.
