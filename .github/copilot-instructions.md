# SAGE Tutorials Copilot Instructions

## Scope
- `intellistream/sage-tutorials` contains learning materials only.
- Not for SAGE core, production apps, or benchmark framework code.

## Critical rules
- Flownet-first ecosystem direction; do not add new `ray` dependencies/imports.
- Tutorials depend on SAGE install; when needed, use SAGE `./quickstart.sh --dev --yes` first.
- Do not create new local virtual environments (`venv`/`.venv`); use the existing configured Python environment.
- In conda environments, use `python -m pip`.
- No fallback logic in tutorial code; fail fast with clear errors.
- Do not embed manual one-off package installs in tutorial code cells/scripts.

## Documentation-first workflow
1. Read `README.md`, `QUICK_START.md`, and the target layer README.
2. Reuse existing tutorial patterns and naming conventions.
3. Keep examples minimal, runnable, and clearly documented.

## High-signal paths
- `L1-common/` to `L5-apps/`, `config/`, root `README.md`, `QUICK_START.md`.

## Polyrepo coordination (mandatory)

- This repository is an independent SAGE sub-repository and is developed/released independently.
- Do not assume sibling source directories exist locally in `intellistream/SAGE`.
- For cross-repo rollout, publish this repo/package first, then bump the version pin in `SAGE/packages/sage/pyproject.toml` when applicable.
- Do not add local editable installs of other SAGE sub-packages in setup scripts or docs.
