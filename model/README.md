# Local model replication package

This package contains synthetic model computations only. It reads no research repository at runtime, makes no network requests, and contains no manuscript, documentary dataset, literature PDF, tracker, source log or author working note. This folder supplies the model component of the deposit.

Run from any directory with Python 3.11 and installed NumPy, Matplotlib and Shapely:

```sh
python3 run_all.py
```

For a fresh comparison against a read-only Markdown reference:

```sh
python3 run_all.py --reference /absolute/path/to/reference.md
```

The default compares with `printed_values.json`, a numerical-only extraction from the specified reference, authenticated by its SHA-256. The optional argument extracts expectations afresh without copying the reference. The historical consolidation count is no longer printed in the current reference; its arithmetic is retained separately and is not a required printed comparison. Both modes recompute the same values. Output stays in this package. `--jobs 1` selects sequential execution; default is three local processes. Expected runtime is about 2–5 minutes on the tested machine; allow longer on slower hardware; measured runtime and tested versions are recorded in `results.json`. Tested with Python 3.11.17, NumPy 2.2.6, Matplotlib 3.10.7 and Shapely 2.1.2. No software is installed by the runner.

Exit codes: **0** = computations and reference coverage complete; **1** = source failure or numerical mismatch; **2** = arithmetic passed but a required statement or figure is absent from the specified reference. `CHECKS.md` lists every mismatch with its reference line, printed value and recomputed value. `results.json` includes the full comparison register and per-script outcomes. A nonzero code must not be described as full replication success.

## Files

| File | Purpose |
|---|---|
| `run_all.py` | Orchestrates all copied check scripts, figures and reference comparison; reports failures explicitly. |
| `check_printed.py` | Extracts table numbers and reference hashes; independently recomputes Tables 1 and A1–A5, figure areas, accounting contrasts and scalar counts. |
| `printed_values.json` | Numerical reference expectations, line locations and hashes; no reference prose. |
| `closed_form/characterise.py` | Original Fraction continuation/investment solver and deterministic seed-7/seed-11 samples. |
| `closed_form/classification.py` | Original closed-form cells and seed-23 joint-only classification. Run from package root, as the runner does. |
| `independent/solver.py` | Independent exact finite-action solver; Lemma 1, F/T/D theorem, zero-saving and infeasible-investment boundaries. |
| `independent/audit.py` | Independent/lead comparison, rational lattice, corollary membership and changed-tie witnesses. |
| `independent/boundaries.py` | Exact endpoint certificates, strict examples, operating-affordability and altered acceptance protocols. |
| `general/check_theory.py` | General-domain welfare ordering, conditional price caps, weighted rights, legacy affordability, overhead and additional exact checks. |
| `extensions/check_extensions.py` | Legacy, overhead, continuous harm, cost-price competition and refundable-reserve extensions; retains failed attempted generalisations. |
| `institutions/solver.py` | Exact Table 2 row checks, Table 1 institutions, noncomposition and figure-area integrals. Writes a failures register even when its process exits zero; the runner checks that register. |
| `phase/fig_cases.py` | Exact affine-cell phase diagram; independent offer enumeration, closed-form partition and boundary checks. Outputs PDF, EPS and PNG with embedded fonts and greyscale hatching. |
| `region/fig_region.py` | Original investment/value region plot; unchanged plotted content, plus PDF/EPS exports. Plotting samples affine lines, while areas and bounds are checked in exact arithmetic. |
| `historical/reserve_checks.py` | Original 61,583-point shared/reserve comparison; the runner extracts a numeric receipt from its stdout. |
| `historical/consolidation.py` | Original consolidation checks, including the historical 288,756-comparison subset and later expanded checks. |
| `historical/model_extensions.py` | Original independent Grid II solver, seed-20260930 sampling, top-up accounting and supplementary diagnostic plots. |
| `econ/scripts/check_ai_dependence_model.py` | Original Grid I/model implementation; used for the historical 12,000-state crosscheck. Its output-writing main is not run. |
| `MANIFEST.md` | Mapping of statements, tables and figures to their checking code. |
| `SHA256SUMS.json` | Integrity hashes of package inputs. Generated outputs are excluded. |

Folders use descriptive names; dependency paths have been updated. Original mathematical functions are retained. Comment-only substitutions, the removal of a progress-log dependency and additional vector exports are listed in the assembly report outside this package.

## Scope and interpretation

The 6 October 2026 numerical reference includes Lemma 1, Theorems 1 and 2, Corollary 1, Proposition 1 and the phase diagram. Table 1a corresponds to internal comparison key 1A; Table 1 to key 1B; Table A4 to A4A and Table A4 panel b to A4B. These internal keys preserve the comparison algorithm.

Finite exact grids verify implementations and do not replace proofs. Documentary counts and citation claims are outside this runner. The phase diagram's threat example uses O1=3; Table 1a uses O1=13/4. These are distinct calculations. Historical figure labels are preserved where they do not denote current manuscript numbering.

Software is licensed under MIT; documentation, compiled data and generated figures under CC BY 4.0. See the root licence files.

## Additional historical checks

Run `python3 model/timing/timing_extension.py` and `python3 model/legacy_check/independent_solver.py model/econ/scripts` from the repository root. These preserve the original mathematical functions; the timing script has only a package-relative import path. Their outputs are separate from `run_all.py`. Historical proposition numbering in these scripts refers to their original derivations.
