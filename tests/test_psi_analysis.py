import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.psi_analysis import (
    PSI_AVERAGE_METRICS,
    load_psi_csv,
    summarize_psi_data,
)


class TestPSIAnalysis(unittest.TestCase):

    def create_valid_dataframe(self):
        """Create a small, valid PSI dataset for testing."""
        data = {
            "timestamp_utc": [
                "2026-10-14T10:00:00+00:00",
                "2026-10-14T10:00:01+00:00",
                "2026-10-14T10:00:02+00:00",
            ]
        }

        for metric in PSI_AVERAGE_METRICS:
            data[metric] = [0.0, 0.1, 0.2]

        return pd.DataFrame(data)

    def test_load_valid_csv(self):
        """A valid CSV should load with three samples."""
        df = self.create_valid_dataframe()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "valid.csv"
            df.to_csv(file_path, index=False)

            result = load_psi_csv(file_path)

        self.assertEqual(len(result), 3)
        self.assertTrue(
            result["timestamp_utc"].is_monotonic_increasing
        )

    def test_summary_statistics(self):
        """Summary statistics should match known values."""
        df = self.create_valid_dataframe()

        summary = summarize_psi_data(df)

        self.assertAlmostEqual(
            summary.loc["cpu_some_avg10", "mean"],
            0.1,
        )
        self.assertAlmostEqual(
            summary.loc["cpu_some_avg10", "max"],
            0.2,
        )
        self.assertEqual(
            summary.loc["cpu_some_avg10", "nonzero_samples"],
            2,
        )

    def test_missing_required_column(self):
        """A CSV missing a required metric should be rejected."""
        df = self.create_valid_dataframe()
        df = df.drop(columns=["cpu_some_avg10"])

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "invalid.csv"
            df.to_csv(file_path, index=False)

            with self.assertRaises(ValueError):
                load_psi_csv(file_path)

    def test_unsorted_timestamps(self):
        """Out-of-order timestamps should be rejected."""
        df = self.create_valid_dataframe()
        df = df.iloc[::-1].reset_index(drop=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "unsorted.csv"
            df.to_csv(file_path, index=False)

            with self.assertRaises(ValueError):
                load_psi_csv(file_path)


if __name__ == "__main__":
    unittest.main()