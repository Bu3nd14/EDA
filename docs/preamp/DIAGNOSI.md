# DIAGNOSI — che cosa guardare, e quando

Documento d'uso e di riparazione del preamplificatore. Nasce da **L58b** (ADR-110): dice come si vedono i
guasti che il circuito non segnala da sé. Le cifre vengono da `data/2026-11-01/L58b/`; la FMEA è
`data/2026-11-01/L58b/fmea_l58b.csv`. I livelli al jack sono in dB SPL a 1 m, come nel resto del
progetto: 0,87 V ≈ 112 dB, il tetto di non-danno; 100 µV ≈ 33 dB, una stanza silenziosa.

Il preamplificatore non ha un microcontrollore (ADR-102) né un LED di diagnosi. La diagnosi è fatta di
**segni che ci sono già** e di **due controlli col tester**.

## 1. I segni che si vedono o si sentono senza strumenti

| Segno | Che cosa vuol dire | Che fare |
|---|---|---|
| **A frontale spento un LED del frontale resta acceso** (mute, guadagno o trim) | La linea dei relè resta alla scheda audio in standby: Q505 o Q506 in corto, R540 o R536 aperte, R537 in corto, U508 B guasto. In tre casi (R536, R537, U508) resta acceso anche il toroidale | Si ripara quando si vuole: non dà colpi al jack. Si legge VRELAY al test point TP504 a frontale spento (deve essere ~0 V; TP505 è VRELAY_REG, acceso anche in standby) |
| **Il mute non zittisce un'uscita** (con la musica, inserendo il mute, un'uscita continua a suonare) | Il contatto di lavoro del relè di mute di quell'uscita è saldato (K4 principale, K2 fissa 1, K3 la Stax) | **Prima di spegnere**: il volume a zero e l'apparecchio a valle spento o scollegato. Allo spegnimento quell'uscita prende ~102 dB SPL, fino a ~125 dB SPL se manca anche la rete. Poi si cambia il relè |
| **A ogni accensione un colpo forte su un'uscita** | Lo stesso guasto: quell'uscita è collegata mentre salgono i rail. ~90 dB SPL sulla principale, ~110 dB SPL su una fissa | Come sopra |
| **All'accensione la musica arriva subito** (meno di ~0,1 s invece di ~1,2 s) | Il toroidale resta acceso in standby: Q503 in corto o i contatti di K501 saldati (il consumo in standby è quello in musica) | Si ripara: non dà colpi |
| **Col +10 dB il livello non sale** | La gamba del +10 dB del blocco B (C137, R136, R143 per canale) | Si ripara: non dà colpi |
| **L'apparecchio non suona mai** (mute sempre inserito) | Fra gli altri guasti, Q509 in corto gate-drain o aperto, o Q501 aperto | Si ripara |

**Il controllo del mute, ogni tanto.** Con la musica, inserire il mute ascoltando **ogni** uscita
(principale, Singxer, Stax): ognuna deve tacere. È il solo modo di vedere un relè di mute saldato su
un'uscita che di solito non si ascolta.

## 2. I blocchi di guadagno, col tester

Quindici dei ventotto guasti silenziosi del blocco (ADR-071) cambiano la **corrente di riposo dei
finali**; sei cambiano la **continua all'uscita**. Si vedono col tester, confrontando con i valori
dello stesso apparecchio da nuovo: così la tolleranza delle parti non conta.

**Come si misura.** Apparecchio acceso, in mute, senza segnale, da almeno 30 minuti con il coperchio
chiuso (i finali alla loro temperatura). Il tester in continua.

- **Continua all'uscita**: fra il test point d'uscita del blocco e la massa vicina.
- **Riposo dei finali**: la tensione ai capi di **ciascuna** delle due resistenze da 22 Ω d'emettitore
  (0,44 V ≈ 20 mA).

| Blocco | Test point d'uscita | Le due 22 Ω |
|---|---|---|
| A sinistro (principale) | TP101 | R134, R135 |
| A destro | TP301 | R334, R335 |
| B sinistro | TP201 | R233, R234 |
| B destro | TP401 | R433, R434 |
| F1 sinistro (Singxer) | TP501 | R533, R534 |
| F1 destro | TP701 | R733, R734 |
| F2 sinistro (Stax) | TP601 | R633, R634 |
| F2 destro | TP801 | R833, R834 |

(Le sigle sono quelle della scheda audio di oggi, lette da `circuits/preamp/preamp_audio.net` con
`data/2026-11-01/L58b/script/sigle_diagnosi.py`. Da rileggere se la scheda si rigenera.)

**Da nuovo**, una volta: annotare per ogni blocco la continua e le due tensioni.

**Poi**, ogni tanto o quando il suono sembra cambiato, rimisurare. È un guasto se:

- **la continua si è spostata di più di 10 mV** dal valore annotato. I guasti la spostano di 15–226 mV;
  il calore, fra 27 e 57 °C d'aria, di ~0,6 mV (`data/2026-10-23/L45d2b3b2b2/riposo.csv`);
- **una delle due tensioni è fuori da 0,33–0,66 V** (15–30 mA), o le due differiscono di più di 0,1 V.
  I guasti danno 0 mA, 9,5 mA, o 0 / 39 mA sbilanciati; il calore porta il riposo da 21,1 a 22,5 mA.

Le soglie sono calcolate sul banco: la dispersione della continua fra esemplari non è mai stata misurata
(NC-028), e da qui il confronto col valore annotato. Sul prototipo si conferma la stabilità dei valori
nel tempo.

**Quello che il tester non vede** (accettato, ADR-110): R123 in corto, R144 in corto, R147 aperta.
Il blocco lavora e lo scostamento è sotto i 3 mV: si perde un po' di rifiuto del rail o di distorsione
ad alta frequenza, senza colpi.

**Un guasto che non è silenzioso**: Q132 in corto base-emettitore porta l'uscita del blocco al rail.
Il blocco non suona più; il calore del VAS in quel guasto è di L66 (NC-076).

## 3. Al banco, a scheda spenta

- **R585** (la tenuta di AT_F, ADR-103): con R585 in corto la ritenuta dopo un guasto è cieca (ADR-109,
  accettato). In funzionamento non si vede: AT_F sta a ~0 V. A scheda spenta e scollegata, l'ohmmetro
  ai capi di R585 non deve leggere un corto. **La lettura in circuito va annotata sul prototipo.**
- **La coppia del mute** (Q501 in serie a Q509, ADR-110): il corto di uno solo dei due non ha effetti
  e non si vede. Per il colpo al jack servono due guasti.

## Che cosa non è qui

- I guasti che il circuito vede e mette in sicuro da sé: il sorvegliante dei rail, Δ, la ritenuta
  (P9 (b), PR-23).
- I guasti della FMEA a priorità bassa senza segno: le righe dei BAS416 di L58a2 (D534, D536, D541).
