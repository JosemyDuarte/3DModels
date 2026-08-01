# BenQ ScreenBar Halo 2 Continuity Camera Mount

A parameter-driven `build123d` design for a removable iPhone Continuity Camera
mount.  The mount clamps only to the 50.75 x 31.3 x 17.5 mm black BenQ rear
body visible in the supplied photos.  It does not bear on or touch the
cylindrical ScreenBar light bar.

This is one printed part: a padded full-depth inverted-U yoke drops over the
rear body, a reinforced arm rises and projects forward, and a second 50 mm-wide,
25 mm-tall U-channel supports the phone's lower long edge in landscape. Two
lower side clips fit over the monitor's 21 mm top edge with 11 mm retention
legs. The phone channel is open at both ends for USB-C/Lightning access and is
far below the rear camera area.

## Hardware and pads

The optional M3 feature uses an ordinary captured M3 hex nut: no soldering
iron is necessary. This simplified version uses no M3 hardware at all: four
1 mm TPU/EPDM pads in the yoke provide the tool-free friction fit.

Adhere 1 mm TPU or EPDM pads into the modeled recesses before installation.
They isolate the painted BenQ plate from the PETG and provide the intended
friction fit.

## Print and export

Create a local environment for this project, then install its runtime and
development dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/python -m screenbar_mount.export
.venv/bin/python -m screenbar_mount.render
```

Print the single part in PETG with the broad yoke rear face on the bed. Use a
4 mm brim only if PETG adhesion needs it. ASA and ABS are also suitable.
Inspect all PNGs in `output/png/` before printing.
