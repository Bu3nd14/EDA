# ADR-012 — Relè di mute su tutte le uscite

Data: 2026-09-08 · Stato: accettata — la durata «per qualche secondo» è superata da ADR-021 (mute tenibile a tempo indefinito)

## Contesto

Due transitori distinti producono un botto in uscita:

1. **All'accensione**, ogni condensatore di accoppiamento (ADR-007) si
   carica attraverso il proprio carico.
2. **Alla commutazione del guadagno** (ADR-004): senza servo di continua
   l'offset residuo salta da ×1 a ×3,16, e il condensatore trasmette il
   gradino.

## Decisione

Un **relè di mute che copre tutte e tre le uscite**, attivo per qualche
secondo all'accensione e durante la commutazione del guadagno.

## Perché

- La ragione decisiva è il **ramo cuffie**, non quello principale: il
  transitorio d'accensione finisce direttamente **nelle orecchie**, non
  in un altoparlante a due metri. Con delle elettrostatiche in testa è
  una ragione sufficiente da sola.
- Sul ramo principale, le Klipsch Heresy a 96 dB/1W/1m rendono qualunque
  botto sgradevole.
- Costa poco ed è una funzione standard.

Nota: il gradino da commutazione del guadagno riguarda **solo** l'uscita
principale, perché il +10 dB sta lì. Le uscite fisse restano a guadagno
unitario sempre. Ma il mute le copre comunque per il transitorio
d'accensione.

Il comando del guadagno si userà una volta ogni cambio di catena, non
ogni sera: il mute su quella transizione è comodità, non necessità
quotidiana.

## Alternative scartate

- **Mute solo sull'uscita principale**: lascerebbe scoperto proprio il
  ramo che ne ha più bisogno.
- **Nessun mute, ritardo di accensione dell'alimentazione**: non risolve
  il gradino della commutazione di guadagno.

## Da riaprire se

Si adotta un servo di continua (ADR-007 riaperta), che eliminerebbe il
gradino da commutazione ma non il transitorio d'accensione.
