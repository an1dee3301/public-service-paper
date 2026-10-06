# Episode data and limits

`digital/records.csv` contains the 27 records of Table B2; `cross_sector/records.csv` contains the 33 records of Table B3 in the 7 October 2026 paper. Both files use the same 12 column labels and row order as the printed tables. Values are exact Markdown-source cell strings after trimming only table-delimiter padding: `<br>` preserves line breaks and `**` preserves emphasis. Numbers, qualifications, source locators and row-local supplier aliases remain as printed. Aliases do not identify the same organisation across different rows.

## Schema and historical preservation

The current records have 12 printed-table columns; this replaces the older 31-column digital schema and 25-column cross-sector schema. Scripts using the old field names must select the preserved historical files explicitly. No old field is presented as a current field unless it appears in the printed table. In particular, the old digital `cost_figures_and_status` field is not the current table’s `Funding / release holder` field.

Each bank has a `historical/` directory containing `records_ebe314c.csv` and `source_check_codes_ebe314c.csv`, byte-identical to the earlier deposit. These keep the original richer bank and the earlier occurrence-level verdicts, including failed access and disputed claims. They are not current confirmations. Historical records and public citations can identify source parties; the current row-local aliases are not a guarantee that parties cannot be inferred from sources.

## Current source-check file

The current `source_check_codes.csv` is a row/source register, with columns `row`, `source_id`, `recorded_reading_scope`, `row_locators` and `check_scope`. The reading scope and locators are transcribed from the current printed source cell. They report that cell’s dated reading history, not a new independent source check. A locator block applies to the whole row and is repeated for each source; it must not be attributed to every source individually. Reconstruction joins the source entries in order, then the locator block; this reproduces every source cell exactly.

The namespace `G3:` refers to `sources/digital.json`; `G1:` refers to `sources/cross_sector.json`. The identifier following the colon is the register’s `source_id`; `G3:WB` is the income-classification source. Registers supply citations, addresses and available capture hashes. Five later successful captures now carry their recorded address, access timestamp and byte hash; earlier capture metadata is retained in each updated record. Text-capture hashes identify saved visible text, not original server-response bytes. Unavailable metadata elsewhere remains explicitly unavailable.

## Interpretation limits

These are purposively selected descriptive records with source-attributed claims, forecasts, allegations and unverified outcomes. The 27 digital records include two boundary diagnostics; the 33 cross-sector records include 22 partial fits and 11 counterexamples. The first bank’s C1–C3 cells are descriptive readings; the second uses Y/P/N/U. Classifications were not independently coded. Equality to the table is version consistency, not new factual adjudication or a causal finding. Previously recorded conflicting dates and limited or indirect readings are retained.

`transitions/design.md` and `transitions/evidence_matrix.md` retain the frozen design and subsequent lead matrix. `POINTERS.md` is the historical 6 October register; episode paths now resolve to current records, while its earlier reading-stage descriptions should be read against the preserved historical files. Public originals are referenced, not redistributed. Only the two expressly requested data tables and their source metadata are transcribed; no surrounding paper text is distributed here.
