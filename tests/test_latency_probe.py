import csv
import tempfile
import unittest
from pathlib import Path

from src.latency_probe import (
    measure_operation_latency,
    save_latency_csv,
    summarize_latency,
)


class TestLatencyProbe(unittest.TestCase):

    def test_measure_operation_latency(self):
        measurements = measure_operation_latency(
            lambda: sum(range(10)),
            repetitions=5,
        )

        self.assertEqual(len(measurements), 5)

        for index, measurement in enumerate(measurements, start=1):
            self.assertEqual(measurement["sample_number"], index)
            self.assertIn("timestamp_utc", measurement)
            self.assertGreaterEqual(measurement["latency_ms"], 0)

    def test_reject_non_positive_repetitions(self):
        with self.assertRaises(ValueError):
            measure_operation_latency(lambda: None, repetitions=0)

    def test_latency_summary(self):
        measurements = [
            {"latency_ms": 1.0},
            {"latency_ms": 2.0},
            {"latency_ms": 3.0},
            {"latency_ms": 4.0},
            {"latency_ms": 5.0},
        ]

        summary = summarize_latency(measurements)

        self.assertEqual(summary["samples"], 5)
        self.assertEqual(summary["mean_ms"], 3.0)
        self.assertEqual(summary["median_ms"], 3.0)
        self.assertEqual(summary["p95_ms"], 5.0)
        self.assertEqual(summary["min_ms"], 1.0)
        self.assertEqual(summary["max_ms"], 5.0)

    def test_reject_empty_measurements(self):
        with self.assertRaises(ValueError):
            summarize_latency([])

    def test_reject_negative_latency(self):
        measurements = [{"latency_ms": -1.0}]

        with self.assertRaises(ValueError):
            summarize_latency(measurements)

    def test_save_latency_csv(self):
        measurements = [
            {
                "timestamp_utc": "2026-10-31T10:00:00+00:00",
                "sample_number": 1,
                "latency_ms": 1.25,
            },
            {
                "timestamp_utc": "2026-10-31T10:00:01+00:00",
                "sample_number": 2,
                "latency_ms": 2.50,
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "latency.csv"
            save_latency_csv(measurements, output_path)

            with output_path.open(
                newline="",
                encoding="utf-8",
            ) as file:
                rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["sample_number"], "1")
        self.assertEqual(rows[1]["latency_ms"], "2.5")


if __name__ == "__main__":
    unittest.main()