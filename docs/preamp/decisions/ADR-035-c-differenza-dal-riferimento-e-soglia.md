# ADR-035 — C si misura per differenza dalla corsa di riferimento, e ha una soglia propria di 1 mV

Data: 2026-09-16 · Stato: accettata — come verdetto del taglio superata da ADR-040 (salto di livello ≤ 20 dB in 100 ms); C2 resta come diagnostica

## Contesto

ADR-032 ha dato a V2 una soglia (100 µV di picco in banda, al jack) e un metodo,
e ha lasciato scritto nel proprio «Da riaprire se»:

> **L29 trova che nessuna variante di mute rispetta A, B e C insieme**: la
> scelta torna all'utente, con i numeri.

L29a ha costruito lo strumento del metodo (`scripts/v2_metodo.py`) e i deck
versionati, e **prima di misurare le varianti** ha trovato che il metodo, preso
alla lettera, non separa i casi che L29 incontra. Le cifre, tutte verificate sui
dati di `data/2026-09-15/L29a/`:

1. **C sottrae solo la fondamentale**, quindi la distorsione di regime del
   circuito resta per sempre nel residuo. Su una corsa **mai in mute**, cioè
   senza alcun evento da misurare, la seconda armonica al jack principale vale
   **887 µV** — nove volte la soglia (`esplorazione/armt_main.txt`). Il
   pavimento completo di C vale **1,23 mV** sulla principale e **188 µV** sulle
   fisse a 1 kHz, **21,9 mV** a 20 kHz, **167 µV** a 20 Hz
   (`esplorazione/pav4_out.csv`). Anche a 0 dB vale 184 µV.
   **Non è un difetto dei modelli segnaposto**: qualsiasi stadio a discreti in
   classe A a 12 V di picco ha una h2 ben sopra lo 0,0008 % che servirebbe.
   Perciò **nessun circuito reale può passare C a 100 µV.**
2. **Il resto del pavimento è numerico e non scende.** Tolte h2..h20, restano
   390 µV sulla principale e 124 µV sulle fisse: rapporto 3,15, cioè esattamente
   il rapporto di guadagno. Due spiegazioni sono state **falsificate**: il
   ricampionamento dello strumento sbaglia 4,4 µV a 12 V e 1 kHz con passi da
   10 µs (autotest T7, 280 volte sotto), e la precisione di scrittura darebbe fra
   le uscite un rapporto di 10, non di 3,15. Un `reltol` diecimila volte più
   stretto muove il residuo solo da 112 a 87 µV RMS e il suo spettro non ha
   righe (la più alta è 2,6 µV, `esplorazione/spettro_main_r7.txt`). Un tono puro
   in un circuito deterministico può produrre **solo** armoniche, quindi il resto
   è numerico per necessità — ma **non è attribuito**, e nessuna manopola del
   solutore provata lo abbassa in modo utile.
3. **Nessuna dissolvenza di durata pratica passa C**: il residuo del fit scende
   solo come 1/T, e a 1 kHz una rampa lineare da 10 s lascia ancora 1,5 mV
   (`strumento/caratterizza_C_960.txt`). Non dipende dalla parità della
   finestra: 960 e 961 campioni danno le stesse cifre.

