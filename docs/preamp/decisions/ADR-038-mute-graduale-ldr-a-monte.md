# ADR-038 — Il mute graduale si fa a monte, con fotoresistenze in serie e verso massa all'ingresso del blocco A; il relè al jack resta, e guadagno e trim si cambiano solo col jack a massa

Data: 2026-09-16 · Stato: accettata

## Contesto

ADR-037 aveva scelto, per il mute graduale, due MOSFET contrapposti con driver
fotovoltaico (VOM1271 + DMN6040SVT), in serie e verso massa **al jack**. Nella
stessa sessione il lavoro l'ha messa in difficoltà su quattro punti:

1. **La dissolvenza avviene sotto soglia, e lì nessuno la descrive.** Il modello
   del costruttore è un LEVEL 3 senza `NFS`: a Vds = 10 mV la conduttanza salta
   da ~45 nS a 0,70 S fra 2,45 e 2,50 V di gate. Il datasheet non pubblica la
   regione (`data/2026-09-16/L29b/driver_e_mosfet/`). Serve un'ipotesi dichiarata
   (`models/mosfet_n/dmn6040svt_sottosoglia.lib`).
2. **Le rampe diventano lunghe, per calcolo.**
   - La soglia va da 1 a 3 V.
   - La corrente del fotovoltaico va da 6,0 µA minimi a 15 µA tipici, a 10 mA.
   - Per attraversare lentamente tutta la dispersione servono **circa 7–10 s per
     verso**, calcolati.
3. **Il banco con le coppie reali non converge alle tolleranze di V2.**
   - Il nodo dei source della derivazione si pompa a −11,9 V.
   - Le sole varianti che corrono (`reltol=1e-4`, oppure `abstol=1e-9`) sono più
     larghe delle grandezze da misurare
     (`data/2026-09-16/L29b/coppie_reali_convergenza/`).
4. **Una ricerca in rete, chiesta dall'utente**, ha trovato che nessuno fa quello
   che il progetto chiede. Fonti verificate in L29b:
   - **ESP, «Muting Circuits»** (sound-au.com/articles/muting.html):
     - i MOSFET con alimentazione flottante: «the complexity of the complete
       system is such that it can't be recommended»;
     - le LDR: «very low distortion during the transition», «at least 100dB»;
     - «there must be no DC along with the signal that's being muted».
   - **Pass Labs, Benchmark, Accuphase.** Il relè d'uscita serve all'accensione e
     alla protezione; il mute dell'utente passa dal volume, a monte.
   - **TI SLEA044**, sez. 3. Gradino accettabile ai morsetti del diffusore
     **10,7–21,4 mV**, con un diffusore da 96 dB a 1 m. Diviso per il ×21,1 del
     finale (NC-028) fa **0,5–1,0 mV al jack**: un **calcolo** di L29b.
   - **Sul taglio della musica (C) nessuna fonte pubblica una cifra.**

Portato all'utente con tre strade: LDR a monte, C allentata, MOSFET al jack. Poi
la domanda dell'utente: il cambio di guadagno come si risolve?

## Decisione

Parole dell'utente: «mi piace 1, ma non risolve il cambio di guadagno, vero?»,
poi «Concordo, Opzione 1 piú ipotesis 1, e credo che avessimo giá definito che
sia trim che cambio guadagno funzionano solo a mute inserito (da lí la necessitá
dei LED)».

**1. Il mute graduale sta a monte.**
- Una fotoresistenza optoaccoppiata **in serie** fra il connettore d'ingresso
  selezionato e l'ingresso del blocco A, e una **verso massa** sull'ingresso del
  blocco A.
- Il blocco A alimenta tutte e tre le uscite, quindi un solo punto per canale le
  silenzia tutte.
- Lì non c'è continua: l'ingresso è riferito a massa da R_IN = 1 MΩ
  (`gain_block.py`).
