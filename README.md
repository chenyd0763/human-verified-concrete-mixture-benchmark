# Human-Verified Concrete Mixture Benchmark

This repository contains the human-verified reference dataset and audit-corrected evaluation results supporting the manuscript:

> *From Waste-Derived Concrete Literature to Traceable Mixture Data for Carbonation Assessment: An Evidence-Grounded, Language-Model-Assisted Workflow*

## Dataset contents

The Excel workbook contains eight worksheets:

- `ReadMe`: dataset scope, verification protocol, and interpretation notes;
- `Paper_Index`: bibliographic metadata for the 18 blind-test articles;
- `Mixtures`: 175 human-verified concrete mixture records;
- `Strength_Observations`: 566 compressive-strength observations;
- `Material_Metadata`: reported material identity, treatment, density, and chemistry information;
- `Source_Evidence`: page- and location-level provenance for extracted fields;
- `Evaluation_Results`: final audit-corrected A0–A6 aggregate metrics;
- `Data_Dictionary`: definitions of key fields and metrics.

## Human verification

A primary annotator reconstructed all eligible mixtures and strength observations from the 18 full-text articles. A second concrete researcher independently reviewed the critical numerical fields in all 18 articles against the original sources. Disagreements were resolved by consensus through direct reinspection of the relevant tables, figures, and passages. Blank cells indicate values that were not reported, were not applicable, or could not be defensibly resolved from the source article.

## Version

- Dataset version: `v1.1`
- Release date: 18 October 2026
- File: `S2_minimal_dataset_human_verified_v1.1.xlsx`

## Citation

Until the associated article is published, please cite this repository and the `v1.1` release URL. The formal article citation and data DOI will be added when available.

## License

The dataset and accompanying documentation are licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). See `LICENSE.md`.

