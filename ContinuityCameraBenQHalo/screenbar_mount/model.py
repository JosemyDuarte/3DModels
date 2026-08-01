"""Build the fixed BenQ plate adapter and replaceable universal phone cradle."""

from dataclasses import dataclass

from build123d import Align, Axis, Box, Compound, Cylinder, Location, Polygon, RegularPolygon, Shape, Solid, Vector

from .config import MountConfig


def _box(length: float, width: float, height: float, x: float, y: float, z: float) -> Shape:
    """Return a box positioned by its minimum corner."""
    return Location((x, y, z)) * Box(
        length, width, height, align=(Align.MIN, Align.MIN, Align.MIN)
    )


def _cylinder_y(diameter: float, length: float, x: float, y: float, z: float) -> Shape:
    """Return a cylinder whose axis runs in positive Y from ``y``."""
    cylinder = Cylinder(diameter / 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Location((x, y + length, z)) * cylinder.rotate(Axis.X, 90)


def _cylinder_x(diameter: float, length: float, x: float, y: float, z: float) -> Shape:
    """Return a cylinder whose axis runs in positive X from ``x``."""
    cylinder = Cylinder(diameter / 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Location((x, y, z)) * cylinder.rotate(Axis.Y, 90)


def _hex_prism_y(flat: float, depth: float, x: float, y: float, z: float) -> Shape:
    """Return an M3 hex-nut pocket extruded along positive Y."""
    radius = flat / (3**0.5)
    face = RegularPolygon(radius, 6, major_radius=True).face().rotate(Axis.Z, 30)
    return Location((x, y, z)) * Solid.extrude(face.rotate(Axis.X, -90), Vector(0, depth, 0))


def _hex_prism_x(flat: float, depth: float, x: float, y: float, z: float) -> Shape:
    """Return an M3 hex-nut pocket extruded along positive X."""
    radius = flat / (3**0.5)
    face = RegularPolygon(radius, 6, major_radius=True).face().rotate(Axis.Z, 30)
    return Location((x, y, z)) * Solid.extrude(face.rotate(Axis.Y, 90), Vector(depth, 0, 0))


def _safe_fillet(shape: Shape, radius: float, axis: Axis) -> Shape:
    """Round a useful subset of exterior edges without risking a failed export."""
    try:
        solid = shape.solids()[0]
        return solid.fillet(radius, solid.edges().filter_by(axis))
    except Exception:
        return shape


def _dovetail_profile(c: MountConfig, clearance: float = 0.0) -> Shape:
    """Make a vertical-extrusion dovetail face in the X/Y plane.

    The broad face is behind the phone.  The 45-degree flanks print cleanly
    when the parts are laid on their rear faces.
    """
    base = c.dovetail_base_width + 2 * clearance
    neck = c.dovetail_neck_width + 2 * clearance
    depth = c.dovetail_depth + clearance
    return Polygon(
        (-base / 2, 0),
        (base / 2, 0),
        (neck / 2, depth),
        (-neck / 2, depth),
    ).face()


def _dovetail_rail(c: MountConfig) -> Shape:
    """The fixed male rail on Part A; Part B lowers over it from above."""
    profile = _dovetail_profile(c)
    return Location((0, c.phone_back_y - c.dovetail_depth, c.phone_shelf_z)) * Solid.extrude(
        profile, Vector(0, 0, c.dovetail_height - c.dovetail_top_stop + 0.1)
    )


def _plate_reference(c: MountConfig) -> Shape:
    """The black rear BenQ body captured by the inverted-U yoke."""
    return _box(
        c.plate_width,
        c.benq_body_depth,
        c.benq_body_height,
        -c.plate_width / 2,
        0,
        0,
    )


def _plate_saddle(c: MountConfig) -> tuple[Shape, Shape, Shape, Shape]:
    """Full-depth inverted-U yoke, pad recesses, and optional M3 clamp.

    The yoke follows the red outline in the supplied rear photo: a top bridge
    spans the 50.75 mm BenQ body while two full-depth legs descend outside its
    left and right edges.  The bottom remains entirely open and ends above the
    cylindrical light bar.
    """
    top = _box(
        c.saddle_outer_width,
        c.yoke_inner_depth,
        c.wall_thickness,
        -c.saddle_outer_width / 2,
        c.saddle_front_y,
        c.benq_body_height,
    )
    left_leg = _box(
        c.wall_thickness,
        c.yoke_inner_depth,
        c.benq_body_height + c.wall_thickness,
        -c.saddle_outer_width / 2,
        c.saddle_front_y,
        0,
    )
    right_leg = _box(
        c.wall_thickness,
        c.yoke_inner_depth,
        c.benq_body_height + c.wall_thickness,
        c.saddle_outer_width / 2 - c.wall_thickness,
        c.saddle_front_y,
        0,
    )
    # A partial rear wall fixes fore/aft position.  It joins the top bridge
    # and never reaches the LED bar; its screw presses only a TPU pad.
    rear_clamp_wall = _box(
        c.saddle_outer_width,
        c.wall_thickness,
        c.benq_body_height - 5.0 + c.wall_thickness,
        -c.saddle_outer_width / 2,
        -c.clamp_clearance - c.wall_thickness,
        5.0,
    )

    # Two pad stations on each inside leg prevent marks while centering the
    # yoke laterally.  Recesses point outwards into the printed legs.
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

    clamp_bore = _cylinder_y(
        c.m3_clearance_diameter,
        c.wall_thickness + c.clamp_clearance + 1.2,
        0,
        -c.clamp_clearance - c.wall_thickness - 0.1,
        c.benq_body_height / 2,
    )
    nut_pocket = _hex_prism_y(
        c.m3_nut_flat + 2 * c.nut_clearance,
        c.m3_nut_depth + 0.15,
        0,
        -c.clamp_clearance - c.wall_thickness + 0.8,
        c.benq_body_height / 2,
    )
    # An exterior-side loading slot accepts the nut without weakening either
    # plate-contact face.  It remains outside the BenQ clearance envelope.
    nut_access = _box(
        c.saddle_outer_width / 2 - 1.0,
        c.m3_nut_depth + 0.4,
        c.m3_nut_flat + 2 * c.nut_clearance,
        -c.saddle_outer_width / 2 - 0.1,
        -c.clamp_clearance - c.wall_thickness + 0.7,
        c.benq_body_height / 2 - (c.m3_nut_flat + 2 * c.nut_clearance) / 2,
    )
    saddle = (
        top.fuse(left_leg, right_leg, rear_clamp_wall)
        - Compound(pad_recesses)
        - clamp_bore
        - nut_pocket
        - nut_access
    )
    return saddle, Compound(pad_recesses), clamp_bore, nut_pocket


def _support_arm(c: MountConfig) -> Shape:
    """Return the filleted rear upright, forward bridge, and dovetail rail."""
    # Keep the tall web on the monitor-side face of the plate.  It rises clear
    # of the cradle before bridging forward, so the removable dovetail does
    # not collide with the fixed upright during insertion.
    arm_y = c.saddle_front_y
    rail_height = c.dovetail_height - c.dovetail_top_stop
    arm_top_z = c.phone_shelf_z + rail_height + c.wall_thickness
    rail_rear_y = c.phone_back_y - c.dovetail_depth - c.dovetail_depth / 2
    upright = _box(
        c.arm_width,
        c.wall_thickness,
        arm_top_z - c.yoke_top_z,
        -c.arm_width / 2,
        arm_y,
        c.yoke_top_z - 0.1,
    )
    forward_bridge = _box(
        c.arm_width,
        rail_rear_y - arm_y + 0.2,
        c.wall_thickness,
        -c.arm_width / 2,
        arm_y - 0.1,
        arm_top_z - c.wall_thickness,
    )
    # The upright and forward bridge overlap by a full wall thickness.  This
    # continuous 18 x 4 mm web is the primary bending load path; the rounded
    # exterior edges remove the usual stress riser at the inside corner.
    arm = upright.fuse(forward_bridge, _dovetail_rail(c))
    return _safe_fillet(arm, c.arm_fillet_radius, Axis.X)


def _plate_adapter(c: MountConfig) -> tuple[Shape, Shape, Shape, Shape, Shape]:
    saddle, pads, clamp_bore, clamp_nut = _plate_saddle(c)
    adapter = saddle.fuse(_support_arm(c))
    return adapter, pads, clamp_bore, clamp_nut, _plate_reference(c)


def _spring_arm(c: MountConfig, right: bool) -> Shape:
    """A lower-rooted PETG leaf spring and small front retention lip.

    A 2.6 mm wide, 20 mm tall cantilever is intentionally the one local
    exception to the nominal 4 mm structural wall: it supplies the elastic
    travel needed to accept the 146--165 mm universal phone range.
    """
    inner_x = c.spring_gap / 2 if right else -c.spring_gap / 2
    arm_x = inner_x if right else inner_x - c.cradle_arm_thickness
    arm = _box(
        c.cradle_arm_thickness,
        c.wall_thickness,
        c.cradle_arm_height + c.wall_thickness + 0.1,
        arm_x,
        c.phone_front_y - c.wall_thickness,
        c.phone_shelf_z - c.wall_thickness - 0.1,
    )
    shelf_edge = c.cradle_shelf_span / 2
    if right:
        root_x = shelf_edge - 0.1
        root_length = arm_x + c.cradle_arm_thickness - root_x + 0.1
    else:
        root_x = arm_x
        root_length = -shelf_edge - root_x + 0.2
    # The narrow front runner connects the spring root to the central shelf
    # while leaving the short phone ends and their centrally placed ports open.
    root = _box(
        root_length,
        c.wall_thickness,
        c.wall_thickness,
        root_x,
        c.phone_front_y - c.wall_thickness,
        c.phone_shelf_z - c.wall_thickness - 0.1,
    )
    # A small front lip retains the phone face after the side springs close,
    # without forming a back plate or touching the rear camera system.
    lip_x = inner_x - c.retention_lip_depth if right else inner_x
    lip = _box(
        c.retention_lip_depth,
        c.retention_lip_depth,
        c.wall_thickness,
        lip_x,
        c.phone_front_y - c.retention_lip_depth,
        c.phone_shelf_z + c.cradle_arm_height - c.wall_thickness,
    )
    return arm.fuse(root, lip)


def _cradle_lock_features(c: MountConfig) -> tuple[Shape, Shape]:
    """M3 side-lock bore and captive-nut pocket for the dovetail connection."""
    # The accessible screw enters from the right side, crosses the cradle
    # receiver, and bears on the fixed rail's right flank at X = +base/2.
    bore = _cylinder_x(
        c.m3_clearance_diameter,
        22.0,
        3.0,
        c.phone_back_y - c.dovetail_depth / 2,
        c.phone_shelf_z + c.dovetail_height / 2,
    )
    nut = _hex_prism_x(
        c.m3_nut_flat + 2 * c.nut_clearance,
        c.m3_nut_depth + 0.15,
        8.0,
        c.phone_back_y - c.dovetail_depth / 2,
        c.phone_shelf_z + c.dovetail_height / 2,
    )
    return bore, nut


def _phone_cradle(c: MountConfig) -> tuple[Shape, Shape, Shape, Shape]:
    """Open-back shelf, self-centering snap arms, dovetail pocket, M3 lock."""
    shelf = _box(
        c.cradle_shelf_span,
        c.cradle_shelf_depth,
        c.wall_thickness,
        -c.cradle_shelf_span / 2,
        c.phone_back_y,
        c.phone_shelf_z - c.wall_thickness,
    )
    # A central receiver joins the shelf but stays far narrower than the
    # phone, leaving the entire rear camera area and both device ends open.
    receiver = _box(
        42.0,
        c.dovetail_depth + c.wall_thickness,
        c.dovetail_height - c.dovetail_top_stop - 0.2,
        -21.0,
        c.phone_back_y - c.dovetail_depth - c.wall_thickness,
        c.phone_shelf_z - 0.1,
    )
    female_profile = _dovetail_profile(c, c.dovetail_clearance)
    female_pocket = Location(
        (
            0,
            c.phone_back_y - c.dovetail_depth + c.dovetail_clearance / 3,
            c.phone_shelf_z - 0.1,
        )
    ) * Solid.extrude(
        female_profile, Vector(0, 0, c.dovetail_height - c.dovetail_top_stop + 0.3)
    )
    lock_bore, lock_nut = _cradle_lock_features(c)
    arms = Compound((_spring_arm(c, False), _spring_arm(c, True)))
    cradle = shelf.fuse(receiver, arms) - female_pocket - lock_bore - lock_nut
    return cradle, female_pocket, lock_bore, lock_nut


@dataclass(frozen=True)
class ScreenBarMount:
    """The two printable parts plus their mechanical reference volumes."""

    plate_adapter: Shape
    phone_cradle: Shape
    assembled: Shape
    benq_plate_reference: Shape
    saddle_pad_recesses: Shape
    plate_clamp_bore: Shape
    plate_clamp_nut_pocket: Shape
    dovetail_pocket: Shape
    cradle_lock_bore: Shape
    cradle_lock_nut_pocket: Shape
    config: MountConfig


def build_screenbar_mount(config: MountConfig | None = None) -> ScreenBarMount:
    """Build the default two-piece plate adapter and universal phone cradle."""
    c = config or MountConfig()
    adapter, pads, clamp_bore, clamp_nut, plate = _plate_adapter(c)
    cradle, dovetail_pocket, lock_bore, lock_nut = _phone_cradle(c)
    return ScreenBarMount(
        plate_adapter=adapter,
        phone_cradle=cradle,
        # Parts are intentionally clearance-separated at the dovetail.  Keep
        # the inspection assembly as a compound rather than boolean-fusing
        # two independent printable components.
        assembled=Compound((adapter, cradle)),
        benq_plate_reference=plate,
        saddle_pad_recesses=pads,
        plate_clamp_bore=clamp_bore,
        plate_clamp_nut_pocket=clamp_nut,
        dovetail_pocket=dovetail_pocket,
        cradle_lock_bore=lock_bore,
        cradle_lock_nut_pocket=lock_nut,
        config=c,
    )
