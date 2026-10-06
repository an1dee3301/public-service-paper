# E1 tender/contract clause codebook v1 (30 Sep 2026)
Unit: one procurement document (tender/RFQ/contract) for an AI, ML, chatbot or AI-bearing cloud/software service. Code only what the document says; quote the decisive text (≤40 words) with page/section if visible.
| Field | Codes | Maps to |
|---|---|---|
| ai_object | core_ai / ai_component / cloud_software_no_ai / not_relevant | scope |
| named_foreign_platform | list | dependence exposure |
| exit_transition | specified (duties/timeline for handover, transition assistance, exit plan) / mentioned / none | Condition 3 (operable fallback) |
| data_return_export | specified / mentioned / none | Condition 3 |
| knowledge_or_ip_transfer | source code, escrow, skills/knowledge transfer, buyer ownership of IP/models: specified / mentioned / none | Condition 3 |
| supplier_change_of_terms | buyer_consent_required / notice_only / supplier_unilateral / silent | Condition 2 (refusal right) |
| price_adjustment | fixed / formula_or_index / negotiated_with_approval / supplier_list_price / silent | Condition 2 |
| buyer_termination | convenience / cause_only / silent | Condition 2 |
| financing_alternative | budget or obligation for second source, parallel run, in-house capacity, or transition funding: specified / mentioned / none | Condition 1 |
| lock_in_safeguard | open standards / interoperability / vendor-neutral / portability requirement: specified / mentioned / none | general |
| contract_term_months | number or blank | |
Rules: tender specs often omit legal terms incorporated by reference (e.g., GCC/SLA); code 'silent'/'none' only for what is in the document and flag `incorporates_by_reference` (true/false, name the instrument).
