# Full-document second automated coding and adjudication

**Completed 30 September 2026, SGT.** Pass C was produced from `codebook.md`, `../../sources/terms.json` and the preserved texts only; its 40-row CSV was hashed before the first comparison outputs were opened. Pass C is an **AI second coder**, not human intercoder reliability. The post-freeze `adjudicated.csv` records all 40 A/C pairs and the proposed resolution. No manuscript inference should be based on an apparent agreement rate alone.

## Exact categorical agreement with Pass A

| Field | Matches / 8 | Agreement | Cohen's κ |
|---|---:|---:|---:|
| Model-retirement notice | 6 | 75.0% | 0.568 |
| Affirmative export right | 4 | 50.0% | 0.373 |
| Customer convenience termination | 6 | 75.0% | 0.673 |
| Price-change notice | 4 | 50.0% | 0.396 |
| Material legal-terms notice | 4 | 50.0% | 0.385 |
| **All cells (descriptive only)** | **24 / 40** | **60.0%** | — |

The denominator includes five `not_applicable` Meta cells and four `not_observed` Microsoft cells that agree by construction of the evidence boundary. Codes measure **read-document evidence**, not operative government contracts. For some Anthropic and Google cells, A and C independently chose different frozen captures; their exact-code comparison is therefore a reproducibility diagnostic rather than a same-version reliability estimate. κ uses the two coders' observed marginal category frequencies for each 8-cell field.

## Sixteen differences and proposed adjudication

Quoted fragments below identify the decisive **clause text** in the frozen files; they are deliberately short. `A → C → final` uses the codebook vocabulary. Clause references and document IDs for every cell are in the two CSVs. A final `yes` records an affirmative general rule while its exceptions remain in the Pass C notes; `conditional` records an actual eligibility, request, temporal or layer restriction.

| Provider / field | A → C → final | Clause text and reason |
|---|---|---|
| OpenAI / export | yes → conditional → **conditional** | DPA `p1_dpa_latest` §2.11: “at Customer’s instruction, return or delete Customer Data.” Instruction and data scope meet the codebook's conditional rule; no model export follows. |
| OpenAI / convenience | not_observed → no_in_read_document → **no_in_read_document** | Agreement `p1_business_latest` §11.2 permits termination for material breach or insolvency; §2.3's exit follows “materially reduces the Services functionality.” Full read supplies no unconditional convenience right. |
| OpenAI / material terms | yes → conditional → **yes** | Agreement §16.13: “at least thirty days notice before the update is effective” for material impact in OpenAI's judgment. It is an explicit rule; legal-compliance and judgment exceptions remain noted. |
| Anthropic / export | yes → conditional → **conditional** | DPA `p2_dpa_live` H.1: “if requested to do so by Customer within that period, return a copy of all Customer Data” within 30 days after end. Pass A used `p2_dpa_latest`; both captures show the request condition. |
| Anthropic / price | yes → conditional → **conditional** | Commercial Terms `p2_business_live` H.1: new rates effective “the earlier of 30 days after the updates are posted ... or Customer otherwise receives Notice.” Receipt can be earlier. Pass A used `p2_business_latest`. |
| Anthropic / material terms | yes → conditional → **conditional** | Commercial Terms M.3 uses the same earlier-of-posting-or-Notice rule; regulatory changes “take effect immediately.” Pass A used a different dated capture. |
| Google / retirement | not_observed → conditional → **conditional** | `p3_lifecycle_live`, short-term models: a posted date “gives you at least 45 days to migrate.” Pass A cited `p3_lifecycle_latest`, a different model-deprecations page without that general statement. The 45-day rule is layer- and class-specific. |
| Google / export | yes → conditional → **conditional** | DPA `p3_dpa_live` §9.1 permits export “During the Term” and “in a manner consistent with the functionality of the Services”; §6.2 calls for return before term end. |
| Google / convenience | yes → conditional → **yes** | Cloud Terms `p3_business_live` §8.5: “Customer may terminate this Agreement for its convenience at any time on prior written notice.” Order Form financial commitments limit cost relief, not the right itself. |
| Google / price | not_observed → no_in_read_document → **no_in_read_document** | Cloud Terms §2.6: “Google may change the Fees at any time”; 30-day advance notice is expressly “For GWS Services, Looker ... and Cloud Identity Services only,” not the GCP AI surface. |
| Google / material terms | yes → conditional → **yes** | Cloud Terms §1.4(b)–(c): GCP material updates generally “become effective 30 days after they are posted”; immediate law/new-functionality exceptions are recorded. |
| Microsoft / retirement | yes → conditional → **yes** | `p4_lifecycle_live`, notification table: GA “At least 60 days before retirement” and preview “At least 30 days”; emergency retirement can shorten notice. The field records existence of an explicit rule, with categories in notes. |
| Mistral / price | not_observed → no_in_read_document → **no_in_read_document** | Commercial Terms `p7_business_live` §10.1 points to the pricing page; §§13.1–13.4 address legal-term updates. No separate existing-service price-change notice appears in the full read document. |
| Alibaba / export | not_observed → no_in_read_document → **no_in_read_document** | Membership Terms `p8_business_live` §8.5: customer “will lose access to any Member Content” on termination. The read membership and product terms contain no affirmative retrieval grant; this is only a read-document negative. |
| Alibaba / price | not_observed → no_in_read_document → **no_in_read_document** | Membership Terms §6.3: payment terms updates “will take effect upon publication.” That is not advance notice for existing Model Studio prices. |
| Alibaba / material terms | yes → conditional → **yes** | Membership Terms §1.2: material changes generally “become effective 15 days after they are posted.” New-service/function and legal-compliance changes can be immediate; retain those exceptions. |

## Interpretation

Pass C mainly separated general affirmative rules from qualified use, and `not_observed` from a full read that lacked a right. The highest practical-risk differences concern export: DPA/customer-data return is narrower than export of a usable replacement, and a customer request or live-term deadline can govern. The agreement numbers should not be presented as human validation or as proof that model terms apply to any executed public-sector order. A human coder still needs to review the adjudications before a scaled audit or submission claim.
