# Contributing

Keep changes traceable to source material or label them as new implementation. Include meaningful tests for matching and data validation changes. Document target-device validation for camera, audio, and sensor changes. Keep private images, embeddings, credentials, and personal contact details out of commits.

Run `python -m compileall -q src tests` and `PYTHONPATH=src python -m unittest discover -s tests -v` before proposing changes. Use `$env:PYTHONPATH="src"` in PowerShell instead of the inline Linux environment assignment.
