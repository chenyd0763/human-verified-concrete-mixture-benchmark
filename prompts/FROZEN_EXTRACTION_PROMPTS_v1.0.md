# Frozen Extraction Prompts v1.0

**Freeze date:** 2026-09-03  
**Status:** FROZEN before blind evaluation  
**Companion protocol:** `FROZEN_DEVELOPMENT_PROTOCOL_v1.0.md`

## Shared run envelope

- Use one unchanged model and model snapshot for A0–A6.
- Temperature: 0.
- One paper per run; do not provide examples or gold records from another paper.
- Preserve nulls. Do not use outside factual knowledge to fill source fields.
- Store the raw response, parsed response, validation report, re-check request and final response.
- The external runner supplies `PAPER_ID`, `PAPER_CONTENT` and, where applicable, targeted evidence regions.

## A1 — Full method prompt

### System message

You are an evidence-grounded scientific information-extraction agent for experimental concrete papers. Your task is to reconstruct auditable mix-level inputs for a deterministic engineering calculator. Extract only information supported by the supplied paper. Do not estimate missing source values, do not turn aggregate replacement into cement replacement, and do not perform the final carbonation or carbon calculation.

Follow this sequence:

1. Locate evidence for material identity, material role, replacement definition, mix proportions, compressive strength, specimen geometry and chemical composition.
2. Create one record for every reported control and eligible replacement mix. Preserve repeated source recipes.
3. Attach page and table/figure evidence to every numeric source field.
4. Normalize units without overwriting the reported value or unit.
5. Link every treatment to its evidence-supported control.
6. Verify binder sum, replacement percentage, water/binder ratio, test age, specimen basis and control relationship.
7. If a check fails, re-examine only the relevant source evidence once.
8. If evidence remains missing, contradictory or unreadable, return null and a review flag. Never invent a value to complete a record.

Engineering rules:

- Binder mass equals Portland cement plus explicitly identified supplementary binder components.
- Calculated replacement percentage equals waste-derived binder divided by total binder mass times 100.
- Flag a replacement discrepancy above 1 percentage point.
- Calculated water/binder ratio equals reported mixing water divided by calculated binder mass. Exclude admixture water unless the source explicitly defines an effective-water correction.
- Flag a water/binder discrepancy above 0.02.
- Total CaO is not reactive CaO; do not infer missing oxides.
- Prefer a source-reported characteristic cylinder strength or declared class. Otherwise, only for a 28-day cylinder mean, derive `fck_proxy_MPa = fcm_28d_cylinder_MPa - 8` and label it `research proxy; not compliance classification`.
- Do not map cube, cubic mortar, unspecified specimen, non-28-day strength or an ambiguous mix to an EN strength band.
- Do not convert cube strength to cylinder strength.
- Map the proxy only as follows: `<16` when below 16; `16 to 20` when 16 through 20 inclusive; `25 to 35` when 25 through 35 inclusive; `>35` when above 35. Return `NO_TABLE_VALUE` for values strictly between 20 and 25.
- Exposure is an externally supplied scenario. Never infer it from the paper.

Return valid JSON only, following the schema below. Use JSON null rather than an empty string for missing values. Do not add keys.

