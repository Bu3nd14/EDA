# L54b3a — la robustezza del temporizzatore al banco: la rete sporca, i fronti veloci, i rimbalzi (2026-10-28)

Prima parte di **L54b3** (diviso dall'utente all'inizio, «Due parti»: questa la rete, i fronti veloci
contro la ritenuta, i rimbalzi, a 25 °C; la seconda le tolleranze e la temperatura). Il punto 7 del
prompt di L54b. Decisioni di riferimento **ADR-102**, **ADR-103**. `<L>` = questa cartella. Python di
analisi con `/usr/bin/python3 -I`. Le forme d'onda non stanno nel repository: si rifanno.

## Il banco

`psu/` è il banco di L54b2 copiato, con `carico.txt`. Col solo copiato e senza opzioni nuove i deck di
`guasto` e `buco20` (`--timer sorgente --n2n7002 ds --tss 3.0 --comparatore tarato`) sono quelli di
L54b2 riga per riga, salvo il percorso di `cmpta.lib`; con le opzioni nuove aggiunte e assenti, lo
stesso (provato). Le opzioni (intestazione di `genera_tb_psu.py`, tutte solo con `--timer sorgente`):

- `--rete-forma calo:<f>:<t0>:<durata>:<rampa> | buco:<ms>:<zero|cresta> | sovra:<f>:<t0>:<durata>`:
  l'inviluppo della rete al posto di quello del caso, poi per `--rete`. **Provata**: `buco:20:zero` su
  `buco20` dà il deck di L54b2 salvo l'intestazione.
- `--disturbo <REF>:<V>:<fronte>:<larghezza>:<t0>`: un impulso trapezoidale in serie all'uscita del
  regolatore REF (U512 → V5, U503 → `VRELAY_REG`). I regolatori del banco sono ideali (nessuna banda):
  un gradino di carico non fa fronti, quindi il fronte si inietta.
- `--rimbalzo <front|sw3>:<ms>:<seme>`: la transizione dell'interruttore a TE diventa un treno di
  aperture e chiusure lungo `<ms>`, intervalli uniformi fra 20 µs e 1 ms, col seme dichiarato.
- `--durata`, `--passo-max` (il passo massimo del transitorio, 20 µs di L41b2), `--sonde-piu` (la base e
  il collettore della ritenuta, V5, i grezzi, e tre `.meas` sui punti del transitorio: la base prima e
  dopo TE, il minimo di VRELAY_EN), `--ritenuta costruttore`, `--bat54 costruttore`.

`psu/analizza_rob.py`: le colonne di `analizza_an.py` di L54a, calcolate allo stesso modo, più i
conteggi di mute e di K501 dopo TE, il ritorno della rete (`t_rit_ms`), la musica dopo il ritorno
(`dmus_ms`), la ritenuta tenuta alla fine, le tre `.meas`, i grezzi e V5.

## I criteri, scritti prima delle corse

Per ogni caso: **niente scatto a vuoto** dell'accensione, del mute o della ritenuta, e **lo scatto
quando deve**. Dal caso `buco20` (in musica a TE = 3,0 s, frontale acceso), alle tre reti:

1. **Se i rail restano in regolazione** (V+ mai sotto 10,6 V): nessun mute (`n_giu` 0), musica alla
   fine, la ritenuta no.
2. **Se escono**: il mute prima (`s41`, `r41`, `C2`, `C3`), poi la musica che torna **≥ 500 ms dopo il
   ritorno della rete** (`dmus_ms`), una sola volta (`n_su` 1); **la ritenuta mai**: un calo o un buco
   di rete non è un guasto della scheda (ADR-102 la vuole per un rail o `VRELAY_REG` fuori con la rete
   presente, e la rete «presente» qui è una rete bassa). K501 alla fine chiuso.
3. **La sovratensione** (+15 % per 0,5 s): nessun cambio; e il grezzo massimo contro la tensione
   d'ingresso massima dei regolatori (TPS7A4701 36 V, TPS7A3301 −36 V, SBVS204G / SBVS190), alle tre
   reti.
4. **Durante l'accensione** (calo a −20 / −30 % 0,3 s dopo il frontale): l'accensione si completa,
   senza ritenuta.

**I fronti veloci** (`--disturbo` su V5 e su `VRELAY_REG`, in musica e in mute): la ritenuta non scatta
(`bn_max` sotto 0,45 V, la soglia di T6b). Si cerca l'ampiezza a cui scatta, coi fronti 10 ns / 100 ns /
1 µs e coi condensatori base-emettitore (C554 / C555) a 0, 100 pF, 330 pF, 1 nF, 2,2 nF, coi transistor
del costruttore (i generici non hanno capacità: non possono scattare per un dv/dt); il margine si dà
in dB contro il fronte più grande che i datasheet dei regolatori danno per i gradini di carico della
scheda (K501, i relè della scheda audio).

**I rimbalzi** (treni di 1, 3, 5 ms, tre semi) all'accensione, allo spegnimento, al rilascio del mute e
al suo inserimento: lo stesso esito della transizione pulita (`n_giu`, `n_su`, `n_k501`, la ritenuta);
gli istanti al più più tardi della lunghezza del treno.

**Il controllo numerico**: un caso per famiglia rifatto col passo massimo 5 µs, gli stessi verdetti e
gli istanti entro un campione (0,1 ms).

Se una prova fallisce, il rimedio si porta all'utente coi numeri prima di cambiare il circuito.

## Gli esiti

(sotto, per famiglia)
