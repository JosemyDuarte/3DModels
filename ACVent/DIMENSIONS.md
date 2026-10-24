# AC vent deflector dimensions

All dimensions are in millimetres. Overall bounds are measured from the saved solids in [validation.json](previews/validation.json). Design parameters are in [geometry.py](src/lib/geometry.py).

| Feature | Dimension |
| --- | --- |
| Vent / assembled mounting footprint | 225 × 175 |
| Full assembly (X × Y × Z) | 225 × 175 × 67.742 |
| Left half bounds | 120.5 × 175 × 67.742 |
| Right half bounds | 112.35 × 175 × 67.437 |
| Nominal wall thickness | 2.4 |
| Curved transition radius | 25 |
| Ramp angle | 10° |
| Side mounting rim width | 15.5 |
| Horizontal mounting rim width | 17.0 |
| Centre seam / minimum part separation | 0.3 |
| Overlap length / thickness | 8.0 / 1.2 |
| Joint clearance | 0.3 |
| Root ramp angle | 26.565° |
| Magnets (18 total, 9 per half) | Ø12 × 2 |
| Blind magnet pockets | Ø12.3 × 2.1 deep |
| Material below magnet pockets | 1.3 |
| Reinforcing pad radial wall | 2.0 |
| Thin fit frame height | 5.6 |
| First-layer sample depth (print orientation) | 18.0 |

The halves overlap at the centre; their individual widths do not add up to the assembly width.

## Pocket locations

Mounting plane: Z = 0. The footprint spans X = −112.5…112.5 and Y = −12.4…162.6.

- Side pockets: X = ±103.5; Y = 7.6, 34.6, 61.6, 88.6, 115.6, 142.6.
- Horizontal pockets: X = ±28.125, ±56.25, ±84.375; Y = −3.75.

Use the thin fit frame to confirm the footprint and magnet contact locations on the actual vent. See [README.md](README.md) for fit, assembly and printing guidance.
