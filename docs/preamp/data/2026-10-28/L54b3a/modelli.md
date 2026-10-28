# L54b3a - modelli del costruttore: BC847A/B/C, BC857A/B/C, BAT54

Data: 2026-10-28. Costruttore: **Diodes Incorporated**, non Nexperia (vedi sotto). Esito di
`validate_models.py`: **83/83** (erano 69; +7 provenienza +7 elettrici); `--check-provenance`: **39/39**.

## Perche non Nexperia
`assets.nexperia.com/documents/spice-model/BC847.txt` e `BC847B.txt`, `assets.nexperia.cn/.../BAT54.txt`:
HTTP 403 Access Denied (Akamai) a curl; `www.nexperia.com/product/BC847B` e `www.nexperia.cn/product/BAT54`: 403 al
WebFetch. Non ho aggirato il filtro (stesso esito di `vendor/diodes/nexperia/BAV199/PROVENANCE.json`). I modelli
Nexperia esistono (le pagine prodotto elencano «BC847 SPICE model» 2024-04-05 e «BAT54 SPICE model» 2020-08-25, da
frammenti di ricerca, non visti da me) ma restano da scaricare a mano da un browser. onsemi: `.../models/lib/bc847b.lib`
ridà una pagina web da 304 kB (soft-404), niente tenuto. Diodes pubblica modello e datasheet di tutti e sette i tipi:
URL `https://www.diodes.com/spice/download/<id>/<NOME>.spice.txt` (curl, 200 text/plain). **L'id decide il file, il
nome nell'URL non viene controllato** (id 2541 col nome BC847B ridà l'MMBT5551): ogni id e confermato dal nome servito.

## File
| Parte | id | vendor/ (0444, .sha256, PROVENANCE.json) | models/ + .provenance.json | modello da usare |
|---|---|---|---|---|
| BC847A | 2845 | `vendor/bjt_npn/diodes_inc/BC847A/` | `models/bjt_npn/bc847a.lib` | `DI_BC847A` |
| BC847B | 2846 | `vendor/bjt_npn/diodes_inc/BC847B/` (+ datasheet DS11108) | `models/bjt_npn/bc847b.lib` | `DI_BC847B` |
| BC847C | 2847 | `vendor/bjt_npn/diodes_inc/BC847C/` | `models/bjt_npn/bc847c.lib` | `DI_BC847C` |
| BC857A | 2923 | `vendor/bjt_pnp/diodes_inc/BC857A/` | `models/bjt_pnp/bc857a.lib` | `DI_BC857A` |
| BC857B | 2926 | `vendor/bjt_pnp/diodes_inc/BC857B/` (+ datasheet DS11207) | `models/bjt_pnp/bc857b.lib` | `DI_BC857B` |
| BC857C | 2931 | `vendor/bjt_pnp/diodes_inc/BC857C/` | `models/bjt_pnp/bc857c.lib` | `DI_BC857C` |
| BAT54 | 510 | `vendor/diodes/diodes_inc/BAT54/` (+ datasheet DS11005) | `models/diodes/bat54.lib` | `BAT54` |

Il nome del modello ha il prefisso `DI_` (non `BC847B`). Istanza: `Qx C B E DI_BC847B`; `Dx anodo catodo BAT54`.
Datasheet: DS11108 Rev. 28-2 (maggio 2025, BC846A-BC848C, `datasheet/download/BC846B.pdf`), DS11207 Rev. 28-2
(maggio 2025, `assets/Datasheets/BC856A-BC858C.pdf`), DS11005 Rev. 34-2 (nov. 2023, `assets/Datasheets/BAT54_A_C_S.pdf`).
Il datasheet A/B/C e uno solo, tenuto nella cartella della B; PDF rinominati col numero di documento (dichiarato).

## Ritocchi (contati)
- **BC847A e BC847C: 1 ritocco.** Il file del costruttore ha una riga nuda `BJTs` (la coda del commento `*SRC=` senza
  `*`): ngspice 47 la legge come sorgente B ed esce con `mal formed B source instance: bjts`, exit 1, nessun deck parte.
  Nella copia in `models/` e `*BJTs`. L'originale in `vendor/` e intatto.
- BC847B, BC857A/B/C, BAT54: **0 ritocchi** (le righe non-commento sono identiche, verificato per script; CRLF del
  costruttore tenuti sotto un'intestazione nostra in LF). Nessun warning di ngspice su nessun parametro (provato con
  il dump dei dispositivi: ogni parametro del file compare col suo valore; XTI non e dato e vale 3 di default).

## Ricette contro datasheet (set temp = 25)
BC847B (DS11108 p. 4) / BC857B (DS11207 p. 4):

| Cifra | BC847B misurato | BC847B datasheet | BC857B misurato | BC857B datasheet |
|---|---|---|---|---|
| hFE, IC 2 mA, VCE 5 V | 239,4 | 200..450 (typ 290) | 308,2 | 220..475 (typ 290) |
| VBE(on), IC 2 mA, VCE 5 V | **708,4 mV: FUORI, +8,4 mV oltre il massimo** | 580..700 (typ 660) | 694,8 mV | 600..750 (typ 650) |
| fT, IC 10 mA, VCE 5 V, 100 MHz | 253,8 MHz | min 100, typ 300 | 186,2 MHz | min 100, typ 200 |
| Cobo, VCB 10 V, 1 MHz | 3,000 pF | typ 3 pF (nessun min/max) | 3,000 pF | typ 3 pF |
| Cibo, VEB 0,5 V inverso | 11,02 pF | **il datasheet non lo da** | 22,29 pF | **non dato** |

