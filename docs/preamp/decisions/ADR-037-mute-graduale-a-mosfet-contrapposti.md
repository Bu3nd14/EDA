# ADR-037 — Il mute graduale reale: MOSFET contrapposti con driver fotovoltaico, in serie e verso massa, col relè NC tenuto

Data: 2026-09-16 · Stato: accettata

## Contesto

ADR-036 ha scelto «per ora» un mute **graduale in serie con rampa da 3 s**, ma
misurato solo con un elemento **ideale**: una conduttanza pura da 1e-12 a 10 S,
senza capacità, col jack mai portato a massa. L29b deve farne un circuito reale.
La tecnica è libera (ADR-021 §4). Due verifiche scratch hanno cambiato la
domanda prima della scelta. Sono **SIMULATE, modelli segnaposto, elemento
ideale**, e non sono misure di V2 sul circuito reale.

**1. Un elemento solo in serie non rispetta B**
(`data/2026-09-16/L29b/capacita_da_aperto/`, AC, al tono di prova, prima del filtro).
- Ogni elemento reale ha una capacità da aperto. Con 2 pF, a mute inserito, al
  jack principale (100 k) arrivano **10,4 mV a 1 kHz** e **206 mV a 20 kHz**,
  contro i 100 µV di B.
- A 20 kHz servirebbero ≲ 1,4 fF: nessuna parte fisica, nemmeno il PCB.
- Con 0,1 Ω dal jack a massa, B scende a 1,5 µV anche con 10 pF.

**2. La derivazione al jack dev'essere graduale anch'essa, e lenta**
(`data/2026-09-16/L29b/sequenza_ideale/`, metodo di V2 invariato, 1 kHz, +10 dB,
100 k). Serie da 3 s, poi derivazione in Tj; al rilascio l'inverso.

| C_off / Tj | B2 principale | C2 principale ins / rel | C2 fisse ins / rel |
|---|---|---|---|
| 50 pF / 20 ms | 0,38 µV | **67,2 / 66,2 mV** | **25,5 / 25,4 mV** |
| 50 pF / 200 ms | 0,38 µV | 2,98 / 3,43 mV | 0,92 / **1,03** mV |
| 50 pF / 1 s | 0,38 µV | 2,98 / 2,97 mV | 0,83 / 0,87 mV |

Con **Tj ≈ 1 s** la coppia torna alle cifre dell'elemento ideale di ADR-036:
principale 2,93–3,05 mV, fisse 0,83–0,87 mV. Senza segnale A resta a
**4–17 pV** anche con la derivazione più rapida.

**3. L'elemento in serie resta nel percorso a mute rilasciato.**
- La sua resistenza da acceso si somma all'impedenza d'uscita: **E4 < 100 Ω**,
  misurata a **60,13 Ω** al massimo in L13.
- Un contatto di bypass non risolve: chiudendolo toglie un gradino V·Ron/R_carico,
  che con 12 V su 10 k supera 1 mV già con Ron ≈ 1 Ω.

I candidati, coi datasheet scaricati in L29b (`vendor/optocoupler/`,
`vendor/jfet/onsemi/`, `vendor/mosfet_n/`). Le somme su E4 sono **calcolate**.

| Candidato | Ron da acceso (datasheet) | E4 | Rampa | Senza alimentazione |
|---|---|---|---|---|
| Fotoresistenza, NSL-32SR3 / VTL5C4 | 60 Ω max a 20 mA / 75 Ω tipici a 40 mA | ≈ 120–135 Ω ✗ | lenta di natura, legge non pubblicata; 0,7 %/°C | aperta |
| JFET, J112 / MMBFJ112 | 50 Ω max | ≈ 110 Ω ✗ | chiede un rail di gate oltre −20 V contro ±12 V di segnale | **acceso** |
| **MOSFET contrapposti** DMN6040SVT + driver VOM1271 | 2 × 60 mΩ max a Vgs = 4,5 V (44 mΩ a 10 V, che il driver non raggiunge) | invariata ✓ | Vgs ∝ corrente nel LED su una resistenza gate-source | aperto |
| PhotoMOS AQY212EH | 0,85 Ω tipici / 2,5 Ω max | ✓ | no: 1–4 ms, come un contatto netto | aperto |

