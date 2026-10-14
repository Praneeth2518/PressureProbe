
import time


def main():
    duration_seconds = 20
    deadline = time.monotonic() + duration_seconds
    iterations = 0

    print(f"CPU worker started for {duration_seconds} seconds.")

    while time.monotonic() < deadline:
        # Deliberately perform CPU-bound work.
        iterations += sum(range(1000))

    print(f"CPU worker finished. Iterations completed: {iterations}")


if __name__ == "__main__":
    main()
