"""Clip a Cartopy Robinson map along a latitude without rectangular side cuts."""

from .clip import (
    clip_robinson_south_of,
    equatorial_x_limits,
    projected_parallel_y,
    robinson_boundary_above_min_lat,
)

__all__ = [
    "clip_robinson_south_of",
    "equatorial_x_limits",
    "projected_parallel_y",
    "robinson_boundary_above_min_lat",
]
__version__ = "0.1.0"
