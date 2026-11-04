# 2026-11-04 — L71, il frontale mosso durante una sequenza (NC-083)

**Documento datato: non si riscrive.** I dati sono in `data/2026-11-04/L71/` (README lì).

## Che cosa chiedeva il lotto

NC-083 (maggiore, prima di G1, trovata dall'architetto in L65): fra le sequenze del temporizzatore non ce
n'era nessuna col frontale spento **prima che arrivi la musica** (a 1209 ms dall'accensione), col frontale
**riacceso durante lo spegnimento** (i ~120 ms prima che K501 si apra), né con **il tasto del mute (SW3)
mosso dentro Δ** (fra MUTE_CMD e PERMIT_CMD). Per chiuderla: le tre sequenze sul banco del temporizzatore di
oggi, a rete ±10 %, coi colpi al jack in dB SPL e il calore delle parti contro i loro limiti.

## Come si è misurato

Il banco del temporizzatore di L69b **copiato** (non rieseguito sul posto), sul circuito di oggi
(`circuits/preamp/psu.net`, invariato da L69). Il generatore copiato dà, sui casi che c'erano, **i deck di
L69b riga per riga** (accensione a −10 %, spegnimento, inserimento, rilascio: 0 righe diverse a meno dei
percorsi, `script/prova_gen.sh`). Cinque famiglie nuove, sullo schema di `ritenuta_frontale` (il frontale e
SW3 come forme d'onda a più fronti):

| Famiglia | Che cosa | Istanti (ms dal primo fronte) |
|---|---|---|
| `acc_spento_<ms>` | da standby, frontale acceso e rispento | 100 … 1300, fitti fra 1200 e 1205 (fino a 0,05 ms) |
| `spl_riacceso_<ms>` | dalla musica, frontale spento e riacceso | 5 … 400, fitti attorno all'apertura di K501 (122,5 ms) |
| `spl_sw3_<ms>` | dalla musica, frontale spento e poi SW3 a mute | 5, 15, 30, 45 |
| `ins_ritorno_<ms>` | dalla musica, SW3 a mute e di nuovo a musica | 5 … 60 (Δ è 40 ms) |
| `ril_ritorno_<ms>` | dal mute, SW3 a musica e di nuovo a mute | 3 … 30, fitti fra 11 e 12 |

**230 corse, tutte rc 0 con `ok.txt`**: 135 della prima lista alle tre reti, 12 di riferimento (accensione,
rilascio, inserimento, spegnimento: le cifre di L69b, 1209,3 / 18,1 / Δ 40,1 / K501 122,5 ms), 35 a istanti
fitti aggiunti dopo aver visto le prime, e **48 agli angoli peggiori di Δ delle tolleranze di ADR-105**
(i file `toll_c0g_t{0,25,60}_dperm_sp.json` di L54b3b, con le perdite dei diodi alla temperatura) a rete
−10 %. 16 corse a 0 °C col ripiego numerico del banco (`trap`, gmin 1e-8), come in L54b3b: per ADR-105 accorcia
i ritardi, cioè sta dal lato dei limiti.

**Al jack**: la catena V2 di L69b (il ponte e `--matrice l41c`) copiata, con un ponte nuovo
(`ponte/estrai_ponte_l71.py`) per tre ragioni. Il banco audio modella **una sola** apertura del jack e mai
una richiusura: la finestra si apre all'istante dello spegnimento del frontale e finisce prima che il jack o
il guadagno si richiudano. I nove posti del deck si riempiono con corse nuove: il nome del posto è
un'etichetta, il deck è lo stesso. **La musica che torna** si misura a parte (il modo «rientro»): il jack
chiuso per tutta la finestra, aperta sulla chiusura del jack, contro un riferimento coi rail **fermi** al
valore di prima. Il criterio, scritto prima delle corse (`script/tabella_l71.py`): quello di V2 dello
spegnimento, ≤ 100 µV (33,45 dB SPL di picco a 1 m), per ogni posto. **11 gruppi, 198 corse audio, tutte
rc 0**, ognuna partita dal punto giusto (`verifica_partenza.py`).

**Lo stato e l'ordine dei relè** (`script/stato_finale.py`, scritto prima delle corse con lo stato atteso per
famiglia): la musica alla fine, K501, la ritenuta; a ogni chiusura del jack, se il permissivo era già su
(ADR-045, punto 3); a **ogni** distacco del jack dopo una chiusura, il margine fra il jack sicuramente aperto
(bobina sotto 1,2 V più 3 ms) e il guadagno libero al più presto (bobina di K6 sotto 9,6 V).

## Che cosa è uscito

**Al jack, tutto dentro** (`sintesi_l71.txt`):

| | Righe | Sopra 100 µV | Peggiore |
|---|---|---|---|
| Il jack che si stacca (le tre famiglie del frontale e le musiche brevissime) | 90 | 0 | 8,5 nV, **−47,9 dB SPL** (riacceso a 400 ms, −10 %) |
| La musica che torna dopo un riacceso | 9 | 0 | 8,8 µV, **12,3 dB SPL** (riacceso a 140 ms, −10 %) |

