import csv
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "extraction_experiment" / "blind" / "full_paper_config_metrics_v1_2.csv"
OUTPUT = ROOT / "outputs" / "extraction_experiment" / "blind" / "paper_level_bootstrap_ci_v1_3.csv"
DELTA_OUTPUT = ROOT / "outputs" / "extraction_experiment" / "blind" / "paired_delta_vs_A1_bootstrap_v1_3.csv"
SEED = 20260929
RESAMPLES = 10_000
METRICS = [
    "mix_id_recall",
    "complete_core_row_accuracy",
    "evidence_complete_rate",
    "unsupported_nonnull_core_rate",
]


def number(value):
    if value in (None, ""):
        return None
    return float(value)


def percentile(values, probability):
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
    source_rows = list(csv.DictReader(handle))

configs = sorted({row["config"] for row in source_rows})
expected_pairs = {(row["paper_id"], row["config"]) for row in source_rows}
if len(source_rows) != 126 or len(expected_pairs) != 126:
    raise RuntimeError(f"Expected 126 unique paper/config rows; found {len(source_rows)} rows and {len(expected_pairs)} unique pairs")
rng = random.Random(SEED)
records = []
delta_records = []
for scope, scoped_rows in [
    ("all18_paper_macro", source_rows),
    ("clean16_paper_macro", [row for row in source_rows if row["reference_qc"] == "clean"]),
]:
    by_config = defaultdict(list)
    for row in scoped_rows:
        by_config[row["config"]].append(row)
    expected_count = 18 if scope.startswith("all18") else 16
    if any(len(by_config[config]) != expected_count for config in configs):
        raise RuntimeError(f"{scope} must contain {expected_count} papers for every configuration")
    baseline = {}
    for config in configs:
        rows = by_config[config]
        for metric in METRICS:
            values = [number(row[metric]) for row in rows]
            values = [value for value in values if value is not None]
            estimate = sum(values) / len(values)
            samples = []
            for _ in range(RESAMPLES):
                draw = [values[rng.randrange(len(values))] for _ in values]
                samples.append(sum(draw) / len(draw))
            lower = percentile(samples, 0.025)
            upper = percentile(samples, 0.975)
            if config == "A0":
                baseline[metric] = estimate
            records.append(
                {
                    "scope": scope,
                    "config": config,
                    "metric": metric,
                    "papers_with_value": len(values),
                    "estimate": estimate,
                    "ci95_lower": lower,
                    "ci95_upper": upper,
                    "absolute_delta_vs_A0": estimate - baseline.get(metric, estimate),
                    "bootstrap_resamples": RESAMPLES,
                    "seed": SEED,
                }
            )
    by_pair = {(row["paper_id"], row["config"]): row for row in scoped_rows}
    paper_ids = sorted({row["paper_id"] for row in scoped_rows})
    for config in configs:
        if config == "A1":
            continue
        for metric in ["mix_id_recall", "complete_core_row_accuracy"]:
            differences = []
            for paper_id in paper_ids:
                candidate = number(by_pair[(paper_id, config)][metric])
                full = number(by_pair[(paper_id, "A1")][metric])
                if candidate is not None and full is not None:
                    differences.append(candidate - full)
            estimate = sum(differences) / len(differences)
            samples = []
            for _ in range(RESAMPLES):
                draw = [differences[rng.randrange(len(differences))] for _ in differences]
                samples.append(sum(draw) / len(draw))
            delta_records.append(
                {
                    "scope": scope,
                    "config": config,
                    "metric": metric,
                    "papers": len(differences),
                    "mean_paired_delta_vs_A1": estimate,
                    "ci95_lower": percentile(samples, 0.025),
                    "ci95_upper": percentile(samples, 0.975),
                    "bootstrap_resamples": RESAMPLES,
                    "seed": SEED,
                }
            )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

with DELTA_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=delta_records[0].keys())
    writer.writeheader()
    writer.writerows(delta_records)

print(f"Wrote {OUTPUT}")
print(f"Wrote {DELTA_OUTPUT}")
print("Verified 126 unique paper/config rows, 18 papers per configuration, and 16 clean-compatible papers per configuration.")
