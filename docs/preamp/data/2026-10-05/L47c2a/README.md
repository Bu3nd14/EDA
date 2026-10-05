# L47c2a — il mute coi soli relè: il firmware e l'alimentatore col carico nuovo, i dati

La prima parte di L47c2 (scelta dell'utente: «Due parti»). ADR-062 (L47c1). Report:
`docs/preamp/reports/2026-10-05-L47c2a-firmware-alimentatore.md`. Sotto, `<L>` è questa
cartella e `<R>` la radice del repo.

| Percorso | Cosa |
|---|---|
| `deck/genera_tb_psu.py` | il generatore di L42b copiato e adattato al `psu.net` senza il pilota delle LDR; le differenze sono nell'intestazione |
| `deck/genera_tutti.sh`, `deck/corri_tutti.sh` | i sei deck dell'alimentatore: generati, poi corsi in parallelo |
| `deck/analizza.py` (di L42b), `deck/analizza_timer.py` (di L41b1) | copiati identici: non dipendevano dalle LDR |
| `deck/varianti.py`, `deck/corri_varianti.sh` | la tenuta di `VRELAY` con C520 a 3300 e 2200 µF, per la domanda all'utente |
| `deck/corri_controfattuale.sh` | il controfattuale del carico (`--carico l41a`, col metodo gear) |
| `deck/corri_seq.sh`, `tutti_seq.sh`, `analizza_seq.py`, `sano.py`, `confronta.py` | la catena di L41b2 (il core sul circuito fino al punto fisso), adattata: niente DAC, niente inversione, criteri riscritti **prima** delle corse dove la sfumatura li definiva |
| `timer/` | il banco del temporizzatore di L41b1, nominale e angolo minimo; `analisi_timer.txt` |
| `rete/`, `guasti/` | i banchi di L41a ricorsi (L42b): la tenuta di `VRELAY` e i guasti; `analisi.csv` |
| `carico_l41a/` | gli stessi col carico di L41a (senza le bistabili del trim e i 2 mA del micro) |
| `varianti/c3300u/`, `varianti/c2200u/` | la tenuta con C520 più piccolo |
| `seq/` | le sei sequenze col firmware nuovo sul circuito; `analisi_seq.txt` |
| `falsi/esito.txt` | `run_host_tests.sh --falsi`: **19 su 19** |

Le forme d'onda (`*.txt` di wrdata, `*_out.txt`) non si committano (`.gitignore` di radice).

## Come si rifà

Dalla radice del repo, coi percorsi assoluti:

```sh
/bin/zsh <L>/deck/genera_tutti.sh          # i sei deck da circuits/preamp/psu.net
/bin/zsh <L>/deck/corri_tutti.sh           # ngspice, ~2 min; vedi sotto i due «errori» attesi
/usr/bin/python3 <L>/deck/analizza.py <L>/rete      # idem <L>/guasti
cd <L>/timer ; /usr/bin/python3 ../deck/analizza_timer.py tb_psu_timer_nom.log tb_psu_timer_min.log
/bin/zsh <L>/deck/corri_controfattuale.sh  # rigenera e corre carico_l41a/ col metodo gear
/usr/bin/python3 <L>/deck/varianti.py ; /bin/zsh <L>/deck/corri_varianti.sh
/bin/zsh <L>/deck/tutti_seq.sh             # le sei sequenze, ~5 min
/bin/zsh <R>/firmware/preamp_timer/test/run_host_tests.sh --falsi <L>/falsi/esito.txt
```

`corri_tutti.sh` segnala come errore due cose che non lo sono:
- nel banco del temporizzatore, `t_permit … out of interval` nel caso
  `perdita_rete_micro_fermo_alto`: col micro bloccato alto `PERMIT_CMD` non si rilascia nei 400
  ms, e la misura manca per costruzione (come in L41b1 e L42b; `analizza_timer.py` lo sa);
- nel controfattuale col metodo trapezoidale, `regime_m10` si fermava a 0,900153 s («Timestep
  too small», qq504, il fronte di `VRELAY_EN`): da qui `corri_controfattuale.sh` col metodo gear.

## I risultati

**Il firmware sull'host**: 76 controlli, 0 falliti, 9 test su 9; **19 falsi su 19**.

**Il firmware sul circuito** (`seq/analisi_seq.txt`): **6 sequenze su 6**, ognuna al punto fisso
con 0 sostituzioni:

| Sequenza | Cifre |
|---|---|
| accensione | `VRELAY_EN` 100,7 ms dopo i rail in regolazione; `MUTE_CMD` 49,4 ms dopo `VRELAY` ≥ 9,6 V; MUSICA a +0,214 s |
| rilascio | `MUTE_CMD` eccitato **21,1 ms** dopo SW3; MUSICA a +31 ms |
| spegnimento | `MUTE_CMD` rilasciato **21,2 ms** dopo il pin del frontale (che passa V5/2 a +7,1 ms); Δ 39,8 ms; K501 aperto 63,4 ms dopo `PERMIT_CMD` |
| buco di 20 ms | jack a 14,4 ms; classe 1; `MUTE_CMD` di nuovo 0,501 s dopo il ritorno |
| buco di 200 ms | jack a 14,4 ms; classe 2 (V+ a 9,99 V); di nuovo 0,174 s dopo il ritorno |
| guasto (U502) | jack a 10,7 ms; K501 aperto 102,9 ms dopo `MUTE_REQ`, fino alla fine; GUASTO |

**Il temporizzatore** (`timer/analisi_timer.txt`), nominale / angolo minimo: Δ **18,84 / 16,91
ms** (uguali a L41b1 e L42b); `VRELAY` a J1 < 9,6 V 60,4 / 56,5 ms dopo `PERMIT_CMD` (42,0 /
43,2 col guasto di U503); i due controfattuali falliscono come devono. **Lo standby: 80,5 / 79,0
mW dal secondario di T2**, contro 92,5 / 90,8 col pilota (L42b).

**La tenuta di `VRELAY_REG` ≥ 11,4 V** dopo il rilascio dei jack (`rete/analisi.csv`), rete −10 /
nom / +10 %:

| | −10 % | nom | +10 % |
|---|---|---|---|
| **L47c2a, 4700 µF** | **61,1 ms** | 142,2 | 223,6 |
| L42b, col pilota | 36,1 | 102,1 | 168,5 |
| L41a | 62,8 | 144,9 | 227,3 |
| variante 3300 µF | 41,0 | 97,9 | 155,1 |
| variante 2200 µF | 25,1 | 63,1 | 101,3 |
| controfattuale, carico di L41a (gear) | 64,3 | 147,3 | 230,6 |

P9 chiede ≥ 25 ms. **Scelta dell'utente: «Tenere 4700 µF»**.

Il controfattuale sta 1,5–3,3 ms **sopra** L41a, non uguale come in L42b. Il metodo non c'entra:
il deck di oggi col metodo gear dà 61,112 contro 61,097 ms. **Ipotesi, non provata**: il banco
carica i regolatori della loro corrente di riposo per parte da L41b1 (2 µA sul MCP1703), mentre
L41a dava 1 mA a ciascuno; in L42b i ~0,8 mA del DAC e degli amplificatori del pilota
compensavano per caso. La differenza fra oggi e il controfattuale (3,2 ms a −10 %) è il carico
che resta: le bistabili del trim e il micro.

**I guasti** (`guasti/analisi.csv`) tornano verso L41a: U503 spento, jack a **15,65 ms** (L42b
13,29, L41a 15,8); col rivelatore guasto a rete −10 % il sorvegliante di `VRELAY_REG` non scatta
più per primo (jack a 72,7 ms, L42b 59,9, L41a 72,5). U501 e U502 spenti come prima.

**La netlist dell'alimentatore**, rigenerata dopo i soli commenti di `psu.py`: **uguale per
connettività** (118 componenti, 61 reti; `L47c1/script/netdiff.py`); nel testo cambiano solo la
data, il percorso e i numeri di riga di SKiDL. ERC 24 avvisi e 2 errori, come in L47c1.
