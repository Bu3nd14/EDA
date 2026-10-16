# ADR-085 — Il relè di mute della Stax (K3) è un TE Axicom IM06TS, a isolamento supplementare fra bobina e contatti

Data: 2026-10-15 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Supera ADR-084 punto 2** nella parola «rinforzato»: K3 ha isolamento **supplementare** dichiarato
  dal costruttore, e ADR-085 lo conta come «non cede», cioè il cedimento bobina-contatti di K3 non è
  un guasto singolo credibile ed esce da P10. Il resto di ADR-084 resta: il condensatore da 1 µF
  della fissa 2 prima di K3, nella geometria iii di ADR-044; K2 e K4 G6K.
- **Applica il «Da riaprire se» di ADR-044** sul relè che cambia: capacità del contatto aperto e
  tempo di trasferimento confrontati sotto, e V2 rimisurato sulla fissa 2 in L60c2.
- Chiude la **scelta 6 su K3** (ADR-082, ADR-072) col relè nel sorgente.

## Contesto

ADR-084 voleva K3 «con isolamento rinforzato fra bobina e contatti», così che il cedimento
dell'isolamento non lasciasse più 12 V di `VRELAY` per sempre sulla Stax. In L60c2, cercando la
parte, i relè di segnale a due deviatori (TE Axicom IM e P2, Panasonic TX) dichiarano al più un
isolamento **supplementare**, o nessuna categoria (il TX: solo 2000 V di rigidità). Il rinforzato si
trova sui relè di potenza (Finder 40.52, Schrack RT2, Omron G2RL-2), con bobine da 3–4 volte la
corrente del G6K, più grandi, a fori passanti e con una capacità del contatto aperto da verificare.

## Decisione

Le parole dell'utente (2026-10-15), alle due domande poste per nome:
1. sull'isolamento: **«Accetta il supplementare»**;
2. sul relè, con i numeri sotto: **«TE Axicom IM06TS (Recommended)»**.

**K3 è un TE Axicom IM06TS** (IM a due deviatori, bobina 12 V da 140 mW non bistabile, montaggio
superficiale a J), `Relay:IM06` con l'impronta `Relay_SMD:Relay_DPDT_AXICOM_IMSeries_JLeg`. Il suo
isolamento supplementare fra bobina e contatti conta come «non cede»: la riga del cedimento di K3
esce da P10.

## Perché

Dal datasheet, `vendor/relays/te/IM/ENG_DS_108-98001_K.pdf` (TE 108-98001 Rev. K, provenienza nella
cartella):

| | G6K-2F-Y (K2, K4) | IM06TS (K3) | Il confronto (ADR-044) |
|---|---|---|---|
| Isolamento bobina-contatti | base, 1500 V efficaci | **supplementare** IEC/EN 60950 (p. 3); 1800 V efficaci per un minuto, 2500 V impulsivi (p. 22) | — |
| Contatto aperto | 0,1 pF (0,075–0,080 dalla curva) | **al più 1 pF** (p. 23); ~0,2 pF dall'isolamento di −37 dB a 100 MHz | limite ~2,4 pF |
| Intervento / rilascio massimi | 3 ms | 3 ms senza diodo (p. 23; la bobina si scarica su uno zener da 24 V, `psu.py`) | ≤ 3 ms in V2 |
| Trasferimento | 1 ms (ipotesi di ADR-044) | non pubblicato; rimbalzo alla chiusura 1 / 5 ms | 1 ms tenuto |
| Contatti | dorati, biforcati | palladio-rutenio dorati, biforcati, < 50 mΩ, minimo 100 µV | — |
| Bobina a 12 V | 9,1 mA | **11,7 mA** (1029 Ω) | +2,6 mA su `VRELAY`, il caso peggiore da ~88 a ~88,5 mA |
| Piedinatura | 1/8 bobina, COM 3/6, NC 2/7, NO 4/5 | **la stessa**, ma bobina **polarizzata**: + sul pin 1 (p. 5) | asserita dal 2e |

- **Il supplementare regge il caso.** Il guasto è un cedimento fra la bobina a 12 V e un contatto che
  porta il segnale, non un isolamento verso la rete. Il supplementare è dichiarato per 300 V efficaci
  di lavoro e 250 V di rete (p. 3), più di venti volte la tensione che deve tenere qui. Il rinforzato
  costava un relè di potenza, a fori passanti, con 3–4 volte la corrente di bobina e un contatto
  aperto di capacità non dichiarata contro il limite di 2,4 pF di ADR-044.
- **L'IM06TS sta nei numeri di ADR-044**: contatto aperto al più 1 pF contro ~2,4 pF, tempi uguali al
  G6K, stessa piedinatura e stesso montaggio superficiale. Simbolo e impronta sono nella libreria
  KiCad. La bobina polarizzata è asserita da `check_relay_safe_state.py`, perché al contrario il relè
  non interviene.
- **La bobina interviene anche calda**: tensione di intervento sicuro ~75 % del nominale a 23 °C,
  ~84 % a 60 °C, ~92 % a 85 °C (p. 24, letta sulla curva), contro il 95 % di `VRELAY` a −5 %.

Le prove sul circuito sono in `reports/2026-10-15-L60c2-stax-condensatore-e-rele.md`.

## Alternative scartate

- **Un relè di potenza a isolamento rinforzato** (Finder 40.52, Schrack RT2, Omron G2RL-2): bobina da
  3–4 volte la corrente, a fori passanti, capacità del contatto aperto non dichiarata. L'utente non
  l'ha voluto («Accetta il supplementare»).
- **Il TE Axicom P2 (V23079)**: anch'esso supplementare, ma senza simbolo e impronta nella libreria
  KiCad, da disegnare a mano.
- **Il Panasonic TX2**: nessuna categoria d'isolamento dichiarata, solo 2000 V di rigidità.
- **Tornare ai due condensatori** (10 + 1 µF, ADR-084 «Da riaprire se»): il relè che cede con 1 kΩ dava
  131–138 ms, fuori da P10; non serve più.

## Da riaprire se

- **La revisione corrente del datasheet TE** (in L60c2 il sito di TE rifiuta lo scaricamento: si è
  letta la Rev. K del 2009, da Farnell) cambia la categoria d'isolamento, la piedinatura o la
  capacità del contatto aperto. Va riletta prima dell'ordine.
- La catena a valle della Stax cambia, o il progetto porta sulla fissa 2 una tensione di lavoro
  vicina ai 300 V efficaci per cui il supplementare è dichiarato.
- V2 sulla fissa 2 col contatto dell'IM06TS supera la soglia (il «Da riaprire se» di ADR-044).
- Un revisore o una norma applicabile al prodotto chiede il rinforzato per questo guasto: allora si
  torna ai relè di potenza, o ai due condensatori.