Il rientro peggiore ha una ragione: riacceso **dopo** che K501 si è aperto, K501 si richiude, e alla
richiusura V+ cala di 125–205 mV e V− di 275–525 mV per ~15 ms (il jack è ancora in mute); la musica torna
12–20 ms dopo, con V+ 3–4 mV sotto il regime (`script/calo.py`). Al jack sono 12,3 dB SPL, 21 dB sotto la
soglia. Riacceso prima che K501 si apra, la musica torna ~17 ms dopo il frontale, come in un rilascio.

**Gli stati finali sono tutti quelli attesi**, 230 su 230: frontale rispento all'accensione → spento, K501
aperto; riacceso → la musica torna e K501 è chiuso (riacceso a 200 / 400 ms, a K501 già aperto: la musica
0,66–0,73 s dopo il riacceso; a +10 % il riacceso a 200 ms la riporta già dopo 17 ms, come un rilascio; la causa
non l'ho cercata, il rientro è fra i nove misurati al jack); SW3 rimesso → di nuovo nello stato di
partenza. **La ritenuta non scatta mai.** Il guadagno non è mai sbloccato col jack chiuso (C2 dentro su 230)
e il permissivo non sale mai dopo il jack (0 su 230): alla chiusura lo anticipa di 0,1–0,3 ms, come nelle
accensioni e nei rilasci normali. **Il calore**: niente resta acceso fuori dallo stato atteso, quindi nessuna
parte lavora fuori dal suo regime normale; non serviva un banco termico.

**Una cosa esce dal criterio del banco**: il ritardo del permissivo dopo il mute (Δ, la colonna C3,
≥ 16,9 ms). Se la musica arriva e se ne va subito, **Δ si accorcia**:

| Musica (ms) | Δ, valori nominali, −10 % | Δ, angolo peggiore (0 °C) | Margine fisico, nominali / angolo |
|---|---|---|---|
| piena | 39,6–40,1 | 31,4 (ADR-105) | — |
| 22 | 34,9 | — | — |
| 4,1 | 17,5 | — | 14,5 / — |
| 3,2–3,3 (la più breve che chiude il jack) | 11,3–13,0 | **10,0** | **9,3 / 6,9** |

Succede in una finestra di meno di 1 ms: il frontale spento 6,3–7,0 ms prima che la musica arrivi, o SW3
rimesso a mute 6,3–7,0 ms prima che la musica del rilascio arrivi. C3 è fuori in 11 corse a valori nominali e in 25 agli angoli. Il
meccanismo (`script/delta_nodi.py`): Δ è AT_PRT (C550) che scende fino a VREF, più PERMIT_T (C528) che scende
fino alla soglia. Col frontale spento mentre AT_MRQ incrocia VREF, AT_PRT arriva a 2,53 V invece di 4,24 V:
la prima attesa vale quasi zero, e PERMIT_T, caricato da un impulso breve, scende prima.

Il vincolo che quei 16,9 ms proteggevano — il guadagno libero solo a jack sicuramente staccato, ADR-045 —
**regge sempre, con almeno 6,9 ms**: la cifra di 16,9 ms era il Δ del vecchio temporizzatore al suo angolo
minimo (ADR-049). Con impulsi più brevi di 3,2 ms il jack non arriva a chiudersi (bobina sotto 9,6 V) e non
c'è niente da proteggere. Le stesse sequenze nella catena V2: −55,2 dB SPL al più.

**Un comportamento da dichiarare**: il frontale e SW3 impiegano ~7 ms a diventare mute. Se la musica era già
in arrivo, passa lo stesso per 3–6 ms e poi si taglia; senza segnale il colpo al jack è −55 dB SPL. È musica
che stava arrivando, non un colpo di commutazione.

## Le scelte dell'utente

- **Il ritardo del permissivo**, fra tre opzioni (la regola fisica e chiudere; un rimedio nel circuito; una
  non conformità minore): «direi 1. ma spiegami cosa intendi con guadagno libero». Dopo la spiegazione (le
  manopole del guadagno e del trim arrivano ai relè solo quando il permissivo si rilascia; il gradino di
  ~6–114 mV del cambio deve trovare il jack già staccato), **«Sì, regola fisica»**: **ADR-120**.
- **La musica di 3–6 ms dopo il comando contrario**: **«Va bene, dichiararlo»**.

## Che cosa cambia

- **ADR-120**: il criterio del ritardo del permissivo è la regola fisica di ADR-045, letta a ogni distacco del
  jack, margine ≥ 0; i 16,9 ms restano come cifra delle sequenze a musica piena. Il circuito, P9, il PRB e la
  FMEA non cambiano.
- **NC-083 chiusa** con questo report.
- Per i banchi futuri del temporizzatore: `stato_finale.py` di L71 (colonne `r41_min_ms`, `perm_dopo`,
  `mus_min_ms`) è la lettura che applica ADR-120; C3 di `analizza_mc.py` resta come cifra.
