# Working-paper replication files

Local replication materials for the working-paper build of 7 October 2026. The manuscript is posted separately.

## Reproduce the model

With Python 3.11 and NumPy, Matplotlib and Shapely installed:

```sh
python3 model/run_all.py
```

The runner uses the supplied numerical-only reference snapshot, regenerates model checks and figures, and returns 0 only when required arithmetic and printed comparisons pass. `model/README.md` gives optional comparison against a separately held reference and two supplementary historical commands. The tested versions are in `model/results.json` and `model/requirements.txt`.

## Contents

- `model/`: independent solvers, exact checks, numerical reference, results and generated figures.
- `coding/`: codebooks, blind human coding sheets as CSV, automated codes and comparison readouts. `python3 coding/reproduce_documentary_counts.py` recomputes three printed counts (17 of 183 contracts with a provider tag; 21 of 64, 33 per cent, at first-pass confidence of at least 0.85; 22 and 25 documents naming the general conditions) from the released tables.
- `episodes/`: current table records, recorded source-reading scopes, explicitly preserved historical banks and frozen transition design.
- `sources/`: public-document metadata and captured-byte hashes, with unavailable fields explicit.
- `POINTERS.md`: historical 6 October pointer register for the three reference files, mapped to released files or an explicit exclusion.
- `PROVENANCE.md`: hash-only mapping to local origins; no private paths.

The model run passed 172 printed-number comparisons with no mismatch. The two current episode CSVs match the 7 October tables, including source qualifications and row-local aliases. Their earlier records and source-check verdicts remain byte-for-byte under each bank’s `historical/` folder. Other documentary coding remains historical. See `episodes/README.md` for the schema change and reading limits, and `POINTERS.md` for historical pointer exclusions. Missing documentary hashes and access dates are explicitly recorded; they have not been invented.

## Licences

All software (`.py` files in `model/` and `coding/`) is covered by the MIT licence in `LICENSE`. Documentation, author-compiled data tables and figures in `model/`, `coding/`, `episodes/` and `sources/`, plus root documentation, are covered by Creative Commons Attribution 4.0 International in `LICENSE-docs`. Short attributed source fragments and third-party public documents referred to by address and hash are not relicensed and remain with their issuers. No third-party full text is included.