Le tre cose sono state portate all'utente il 2026-09-16 coi numeri, come il
mandato di L29 chiede («se il metodo non separa i casi che L29 incontra, lo si
dice all'utente, non lo si aggiusta in silenzio»). Questa ADR registra le sue
risposte.

## Decisione

1. **C si misura per differenza dalla corsa di riferimento**, non col solo fit
   della fondamentale. La grandezza è

   ```
   C2(t) = [v_jack,evento(t) − tono_fit,evento(t)] − [v_jack,rif(t) − tono_fit,rif(t)]
   ```

   cioè la **differenza dei residui del fit** fra la corsa con l'evento e la
   corsa di riferimento, sulla stessa griglia uniforme a 96 kHz, filtrata dopo.
   Il riferimento è quello di A: tiene dall'inizio lo **stato finale**
   dell'evento.
2. **La soglia di C è 1 mV** di picco, filtrato 20 Hz–20 kHz, al jack.
   **A e B restano a 100 µV**, invariati rispetto ad ADR-032.
3. **C1, il fit della sola fondamentale di ADR-032, resta come diagnostica**, e
   non concorre più al verdetto. Il fit delle armoniche resta nel sottocomando
   `armoniche` di `v2_metodo.py`.
4. **Il pavimento di C2 si misura e si riporta accanto a ogni verdetto**
   (grandezza `C2_pav`, dalle celle a evento nullo). Un valore di C2 che sta
   sotto il proprio pavimento **non è una misura**: si dichiara non decidibile,
   non conforme.
5. **Il solutore resta `trap`.** `method=gear` è rifiutato.
6. Il deck `tb_v2_mute_graduale.cir` acquista una **rampa da 3 s** accanto a
   20 ms, 200 ms e 1 s.

## Perché

- **Perché non la differenza cruda.** Una differenza `v_evento − v_riferimento`
  respingerebbe **ogni** mute, anche uno infinitamente lento: un mute toglie per
  forza volt di musica, e quel residuo sta alla frequenza del tono, non a 1/T,
  quindi il passa-alto a 20 Hz non lo tocca. È esattamente il problema che il fit
  di ADR-032 esisteva per evitare, e ADR-032 lo dice: «Un mute toglie per forza
  volt di musica: confrontati così con 100 µV, boccerebbero anche la dissolvenza
  più lenta». Sottraendo invece i **residui**, la distorsione di regime —
  identica nelle due corse — si cancella, una dissolvenza lenta resta dentro il
  fit e passa, un taglio netto sopravvive e cade.
  L'interpretazione è dichiarata perché la risposta dell'utente («C lo
  consideriamo come differenza dal riferimento») ammetteva anche la lettura
  cruda, che non funziona.
- **Perché non serve fittare le armoniche dentro C2.** L'utente ha chiesto anche
  «fittiamo anche le armoniche». La differenza dal riferimento **cancella ogni
  contenuto di regime**, non le prime venti armoniche soltanto: sottrae più di
  quanto un fit armonico sottrarrebbe, e lo fa senza il problema di
  condizionamento che un fit a quaranta parametri avrebbe su una finestra di
  10 ms, che a 20 Hz copre un quinto di periodo. Il fit armonico resta quindi
  dove serve — nella diagnostica — invece di essere duplicato nel verdetto.
  L'autotest lo misura: con h2 a 900 µV iniettata su una corsa senza eventi, C1
  legge 898 µV e C2 legge **esattamente 0**.
- **Perché 1 mV e non 100 µV.** Il pavimento misurato del metodo con musica a
  1 kHz e fondo scala sta fra 0,4 e 0,7 mV: sotto quella cifra non c'è misura, e
  una soglia sotto il pavimento del proprio metodo non è verificabile — darebbe
  «SOPRA» a qualunque circuito, compreso uno fermo. 1 mV sta 2,6 volte sopra il
  pavimento del fit e 1,4 volte sopra quello della differenza, quindi entrambe le
  letture diventano decidibili.
- **Perché A e B restano a 100 µV.** Lì la risoluzione c'è davvero: A senza
  segnale misura a picovolt, a 20 Hz a 8,5 µV, e B misura 20 mV. Alzare anche
  loro butterebbe via risoluzione che il metodo possiede.
- **Quanto costa in udibilità, calcolato e non misurato.** Con la formula di
  NC-028 (finale ×21,1, Heresy 96 dB/1 W/1 m) 1 mV vale **53,5 dB SPL** di picco
  a 1 m, contro i 33,45 dB dei 100 µV. NC-028 dice però che quella formula
  «tratta il picco del fronte come un tono, e un clic di millisecondi si sente
  meno di un tono»: è un limite superiore grossolano. La cifra resta scritta qui
  perché la scelta sia leggibile per quello che è.
- **Perché `trap` e non `gear`.** `gear` abbassa poco il pavimento (A da 705 a
  476 µV, C da 1,23 a 1,10 mV) e in cambio è un integratore numericamente
  smorzante: attenuerebbe proprio le oscillazioni di commutazione che V2 deve
  misurare. Il rischio è far sparire il transitorio invece di misurarlo.
- **Perché una rampa da 3 s.** Con rampa efficace ~3/13 di T vale ~700 ms:
  non raggiunge la conformità (a 1 kHz servirebbero oltre 10 s), ma dà un quarto
  punto misurato sulla legge 1/T invece di un'estrapolazione.

## Conseguenze, scritte e non decise

- **La soglia di C è provvisoria finché i modelli sono segnaposto** (NC-017).
  Il pavimento che la giustifica è in parte distorsione di modelli non veri: con
  modelli del costruttore la cifra va rifatta, e potrebbe scendere.
- **C non potrà mai «accettare» una variante da sola** finché il pavimento resta
  dove è: può solo respingerla. L'accettazione a 100 µV di A e B resta piena.
- **Il pavimento diffuso resta non attribuito.** È una domanda aperta di L29b,
  non una cosa risolta qui.

## Alternative scartate

- **Soglia unica a 1 mV per A, B e C**: butta via la risoluzione che A e B hanno.
- **Soglia di C a 500 µV**: sta solo 1,28 volte sopra il pavimento del fit e
  **sotto** quello della differenza (705 µV), quindi renderebbe inutilizzabile
  proprio la lettura scelta come verdetto.
- **100 µV invariati col livello di prova di C abbassato di 20 dB**: il conto è
  magro. Il pavimento scende come V^1,65 (misurato: ×6,7 per ×3,16 di livello)
  mentre il taglio scende linearmente, quindi 20 dB comprano solo 4,5 volte: il
  pavimento del fit riscalato a fondo scala darebbe 87 µV, senza margine, e
  quello della differenza 158 µV, ancora sopra. In più la cifra a fondo scala
  diventerebbe un'estrapolazione, non una misura.
- **`method=gear`**: vedi sopra.
- **Riscrivere ADR-032**: le ADR non si riscrivono. Questa la precisa.

## Da riaprire se

- **I modelli diventano quelli del costruttore** (NC-017 chiusa): il pavimento
  di C va rimisurato e la soglia di 1 mV rivista, presumibilmente verso il basso.
- **Il pavimento diffuso viene attribuito** a una causa rimovibile: la soglia di
  C può tornare verso i 100 µV.
- **All'ascolto del prototipo** un clic sotto 1 mV risulta udibile: la soglia era
  troppo alta, e la misura sul prototipo la sostituisce.
- **La finestra di 10 ms** lascia passare clic o boccia dissolvenze (già in
  ADR-032).
- **Un metodo di misura senza fit** diventa disponibile: per esempio due corse
  sulla stessa griglia temporale imposta, in cui anche il rumore numerico si
  cancella.

Precisa **ADR-032** (la soglia e il metodo di C). Non supera nessuna ADR: la
soglia di A e B, il nodo, i carichi, il filtro, il campionamento e i contatti
restano quelli di ADR-032.
