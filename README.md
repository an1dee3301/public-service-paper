# Working-paper replication files

Local replication materials for the working-paper build of 6 October 2026. The manuscript is posted separately.

## Reproduce the model

With Python 3.11 and NumPy, Matplotlib and Shapely installed:

```sh
python3 model/run_all.py
```

The runner uses the supplied numerical-only reference snapshot, regenerates model checks and figures, and returns 0 only when required arithmetic and printed comparisons pass. `model/README.md` gives optional comparison against a separately held reference and two supplementary historical commands. The tested versions are in `model/results.json` and `model/requirements.txt`.

## Contents

- `model/`: independent solvers, exact checks, numerical reference, results and generated figures.
- `coding/`: codebooks, blind human coding sheets as CSV, automated codes and comparison readouts.
- `episodes/`: original episode banks, source-check codes, coding limits and frozen transition design.
- `sources/`: public-document metadata and captured-byte hashes, with unavailable fields explicit.
- `POINTERS.md`: every replication-package pointer in the three reference files, mapped to released files or an explicit exclusion.
- `PROVENANCE.md`: hash-only mapping to local origins; no private paths.

The model run passed 172 printed-number comparisons with no mismatch. Documentary files preserve historical coding; the episode banks have not been silently rewritten to match later manuscript corrections. See their folder notes and the pointer exclusions. Missing documentary hashes and access dates are explicitly recorded; they have not been invented.

## Licences

All software (`.py` files in `model/`) is covered by the MIT licence in `LICENSE`. Documentation, author-compiled data tables and figures in `model/`, `coding/`, `episodes/` and `sources/`, plus root documentation, are covered by Creative Commons Attribution 4.0 International in `LICENSE-docs`. Short attributed source fragments and third-party public documents referred to by address and hash are not relicensed and remain with their issuers. No third-party full text is included.
