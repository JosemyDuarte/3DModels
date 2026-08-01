"""Export the one-piece production BenQ yoke and phone U-hook."""

from pathlib import Path

from build123d import export_step, export_stl

from .simple_hook import build_simple_phone_hook


ROOT = Path(__file__).resolve().parents[1]


def _export(name: str, model: object) -> tuple[Path, Path]:
    stl = ROOT / "output" / "stl" / f"{name}.stl"
    step = ROOT / "output" / "step" / f"{name}.step"
    stl.parent.mkdir(parents=True, exist_ok=True)
    step.parent.mkdir(parents=True, exist_ok=True)
    export_stl(model, stl)
    export_step(model, step)
    return stl, step


def export_screenbar_mount() -> dict[str, tuple[Path, Path]]:
    """Write the single printable production part in STL and STEP."""
    model = build_simple_phone_hook()
    return {
        "single_piece_hook": _export("screenbar_single_piece_phone_hook", model.solid),
    }


if __name__ == "__main__":
    for part, (stl, step) in export_screenbar_mount().items():
        print(f"Wrote {part}: {stl}\nWrote {part}: {step}")
