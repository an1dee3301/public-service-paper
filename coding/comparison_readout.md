# Author (human) coding vs first-pass / model coding: agreement

Preserved comparison readout from the original analysis (read-only on all inputs; 95% CIs are percentile bootstrap, 2000 resamples of coded units, seed 20260930). Provider names (OpenAI, Anthropic, Google, ...) are the *objects coded* in the supplier-terms set, not coders.

## 0. What this does and does not show

- **One human coder.** The author is a single coder who is also the designer of the study. Agreement here is agreement with *one* person, not inter-human reliability; there is no second human, so no human-human kappa exists.
- **Coded after the design was fixed.** The categories, codebooks and the research question were set before the author coded; the author could see the codebook and (for set 1) the capture list. The sheets were blind to the model codes by instruction, which this analysis cannot verify.
- **Model-vs-model agreement is not human validation.** Comparisons between first-pass, second-coder and recoding passes (reported for context) measure model consistency only. The adjudicated codes were produced from the first-pass and recoding passes, so agreement with them is partly agreement with a blend of model outputs.
- **Small n, wide intervals.** n = 40 (set 1, only 8 per field), 14 (set 2) and 50 (set 3). Field-level kappas are indicative only; CIs are wide and many resamples are degenerate.
- **Kappa paradox.** Where one category dominates (set 2: `none` in most cells), kappa can be low or undefined despite high raw agreement. Each table therefore gives raw agreement, kappa, and prevalence-adjusted kappa (PABAK = (k*p_o - 1)/(k - 1), k = number of categories in the scheme). No single number should be read alone.
- Agreement measures consistency of coding, not correctness; it says nothing about whether tender or public terms bind any executed public-sector contract.

## 1. Summary tables

### 1.1 Supplier terms (40 cells = 8 providers x 5 fields)

Primary scheme: `collapsed` (model label `no_in_read_document` counted as the author's `not_observed`; see mapping, section 3.1). Strict-label results follow.

| comparison | scheme | n | exact agreement | kappa | 95% CI | PABAK |
|---|---|---|---|---|---|---|
| A_first_pass | collapsed | 40 | 27/40 (68%) | 0.57 | [0.38, 0.74] | 0.57 |
| A_first_pass | strict_labels | 40 | 27/40 (68%) | 0.57 | [0.38, 0.74] | 0.61 |
| A_first_pass | collapsed_excl_NA_agree_by_construction | 35 | 22/35 (63%) | 0.48 | [0.29, 0.68] | 0.50 |
| A_first_pass | presence(yes/conditional vs not_observed) | 35 | 34/35 (97%) | 0.93 | [0.75, 1.00] | 0.94 |
| B_second_model_coder | collapsed | 40 | 21/40 (52%) | 0.20 | [-0.01, 0.40] | 0.37 |
| B_second_model_coder | strict_labels | 40 | 21/40 (52%) | 0.21 | [0.01, 0.41] | 0.43 |
| B_second_model_coder | collapsed_excl_NA_agree_by_construction | 40 | 21/40 (52%) | 0.20 | [-0.01, 0.40] | 0.37 |
| B_second_model_coder | presence(yes/conditional vs not_observed) | 35 | 25/35 (71%) | 0.12 | [-0.20, 0.47] | 0.43 |
| C_model_recoding | collapsed | 40 | 38/40 (95%) | 0.92 | [0.79, 1.00] | 0.93 |
| C_model_recoding | strict_labels | 40 | 33/40 (82%) | 0.74 | [0.58, 0.89] | 0.79 |
| C_model_recoding | collapsed_excl_NA_agree_by_construction | 35 | 33/35 (94%) | 0.90 | [0.73, 1.00] | 0.92 |
| C_model_recoding | presence(yes/conditional vs not_observed) | 35 | 35/35 (100%) | 1.00 | [1.00, 1.00] | 1.00 |
| ADJ_adjudicated | collapsed | 40 | 33/40 (82%) | 0.75 | [0.57, 0.89] | 0.77 |
| ADJ_adjudicated | strict_labels | 40 | 28/40 (70%) | 0.59 | [0.42, 0.76] | 0.64 |
| ADJ_adjudicated | collapsed_excl_NA_agree_by_construction | 35 | 28/35 (80%) | 0.68 | [0.47, 0.86] | 0.73 |
| ADJ_adjudicated | presence(yes/conditional vs not_observed) | 35 | 35/35 (100%) | 1.00 | [1.00, 1.00] | 1.00 |

`collapsed_excl_NA_agree_by_construction` drops the cells where both codes are `not_applicable` (Meta, 5 cells), which agree by construction and inflate raw agreement. `presence` is a coarser yes/conditional-vs-absent view that removes the yes/conditional boundary.

**Per-field agreement (collapsed scheme; n = 8 per field, CIs very wide)**

| field | A_first_pass | B_second_model_coder | C_model_recoding | ADJ_adjudicated |
|---|---|---|---|---|
| model_retirement_notice_days | 5/8; k=0.31 [0.00,0.78]; PABAK=0.50 | 7/8; k=0.00 [0.00,0.00]; PABAK=0.83 | 7/8; k=0.62 [0.00,1.00]; PABAK=0.83 | 6/8; k=0.43 [0.00,1.00]; PABAK=0.67 |
| export_right_affirmative | 5/8; k=0.51 [0.11,0.82]; PABAK=0.50 | 4/8; k=0.16 [-0.30,0.62]; PABAK=0.33 | 8/8; k=1.00 [1.00,1.00]; PABAK=1.00 | 8/8; k=1.00 [1.00,1.00]; PABAK=1.00 |
| termination_for_convenience_customer | 7/8; k=0.83 [0.44,1.00]; PABAK=0.83 | 3/8; k=0.02 [-0.09,0.24]; PABAK=0.17 | 8/8; k=1.00 [1.00,1.00]; PABAK=1.00 | 7/8; k=0.83 [0.44,1.00]; PABAK=0.83 |
| notice_days_price_change | 7/8; k=0.80 [0.43,1.00]; PABAK=0.83 | 3/8; k=0.07 [-0.33,0.44]; PABAK=0.17 | 8/8; k=1.00 [1.00,1.00]; PABAK=1.00 | 8/8; k=1.00 [1.00,1.00]; PABAK=1.00 |
| notice_days_material_terms | 3/8; k=0.29 [0.00,0.64]; PABAK=0.17 | 4/8; k=0.00 [-0.33,0.29]; PABAK=0.33 | 7/8; k=0.75 [0.00,1.00]; PABAK=0.83 | 4/8; k=0.36 [0.00,0.75]; PABAK=0.33 |

**Per-category (one-vs-rest, collapsed scheme, pooled over fields).** `pos.agree` = 2*both/(author n + comp n).

| author code | A_first_pass | B_second_model_coder | C_model_recoding | ADJ_adjudicated |
|---|---|---|---|---|
| yes | pos.agree=0.40; raw=0.70; k=0.29 (author n=4, comp n=16, both=4) | pos.agree=0.40; raw=0.85; k=0.32 (author n=4, comp n=6, both=2) | pos.agree=0.80; raw=0.95; k=0.77 (author n=4, comp n=6, both=4) | pos.agree=0.53; raw=0.82; k=0.45 (author n=4, comp n=11, both=4) |
| conditional | pos.agree=0.58; raw=0.68; k=0.38 (author n=22, comp n=9, both=9) | pos.agree=0.72; raw=0.68; k=0.33 (author n=22, comp n=25, both=17) | pos.agree=0.95; raw=0.95; k=0.90 (author n=22, comp n=20, both=20) | pos.agree=0.81; raw=0.82; k=0.66 (author n=22, comp n=15, both=15) |
| not_observed | pos.agree=0.95; raw=0.97; k=0.93 (author n=9, comp n=10, both=9) | pos.agree=0.22; raw=0.65; k=-0.00 (author n=9, comp n=9, both=2) | pos.agree=1.00; raw=1.00; k=1.00 (author n=9, comp n=9, both=9) | pos.agree=1.00; raw=1.00; k=1.00 (author n=9, comp n=9, both=9) |
| not_applicable | pos.agree=1.00; raw=1.00; k=1.00 (author n=5, comp n=5, both=5) | pos.agree=0.00; raw=0.88; k=0.00 (author n=5, comp n=0, both=0) | pos.agree=1.00; raw=1.00; k=1.00 (author n=5, comp n=5, both=5) | pos.agree=1.00; raw=1.00; k=1.00 (author n=5, comp n=5, both=5) |

**Source document and numeric days.** Same source document chosen (author source id = pass source id): A_first_pass 30/40; B_second_model_coder 29/40; C_model_recoding 28/40. Different captures of the same provider (live vs archived) explain some code differences, so those pairs test the version choice, not just the reading.

| comparison | author_gave_days | comp_gave_days | both_gave | equal_when_both | only_author | only_comp |
|---|---|---|---|---|---|---|
| A_first_pass | 15 | 13 | 12 | 12 | 3 | 1 |
| B_second_model_coder | 15 | 15 | 8 | 8 | 7 | 7 |
| C_model_recoding | 15 | 16 | 15 | 15 | 0 | 1 |

### 1.2 South Africa tenders (14 assessable of 20 documents)

The author could code 14 of 20 documents. The other 6 (S02, S03, S05, S13, S15, S16) had empty text extractions in the author's texts (S05: text is a different tender, B/SM 99/24, than the sheet's B/SM 97/24), so no author code exists. The model coding for five of those (S02, S03, S13, S15, S16) came from OCR text the author was not given; they cannot be compared and are excluded, not counted as disagreements.

