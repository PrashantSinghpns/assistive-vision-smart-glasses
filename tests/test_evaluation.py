import unittest
from assistive_vision.evaluate import evaluate

class EvaluationTests(unittest.TestCase):
    def test_known_accuracy_and_unknown_false_accepts_have_separate_denominators(self):
        records = [{"name": "Alice", "embedding": [0.] * 128}]
        queries = [{"expected": "Alice", "embedding": [0.] * 128},
                   {"expected": "Unknown", "embedding": [1.] * 128},
                   {"expected": "Unknown", "embedding": [0.01] * 128}]
        result = evaluate(records, queries)
        self.assertEqual(result["known_identification_accuracy"], 1.)
        self.assertEqual(result["unknown_false_acceptance_rate"], 0.5)
        self.assertEqual(result["accepted_unknown"], 1)

    def test_missing_unknown_examples_are_not_reported_as_zero_errors(self):
        result = evaluate([{"name": "Alice", "embedding": [0.] * 128}],
                          [{"expected": "Alice", "embedding": [0.] * 128}])
        self.assertIsNone(result["unknown_false_acceptance_rate"])
