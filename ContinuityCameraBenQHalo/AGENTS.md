# Repository Guidelines

## Project Structure & Module Organization

This model directory contains a parametric `build123d` model for a single-piece
BenQ ScreenBar phone hook. Keep production code in `screenbar_mount/`:

- `config.py` owns every user-adjustable dimension in `MountConfig`.
- `simple_hook.py` is the active production geometry builder.
- `export.py` writes STL and STEP deliverables; `render.py` writes PNG checks.
- `model.py` is retained from an earlier multi-part prototype; do not use it
  for new production changes unless intentionally reviving that design.

Put acceptance tests in `tests/`. Generated files belong only in
`output/stl/`, `output/step/`, and `output/png/`.

## Build, Test, and Development Commands

Use the adjacent `Pot` project's prepared virtual environment until this
repository has its own `.venv`:

```bash
../../Pot/.venv/bin/python -m pytest
../../Pot/.venv/bin/python -m screenbar_mount.export
../../Pot/.venv/bin/python -m screenbar_mount.render
```

Run tests first; then regenerate both manufacturing files and all renders
after every geometry change. Inspect the PNGs before treating an export as
print-ready.

## Coding Style & Naming Conventions

Use Python 3.10+ with four-space indentation, type annotations, and
descriptive `snake_case` names. Keep dimensions in millimetres and never
hard-code a mechanical value that belongs in `MountConfig`. Name builders as
`_feature_name` and public entry points as `build_*`. Comments should explain
mechanical intent—clearance, load path, print orientation, or contact surface.

## Testing Guidelines

Tests use `pytest` and follow `test_<behavior>.py` / `test_<behavior>()` naming.
Add or update acceptance checks for changed dimensions, fit clearances,
single-solid output, camera/port keep-outs, and required export/render files.
Keep tests geometric and deterministic; do not depend on a printer or GUI.

## Commits & Pull Requests

No Git history is currently available, so use concise imperative commit
subjects such as `Refine phone U-hook clearance`. Describe geometry changes,
list the three commands run, and include updated PNGs for visual changes.
Call out changed dimensions, hardware assumptions, or any fit-risk requiring a
physical test print.
