"""Single-piece BenQ rear-body yoke and minimal landscape phone U-hook."""

from dataclasses import dataclass

from build123d import Align, Box, Compound, Location, Shape

from .config import MountConfig


def _box(length: float, width: float, height: float, x: float, y: float, z: float) -> Shape:
    return Location((x, y, z)) * Box(
        length, width, height, align=(Align.MIN, Align.MIN, Align.MIN)
    )


def _benq_body_reference(c: MountConfig) -> Shape:
    return _box(
        c.plate_width,
        c.benq_body_depth,
        c.benq_body_height,
        -c.plate_width / 2,
        0,
        0,
    )


def _benq_yoke(c: MountConfig) -> tuple[Shape, Shape]:
    """Full-depth inverted-U yoke following the user's red outline."""
    top = _box(
        c.saddle_outer_width,
        c.yoke_inner_depth,
        c.wall_thickness,
        -c.saddle_outer_width / 2,
        c.saddle_front_y,
        c.benq_body_height,
    )
    legs = [
        _box(
            c.wall_thickness,
            c.yoke_inner_depth,
            c.yoke_top_z,
            x,
            c.saddle_front_y,
            0,
        )
        for x in (
            -c.saddle_outer_width / 2,
            c.saddle_outer_width / 2 - c.wall_thickness,
        )
    ]
    pad_recesses: list[Shape] = []
    for y in (3.5, c.benq_body_depth - c.pad_width - 3.5):
        pad_recesses.extend(
            (
                _box(
                    c.pad_recess_depth,
                    c.pad_width,
                    c.pad_height,
                    -c.plate_cavity_width / 2 - c.pad_recess_depth,
                    y,
                    (c.benq_body_height - c.pad_height) / 2,
                ),
                _box(
                    c.pad_recess_depth,
                    c.pad_width,
                    c.pad_height,
                    c.plate_cavity_width / 2,
                    y,
                    (c.benq_body_height - c.pad_height) / 2,
                ),
            )
        )
    # There is intentionally no rear wall, screw, or nut: the snug 0.5 mm
    # clearance and four TPU pads provide a clean tool-free friction fit.
    yoke = top.fuse(*legs) - Compound(pad_recesses)
    return yoke, Compound(pad_recesses)


def _phone_hook(c: MountConfig) -> tuple[Shape, Shape]:
    """Open-top, 50 mm-long U-channel supporting the phone's lower long edge."""
    x = -c.phone_hook_span / 2
    shelf = _box(
        c.phone_hook_span,
        c.cradle_internal_depth,
        c.wall_thickness,
        x,
        c.phone_back_y,
        c.phone_shelf_z - c.wall_thickness,
    )
    rear_wall = _box(
        c.phone_hook_span,
        c.wall_thickness,
        c.phone_hook_wall_height,
        x,
        c.phone_back_y - c.wall_thickness,
        c.phone_shelf_z - c.wall_thickness,
    )
    front_wall = _box(
        c.phone_hook_span,
        c.wall_thickness,
        c.phone_hook_wall_height,
        x,
        c.phone_front_y,
        c.phone_shelf_z - c.wall_thickness,
    )
    # One TPU recess per inside face adds harmless, removable friction without
    # closing either phone end or covering any rear camera area.
    pad_z = c.phone_shelf_z + 1.0
    pads = Compound(
        (
            _box(
                c.phone_hook_pad_span,
                c.pad_recess_depth,
                c.pad_height / 2,
                -c.phone_hook_pad_span / 2,
                c.phone_back_y - c.pad_recess_depth,
                pad_z,
            ),
            _box(
                c.phone_hook_pad_span,
                c.pad_recess_depth,
                c.pad_height / 2,
                -c.phone_hook_pad_span / 2,
                c.phone_front_y,
                pad_z,
            ),
        )
    )
    return shelf.fuse(rear_wall, front_wall) - pads, pads


def _monitor_top_clips(c: MountConfig) -> Shape:
    """Two inverted-U clips below the yoke that retain a 21 mm monitor top."""
    clips: list[Shape] = []
    for x in (
        -c.saddle_outer_width / 2,
        c.saddle_outer_width / 2 - c.wall_thickness,
    ):
        top = _box(
            c.wall_thickness,
            c.monitor_thickness + 2 * c.wall_thickness,
            c.wall_thickness,
            x,
            c.monitor_clip_rear_leg_y,
            -c.monitor_clip_yoke_overlap,
        )
        front_leg = _box(
            c.wall_thickness,
            c.wall_thickness,
            c.monitor_clip_drop,
            x,
            c.monitor_clip_front_leg_y,
            -c.monitor_clip_drop,
        )
        rear_leg = _box(
            c.wall_thickness,
            c.wall_thickness,
            c.monitor_clip_drop,
            x,
            c.monitor_clip_rear_leg_y,
            -c.monitor_clip_drop,
        )
        clips.append(top.fuse(front_leg, rear_leg))
    return Compound(clips)


def _forward_bridge(c: MountConfig) -> Shape:
    """Short direct bridge from yoke ceiling to the rear phone-U wall."""
    return _box(
        c.arm_width,
        c.phone_back_y - c.saddle_back_y + 0.1,
        c.wall_thickness,
        -c.arm_width / 2,
        c.saddle_back_y - 0.1,
        c.phone_shelf_z - c.wall_thickness,
    )


@dataclass(frozen=True)
class SimplePhoneHook:
    """The complete one-piece printable mount and reference volumes."""

    solid: Shape
    benq_body_reference: Shape
    yoke_pad_recesses: Shape
    phone_pad_recesses: Shape
    config: MountConfig


def build_simple_phone_hook(config: MountConfig | None = None) -> SimplePhoneHook:
    """Build the production single-piece yoke, arm, and 50 mm phone U-hook."""
    c = config or MountConfig()
    yoke, yoke_pads = _benq_yoke(c)
    phone_hook, phone_pads = _phone_hook(c)
    solid = yoke.fuse(_monitor_top_clips(c), _forward_bridge(c), phone_hook)
    return SimplePhoneHook(
        solid=solid,
        benq_body_reference=_benq_body_reference(c),
        yoke_pad_recesses=yoke_pads,
        phone_pad_recesses=phone_pads,
        config=c,
    )
