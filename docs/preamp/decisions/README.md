# Decisioni di progetto (ADR)

**ADR** = *Architecture Decision Record*. Convenzione nata nel software
(Michael Nygard, 2011) per un problema che in elettronica è anche peggiore:
i valori dei componenti sembrano tutti arbitrari a chi non era presente
quando sono stati scelti, e vengono "corretti" da qualcuno che non sa
cosa stava tenendo insieme quel numero.

## Le regole

1. **Un file per decisione**, numerato progressivamente, datato.
2. **Non si riscrivono mai.** Se una decisione viene superata, si scrive
   una ADR nuova che dichiara di superare la precedente, e si aggiorna
   solo il campo `Stato:` di quella vecchia. Così non esistono due
   versioni della verità e la storia resta leggibile.
3. **Corte.** Una pagina scarsa. Le ADR lunghe non vengono scritte, ed è
   il modo principale in cui questa pratica fallisce.
4. **Il campo "Da riaprire se" non è opzionale.** È il motivo per cui
   questi documenti esistono.

## Il collegamento con il circuito

Ogni valore non ovvio in `circuits/preamp/*.py` porta un commento che
punta alla ADR che l'ha prodotto:

```python
# C_out: 4.7µ MKP - vedi ADR-007. Dimensionato per un finale futuro
# da 10kOhm (3.4 Hz), non per i 100kOhm del cj EV250.
```

Costa un commento. È il collegamento dall'artefatto al ragionamento, ed
è la cosa che di solito manca quando si torna su un progetto dopo mesi.

## Indice

| ADR | Titolo | Stato |
|---|---|---|
| [001](ADR-001-struttura-guadagno.md) | Guadagno unitario, non +16,5 dB | accettata |
| [002](ADR-002-attivo-non-passivo.md) | Preamplificatore attivo, non passivo puro | accettata |
| [003](ADR-003-classe-a-discreti.md) | Classe A pura a discreti, nessun operazionale | accettata — precisata da ADR-021 e ADR-022 |
| [004](ADR-004-rele-su-controreazione.md) | Guadagno commutabile via relè sulla controreazione | accettata |
| [005](ADR-005-appaiamento-rilassato.md) | Appaiamento JFET rilassato a "stessa gradazione" | accettata |
| [006](ADR-006-blocco-unico-riusato.md) | Un solo blocco discreto, usato due volte | accettata — precisata da ADR-023 |
| [007](ADR-007-condensatore-non-servo.md) | Condensatore d'uscita invece di servo di continua | accettata |
| [008](ADR-008-buffer-ingresso-unico.md) | Buffer d'ingresso unico con resistenze di isolamento | superata da ADR-023 |
| [009](ADR-009-niente-telecomando.md) | Niente telecomando: attenuatore a scatti, nessun MCU | accettata — clausola MCU superata da ADR-022 |
| [010](ADR-010-telaio-unico.md) | Telaio unico con alimentatore a bordo | accettata |
| [011](ADR-011-trim-per-ingresso.md) | Trim di livello per ingresso | accettata |
| [012](ADR-012-rele-di-mute.md) | Relè di mute su tutte le uscite | accettata — durata superata da ADR-021 |
| [013](ADR-013-jfet-ingresso-lsk489.md) | JFET d'ingresso: LSK489 | accettata |
| [014](ADR-014-cascode-ingresso.md) | Cascode sulla coppia d'ingresso | accettata |
| [015](ADR-015-rail-15v.md) | Rail a ±15 V, non ±18 V | accettata |
| [016](ADR-016-modello-vendor-e-ciclo-di-vita.md) | Nessun componente a fine vita, nessun dispositivo attivo senza modello vendor | accettata |
| [017](ADR-017-dispositivi-attivi-conformi-a-t7.md) | I dispositivi attivi che soddisfano T7 e T8: si cambia costruttore e package, non topologia | accettata |
| [018](ADR-018-specchio-ingresso-ls352.md) | Lo specchio d'ingresso è un LS352, degenerazione da 47 a 220 Ω | accettata |
| [019](ADR-019-margine-di-fase-trim-interbloccato-tre-guadagni.md) | Margine di fase minimo 60°, trim interbloccato col mute, tre livelli di guadagno | accettata — sonda precisata da ADR-024 |
| [020](ADR-020-quota-ripple-alimentazione.md) | Quota del ripple d'alimentazione nel budget di E5: 1 µV RMS | accettata |
| [021](ADR-021-mute-e-corto-sulle-uscite.md) | Mute tenibile a tempo indefinito, e ogni uscita regge un corto | accettata — precisata da ADR-023 |
| [022](ADR-022-integrati-fuori-dal-percorso-del-segnale.md) | Operazionali e microcontrollore fuori dal percorso del segnale | accettata |
| [023](ADR-023-classe-a-sui-percorsi-ascoltabili.md) | Classe A su ogni percorso ascoltabile, e un buffer per ogni uscita fissa | accettata |
| [024](ADR-024-sonda-capacitiva-cavo-al-jack.md) | La sonda capacitiva di V1 è il cavo: al jack, ogni cavo fino a 4,7 nF; il blocco A col suo cablaggio | accettata |
| [025](ADR-025-cf-330p-rimedio-margine-di-fase.md) | C_f da 22 a 330 pF: il rimedio del margine di fase, uguale in tutte le istanze | accettata |
| [026](ADR-026-terzo-livello-due-rami-in-parallelo.md) | Il terzo livello di guadagno: due rami di R_g in parallelo, 3,57 kΩ e 866 Ω, su due relè | accettata |