Gruppi A/C, solo hFE a 2 mA (finestra): BC847A 210,2 (110..220); BC847C 761,9 (420..800); BC857A 232,9
(125..250); BC857C **793,5 (420..800: dentro per lo 0,8 %)**.

BAT54 (DS11005 p. 2-3):

| Cifra | misurato | datasheet |
|---|---|---|
| VF 0,1 / 1 / 10 / 30 / 100 mA | 141 / 208 / 301 / 385 / 584 mV | max 240 / 320 / 400 / 500 / 800 mV (p. 2) |
| IR, VR 25 V, 25 C | 0,763 uA | max 2,0 uA (p. 2); curva tipica fig. 2 p. 3 ~0,2 uA |
| CT, VR 1 V, 1 MHz | 7,63 pF | max 10 pF (p. 2); fig. 3 p. 3 letta ~9,3 pF (modello -18 %) |
| CT, VR 25 V | 2,53 pF | fig. 3 letta ~2,6 pF |
| **IR a 60 C, VR 25 V** | **7,07 uA** | fig. 2 non ha la curva a 60 C: interpolata tra 25 C (0,205 uA) e 75 C (5,2 uA) = **~1,9 uA** (lettura a occhio, +-25 %) |

## Cio che non torna (coi numeri)
1. **BC847B: VBE(on) 8,4 mV sopra il massimo di datasheet, 48 mV sopra il tipico.** Causa nel modello: IS = 3,75 fA
   contro 10,2 fA dei modelli A e C (che danno 678 mV). Un innesco di ritenuta che dipende dalla VBE vedra una soglia
   piu alta della parte vera (~660 mV tipico). La ricetta lo blocca *come deviazione*.
2. **CJE incoerente tra i gruppi, in tutti e due i tipi**: BC847 A 26,8 pF, B 13,3 pF, C 26,8 pF; BC857 A 13,3 pF,
   B 26,9 pF, C 13,3 pF. Un fattore 2 senza ragione fisica (stessa lastra). Cibo del modello non e affidabile meglio
   di un fattore 2; il datasheet non ne da uno. CJC e coerente (8,67 pF NPN; 7,80 pF PNP A/C, 8,67 pF PNP B) e da
   Cobo = 3,00 pF, che torna col tipico di 3 pF. Con 1 nF base-emettitore la CJE (10-27 pF) conta meno del 3 %.
3. **BF = 1,61k nel BC847B** (e 1,09k nei C) con hFE misurato 239 / 762: il guadagno vero e deciso da ISE/IKF, non da
   BF. Non e un errore, ma BF non e la cifra da leggere.
4. **BAT54, perdita: il modello e 3,7x la curva tipica a 25 C** (IS = 649 nA, piatto in VR; la fig. 2 sale con VR).
   La dipendenza dalla temperatura *e* credibile: IR(60)/IR(25) = 9,3 nel modello contro ~9,5 dalla figura; 75 C:
   17,3 uA contro 5,2 (3,3x); 125 C: 226 uA contro 72 (3,1x). Il modello e quindi una stima per eccesso di ~3,4x
   della curva tipica, a ogni temperatura. A 60 C: 7,1 uA, tra il tipico letto (1,9 uA) e il massimo a 25 C (2 uA)
   scalato col rapporto della figura (~19 uA): dentro quella forbice, e la ricetta lo asserisce.
5. Il modello del BAT54 e di Zetex (v1.0, 25/04/00), non aggiornato da Diodes. Nessun modello ha KF/AF (niente 1/f).
6. Non verificato: stock e prezzo (non richiesti), pagine prodotto diodes.com (403); tutte le letture di figura
   (BAT54 fig. 2 e 3) sono a occhio.

## Parametri chiave
| Modello | IS | BF | CJE | CJC | TF | XTB | EG | XTI | altro |
|---|---|---|---|---|---|---|---|---|---|
| DI_BC847A | 10,2f | 301 | 26,8p | 8,67p | 427p | 1,5 | 1,12 | 3 (default) | IKF 60,7m ISE 5,82p |
| DI_BC847B | 3,75f | 1610 | 13,3p | 8,67p | 520p | 1,5 | 1,12 | 3 | IKF 8,79m ISE 8,38p TR 78,9n |
| DI_BC847C | 10,3f | 1090 | 26,8p | 8,67p | 427p | 1,5 | 1,12 | 3 | IKF 60,7m ISE 1,61p |
| DI_BC857A | 10,2f | 342 | 13,3p | 7,80p | 581p | 1,5 | 1,12 | 3 | IKF 72,9m ISE 5,59p |
| DI_BC857B | 5,51f | 424 | 26,9p | 8,67p | 700p | 1,5 | 1,12 | 3 | IKF 36,4m ISE 2,35p TR 121n |
| DI_BC857C | 10,2f | 1090 | 13,3p | 7,80p | 587p | 1,5 | 1,12 | 3 | IKF 36,4m ISE 1,24p |

BAT54: IS 649n, N 1,04, RS 2,09, IKF 20m, XTI 2, EG 0,58, CJO 12,4p, M 0,381, VJ 0,391, BV 50, IBV 100u, ISR 431n, NR 4,99.

Ricette: `tb_bc847a/b/c`, `tb_bc857a/b/c`, `tb_bat54` in `scripts/validate_models.py`. Non aggiornato `models/README.md`
(elenco dei modelli del costruttore): resta al chiamante.
