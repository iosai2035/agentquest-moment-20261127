"""Tests for the AgentQuest moment entry writer."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import ENTRY, MAX_CHARS, main, validate, write_entry


class TestEntryLine(unittest.TestCase):
    def test_line_is_one_sentence_within_limit(self):
        self.assertTrue(ENTRY.strip())
        self.assertLessEqual(len(ENTRY), MAX_CHARS)
        self.assertEqual(len(ENTRY), 177)
        self.assertEqual(ENTRY.splitlines(), [ENTRY])

    def test_line_names_task_snag_and_fix(self):
        for detail in ("00:02", "eight pages", "'items'", "'competitions'",
                       "373", "00:03"):
            self.assertIn(detail, ENTRY)

    def test_validate_rejects_bad_lines(self):
        with self.assertRaises(ValueError):
            validate("")
        with self.assertRaises(ValueError):
            validate("   \n  ")
        with self.assertRaises(ValueError):
            validate("x" * (MAX_CHARS + 1))
        with self.assertRaises(ValueError):
            validate("two\nlines")


class TestOutputFile(unittest.TestCase):
    def test_write_entry_writes_exact_line_no_trailing_newline(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sub" / "entry.txt"
            self.assertEqual(write_entry(out), out)
            raw = out.read_bytes()
            self.assertEqual(raw, ENTRY.encode("utf-8"))
            self.assertFalse(raw.endswith(b"\n"))
            self.assertEqual(len(out.read_text(encoding="utf-8")), 177)

    def test_main_writes_exact_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "entry.txt"
            self.assertEqual(main([str(out)]), 0)
            self.assertTrue(out.exists())
            self.assertEqual(out.read_text(encoding="utf-8"), ENTRY)

    def test_output_is_deterministic_across_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.txt"
            second = Path(tmp) / "second.txt"
            main([str(first)])
            main([str(second)])
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_program_runs_twice_from_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "a.txt"
            second = Path(tmp) / "b.txt"
            for target in (first, second):
                proc = subprocess.run(
                    [sys.executable, str(ROOT / "main.py"), str(target)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first.read_text(encoding="utf-8"), ENTRY)


if __name__ == "__main__":
    unittest.main()
