# L60a — Le scelte che il rivelatore copriva (2026-10-15)

Prima parte di **L60** («il rivelatore esce e la Stax ha il suo condensatore»). All'inizio della
sessione l'utente ha diviso il lotto: «Tre parti».
- **L60a**: le scelte con l'utente e la decisione;
- **L60b**: togliere il rivelatore;
- **L60c**: il condensatore della Stax e le sue prove.

**Il risultato.** Le quattro scelte che ADR-072 affidava al rivelatore (6, 8, 9 e 10 di
`data/2026-10-14/L45d1/scelte_L45d2.pdf`) hanno di nuovo un rimedio, deciso dall'utente sui numeri
del banco senza rivelatore. La decisione è **ADR-082**. Il circuito non cambia in L60a.

## 1. Il banco

`data/2026-10-15/L60a/` (README): il canale di L45a e i guasti dei controlli di L45b, importati,
con **1 µF sulla fissa 2** e **i carichi montati** (P10 sulla Stax col suo carico, ADR-081 punto 3).
Nessun rivelatore, rail ideali. 30 corse.

**Il controllo prima dei numeri nuovi.** Quattro corse riproducono numeri noti:
- R126 in corto in F2 a vuoto con 4,7 µF: 44,2 ms, come L45d2b1;
- F2 al rail con 4,7 µF sulla Stax: 552 ms, contro ~0,56 s di L61;
- K3 sul jack a vuoto: 12 V fino alla fine, come L45b;
- F2 al rail con 1 µF: 117,5 ms, contro i 117 ms a calcolo di ADR-081.

## 2. Che cosa dice il banco

| Scelta | Sulla Stax, col condensatore da 1 µF | Perché |
|---|---|---|
| **6**, bobina-contatti del relè di mute della Stax (K3) | **12 V per sempre** (11,7 V con 1 kΩ) | K3 sta **dopo** il condensatore |
| 6, lo stesso sul selettore (K13) | 116 ms (95 ms con 1 kΩ) | passa dal blocco e dal condensatore |
| 6, lo stesso sul trim (K7) | 70 ms | idem |
| **8**, il filo del rail + aperto | **388–421 ms**, picco 1,3 V | il rail scende piano, la deriva passa il condensatore |
| 8, il filo del rail − aperto | 3,7 mV | — |
| **9**, il condensatore della Stax in corto | 6,3 mV; con un guasto del blocco dopo **14–15 V per sempre** | guasto latente |
| **10**, R126 in corto | 37–38 ms | dentro; ma Q127 a ~231 °C |

Sulla principale e sulla fissa 1 i relè K4 e K2 che cedono lasciano 12 V per sempre, e il filo del
rail + ~0,95 s e ~0,42 s: contano sulla protezione a valle (PR-30, ADR-081).

**Il calore della scelta 10.** R126 è l'emettitore del carico del VAS. In corto, in ogni posizione,
Q127 (il transistor del moltiplicatore di Vbe, MMBT5551 in SOT-23) dissipa 0,49 W: ~231 °C con
417 °C/W. L'uscita torna a −0,22 V, la corrente dei rail ~0,32 A. Due cose che il prompt chiedeva di
verificare:
- **il rivelatore non lo copriva**: in L45d2b1 (`banco/guasti.csv`) R126 in corto non lo faceva
  scattare in A, F1, F2 e B (solo nel B a +10 dB, per il colpo);
- **il «106 ms» di NC-066 è un altro guasto**: C145 in corto, il rail che cede, il sorvegliante che
  stacca il toroidale (`data/2026-10-14/L45d2b1/psu_riv.csv`). Con R126 in corto i rail non cedono.

Togliere il rivelatore non cambia quindi niente per la scelta 10.

## 3. Le domande e le risposte

Poste per nome, coi numeri qui sopra; le risposte dell'utente:

| Scelta | Risposta |
|---|---|
| 6, il relè di mute della Stax | «Condensatore dopo il relè e solo se non passano le misure nella terza parte allora Relè a isolamento rinforzato» |
| 8, il filo del rail | «Due pin per il rail (Recommended)» |
| 9, il condensatore in corto | «Accettarlo, è doppio (Recommended)» |
| 10, il calore | «Package grande (Recommended)» |

## 4. La decisione: ADR-082

1. **La Stax: il condensatore da 1 µF fra K3 e il jack.** I contatti di K3 restano tutti a monte,
   e una bobina che cede dà un colpo di ~108 ms a calcolo invece di 12 V per sempre. La geometria
   del mute su quell'uscita si riprogetta e si misura in **L60c**; se non regge, **K3 a isolamento
   rinforzato** e il condensatore resta dov'è (il G6K ha isolamento base, 1500 V).
2. **Due pin e due fili per ciascun rail** fra le schede, in **L60b**.
3. **Il condensatore in corto: guasto doppio, accettato.** PR-30 parla di un componente.
4. **Q127 in SOT-223 (DZT5551)**, stesso die e modello: ~88 °C (~121 °C con 60 °C d'aria, dentro
   P7), in **L60b**. L'accoppiamento termico col finale in rame resta possibile: la linguetta è il
   collettore, non il rail.

## 5. Le non conformità

Nessuna aperta o chiusa. **NC-042** avanza: le quattro scelte hanno un rimedio deciso. **NC-066**:
una nota sul «106 ms», che è il caso C145 e non la scelta 10; la voce si chiude in L60b col
rivelatore, come deciso da ADR-081.

## 6. Il piano che segue

- **L60b — il rivelatore esce**: `dc_detector.py`, la linea su J4 pin 4, D525–D527 e R549, PA1 e la
  spec 4.9, i test, i controlli della suite e i disegni (la mappa è in `NEXT-SESSION.md`); più i due
  pin per rail su J1 e Q127 in SOT-223; NC-064…068 chiuse togliendolo.
- **L60c — la Stax**: il condensatore da 1 µF dopo K3; E9, P10 col carico della Stax (il blocco al
  rail, i guasti di L45a, K3 che cede, un pin di un rail aperto), V2, l'inserimento a caldo; NC-042
  aggiornata.

La suite non è toccata da L60a.
