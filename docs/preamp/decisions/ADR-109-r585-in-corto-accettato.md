# ADR-109 — R585 in corto rende cieca la ritenuta: il caso è accettato, dichiarato

Data: 2026-11-01 · Stato: accettata

**Rapporti con le decisioni precedenti.**

- **Scatta il secondo «Da riaprire se» di ADR-102** («Le righe della FMEA delle parti nuove (L58)
  trovano un guasto singolo del temporizzatore che toglie il mute o la ritenuta e che il firmware avrebbe
  coperto»). L'utente non riapre la scelta dei comparatori: **ADR-102 resta**, e il caso entra in P9
  come **(e)**, accettato, accanto a (c) e (d) (ADR-073).
- **ADR-103 resta com'è**: R585 33 kΩ, una resistenza sola. Il rimedio misurato qui (4 × 10 kΩ in serie)
  non è scelto.
- Apre **NC-077**, **minore** (scelta dell'utente).

## Contesto

L58a2 (`data/2026-10-29/L58a/`, report `reports/2026-10-29-L58a-test-point-fmea-distinta.md`): le righe
della FMEA di R585 e dei BAS416, ogni modo latente contro i sette eventi del temporizzatore. Con **R585
in corto** AT_F sta a massa e la ritenuta non scatta più:

- nei sette eventi, senza un guasto di rail, nessuna differenza dalla base;
- col **rail − che cade in musica** (`guasto`) il mute si inserisce come oggi (il jack a 15,6 ms, dopo
  il guadagno e prima del rail: i verdetti del jack uguali), ma **K501 resta chiuso**: oggi si apre a
  129,1 ms e resta aperto fino al frontale. Lo stesso **all'accensione con un rail morto**
  (`accensione_u501`). Con **VRELAY_REG perso** (`guasto_u503`) K501 si apre a 50 ms comunque;
- **P9 (b)** non è rispettato: «dopo un guasto con la rete presente il temporizzatore stacca il
  toroidale». Il firmware, che leggeva i rail, lo copriva.

Riga della FMEA: gravità 4, probabilità 1 (R 0,5 FIT · 0,05 = **0,025 FIT**), rilevabilità 3
(latente), priorità **alta** per la matrice di ADR-070.

**I rimedi provati** (`an_r585_serie.csv`, `an_r585_66k.csv`, `an_r585_serie2.csv`, `an_r585_t0.csv`,
`an_r585_rete.csv`): spezzare R585 in serie fa restare, dopo il corto di un pezzo, una resistenza più
bassa; la ritenuta scatta solo se resta ≥ ~30 kΩ, e il nominale non può salire oltre ~40 kΩ.

| R585 | nominale: accensione a freddo, 60 °C, comparatore 2,2 V (base di Q513 ≤ 0,45 V) | un pezzo in corto: guasto del rail −, K501 |
|---|---|---|
| 33 kΩ (oggi) | 0,300 V | in corto: chiuso |
| 2 × 16,5 kΩ | — | 16,5 kΩ: chiuso |
| 3 × 11 kΩ | — | 22 kΩ: chiuso |
| 3 × 12 kΩ | 0,316 V | 24 kΩ: aperto a 133,3 ms a 25 °C, **chiuso a 0 °C** |
| 2 × 33 kΩ | **1,06 V: la ritenuta scatta a vuoto** | 33 kΩ: aperto |
| **4 × 10 kΩ** | **0,336 V** (rete −10 / +10 %: 0,336 / 0,336) | 30 kΩ: aperto a 129,4 ms (rete ±10 %), 126,8 ms a 0 °C |

## Decisione

L'utente, 2026-11-01, sulla domanda coi numeri qui sopra: **«Accettarlo, dichiarato»**, e la non
conformità **«Minore»**.

1. Il circuito non cambia: R585 resta una resistenza da 33 kΩ.
2. **P9 (e), caso accettato**: con R585 in corto (un guasto latente) e poi un rail che cade con la rete
   presente, il mute si inserisce come oggi e il jack resta muto, ma il toroidale resta acceso finché
   non si spegne il frontale.
3. **NC-077**, minore: si registra; si chiude alla scelta delle parti o al layout (G2), con questa
   decisione come rimedio.

## Perché

- Servono due guasti: R585 in corto (0,025 FIT) e poi un guasto di rail con la rete presente. Il jack
  resta protetto dal sorvegliante, che non passa da R585: il colpo al jack è quello di oggi.
- L'apparecchio guasto non suona: chi ascolta lo spegne dal frontale. Il frontale spento fa cadere
  K501 per la sua via (1 MΩ · 100 nF caricato dal frontale e da `VR_G`, ADR-102), che non passa da
  AT_F; lo spegnimento dal frontale con R585 in corto e i rail sani è uguale alla base
  (`f_r585_corto_spls`). **Non misurato**: lo spegnimento dal frontale col rail già caduto.
- Il rimedio che regge (4 × 10 kΩ) costa tre resistenze e un margine: la base all'accensione a freddo
  sale da 0,300 a 0,336 V contro 0,45.

## Alternative scartate

- **4 × 10 kΩ in serie**: misurato agli angoli (sopra), regge; non scelto dall'utente.
- **2 × 16,5 kΩ, 3 × 11 kΩ, 3 × 12 kΩ, 2 × 33 kΩ**: falliscono sul banco (sopra).
- **Riaprire ADR-102** (tornare al micro): non proposto; il caso richiede due guasti e il jack resta
  protetto.

## Da riaprire se

- Un guasto di rail con la rete presente, misurato col toroidale acceso a tempo indefinito, porta una
  parte oltre i suoi limiti termici (PR-22, P7): la gravità diventa 5 e si torna all'utente col rimedio
  di 4 × 10 kΩ.
- L'autodiagnosi di L58b può vedere la ritenuta cieca a ogni accensione: la riga diventa rilevabile.
- La scelta delle parti o il layout non giustificano più la severità minore.
