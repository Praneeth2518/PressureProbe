
import tempfile
import unittest
from pathlib import Path

from src.psi_collector import parse_psi_line, read_psi_file


class TestPSICollector(unittest.TestCase):

    def test_parse_some_pressure(self):
        line = "some avg10=0.25 avg60=0.10 avg300=0.05 total=123456"

        result = parse_psi_line(line)

        self.assertEqual(result["type"], "some")
        self.assertAlmostEqual(result["avg10"], 0.25)
        self.assertAlmostEqual(result["avg60"], 0.10)
        self.assertAlmostEqual(result["avg300"], 0.05)
        self.assertEqual(result["total"], 123456)

    def test_parse_full_pressure(self):
        line = "full avg10=0.00 avg60=0.01 avg300=0.02 total=987"

        result = parse_psi_line(line)

        self.assertEqual(result["type"], "full")
        self.assertEqual(result["avg10"], 0.0)
        self.assertEqual(result["total"], 987)

    def test_read_psi_file(self):
        content = (
            "some avg10=0.25 avg60=0.10 avg300=0.05 total=123456\n"
            "full avg10=0.00 avg60=0.01 avg300=0.02 total=987\n"
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pressure"
            path.write_text(content, encoding="utf-8")

            result = read_psi_file(path)

        self.assertIn("some", result)
        self.assertIn("full", result)
        self.assertEqual(result["some"]["total"], 123456)
        self.assertEqual(result["full"]["total"], 987)


if __name__ == "__main__":
    unittest.main()