Portati all'utente il 2026-09-16, con la raccomandazione dei MOSFET contrapposti.

## Decisione

**Il mute di progetto è fatto, per ogni uscita e ogni canale, da tre elementi.**
Parole dell'utente: «confordo con te al 100% accetto i due MOSFET contrapposti
col driver fotovoltaico (in serie più un elemento graduale verso massa, relè NC
tenuto), con mute che durano circa 4 s».

1. **In serie**, fra il condensatore d'uscita e il jack: due MOSFET N **DMN6040SVT
   contrapposti**, source comuni e gate comuni, così il blocco vale in entrambe le
   polarità. Il gate è pilotato da un **fotoaccoppiatore fotovoltaico VOM1271**
   fra gate e source comuni, con una resistenza gate-source. La corrente nel LED
   fissa la tensione di gate, quindi la conduttanza.
2. **Verso massa**, dal jack: una seconda coppia uguale, col suo VOM1271.
3. **Il relè NC di ADR-012** resta dal jack a massa, come oggi. È lo **stato
   sicuro a macchina spenta** e a bobina diseccitata.

**La sequenza.**
- **Inserzione**: la serie si apre con una rampa da **3 s**, poi la derivazione si
  chiude con una rampa da **≈ 1 s**, poi il relè si diseccita.
- **Rilascio**: il relè si eccita, poi la derivazione si apre in ≈ 1 s, poi la
  serie si chiude in 3 s.
- Un'operazione di mute dura **circa 4 s** in ciascun verso.
- La rampa della serie resta quella scelta in ADR-036. Quella della derivazione
  (≈ 1 s) viene dallo scratch sopra, e il valore esatto si fissa nel sorgente
  con la misura.

**Il comando.**
- Le rampe sono rampe di **corrente nei LED** dei VOM1271, generate fuori dal
  percorso del segnale.
- **Il permissivo del trim (K6, ADR-027 §4) segue lo stato «mute completo»**, non
  il comando: il trim si abilita solo a sequenza d'inserzione finita, e si
  disabilita prima che inizi il rilascio.

## Perché

- **È l'unico candidato che lascia E4 dov'è.** Il driver porta il gate al
  massimo a Voc (≥ 7,8 V), fra i due punti del datasheet (60 mΩ max a 4,5 V, 44 mΩ
  a 10 V, pag. 3): per coppia ≤ **120 mΩ**, circa quanto un contatto G6K
  (100 mΩ max). Fotoresistenza e JFET sforano E4 già per calcolo.
- **La rampa è comandabile.** Con la resistenza gate-source, la tensione di gate
  segue la corrente di cortocircuito del fotovoltaico (a 10 mA nel LED: minimo
  6,0 µA, tipici 15 µA, massimo non pubblicato; Voc minimo 7,8 V, tipici 8,4 V;
  datasheet VOM1271, tabella «Output») fino a Voc: una rampa di corrente nel LED diventa una rampa di
  conduttanza. Il PhotoMOS commuta in millisecondi, e un contatto netto porta C a
  volt (L29a, ADR-036).
- **A macchina spenta è aperto**, perché i MOSFET sono ad arricchimento. Il JFET
  sarebbe acceso.
- **La capacità da aperto** (Coss 57 pF **tipici** a 25 V per MOSFET, massimo non pubblicato, datasheet pag. 3; due in serie nella coppia) è
  dell'ordine del caso che la derivazione da ≈ 1 s copre nello scratch da 50 pF.
  Quanto vale davvero alle tensioni del segnale lo dice il modello del costruttore.
- **Il relè NC resta** perché ADR-012 vuole il jack a massa a macchina spenta, e
  nessun elemento a stato solido lo dà senza alimentazione.
- **Il prezzo accettato**:
  - circa 4 s per ogni operazione di mute;
  - 12 VOM1271 e 24 MOSFET (tre uscite × due canali × due coppie);
  - un generatore di rampe e una logica di sequenza.

## Cosa precisa, e cosa si deve ancora verificare

- **ADR-012**, senza riscriverla. Il relè resta, a riposo verso il silenzio, e
  non è più l'elemento che taglia la musica. Taglia solo quando la derivazione
  ha già portato il jack a µV. `check_relay_safe_state.py` continua ad
  asserirlo sul relè.
