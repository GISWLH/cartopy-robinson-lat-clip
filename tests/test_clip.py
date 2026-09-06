from __future__ import annotations

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
import pytest
from shapely.geometry import Polygon

from robinson_lat_clip import (
    clip_robinson_south_of,
    equatorial_x_limits,
    projected_parallel_y,
    robinson_boundary_above_min_lat,
)

MIN_LAT = -60.0
EQ_TOL = 1.0  # projected metres; Robinson equator is ~1.7e7 m wide


def _path_polygon(path):
    verts = np.asarray(path.vertices, dtype=float)
    poly = Polygon(verts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly, verts


def _longest_vertical_run(verts: np.ndarray, x_atol: float = 1.0) -> float:
    """Longest |dy| among consecutive vertices that share the same x."""
    longest = 0.0
    for p0, p1 in zip(verts[:-1], verts[1:]):
        if abs(p0[0] - p1[0]) <= x_atol:
            longest = max(longest, abs(float(p1[1] - p0[1])))
    return longest


def test_boundary_is_valid_closed_polygon():
    path = robinson_boundary_above_min_lat(MIN_LAT)
    poly, verts = _path_polygon(path)
    assert np.allclose(verts[0], verts[-1])
    assert poly.is_valid
    assert poly.area > 0


def test_southern_edge_is_the_cutoff_parallel():
    path = robinson_boundary_above_min_lat(MIN_LAT)
    y_cut = projected_parallel_y(MIN_LAT)
    ymin = float(np.asarray(path.vertices)[:, 1].min())
    assert ymin == pytest.approx(y_cut, rel=0, abs=1.0)


def test_xlim_stays_equatorial_not_60s_width():
    proj = ccrs.Robinson()
    path = robinson_boundary_above_min_lat(MIN_LAT, proj=proj)
    verts = np.asarray(path.vertices, dtype=float)

    x0, x1 = equatorial_x_limits(proj)
    assert verts[:, 0].min() == pytest.approx(x0, abs=EQ_TOL)
    assert verts[:, 0].max() == pytest.approx(x1, abs=EQ_TOL)

    # The 60S parallel is narrower than the equator. If we had used
    # set_extent(lat_min=-60), xlim would collapse to this width.
    south = proj.transform_points(
        ccrs.PlateCarree(),
        np.array([-180.0, 180.0]),
        np.array([MIN_LAT, MIN_LAT]),
    )
    width_60s = float(south[1, 0] - south[0, 0])
    width_eq = float(x1 - x0)
    assert width_60s < 0.85 * width_eq
    assert (verts[:, 0].max() - verts[:, 0].min()) > 0.98 * width_eq


def test_left_and_right_extremes_are_equatorial():
    path = robinson_boundary_above_min_lat(MIN_LAT)
    verts = np.asarray(path.vertices, dtype=float)
    left = verts[np.argmin(verts[:, 0])]
    right = verts[np.argmax(verts[:, 0])]
    assert abs(left[1]) < 1.0
    assert abs(right[1]) < 1.0


def test_clip_does_not_change_axes_xlim():
    fig = plt.figure(figsize=(4.0, 2.2))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=ccrs.Robinson())
    ax.set_global()
    path = clip_robinson_south_of(ax, MIN_LAT)
    x0, x1 = equatorial_x_limits(ax.projection)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    plt.close(fig)

    assert xlim[0] == pytest.approx(x0, abs=EQ_TOL)
    assert xlim[1] == pytest.approx(x1, abs=EQ_TOL)
    assert ylim[0] == pytest.approx(ax.projection.y_limits[0], abs=EQ_TOL)
    assert ylim[1] == pytest.approx(ax.projection.y_limits[1], abs=EQ_TOL)
    assert float(np.asarray(path.vertices)[:, 1].min()) == pytest.approx(
        projected_parallel_y(MIN_LAT), abs=1.0
    )


def test_set_extent_inserts_vertical_side_cuts():
    """Document the Cartopy behaviour this package exists to avoid."""
    fig = plt.figure(figsize=(4.0, 2.2))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=ccrs.Robinson())
    ax.set_global()
    ax.set_extent([-179.5, 179.5, MIN_LAT, 89.5], crs=ccrs.PlateCarree())
    fig.canvas.draw()
    verts = np.asarray(ax.spines["geo"].get_path().vertices, dtype=float)
    plt.close(fig)
    # set_extent clips the oval with a rectangle, so the equator is replaced
    # by a vertical chord on each side.
    assert _longest_vertical_run(verts) > 1.0e6


def test_clipped_path_has_no_vertical_side_cuts():
    path = robinson_boundary_above_min_lat(MIN_LAT)
    verts = np.asarray(path.vertices, dtype=float)
    assert _longest_vertical_run(verts) < 5.0e4


def test_invalid_min_lat_raises():
    with pytest.raises(ValueError, match="min_lat"):
        robinson_boundary_above_min_lat(min_lat=120.0)
    with pytest.raises(ValueError, match="min_lat"):
        robinson_boundary_above_min_lat(min_lat=-90.0)
