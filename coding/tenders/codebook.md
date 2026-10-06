# Tender clause codebook v3 (30 September 2026)

Supersedes `evidence_b/sa_etenders/CLAUSE_CODEBOOK_E1.md` (v1) for the five clause types below. Frozen together with `PROTOCOL_INCOME_GRADIENT.md`. Scope: procurement packs (tender, RFQ, draft contract, annexes, standard conditions printed in the pack) for AI or AI-bearing cloud and software services.

All examples are quoted from the South African tender texts under `evidence_b/sa_etenders/` (`sa_txt`, `sa_txt2`), checked by string search on 30 September 2026. Platform and vendor names inside quotes are replaced by [platform] or omitted with an ellipsis. Quote fragments follow the source spelling. Document identifiers are the short tender codes from the OCDS ids. The codebook was written from the model-coding output (`sa_clauses_llm_v2.csv`), the derived disagreement list (`cowork_verify/disagreements_sa.csv`) and the texts; no author coding sheet was opened.

## 1. What went wrong in v1

1. v1 coded "supplier_change_of_terms = buyer_consent_required" and mapped it to "Condition 2 (refusal right)". The clause it captured (a signed written amendment) binds the two parties to the contract; it does not let a buyer reject a change to a platform's own terms, and it does not let the buyer leave. It is now named `variation_control` and is never read as a refusal or exit right.
2. v1 put inbound migration (moving onto the awarded platform) and outbound exit (leaving it) into the same fields (`exit_transition`, `financing_alternative`). Both coders read those fields differently. v3 adds a mandatory direction test.
3. v1 counted "return of documents" and "data export as a service feature" as data return.
4. v1 listed "parallel run" as financing of an alternative without saying which direction it serves.
5. Origin of a clause (printed by the buyer, reproduced standard conditions, or merely cited) was mixed with presence.

## 2. Global rules

R1. **Direction test (mandatory for T3, T4, T5).** Ask: does this text move the buyer's work onto the awarded supplier's service (inbound), or off it, or keep it running while the buyer changes provider (outbound/continuity)? Inbound text is recorded in `inbound_note` and never counts toward T2 to T5.

R2. **Holder test.** A right counts as the buyer's only if the buyer can exercise it on its own initiative. A duty counts as the supplier's only if the text says "shall", "must", "will be required" or an equivalent, addressed to the supplier or bidder. "May", "should be able to", and evaluation criteria ("a plan for...") are `mentioned` at most.

R3. **Source tag** on every positive code: `own_text` (drafted for this tender: specification, ToR, special conditions, pricing schedule, draft contract); `reproduced_in_pack` (standard conditions printed in the pack); `incorporated_not_seen` (named but not printed; recorded, not counted as present). A clause is never both `own_text` and `reproduced_in_pack`: if the identical sentence appears as the printed standard conditions, its tag is `reproduced_in_pack`, whichever section of the pack it sits in.

R4. **Quote and locator.** A positive code needs a quote of 40 words or fewer and a locator (section, page or clause number). No quote, no code.

R5. **Grades.** `specified` = holder test met, trigger stated, object stated; `mentioned` = topic present but a required element is missing or the text is only evaluative; `none` = nothing in the pack; `not_readable` = text not usable (OCR failure, empty extraction).

R6. **Default on genuine ambiguity:** the lower-protection code. Record `ambiguous=true`.

R7. Code the pack, not the eventual contract. Note the platform whose terms may govern the service layer (needed for `flow_down`), but do not infer platform terms from the tender.

## 3. The five clause types

### T1. Inbound amendment control (`variation_control`)

Definition: a clause on how the terms of *this contract* may be varied. It says nothing about whether the buyer may leave, and it does not by itself give the buyer a right to reject a change to a supplier's own online terms.

Codes: `mutual_written_variation`; `buyer_approval_of_supplier_changes` (the text names supplier-side changes to service terms, prices, versions, or platform terms and requires buyer approval); `supplier_may_vary_after_award`; `notice_only`; `silent`.

