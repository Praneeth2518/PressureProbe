import csv
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path


def measure_operation_latency(operation, repetitions=100):
    """Measure each operation's execution time and timestamp."""
    if repetitions <= 0:
        raise ValueError("repetitions must be positive.")

    measurements = []

    for sample_number in range(1, repetitions + 1):
        timestamp_utc = datetime.now(timezone.utc).isoformat()

        start = time.perf_counter()
        operation()
        end = time.perf_counter()

        latency_ms = (end - start) * 1000

        measurements.append({
            "timestamp_utc": timestamp_utc,
            "sample_number": sample_number,
            "latency_ms": latency_ms,
        })

    return measurements


def summarize_latency(measurements):
    """Calculate descriptive statistics for latency measurements."""
    if not measurements:
        raise ValueError("measurements must not be empty.")

    latency_values = [
        measurement["latency_ms"]
        for measurement in measurements
    ]

    if any(
        not math.isfinite(value) or value < 0
        for value in latency_values
    ):
        raise ValueError("Latency values must be finite and non-negative.")

    ordered = sorted(latency_values)
    p95_index = math.ceil(0.95 * len(ordered)) - 1

    return {
        "samples": len(ordered),
        "mean_ms": statistics.mean(ordered),
        "median_ms": statistics.median(ordered),
        "p95_ms": ordered[p95_index],
        "min_ms": min(ordered),
        "max_ms": max(ordered),
    }


def save_latency_csv(measurements, output_path):
    """Save timestamped latency measurements to a CSV file."""
    if not measurements:
        raise ValueError("measurements must not be empty.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp_utc",
                "sample_number",
                "latency_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(measurements)

    return output_path


def main():
    def sample_operation():
        sum(range(1000))

    repetitions = 1000
    output_path = Path("results") / "latency_baseline.csv"

    measurements = measure_operation_latency(
        sample_operation,
        repetitions=repetitions,
    )

    summary = summarize_latency(measurements)
    saved_path = save_latency_csv(measurements, output_path)

    print("PressureProbe Latency Probe")
    print(f"Samples: {summary['samples']}")
    print(f"Mean latency: {summary['mean_ms']:.6f} ms")
    print(f"Median latency: {summary['median_ms']:.6f} ms")
    print(f"95th percentile latency: {summary['p95_ms']:.6f} ms")
    print(f"Minimum latency: {summary['min_ms']:.6f} ms")
    print(f"Maximum latency: {summary['max_ms']:.6f} ms")
    print(f"Measurements saved to: {saved_path}")


if __name__ == "__main__":
    main()