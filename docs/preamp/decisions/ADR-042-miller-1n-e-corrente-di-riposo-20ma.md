# ADR-042 — Miller da 470 pF a 1 nF, e la corrente di riposo d'uscita a ~20 mA, coi modelli del costruttore

Data: 2026-09-23 · Stato: accettata

## Contesto

Coi modelli del costruttore (L39), V1 è sceso sotto i 60° di **ADR-019** su ogni
istanza a guadagno unitario (NC-034). Il blocco B a 0 dB è a 55,55°, il blocco A a 57,93°,
il buffer delle fisse a 54,92°. La corrente di riposo d'uscita è salita da 14,6 a
20,3 mA a parità di moltiplicatore (NC-035). ADR-017 prevedeva questo caso: il Miller
«va rideciso con una ADR sua». L'utente, il 2026-09-22, ha dato la direzione: margine
di fase prima della banda, cioè banda ridotta oppure guadagno minimo fino a +1,5 dB.

## Decisione

**C124, il Miller del VAS, passa da 470 pF a 1 nF, dielettrico C0G, in tutte le otto
istanze.** Il moltiplicatore di Vbe resta a **1,69 kΩ**, e la corrente di riposo
d'uscita di progetto diventa quella che dà coi modelli del costruttore: **~20,3 mA**.
C_f (C137, 330 pF, ADR-025), la rete di controreazione ed E1 non cambiano. Decisione
dell'utente del 2026-09-23, sui numeri di L40.

## Perché

**La causa della caduta è una sola.** È stata separata in
`data/2026-09-23/L40/cause/` e `mje/`, rimettendo una cosa alla volta al segnaposto,
sulla cella peggiore del blocco B a 0 dB. Rimettere tutto al segnaposto ridà 61,80°,
cioè esattamente L39/prima.

| Cambiato rispetto al costruttore | V1 |
|---|---|
| niente | 55,55° |
| CJE/CJC dei MJE al segnaposto (300 p invece di 3,06 nF) | **62,49°** |
| TF dei MJE / VAF dei MJE | 55,06° / 55,42° |
| MMBT5551/5401 al segnaposto | 55,64° |
| JFET / diodo al segnaposto | 54,47° / 55,92° |
| I_q a 14,6 mA (R128 1,33 k) | 54,27° |

È la capacità di giunzione dei MJE, cioè la f_T sotto il minimo di NC-025. Un polo non
dominante più basso si compensa abbassando il crossover, ed è quello che fa il Miller.

**Il margine**, deck versionati rigenerati (regressione in `data/2026-09-23/L40/dopo/`,
esplorazione in `strada_a/`):

| Istanza, criterio ADR-024 | 470 pF | **1 nF** |
|---|---|---|
| blocco B 0 dB | 55,55° | **62,08°** |
| blocco B +3 / +10 dB | 63,90 / 100,19° | 76,20 / 96,66° |
| blocco A, cablaggio ≤ 1 nF | 57,93° | 67,69° |
| buffer delle fisse, al jack | 54,92° | 63,21° |
| crossover del blocco B a 0 dB, a vuoto | 889 kHz | 430 kHz |

**Il prezzo, dichiarato e accettato.** È lo stesso per cui ADR-025 aveva scartato 1 nF
sui segnaposto:
- **slew rate** a gradino in discesa da −3,40 a **−1,68 V/µs**. Una sinusoide a
  20 kHz e 12 V di picco (+10 dB, fondo scala, pendenza ideale 1,51 V/µs) comincia a
  entrare in slew: 0,57 V di continua a valle, contro 0,06 V. A metà ampiezza
  (6 V di picco) resta a 0,04 V;
- **PSRR del rail +** a 10 kHz da 39,5 a **33,0 dB** a 0 dB, da 29,5 a **23,0 dB** a
  +10 dB. La quota di ADR-020 resta: si ricalcolano i limiti per tono della «Nota su E5»;
- **banda** a 0 dB da 2,45 MHz (con 0,52 dB di picco) a **912 kHz** (0,11 dB). A
  +10 dB da 182 a **113 kHz**, e −0,134 dB a 20 kHz rispetto a 1 kHz. Nessun requisito
  fissa una banda, e l'utente non la voleva;
- V3 recupera in 3,03 µs invece di 1,07. Zout a 20 kHz, al nodo, 0,57 invece di 0,27 Ω.

**Cosa non cambia**: E2 (+3,039 / +9,963 dB), E5, il punto di lavoro, il clip
(+13,23 / −13,79 V) e la continua al jack di V3.

**La corrente.** L'utente tiene i ~20,3 mA invece di tornare a 14,6 con R128 1,33 kΩ.
- **A favore**: nessun valore da cambiare; +0,5° di V1 (62,08 contro 61,57°); più
  classe A di riserva.
- **Contro**: 0,993 W a riposo per blocco invece di 0,822, cioè **~1,4 W in più** sugli
  otto blocchi, che pesano su NC-029 e sul budget dell'alimentatore. Le correnti di
  rail diventano 32,6 / 33,6 mA per blocco.
- **P7 regge** (MJE peggiore 0,362 W contro 1,04 W, L39).

R128 resta un valore select-on-test al banco: fissa la corrente attraverso la Vbe, e
nessun modello porta la dispersione.

## Alternative scartate

- **Guadagno minimo +1,5 dB**: una gamba fissa R_G0 7,87 kΩ da FB a massa su blocco A,
  blocco B e buffer, e R_G3 a 6,49 kΩ perché +3 e +10 dB restino dove sono.
  - **Da solo non basta**: 59,95° sul blocco B, 59,11° sul buffer. Sopra lo zero di C_f
    (321 kHz) il guadagno di rumore torna verso 1, e il guadagno in più compra solo ~4,4°.
  - **Con C_f 220 pF e Miller 560 pF** arriva a 63,11°, con slew −2,89 V/µs e PSRR+
    36,5 dB. Ma cambia **E1** (ADR-001) a +1,5 dB, porta le uscite fisse a +3 dB, è
    una modifica di topologia su tre istanze, supera ADR-025 e obbliga a rimisurare V2.
- **Miller 820 pF**: 60,70° a 20 mA, 60,02° a 14,6 mA. Nessun margine.
- **Miller 1,2 nF**: 63,24°, ma slew −1,41 V/µs e 0,82 V di continua a 20 kHz a fondo
  scala.
- **Corrente a 14,6 mA (R128 1,33 kΩ)**: −0,17 W per blocco, V1 61,57°. L'utente ha
  preferito non cambiare il valore.
- **C_f più grande** a 0 dB: non aiuta, con R_g aperta la controreazione è già totale
  (L39, 1 nF: 54,83°).

## Da riaprire se

- **La f_T dei MJE misurata sul prototipo**, o un modello del costruttore corretto
  (NC-025), dà una CJE molto più bassa di 3,06 nF. Il polo che questa ADR compensa si
  sposta, e 1 nF diventa compensazione in più pagata in slew e PSRR per niente. Il valore
  si rispazza con `strada_a/`.
- **Lo slew a 20 kHz si sente o si misura**: THD+N a 20 kHz a fondo scala, sul
  prototipo, sopra quella a 6 V di picco in modo sproporzionato. Allora si torna alla
  strada del guadagno minimo con C_f e un Miller più piccolo.
- **L'alimentatore non sta nella quota di ADR-020** col PSRR+ ridotto a 10–20 kHz.
- **La stima termica del telaio** (NC-029, L30) non regge con ~20 mA: la strada pronta
  è R128 1,33 kΩ (14,6 mA, 0,5° di V1 in meno).
