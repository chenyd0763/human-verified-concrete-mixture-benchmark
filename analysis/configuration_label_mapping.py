import csv
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLIND = ROOT / "outputs" / "extraction_experiment" / "blind"
SOURCE = BLIND / "full_paper_config_metrics_v1_2.csv"
PAPER_OUTPUT = BLIND / "full_paper_config_metrics_audit_corrected_v1_4.csv"
AGG_OUTPUT = BLIND / "full_aggregate_metrics_audit_corrected_v1_4.csv"
CI_OUTPUT = BLIND / "paper_level_bootstrap_ci_audit_corrected_v1_4.csv"
DELTA_OUTPUT = BLIND / "paired_delta_vs_A1_bootstrap_audit_corrected_v1_4.csv"

# Audit-confirmed identity mapping: target manuscript configuration <- old result row.
SOURCE_FOR_TARGET = {
    "A0": "A0",
    "A1": "A4",
    "A2": "A2",
    "A3": "A3",
    "A4": "A5",
    "A5": "A1",
    "A6": "A6",
}
SEED = 20260929
RESAMPLES = 10_000
BOOTSTRAP_METRICS = [
    "mix_id_recall",
    "complete_core_row_accuracy",
    "unsupported_nonnull_core_rate",
]


def number(value):
    return None if value in (None, "") else float(value)


def percentile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
    old_rows = list(csv.DictReader(handle))

old_by_pair = {(row["paper_id"], row["config"]): row for row in old_rows}
paper_ids = sorted({row["paper_id"] for row in old_rows})
corrected = []
for paper_id in paper_ids:
    for target, source in SOURCE_FOR_TARGET.items():
        row = dict(old_by_pair[(paper_id, source)])
        row["config"] = target
        row["audit_source_config"] = source
        # Evidence completeness was controlled by the historical configuration
        # label and therefore cannot be recovered by result-row remapping.
        row["evidence_complete_rows"] = ""
        row["evidence_complete_rate"] = ""
        corrected.append(row)

fieldnames = list(corrected[0].keys())
with PAPER_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(corrected)

aggregate_records = []
for scope, scoped_rows in [
    ("all18_descriptive", corrected),
    ("clean16", [row for row in corrected if row["reference_qc"] == "clean"]),
]:
    for config in SOURCE_FOR_TARGET:
        rows = [row for row in scoped_rows if row["config"] == config]
        reference_rows = sum(int(row["reference_rows"]) for row in rows)
        predicted_rows = sum(int(row["predicted_rows"]) for row in rows)
        common_rows = sum(int(row["common_rows"]) for row in rows)
        core_correct = sum(int(row["core_correct"]) for row in rows)
        # Each matched reference row has 11 frozen core fields.
        core_expected = 11 * reference_rows
        complete_core = sum(int(row["complete_core_rows"]) for row in rows)
        unsupported = sum(int(row["unsupported_nonnull_core_values"]) for row in rows)
        predicted_nonnull = sum(int(row["predicted_nonnull_core_values"]) for row in rows)
        aggregate_records.append({
            "scope": scope,
            "config": config,
            "papers": len(rows),
            "reference_rows": reference_rows,
            "predicted_rows": predicted_rows,
            "common_rows": common_rows,
            "mix_id_recall_micro": common_rows / reference_rows,
            "core_field_accuracy_micro_expected_denominator": core_correct / core_expected,
            "complete_core_row_accuracy_micro": complete_core / reference_rows,
            "unsupported_nonnull_core_rate_micro": unsupported / predicted_nonnull if predicted_nonnull else "",
        })

with AGG_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=aggregate_records[0].keys())
    writer.writeheader()
    writer.writerows(aggregate_records)

rng = random.Random(SEED)
ci_records = []
delta_records = []
for scope, scoped_rows in [
    ("all18_paper_macro", corrected),
    ("clean16_paper_macro", [row for row in corrected if row["reference_qc"] == "clean"]),
]:
    by_pair = {(row["paper_id"], row["config"]): row for row in scoped_rows}
    ids = sorted({row["paper_id"] for row in scoped_rows})
    for config in SOURCE_FOR_TARGET:
        for metric in BOOTSTRAP_METRICS:
            values = [number(by_pair[(paper_id, config)][metric]) for paper_id in ids]
            values = [value for value in values if value is not None]
            estimate = sum(values) / len(values)
            samples = [sum(values[rng.randrange(len(values))] for _ in values) / len(values) for _ in range(RESAMPLES)]
            ci_records.append({
                "scope": scope,
                "config": config,
                "metric": metric,
                "papers_with_value": len(values),
                "estimate": estimate,
                "ci95_lower": percentile(samples, 0.025),
                "ci95_upper": percentile(samples, 0.975),
                "bootstrap_resamples": RESAMPLES,
                "seed": SEED,
            })
    for config in SOURCE_FOR_TARGET:
        if config == "A1":
            continue
        for metric in ["mix_id_recall", "complete_core_row_accuracy"]:
            differences = [
                number(by_pair[(paper_id, config)][metric]) - number(by_pair[(paper_id, "A1")][metric])
                for paper_id in ids
            ]
            estimate = sum(differences) / len(differences)
            samples = [sum(differences[rng.randrange(len(differences))] for _ in differences) / len(differences) for _ in range(RESAMPLES)]
            delta_records.append({
                "scope": scope,
                "config": config,
                "metric": metric,
                "papers": len(differences),
                "mean_paired_delta_vs_A1": estimate,
                "ci95_lower": percentile(samples, 0.025),
                "ci95_upper": percentile(samples, 0.975),
                "bootstrap_resamples": RESAMPLES,
                "seed": SEED,
            })

for path, records in [(CI_OUTPUT, ci_records), (DELTA_OUTPUT, delta_records)]:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

print(f"Wrote {PAPER_OUTPUT}")
print(f"Wrote {AGG_OUTPUT}")
print(f"Wrote {CI_OUTPUT}")
print(f"Wrote {DELTA_OUTPUT}")
print("Applied audit mapping to 126 paper/config records and recomputed paper-level bootstrap intervals.")
