"""Reproduce the published aggregate extraction metrics from paper-level counts."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


CORE_FIELD_COUNT = 11
CONFIG_ORDER = ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]


def integer(row: dict[str, str], key: str) -> int:
    value = row.get(key, "").strip()
    return int(value) if value else 0


def aggregate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["config"]].append(row)

    output: list[dict[str, object]] = []
    for config in CONFIG_ORDER:
        config_rows = grouped[config]
        reference = sum(integer(row, "reference_rows") for row in config_rows)
        predicted = sum(integer(row, "predicted_rows") for row in config_rows)
        matched = sum(integer(row, "common_rows") for row in config_rows)
        core_correct = sum(integer(row, "core_correct") for row in config_rows)
        complete = sum(integer(row, "complete_core_rows") for row in config_rows)
        unsupported = sum(integer(row, "unsupported_nonnull_core_values") for row in config_rows)
        predicted_nonnull = sum(integer(row, "predicted_nonnull_core_values") for row in config_rows)
        output.append(
            {
                "configuration": config,
                "papers": len(config_rows),
                "reference_rows": reference,
                "predicted_rows": predicted,
                "matched_rows": matched,
                "core_correct": core_correct,
                "core_expected": CORE_FIELD_COUNT * reference,
                "complete_core_rows": complete,
                "unsupported_nonnull_core_values": unsupported,
                "predicted_nonnull_core_values": predicted_nonnull,
                "mixture_recall": matched / reference,
                "core_field_accuracy": core_correct / (CORE_FIELD_COUNT * reference),
                "complete_row_accuracy": complete / reference,
                "unsupported_core_rate": unsupported / predicted_nonnull if predicted_nonnull else "",
            }
        )
    return output


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: score_aggregate_metrics.py INPUT.csv OUTPUT.csv")
    source = Path(sys.argv[1])
    destination = Path(sys.argv[2])
    with source.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    result = aggregate(rows)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    for row in result:
        print(
            f"{row['configuration']}: recall={row['mixture_recall']:.4f}, "
            f"core={row['core_field_accuracy']:.4f}, "
            f"complete={row['complete_row_accuracy']:.4f}, "
            f"unsupported={row['unsupported_core_rate']:.4f}"
        )


if __name__ == "__main__":
    main()
