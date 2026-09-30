import unittest
from assistive_vision.matching import match_identity


class MatchingTests(unittest.TestCase):
    def test_nearest_identity(self):
        records = [{"name": "A", "embedding": [0.0] * 128},
                   {"name": "B", "embedding": [1.0] * 128}]
        self.assertEqual(match_identity([1.0] * 128, records)[0], "B")

    def test_unknown_rejection(self):
        records = [{"name": "A", "embedding": [0.0] * 128}]
        self.assertEqual(match_identity([1.0] * 128, records)[0], "Unknown")

    def test_empty_gallery(self):
        self.assertEqual(match_identity([0.0] * 128, [])[0], "Unknown")

    def test_invalid_vector(self):
        with self.assertRaises(ValueError):
            match_identity([0.0], [])

    def test_nonfinite_vector(self):
        with self.assertRaises(ValueError):
            match_identity([float("nan")] * 128, [])

    def test_threshold_boundary(self):
        records = [{"name": "A", "embedding": [0.0] * 128}]
        query = [0.6] + [0.0] * 127
        self.assertEqual(match_identity(query, records, 0.6)[0], "A")
        self.assertEqual(match_identity(query, records, 0.59)[0], "Unknown")

    def test_invalid_threshold(self):
        for threshold in [0, -1, float("nan"), float("inf")]:
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                match_identity([0.0] * 128, [], threshold)


if __name__ == "__main__":
    unittest.main()
