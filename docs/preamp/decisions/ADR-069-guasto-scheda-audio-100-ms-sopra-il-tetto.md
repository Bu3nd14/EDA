# ADR-069 — Un guasto della scheda audio: al più 100 ms sopra il tetto di non-danno, su ogni uscita, con qualunque apparecchio a valle

Data: 2026-10-13 · Stato: accettata

**Rapporti con le decisioni precedenti.**
- **Aggiunge PR-30** al PRB (ADR-053) e **P10** a `REQUIREMENTS.md`. PR-23 e P9 (b) restano parola
  per parola: valgono per la rete e l'alimentatore.
- È la strada 1 di quelle proposte dopo L45a (il tetto per l'alimentatore, una durata per i guasti
  della scheda audio). La scelta del **rimedio** resta a **L45d** (NC-042).

## Contesto

L45a (`reports/2026-10-13-L45a-fmea-blocco.md`) ha simulato 112 modi di guasto del blocco di
guadagno, durante l'ascolto. Un guasto su due porta il jack oltre il tetto di non-danno di PR-23
(0,87 V): ~14,9 V con il blocco al rail. Il tetto **non si può rispettare** per questi guasti con
nessun rimedio. Il gradino arriva al jack insieme al guasto (picco a 0 ms), e il mute inserito a 0,1,
1, 3 o 10 ms lascia il picco a 14,8–14,9 V. Né si può limitare l'escursione al jack, perché col
volume al massimo la musica stessa supera 0,87 V. Il tetto di PR-23 è scritto per la rete e
l'alimentatore, dove le uscite si staccano *prima* che il circuito esca di regolazione. Per un
componente che si rompe durante l'ascolto quel meccanismo non c'è, e serve un altro criterio.

## Decisione

Per un guasto singolo della scheda audio durante l'ascolto, **il colpo resta sopra 0,87 V al più
100 ms su ogni uscita**. Si misura sul jack senza filtro, con l'uscita a vuoto, e si assume a valle
un apparecchio accoppiato in continua senza protezione propria. Le parole dell'utente
(2026-10-13): «io mi adeguerei allo standard dei 100ms»; «non so come sia internamente il Singxer, e
non escludo un finale accoppiato in continua»; e sul testo di PR-30, «Firmo così».

## Perché

- **Il danno di un colpo sta nella sua durata, non nel picco.** Il picco è già al clip del finale
  (~114 dB SPL a 1 m col cj di oggi), lo stesso della musica a volume pieno. Quello che danneggia è
  una continua che dura: il cono di un woofer spinto e tenuto a fine corsa dietro un finale
  accoppiato in continua, la sua bobina che scalda, la membrana di un'elettrostatica tirata contro
  uno statore. Da recensioni, non da uno schema, la Stax SRM-T1 risulta accoppiata in continua.
- **100 ms è quello che fanno le protezioni dei diffusori dei finali commerciali** con una continua
  grande. Su schede col µPC1237: ~100 ms con 10 V, meno di 0,5 s con 20 V, secondi con 2 V
  (Hifisonix, una scheda di protezione; Pinkfish, misure su una scheda). Il colpo di un guasto della
  scheda, al clip del finale, sta nella fascia «grande».
- **Generale per scelta dell'utente.** Il finale potrebbe cambiare («potrei in futuro cambiare il
  finale»), e del Singxer non si sa se protegga le cuffie. Il criterio non conta quindi né sul
  trasformatore d'uscita del cj EV250, che oggi blocca la continua, né su protezioni a valle.
- **Oggi non è rispettato**, a calcolo, per il gradino di 14,9 V di un blocco al rail, che decade col
  condensatore d'uscita da 4,7 µF sui bleed:

  | Uscita | Carico | Costante di tempo | Sopra 0,87 V |
  |---|---|---|---|
  | Principale | a vuoto, 220 k ∥ 220 k | 0,52 s | **~1,5 s** |
  | Principale | cj, 100 kΩ | 0,25 s | ~0,7 s |
  | Fisse | a vuoto, 470 k ∥ 470 k | 1,1 s | **~3,1 s** |
  | Stax | 50 kΩ | 0,20 s | ~0,56 s |

  Un rivelatore che apra il sink di `MUTE_CMD` porterebbe il colpo a qualche millisecondo di
  rilevazione più i 3 ms del relè (G6K, rilascio 3 ms max). Il rivelatore che dopo L45a sembrava
  inutile (non abbassa il picco) torna quindi un candidato, per la durata. La scelta è di L45d.

## Alternative scartate

- **Il tetto di 0,87 V di picco anche per i guasti della scheda audio**: irraggiungibile con qualunque
  rimedio (L45a, il taglio a 0,1 ms).
- **1 s**: passerebbe quasi senza far niente col carico del cj, ma non con l'uscita a vuoto né con un
  finale accoppiato in continua senza protezione. È più lungo delle protezioni dei diffusori.
- **10 ms o meno**: più severo dello standard, e lo raggiunge solo un rivelatore molto veloce.
  Nessun dato a valle lo chiede.
- **Il guasto singolo accettato e dichiarato, senza criterio**: lascia la catena a valle senza
  garanzia proprio nel caso che l'utente non esclude, un finale accoppiato in continua.

## Da riaprire se

- Si conosce l'interno del Singxer SA-1 o del finale nuovo, e c'è una protezione dalla continua a
  valle di cui il progetto possa fidarsi.
- Lo schema della SRM-T1 mostra un accoppiamento in alternata all'ingresso: allora per la Stax conta
  il suo condensatore, non i 100 ms.
- L45d trova che 100 ms costano un circuito sproporzionato al rischio: si torna all'utente con i
  numeri, non si allenta in silenzio.
