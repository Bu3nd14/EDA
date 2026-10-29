# ADR-107 — I test point delle due schede

Data: 2026-10-29 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- Fa la prima metà di **L58** (richiesta dell'utente dopo L45d1, 2026-10-14: «test point per diagnosi»).
  L'autodiagnosi resta a L58b.
- Non tocca nessun valore: i test point non entrano nei deck SPICE (`spice_export` non li registra).

## Contesto

Per la diagnosi al banco e la riparazione servono punti di misura sui rail, su `VRELAY` dai due lati del
cablaggio, su V5, sulle uscite del temporizzatore (`MUTE_G`, `PERMIT_G`, `PERMIT_T`), sui comandi dei
relè e sull'uscita di ogni blocco, ciascuno con il suo riferimento accanto.

## Decisione

1. **Il pezzo**: il simbolo KiCad `Connector:TestPoint` con l'impronta
   `TestPoint:TestPoint_Keystone_5000-5004_Miniature` (anello Keystone a foro: rosso 5000 sul segnale,
   nero 5001 sul riferimento). Non `Conn_01x01`: `check_relay_safe_state.py` legge il piedino 1 di un
   `Connector_Generic` come un jack. Il valore è `TP_<rete>`, mai un valore di cablaggio (POWER, RLY_RET,
   MUTE_TIMER: `check_psu_harness.py` trova i cablaggi per valore).
2. **Scheda audio** (`preamp_audio.py`, `TP()`): TP1 VPLUS, TP2 VMINUS, TP3 GND (accanto a J1);
   TP4 VRELAY, TP5 RLY_RET (accanto a J1 / J2); TP6 MUTE_CMD, TP7 PERMIT_CMD, TP8 MUTE_SW, TP9 RLY_RET
   (accanto a J4). Per ogni blocco l'uscita e la massa: TP101 / TP102 (AL), TP201 / TP202 (BL), TP301 /
   TP302 (AR), TP401 / TP402 (BR), TP501 / TP502 (F1L), TP601 / TP602 (F2L), TP701 / TP702 (F1R),
   TP801 / TP802 (F2R).
3. **Alimentatore** (`psu.py`, `testpoint()`): TP501 VPLUS, TP502 VMINUS, TP503 GND, TP504 VRELAY
   (dopo Q505, il lato del cablaggio), TP505 VRELAY_REG (prima di Q505), TP506 RLY_RET; TP507 V5,
   TP508 MUTE_G, TP509 PERMIT_G, TP510 PERMIT_T, TP511 RLY_RET; TP512 MUTE_CMD, TP513 PERMIT_CMD,
   TP514 MAINS_G, TP515 MAINS_COIL, TP516 VR_G, TP517 RLY_RET. Niente sul lato di rete.
4. **Il vincolo per G2**: ogni test point di segnale sta accanto al suo riferimento — i rail a GND, la
   logica, `VRELAY` e i comandi dei relè a RLY_RET (la logica torna lì, non a GND: NT501), l'uscita di un
   blocco alla massa dello stesso blocco. Le coppie sono quelle dei punti 2 e 3.

## Perché

Un anello a foro regge il puntale a uncino e il colore dice il riferimento; il simbolo TestPoint non
inganna i controlli che leggono i connettori. Leggere `VRELAY` e i rail dai due lati del cablaggio
separa un guasto del cavo da uno della scheda.

## Alternative scartate

- Piazzole SMD (`TestPoint_Pad`): non reggono un puntale a uncino durante una misura lunga.
- `Conn_01x01` su pin header: letto come jack da `check_relay_safe_state.py`.

## Da riaprire se

- Il layout di G2 non trova spazio per un riferimento accanto al suo segnale.
- L'autodiagnosi di L58b chiede altri punti.
