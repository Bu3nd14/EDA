# Prompt per la sessione successiva — L69, la ritenuta che tiene i 5 V a massa

Nome della sessione: **hi-fi preamp L69** (la convenzione è in `CLAUDE.md`).

> Prompt scritto alla chiusura di L68 (2026-11-03: la FMEA del temporizzatore a comparatori, NC-078
> chiusa). Le righe di R572 e R576 in corto sono uscite a gravità 5; l'utente ha scelto «Non conformità
> maggiore» (NC-079) e poi «Prima la correzione». L'ordine verso G1: **L69** → L65 → G1.

Riprendo il progetto del preamplificatore hi-fi in questo repository. Questa sessione fa **L69**, e si
ferma.

## Che cosa fare

**Il rimedio di NC-079**: con R572 (200 kΩ, il pull-up di AT_MRQ) o R576 (10 kΩ, il pull-up di AT_ON) in
corto, e poi un rail che cade (in musica, o all'accensione con un rail morto), la ritenuta scatta col suo
anodo su AT_ON, che è sui 5 V (R576) o li riceve da AT_MRQ attraverso D537 (R572): Q514 e Q513 tengono i
5 V a massa. U504 va al limite, **0,25 A**, 218 / 205 °C a calcolo; la corrente passa da Q514 nella base di
Q513 a V_BE 1,48 V: **Q513 ~0,37 W, ~209 °C** (BC847, 403 °C/W, Tj max 150 °C; 0,25 A di emettitore
contro i 200 mA di picco). Il circuito **cambia**.

1. **Leggi prima**:
   - NC-079 in `NONCOMPLIANCE.md`, ADR-115 (che cosa ha deciso l'utente e che cosa no), la riga di L69
     nella tabella dei lotti di `STATE.md`;
   - il report di L68 (`reports/2026-11-03-L68-fmea-temporizzatore.md`) e il README di
     `data/2026-11-03/L68/`: il banco (`psu/`, coi modi in `modi.py`: `RIGHE_L68`, `EVENTI_L58B`), le
     corse, `calore_5v.csv`, la catena, `fmea_l68.py`;
   - il temporizzatore nel sorgente, `circuits/preamp/psu.py` (la ritenuta: Q513 / Q514, R582–R585,
     C554 / C555; AT_ON = VRELAY_EN, R576; AT_MRQ, R572, D537), e ADR-102 / ADR-103 (R585) / ADR-105.
2. **Il meccanismo, misurato** sul banco di L68 (`script/guarda.py` sulle forme d'onda di
   `f_r576_corto_guas` e `f_r572_corto_guas`, che non sono versionate: si ricorrono): la corrente della
   ritenuta, la potenza di Q513 e Q514, i 5 V.
3. **Le opzioni**, ognuna misurata **prima** di portarla all'utente (memoria «Opzioni verificate sui
   limiti»: la temperatura di Q513 / Q514 e di U504 contro il limite, a rete ±10 %): per esempio una
   resistenza in serie all'anodo della ritenuta o al pull-up di AT_ON, o un pull-up di AT_MRQ che non arrivi
   ad AT_ON. Per ognuna: R572 e R576 in corto col rail che cade, **e** i sette eventi e il mute dal frontale
   a circuito sano, contro le corse sane di L64b (`data/2026-11-03/L64b/an_l64b.csv`, i criteri di L54b3b:
   la ritenuta che scatta col rail − che cade, K501 ≥ 50 ms dopo il permesso, la base di Q513 ≤ 0,45 V dove
   non deve scattare, anche a freddo e col comparatore a 2,2 V come in L58a). Poi la domanda all'utente,
   per nome, coi numeri.
4. **Il sorgente**: il rimedio scelto in `psu.py` col commento che punta all'ADR nuova; `psu.net` e i
   disegni rigenerati (`run_tests.sh`, gli schemi completi di L63 ridisegnati uguali dove non cambia
   niente); `check_psu_harness.py` se tocca i connettori.
5. **Le corse rifatte sul sorgente nuovo**: le simulazioni del temporizzatore di L68 che toccano la
   ritenuta e AT_ON (almeno le 31 righe della ritenuta cieca, R572 / R576, e le parti nuove del rimedio coi
   loro modi), contro gli otto eventi; il calore dei 5 V; le righe toccate riscritte in una fonte nuova di
   `fmea_oggi.py` (`FMEA_FONTI` in `build_dossier.py`), le parti nuove con le loro righe (`copertura.py`
   deve restare a 0 per l'alimentatore).
6. **Il dossier rigenerato** (`build_dossier.py` «OK», i sabotaggi di L68 riportati sui file nuovi cadono
   tutti), e il PDF all'utente se lo vuole (in `/Users/roberto/Documents`, un PDF per documento).

## I vincoli

- **La macchina è un MacBook Air senza ventole**: al più **3 simulazioni insieme**, con `nice -n 10`;
  prima di lanciare, `pgrep ngspice`. Se l'utente dice che girano altre sessioni, al più **2**. La catena al
  jack: 2 insieme (~1 GB l'una).
- Comandi semplici, percorsi assoluti, script scritti con Write; il controllo del worktree rifiuta i
  comandi composti (cicli, variabili calcolate, `nice` in una catena, gli script in linea con `<<`, le
  pipe dentro `$(...)`): scriverli in uno script.
- Una lista che `xargs` sta leggendo non si riscrive; i sabotaggi toccano i file per un istante: niente
  commit mentre girano.
- `git add` un percorso alla volta; commit e push prima di ogni lista lunga.
- Le forme d'onda e le corse grezze non si committano: `.gitignore` prima di ogni `git add` di una
  cartella dati (L68: ~19 MB versionati, ~40 GB di forme d'onda fuori).
- Le domande si fanno per nome; i colpi al jack in dB SPL; ogni opzione con la sua temperatura contro il
  limite.

## CHIUSURA

1. `STATE.md`: L69 **fatto**, NC-079 chiusa se il rimedio regge, il prossimo **L65**; le celle di In breve;
   il diario (la voce più vecchia delle tre va in `STATE-STORIA.md`).
2. Riscrivi questo file per L65 («Nome della sessione: hi-fi preamp L65»).
3. Commit, push, PR; `/bin/zsh scripts/chunk_close.sh L69`; rimuovi il worktree; fermati.
