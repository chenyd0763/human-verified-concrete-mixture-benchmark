# Human-Verified Concrete Mixture Benchmark

This repository contains the public data and evaluation materials supporting the manuscript *From Waste-Derived Concrete Literature to Traceable Mixture Data for Carbonation Assessment: An Evidence-Grounded, Language-Model-Assisted Workflow*.

## Public release

The benchmark contains consensus reference records for 18 blind-test articles:

- 175 concrete mixture records;
- 566 compressive-strength observations;
- material metadata and field-level source locations;
- aggregate and paper-level evaluation counts for configurations A0--A6.

A primary annotator reconstructed the eligible records from the source articles. A second concrete researcher verified all critical numerical fields against the original articles. Disagreements were resolved by consensus through direct reinspection of the relevant tables, figures, and passages. The released workbook contains the resulting consensus reference records used for the reported evaluation.

## Repository contents

- `data/`: human-verified benchmark workbook;
- `corpus/`: article inventory and corpus-screening description;
- `prompts/`: frozen extraction prompts used for A0--A6;
- `schema/`: documented release schema and the 11 scored core fields;
- `scoring/`: metric definitions, paper-level counts, and a script that reproduces the published aggregate metrics;
- `analysis/`: bootstrap and downstream scenario-analysis scripts;
- `metadata/`: final release status, execution record, correction log, and checksums.

## Reproduce the aggregate metrics

Python 3.9 or later is sufficient; the scoring script uses only the standard library.

```bash
python scoring/score_aggregate_metrics.py \
  scoring/input/paper_level_scoring_counts.csv \
  scoring/reproduced_aggregate_metrics.csv
```

The script calculates mixture recall, core-field accuracy, complete-row accuracy, and unsupported non-null rate from the released paper-level counts. The expected published values are stored in `scoring/tests/expected_published_aggregate_metrics.csv`.

## Source access and copyright

The repository identifies all source articles and records page and table or figure locations for the annotated evidence. Publisher-provided article files and verbatim source passages are not redistributed. Readers can verify the listed locations in the cited articles through their institutional or lawful access.

## Version

- Release: `v1.2`
- Reference status: human-verified consensus benchmark

## License

The released dataset, documentation, and original analysis code are licensed under CC BY 4.0. Bibliographic metadata and third-party article content remain subject to their original terms.
