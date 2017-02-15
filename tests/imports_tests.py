# pylint: disable=no-self-use
"""Tests for the Xtralien imports module

The imports module is used to provide a consistent user
interface to people using the Xtralien Python Distribution
and includes many common packages and functions.
"""
import unittest

from os import path
import numpy as np

import xtralien.imports as imports


class TestRunner(unittest.TestCase):
    """Test Runner class

    This class contains all of the tests for the
    xtralien imports modules
    """
    def test_load_csv_skip_headers(self):
        """Test loading a CSV by skipping headers
        """
        arr = imports.load_csv(
            path.join(
                path.dirname(path.realpath(__file__)),
                'data',
                'test_1.csv'
            ),
            skip_headers=True
        )

        self.assertEqual(
            arr.all(),
            (np.zeros((15, 9)) + 0.1).all()
        )

if __name__ == "__main__":
    unittest.main()
