# Contributing

Keep changes traceable to source material or label them as new implementation. Include meaningful tests for matching and data validation changes. Document target-device validation for camera, audio, and sensor changes. Keep private images, embeddings, credentials, and personal contact details out of commits.

Install the core package with `python -m pip install -e .`, then run `python -m compileall -q src tests` and `python -m unittest discover -s tests -v` before proposing changes. The core test suite uses simulated adapters and does not require the native vision libraries. Validate any vision changes separately against an installed camera environment.