| field | n | exact agreement | kappa | 95% CI | PABAK | weighted kappa (linear) | modal share author/model | boot valid |
|---|---|---|---|---|---|---|---|---|
| all_5_fields_raw_agreement_only | 70 | 55/70 (79%) | n/a | [n/a, n/a] | n/a | n/a | 0.43/0.51 |  |
| ordinal_fields_pooled(exit,data,financing) | 42 | 31/42 (74%) | 0.29 | [0.06, 0.51] | 0.61 | 0.35 | 0.71/0.86 | 2000 |
| exit_transition | 14 | 9/14 (64%) | 0.38 | [0.09, 0.72] | 0.46 | 0.44 | 0.50/0.71 | 1999 |
| data_return_export | 14 | 12/14 (86%) | 0.28 | [0.00, 0.48] | 0.79 | 0.34 | 0.93/0.86 | 1759 |
| financing_alternative | 14 | 10/14 (71%) | 0.00 | [0.00, 0.00] | 0.57 | 0.00 | 0.71/1.00 | 1981 |
| buyer_consent_to_changes | 14 | 11/14 (79%) | 0.66 | [0.30, 1.00] | 0.68 | n/a | 0.64/0.43 | 2000 |
| incorporates_GCC | 14 | 13/14 (93%) | 0.84 | [0.44, 1.00] | 0.86 | n/a | 0.71/0.64 | 1994 |

Coarser views (robustness):

| field | scheme | n | exact agreement | kappa | 95% CI | PABAK |
|---|---|---|---|---|---|---|
| exit_transition | presence(mentioned/specified vs none) | 14 | 11/14 (79%) | 0.57 | [0.17, 1.00] | 0.57 |
| data_return_export | presence(mentioned/specified vs none) | 14 | 13/14 (93%) | 0.63 | [0.00, 1.00] | 0.86 |
| financing_alternative | presence(mentioned/specified vs none) | 14 | 10/14 (71%) | 0.00 | [0.00, 0.00] | 0.43 |
| buyer_consent_to_changes | presence(consent by any route vs silent) | 14 | 14/14 (100%) | 1.00 | [1.00, 1.00] | 1.00 |

Kappa is undefined (n/a) when one coder's marginal is constant and equals the other's chance expectation; report raw agreement and PABAK in that case. Per-category one-vs-rest rows are in `agreement_sa.csv`. Confusion tables are in section 2.

### 1.3 Colombia SECOP II contracts (50 rows, 6 categories)

| comparison | scheme | n | exact agreement | kappa | 95% CI | PABAK | note |
|---|---|---|---|---|---|---|---|
| first_pass_model | 6_categories | 50 | 46/50 (92%) | 0.90 | [0.80, 0.97] | 0.90 |  |
| second_model_blind | 6_categories | 50 | 39/50 (78%) | 0.73 | [0.58, 0.87] | 0.74 |  |
| model_vs_model_same50 | 6_categories | 50 | 39/50 (78%) | 0.73 | [0.58, 0.87] | 0.74 | NOT human validation |
| model_vs_model_all100 | 6_categories | 100 | 74/100 (74%) | 0.68 | [0.58, 0.78] | 0.69 | NOT human validation; n=100 sample incl. these 50 |
| first_pass_model | 4_groups(product+dev merged; incidental+unclear merged) | 50 | 47/50 (94%) | 0.91 | [0.81, 1.00] | 0.92 | robustness only; merges are post hoc |
| second_model_blind | 4_groups(product+dev merged; incidental+unclear merged) | 50 | 41/50 (82%) | 0.74 | [0.59, 0.89] | 0.76 | robustness only; merges are post hoc |

