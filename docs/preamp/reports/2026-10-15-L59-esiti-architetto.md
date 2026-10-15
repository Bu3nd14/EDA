# 2026-10-15 — L59, gli esiti della revisione avversariale del rivelatore di continua

**Documento datato: non si riscrive.** Le voci che apre vivono in `../NONCOMPLIANCE.md`. Il
report dell'architetto, verbatim, è `2026-10-15-L59-architetto-avversariale.md`. La decisione
nuova è **ADR-080**.

## Che cosa è stato questo lotto

L'utente, il 2026-10-14, dopo la chiusura di L45d2b1: «non sono certo che il rilevatore di
continua sia OK, un segnale sotto i 16Hz é un input assolutamente plausibile, modifica il piano
per far rivedere il rilevatore di continua all'avversariale come prossima cosa», e «aggiungi per
favore il task di rivedere e confrontare con letteratura e cercando online (sempre a carico
dell'avversariale)». Questo lotto è quella revisione, e la decisione che ne è venuta.

### La cecità, com'è andata davvero

- **Agente nuovo, non un fork**, lanciato per primo, in background, dal checkout principale. Il
  prompt conteneva la data, il dubbio dell'utente **senza la frase sui 16 Hz** («non sono certo che
  il rilevatore di continua sia OK»), le sei voci da contestare, la richiesta della letteratura con
  le fonti, le letture. Niente dei limiti dichiarati di ADR-079 oltre a ciò che sta nei file.
- **Il controllo cieco sui 16 Hz non è valido.** L'architetto dichiara (R2) di aver avuto nel
  contesto fin dall'inizio il titolo di una nota di memoria dell'utente, «Sotto i 16 Hz è
  plausibile». L'indice delle memorie arriva anche agli agenti lanciati dalla sessione. Che abbia
  sollevato i segnali sotto la banda **non dice quindi niente** sulla sua sensibilità. Il rilievo
  che nessuna nota conteneva è R1, il guasto mascherato dalla musica: quello l'architetto l'ha
  trovato da sé, e non l'avevano visto né l'orchestratore né l'altro modello (sotto).
- **Ciò che aveva visto l'orchestratore prima del lancio:** `NEXT-SESSION.md`, quella stessa nota
  di memoria, l'inizio degli esiti di L52. Non aveva letto `dc_detector.py`, ADR-079 né il report di
  L45d2b1.
- **Bash rifiutato di nuovo**, come in L52 («this command's working directory resolved to the
  shared checkout … Refusing to run it there»). L'agente era stato lanciato prima del worktree, ma
  la sessione ci è entrata mentre lavorava. **Ogni cifra del report è un calcolo a mano.** Per la
  prossima volta: il worktree si apre **dopo** che il revisore ha finito, e un controllo cieco su un
  tema che sta in una nota di memoria va dichiarato impossibile in partenza.
- L'architetto dichiara la fase 2 letta solo a rilievi scritti (NC-063, la testata del registro,
  NC-059, NC-061, NC-062), e nessun rilievo tolto o ammorbidito.

## Il dubbio dell'utente, e la risposta

**Il dubbio era fondato, e il rivelatore aveva anche un difetto che il dubbio non nominava.**

1. **Sotto la banda: sì, scatta su ingressi sani** (R2). Sulle uscite fisse, che portano la
   sorgente a 0 dB a qualunque volume, un'ondulazione fra 1 e 5 Hz da 0,6–1,35 V di picco
   (0,4–0,7 V agli angoli delle tolleranze) lo fa scattare, e lo scatto spegne l'apparecchio fino
   al frontale. Il phono di casa dà ~0,7 V di picco nominali. Lo fa scattare anche una sorgente che
   si accende con la continua che il contratto le concede (0,65 V: 163 ms fuori finestra all'angolo
   basso). Il limite scritto in ADR-079 era sbagliato anche nella forma: per un seno la frequenza
   critica è ~8 Hz, non 16; e «a volume massimo» non vale per le fisse.
2. **Con la musica sopra può non scattare** (R1). Tutti i 762 guasti del banco di L45d2b1 erano in
   silenzio. Il temporizzatore riparte a ogni rientro nella finestra, quindi un avvallamento del
   basso ogni 63–82 ms basta a tenerlo a zero: un guasto che lascia +1,93 V su una fissa resta
   ~0,88 s sopra il tetto, 9 volte il limite, se la musica scende sotto −1,35 V abbastanza spesso.
   È un calcolo a mano, da provare su un banco con la musica.

## I rilievi, per nome, e che cosa ne ha deciso l'utente

