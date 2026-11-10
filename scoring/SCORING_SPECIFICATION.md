# Scoring Specification

## Row matching

Reference and predicted mixtures are matched within each paper by source mixture identifier after trimming surrounding whitespace. A missing reference mixture remains in every reference-based denominator. An unmatched predicted mixture contributes to the predicted-row and unsupported-value counts.

## Core fields

The 11 scored fields are listed in `../schema/core_fields.json`.

- Numeric values are compared after unit normalization using an absolute tolerance of 0.011.
- Categorical and identifier fields require exact normalized equality.
- A null reference field matches only a null prediction.
- Empty strings are normalized to null before scoring.

## Metrics

For each configuration, let:

- `R` be the number of reference mixtures;
- `M` be the number of matched reference mixtures;
- `C` be the number of correct core-field values;
- `Q` be the number of matched mixtures correct on all 11 core fields;
- `U` be the number of populated predicted core values lacking reference support;
- `P` be the number of populated predicted core values.

The reported micro-aggregated metrics are:

- mixture recall = `M / R`;
- core-field accuracy = `C / (11 * R)`;
- complete-row accuracy = `Q / R`;
- unsupported non-null rate = `U / P`.

These denominators retain missing mixtures as incorrect. Core-field accuracy therefore measures expected-record completeness and correctness, not accuracy among recovered rows alone.

## Published configuration labels

The released paper-level counts already use the final A0--A6 definitions. The historical label correction is documented in `../metadata/CORRECTION_LOG.md`.

## Reproduction

Run `score_aggregate_metrics.py` on `input/paper_level_scoring_counts.csv`. The script uses raw integer counts and writes one aggregate row per configuration.
