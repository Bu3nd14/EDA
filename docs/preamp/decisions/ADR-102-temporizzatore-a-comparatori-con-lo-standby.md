# ADR-102 — Il temporizzatore dell'alimentatore a comparatori, con lo standby: il micro e il firmware escono

Data: 2026-10-26 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Chiude NC-054** (maggiore, prima di G1): il confronto coi numeri chiesto da L52 (rilievi R3, R4
  dell'architetto) e la decisione dell'utente.
- **Supera ADR-048 al punto 6** (il temporizzatore ibrido col micro) e **ADR-049 ai punti 1–3 e 7**
  (l'ATtiny3216, il firmware in `firmware/preamp_timer/`, i pull-down «per il micro»: restano come
  pull-down del temporizzatore). Restano in vigore di ADR-049: Δ e Δ₂ in hardware (punto 4), Q505 che
  in standby toglie `VRELAY` alla scheda audio (punto 5).
- **Non cambia ADR-048 ai punti 1–5 e 7–8**: due trasformatori, `VRELAY` a 12 V su T2, l'interruttore
  frontale a bassa tensione e lo standby col posteriore che stacca tutto, il sorvegliante su `MUTE_G`,
  la ritenuta dopo un guasto con la rete presente. **PR-25 resta com'è.**
- **Scatta il «Da riaprire se» di ADR-073** («il firmware cambia in modo da non leggere più i rail»):
  la riserva del sorvegliante cieco diventa hardware, più veloce (sotto).
- **ADR-076**: la diagnosi del mute che non si inserisce era affidata al firmware in L58; L58 la fa
  in hardware o torna all'utente. Q505 resta, quindi il secondo «Da riaprire se» di ADR-076 non scatta.
- **ADR-078 punto 2** (lo standby letto dal firmware) e **ADR-091** (la partenza morbida dentro i 2 s
  del firmware): il timeout dei 2 s c'è anche nel temporizzatore nuovo (2,05 s sul banco).
- **NC-037** resta aperta, col criterio nuovo (sotto).

## Contesto

L54a (`data/2026-10-25/L54a/`, README; report `reports/2026-10-26-L54a-micro-standby.md`). ADR-048
aveva scelto il micro per il convertitore esponenziale delle fotoresistenze, tolto da ADR-062, e per i
«molti stati»; nessuno l'aveva riesaminato. Il banco dell'alimentatore di L45d2b3b1, provato sul suo
caso noto (deck uguale salvo i percorsi, uscite del firmware byte-identiche), ha corso le tre opzioni
di NC-054 coi casi di L41c, quelli della FMEA che contano sul firmware e il consumo, alle tre reti dove
la rete conta.

## Decisione

Parola dell'utente (2026-10-26), alla domanda coi numeri delle quattro opzioni: **«Comparatori, con lo
standby»**.

1. **Il micro U509 e il firmware escono.** Al loro posto, sui 5 V della logica e su `RLY_RET`, un
   temporizzatore di **dodici canali di comparatore** a uscita aperta (tre TLV1704), RC, diodi e una
   ritenuta a due transistor. Pilota quello che pilotava il micro: `MUTE_REQ`, `PERMIT_REQ`,
   `MAINS_REQ`, `VRELAY_EN`. Il sorvegliante su `MUTE_G`, Δ e Δ₂ (U508), i pull-down e i sink non si
   toccano.
2. **Le funzioni, una per una** (i valori del banco, `psu/genera_tb_psu.py`, `TIMER_AN`):
   - *alimentazione buona*: quattro canali nuovi con le soglie del sorvegliante (rail +, rail −,
     `VRELAY_REG`, rete) sugli stessi partitori; il rilascio dopo 0,57 s di alimentazione buona
     (820 kΩ · 1 µF), all'accensione e dopo un buco di rete;
   - *il tasto e il frontale*: un nodo filtrato (200 kΩ · 100 nF) che ogni ingresso cattivo svuota
     subito; `PERMIT_REQ` cade ~24 ms dopo `MUTE_REQ` (4,7 MΩ · 10 nF), come il firmware;
   - *K501*: cade ~84 ms dopo il permissivo allo spegnimento (1 MΩ · 100 nF, caricato dal frontale e
     da `VR_G`);
   - *la ritenuta*: una coppia BC847 / BC857 a tiristore sul nodo «acceso», che scatta con un rail o
     `VRELAY_REG` fuori soglia e la rete presente, se l'apparecchio è acceso da ≥ ~1,9 s con la rete
     presente (2,7 MΩ · 1 µF); tiene mute, `VRELAY` e K501 giù finché il frontale non si spegne. Lo
     stesso armamento fa il timeout dei 2 s all'accensione.
3. **Il sorgente** (`circuits/preamp/psu.py`), i disegni, il controllo dei relè (`--timer`), il calore
   e il consumo rifatti sul sorgente, e `firmware/preamp_timer/` tolto, in **L54b**. Le righe della
   FMEA delle parti nuove vanno in L58.

## Perché

Le cifre sono del banco di L54a, a 25 °C; «oggi» è il micro sullo stesso banco.

| | oggi (micro) | comparatori, con lo standby |
|---|---|---|
| Perdita di rete: jack / guadagno | 17,4 / 34,6 ms | 17,4 / 55,5 ms |
| Spegnimento dal frontale: jack / K501 | 31,3 / 131,5 ms | 10,3 / 123,1 ms |
| Guasto del rail − con la rete: jack / K501, poi | 15,6 / 115,5 ms | 15,6 / 129,1 ms, ritenuta fino al frontale |
| Sorvegliante del rail + cieco: mute dopo la soglia | 2,2 ms (L45c2, ADR-073) | < 0,5 ms |
| Corto davanti al regolatore +: R550 | 7,2 / 8,8 J | 7,7 / 9,3 J (rete 0 / +10 %) |
| Bobina di K501 in corto: R552 | 0,49 / 0,56 J | 0,47 / 0,54 J |
| Standby da T2, rete −10 / 0 / +10 % | ~76 / 85 / 95 mW | 117 / 130 / 145 mW |
| In musica, dai secondari a +10 % | 18,03 W | 18,00 W |
| Dal frontale alla musica | 0,74 s | 1,11 s |

- **PR-24 per costruzione**: non c'è firmware. Il controfattuale senza Δ (C528 e il ritardo di
  `PERMIT_REQ` a 10 pF) fallisce come deve: il guadagno si muove prima del jack.
