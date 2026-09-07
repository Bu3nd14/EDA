# Provenance convention

Every file under `models/` (model/subckt library files) has a sidecar
JSON file next to it: `<same-basename-with-extension>.provenance.json`.
Example: `models/diodes/generic_diode.lib` -> 
`models/diodes/generic_diode.provenance.json`.

## Schema

```json
{
  "canonical_file": "generic_diode.lib",
  "device_class": "diodes",
  "origin": "authored | vendor_derived",
  "vendor_source_path": null | "vendor/diodes/demo_vendor/1N4148_TEST/vendor_1n4148_test.lib",
  "vendor_source_sha256": null | "<sha256 of the vendor original at copy time>",
  "date_created": "YYYY-MM-DD",
  "author": "roberto.carmeli@gmail.com | AI agent name + session",
  "changes": "free text: exactly what differs from the vendor original, or 'N/A - authored from scratch, not derived from any vendor file'",
  "reason": "why this file/change exists",
  "notes": "known limitations, e.g. 'macro-model, not a foundry-accurate model'"
}
```

## Rules

1. `origin: "authored"` files must have `vendor_source_path: null` and
   `vendor_source_sha256: null`, and `changes` must say so explicitly.
2. `origin: "vendor_derived"` files MUST have a non-null
   `vendor_source_path` pointing at a real file under `vendor/`, and
   `vendor_source_sha256` must match the sha256 actually recorded in
   that vendor file's own `<file>.sha256` at the time of derivation
   (used as a tamper/staleness check — it does NOT have to match the
   vendor file's *current* hash if the vendor file was later replaced
   with a newer datasheet revision; it documents which revision this
   copy was derived from).
3. `scripts/validate_models.py` enforces (1) structurally for every
   model file (run with `--check-provenance` to check provenance only,
   without running ngspice), and for (2) it actually re-hashes the
   live file at `vendor_source_path` and compares it to
   `vendor_source_sha256` recorded in the sidecar — a real mismatch
   (e.g. someone managed to modify a "frozen" vendor file, or the
   provenance path is stale/wrong) is reported as a FAIL, not silently
   ignored.
4. Every vendor file added under `vendor/` gets its own
   `PROVENANCE.json` (see `vendor/README.md`) recording where *we*
   obtained it from (real download URL, or, for the disposable demo
   fixture in this repo, an explicit "FABRICATED FOR DEMO" statement).

## Known limitation (flagged, not silently ignored)

The validator checks that `vendor_source_sha256` is present and
non-empty for `vendor_derived` files, and that the referenced
`vendor_source_path` currently exists, and that its *current* sha256
still matches (since in this project vendor files are frozen read-only
and never change, current == derivation-time hash in practice). If a
future workflow legitimately updates a vendor file in place (which
should never happen — vendor files are supposed to be immutable), this
check would correctly flag every derived copy as stale, which is the
intended behavior.
