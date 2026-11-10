import csv
import math
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "01a06040-7c0b-7213-9435-860b1f0e0ee2" / "EN_16757_2022_Table_G1_transcription.xlsx"
OUTPUT = ROOT / "outputs" / "extraction_experiment" / "blind" / "EN_G1_1m2_50_100y_uptake_factor_matrix_v1_3.csv"
BANDS = [
    ("<16", 5),
    ("16 to 20", 6),
    ("25 to 35", 7),
    (">35", 8),
]

workbook = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
sheet = workbook["Table G.1"]
records = []
for row in range(8, 16):
    lookup_id = sheet.cell(row, 1).value
    if not lookup_id:
        continue
    dc_percent = sheet.cell(row, 9).value
    for band, column in BANDS:
        k = sheet.cell(row, column).value
        for years in (50, 100):
            if k is None:
                depth_mm = None
                factor = None
                status = "NO TABLE VALUE"
            else:
                depth_mm = float(k) * math.sqrt(years)
                # For A_exp = 1 m2: M_CO2 = factor * C * U_tcc.
                factor = (depth_mm / 1000.0) * (float(dc_percent) / 100.0)
                status = "CALCULATED_FROM_TRANSCRIPTION"
            records.append(
                {
                    "lookup_id": lookup_id,
                    "application": sheet.cell(row, 2).value,
                    "environment": sheet.cell(row, 3).value,
                    "condition": sheet.cell(row, 4).value,
                    "strength_band": band,
                    "service_life_years": years,
                    "k_mm_per_sqrt_year": k,
                    "Dc_percent": dc_percent,
                    "carbonation_depth_mm": depth_mm,
                    "uptake_factor_per_C_times_Utcc_for_1m2": factor,
                    "status": status,
                    "restriction": "Multiply the factor by validated C and U_tcc to obtain M_CO2; EN transcription requires licensed-source verification.",
                }
            )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

print(f"Wrote {len(records)} scenario rows to {OUTPUT}")