**Per-category (author category vs each model coding; one-vs-rest)**

| category | first_pass_model | second_model_blind |
|---|---|---|
| ai_product_or_platform | pos.agree=0.96; k=0.95 [0.82,1.00] (author n=13, comp n=14, both=13) | pos.agree=0.92; k=0.90 [0.73,1.00] (author n=13, comp n=13, both=12) |
| ai_development_service | pos.agree=1.00; k=1.00 [1.00,1.00] (author n=9, comp n=9, both=9) | pos.agree=0.78; k=0.73 [0.45,0.94] (author n=9, comp n=9, both=7) |
| cloud_or_software_nonAI | pos.agree=0.96; k=0.94 [0.79,1.00] (author n=12, comp n=11, both=11) | pos.agree=0.80; k=0.75 [0.47,0.94] (author n=12, comp n=8, both=8) |
| individual_professional_ai | pos.agree=0.94; k=0.93 [0.74,1.00] (author n=8, comp n=9, both=8) | pos.agree=0.82; k=0.79 [0.50,1.00] (author n=8, comp n=9, both=7) |
| incidental | pos.agree=0.67; k=0.62 [0.18,0.91] (author n=7, comp n=5, both=4) | pos.agree=0.59; k=0.51 [0.13,0.79] (author n=7, comp n=10, both=5) |
| unclear | pos.agree=0.67; k=0.66 [0.00,1.00] (author n=1, comp n=2, both=1) | pos.agree=0.00; k=-0.02 [-0.05,0.00] (author n=1, comp n=1, both=0) |

## 1.4 Provenance question for the lead (independence of the human codes)

- The author's supplier-terms sheet records `minutes_spent` totalling 87 minutes for 40 cells (the sheet's own instructions estimate 2-4 hours). The author's evidence notes are fluent, clause-cited prose of the same style as the model recoding's notes, and the author's numeric days equal the recoding pass's in 15 of 15 cells where both give a number.
- Agreement with the model recoding (C) is 95% (kappa 0.92), against 68% with the first pass (A) and 52% with the second coder (B), although the recoding pass disagreed with A on 16 of 40 cells. This pattern is *consistent with* the author's codes being independent and the recoding being the most careful reading, but it is *also* what would be seen if the sheet were drafted or pre-filled with model assistance. Nothing in the files can distinguish these. **The lead should confirm that the author coded the sheets unaided before this is described as an independent human check.** The SA and SECOP sheets carry the same style of notes (e.g. tender-ID mismatch and empty-extraction notes for SA).

## 2. Confusion tables (rows = author, columns = comparison coding)

### 2.1 Supplier terms, collapsed scheme, pooled over 5 fields

**A_first_pass**

| author | yes | conditional | not_observed | not_applicable |
|---|---|---|---|---|
| yes | 4 | 0 | 0 | 0 |
| conditional | 12 | 9 | 1 | 0 |
| not_observed | 0 | 0 | 9 | 0 |
| not_applicable | 0 | 0 | 0 | 5 |

**B_second_model_coder**

| author | yes | conditional | not_observed | not_applicable |
|---|---|---|---|---|
| yes | 2 | 2 | 0 | 0 |
| conditional | 2 | 17 | 3 | 0 |
| not_observed | 2 | 5 | 2 | 0 |
| not_applicable | 0 | 1 | 4 | 0 |

**C_model_recoding**

| author | yes | conditional | not_observed | not_applicable |
|---|---|---|---|---|
| yes | 4 | 0 | 0 | 0 |
| conditional | 2 | 20 | 0 | 0 |
| not_observed | 0 | 0 | 9 | 0 |
| not_applicable | 0 | 0 | 0 | 5 |

**ADJ_adjudicated**

| author | yes | conditional | not_observed | not_applicable |
|---|---|---|---|---|
| yes | 4 | 0 | 0 | 0 |
| conditional | 7 | 15 | 0 | 0 |
| not_observed | 0 | 0 | 9 | 0 |
| not_applicable | 0 | 0 | 0 | 5 |

Strict-label tables (with `no_in_read_document`) are in `confusion_supplier_terms.csv`.

### 2.2 South Africa (n = 14 documents per field)

**exit_transition**

| author | none | mentioned | specified |
|---|---|---|---|
| none | 7 | 0 | 0 |
| mentioned | 3 | 2 | 2 |
| specified | 0 | 0 | 0 |

**data_return_export**

| author | none | mentioned | specified |
|---|---|---|---|
| none | 12 | 0 | 1 |
| mentioned | 0 | 0 | 0 |
| specified | 0 | 1 | 0 |

**financing_alternative**

| author | none | mentioned | specified |
|---|---|---|---|
| none | 10 | 0 | 0 |
| mentioned | 4 | 0 | 0 |
| specified | 0 | 0 | 0 |

**buyer_consent_to_changes**

| author | silent | only_via_GCC | required_own_text |
|---|---|---|---|
| silent | 4 | 0 | 0 |
| only_via_GCC | 0 | 6 | 3 |
| required_own_text | 0 | 0 | 1 |

**incorporates_GCC**

| author | no | yes |
|---|---|---|
| no | 4 | 0 |
| yes | 1 | 9 |

### 2.3 SECOP (n = 50)

**author vs first_pass_model**

| author | ai_product_or_platform | ai_development_service | cloud_or_software_nonAI | individual_professional_ai | incidental | unclear |
|---|---|---|---|---|---|---|
| ai_product_or_platform | 13 | 0 | 0 | 0 | 0 | 0 |
| ai_development_service | 0 | 9 | 0 | 0 | 0 | 0 |
| cloud_or_software_nonAI | 0 | 0 | 11 | 0 | 1 | 0 |
| individual_professional_ai | 0 | 0 | 0 | 8 | 0 | 0 |
| incidental | 1 | 0 | 0 | 1 | 4 | 1 |
| unclear | 0 | 0 | 0 | 0 | 0 | 1 |

**author vs second_model_blind**

