import pandas as pd


def compile_master_catalogue(file_paths, output_path):
    all_data = []

    col_names = [
        "Year",
        "Month",
        "Day",
        "Hour",
        "Minute",
        "Second",
        "Latitude",
        "Longitude",
        "Depth",
        "Ml",
        "Mb",
        "Ms",
        "Intensity",
    ]

    for file in file_paths:
        # Explicitly load the Excel file object to access all sheet names safely
        xls = pd.ExcelFile(file)

        # Iterate through every explicit tab name found in the file
        for sheet_name in xls.sheet_names:
            print(f"Processing {file} -> Tab: {sheet_name}...")

            # Parse the specific sheet from the already-loaded file object
            df_clean = pd.read_excel(
                xls, sheet_name=sheet_name, skiprows=10, names=col_names
            )
            all_data.append(df_clean)

    # 1. Concatenate all tabs
    master_df = pd.concat(all_data, ignore_index=True)

    # 2. Enforce strict numeric types (Coerce non-numbers to NaN)
    time_cols = ["Year", "Month", "Day", "Hour", "Minute", "Second"]
    for col in time_cols:
        master_df[col] = pd.to_numeric(master_df[col], errors="coerce")

    # 3. Purge invalid rows
    master_df = master_df.dropna(subset=["Year", "Month", "Day"])
    master_df = master_df[master_df["Year"] >= 1900]

    # 4. Create the unified timestamp (Aligning GMT to PST)
    master_df["timestamp"] = pd.to_datetime(
        {
            "year": master_df["Year"],
            "month": master_df["Month"],
            "day": master_df["Day"],
            "hour": master_df["Hour"].fillna(0),
            "minute": master_df["Minute"].fillna(0),
            "second": master_df["Second"].fillna(0),
        }
    ) + pd.Timedelta(hours=8)

    print(master_df)

    # 5. Deduplicate overlapping events
    initial_count = len(master_df)
    master_df = master_df.drop_duplicates(subset=["timestamp", "Latitude", "Longitude"])
    final_count = len(master_df)

    # 6. Sort chronologically
    master_df = master_df.sort_values("timestamp").reset_index(drop=True)

    print("-" * 30)
    print(f"Total valid records parsed: {initial_count}")
    print(f"Duplicate events removed: {initial_count - final_count}")
    print(f"Final Master Catalogue size: {final_count} unique events")

    master_df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    files_to_merge = [
        "./Earthquake Catalogue of MARIKINA.xlsx",
        "./Earthquake Catalogue of Rizal and vicinity.xlsx",
    ]
    compile_master_catalogue(files_to_merge, "phivolcs_master_catalogue.csv")
