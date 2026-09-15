# ADR-032 — V2 ha una soglia: al jack, 100 µV di picco in banda, nel caso peggiore, per il gradino, il residuo in mute e il taglio della musica

Data: 2026-09-15 · Stato: accettata

## Contesto

V2 chiedeva di misurare i transitori di commutazione senza dire quanto è
accettabile. NC-028, il gradino al rilascio del mute, non era decidibile. Il
criterio 3 di ADR-030 confrontava due gradini «nell'uso reale» senza un limite.
L'utente, 2026-09-15 (`STATE.md`, «Dopo L20»): «non deve essere udibile come bump
in nessuna condizione e su nessuna uscita, pensiamo ad un rilascio soft a
resistenza variabile se necessario, o a qualsiasi altra soluzione. L'uso reale
non conta».

## Decisione

1. **≤ 100 µV di picco, filtrato 20 Hz–20 kHz, sul jack di ognuna delle tre
   uscite** (`MAINJACK`, `FIXJACK1`, `FIXJACK2`), in ogni condizione,
   **accensione e spegnimento compresi**. Sullo spegnimento l'utente, in L38:
   «si lo spegnimento rientra».
2. **Vale per tre grandezze distinte**, scelta dell'utente in L38 («A, B e C»):
   - **A**, il gradino che una commutazione lascia al jack;
   - **B**, la musica che arriva al jack a mute inserito;
   - **C**, il taglio netto della musica quando un contatto commuta.
3. **Sotto i 20 Hz nessun limite oltre il filtro**: il cono può muoversi «in
   maniera non distruttiva».
4. **Il caso peggiore sostituisce l'uso reale, anche nel criterio 3 di ADR-030.**
   Il gradino del cambio sotto mute seguito dal rilascio si confronta con quello
   del cambio a caldo **nel caso peggiore**. Il resto del criterio non cambia.
5. **Il metodo sta in `REQUIREMENTS.md`, V2, «Metodo di misura».** Le scelte di
   metodo sono di questo lotto, non misure d'udibilità:
   - passa-alto Butterworth del **2° ordine**; l'utente sull'ordine: «indifferente»;
   - finestra di **10 ms** per C, scelta dall'utente fra le proposte;
   - contatto a **100 mΩ**;
   - carichi da **10 kΩ e 100 kΩ**.

## Perché

- **Nessuna cifra del repo sta sotto soglia.** Tutte da NC-028 e ADR-030:
  - rilascio con musica: **5,37 V** a +10 dB, 1,79 V a 0 dB, 1,72 V sulla fissa,
    simulati in L11;
  - col contatto prima del condensatore, un gradino d'offset di 14–104 mV, da
    simulazioni scratch;
  - il cambio di guadagno a caldo: 6–114 mV, **calcolati**;
  - residuo a mute inserito: 4 mV picco-picco, da simulazione scratch con il
    contatto a 0,01 Ω (`tb_mute_corto.cir`). Il datasheet G6K dà **100 mΩ
    massimi** (`vendor/relays/omron/G6K/en-g6k.pdf`, Characteristics).
- **100 µV sono ≈ 33 dB SPL di picco a 1 m**: calcolati con la formula di
  NC-028, limite superiore, non misurati. Il valore è 33,45 dB
  (`data/2026-09-15/L38/calcolo_v2.out.txt`); il diario scriveva «circa 34».
- **Il filtro non ammorbidisce un gradino netto.** 104 mV escono a 0,11 V a
  ogni ordine del passa-alto. Separa solo le variazioni lente: una rampa di
  104 mV in 500 ms dà 0,755 mV col 2° ordine, 1,655 col 1° e 0,397 col 4°
  (calcolato, stesso file). L'ordine sposta di circa ×2 la durata che deve avere
  un rilascio lento, e non cambia il verdetto su nessuna cifra esistente.
- **C ha bisogno di una finestra.** Un mute toglie per forza volt di musica:
  confrontati così con 100 µV, bocerebbero anche la dissolvenza più lenta.
  Perciò si sottrae la musica ricostruita su 10 ms. Una dissolvenza più lenta
  resta nel tono ricostruito, un taglio più rapido resta nel residuo.
- **Conseguenze, scritte e non decise.**
  - La «regola d'uso» che ADR-030 tiene come alternativa all'interblocco non
    rende conforme V2: «L'uso reale non conta».
  - Con la musica presente, un contatto che commuta di colpo non rispetta C. Se
    L29 lo conferma serve un mute graduale, come l'utente aveva previsto:
    «rilascio soft».

## Alternative scartate

- **La soglia su `v(OUT)`**: non è ciò che arriva al cavo («Nota su jack», L34).
- **Nessun filtro**: conterebbe la scarica infrasonica (τ 0,32 s), che l'utente
  lascia libera.
- **Valore efficace invece del picco**: un clic breve ha un valore efficace
  piccolo.
- **Solo A**: proposta in L38; l'utente ha scelto A, B e C.
- **L'uso reale**: escluso dall'utente.

## Da riaprire se

- **Il finale non è più ×21,1** o i diffusori non sono più 96 dB/1 W/1 m: la
  stima in dB SPL cambia.
- **Il guadagno dell'SRM-T1 diventa noto**: la stima per le fisse diventa
  calcolabile.
- **L29 trova che nessuna variante di mute rispetta A, B e C insieme**: la
  scelta torna all'utente, con i numeri.
- **La finestra di 10 ms**, all'ascolto del prototipo, lascia passare clic o
  boccia dissolvenze.
- **Il relè di mute non è più un G6K**: vanno riletti resistenza di contatto e
  tempi.

Precisa **ADR-030** (criterio 3) e **ADR-012** (cosa il mute deve garantire). Non
supera nessuna ADR.
