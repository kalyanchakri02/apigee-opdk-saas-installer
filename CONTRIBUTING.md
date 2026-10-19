# Contributing

Thanks for your interest in improving the Apigee OPDK/SaaS Installer.

1. Open an issue first for larger changes so we can agree on the approach.
2. Fork the repo and create a branch: `git checkout -b feature/my-change`
3. Add or update tests, and run `python -m pytest tests/unit/`.
4. Open a pull request describing what changed and why.

## Adding a resource type
Create a class in `install/resources/` that inherits `Resource`, implement `_exists()`, `_create()` and `apply()`, and wire it into `install/ApigeeInstaller.py`.

Never commit credentials, org names, or real KVM values.
