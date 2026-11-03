# L64c — il dossier rigenerato, la chiusura: i dati

La terza delle tre parti di L64 (l'utente, 2026-11-02: «Three parts, like last time»). Il circuito è
quello di `main` dopo L64b (01084983f): **non cambia**. Sotto, `<L>` è questa cartella e `<R>` la
radice del repo. Le corse a priorità bassa, al più due insieme.

## Le scelte dell'utente

- le righe della FMEA che dicevano il micro: **«Riscriverle ora»** (dalle corse di oggi);
- la FMEA nella pagina: **«Sintesi + alte + medie»**;
- le schede di prova del 9 ottobre: **«Togliere la sezione»** (nominate in «Cosa non dice», coi conti);
- la consegna: **«qui sul mac nella folder che dici tu, ma 3 PDF»**;
- R517 / R518 in corto (U504 a 241 °C): **«Accettare come C536»**; i 5 V persi al jack (69,7 dB SPL):
  **«Accettare come U503»** — ADR-114;
- la FMEA del temporizzatore a comparatori: **«Non conformità, lotto apposta»** — NC-078, L68.

## Il primo giro

`primo_giro.txt`: `build_dossier.py` con `PARTI` completa sul `main` di L64b, prima di ogni cambio:
**nessun rifiuto**. La pagina passava, ma diceva le schede di prova come «sbrogliate dalle netlist di
oggi», il micro nella riga dell'alimentatore di «Cosa non dice», e «nessun modello del costruttore»
nella provenienza dell'alimentatore: tre frasi false che nessun controllo vedeva.

## Che cosa c'è

| Percorso | Che cosa |
|---|---|
| `script/parti_schede.py`, `parti_schede.csv` | Le parti dei `.kicad_pcb` di L49a / L49b contro le netlist di oggi: scheda audio 458 contro 653 (195 aggiunte, 67 valori cambiati), alimentatore 118 contro 187 (77 aggiunte, 8 tolte, fra cui U509 ATtiny3216 e J515 UPDI). I fori di montaggio fuori dal conto |
| `script/ridisegna.sh` | I due schemi completi di L63 ridisegnati fuori dal repo e confrontati: i manifesti byte per byte, gli SVG a meno della data e degli identificativi delle clip di matplotlib |
| `script/fmea_oggi.py`, `fmea_oggi.csv`, `fmea_oggi_conti.csv` | La FMEA di oggi: le cinque fonti (L45d2b3b3, L58a2, L58b, L66, L64c), la riga più recente per chiave (ref, modo, caso). **563 righe: 15 alte, 67 medie, 476 basse, 5 escluse**. Rifiuta una priorità che la matrice di ADR-070 non dà, una riga ancora «alla diagnosi», una riga senza stato |
| `script/copertura.py`, `copertura.csv` | Le parti delle netlist di oggi senza nessuna riga: dell'alimentatore **59 su 187** (37 del temporizzatore a comparatori, 5 connettori, 17 test point): NC-078. Sulla scheda audio il conto per nome non vale (le righe nominano le parti per ruolo) |
| `psu/` | Il banco dell'alimentatore di L64b, copiato. **Un'aggiunta** in `modi.py`: `RIGHE_L64C`, i dodici modi degli ingressi del temporizzatore (R517, R518, R541, R542, C532, C533, aperti e in corto) contro `accs`, `spls`, `inss` |
| `carico.txt` | Quello di L64b, copiato (il carico non cambia) |
| `lista_l64c.txt`, `lista_ciechi.txt`, `script/corri_sequenze.sh`, `script/controlla_ok.py`, `seq/oggi/` | **44 corse**: le 36 degli ingressi, C536 in corto e U512 spento alle tre reti (6), e i due canali ciechi del sorvegliante (le sequenze di L64b ricorse qui: le loro forme d'onda non sono versionate). Ogni `ok.txt` con le opzioni della sua riga |
| `script/analizza.sh`, `an_l64c.csv` | `psu/analizza_mc.py` (le colonne di L54b3b). I due canali ciechi **uguali a `an_l64b.csv` colonna per colonna** |
| `script/calore_5v.py`, `calore_5v.csv` | U504 e U512 (MCP1703A): la potenza dalle forme d'onda, la Tj al caso peggiore di 100 ms a 60 °C d'aria, col metodo e i limiti di `riassunto_075.py` di L45d2b3b1. C536 in corto **2,99 W, 245,6 °C** (L45d2b3b1: 2,99 W, 240–246 °C); **R517 / R518 in corto 2,93 W, 241,4 °C**, R518 anche U512 a 128 °C |
| `catena/` | La catena fino al jack di L64b (il ponte, il deck di V2 con la matrice l41c, le corse, la guardia, l'analisi), su una copia del generatore del deck che prende i casi da `L64C_CASI`; `tabella.py` coi criteri scritti prima delle corse (≤ 2 mV, l'obiettivo di ADR-046). **Il controllo**: `corto_u503` di L64b ridà **6,492 mV**. I 5 V persi: **6,509 mV, 69,7 dB SPL** alle tre reti (`tabella_l64c.csv`); i canali ciechi: **87,5 µV (32,3 dB SPL)** il +, **14,4 µV (16,6 dB SPL)** il − (`tabella_l64c_ciechi.csv`) |
| `script/fmea_l64c.py`, `fmea_l64c.csv` | Le **28 righe** riscritte: le dieci del sorvegliante accettate con ADR-073 (superata) **da alta a bassa** (gravità 1, il jack sotto V2); i dodici modi degli ingressi (R517 / R518 in corto **da bassa ad alta**, gravità 5, ADR-114); R543 e R544–R547 escluse (uscite col micro); C536 in corto alta, accettata; U512 spento **da bassa a media** (69,7 dB SPL, ADR-114) |
| `script/sabotaggi.py`, `sabotaggi.txt` | I sabotaggi di L64a e L64b (le loro liste, importate) e i dodici nuovi |

Le forme d'onda (`*_out.txt`), i `.dat` e i deck delle singole corse della catena non stanno nel
repository (`.gitignore`): si rifanno coi comandi sotto.

## Comandi

```sh
/usr/bin/python3 -I <L>/script/parti_schede.py <R>
/bin/zsh <L>/script/ridisegna.sh <cartella fuori dal repo>
/bin/zsh <L>/script/corri_sequenze.sh 2 <L>/lista_l64c.txt ; /usr/bin/python3 -I <L>/script/controlla_ok.py
/bin/zsh <L>/script/analizza.sh
/usr/bin/python3 -I <L>/script/calore_5v.py <L>/seq/oggi <L>/calore_5v.csv $(sed 's/ .*//' <L>/lista_l64c.txt)
/bin/zsh <L>/catena/catena.sh ; /bin/zsh <L>/catena/catena_ciechi.sh     # escono 1: il criterio e' superato
/usr/bin/python3 -I <L>/script/fmea_l64c.py ; /usr/bin/python3 -I <L>/script/fmea_oggi.py
/usr/bin/python3 -I <L>/script/copertura.py <R>
/usr/bin/python3 <R>/docs/preamp/dossier/build_dossier.py
/usr/bin/python3 <L>/script/sabotaggi.py
```
