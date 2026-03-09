import pandas as pd
from pathlib import Path

MAX_CSV_SIZE_BYTES = 500 * 1024  # 500 KB


def parquet_to_csv_limited(parquet_file, csv_file, max_bytes=MAX_CSV_SIZE_BYTES):
    """
    Convert a Parquet file to a CSV file with a strict size limit.
    The CSV will be truncated row-by-row to stay <= max_bytes.
    """
    parquet_file = Path(parquet_file)
    csv_file = Path(csv_file)

    try:
        df = pd.read_parquet(parquet_file)
    except Exception as e:
        print(f"❌ Failed to read parquet file: {e}")
        return

    if df.empty:
        print("⚠️ Parquet file is empty. Writing empty CSV with header only.")
        df.head(0).to_csv(csv_file, index=False)
        return

    # Write header first
    header_csv = df.head(0).to_csv(index=False)
    header_size = len(header_csv.encode("utf-8"))

    if header_size >= max_bytes:
        print("❌ CSV header alone exceeds size limit. Aborting.")
        return

    rows = []
    current_size = header_size

    for _, row in df.iterrows():
        row_csv = row.to_frame().T.to_csv(index=False, header=False)
        row_size = len(row_csv.encode("utf-8"))

        if current_size + row_size > max_bytes:
            break

        rows.append(row)
        current_size += row_size

    if not rows:
        print("⚠️ No rows could fit under size limit. Writing header only.")
        df.head(0).to_csv(csv_file, index=False)
        return

    out_df = pd.DataFrame(rows, columns=df.columns)
    out_df.to_csv(csv_file, index=False)

    final_size = csv_file.stat().st_size
    print(f"✅ Converted '{parquet_file}' → '{csv_file}'")
    print(f"📏 Output size: {final_size} bytes ({final_size / 1024:.2f} KB)")
    print(f"🧮 Rows written: {len(out_df)} / {len(df)}")


# 👇 Put your file paths here
parquet_to_csv_limited(
    r"E:\efficient-cybersecurity-tool\malware\data\test\test_ember_2018_v2_features.parquet",
    r"E:\efficient-cybersecurity-tool\sample testing\malware\test_ember_2018_v2_features.csv"
)
