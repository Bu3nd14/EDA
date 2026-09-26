# L30 — lo spegnimento, il failsafe dell'alimentatore e il calore del telaio (2026-09-26)

**Mandato**: NC-028 per lo spegnimento (bloccante) e NC-029 (maggiore), da ADR-043, dalla nota
di ADR-045 e dal contratto di J4 di L35. Decisioni: **ADR-046** (spegnimento e failsafe),
**ADR-047** (P5). Dati: `data/2026-09-26/L30/` (README).

I transitori sono detti in **dB SPL di picco a 1 m** con la formula di NC-028 (100 µV ≈ 33,45 dB,
poi 20 log10 del rapporto; finale ×21,1, Heresy 96 dB/1W/1m). È un limite superiore, calcolato,
e va confrontato con la soglia V2 (~33 dB) e con il fondo di una stanza silenziosa (~25–35 dB(A):
un picco contro un livello pesato A).

## 1. Le decisioni dell'utente

ADR-043 lasciava all'utente due domande. Si sono fatte conversando, con le cifre davanti.
1. **La soglia in caso di guasto**: «una soglia di non-danno basta».
2. **Il tetto proposto e la forma del failsafe**: «le soglie vanno bene come tetto, non come
   target, dobbiamo stare più bassi, il resto OK». Il tetto è 0,87 V di picco al jack
   principale (~112 dB): l'ingresso che porta il MV50 (612 mV) alla piena potenza. La forma:
   - un sorvegliante sui rail;
   - una tenuta dei rail;
   - una tenuta di `VRELAY` per l'ordine di ADR-045;
   - il corto istantaneo accettato con l'argomento dei 30 W del finale contro i 100–105 W delle
     Heresy.
3. **Lo spegnimento normale**: «sì, interruttore morbido va bene».

**Una rettifica fatta durante la conversazione.** Le prime cifre portate all'utente (~74 dB col
relè chiuso) erano di L29c, cioè della geometria in derivazione. Da ADR-044 il relè al jack è un
deviatore in serie. Si è corretto prima della decisione, coi numeri diagnostici di L29d2 (§ 4.3
di quel report).

**Perché lo spegnimento morbido.** Il mute completo dura ~6,6 s: la dissolvenza da 6 s di
ADR-039/040, più 0,5 s per i relè. Tenerlo coi rail dopo la perdita di rete chiede ~0,35 F per
rail (265 mA × 6,6 s / 5 V). Con l'interruttore che è solo un ingresso del temporizzatore, la
rete resta finché il mute è completo.

## 2. Il banco

Il generatore di V2 è esteso con `--matrice l30`:
- lavora sul sorgente (geometria iii e bleed dalla netlist, col controllo del 2e);
- K1/K5 usano il gemello comportamentale.

**Il deck versionato si rigenera byte-identico.** Delle 29 corse, 27 sono finite. Le 2 non finite
sono controfattuali: «Timestep too small» nel JFET, come le 7 corse di L29d2.

**Due errori miei, trovati e corretti prima di dare un numero:**
- **Il primo giro è girato senza i contatti del jack.** Il generatore li aggiungeva solo per
  `l29d2` e `sorgente`. Ogni `alter` sui contatti diceva «no such device», ngspice usciva 0 e
  `corri.sh` segnava rc=0. Una lettura sbadata avrebbe preso quei numeri.
  - **Guardia per i lotti futuri**: `grep -l 'no such device' corse/*.log` vuoto. Qui lo è.
- **Il rail negativo aveva una PWL col tempo all'indietro** (`t0 + v/s` con v < 0). Corretto con
  `abs(v)`.

## 3. Lo spegnimento morbido: V2 regge

Il mute è completo da prima: jack isolati, lato del condensatore a massa, LDR a d = 1. Poi la rete
si stacca e i rail scendono come in L29c.

| Rampa | Rail | Guadagno a 0 dB | Peggiore | dB SPL |
|---|---|---|---|---|
| 10 ms | simmetrici / + in ritardo / − in ritardo | inizio o metà discesa | 0,20–2,7 µV | −20 … +2 |
| 300 ms | idem | idem | 0,07–1,04 µV | −29 … −6 |

**12 su 12 sotto 100 µV, il peggiore 31 dB sotto V2.** Nessun ordine fra `VRELAY` e rail conta:
il guadagno all'inizio e a metà discesa danno lo stesso ordine di grandezza.

## 4. Il guasto: sotto l'obiettivo, e 54 dB sotto il tetto

Un rail (+ o −) o entrambi scendono linearmente con la pendenza di 265 mA sulla tenuta. Il
sorvegliante scatta a 13,5 V, e il contatto in serie si apre 3 ms dopo, al rilascio massimo del
G6K.

| Tenuta per rail | Da 13,5 a 10,6 V | Peggiore (s / + / −) | dB SPL |
|---|---|---|---|
| 470 µF | 5,1 ms | 1,36 / 1,77 / 1,62 mV | 56 / 58 / 58 |
| 1000 µF | 10,9 ms | 0,64 / 1,28 / 1,18 mV | 50 / 56 / 55 |
| 2200 µF | 24 ms | 0,51 / 1,04 / 1,42 mV | 48 / 54 / 57 |

