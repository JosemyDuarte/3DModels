"""All mechanical dimensions for the ScreenBar Continuity Camera mount (mm)."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class MountConfig:
    """Dimensions and fit choices for the two-part printed assembly.

    Coordinates use X across the monitor, Y from the monitor/rear plate toward
    the viewer, and Z upward.  The BenQ plate is represented by the volume
    X = +/- plate_width / 2, Y = 0..plate_thickness.  Positive Y is forward.
    """

    # User-measured rear BenQ body captured by the inverted-U yoke.
    # The supplied caliper photo refines the initial 50.5 mm estimate.
    plate_width: float = 50.75
    plate_thickness: float = 3.0
    benq_body_depth: float = 31.3
    benq_body_height: float = 17.5
    phone_thickness: float = 11.5
    phone_offset: float = 12.0
    # The simplified one-piece version keeps the phone at the yoke ceiling.
    # Increase this only if a later revision needs a deliberate raise.
    phone_height: float = 0.0
    clamp_clearance: float = 0.5
    tpu_pad_thickness: float = 1.0
    wall_thickness: float = 4.0

    # Fit and material options.
    fastener_style: Literal["captured_nut", "heat_set_insert"] = "captured_nut"
    plate_side_clearance: float = 0.5
    saddle_height: float = 28.0
    saddle_top_stop: float = 4.0
    pad_recess_depth: float = 1.0
    pad_width: float = 13.0
    pad_height: float = 12.0

    # M3 hardware.  The nut pockets accept a normal 5.5 mm AF M3 nut with
    # print allowance; M3 thumb screws are bought hardware, not printed.
    m3_clearance_diameter: float = 3.4
    m3_nut_flat: float = 5.5
    m3_nut_depth: float = 2.6
    nut_clearance: float = 0.25

    # Raised arm and connection.  The phone shelf is 70 mm above the saddle
    # entry datum, within the requested 65--75 mm range.
    arm_width: float = 18.0
    arm_fillet_radius: float = 3.0
    dovetail_height: float = 34.0
    dovetail_base_width: float = 18.0
    dovetail_neck_width: float = 12.0
    dovetail_depth: float = 5.0
    dovetail_clearance: float = 0.30
    # The female rail is open at its top so it prints support-free.  This
    # reduces the usable rail length; the M3 side lock sets final height.
    dovetail_top_stop: float = 4.0

    # Universal edge-only landscape cradle.  Modern 6.1--6.9 inch iPhones
    # fall inside this span; open rear geometry protects every camera layout.
    phone_min_landscape_span: float = 146.0
    phone_max_landscape_span: float = 165.0
    cradle_shelf_span: float = 132.0
    cradle_internal_depth: float = 12.0
    cradle_shelf_depth: float = 9.0
    cradle_arm_thickness: float = 2.6
    cradle_arm_height: float = 20.0
    cradle_lead_in: float = 5.0
    retention_lip_depth: float = 2.0

    # Minimal single-piece phone U-channel. It supports the central 50 mm of
    # the phone's lower long edge; the open ends preserve port access.
    phone_hook_span: float = 50.0
    phone_hook_wall_height: float = 25.0
    phone_hook_pad_span: float = 12.0

    # Two side clips attach below and within the yoke footprint, hanging over
    # the monitor's top edge without extending behind the yoke.
    # Their clear opening matches the 21 mm measured monitor thickness.
    monitor_thickness: float = 21.0
    monitor_clip_drop: float = 11.0
    monitor_clip_yoke_overlap: float = 0.1

    @property
    def plate_cavity_width(self) -> float:
        """Total lateral allowance around the plate, not pad compression."""
        return self.plate_width + 2 * self.plate_side_clearance

    @property
    def plate_cavity_depth(self) -> float:
        return self.plate_thickness + 2 * self.clamp_clearance

    @property
    def yoke_inner_depth(self) -> float:
        return self.benq_body_depth + 2 * self.clamp_clearance

    @property
    def yoke_top_z(self) -> float:
        return self.benq_body_height + self.wall_thickness

    @property
    def saddle_outer_width(self) -> float:
        return self.plate_cavity_width + 2 * self.wall_thickness

    @property
    def saddle_outer_depth(self) -> float:
        return self.yoke_inner_depth

    @property
    def saddle_front_y(self) -> float:
        return -self.clamp_clearance

    @property
    def saddle_back_y(self) -> float:
        return self.benq_body_depth + self.clamp_clearance

    @property
    def monitor_clip_rear_leg_y(self) -> float:
        """Rear leg centred within the yoke's front-to-back footprint."""
        outer_depth = self.monitor_thickness + 2 * self.wall_thickness
        return self.saddle_front_y + (self.yoke_inner_depth - outer_depth) / 2

    @property
    def monitor_clip_front_leg_y(self) -> float:
        return self.monitor_clip_rear_leg_y + self.wall_thickness + self.monitor_thickness

    @property
    def phone_back_y(self) -> float:
        """Phone screen-side surface, 12 mm forward of the BenQ body."""
        return self.benq_body_depth + self.phone_offset

    @property
    def phone_front_y(self) -> float:
        return self.phone_back_y + self.cradle_internal_depth

    @property
    def phone_shelf_z(self) -> float:
        return self.yoke_top_z + self.phone_height

    @property
    def spring_gap(self) -> float:
        """Relaxed gap; phones enter with a small useful PETG preload."""
        return self.phone_min_landscape_span - 1.0