- **Parte di partenza: VTL5C4.** È l'unica dei candidati con la curva
  resistenza–corrente pubblicata (0,1–40 mA, 10 kΩ → 75 Ω), i tempi, 5 pF di
  capacità della cella e 400 MΩ minimi al buio. Due aperti:
  - **la disponibilità non è confermata** presso un distributore;
  - l'NSL-32SR3, a stock, pubblica solo due punti.

  La parte si conferma prima di G2.

**2. Il relè NC al jack resta**, dove è oggi, a valle del condensatore.
- È lo **stato sicuro** di ADR-012, a macchina spenta e a bobina diseccitata.
- **Non si chiude mai con la musica presente**: si chiude solo a mute graduale
  completo, e si apre prima che la musica rientri.

**3. Un'unica variabile di profondità** comanda LDR e relè, così un'inversione a
metà ripercorre la stessa strada (L29b):
- la serie si apre;
- poi la derivazione si chiude, e la serie resta alta prima che la derivazione
  scenda, perché la sorgente non veda mai un carico basso;
- a profondità completa, con isteresi, il relè al jack va a massa.

Al rilascio, l'inverso.

**4. Guadagno e trim si cambiano solo col jack a massa**, a musica già spenta:
dissolvenza, relè al jack, commutazione, attesa, apertura del relè, rientro.
- **Il trim** lo faceva già (F8, ADR-019, ADR-027), coi LED dello stato vero (F9).
- **Il guadagno.** ADR-030 lo subordinava a una misura: «solo se L29 lo
  giustifica». L'utente lo considera già deciso. La ragione per cui ora regge è
  l'ipotesi 1 qui sotto.
- **Come si impone, e i LED del guadagno**, restano di **L36**: interblocco da
  premere (ADR-030, strada B) oppure mute automatico al cambio.

## Perché

**L'ipotesi 1: il cambio di guadagno sotto un jack a massa, a musica spenta.
Ragionamento, non simulato.**
- Il gradino del cambio di guadagno è l'offset del blocco B che cambia col
  guadagno: 6–114 mV calcolati (ADR-030). Un mute a monte non lo tocca.
- Col relè al jack chiuso, il 4,7 µF si ricarica al nuovo offset attraverso i
  47 Ω in **τ ≈ 0,22 ms** (47 Ω × 4,7 µF). Dopo qualche decina di ms i due lati
  sono coerenti, e il rilascio non porta salto.
- **È già stato osservato.** In L11 (scratch, tabella di NC-028), col contatto
  dopo il condensatore, il cambio 0 → +10 dB «sotto mute, senza segnale» dava
  **pV** al rilascio. Il difetto di quel mute era la musica che caricava il
  condensatore, e ora la musica è spenta prima.
- **Stima calcolata di C alla chiusura del relè**, con la serie al buio e la
  derivazione accesa:
  - 5 pF della cella in serie a 20 kHz valgono ≈ 1,6 MΩ, contro 75 Ω verso massa:
    ≈ 4,7e-5;
  - al tono di prova (3,818 V di picco × 3,15) sono **≈ 0,57 mV al jack
    principale a 20 kHz**, prima del filtro; a 1 kHz, 20 volte meno.
  - Il relè li taglia di colpo, sotto 1 mV **ma vicino a 20 kHz**. È da misurare.

**Perché a monte è più semplice che al jack:**
- **E4 non c'entra più.** L'impedenza d'uscita la fanno blocco B e buffer, a
  valle. È il vincolo che aveva escluso le LDR al jack.
- **La non linearità della LDR in serie pesa poco.** Alimenta 1 MΩ, quindi ai
  suoi capi cade quasi niente: con 75 Ω, circa 75 ppm del segnale. È un calcolo,
  e la distortion va misurata.
- **Niente continua**, niente nodo flottante pompato, niente driver isolato: il
  LED si comanda da massa.
- **La curva della parte è in buona parte pubblicata.** Il modello si appoggia a
  dati, più un'estrapolazione dichiarata sopra i ~10 kΩ.