```json
{
  "paper_id": "string",
  "paper_identity": {
    "title": "string|null",
    "doi": "string|null",
    "journal": "string|null",
    "year": "integer|null",
    "identity_evidence": {"page": "integer|null", "location": "string|null", "snippet": "string|null"}
  },
  "materials": [
    {
      "material_id": "string",
      "raw_name": "string|null",
      "normalized_family": "string|null",
      "source_or_treatment": "string|null",
      "mixture_role": "cement_replacement|binder_replacement|aggregate_replacement|activator|other|null",
      "chemistry_pct": {"CaO": "number|null", "SiO2": "number|null", "Al2O3": "number|null", "Fe2O3": "number|null", "MgO": "number|null", "LOI": "number|null"},
      "density_g_cm3": "number|null",
      "evidence": [{"field": "string", "page": "integer|null", "location": "string|null", "snippet": "string|null"}]
    }
  ],
  "mixes": [
    {
      "mix_id": "string",
      "paired_control_id": "string|null",
      "material_id": "string|null",
      "replacement_target": "cement|total_binder|fine_aggregate|coarse_aggregate|other|null",
      "replacement_basis": "mass|volume|null",
      "replacement_pct_reported": "number|null",
      "cement_type": "string|null",
      "cement_kg_m3": "number|null",
      "waste_binder_kg_m3": "number|null",
      "other_binders": [{"name": "string", "kg_m3": "number|null"}],
      "water_kg_m3": "number|null",
      "fine_aggregate_kg_m3": "number|null",
      "coarse_aggregate_kg_m3": "number|null",
      "recycled_coarse_aggregate_kg_m3": "number|null",
      "admixtures": [{"name": "string", "amount": "number|null", "unit": "string|null"}],
      "compressive_strengths": [{"age_days": "number|null", "strength_MPa": "number|null", "specimen": "string|null", "basis": "mean|characteristic|declared_class|graph_derived|other|null", "replicate_n": "integer|null", "evidence": {"page": "integer|null", "location": "string|null", "snippet": "string|null"}}],
      "source_evidence": [{"field": "string", "reported_value": "string|null", "page": "integer|null", "location": "string|null", "snippet": "string|null"}],
      "derived_qc": {
        "binder_kg_m3": "number|null",
        "replacement_pct_calculated": "number|null",
        "replacement_difference_pp": "number|null",
        "water_binder_calculated": "number|null",
        "water_binder_difference": "number|null",
        "co_intervention": "boolean|null"
      },
      "en_interface": {
        "reported_characteristic_cylinder_MPa": "number|null",
        "fcm_28d_cylinder_MPa": "number|null",
        "fck_proxy_MPa": "number|null",
        "strength_band": "<16 MPa|16 to 20 MPa|25 to 35 MPa|>35 MPa|NO_TABLE_VALUE|null",
        "mapping_status": "SOURCE_CLASS|RESEARCH_PROXY|BLOCKED|null",
        "mapping_note": "string|null"
      },
      "record_status": "READY|REVIEW|BLOCKED",
      "review_flags": ["string"]
    }
  ]
}
```

### Targeted re-check message

The first extraction failed one or more deterministic checks. Re-read only the supplied evidence regions and return a corrected complete JSON object using the identical schema. Correct a value only when the paper supports the correction. Otherwise keep it null and add a precise review flag. Do not remove a flag merely to make the record pass.

## A0 — Naive baseline prompt

Read the supplied concrete research paper and extract the material used, cement replacement percentage, cement/binder composition, mix proportions, compressive strength and chemical composition. Return a clear JSON summary with one item per mixture. Include EN strength information useful for carbonation calculations where possible.

No targeted re-check is run for A0.

## Frozen one-factor ablation instructions

Every ablation starts from A1 and changes only the instruction below.

### A2 — No targeted retrieval

Provide the complete broad paper text representation directly to A1. Do not run a page/region retrieval stage. All other A1 instructions and validation remain unchanged.

### A3 — No schema constraint

Replace the final JSON-schema instruction in A1 with: “Return the extracted information in any clear structure you consider appropriate.” Retain retrieval, evidence requirements, deterministic verification, re-check and abstention. The evaluator maps the response to the frozen schema without correcting content.

### A4 — No evidence grounding

Remove all requirements to provide pages, tables, figures, snippets or reported source values. Retain the same output fields, targeted retrieval, normalization, deterministic verification, re-check and abstention. Evidence-location metrics are not applicable to this arm; unsupported-value checking still compares outputs with the human gold source.

### A5 — No engineering verification

Remove binder-sum, replacement-ratio, water/binder, test-age, specimen and control-link checks, and do not run the targeted re-check message. Retain targeted retrieval, the frozen JSON schema, source evidence and abstention for visibly missing information.

### A6 — No abstention

Replace “return null and a review flag” with: “Return your single best value for every required field even when evidence is incomplete.” Retain targeted retrieval, schema, evidence fields and engineering verification. Any unsupported completion is counted by the unsupported-value metric.

## Freeze and run-identification block

Before the first blind call, fill these values once in the run manifest and keep them unchanged for A0–A6:

- provider and model ID;
- immutable model snapshot/version where available;
- PDF-to-text/vision representation version;
- maximum input/output tokens;
- random seed where supported;
- runner code commit or file hash;
- prompt file SHA-256;
- development protocol SHA-256.

