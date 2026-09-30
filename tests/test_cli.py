import subprocess
import sys
import unittest


class CliTests(unittest.TestCase):
    def test_help_without_native_dependencies(self):
        for module in ["assistive_vision.app", "assistive_vision.enroll"]:
            result = subprocess.run([sys.executable, "-m", module, "--help"],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("usage:", result.stdout)

    def test_invalid_gallery_reports_cli_error(self):
        result = subprocess.run([sys.executable, "-m", "assistive_vision.app",
                                 "--gallery", "missing-gallery.json"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot read gallery", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