- **Lo spegnimento della LDR è lento per natura**: fino a 1,5 s per arrivare a
  100 kΩ. È una dissolvenza che non si deve costruire.

**Rumore, calcolato.** 75 Ω in serie danno ≈ 1,1 nV/√Hz. All'uscita principale
(× 3,15, 20 kHz) sono ≈ 0,49 µV, in quadratura coi 4,92 µV peggiori di L16:
≈ 4,94 µV, contro 9,90 µV (E5). Da misurare, insieme alla capacità
d'accoppiamento LED–cella (0,5 pF) che porta il rumore del comando del LED
sull'ingresso.

## Cosa precisa, e cosa si deve ancora verificare

- **Supera ADR-037.**
- **Precisa ADR-036:**
  - la posizione del graduale passa da «in serie al jack» a «a monte»;
  - la rampa da 3 s va riletta sui tempi della parte;
  - le attese uditive sulla dissolvenza restano valide nella sostanza.
- **Precisa ADR-012:** il relè resta, ma non taglia mai la musica.
- **Precisa ADR-021 e P7:** il mute come è cablato al jack non cambia. A mute
  inserito gli stadi d'uscita **non hanno segnale**, una condizione meno severa di
  quella con cui P7 è stato misurato conforme in L17. **Ipotesi da confermare in
  L29b**: P7 resta conforme senza una misura nuova.
- **Precisa ADR-030:** l'interblocco del guadagno non è più «solo se», e L36 ne
  decide la forma.
- **Precisa ADR-022:** il comando dei LED sta fuori dal percorso del segnale;
  vale §2 per l'accoppiamento LED–cella.
- **Da misurare, col metodo di V2** (L29b, e il caso peggiore in L29c):
  - C della dissolvenza a 20 Hz, 1 kHz e 20 kHz sulle tre uscite, col pavimento
    accanto;
  - C e A alla chiusura e all'apertura del relè;
  - B;
  - il cambio di guadagno e di trim nella sequenza;
  - l'inversione a metà;
  - accensione e spegnimento;
  - E3, E5 e la distorsione della serie;
  - il carico minimo che la sorgente vede durante la dissolvenza.
- **Le incognite dichiarate:**
  - la regione ad alta resistenza della LDR, non pubblicata;
  - la sua dispersione fra pezzi, la memoria della luce e la temperatura (a
    60 °C restano 15 °C di margine sui 75 °C della parte);
  - la disponibilità della VTL5C4.

## Alternative scartate

- **I MOSFET contrapposti al jack (ADR-037):**
  - la regione di lavoro non è modellata né pubblicata;
  - rampe calcolate da 7–10 s per verso;
  - un banco che non converge alle tolleranze di V2;
  - «can't be recommended» (ESP).
- **Allentare C e accettare il taglio netto, come l'industria:** l'utente ha
  scelto di tenere la soglia.
- **Le LDR al jack:** E4 sforata per calcolo (ADR-037).
- **Il guadagno in continua sempre unitario**, con condensatori nei rami R_g:
  - R_g3 ∥ R_g10 = 697 Ω, quindi circa 110 µF per un taglio sotto 2 Hz;
  - elettrolitici nella controreazione, contro lo spirito di ADR-007;
  - V1 ed E5 da rifare;
  - e non tocca il salto di livello della musica.
- **Abbassare l'offset** fino a rendere innocuo il cambio a caldo: servirebbe un
  offset d'ingresso sotto circa 0,05 mV, impossibile senza servo (T2).

## Da riaprire se

- La misura di C della dissolvenza con la LDR è molto peggiore dell'elemento
  ideale di ADR-036.
- La chiusura del relè a 20 kHz supera 1 mV di C.
- E3 o E5 escono dai limiti per la LDR in serie, o per il rumore del comando.
- La VTL5C4 non si trova, e nessuna parte con curva pubblicata la sostituisce.
- Il prototipo contraddice il cambio di guadagno sotto jack a massa (pV in L11).