- **PR-20, PR-23**: i jack si staccano negli stessi istanti e coi rail uguali; il rail resta in
  regolazione fino allo stacco in ogni caso, e il guadagno si muove dopo. Le cifre al jack del dossier
  (39,2 nV alla perdita di rete, §24) valgono quindi anche qui; L54b le rifà sul sorgente.
- **Dopo un buco di 20 ms** la musica torna 521 ms dopo la rete (la specifica: ≥ 500 ms).
- **Il calore**: in musica −25 mW (il micro attivo non c'è più); il telaio resta a **57,2 °C** contro
  60 °C nel caso peggiore.
- **Il prezzo**: circa 33 parti in più; lo standby +41 / 45 / 50 mW, soprattutto i pull-up delle uscite
  tenute basse; l'accensione 0,37 s più lenta.
- **Il firmware non c'è da scrivere, provare sul circuito e programmare**: `main_attiny.c` non esisteva,
  e nessun falso era mai stato fatto fallire sul circuito dopo L41b2 (dossier §27).

## Alternative scartate

- **Il micro, come oggi**: nessun cambio di circuito, standby più basso di ~45 mW, ma il firmware da
  scrivere e collaudare, e la riserva del sorvegliante cieco a 2,2 ms (un'eccezione accettata).
- **I comparatori senza standby** (interruttore di rete, niente K501): telaio 56,5 °C, standby zero, ma
  **senza K501 niente stacca un guasto**: col corto davanti al regolatore + R550 (2 W) resta a
  83–102 W senza fine, 44–54 J nel primo secondo; servirebbe un relè o un fusibile apposta. E cambia
  PR-25.
- **Senza standby e senza T2** (`VRELAY` da un raddrizzatore suo sui secondari di T1, serbatoio
  proprio): ~56,2 °C, ma lo stesso guasto senza fine e lo stesso cambio di PR-25.

## Da riaprire se

- Il consumo in standby col pezzo di T2 scelto supera 0,5 W alla presa: prima si tolgono i pull-up
  delle uscite tenute basse in standby (L54b), poi si torna all'utente.
- Le righe della FMEA delle parti nuove (L58) trovano un guasto singolo del temporizzatore che toglie
  il mute o la ritenuta e che il firmware avrebbe coperto.
- La diagnosi di L58 (ADR-076) non si può fare in hardware senza più parti di quante ne tolga il micro.
- Il prototipo mostra un'accensione o una ritenuta che scattano per i disturbi (dv/dt, rete sporca).
