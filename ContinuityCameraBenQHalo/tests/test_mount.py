"""Acceptance checks for the simplified single-piece ScreenBar phone hook."""

import pytest
from build123d import Align, Box, Location, Shape

from screenbar_mount.config import MountConfig
from screenbar_mount.export import export_screenbar_mount
from screenbar_mount.render import RENDER_FILENAMES, render_screenbar_mount
from screenbar_mount.simple_hook import build_simple_phone_hook


def _volume(shape: Shape | None) -> float:
    return float(getattr(shape, "volume", 0.0) or 0.0)


def _box(length: float, width: float, height: float, x: float, y: float, z: float) -> Shape:
    return Location((x, y, z)) * Box(
        length, width, height, align=(Align.MIN, Align.MIN, Align.MIN)
    )


def test_yoke_clears_the_measured_benq_body_and_has_protective_pad_recesses() -> None:
    model = build_simple_phone_hook()
    c = model.config

    assert _volume(model.solid.intersect(model.benq_body_reference)) < 1e-5
    assert c.plate_width == pytest.approx(50.75)
    assert c.benq_body_depth == pytest.approx(31.3)
    assert c.benq_body_height == pytest.approx(17.5)
    assert len(model.yoke_pad_recesses.solids()) == 4
    assert c.pad_recess_depth == pytest.approx(1.0)


def test_lower_side_monitor_clips_leave_a_21_mm_top_edge_opening() -> None:
    model = build_simple_phone_hook()
    c = model.config

    monitor_top = _box(
        c.saddle_outer_width,
        c.monitor_thickness,
        c.monitor_clip_drop - c.monitor_clip_yoke_overlap,
        -c.saddle_outer_width / 2,
        c.monitor_clip_rear_leg_y + c.wall_thickness,
        -c.monitor_clip_drop,
    )
    assert c.monitor_thickness == pytest.approx(21.0)
    assert c.monitor_clip_drop == pytest.approx(11.0)
    assert c.monitor_clip_rear_leg_y > c.saddle_front_y
    assert c.monitor_clip_front_leg_y + c.wall_thickness < c.saddle_back_y
    assert model.solid.bounding_box().min.Z == pytest.approx(-c.monitor_clip_drop)
    assert _volume(model.solid.intersect(monitor_top)) < 1e-5


def test_one_printed_solid_has_a_50_mm_wide_open_phone_u_channel() -> None:
    model = build_simple_phone_hook()
    c = model.config
    bounds = model.solid.bounding_box()

    assert len(model.solid.solids()) == 1
    assert c.phone_hook_span == pytest.approx(50.0)
    assert c.phone_hook_wall_height == pytest.approx(25.0)
    assert c.phone_thickness == pytest.approx(11.5)
    assert c.cradle_internal_depth == pytest.approx(12.0)
    assert bounds.max.Z == pytest.approx(c.phone_shelf_z + c.phone_hook_wall_height - c.wall_thickness)
    # Phone ends remain completely open: the hook is only a central 50 mm rail.
    end_keepout = _box(30.0, c.cradle_internal_depth, 80.0, 55.0, c.phone_back_y, c.phone_shelf_z)
    assert _volume(model.solid.intersect(end_keepout)) < 1e-5


def test_phone_camera_space_and_ports_stay_clear() -> None:
    model = build_simple_phone_hook()
    c = model.config

    camera_keepout = _box(120.0, c.cradle_internal_depth, 80.0, -60.0, c.phone_back_y, c.phone_shelf_z + 12.0)
    assert _volume(model.solid.intersect(camera_keepout)) < 1e-5


def test_mount_is_fully_tool_free_without_m3_features() -> None:
    model = build_simple_phone_hook()
    c = model.config

    assert c.phone_height == pytest.approx(0.0)
    assert model.solid.bounding_box().max.Z < 55.0


def test_exports_and_renders_produce_the_single_part_deliverables() -> None:
    exported = export_screenbar_mount()
    rendered = render_screenbar_mount()

    assert set(exported) == {"single_piece_hook"}
    assert all(path.exists() and path.stat().st_size > 0 for pair in exported.values() for path in pair)
    assert {path.name for path in rendered} == set(RENDER_FILENAMES)
    assert all(path.exists() and path.stat().st_size > 0 for path in rendered)
