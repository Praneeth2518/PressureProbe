
import csv
import platform
import time
from datetime import datetime, timezone
from pathlib import Path


# Linux exposes PSI measurements through these virtual files.
PSI_FILES = {
    "cpu": Path("/proc/pressure/cpu"),
    "memory": Path("/proc/pressure/memory"),
    "io": Path("/proc/pressure/io"),
}


def parse_psi_line(line):
    """Parse one PSI line into a dictionary of measurements."""
    parts = line.split()
    metrics = {"type": parts[0]}

    for item in parts[1:]:
        key, value = item.split("=", 1)

        if key == "total":
            metrics[key] = int(value)
        else:
            metrics[key] = float(value)

    return metrics


def read_psi_file(path):
    """Read a PSI file and return its measurements."""
    result = {}

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            metrics = parse_psi_line(line)
            result[metrics["type"]] = metrics

    return result


def collect_sample():
    """Collect one timestamped PSI sample from Linux."""
    if platform.system() != "Linux":
        raise RuntimeError(
            "Real PSI collection requires Linux. "
            "On Windows, test parsing and CSV output separately."
        )

    sample = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    for resource, path in PSI_FILES.items():
        try:
            measurements = read_psi_file(path)

            for pressure_type, metrics in measurements.items():
                for metric, value in metrics.items():
                    if metric == "type":
                        continue

                    column = f"{resource}_{pressure_type}_{metric}"
                    sample[column] = value

        except (OSError, ValueError) as error:
            print(f"Warning: Could not read {path}: {error}")

    return sample


def collect_to_csv(output_path, interval_seconds=1, duration_seconds=10):
    """Collect PSI samples periodically and save them to CSV."""
    if interval_seconds <= 0 or duration_seconds <= 0:
        raise ValueError("Interval and duration must be positive.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    samples = []
    deadline = time.monotonic() + duration_seconds

    while time.monotonic() < deadline:
        sample = collect_sample()

        if sample:
            samples.append(sample)

        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(interval_seconds, remaining))

    if not samples:
        raise RuntimeError("No PSI samples were collected.")

    columns = list(dict.fromkeys(
        key for sample in samples for key in sample
    ))

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(samples)

    print(f"Collected {len(samples)} samples.")
    print(f"Saved measurements to: {output_path.resolve()}")


if __name__ == "__main__":
    collect_to_csv(
        output_path="data/raw/psi_baseline.csv",
        interval_seconds=1,
        duration_seconds=10,
    )
