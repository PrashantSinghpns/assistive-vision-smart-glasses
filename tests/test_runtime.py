"""Exercise camera lifecycle with fake adapters; no native hardware required."""
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from assistive_vision import app


class RuntimeTests(unittest.TestCase):
    def run_app(self, *, opened=True, read_ok=True):
        camera = MagicMock()
        camera.isOpened.return_value = opened
        camera.read.return_value = (read_ok, SimpleNamespace(shape=(480, 640, 3)))
        cv2 = MagicMock()
        cv2.error = RuntimeError
        cv2.VideoCapture.return_value = camera
        faces = MagicMock()
        faces.face_locations.return_value = []
        faces.face_encodings.return_value = []
        decoder = MagicMock()
        decoder.decode.return_value = []
        modules = {"cv2": cv2, "face_recognition": faces,
                   "pyzbar": SimpleNamespace(pyzbar=decoder), "pyzbar.pyzbar": decoder}
        with patch.dict("sys.modules", modules), patch.object(app, "load_gallery", return_value=[]), \
             patch("sys.argv", ["assistive-vision", "--gallery", "local.json", "--headless", "--max-frames", "2"]):
            if not opened or not read_ok:
                with self.assertRaises(SystemExit) as error:
                    app.main()
                self.assertEqual(error.exception.code, 2)
            else:
                app.main()
        camera.release.assert_called_once()
        cv2.imshow.assert_not_called()
        cv2.waitKey.assert_not_called()
        cv2.destroyAllWindows.assert_not_called()
        return camera

    def test_headless_frame_limit_and_cleanup(self):
        camera = self.run_app()
        self.assertEqual(camera.read.call_count, 2)

    def test_camera_open_failure_cleanup(self):
        self.run_app(opened=False)

    def test_capture_failure_cleanup(self):
        self.run_app(read_ok=False)
