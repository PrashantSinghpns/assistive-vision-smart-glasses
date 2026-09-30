# Troubleshooting

| Symptom | Resolution |
|---|---|
| Missing cv2, face_recognition, or pyzbar | Activate the environment and install `python -m pip install -e ".[vision]"` from the project root. |
| dlib build fails | Use Python 3.11 and install your platform's C++ compiler and CMake. Native installation is platform dependent. |
| Unable to find ZBar shared library | Install the native ZBar library for the operating system; the Python package alone is insufficient. |
| Camera cannot be opened | Check camera permissions, camera index, and whether another app is using it. CSI camera modules may need a separate capture adapter. |
| Preview fails over SSH | Pass `--headless`; use Ctrl+C or `--max-frames` to stop. |
| eSpeak executable not found | Install eSpeak and ensure it is on PATH, or omit `--speak` for visual/logged output. |
| Gallery rejected | Regenerate it with enrollment. Schema version must be integer 1, identity names must be valid, and each vector must contain 128 finite numbers. |
| Enrollment finds no valid images | Use `data/enrollment/<identity>/*.jpg` or PNG images with exactly one detectable face. Review warning logs. |
| Face repeatedly classified Unknown | Check enrollment quality, lighting, distance, and threshold calibration. Increasing the threshold may increase false acceptance. |

The `Unknown` identity label is reserved. Enrollment datasets and galleries stay private. A successful mocked runtime check does not confirm real camera or audio behavior.
