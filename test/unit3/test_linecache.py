"""Tests for the linecache module."""

import linecache
import unittest


class GetlineTest(unittest.TestCase):
    def test_first_line_contains_expected_content(self):
        self.assertEqual(linecache.getline(__file__, 1), '"""Tests for the linecache module."""\n')

    def test_out_of_range_returns_empty_string(self):
        self.assertEqual(linecache.getline(__file__, 0), "")
        self.assertEqual(linecache.getline(__file__, 99999), "")

    def test_unknown_file_returns_empty_string(self):
        self.assertEqual(linecache.getline("no_such_file_xyz.py", 1), "")


if __name__ == "__main__":
    unittest.main()
