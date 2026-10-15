# ADR-081 — Le Stax protette dal condensatore d'uscita da 1 µF; la garanzia sui guasti della scheda audio vale per la catena di oggi, e il rivelatore di continua cade

Data: 2026-10-15 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Supera ADR-069 nel criterio**: PR-30 e P10 non assumono più a valle un apparecchio qualunque,
  accoppiato in continua e senza protezione, ma la catena di oggi (il primo «Da riaprire se» di
  ADR-069: si conosce che cosa protegge ciascuna uscita).
- **Supera ADR-080**: il rivelatore differenziale non si costruisce.
- **Supera ADR-072 e ADR-079 nel rimedio della scelta 1** di `data/2026-10-14/L45d1/scelte_L45d2.pdf`
  (il blocco al rail): il rivelatore di continua sulle uscite esce dal progetto. **Le scelte 6, 8, 9
  e 10, che ADR-072 affidava allo stesso rivelatore, restano senza rimedio** finché il lotto
  successivo non le rimette davanti all'utente (vedi «Conseguenze»).
- **Supera ADR-007 su una sola uscita**: la fissa 2 (Stax) passa da 4,7 µF a 1 µF; la principale e
  la fissa 1 restano a 4,7 µF.

## Contesto

L61 (`reports/2026-10-15-L61-stax.md`), lotto piccolo chiesto dall'utente dopo L59: «il nodo sono le
STAX, non voglio romperle, pensiamo come proteggere le STAX e capiamo se é davvero necessario […] Se
non serve proteggerle il rilevatore cade, se troviamo una soluzione per una sola uscita magari
riduciamo complessitá».