- **Tutte sotto l'obiettivo di 2 mV.** Il peggiore, 1,77 mV (~58 dB), sta 54 dB sotto il tetto.
- **G** (`VRELAY` persa, guadagno a 0 dB 10 ms dopo il comando): **identiche a F**. Anche con
  470 µF, dove il guadagno cambia col rail già a ~7,9 V: il jack è isolato da 7 ms.
- **Il controfattuale senza Δ** (guadagno col comando, jack ancora collegato): **69 mV,
  ~90 dB**. È la cifra di ADR-045, e dice che la tenuta di `VRELAY` serve anche nel guasto.
- **Da dove viene il residuo di 0,5–1,8 mV.** Da due istanti, e mai dalla perdita della
  regolazione:
  - all'inizio della discesa, col jack collegato: il rail passa da 15 a 13,5 V e l'uscita
    risente del PSRR. È il picco delle corse simmetriche con 470 e 1000 µF;
  - all'apertura del contatto, a +3 ms: tutte le altre.
- **Perché ≥ 1500 µF effettivi e non 470.** 470 µF passano, ma lasciano ~1 ms fra il contatto
  (+4 ms col trasferimento) e i 10,6 V, senza la tolleranza del condensatore né il ritardo del
  sorvegliante. Con 1500 µF effettivi (2200 nominali, −20 %) restano ~11 ms.

**I 4 mV «non spiegati» di L29d2 sono spiegati.** Il picco cadeva a +427 µs dall'apertura, dentro
la finestra in cui il banco richiude il contatto per il rimbalzo (+400…+600 µs), mentre i rail
avevano già cominciato a scendere. È l'ordine dei tempi, non un percorso nascosto. Con
l'ordine di ADR-046 non si ripresenta.

## 5. La soglia di perdita della regolazione, rimisurata

Dalle corse di guasto lente (`soglia_regolazione.csv`, MAIN_A contro il suo valore a regime):

| Scostamento | Entrambi i rail | Solo il + | Solo il − |
|---|---|---|---|
| 10 mV | 10,3–10,6 V | 10,5 V | −7,5 V |
| 100 mV | 10,2–10,4 V | 10,2 V | −1,3 V |

Il vincolo è sul **rail +, ~10,6 V** (L29c: 9,5–10,4 V sul circuito di allora).

## 6. Il calore: P5 al numero vero

La stima è `termica/stima_telaio.py` (CALCOLATA; ipotesi nel file). Totale **15,4 W nominali,
17,8 W nel caso peggiore**: scheda audio 7,94, regolatori 2,65–3,71, trasformatore 2,5–3,5,
bobine e LED 0,88, il resto ~1,5.
- **Due salti in serie**: il telaio sigillato +7–10 °C, poi il vano chiuso della libreria.
- **Nel telaio**: 51–55 °C col vano stretto (3 cm), 47–50 °C con 10 cm, 42–45 °C all'aria.
- **I 60 °C di ADR-021 reggono**: si superano solo con un vano che tocca il telaio.
- **ADR-047**: P5 aggiornato, P7 invariato.
- **La condizione**: nessun'altra sorgente di calore nello stesso vano. Il MV50 a valvole, per
  esempio, deve stare fuori.
- **La conferma** resta la misura nel prototipo.

## 7. Cosa cambia nel repo

- **`circuits/preamp/preamp_audio.py`: solo commenti.**
  - Il contratto di ADR-046 accanto a J4, al posto della nota per il failsafe.
  - La tenuta dei rail accanto a J1.
  - La netlist non cambia: rigenerata, differisce solo per etichette, data e percorso, e per due
    nomi di net fuse. Il deck V2 generato da quella netlist è **byte-identico**.
  - La netlist non si ricommitta.
- **`REQUIREMENTS.md`**: P5 (ADR-047), P9 nuovo (ADR-046), V2 precisato allo spegnimento.
- **ADR-046, ADR-047**; indice delle ADR.

**Trappola nuova: SKiDL non dà nomi stabili alle net fuse.** A sorgente invariato, due
esecuzioni consecutive hanno dato `BL_IN` / `L_MAINOUT` la prima e `L_ATT_W` / `L_MAINJACK` la
seconda. Le connessioni sono le stesse. Un diff di netlist dopo una rigenerazione va quindi letto
sulle connessioni, non sui nomi.

## 8. Cosa resta

- **Il circuito dell'alimentatore** non esiste ancora in `circuits/`. Deve realizzare P9: il
  relè di rete e l'interruttore morbido, il sorvegliante, la tenuta dei rail e di `VRELAY`, il
  temporizzatore. Poi si verifica col banco di L30, sostituendo le rampe comportamentali con il
  circuito, col metodo di V2.
- **I due controfattuali non corsi** (relè tardivo, corto istantaneo). L'evidenza della loro
  forma resta in L29d2: fino a 2,3 V (~121 dB) col relè in ritardo di 100 ms.
- **NC-028 e NC-029**: vedi `NONCOMPLIANCE.md`.