Decision rules:
- A "no variation except by signed writing" sentence is `mutual_written_variation` and nothing stronger.
- Upgrade to `buyer_approval_of_supplier_changes` only if the text names supplier-side changes and requires the buyer's approval or objection right.
- A statement that terms are subject to change before signature is a pre-award offer statement, not a post-award change right; code `silent` for post-award and note it.
- Approval of scope additions (extra servers, extra users) is a scope control, not variation of terms: record `scope_addition_approval` and do not code T1 from it.
- Tag with R3; report counts of `own_text`, `reproduced_in_pack` and `incorporated_not_seen` separately, and a combined "any route" count only beside them.

Include (quotes):
- `mutual_written_variation`, `reproduced_in_pack`: "No variation in or modification of the terms of the contract shall be made except by written amendment signed by the parties concerned." (standard general conditions of contract, clause 18.1, printed in tender pack 100222, Municipal Demarcation Board.)
- `mutual_written_variation`, municipal version: "No agreement to amend or vary a contract or order or the conditions, stipulations or provisions thereof shall be valid and of any force unless such agreement to amend or vary is entered into in writing and signed by the contracting parties." (Lesedi Local Municipality conditions, clause 34.1.)

Exclude / edge:
- "All pricing and other terms are subject to change at any time by us until execution and delivery by all parties of the final enrollment and all other necessary legal documentation." (Council for Geoscience pack, a quotation.) Pre-signature only: `silent` post-award; the earlier model code `supplier_unilateral` overstates it.
- "The service provider should be able to spool up, support, and maintain additional servers for the Department as and when required. NB: Any additions will be agreed upon beforehand." (National School of Government ToR 5.5.) Scope addition control: `scope_addition_approval`, not T1.

### T2. Buyer exit (`buyer_exit_right`)

Definition: the buyer may end the contract, in whole or in part, on its own initiative and without supplier default. Also covers a penalty-free exit after a notified supplier change. Termination for default or insolvency, expiry and non-renewal are not exit.

Codes: `convenience` (with notice period in days if stated); `conditional` (right limited to an anniversary, to non-renewal, or to a stated event other than default); `cause_only`; `silent`.

Decision rules:
- The trigger word test: "at its discretion", "in its own interest", "if it wishes" without a default trigger = `convenience`.
- Right exercisable only at an anniversary or renewal date = `conditional` (not `convenience`).
- A notice period does not turn a convenience right into a conditional one; record the days.
- The general conditions' termination for default is `cause_only` even if the buyer alone decides whether to invoke it.
- If both a convenience right and cause-only text appear, code `convenience`.
- Tag with R3. Standard conditions that contain only cause-based termination (as the national general conditions do) yield `cause_only` for every pack that reproduces them, and that is an inheritance pattern, reported as such.

Include:
- `convenience`: "Kouga Local Municipality reserves the right to terminate the services of the provider at the sole discretion of the Kouga Local Municipality."
- `convenience` with notice: "The CBRTA, if it wishes to terminate the contract, shall be required to give 30 (thirty) days written notice of its intention to terminate the contract. Such notice must be preceded by bona fide discussion between the CBRTA and the successful Bidder." (record 30 days and the consultation condition.)
- `convenience` with notice: "...to terminate the contract, provided a one (1) month notification is given to the appointed bidder." (National Student Financial Aid Scheme pack.)
- `convenience` in a purchase order: "Rand Water reserves the right, at any time, in its own best interest, ... and without liability, to terminate a Purchase Order in whole or in part" (text broken by a page footer in the extraction; quote may fail a strict verbatim test).