| author | ai_product_or_platform | ai_development_service | cloud_or_software_nonAI | individual_professional_ai | incidental | unclear |
|---|---|---|---|---|---|---|
| ai_product_or_platform | 12 | 1 | 0 | 0 | 0 | 0 |
| ai_development_service | 1 | 7 | 0 | 0 | 0 | 1 |
| cloud_or_software_nonAI | 0 | 0 | 8 | 0 | 4 | 0 |
| individual_professional_ai | 0 | 0 | 0 | 7 | 1 | 0 |
| incidental | 0 | 0 | 0 | 2 | 5 | 0 |
| unclear | 0 | 1 | 0 | 0 | 0 | 0 |

## 3. Method and label mapping

### 3.1 Supplier terms

- Author sheet `1_Supplier_terms_40cells_DONE.xlsx` (Coding tab, column `your_code`; also `numeric_days`, `source_id`, `clause_locator`, `evidence_note`). Key = (provider, field); cell ids H01-H40.
- Comparison codings, all keyed on (provider, field), 40/40 matched one-to-one: **A_first_pass** = `code_A` in `SUPPLIER_TERMS_V2/TERMS_V2_TABLE.csv` (= `manual_codes.csv`, the frozen rule-based first pass); **B_second_model_coder** = `code_B` (same table; extraction run against pass A's source ids); **C_model_recoding** = `pass_c/pass_c_codes.csv` (`code`, produced blind to A/B per its own readout); **ADJ_adjudicated** = `pass_c/adjudicated_codes.csv` (`adjudicated_code`, resolves A vs C after the fact).
- Author dropdown labels: `yes`, `conditional`, `not_observed`, `not_applicable`. Model files add `no_in_read_document` (a full read of the identified document found no qualifying clause; A: 0, B: 2, C: 5, adjudicated: 5 cells). **Mapping used for the primary scheme: `no_in_read_document` -> `not_observed`**, because the author's dropdown has no separate label and the author's instruction defines `not_observed` as no qualifying clause in the captured sources. **This is a judgement call, flagged as ambiguous:** the codebook distinguishes 'no clause in a fully read document' from 'missing/excerpted text'; the author could not record that distinction. The strict scheme (no mapping, so every `not_observed` vs `no_in_read_document` pair is a disagreement) is reported alongside.
- `ambiguous` is in the model codebook but is never used by any pass; `not_applicable` (Meta, 5 cells) is used identically by author and all passes.
- Kappa uses the pooled 40-cell marginals (or 8-cell per-field marginals); the same-source diagnostic compares source ids as recorded.

### 3.2 South Africa

- Author sheet `2_South_Africa_tenders_20docs_DONE.xlsx` (sid S01-S20). Row-key mapping: the *blind* sheet `evidence_b/human_coding/SA_H_blind_sheet.xlsx` gives `local_text_file` = `sa_etenders/sa_txt/<ocid>__<doc-uuid>.txt` for each sid (the DONE sheet's paths were renamed to `reference/sa_tender_texts/Sxx.txt`; file bytes were checked identical to the model corpus for the 14 comparable documents and S11 comes from the OCR folder in both). That basename is the `doc` key of `sa_clauses_llm_v2.csv`; 20/20 join one-to-one.
- Model coding: `sa_clauses_llm_v2.csv` (first-pass). The earlier `sa_clauses_llm_v1.csv` covers 14 of the 20 sheet documents and is identical to v2 on every shared document for the compared fields, so it is not reported separately (it would repeat the same numbers). No second model pass and no adjudication exist for this set.
- Label mapping: `exit_transition`, `data_return_export`, `financing_alternative`: author {none, mentioned} vs model {none, mentioned, specified} share the same ordered labels (none < mentioned < specified); the author never used `specified` for exit or financing, and used it once for data return. Linear-weighted kappa is given as a supplement.
- `incorporates_GCC` (yes/no) <-> model `gcc_incorporated` (True/False).
- **`buyer_consent_to_changes` needs a derived model label (ambiguous mapping, flagged).** Author labels: `silent`, `only_via_GCC`, `required_own_text`. The model has two fields: `supplier_change_of_terms` (own-text reading: `silent` / `buyer_consent_required`) and `eff_change_of_terms`, which adds the GCC clause 18.1 effect (`buyer_consent_required(GCC18.1)`). Mapping used: model `supplier_change_of_terms = buyer_consent_required` -> `required_own_text`; else `eff_change_of_terms` starting `buyer_consent_required(GCC` -> `only_via_GCC`; else `silent`. Only `silent` and `buyer_consent_required` occur among the 14 documents (`notice_only`/`supplier_unilateral` would have raised an error). A consent-by-any-route binary view removes the own-text/GCC distinction.
- The model's `incorporates_by_reference` (broader than GCC) has no author counterpart and is not compared. Author `financing_alternative=mentioned` was compared with the model raw field, not the `eff_financing_alt` variant (which credits GCC 23.2 default replacement; author's sheet did not).

### 3.3 SECOP

- Author sheet `3_Colombia_contracts_50rows_DONE.xlsx`, key `vid` (V001-V100 sample ids). The blind sheet `SECOP_H_blind_sheet.xlsx` has identical vid order and identical (500-character-truncated) `contract_object (Spanish)` text. `vid -> id_contrato` comes from the SECOP validation file in `evidence_b/secop/` (`VALIDATION_*_vs_*.csv`, 100 rows); 50/50 join, and the first-pass model code in that file equals `llm_category` in `secop_classified_v1.csv` for all 50 (asserted).
- Comparison codings: **first_pass_model** (`llm_category`/validation `llm` column) and **second_model_blind** (the validation file's blind second-coder column). Labels are identical across author and both model codings (6 categories: ai_product_or_platform, ai_development_service, cloud_or_software_nonAI, individual_professional_ai, incidental, unclear), so no mapping was needed. Note the author saw only the first 500 characters of the object text; the first-pass model may have seen the full text.
- Model-vs-model agreement on the same 50 and on all 100 is reported for context only.

### 3.4 Statistics

Exact agreement = share of identical codes. Cohen's kappa (unweighted, two coders, categories = union of observed labels for the scheme). Bootstrap: 2000 resamples of coded units with replacement, seed 20260930, percentile 2.5/97.5; resamples where kappa is undefined are dropped and their number reported (`boot_valid` in the CSVs); if fewer than 20 valid, CI = n/a. PABAK = (k*p_o - 1)/(k - 1) with k the number of categories in the scheme (4 for collapsed supplier terms, 3 for ordinal SA fields, 6 for SECOP). Pooled 'ALL' rows treat cells as independent, which they are not (providers and fields cluster), so their CIs are optimistic.

## 4. Disagreements for adjudication

### 4.1 Supplier terms (collapsed scheme; full text in `disagreements_supplier_terms.csv`)

Side-by-side view: one row per cell where the author differs from at least one pass (author / A / B / C / adjudicated; `nio` = `no_in_read_document`). Author evidence and each pass's clause are in the CSV.

| cell | provider / field | author | A | B | C | adjudicated | author src / locator | author evidence |
|---|---|---|---|---|---|---|---|---|
| H02 | OpenAI / export_right_affirmative | conditional | yes | conditional | conditional | conditional | p1_dpa_latest / §2.11 Data Return or Deletion | After expiry or termination, OpenAI will return or delete Customer Data at Customer instruction, subject to legally required retention. Return requires instruction; no post-termination request window or format is stated. |
| H03 | OpenAI / termination_for_convenience_customer | not_observed | not_observed | conditional | nio | nio | p1_business_latest / §§1.2, 11.2–11.3, 16.13 | The captured agreement provides non-renewal, cause-based termination and specified exits after provider changes, but no general customer right to terminate without cause; minimum commitments can be non-cancellable. |
| H05 | OpenAI / notice_days_material_terms | conditional | yes | conditional | conditional | yes | p1_business_latest / §16.13(a)–(b) Updates | If OpenAI decides an update materially affects rights or obligations, it gives at least 30 days before effectiveness; compliance changes get as much notice as reasonably possible. Posting can be notice; customer may stop using or… |
| H06 | Anthropic / model_retirement_notice_days | conditional | yes | conditional | yes | yes | p2_lifecycle_live / Notification / retirement policy | Lifecycle documentation promises at least 60 days before retirement for publicly released models to customers with active deployments. Partner-operated Bedrock and Google Cloud set separate schedules; documentation only. |
| H07 | Anthropic / export_right_affirmative | conditional | yes | conditional | conditional | conditional | p2_dpa_latest / §H.1(a)–(b) Deletion and Return | Within 30 days after termination/expiry, Customer must request return of a copy of Customer Data or use available self-service return. Deletion follows, with legal/dispute/harmful-use exceptions; no weights or model replacement r… |
| H08 | Anthropic / termination_for_convenience_customer | yes | yes | conditional | yes | yes | p2_business_latest / §I.2(a) Termination | Each party may terminate for convenience with Notice at any time. The 30-day prior-Notice requirement applies to Anthropic, not Customer; accrued fees remain. |
| H09 | Anthropic / notice_days_price_change | conditional | yes | not_observed | conditional | conditional | p2_business_latest / §H.1 Payment of Fees | Published model rates update effective at the earlier of 30 days after posting or when Customer otherwise receives Notice. The latter can shorten actual lead time; marketplace rates have analogous service-specific language. |
| H10 | Anthropic / notice_days_material_terms | conditional | yes | not_observed | conditional | conditional | p2_business_latest / §M.3 Amendment and Modification | Terms updates become effective 30 days after posting or Customer receipt of Notice, whichever is earlier; law/regulation changes can take effect immediately. No specific objection right is stated beyond convenience termination. |
| H11 | Google / model_retirement_notice_days | conditional | not_observed | conditional | conditional | conditional | p3_lifecycle_live / Models available for shorter availability periods | Vertex AI model-version page says a posted fixed retirement date gives at least 45 days to migrate for shorter-availability models. Other models list retirement dates and may have different availability; documentation only. |
| H12 | Google / export_right_affirmative | conditional | yes | yes | conditional | conditional | p3_dpa_live / §§6.2, 9.1 Access; Data Export | During the term Google enables Customer to export Customer Data consistent with service functionality; Customer can instruct return before term ends. The DPA does not give an unrestricted post-term export window. |
| H13 | Google / termination_for_convenience_customer | conditional | yes | conditional | conditional | yes | p3_business_live / §8.5 Termination for Convenience | Customer may terminate at any time on prior written notice, subject to financial commitments in an Order Form/addendum; stopping use alone does not cancel those commitments. |
| H14 | Google / notice_days_price_change | not_observed | not_observed | yes | nio | nio | p3_business_live / §2.6 Fee Revisions | For GCP/Vertex AI, Google may change Fees at any time; the explicit 30-day advance notice and renewal-only pricing apply to GWS, Looker and Cloud Identity, not this GCP surface. |
| H15 | Google / notice_days_material_terms | conditional | yes | conditional | conditional | yes | p3_business_live / §1.4(b)–(c) Updates to Agreement/URL Terms | Material GCP agreement and URL-term updates usually take effect 30 days after posting. New functionality and legal-compliance updates may be immediate; customer may stop use or terminate for convenience. |
| H16 | Microsoft Azure OpenAI / model_retirement_notice_days | conditional | yes | conditional | conditional | yes | p4_lifecycle_live / GA model retirement notice; Preview model retirement notice | Model lifecycle documentation states at least 60 days notice for GA model retirement and 30 days for previews, with shorter emergency retirement possible for security/compliance. GA 18-month life is a separate measure; this is do… |
| H17 | Microsoft Azure OpenAI / export_right_affirmative | not_observed | not_observed | conditional | not_observed | not_observed | p4_business_2024; p4_service_2024 / MCA licensing-document landing page; Azure Product Terms, D… | The supplied MCA capture is a document landing page, not agreement text. Azure Product Terms mention paid hosting in an Extended Term but do not grant an affirmative Customer Data export right in the captured text; DPA unavailabl… |
| H18 | Microsoft Azure OpenAI / termination_for_convenience_customer | not_observed | not_observed | conditional | not_observed | not_observed | p4_business_2024; p4_service_2024 / MCA licensing-document landing page; Azure Product Terms | No customer convenience-termination clause is captured. Azure reservation cancellation rules concern reserved capacity, not general Azure OpenAI subscription termination; MCA body was not captured. |
| H20 | Microsoft Azure OpenAI / notice_days_material_terms | not_observed | not_observed | conditional | not_observed | not_observed | p4_business_2024; p4_service_2024 / MCA licensing-document landing page; Azure Product Terms | Captured MCA landing page does not contain legal amendment clauses. Product Terms discuss service-feature retirement, which is not notice of material legal-term changes. |
| H22 | AWS Bedrock / export_right_affirmative | conditional | conditional | not_observed | conditional | conditional | p5_business_live / §5.3(b) Post-Termination | For 30 days after termination AWS allows retrieval of Your Content only if all amounts due are paid; this window does not apply after termination for cause under §5.2(b). Content is not model weights. |
| H23 | AWS Bedrock / termination_for_convenience_customer | yes | yes | conditional | yes | yes | p5_business_live / §5.2(a) Termination for Convenience | Customer may terminate for any reason by giving notice and closing accounts where AWS provides an account-closing mechanism. Charges incurred through termination remain due. |
| H26 | Meta / model_retirement_notice_days | not_applicable | not_applicable | conditional | not_applicable | not_applicable | meta_llama_2026 / Preamble; §1 Grant of Rights | Captured document licenses downloadable Llama 2 materials and weights; there is no hosted API model-version retirement service to which notice days apply. |
| H27 | Meta / export_right_affirmative | not_applicable | not_applicable | nio | not_applicable | not_applicable | meta_llama_2026 / §1 Grant of Rights | Open-weight license grants use, reproduction and distribution of Llama Materials; it is not hosted storage of customer prompts/outputs requiring a customer-data export clause. |
| H28 | Meta / termination_for_convenience_customer | not_applicable | not_applicable | nio | not_applicable | not_applicable | meta_llama_2026 / §6 Term and Termination | This is a downloaded-weights license, not a hosted API purchasing relationship. §6 addresses Meta termination for breach and licensee deletion on termination; customer service convenience exit is not comparable. |
| H29 | Meta / notice_days_price_change | not_applicable | not_applicable | not_observed | not_applicable | not_applicable | meta_llama_2026 / §1 Grant of Rights; §2 Additional Commercial Terms | Royalty-free Llama 2 weight license has no ongoing hosted-service prices to increase; larger licensees may need a separate negotiated license. |
| H30 | Meta / notice_days_material_terms | not_applicable | not_applicable | not_observed | not_applicable | not_applicable | meta_llama_2026 / Preamble; §6 Term and Termination | The captured weight license is not a hosted API legal-terms update regime; no customer service amendment notice can be compared. |
| H34 | Mistral / notice_days_price_change | not_observed | not_observed | conditional | nio | nio | p7_business_live / §10.1 Pricing; §13 Updates to Terms | Pricing is on a pricing page unless an Order Form says otherwise. Captured terms give 30-day notice for material legal-term updates but no explicit lead time for an increase in customer charges. |
| H35 | Mistral / notice_days_material_terms | conditional | yes | conditional | yes | yes | p7_business_live / §§13.2–13.4 Updates to Terms | Material legal-term updates are notified by email or account notice and become effective 30 days later. Nonmaterial, legal-compliance and material-security changes can be immediate; customer may exit before effect. |
| H39 | Alibaba Cloud Model Studio / notice_days_price_change | not_observed | not_observed | yes | nio | nio | p8_business_live; p8_service_live / Membership Agreement §6.3; Product Terms Singapore Addendum | General fees may update and take effect upon publication, with no advance window for Model Studio. The product addendum gives reasonable advance notice only for ECS/VPC/SLB/CDN customers, expressly excluding other products. |
| H40 | Alibaba Cloud Model Studio / notice_days_material_terms | conditional | yes | yes | conditional | yes | p8_business_live / §1.2 Modification of Terms | Material legal changes generally take effect 15 days after posting. New services/functions, legal-compliance changes, or Alibaba-specified dates may take effect immediately/otherwise; posting is the notice channel. |

28 of 40 cells differ from at least one pass; against adjudicated: 7 cells; against A: 13; B: 19; C: 2.

Pass B (second model coder) coded all five Meta cells (open-weight licence, not a hosted API) as `conditional`/`not_observed`/`no_in_read_document` rather than `not_applicable`; the author, pass A and pass C agree on `not_applicable`. The largest author-vs-A pattern is 12 cells where the author is `conditional` and A is `yes`: A treated a general rule with exceptions as `yes`, the author and C as `conditional`; the adjudication set 7 of the author's `conditional` cells to `yes`, and those 7 are the author-vs-adjudicated disagreements that remain (all on the yes/conditional boundary, not presence vs absence: on the presence view author and adjudicated agree on 35/35).

Full-text pass clauses and notes for each of these pairs, and whether the author and the pass used the same source document, are in the CSV (`same_source_document`).

### 4.2 South Africa (all disagreements, n = 15)

| sid | field | author_code | model_code | author_note | model_quote |
|---|---|---|---|---|---|
| S08 | exit_transition | mentioned | none | “Migrate the current solution to cloud” includes data/integration points; pricing lists “Migration to Cloud.” This is incoming implementation, not a promise by the new supplier to return data or fund a later exit. |  |
| S09 | exit_transition | mentioned | specified | New provider must take over from incumbent with knowledge transfer, documentation and continuity. The duty is inbound; no later exit, data return/export or separate alternative funding is specified. | The appointed service provider must be able to transfer roles and responsibilities and take over ownership from the current service provider in a smooth manner, without disrupting the day-to-day activities of the FAIS Ombud. |
| S12 | exit_transition | mentioned | none | Year 3 table asks bidders to price “Migration Plan (Implementation Cost).” The annex gives no migration duties, committed budget, data export or consent rule; direction and purpose of migration remain unclear. |  |
| S14 | exit_transition | mentioned | specified | CSP must move existing workloads and database data to the new platform in at most three months; bid includes once-off migration costs. This is inbound migration, not new-supplier exit/data-return duty or committed fallback funding. | Transnet requires a transition period of 3 months to move from one data centre to another. The CSP will be required to migrate existing workloads from the current public platform utilized by Transnet to the new platform |
| S17 | exit_transition | mentioned | none | Bid must price “Tenant transfer costs” and propose inbound migration; no later exit or funded fallback is assured. ToR §5.5 requires agreement for additional servers only; general amendment control comes through GCC §18.1. |  |
| S07 | data_return_export | specified | mentioned | Cloud archiving requires “retention, legal hold, case management, and data export.” This is an export feature, with no express exit assistance or separate replacement funding. | Comprehensive compliance, E-discovery, and litigation support, including retention, legal hold, case management, and data export. |
| S20 | data_return_export | none | specified | Evaluation asks for “a plan for handover/knowledge transfer.” ToR §5.13 bars amendment without EWSETA CEO written confirmation; no buyer data return or separate fallback funding is specified. | Any document, other than the contract itself mentioned in GCC clause 5.1 shall remain the property of the purchaser and shall be returned (all copies) to the purchaser on completion of the supplier’s performance under the contract if so required by the purcha… |
| S08 | financing_alternative | mentioned | none | “Migrate the current solution to cloud” includes data/integration points; pricing lists “Migration to Cloud.” This is incoming implementation, not a promise by the new supplier to return data or fund a later exit. |  |
| S12 | financing_alternative | mentioned | none | Year 3 table asks bidders to price “Migration Plan (Implementation Cost).” The annex gives no migration duties, committed budget, data export or consent rule; direction and purpose of migration remain unclear. |  |
| S14 | financing_alternative | mentioned | none | CSP must move existing workloads and database data to the new platform in at most three months; bid includes once-off migration costs. This is inbound migration, not new-supplier exit/data-return duty or committed fallback funding. |  |
| S17 | financing_alternative | mentioned | none | Bid must price “Tenant transfer costs” and propose inbound migration; no later exit or funded fallback is assured. ToR §5.5 requires agreement for additional servers only; general amendment control comes through GCC §18.1. |  |
| S07 | buyer_consent_to_changes | only_via_GCC | required_own_text | Cloud archiving requires “retention, legal hold, case management, and data export.” This is an export feature, with no express exit assistance or separate replacement funding. | No variation in or modification of the terms of the contract shall be made except by written amendment signed by the parties concerned. |
| S08 | buyer_consent_to_changes | only_via_GCC | required_own_text | “Migrate the current solution to cloud” includes data/integration points; pricing lists “Migration to Cloud.” This is incoming implementation, not a promise by the new supplier to return data or fund a later exit. | No variation in or modification of the terms of the contract shall be made except by written amendment signed by the parties concerned. |
| S17 | buyer_consent_to_changes | only_via_GCC | required_own_text | Bid must price “Tenant transfer costs” and propose inbound migration; no later exit or funded fallback is assured. ToR §5.5 requires agreement for additional servers only; general amendment control comes through GCC §18.1. | “No variation in or modification of the terms of the contract shall be made except by written amendment signed by the parties concerned.” (GCC 18.1) |
| S07 | incorporates_GCC | yes | no | Cloud archiving requires “retention, legal hold, case management, and data export.” This is an export feature, with no express exit assistance or separate replacement funding. |  |

Notes for the lead. (a) `author_note` is the author's single note for the whole document, not per field; `model_quote` is blank when the model coded `none`. (b) The three `buyer_consent_to_changes` disagreements (S07, S08, S17) look definitional rather than reading errors: in each, the tender pack itself reproduces the full GCC text including clause 18.1 ("No variation in or modification of the terms of the contract ...", found in the supplied text at lines ~839, ~1575, ~2307), which the model counted as the document's own text (`required_own_text`) and the author counted as coming through the GCC (`only_via_GCC`). Under the consent-by-any-route view these three agree (14/14). Which label the paper wants is a codebook decision. (c) S07 `incorporates_GCC`: the supplied text states that the General Conditions of Contract 'will form part of all bid' documents and reproduces them, but the model has `gcc_incorporated = False`; the model looks wrong here. (d) The `mentioned` (author) vs `none` (model) financing/exit disagreements (S08, S12, S14, S17) are all cases where the author counted an inbound migration or migration-cost line as a 'mention' while the author's own note says it is not an exit duty or funded fallback; the author's notes and codes are in mild tension there, and the model's `none` matches the notes' reasoning. Please adjudicate against the codebook wording ('budget or obligation for second source, parallel run, in-house capacity, or transition funding').

**Documents the author could not assess (model coded from OCR text the author did not see; not compared):**

| sid | tender | author note | model exit/data/fin | model consent(eff) |
|---|---|---|---|---|
| S02 | LDE/B13/2026/27 | Text extraction contains only form feeds; clauses cannot be assessed from this source. | none/none/none | buyer_consent_required(GCC18.1) |
| S03 | DBAC04/05/2025-26 | Text extraction contains only form feeds; clauses cannot be assessed from this source. | mentioned/none/mentioned | silent |
| S05 | BSM 97/24 | Source identifies B/SM 99/24 throughout; workbook targets B/SM 97/24. No clause coding transferred across tender IDs. | none/none/none | buyer_consent_required |
| S13 | RFQ 534-09-2023  | Text extraction contains only a form feed; clauses cannot be assessed from this source. | none/none/none | silent |
| S15 | DSM 11/24 | Text extraction contains only form feeds; clauses cannot be assessed from this source. | mentioned/none/none | silent |
| S16 | SCM/BID 017/2025-26 | Text extraction contains only form feeds; clauses cannot be assessed from this source. | mentioned/none/none | silent |

### 4.3 SECOP (first-pass model vs author, then second model coder vs author)

**first_pass_model: 4 disagreements of 50**

| vid | author | first_pass_model | other model | supplier/contract type | object (as shown to author) | author note |
|---|---|---|---|---|---|---|
| V010 | incidental | ai_product_or_platform | incidental | firm / Compraventa | Adquisición de equipos especializados destinados a la modernización y fortalecimiento del ambiente de formación STEM; incluyendo componentes para robótica TXT; aplicaciones de inteligencia artificial y robots industriales; con el fin de garantizar el desarrollo de competencias tecnológicas en el Centro Internacional de Producci… | STEM equipment; AI applications are one component. |
| V054 | incidental | unclear | incidental | firm / Prestación de servicios | CONVENIO DE COOPERACION ENTRE EL MUNICIPIO DE GIRÓN Y CAMPUSLANDS S.A.S BIC; QUE BUSCA IMPLEMENTAR LA FORMACION Y CAPACITACIÓN DE PROGRAMAS TECNOLOGICOS DE ALTO NIVEL EN EL USO DE LA INTELIGENCIA ARTIFICIAL CON EL FIN DE CONVERTIR LA FORMACION EN EXPERIENCIA; INGRESOS Y PROYECCION PROFESIONAL PARA LOS JOVENES RESIDENTES DEL MUN… |  |
| V076 | cloud_or_software_nonAI | incidental | incidental | individual/other / Prestación de servicios | Contratar en nombre de la NACIÓN - CONSEJO SUPERIOR DE LA JUDICATURA - DIRECCIÓN EJECUTIVA SECCIONAL DE ADMINISTRACIÓN JUDICIAL DE TUNJA; la prestación de servicios de apoyo a la revisión y ajuste de expedientes digitalizados por los diferentes Despachos Judiciales para garantizar que se cumplan todos los requisitos técnicos y … |  |
| V037 | incidental | individual_professional_ai | individual_professional_ai | individual/other / Prestación de servicios | Prestar servicios de apoyo a la gestión para  diseñar y desarrollar el mecanismo de telecomunicación de un prototipo  basado en realidad aumentada e  inteligencia artificial para comercializar prendas de vestir según los exigido por el  proyecto de I+D+i SGPS 10879-2023 | Telecommunications mechanism for a broader AR/AI prototype. |

**second_model_blind: 11 disagreements of 50**

| vid | author | second_model_blind | other model | supplier/contract type | object (as shown to author) | author note |
|---|---|---|---|---|---|---|
| V042 | ai_product_or_platform | ai_development_service | ai_product_or_platform | firm / Consultoría | PARAMETRIZACIÓN; CONFIGURACIÓN; DESPLIEGUE Y PUESTA EN FUNCIONAMIENTO DE UNA PLATAFORMA TECNOLÓGICA CLOUD COMPUTING PARA LA GESTIÓN DIGITAL INTEGRAL DE LA COMISARÍA DE FAMILIA DE CAMPOALEGRE; INCORPORANDO TECNOLOGÍAS DE INTELIGENCIA ARTIFICIAL (IA); BAJO LA MODALIDAD DE SOFTWARE COMO SERVICIO (SAAS) |  |
| V075 | individual_professional_ai | incidental | individual_professional_ai | individual/other / Prestación de servicios | DSEC561 Prestar sus servicios profesionales especializados a la Dirección Técnica de Seguridad para la ejecución; análisis; desarrollo; soporte y mantenimiento de aplicaciones; herramientas e infraestructura tecnológica; incluyendo el apoyo en el diseño; entrenamiento e integración de modelos de inteligencia artificial aplicado… |  |
| V028 | unclear | ai_development_service | unclear | firm / Prestación de servicios | Llevar a cabo la estrategia de implementación; uso y adopción de inteligencia artificial -IA-; para los entornos de funcionamiento y misionales; incluyendo la definición de retos de ciudad; en La Agencia Distrital para la Educación la Ciencia y la Tecnología - Atenea | AI adoption strategy; no specific system or platform identified. |
| V056 | cloud_or_software_nonAI | incidental | cloud_or_software_nonAI | individual/other / Prestación de servicios | Contratar en nombre de la NACIÓN - CONSEJO SUPERIOR DE LA JUDICATURA - DIRECCIÓN EJECUTIVA SECCIONAL DE ADMINISTRACIÓN JUDICIAL DE TUNJA; la prestación de servicios de apoyo a la revisión y ajuste de expedientes digitalizados por los diferentes Despachos Judiciales para garantizar que se cumplan todos los requisitos técnicos y … |  |
| V073 | cloud_or_software_nonAI | incidental | cloud_or_software_nonAI | individual/other / Prestación de servicios | Contratar en nombre de la NACIÓN - CONSEJO SUPERIOR DE LA JUDICATURA - DIRECCIÓN EJECUTIVA SECCIONAL DE ADMINISTRACIÓN JUDICIAL DE TUNJA; la prestación de servicios de apoyo a la revisión y ajuste de expedientes digitalizados por los diferentes Despachos Judiciales para garantizar que se cumplan todos los requisitos técnicos y … |  |
| V097 | incidental | individual_professional_ai | incidental | individual/other / Prestación de servicios | Prestar servicios personales en desarrollo de modelos 3D; basados en prendas de vestir; los cuales serán integrados en el prototipo soportado en realidad aumentada e inteligencia artificial con el fin de comercializar prendas de vestir según lo exigido por el proyecto sennova de I+D+i SGPS 10879-2023; del Centro Industrial de M… | 3D garment models for a broader AR/AI prototype; no AI work specified. |
| V019 | ai_development_service | ai_product_or_platform | ai_development_service | firm / Decreto 092 de 2017 | PRESTACIÓN DEL SERVICIO PARA LA IMPLEMENTACIÓN DE UN SISTEMA DE AGENDAMIENTO AUTOMÁTICO DEL PROCESO DE CITAS MÉDICAS; INCLUYENDO EL ALMACENAMIENTO DE DATOS Y ARCHIVOS EN LA NUBE; UTILIZANDO TECNOLOGÍAS AVANZADAS Y MECANISMOS DE INTELIGENCIA ARTIFICIAL; PARA FORTALECER LA ATENCIÓN A LOS USUARIOS DE LA ESE HUS |  |
| V076 | cloud_or_software_nonAI | incidental | incidental | individual/other / Prestación de servicios | Contratar en nombre de la NACIÓN - CONSEJO SUPERIOR DE LA JUDICATURA - DIRECCIÓN EJECUTIVA SECCIONAL DE ADMINISTRACIÓN JUDICIAL DE TUNJA; la prestación de servicios de apoyo a la revisión y ajuste de expedientes digitalizados por los diferentes Despachos Judiciales para garantizar que se cumplan todos los requisitos técnicos y … |  |
| V081 | cloud_or_software_nonAI | incidental | cloud_or_software_nonAI | individual/other / Prestación de servicios | Contratar la prestación de servicios para la verificación de los expedientes digitalizados por la UT CSJ NX-DF en cuanto a calidad y cumplimiento de los requerimientos técnicos y funcionales definidos en el protocolo para la gestión de documentos electrónicos y que se encuentran cargados en Azure y Gestor Documental-BestDoc en … |  |
| V037 | incidental | individual_professional_ai | individual_professional_ai | individual/other / Prestación de servicios | Prestar servicios de apoyo a la gestión para  diseñar y desarrollar el mecanismo de telecomunicación de un prototipo  basado en realidad aumentada e  inteligencia artificial para comercializar prendas de vestir según los exigido por el  proyecto de I+D+i SGPS 10879-2023 | Telecommunications mechanism for a broader AR/AI prototype. |
| V059 | ai_development_service | unclear | ai_development_service | individual/other / Prestación de servicios | Contratar los servicios para la gestión integral de datos que incluya el análisis; diseño; desarrollo; implementación; puesta en producción; así como gobierno y arquitectura de información; utilizando herramientas tecnológicas que permitan realizar procesos de Analítica de Datos (descriptiva; predictiva y prescriptiva); Big Dat… | AI implementation is in scope; supplier type does not establish an individual practitioner. |
