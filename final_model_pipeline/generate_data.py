from datetime import timedelta

import numpy as np
import pandas as pd

# ==========================================
# 🛑 EMPIRICAL CALIBRATION ZONE 🛑
# ==========================================
SHAKE_TABLE_DANGEROUS_PEAK = 100.0  # 60Hz to 138Hz range
SHAKE_TABLE_MODERATE_PEAK = 50.0  # Your lab: ~47Hz is Moderate
SHAKE_TABLE_MINOR_PEAK = 25.0
# ==========================================


def generate_continuous_hybrid_dataset(phivolcs_path, output_path):
    print("Loading PHIVOLCS Master Catalogue magnitudes...")
    phivolcs = pd.read_csv(phivolcs_path)
    # We only need the physical magnitudes, not the broken historical dates
    phivolcs["Magnitude"] = phivolcs[["Ml", "Mb", "Ms"]].max(axis=1)
    magnitudes = phivolcs["Magnitude"].dropna().values

    # Determine timeline length: 15 minutes (90 rows of 10s) per historical earthquake
    rows_per_quake = 90
    total_rows = len(magnitudes) * rows_per_quake

    print(f"Generating continuous master timeline of {total_rows} rows...")
    start_time = pd.Timestamp("2026-01-01 00:00:00")
    timestamps = [start_time + timedelta(seconds=i * 10) for i in range(total_rows)]

    # Initialize the entire timeline with our calibrated Class 0 and Class 1 noise floor
    frequencies = np.zeros(total_rows)
    labels = np.zeros(total_rows, dtype=int)

    for i in range(total_rows):
        if i % 10 == 0:
            # Occasional machine wind-down / minor noise (Class 1)
            frequencies[i] = np.random.uniform(3.0, 15.0)
            labels[i] = 1
        else:
            # Standard ambient isolation pad noise floor (Class 0)
            frequencies[i] = np.random.uniform(0.0, 2.5)
            labels[i] = 0

    print("Injecting historical earthquake signatures into the timeline...")
    # Inject one earthquake into the center of every 15-minute block
    for idx, mag in enumerate(magnitudes):
        center_index = (idx * rows_per_quake) + (rows_per_quake // 2)

        if mag >= 6.0:
            label = 3
            peak_base = SHAKE_TABLE_DANGEROUS_PEAK
        elif mag >= 4.0:
            label = 2
            peak_base = SHAKE_TABLE_MODERATE_PEAK
        else:
            label = 1
            peak_base = SHAKE_TABLE_MINOR_PEAK

        # Apply the [-2, 3] earthquake window (50 seconds total)
        for offset in range(-2, 3):
            target_idx = center_index + offset
            if 0 <= target_idx < total_rows:
                frequencies[target_idx] = max(
                    0, np.random.normal(peak_base, peak_base * 0.2)
                )
                labels[target_idx] = label

    # Build final DataFrame
    df_hybrid = pd.DataFrame(
        {"timestamp": timestamps, "peak_frequency": frequencies, "label": labels}
    )

    df_hybrid.to_csv(output_path, index=False)
    print(f"Successfully generated continuous univariate dataset: {output_path}")
    print("\nClass Distribution:")
    print(df_hybrid["label"].value_counts())


if __name__ == "__main__":
    PHIVOLCS_FILE = "phivolcs_master_catalogue.csv"
    OUTPUT_FILE = "wida_calibrated_hybrid_data.csv"

    generate_continuous_hybrid_dataset(PHIVOLCS_FILE, OUTPUT_FILE)
