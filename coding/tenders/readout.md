# South Africa tender clauses: recode under codebook v3 (1 October 2026)

**Status: first-pass model extraction, checked only for verbatim quotation and cross-tabulated against one blind human coder. Not a validated estimate.**

Inputs: the 109 documents screened relevant in the preceding automated pass and the frozen tender codebook. The source texts are withheld. All 109 recoding outputs parsed; the released tables retain the original codes and quotation-check flags.

## 1. Relevance

The v3 screen keeps **82 of 109** documents. The 27 dropped are mostly requests for quotation for staff training courses on a cloud platform, laptop or hardware supply, and single-seat certifications, where no AI or cloud service is bought.

## 2. Counts (n = 82 relevant documents)

| Clause type | Positive code | n | Share | Source tag |
|---|---|---:|---:|---|
| T1 variation control | mutual written variation | 33 | 40% | 29 reproduced standard conditions, 4 own text |
| | buyer approval of supplier changes | 2 | 2% | own text |
| | supplier may vary after award | 1 | 1% | own text |
| | silent | 46 | 56% | 2 of them name the general conditions without printing them |
| T2 buyer exit | convenience | 5 | 6% | 4 own text, 1 reproduced |
| | conditional | 5 | 6% | own text |
| | cause only | 49 | 60% | 36 reproduced, 13 own text |
| | silent | 22 | 27% | |
| T3 data return | specified at end of contract | 2 | 2% | own text |
| | mentioned | 4 | 5% | |
| T4 financing an alternative | specified | 0 | 0% | |
| | mentioned | 1 | 1% | a re-procurement remedy on supplier default, not buyer-funded capacity |
| T5 continuity/transition | specified | 4 | 5% | own text |
| | mentioned | 4 | 5% | |

One document returned no codes (unreadable text). The two data-return clauses that meet the v3 test are an ERWAT requirement to submit "all data in a readable, accessible format at the end of their contract" and a hand-over of "any and all information and data" to the purchaser.

**What changed from v2.** The v2 figure "refusal-type consent 71/109 (65%)" is retired. The clause behind it is a mutual written-variation clause that binds both parties; it is not a buyer's right to refuse a platform's own change of terms, and it gives no exit. Under v3 no document gives the buyer a right to refuse a supplier's change of terms and then leave at no cost. Financing of an alternative falls from 2 to 0 specified, as the codebook predicted. Termination for convenience is 5 of 82 (v2: 6 of 109).

## 3. Quote check

91 of 113 positive-code quotes match the source text exactly after normalising case, punctuation and spacing. Of the other 22, 18 are near matches (partial-match score 91.8 to 98.5), almost all the same printed general-conditions clause with OCR or spacing differences. Four score 60 to 72 and need a hand check before any is cited (NRF/SAQA termination on compromised communication; a purchase-order price-variation clause; a convenience clause in one pack; a "closeout and handover report" line).

## 4. Against the author's blind sheet (20 documents, all matched)

The author coded the v2 fields, so this is a cross-tabulation, not an agreement statistic.

- Both treat the same 5 documents as unreadable.
- Data return: 13 of 14 readable agree on none; the one author `specified` is a model `mentioned`.
- Financing: the author's 4 `mentioned` are all model `none`. Codebook v3 predicted this (they concern inbound migration onto the new system, not a funded exit).
- Exit/transition: the author's 7 `mentioned` are 2 model `mentioned` and 5 `none`; to be checked against the direction rule.
- Variation: 6 documents the author coded `only_via_GCC` are model `silent`. Under v3 rule R3 a named but unprinted general-conditions clause should be tagged `incorporated_not_seen`, not silent. This looks like a model under-coding and is the first item for the human pass.

## 5. What this supports

A descriptive statement only: in a public South African corpus of AI and cloud tender documents from 2023 to 2026, buyer-side protections of the kind the model requires (a refusal right with a funded fallback) are close to absent; exit for convenience and data return are rare; the common clause is a mutual written-variation clause. No income comparison and no causal claim follow from one upper-middle-income country. A v3 human pass (protocol section 5) is still owed.
