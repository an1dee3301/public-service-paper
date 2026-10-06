# Supplier terms V2 codebook — 30 September 2026

Unit: provider × service surface × document layer × dated version × field. A commercial agreement, service-specific terms, DPA, lifecycle documentation and public-government terms are distinct layers. A linked layer is not incorporated or operative merely because it is public. Order forms, negotiated addenda, reseller terms and customer location may change priority. Meta Llama weight licenses are not hosted API contracts.

Pass A is manual rule-based coding; Pass B is a separate second automated coder extraction from locally captured text, with no web tools. Both use only the identified version and retain document ID, clause locator, concise evidence summary, status, and numeric days when explicitly stated. Codes: `yes`, `no_in_read_document`, `conditional`, `ambiguous`, `not_observed`, `not_applicable`. `no_in_read_document` requires a full usable read of the identified document; missing or excerpted text is `not_observed`. An affirmative right is `yes` only if granted to the customer; provider discretion, mere feature availability or a linked page is insufficient. Numeric windows refer to calendar days unless the text says otherwise; do not turn months into days without labeling the conversion. Exceptions, triggering event and eligible customer belong in the note.

| Field | Coding rule |
|---|---|
| `model_retirement_notice_days` | A *model-version* retirement/lifecycle page states a notice or support window. Do not substitute cloud-service discontinuation or general agreement notice. Record value, units, start event, exceptions and whether policy is contractual. |
| `export_right_affirmative` | Terms or DPA affirm customer ability to retrieve/export customer content or data, with scope and post-termination window. `conditional` if subject to availability, request, payment, format or limited retention. Prompts/outputs are not weights or a usable replacement. |
| `termination_for_convenience_customer` | Customer may terminate without breach or cause. Note advance notice and charges; expiry or provider termination does not count. |
| `notice_days_price_change` | Explicit advance or post-notice for increased charges affecting existing customer/service; state whether posted-only, email, exception or renewal-only. |
| `notice_days_material_terms` | Explicit notice for material legal-term amendment, separately from price or service deprecation. Note objection/exit remedy and immediate exceptions. |

The seven pilot fields remain separate and retain their original definitions in `../SUPPLIER_TERMS_PILOT/CODEBOOK.md`. The table is descriptive public-default evidence only: it cannot show executed government terms, fallback funding, operable migration, binding resident refusal, or outcomes. Compare like service, layer and date before cross-country inference; country availability is not an income gradient.
