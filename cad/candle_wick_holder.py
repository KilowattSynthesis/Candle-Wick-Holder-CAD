from dataclasses import dataclass
from pathlib import Path

import build123d as bd
import build123d_ease as bde
from build123d_ease import show
from loguru import logger


@dataclass
class PartSpec:
    """Specification for candle_wick_holder."""

    candle_id: float = 72.0
    candle_od: float = 80.0

    candle_thread_depth: float = 5.0

    cross_width: float = 10.0
    cross_thickness: float = 3

    vertical_wall_thickness: float = 3

    wick_diameter: float = 3.0

    anchor_diameter: float = 4.0
    inner_anchor_x_pos: float = 8.0
    anchor_length: float = 8.0

    def __post_init__(self) -> None:
        """Post initialization checks."""


def make_candle_wick_holder(spec: PartSpec) -> bd.Part | bd.Compound:
    """Create a CAD model of candle_wick_holder."""
    p = bd.Part(None)

    cross_part = bd.Part(None)
    for rot in (0, 90):
        cross_part += bd.Box(
            spec.candle_od * 1.5,
            spec.cross_width,
            spec.cross_thickness + spec.candle_thread_depth,
            align=bde.align.ANCHOR_BOTTOM,
        ).rotate(axis=bd.Axis.Z, angle=rot)

    p += cross_part & bd.Cylinder(
        radius=spec.candle_od / 2 + spec.vertical_wall_thickness,
        height=spec.cross_thickness + spec.candle_thread_depth,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Remove the wick hole.
    p -= bd.Cone(
        bottom_radius=6 / 2,
        top_radius=spec.wick_diameter / 2,
        height=spec.candle_thread_depth * 2,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Remove the candle threads.
    p -= bd.Cylinder(
        radius=spec.candle_od / 2,
        height=spec.candle_thread_depth,
        align=bde.align.ANCHOR_BOTTOM,
    ) - bd.Cylinder(
        radius=spec.candle_id / 2,
        height=spec.candle_thread_depth,
        align=bde.align.ANCHOR_BOTTOM,
    )

    # Add the wick anchor.
    for x_pos in (
        spec.inner_anchor_x_pos,
        spec.inner_anchor_x_pos + 7,
        -spec.inner_anchor_x_pos,
        -(spec.inner_anchor_x_pos + 7),
    ):
        p += bd.Pos(
            (
                0,
                x_pos,
                spec.cross_thickness + spec.candle_thread_depth,
            )
        ) * bd.Cylinder(
            radius=spec.anchor_diameter / 2,
            height=spec.anchor_length,
            align=bde.align.ANCHOR_BOTTOM,
        )

    return p


if __name__ == "__main__":
    parts = {
        "candle_wick_holder": show(make_candle_wick_holder(PartSpec())),
    }

    logger.info("Showing CAD model(s)")

    (export_folder := Path(__file__).parent.with_name("build")).mkdir(
        exist_ok=True
    )
    for name, part in parts.items():
        assert isinstance(part, bd.Part | bd.Solid | bd.Compound), (
            f"{name} is not an expected type ({type(part)})"
        )
        if not part.is_manifold:
            logger.warning(f"Part '{name}' is not manifold")

        bd.export_stl(part, str(export_folder / f"{name}.stl"))
        bd.export_step(part, str(export_folder / f"{name}.step"))
