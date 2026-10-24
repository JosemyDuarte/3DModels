# Models

All dimensions are millimetres. Shared dimensions and geometry: `lib/geometry.py`.

| Entrypoints | Outputs | Purpose |
| --- | --- | --- |
| deflector_left.py, deflector_right.py | STEP, STL | Full halves, flat outer ends and nine magnet pockets each (six side, three horizontal; Ø12 × 2 mm magnets) |
| vent_assembly.py | STEP | Installed full assembly |
| vent_exploded.py | STEP | Separated full halves |
| first_layers_left.py, first_layers_right.py | STEP, STL | Actual first 18 mm, already oriented for printing |
| fit_frame_left.py, fit_frame_right.py | STEP, STL | 5.6 mm mounting-plane cut, full XY fit retained |
| fit_frame_assembly.py | STEP | Assembled low-material fit frame |

Run `.venv/bin/python src/<entrypoint>.py` from the project root with
`CADGEN_CACHE_DIR="$PWD/.cadgen"`. Assemblies regenerate their child parts.
See the root README for printing and fit-test instructions.
