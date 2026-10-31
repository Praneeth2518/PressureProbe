from pathlib import Path

import pandas as pd


PSI_AVERAGE_METRICS = [
    "cpu_some_avg10",
    "cpu_some_avg60",
    "cpu_some_avg300",
    "cpu_full_avg10",
    "cpu_full_avg60",
    "cpu_full_avg300",
    "memory_some_avg10",
    "memory_some_avg60",
    "memory_some_avg300",
    "memory_full_avg10",
    "memory_full_avg60",
    "memory_full_avg300",
    "io_some_avg10",
    "io_some_avg60",
    "io_some_avg300",
    "io_full_avg10",
    "io_full_avg60",
    "io_full_avg300",
]


def load_psi_csv(file_path):
    """Load and validate a PSI CSV file."""
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"PSI data file not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("PSI data file contains no samples.")

    required_columns = ["timestamp_utc", *PSI_AVERAGE_METRICS]
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        utc=True,
        errors="raise",
    )

    if df["timestamp_utc"].isna().any():
        raise ValueError("Timestamps contain missing values.")

    if not df["timestamp_utc"].is_monotonic_increasing:
        raise ValueError("Timestamps must be in chronological order.")

    for column in PSI_AVERAGE_METRICS:
        df[column] = pd.to_numeric(df[column], errors="raise")

        if df[column].isna().any():
            raise ValueError(
                f"Metric '{column}' contains missing values."
            )

        if not df[column].map(
            lambda value: pd.notna(value) and abs(value) != float("inf")
        ).all():
            raise ValueError(
                f"Metric '{column}' contains non-finite values."
            )

        if (df[column] < 0).any():
            raise ValueError(
                f"Metric '{column}' contains negative values."
            )

    return df


def summarize_psi_data(df):
    """Calculate descriptive statistics for PSI rolling averages."""
    summary = df[PSI_AVERAGE_METRICS].agg(
        ["min", "mean", "max"]
    ).T

    summary["nonzero_samples"] = (
        df[PSI_AVERAGE_METRICS] != 0
    ).sum()

    summary["total_samples"] = len(df)

    summary["nonzero_percentage"] = (
        summary["nonzero_samples"]
        / summary["total_samples"]
        * 100
    )

    return summary.round(6)


def analyze_psi_file(file_path):
    """Load a PSI dataset and return its data and summary."""
    df = load_psi_csv(file_path)
    summary = summarize_psi_data(df)

    return df, summary


if __name__ == "__main__":
    datasets = {
        "BASELINE": "data/raw/psi_baseline.csv",
        "CPU CONTENTION": "data/raw/psi_cpu_contention.csv",
    }

    for name, file_path in datasets.items():
        df, summary = analyze_psi_file(file_path)

        duration = (
            df["timestamp_utc"].iloc[-1]
            - df["timestamp_utc"].iloc[0]
        ).total_seconds()

        print(f"\n{'=' * 75}")
        print(name)
        print(f"Samples: {len(df)}")
        print(f"Duration: {duration:.2f} seconds")
        print("\nPSI rolling-average summary:")
        print(summary.to_string())