Dai documenti in rete:
- **Stax SRM-T1**: accoppiata in continua (risposta dichiarata «DC–44 kHz», 60 dB di guadagno,
  50 kΩ d'ingresso, 300 V efficaci al massimo, polarizzazione 230 / 580 V). Nessuna protezione nota;
  di serie mancano le resistenze di sicurezza in uscita che i riparatori aggiungono. Un criterio di
  danno pubblicato per le elettrostatiche non si è trovato: i forum parlano di archi e di membrane
  danneggiate, senza misure.
- **Singxer SA-1**: i rivenditori dichiarano una protezione dalla continua e un ritardo
  all'accensione; un annuncio dice che l'ingresso è in alternata (un ponticello lo porta in continua).
  Nessuno schema lo conferma.
- **Il finale cj EV250**: il trasformatore d'uscita blocca la continua verso i diffusori (ADR-069).

## Decisione

1. **La fissa 2 (Stax) ha il condensatore d'uscita da 1 µF film**, al posto di 4,7 µF. Col carico
   della Stax (50 kΩ ∥ i due bleed da 470 k = 41,2 kΩ), a calcolo
   (`data/2026-10-15/L61/script/stax_e9.py`):

   | C (±5 %) | 20 Hz, catena intera | Sopra 0,87 V, blocco al rail (14,9 V) | A vuoto |
   |---|---|---|---|
   | 0,95 µF | 0,178 dB | 111 ms | 0,63 s |
   | 1,00 µF | 0,162 dB | 117 ms | 0,67 s |
   | 1,05 µF | 0,147 dB | 123 ms | 0,70 s |

   Il condensatore vede **ogni** continua che arriva da monte: il blocco A, il buffer F2, il filo di
   un rail. Non scatta sulla musica sotto la banda e la musica non lo maschera: i due difetti di L59
   (NC-064, NC-065) non lo riguardano.
2. **PR-30 riscritta** per la catena di oggi. Il testo firmato dall'utente il 2026-10-15
   («Firmo così»):

   > Un guasto della scheda audio non danneggia la catena di oggi. Un componente che si rompe mentre
   > si ascolta può dare un colpo, ma sull'uscita della Stax resta sopra il tetto di non-danno
   > (0,87 V) al più 125 ms, col suo carico. L'uscita principale conta sul trasformatore del finale a
   > valvole, la fissa 1 sulla protezione dichiarata del Singxer. Un apparecchio nuovo a valle fa
   > rivedere il preamp.

3. **P10** si misura sulla fissa 2 col carico della Stax (50 kΩ sul jack), non a vuoto: a vuoto non
   c'è niente da proteggere. Sulla principale e sulla fissa 1 P10 non ha più una soglia di durata.
4. **Il rivelatore di continua esce dal progetto** (`circuits/preamp/dc_detector.py`, la linea
   `DC_FLT` su J4 pin 4, D525–D527 sull'alimentatore, la lettura di PA1 nel firmware, spec 4.9). Lo
   si toglie nel lotto successivo, non qui: L61 non cambia il circuito.

## Perché

- **Le Stax vanno protette**: l'energizzatore è in continua con ×1000 di guadagno e nessuna
  protezione propria, e oggi un blocco al rail le tiene al massimo per ~0,56 s. Il danno non si sa
  escludere.
- **Il condensatore costa una parte che c'è già**, e non ha falsi scatti né mascheramenti. Il
  rivelatore differenziale di ADR-080 era ancora da provare, e lasciava il blocco A dopo una prova al
  gate.
- **Il limite di 100 ms non si raggiunge col solo condensatore dentro ±0,2 dB a 20 Hz**: E9 chiede
  τ ≥ 36,9 ms (C ≥ 895 nF sul carico della Stax), 100 ms chiedono τ ≤ 35,2 ms (C ≤ 854 nF). Con
  1 µF E9 resta dentro anche al −5 %, e la durata è ~117 ms: della stessa misura delle protezioni dei
  diffusori (ADR-069) e circa un quinto di oggi.
- **Le altre uscite hanno già una protezione a valle**: il trasformatore del cj; la protezione
  dichiarata del Singxer (non verificata su uno schema: un'ipotesi, scritta come tale).

## Alternative scartate

- **Il rivelatore differenziale su tutte le uscite (ADR-080, L60 com'era)**: garanzia generale, ma un
  circuito ancora da provare contro la musica e sotto la banda, per una catena che a valle ha già due
  protezioni su tre.
- **Le Stax non protette**: l'energizzatore è in continua e senza protezione; sconsigliata e non
  scelta.
- **0,82 µF**: ~96 ms, ma 0,237 dB a 20 Hz, fuori da E9.
- **Un rivelatore solo sulla fissa 2**: guardando il buffer F2 non vede un guasto del blocco A, che il
  buffer copia fedelmente; per vederlo serve la presa sul blocco A, cioè la parte più difficile di
  ADR-080.

## Conseguenze

- **NC-064 e NC-065** si chiudono togliendo il rivelatore, nel lotto successivo; **NC-066, NC-067,
  NC-068** con lui.
- **Le scelte 6, 8, 9 e 10 di ADR-072** tornano all'utente nel lotto successivo, coi numeri:
  - **6**, l'isolamento bobina-contatti di un relè che cede (12 V sul segnale);
  - **8**, il filo del rail positivo aperto fra le schede (13,3 V al jack, L45c1). Sulla Stax lo
    ferma il condensatore; sulla principale e sulla fissa 1 conta sulla protezione a valle;
  - **9**, il condensatore d'uscita in corto;
  - **10**, il calore da solo, coperto dal rivelatore che spegneva i rail. NC-066 dice anche «coperto
    dal sorvegliante a 106 ms»: da verificare.
- **Da rifare sulla fissa 2 con 1 µF**: E9 col banco, P10 col carico della Stax, V2 (il mute e i suoi
  colpi: la geometria di ADR-044 è stata misurata con 4,7 µF), l'inserimento a caldo, il commento di
  ADR-007 nel sorgente.
- **La nota di memoria «catena a valle generica»** non vale più per i guasti della scheda audio.

## Da riaprire se

- Cambia un apparecchio a valle: un finale nuovo (soprattutto accoppiato in continua e senza
  protezione), un energizzatore nuovo, o la fissa 1 collegata a un altro apparecchio.
- Lo schema o l'apertura del Singxer SA-1 mostra che la protezione dalla continua non c'è.
- Si trova un criterio di danno pubblicato per le elettrostatiche più severo di ~120 ms al massimo.
