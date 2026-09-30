import json
from pathlib import Path
import tempfile
import unittest
from assistive_vision.gallery import load_gallery, validate_records


class GalleryTests(unittest.TestCase):
    def record(self, **changes):
        return {"name": "Person A", "embedding": [0.0] * 128, **changes}

    def test_reject_malformed_record_shapes(self):
        for value in [None, {}, [], [None], [{}]]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_records(value)

    def test_reject_invalid_names(self):
        for name in ["", " ", 1, "Unknown", "unknown", "A\nB", " A"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_records([self.record(name=name)])

    def test_reject_invalid_values(self):
        for value in [True, None, "0", float("nan"), float("inf")]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_records([self.record(embedding=[value] * 128)])

    def test_load_and_schema_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gallery.json"
            with self.assertRaises(ValueError):
                load_gallery(path)
            for data in [[], {"schema_version": True}, {"schema_version": 2},
                         {"schema_version": 1, "records": []}]:
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.subTest(data=data), self.assertRaises(ValueError):
                    load_gallery(path)
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_gallery(path)
            path.write_text(json.dumps({"schema_version": 1, "records": [self.record()]}), encoding="utf-8")
            self.assertEqual(load_gallery(path)[0]["name"], "Person A")
