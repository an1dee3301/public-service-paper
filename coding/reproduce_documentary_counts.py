#!/usr/bin/env python3
"""Recount three documentary quantities using the released tables (standard library)."""
import csv
import json
import re
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIDENCE_MIN = Decimal('0.85')
PHRASE = 'general conditions of contract'
# Subject suppliers only: these are the original administrative-text search rules.
PROVIDER_PATTERNS = {
    'azure': r'\bazure\b', 'microsoft': r'microsoft', 'openai': r'open\s?ai',
    'chatgpt': r'chat\s?gpt', 'google': r'\bgoogle\b', 'gemini': r'\bgemini\b',
    'aws': r'\baws\b|amazon web services', 'google_cloud': r'google cloud|vertex|\bgcp\b',
}


def provider_tag(object_text, process_text, firm_supplier_text):
    """Original rule; caller supplies empty supplier text for a non-firm."""
    text = object_text + ' ' + process_text + ' ' + firm_supplier_text
    return any(re.search(pattern, text, re.I) for pattern in PROVIDER_PATTERNS.values())


def general_conditions_flags(text):
    """Literal and whitespace-only normalization; no punctuation/OCR correction."""
    lower = text.lower()
    return PHRASE in lower, PHRASE in re.sub(r'\s+', ' ', lower)


def flag(value):
    if value not in ('True', 'False'):
        raise ValueError(f'Expected True/False, got {value!r}')
    return value == 'True'


def table(name, key):
    with (HERE / name).open(newline='', encoding='utf-8-sig') as f:
        records = list(csv.DictReader(f))
    indexed = {row[key]: row for row in records}
    if len(indexed) != len(records) or '' in indexed:
        raise ValueError(f'Duplicate or empty key in {name}')
    return indexed


def counts():
    eligible = table('contracts/eligible_contracts.csv', 'id_contrato')
    outcomes = table('contracts/outcomes_v2.csv', 'id_contrato')
    tags = table('contracts/provider_tags.csv', 'id_contrato')
    core = {key for key, row in eligible.items() if flag(row['elig_core'])}
    if set(tags) != core or set(outcomes) != set(eligible):
        raise ValueError('Contract tables do not have the expected exact join coverage')
    risk, high = [], []
    for key in sorted(core):
        row = outcomes[key]
        if not flag(row['elig_core']):
            raise ValueError('Eligibility disagreement across contract tables')
        if flag(row['atrisk_f12']):
            risk.append(row)
            if Decimal(eligible[key]['label_conf_v1']) >= CONFIDENCE_MIN:
                high.append(row)
    if not high:
        raise ValueError('Empty confidence sensitivity denominator')
    numerator = sum(flag(row['later_12m']) for row in high)
    percent = Decimal(100) * numerator / len(high)
    codes = table('tenders/sa_clauses_v3.csv', 'doc')
    matches = table('tenders/general_conditions_matches.csv', 'doc')
    relevant = {key for key, row in codes.items() if flag(row['relevant'])}
    if set(matches) != relevant:
        raise ValueError('Tender table does not cover exactly the relevant documents')
    for row in matches.values():
        if not re.fullmatch(r'[0-9a-f]{64}', row['extracted_text_sha256']):
            raise ValueError('Invalid extracted-text hash')
        if flag(row['literal_match']) and not flag(row['whitespace_normalized_match']):
            raise ValueError('Literal match must also match the normalized rule')
    silent = {key for key in relevant if codes[key]['T1_variation_control.code'] == 'silent'}
    return {
        'provider_tags': {'core_contracts': len(core),
                          'tagged': sum(flag(row['provider_tag']) for row in tags.values())},
        'confidence_sensitivity': {
            'threshold_inclusive': str(CONFIDENCE_MIN), 'at_risk_unfiltered': len(risk),
            'later_unfiltered': sum(flag(row['later_12m']) for row in risk),
            'at_risk_filtered': len(high), 'later_filtered': numerator,
            'percent': str(percent), 'rounded_percent': int(round(percent)),
        },
        'general_conditions': {
            'relevant_documents': len(relevant), 'silent_documents': len(silent),
            'literal': sum(flag(matches[key]['literal_match']) for key in silent),
            'whitespace_normalized': sum(flag(matches[key]['whitespace_normalized_match']) for key in silent),
        },
    }


if __name__ == '__main__':
    print(json.dumps(counts(), indent=2))
