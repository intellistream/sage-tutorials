# CHANGELOG

All notable changes to this repository are documented in this file.

## PyPI Release Status

Checked package name `isage-tutorials` on PyPI (`https://pypi.org/pypi/isage-tutorials/json`) on 2026-02-14.

- No published package was found (HTTP 404).

## [Unreleased]

### Changed
- Updated docs to remove `dev-notes` references.
- Standardized architecture/help links to stable public docs.
- Removed `ray` logger suppression from L3-kernel tutorial files (`hello_local_batch.py`, `hello_comap_function_example.py`) — ray is no longer a runtime dependency per the Flownet-first policy.
- Replaced outdated Ray cluster setup instructions in `cpu_node_demo.py` usage guide with Flownet/sage-cluster equivalents.