| Rilievo | Severità proposta | Decisione dell'utente | Voce |
|---|---|---|---|
| Il guasto mascherato dalla musica (R1) | bloccante per il congelamento della topologia | **bloccante** | **NC-064** |
| Lo scatto sotto la banda e sulla continua delle sorgenti (R2) | maggiore | **bloccante** («Lo scatto sotto la banda bloccante») | **NC-065** |
| La stessa reazione per un guasto e per un evento della sorgente (R3) | minore | minore | NC-066 |
| All'accensione con un guasto presente, scatto e chiusura dei jack negli stessi millisecondi (R4) | minore | minore | NC-067 |
| Le correnti del rivelatore nella massa audio (R5) | osservazione | osservazione: vincolo di layout per G2, scritto nel prompt del lotto nuovo | — |
| Cifre vecchie nei commenti (91,5 invece di 86,2 ms; il seno a 10 Hz «atteso lo scatto») (R6) | minore | minore | NC-068 |
| Il precedente non citato (Zenith US 4,301,330) e la finestra larga ±26 % agli angoli (R7) | osservazione | osservazione: il precedente è citato in ADR-080 | — |

**Regge, secondo l'architetto:** l'alimentazione dal maggiore fra VPLUS e VRELAY, la 634k verso
VMINUS, la linea su J4 coi tre gate in hardware, la ritenuta nel firmware, i dodici canali. Nessun
eccesso di progetto. La costante termica della bobina mobile è «a few seconds» (US 8,259,953):
100 ms è prudente per il calore.

## Le altre proposte messe a confronto

Durante il lotto l'utente ha portato una proposta di **un altro modello**, scritta offline
(`data/2026-10-15/L59/proposta-altro-modello.md`, verbatim; l'architetto non l'ha vista), e tre idee
proprie. L'orchestratore le ha lette contro ADR-079 e contro il report.

### La proposta dell'altro modello (rivelatore a microcontrollore, 100 ms)

- **Vede il problema dell'ondulazione** (0,5–5 Hz), come R2, e non lo accetta come limite.
- **Non vede il guasto mascherato dalla musica**, e la sua soluzione A lo peggiora: una continua da
  guasto con la musica sopra «si muove», quindi la derivata la classifica come infrasuono e il tempo
  sale a 1500 ms, 15 volte P10.
- **Il suo pseudo-codice scatta proprio sul disco ondulato**: il contatore è uno solo e il tempo
  bersaglio cambia a ogni campione. A calcolo, con 2 V a 2 Hz e la soglia a 0,58 V, l'uscita resta
  sopra soglia ~203 ms, e al picco (~102 ms dopo la soglia) la pendenza è nulla con il contatore
  già a ~100.
- **Le soluzioni B e C, alla lettera, tolgono anche la continua**: un passa-alto a 15–20 Hz sul
  percorso del rivelatore lo rende cieco a 0 Hz; la «media a lungo termine» di B è il passa-basso
  che ADR-079 aveva già scartato.
- **La premessa «sopra i 20 Hz il semiperiodo dura 25 ms»** vale per un seno; un impulso al 90 %
  resta dallo stesso lato quasi tutto il periodo.
- **Mette la protezione nel firmware**, contro PR-24 («La sicurezza non dipende dal firmware»).
- Nessuna fonte citata, nessuna ampiezza dell'ondulazione alle uscite.

### Le idee dell'utente

1. **Una finestra di osservazione che scorre, più lunga di 100 ms.** Lecita: P10 conta il tempo
   dall'istante del guasto, quindi dopo il guasto restano ~95 ms per decidere, ma la memoria può
   guardare indietro quanto vuole. Aiuta col disco ondulato già in corso (periodico, 0,56 Hz a 33⅓
   giri), non con la puntina appena appoggiata né con un guasto che arriva durante un'ondulazione.
   Superata dalla decisione: con la presa differenziale l'ondulazione non arriva al confronto.
2. **Quale tempo è fisicamente ragionevole.** Il conto dell'orchestratore, con le ipotesi dichiarate
   (6 Ω di bobina, ~2 J/K, finale a 21,1×): +50 °C nella bobina in ~3,7 s con 0,6 V al preamp,
   ~1,8 s con 0,87 V, ~0,5 s al clip del finale. Le stime sono coerenti con la fonte dell'architetto
   («a few seconds»). Le protezioni dei diffusori (ADR-069) sono a tempo inverso; P10 tiene 100 ms
   fissi, più severo di loro sulla continua piccola. Il disco ondulato chiederebbe ≥ 0,9 s.
