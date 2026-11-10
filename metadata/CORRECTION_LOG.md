# Configuration Label Correction

## Scope

The correction concerns configuration labels, not reference records or extracted values.

During the experiment, several run directories retained historical configuration labels that no longer matched the final component definitions used in the manuscript. The final reporting labels were assigned from the component actually enabled or removed in each run. The mapping was frozen before calculation of the reported aggregate table:

| Final label | Historical result label | Final definition |
|---|---|---|
| A0 | A0 | Naive baseline |
| A1 | A4 | Complete workflow |
| A2 | A2 | No targeted retrieval |
| A3 | A3 | No fixed JSON template |
| A4 | A5 | No evidence grounding |
| A5 | A1 | No engineering verification |
| A6 | A6 | No abstention |

The mapping was determined from the recorded configuration logic and run metadata. Performance values were not used to choose the mapping. The paper-level counts in `scoring/input/paper_level_scoring_counts.csv` already use the final labels above. The mapping implementation is preserved in `analysis/configuration_label_mapping.py`.

The human-verified reference records were unchanged by this label correction.