Exclude / edge:
- `conditional`: "ERWAT reserve the right to extend or terminate the Support and Maintenance service on or after anniversary of the effective date for the period of this contract."
- `conditional`: "In the event that Interfront elects not to renew the license, the contract may be terminated by Interfront by written notice to the service provider" (tied to non-renewal).
- `cause_only`: "The purchaser, without prejudice to any other remedy for breach of for default contract, by written notice of default sent to the supplier, may terminate this contract in whole or in part: (a) if the supplier fails to deliver..." (general conditions, clause 23.1; the wording is the source's own.)

### T3. Data return (`data_return`)

Definition: at or after termination or expiry, the supplier must hand back, deliver or export the buyer's data in a usable form. A second value records portability during the term.

Codes: `specified_end_of_contract` (holder: supplier; trigger: end or termination; object: buyer data; form or deadline stated or "readable/usable/non-proprietary"); `mentioned`; `portability_during_term` (secondary code, separate variable); `none`.

Decision rules:
- The object must be data or content the service holds for the buyer. Return of the buyer's own bid documents, specifications or confidential information is *not* data return: code `none`, note `documents_only`.
- A required *feature* (export capability, retention, e-discovery) is `mentioned` and flagged `feature_only`, not `specified`, because no end-of-contract duty or trigger is stated.
- A permission to move data during the term is `portability_during_term`; it does not by itself make T3 `specified_end_of_contract`.
- Destruction certificates alone are not return.

Include:
- `specified_end_of_contract`: "Contract Termination / Exit Procedure ... Provide a full SQL backup (or equivalent non-proprietary data-dump format). ... Deliver all necessary decryption keys, credentials, and documentation." (Mogale City Local Municipality; the earlier relevance code for this pack was "not relevant", so it will not enter the AI or cloud set unless the relevance screen changes.)
- `specified_end_of_contract`: "Bidders are required to submit to ERWAT all data in a readable, accessible format at the end of their contract."
- `portability_during_term`: "The cloud service provider shall allow the QCTO to move data on and off the cloud platforms as needed."

Exclude / edge:
- `mentioned`, `feature_only`: "Comprehensive compliance, E-discovery, and litigation support, including retention, legal hold, case management, and data export." (Greater Tzaneen Municipality.)
- `none`, `documents_only`: "Any document, other than the contract itself mentioned in GCC clause 5.1 shall remain the property of the purchaser and shall be returned (all copies) to the purchaser on completion of the supplier's performance under the contract if so required by the purchaser." Clause 5.1 concerns the specification, plans and information furnished by the purchaser; it is not the buyer's data held on a service.
- `none`: "This bid and any other documents supplied by Agrément South Africa remain proprietary ... and must be promptly returned to Agrément South Africa upon request" (bid documents).

### T4. Financing of an alternative (`buyer_financing_alternative`)

Definition: a buyer-held or buyer-priced item that pays for leaving the awarded supplier or for a second source: a reserve or budget line for a later exit, a priced outbound transition line the buyer commits to, a priced parallel run of the *awarded* service with a second provider, or funded in-house capacity to take the service back. Supplier onboarding and inbound migration costs never count, because they finance entry, not the alternative.

Codes: `specified` (an amount, a priced line, or a committed budget statement, and a direction that is outbound or second-source); `mentioned` (the alternative or the parallel procurement is named, no funding stated); `none`.

Decision rules:
- Apply R1. A price line labelled "migration", "tenant transfer" or "implementation" for moving onto the awarded platform is inbound: `none`, `inbound_note`.
- A parallel run counts only if it preserves the option to revert to, or move to, a provider other than the one being awarded. A parallel run to cut over to the awarded system is inbound.
- A standby or second supplier without funding is continuity (T5 `standby_supplier`), not T4.
- The field is a tender-visible proxy. It does not observe the ex ante budget line and releasing party of Condition 1; results must say so.

Include:
- `mentioned` (buyer's own alternative procurement, no funding stated): "An open bid process is being kicked off as a parallel process to procure cloud hosting for a period of 60-months." (Department of Labour extension memo.) Pair with the T5 switching-time note below.
- No `specified` example exists among the quotes in `sa_clauses_llm_v2.csv`; both earlier `specified` codes fail v3 (below). The expected v3 count of `specified` is therefore zero for the current South African corpus, to be confirmed on recode.

Exclude:
- Inbound price lines: "Proposal to include the subscription / Tenant transfer costs, Management fee cost, and Once-off / initial costs and monthly support costs." (National School of Government); "g) Migration Plan (Implementation ... Cost)" (Railway Safety Regulator, Year 3 fee table, bidders to price it; direction unclear, so `none`); pricing line "Migration to Cloud" (Road Accident Fund); "Once-off migration" costs added to the price used for evaluation (Transnet).
- Earlier `specified` code, now `none`: "Address how the parallel process will migrate from old to new." (Municipal Demarcation Board; a cut-over parallel run onto the new system, inbound.)
- Earlier `specified` code, now T5 `standby_supplier` and T4 `none`: "For Category A & B the CCT intends to appoint a main tenderer - the highest ranked tenderer (the winner) and in addition, one standby tenderer for the allocation of work." (City of Cape Town; a second source is arranged but nothing is funded.)

### T5. Continuity and transition (`continuity_transition`)

Definition: the supplier is required to keep the service running while the buyer changes provider, or to help a successor or the buyer take over, at exit. Two sub-variables, both outbound or continuity: `outbound_transition` and `continuity_during_change`. Inbound takeover is recorded separately as `inbound_takeover` and never counted.

Codes for `outbound_transition`: `specified` (supplier duty, trigger at termination or expiry, object: handover of assets, documentation, knowledge or run-off support to the buyer or successor, with duration or deliverables); `mentioned`; `none`. Codes for `continuity_during_change`: `specified` (run-off or extended service period, exit plan, interim agreement, standby supplier arranged in the pack); `mentioned`; `none`.

Decision rules:
- Apply R1 first. Who is taking over from whom decides.
- "Handover" or "knowledge transfer" in a scoring criterion, with no stated direction, is `mentioned` and flagged `direction_unclear`.
- Handover of documentation and deliverables on termination is `outbound_transition` = `specified` (grade note: `handover_only`, no run-off).
- Skills transfer to the buyer's staff during the project is capability building, not exit; record in `knowledge_transfer` (unchanged field), not T5.
- A buyer's statement of how long switching would take is not a supplier duty: record it in `switching_time_note` (useful for the notice-versus-activation argument) and code T5 `none`.

Include:
- `outbound_transition` = `specified`, `handover_only`: "On termination of this agreement, the contractor shall, on demand hand over all documentation provided as part of the project and all deliverables, etc., without the right of retention, to BANKSETA."
- `outbound_transition` = `specified`: "Contract Termination / Exit Procedure ... Provide a full SQL backup within 10 business days of contract termination." (Mogale City Local Municipality; see T3 on relevance.)
- `continuity_during_change` = `specified`, `standby_supplier`: the City of Cape Town standby tenderer sentence quoted under T4.
- `mentioned`: "vendor lock in prevention (modular / open architecture), risk sharing, exit clauses;" (Industrial Development Corporation; a topic in a consultant's scope of work, not a duty on a supplier.)
- `mentioned`, `direction_unclear`: "a plan for handover/knowledge transfer." (EWSETA evaluation item.)
- `switching_time_note`, T5 `none`: "The full open bid process and migration to a new cloud platform requires a timeline of 12 months to migrate between cloud providers." (Department of Labour.)

Exclude (inbound, `inbound_takeover`):
- "The appointed service provider must be able to transfer roles and responsibilities and take over ownership from the current service provider in a smooth manner, without disrupting the day-to-day activities of the FAIS Ombud." (Office of the Ombud for Financial Service Providers, 25.13.)
- "Transnet requires a transition period of 3 months to move from one data centre to another. The CSP will be required to migrate existing workloads from the current public platform utilized by Transnet to the new platform..." (Transnet SOC Ltd.)
- "Migrate the current solution to cloud (Migration includes software installation, data and integration points)." (Road Accident Fund.)
- "Interfront may require the bidder(s) to enter into an interim agreement under which the transition services would commence;" (award stage, `direction_unclear`, `mentioned` at most.)

## 4. Confusions found in `disagreements_sa.csv`, resolved one by one

The file lists 15 disagreements between the author's codes and the model's codes on 14 documents. Rows are given by document code and field.

| # | Doc, field | Author / model | What happened | v3 rule and result |
|---|---|---|---|---|
| 1 | S08 exit_transition | mentioned / none | Road Accident Fund: "Migrate the current solution to cloud" plus a "Migration to Cloud" price line. Inbound. | R1: `inbound_takeover`; T5 `none`. Model was right; the author's `mentioned` is withdrawn. |
| 2 | S09 exit_transition | mentioned / specified | FAIS Ombud: new provider "take over ownership from the current service provider". Inbound. | R1: `inbound_takeover`; T5 `none`. Model's `specified` was wrong. |
| 3 | S12 exit_transition | mentioned / none | Railway Safety Regulator: "Migration Plan (Implementation ... Cost)" in the Year 3 table; direction unclear. | R1 and R6: direction not shown, so lower-protection code: `none`, `direction_unclear`. |
| 4 | S14 exit_transition | mentioned / specified | Transnet: three-month transition to "the new platform", once-off migration cost. Inbound. | R1: `inbound_takeover`; T5 `none`. Model's `specified` was wrong. |
| 5 | S17 exit_transition | mentioned / none | National School of Government: "Tenant transfer costs" and inbound migration. | R1: `none`. Model was right. |
| 6 | S07 data_return | specified / mentioned | Greater Tzaneen: "including retention, legal hold, case management, and data export" is a service feature, no end-of-contract duty. | T3 rule: `mentioned`, `feature_only`. Model was right. |
| 7 | S20 data_return | none / specified | EWSETA: model coded a general-conditions clause returning "any document ... mentioned in GCC clause 5.1". The object is the purchaser's supplied information, not data. | T3 rule: `none`, `documents_only`. Author was right; model's `specified` was wrong. |
| 8 to 11 | S08, S12, S14, S17 financing_alternative | mentioned / none | Inbound migration and onboarding price lines read as financing of an alternative. | T4 rule: inbound lines never count; `none`. Model was right in all four. |
| 12 to 14 | S07, S08, S17 buyer_consent_to_changes | only_via_GCC / required_own_text | The pack itself reproduces the printed clause 18.1 ("No variation in or modification of the terms of the contract shall be made except by written amendment signed by the parties concerned."); the model treated it as the document's own text, the author as coming through the general conditions. Not a reading error: a labelling choice. | R3: `reproduced_in_pack`, code `mutual_written_variation` in all three; both earlier labels retire. The field is renamed `variation_control` and is not a refusal or exit right. Report "any route" only beside the tag split. |
| 15 | S07 incorporates_GCC | yes / no | The pack states the general conditions "will form part of all bid" documents and prints them. | Printed and stated to be part of the bid: `reproduced_in_pack` (yes). Model's `no` was wrong. |

Net effect on counts (to be confirmed on recode, not yet computed): the inbound-versus-outbound rule removes the model's `specified` codes for exit in S09 and S14 and all four author `mentioned` codes for financing; the documents-only rule removes some `specified` data-return codes based on general-conditions clause 5.2; and the two earlier financing `specified` codes fall to `none` or to T5 standby supplier.

## 5. Other changes from v1

- `price_adjustment`, `lock_in_safeguard`, `knowledge_or_ip_transfer` are unchanged and out of scope here; they keep their v1 definitions.
- `buyer_termination` in v1 is replaced by T2.
- `financing_alternative` in v1 is replaced by T4; `exit_transition` in v1 is split into T3 (data), T5 (transition and continuity) and the retained `inbound_takeover` note.
- New fields: `source_tag`, `direction`, `ambiguous`, `switching_time_note`, `flow_down` (does the pack make a named platform's own terms applicable to the buyer: yes, no, unclear).

## 6. Calibration before use

Five packs (not later analysed) are coded first by each coder; mismatches are resolved against this text; the wording is amended once. Agreement thresholds and what happens below them are in `PROTOCOL_INCOME_GRADIENT.md`, section 5.
