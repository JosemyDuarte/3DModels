"""Fixed-camera PNG renders for the one-piece BenQ yoke and phone U-hook."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from build123d import Align, Box, Location, Shape

from .simple_hook import build_simple_phone_hook


ROOT = Path(__file__).resolve().parents[1]
IMAGE_SIZE = (9, 7)
RENDER_FILENAMES = (
    "screenbar_single_hook_isometric.png",
    "screenbar_single_hook_front.png",
    "screenbar_single_hook_side.png",
    "screenbar_single_hook_yoke_detail.png",
)
BOUNDS = ((-100, 100), (-10, 75), (-5, 135))


def _write_png(
    models: list[tuple[Shape, str, float]], destination: Path, elevation: float, azimuth: float
) -> None:
    figure = plt.figure(figsize=IMAGE_SIZE)
    axes = figure.add_subplot(projection="3d")
    for model, color, alpha in models:
        vertices, triangles = model.tessellate(0.45)
        faces = [
            [(vertices[index].X, vertices[index].Y, vertices[index].Z) for index in triangle]
            for triangle in triangles
        ]
        axes.add_collection3d(
            Poly3DCollection(faces, facecolors=color, edgecolors="#34343b", linewidths=0.16, alpha=alpha)
        )
    axes.set_xlim(*BOUNDS[0])
    axes.set_ylim(*BOUNDS[1])
    axes.set_zlim(*BOUNDS[2])
    axes.set_box_aspect(tuple(maximum - minimum for minimum, maximum in BOUNDS))
    axes.view_init(elev=elevation, azim=azimuth)
    axes.set_axis_off()
    figure.savefig(destination, dpi=200, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(figure)


def _phone_reference(model: object) -> Shape:
    """A translucent generic iPhone envelope for assembly-only renders."""
    config = getattr(model, "config")
    return Location(
        (-155.0 / 2, config.phone_back_y, config.phone_shelf_z)
    ) * Box(155.0, config.cradle_internal_depth, 75.0, align=(Align.MIN, Align.MIN, Align.MIN))


def render_screenbar_mount() -> list[Path]:
    """Render the single part, fitted BenQ body, and translucent phone envelope."""
    model = build_simple_phone_hook()
    output = ROOT / "output" / "png"
    output.mkdir(parents=True, exist_ok=True)
    common = [
        (model.solid, "#262a33", 1.0),
        (model.benq_body_reference, "#b58c50", 0.35),
        (_phone_reference(model), "#4d79a8", 0.20),
    ]
    views = (
        ("screenbar_single_hook_isometric.png", common, 22, -128),
        ("screenbar_single_hook_front.png", common, 0, -90),
        ("screenbar_single_hook_side.png", common, 0, 0),
        ("screenbar_single_hook_yoke_detail.png", [(model.solid, "#262a33", 1.0), (model.benq_body_reference, "#b58c50", 0.45)], 20, 45),
    )
    paths: list[Path] = []
    for filename, shapes, elevation, azimuth in views:
        path = output / filename
        _write_png(shapes, path, elevation, azimuth)
        paths.append(path)
    return paths


if __name__ == "__main__":
    for path in render_screenbar_mount():
        print(f"Wrote {path}")