- **ADR-021**, senza riscriverla. Il «mute come è cablato» di P7 non è più «tutti
  e tre i jack a massa a valle del condensatore». A mute inserito la serie è
  aperta, e lo stadio d'uscita vede solo 47 Ω, il condensatore e il bleeder. Col
  corto al connettore e il mute rilasciato, la corrente passa nei MOSFET in
  serie. P7 si rilegge su questa topologia.
- **ADR-022 §1.** Il VOM1271 è un integrato, ma comanda un discreto: i MOSFET
  sono i componenti del percorso. La sua uscita però sta **galvanicamente su un
  nodo di segnale**, fra gate e source. Il suo effetto si misura con le soglie
  di §2: ΔZout ≤ 1 Ω, Δ risposta ≤ 0,01 dB, rumore dentro la quota ausiliaria.
- **Da misurare in L29b, col metodo di V2**: A senza segnale, B, C2 col suo
  pavimento, a 20 Hz, 1 kHz e 20 kHz, tre uscite, 10 e 100 kΩ.
- **Da misurare in L29c** (caso peggiore):
  - la dispersione della soglia dei MOSFET (1–3 V) e della corrente del
    fotovoltaico (minimo 6,0 µA contro 15 µA tipici, massimo non pubblicato), che
    spostano la forma della rampa;
  - lo **spegnimento**: se i rail cadono in millisecondi, i gate si scaricano in
    millisecondi e la serie si apre di colpo, con la musica presente. Senza una
    tenuta dell'alimentazione dei LED, lo spegnimento sarebbe un taglio netto.
- **Le incognite dichiarate**:
  - la distorsione dei MOSFET durante la rampa, che entra in C;
  - il **circuito di spegnimento rapido integrato** nel VOM1271 (datasheet,
    «Integrated rapid turn-off circuitry»), che potrebbe scaricare il gate di
    colpo invece di seguire la rampa di discesa della corrente nel LED: va visto
    sul modello del costruttore prima di fidarsi della rampa d'inserzione;
  - la fedeltà dei modelli del costruttore, scaricati in L29b e non ancora
    collaudati in ngspice;
  - la disponibilità del VOM1271, che non è stato possibile leggere presso un
    distributore;
  - i 32 settimane di consegna dichiarati per il DMN6040SVT.

## Alternative scartate

- **Fotoresistenza optoaccoppiata**: E4 sforata per calcolo (60–75 Ω in più),
  distorsione non pubblicata, 0,7 %/°C; VTL5C4 senza disponibilità confermata.
- **JFET**: E4 sforata (50 Ω), acceso senza alimentazione, e un rail di gate
  oltre −20 V.
- **PhotoMOS integrato**: nessuna rampa comandabile, e CPC1017N in Last Time Buy
  (11/11/2026).
- **Serie sola**: B non si rispetta con nessuna capacità fisica (scratch 1).
- **Derivazione a contatto netto**: aprendola con la musica scopre di colpo il
  residuo della capacità, cioè mV a 1 kHz contro 1 mV di C (scratch 1 e 2).
- **Cambiare E4** per ammettere fotoresistenza o JFET, o metterne più in
  parallelo: più parti e più corrente nei LED, e la distorsione della resistenza
  in serie resterebbe non quantificata.

## Da riaprire se

- La misura dell'elemento reale **si allontana dall'ideale** oltre il fuori soglia
  accettato in ADR-036: principale oltre ~3 mV di C, oppure fisse sopra 1 mV.
- La **dispersione** di soglia e fotocorrente (L29c) porta C, o A senza segnale,
  fuori soglia.
- Lo **spegnimento** non si può rendere graduale senza un'alimentazione dei LED
  che tenga per ≥ 4 s.
- Il **VOM1271** o il **DMN6040SVT** non si trovano: la tecnica resta, la parte si
  sostituisce con una di pari Ron, Coss e fotocorrente, e la misura si rifà.
- L'**ascolto del prototipo** giudica inaccettabili i ~4 s.

Precisa **ADR-012**, **ADR-021** e **ADR-036** (la «serie» diventa serie più
derivazione). Non supera nessuna ADR.
