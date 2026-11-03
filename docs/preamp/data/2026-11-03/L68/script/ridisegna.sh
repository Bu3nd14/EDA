#!/bin/zsh
# L64c: i due schemi completi di L63 (audio_draw.py, psu_draw.py) ridisegnati in <dir> fuori dal repo
# e confrontati byte per byte con quelli versionati in docs/preamp/schematic/. La seconda strada
# degli schemi del dossier: lo schema e' quello che il sorgente di oggi disegna.
#
#   /bin/zsh script/ridisegna.sh <dir>
set -u
OUT=$1
R=${0:A:h:h:h:h:h:h:h}
S=$R/docs/preamp/schematic
PY=/Users/roberto/EDA/env/venv/bin/python3
mkdir -p "$OUT"
cd "$OUT" || exit 2
AUDIO_SHEET_DIR=$OUT $PY $S/audio_draw.py > "$OUT/audio_draw.txt" 2>&1 || { echo "audio_draw.py: rc $?"; exit 1; }
PSU_SHEET_DIR=$OUT $PY $S/psu_draw.py > "$OUT/psu_draw.txt" 2>&1 || { echo "psu_draw.py: rc $?"; exit 1; }
# Lo SVG di matplotlib porta la data (dc:date) e identificativi di clip casuali (id="p<esadecimale>",
# url(#p<esadecimale>)): si tolgono da tutti e due prima del confronto, e il resto deve essere uguale
# byte per byte. Il PDF porta le sue date di creazione: non si confronta (lo SVG e' lo stesso disegno).
norm() {
    /usr/bin/sed -E -e '/<dc:date>/d' -e 's/(id="|url\(#)p[0-9a-f]+/\1pX/g' "$1"
}
diversi=0
for f in audio.manifest.json psu.manifest.json; do
    if cmp -s "$OUT/$f" "$S/$f"; then echo "$f uguale"; else echo "$f DIVERSO"; diversi=$((diversi + 1)); fi
done
for f in audio.svg psu.svg; do
    norm "$OUT/$f" > "$OUT/$f.norm"
    norm "$S/$f" > "$OUT/$f.versionato.norm"
    if cmp -s "$OUT/$f.norm" "$OUT/$f.versionato.norm"; then
        echo "$f uguale (a meno della data e degli identificativi delle clip)"
    else
        echo "$f DIVERSO"; diversi=$((diversi + 1))
    fi
done
exit $diversi