3. **Un filtro subsonico sul solo ingresso del phono, e lo scatto solo per tensioni alte ma
   veloce.** Il Technics SU-9070, verificato in rete: ingressi linea «DC – 100,000 Hz (+0/−3 dB)»,
   «Low Filter (Subsonic): 20 Hz, −12 dB/oct», mute −20 dB, nessuna protezione elencata
   ([hifi-wiki](https://hifi-wiki.com/index.php/Technics_SU-9070); il
   [catalogo 1980](https://www.preservationsound.com/wp-content/uploads/2013/08/Technics_Pro_1980.pdf)
   lo chiama «DC flat amplifier», è una scansione e non si è potuta leggere per intero; se il filtro
   sia commutabile non è confermato). Per tenere E9 (±0,2 dB da 20 Hz) il filtro andrebbe al 3°
   ordine a ~12 Hz (−29 dB a 4 Hz), non a 20 Hz. «Solo tensioni alte» ha una trappola: col finale a
   21× già 1 V al preamp sono 21 V sul woofer e 2 V portano il finale al clip; alzando la soglia a
   2 V i 57 guasti sotto i 2 V resterebbero al condensatore d'uscita, fino a ~0,9 s sulle fisse.
   È stata la seconda strada sul tavolo («due rami»), non scelta.
4. **Un comparatore digitale invece che analogico.** Aiuta nella taratura delle soglie, negli
   algoritmi, nel guadagno di B (il micro lo sa) e nella diagnosi. Non cambia l'informazione (in
   ~85 ms 1 Hz e la continua sono la stessa forma d'onda; la media di un basso a 20 Hz da 4 V di
   picco su 85 ms lascia fino a ~0,8 V), non rende più facile la presa sul gate d'ingresso (anzi:
   il campionatore vuole un buffer), mette la protezione nel firmware (PR-24) e porta prese
   analogiche attraverso J4. Non scelto.

## La decisione

Le domande, per nome, e le risposte dell'utente:

- **La direzione.** Dopo un approfondimento chiesto dall'utente sul rivelatore differenziale e sul
  digitale: **«Differenziale analogico, A dopo»**. Il rivelatore guarda la differenza fra
  l'ingresso e il nodo di reazione di ogni blocco invece della sua uscita: subito sui buffer delle
  fisse e sul blocco d'uscita; sul blocco d'ingresso si decide nel lotto nuovo, dopo la prova di
  rumore e fronti al gate. Comparatori, persistenza, linea su J4, gate in hardware e ritenuta
  restano. → **ADR-080**.
- **Le severità:** «Lo scatto sotto la banda bloccante»; le altre come proposte.
- **L'ordine:** «Lotto proprio, prima»: un lotto nuovo, **L60**, prima di L45d2b2.
- **L'ondulazione del phono:** «No, usiamo una stima»: si dimensiona sul caso peggiore della
  letteratura e lo si scrive come ipotesi.

## Che cosa resta da provare (va a L60)

- Il banco dei guasti **con la musica** (R1), letto per differenza dalla corsa senza guasto, sul
  rivelatore di oggi e su quello nuovo.
- Le ondulazioni sotto i 10 Hz e la continua delle sorgenti (R2) sullo stesso banco.
- L'errore fra ingresso e reazione di un blocco sano ad alta frequenza e al clip: decide la soglia.
- Quali guasti il differenziale **non** vede (quelli che spostano il nodo d'ingresso stesso, le
  parti dopo il blocco, i due corti della scelta 9), con P10 per ognuno.
- Sul blocco d'ingresso: la corrente della presa sul gate, il rumore, i fronti dei comparatori che
  rientrano.

## La letteratura chiesta dall'utente dopo la decisione

L'utente, a decisione presa: «ci sono esempi in letteratura (Douglas Self, Pass, etc) di un
rilevatore di continua? come hanno affrontato il problema in generale?». Cercato dall'orchestratore:
- **La pratica comune è il filtro più la finestra, sul finale.** «All DC protection schemes rely on a
  filter to remove the audio component down to the lowest frequency of interest»
  ([ESP AN-017](https://sound-au.com/appnotes/an017.htm)). Il manuale di Self (*Audio Power Amplifier
  Design Handbook*, 4ª ed.) ha un capitolo sulla protezione con la continua e i servo
  ([descrizione](https://www.safaribooksonline.com/library/view/audio-power-amplifier/9780240521626/));
  i circuiti non si sono potuti leggere. Le schede derivate da Self nei forum: continua, ritardo
  all'accensione, mancanza di rete, su relè ([diyAudio](https://www.diyaudio.com/community/threads/speaker-protection-circuit-questions.379564/)).
- **Pass**: nessun documento suo sulla protezione dalla continua. Dai forum, nei finali Aleph nessuna
  protezione dichiarata, e Pass che non ricorda un Aleph che abbia rotto un altoparlante
  ([diyAudio](https://www.diyaudio.com/community/threads/relay-or-not-relay.13477/latest)): una
  scelta di affidabilità, non un rivelatore. Fonte secondaria.
- **Il precedente del principio di ADR-080: il Crown IOC** («Input/Output Comparator»). Un
  amplificatore d'errore confronta ingresso e uscita del finale, e una finestra su quell'errore
  accende l'indicatore: «An op-amp senses the input signal and output signal at the same time. If
  there is any variation in the shape of the two waveforms, then the output does not truly
  represent the input», sensibile a meglio dello 0,05 % ([AE Techron](https://aetechron.com/ioc/);
  [pinkfishmedia](https://pinkfishmedia.net/forum/threads/crown-ioc-distortion-weirdness.244772/)).
  Lì serve a segnalare la distorsione, non a proteggere; ma è lo stesso confronto, sordo alla musica
  per costruzione. Fonti del costruttore successore e di un forum, non lo schema Crown.
- **Nei preamplificatori un rivelatore sulle uscite non si è trovato**, né dall'architetto né qui.
