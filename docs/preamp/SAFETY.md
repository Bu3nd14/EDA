# SAFETY — Registro della sicurezza di rete (P2)

**Documento vivo.** Elenca ciò che nel progetto tocca la rete e ciò che resta da decidere o
verificare. **Non è l'analisi di sicurezza** richiesta da P2: ne è l'indice. La sua assenza a
G3 resta un **BLOCK automatico** (ADR-010, `AGENTS.md`).

Aperto in L41a (2026-09-26) con ADR-048. Ogni lotto che tocca la sezione rete lo aggiorna.

## Architettura (ADR-048)

- **Retro**: un modulo presa IEC con fusibile e **interruttore bipolare** (fase e neutro).
  Spento = rete staccata da tutto il telaio.
- **Sempre sotto tensione col retro acceso**: il primario del **piccolo trasformatore** (T2),
  dietro il proprio fusibile F501 sulla scheda d'alimentazione. Alimenta lo standby.
- **Il toroidale dei rail** (T1, 2×15 V 50 VA): acceso dal relè di rete **K501**, bipolare.
  Diseccitato = T1 staccato su fase e neutro.
- **Il pannello frontale non porta rete**: l'interruttore frontale è un ingresso a bassa
  tensione del temporizzatore.
- **Terra di protezione**: dal modulo IEC al telaio, direttamente, non attraverso la scheda
  d'alimentazione.

## Le parti che toccano la rete

| Ref / parte | Dove | Cosa serve decidere o verificare | Stato |
|---|---|---|---|
| Modulo IEC con fusibile e interruttore bipolare | retro | taglia del fusibile contro lo spunto di T1 (50 VA) più T2; marchio, tensione e corrente nominali dell'interruttore | aperto (giro componenti) |
| Terra di protezione | modulo IEC → telaio | punto di fissaggio dedicato, conduttore, sezione; continuità misurata sul prototipo | aperto |
| J510 `AC_IN` | scheda d'alimentazione | morsetto a vite per la rete, distanze verso il resto della scheda | aperto (layout, G2) |
| F501 | scheda d'alimentazione | valore dal datasheet di T2 (lento), portafusibile chiuso | aperto |
| T2 (piccolo toroidale, 12 V AC preferito) | telaio o scheda | isolamento primario/secondario (doppio o rinforzato), protezione termica o contro il corto; perdite a vuoto per lo standby | aperto |
| K501 G2RL-2A 12 VDC | scheda d'alimentazione | isolamento bobina/contatti adeguato alla rete (datasheet); contatti contro lo spunto di T1; bobina sensibile preferita (ADR-048, P5) | aperto |
| T1 (toroidale 2×15 V 50 VA) | telaio | isolamento primario/secondario; fissaggio senza spira in corto attraverso il bullone centrale | aperto |
| J511, J512 | scheda d'alimentazione | morsetti dei primari; distanze | aperto (layout) |
| Cablaggio di rete interno | telaio | percorso lontano dagli ingressi audio (ADR-010, ronzio), guaine, fissaggi | aperto (G2) |

## Distanze e norma di riferimento

- **La norma** da applicare per un apparecchio audio domestico va identificata e scritta qui,
  prima di G2 (probabilmente la famiglia EN/IEC 62368-1): **non ancora fatto**. Non si
  scrivono cifre di distanza a memoria.
- Distanze in aria e superficiali fra la sezione rete e la bassa tensione, sulla scheda
  d'alimentazione: da ricavare dalla norma, e da verificare sul layout (G2).

## Il consumo in standby

- Col retro acceso e il frontale spento: le perdite a vuoto di T2, più la logica a riposo
  (MCP1703 ~2 µA, il micro in sonno, il sorvegliante, il riferimento LM4040 ~1,2 mA a 5 V).
- **Il limite europeo applicabile**: Regolamento (UE) 2023/826 («Standby Regulation», abroga
  1275/2008 e 107/2009), applicabile dal **9 maggio 2025**.
  - Dal 2025-05-09: **standby ≤ 0,5 W**; off mode ≤ 0,5 W; standby con visualizzazione di
    informazioni ≤ 0,8 W.
  - Dal 2027-05-09 (secondo scaglione): off mode ≤ 0,3 W; lo standby resta 0,5 W.
  - **Provenienza, dichiarata**: letti in L41a su due pagine ufficiali della Commissione
    (`energy-efficient-products.ec.europa.eu`, comunicato `energy.ec.europa.eu` del
    2025-05-08) e su fonti terze concordi (SGS, Nemko, UL). **Il testo del regolamento su
    EUR-Lex non è stato letto**: da questo ambiente risponde 202 a corpo vuoto. L'articolo e
    il punto dell'allegato, e le eventuali eccezioni, vanno confermati sulla fonte primaria
    prima di G3.
  - Il nostro standby è «standby» (il frontale lo riaccende), senza rete dati: il limite è
    **0,5 W**. Il bilancio: perdite a vuoto di T2, U503 in regolazione (0,58 mA di riposo,
    SBVS204G), MCP1703, i due comparatori (~55 µA per canale, SBOS589D), l'LM4040 (~1,2 mA
    dal partitore di R503). Va misurato sul prototipo; il pezzo di T2 va scelto anche su
    questo.
  - **Trovato in L41a, e oggi FUORI**: in standby l'apparecchio è in mute, K6 è rilasciato,
    `VTRIM` è viva e le quattro bobine bistabili del trim (K7–K10) sono pilotate di continuo
    (L16, ADR-027): 4 × 9,1 mA a 12 V ≈ **0,44 W**, più ~6 mA di LED a pannello. Da sole
    superano 0,5 W. **Rimedio per L41b**: in standby il temporizzatore toglie `VRELAY` alla
    scheda audio (interruttore sul lato alto verso J1 pin 4); il micro resta su V5. In standby
    i LED del pannello si spengono.

## Modi di guasto noti

- **Spegnere dal retro mentre suona** = perdita di rete, cioè il caso guasto di P9 (b): nel banco
  di L30 al peggio ~58 dB SPL di picco a 1 m, contro un tetto di non-danno di ~112 dB.
- **Contatto di K501 saldato**: T1 resta acceso anche da spento dal frontale; il temporizzatore
  ha già messo il mute. Si spegne dal retro. Da gestire nel manuale d'uso.
- **Guasto di un regolatore o di un rail con la rete presente**: mute netto dal sorvegliante,
  poi il temporizzatore stacca K501 e resta spento finché non si gira il frontale (ADR-048).
