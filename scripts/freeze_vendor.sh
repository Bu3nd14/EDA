#!/bin/sh
# freeze_vendor.sh - make every file under vendor/ read-only (0444).
# Idempotent: safe to re-run any time. This is the structural
# enforcement that vendor originals are never hand-edited in place.
set -e

VENDOR_DIR="/Users/roberto/EDA/vendor"

if [ ! -d "$VENDOR_DIR" ]; then
    echo "ERROR: $VENDOR_DIR does not exist" >&2
    exit 1
fi

count=0
while IFS= read -r f; do
    chmod 0444 "$f"
    count=$((count + 1))
done << EOF
$(find "$VENDOR_DIR" -type f ! -name "README.md" ! -name ".DS_Store")
EOF

echo "Froze $count file(s) under $VENDOR_DIR to mode 0444."
