"""Clip a Robinson globe south of a latitude while keeping elliptical sides.

Why not ``ax.set_extent(..., lat_min=-60)``
------------------------------------------
Cartopy then replaces the Robinson oval with a rectangular clip whose
``xlim`` is the *projected width at that latitude*. On Robinson, 60°S is
narrower than the equator, so the left/right limbs become vertical cuts.

This module instead:

1. Takes the native Robinson ellipse path.
2. Intersects it with the half-plane ``y >= y(min_lat)``.
3. Calls ``ax.set_boundary`` with that truncated oval.
4. Restores equatorial ``xlim`` (and the original projection ``ylim``).

The visible outline is then a Robinson ellipse with a flat 60°S chord.
"""

from __future__ import annotations

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path as MplPath
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import box as shapely_box

DEFAULT_MIN_LAT = -60.0


def equatorial_x_limits(proj: ccrs.Projection | None = None) -> tuple[float, float]:
    """Return the full equatorial Robinson x-range."""
    if proj is None:
        proj = ccrs.Robinson()
    x0, x1 = proj.x_limits
    return float(x0), float(x1)


def projected_parallel_y(lat: float, proj: ccrs.Projection | None = None) -> float:
    """Projected y of a parallel at lon=0."""
    if proj is None:
        proj = ccrs.Robinson()
    return float(proj.transform_point(0.0, lat, ccrs.PlateCarree())[1])


def robinson_boundary_above_min_lat(
    min_lat: float = DEFAULT_MIN_LAT,
    proj: ccrs.Projection | None = None,
) -> MplPath:
    """Robinson ellipse cut along ``min_lat``, with curved sides kept intact."""
    if not -90.0 < float(min_lat) < 90.0:
        raise ValueError(f"min_lat must be inside (-90, 90); got {min_lat}.")
    if proj is None:
        proj = ccrs.Robinson()

    fig = plt.figure(figsize=(1.0, 1.0))
    tmp = fig.add_axes([0.0, 0.0, 1.0, 1.0], projection=proj)
    tmp.set_global()
    fig.canvas.draw()
    verts = np.asarray(tmp.spines["geo"].get_path().vertices, dtype=float)
    plt.close(fig)

    ellipse = ShapelyPolygon(verts).buffer(0)
    x0, x1 = proj.x_limits
    _y0, y1 = proj.y_limits
    y_cut = projected_parallel_y(min_lat, proj)
    keep = shapely_box(x0 - 1.0, y_cut, x1 + 1.0, y1 + 1.0)
    clipped = ellipse.intersection(keep)
    if clipped.is_empty:
        raise ValueError(f"Clipping at lat={min_lat} produced an empty geometry.")
    if clipped.geom_type == "MultiPolygon":
        clipped = max(clipped.geoms, key=lambda geom: geom.area)
    coords = np.asarray(clipped.exterior.coords, dtype=float)
    return MplPath(coords, closed=True)


def clip_robinson_south_of(
    ax,
    min_lat: float = DEFAULT_MIN_LAT,
    *,
    keep_equatorial_xlim: bool = True,
    keep_full_ylim: bool = True,
) -> MplPath:
    """Hide everything south of ``min_lat`` on a Robinson GeoAxes.

    Parameters
    ----------
    ax:
        A Cartopy GeoAxes using ``ccrs.Robinson()``.
    min_lat:
        Southern cutoff in degrees. Default ``-60`` hides Antarctica.
    keep_equatorial_xlim:
        If True (default), restore the equatorial ellipse width so Cartopy
        cannot collapse ``xlim`` to the cutoff-latitude width.
    keep_full_ylim:
        If True (default), keep the original Robinson ``y_limits``. The
        clipped path still hides the southern cap; the axes box stays the
        same height as a full globe.
    """
    if not hasattr(ax, "set_boundary"):
        raise TypeError("ax must be a Cartopy GeoAxes with set_boundary().")

    path = robinson_boundary_above_min_lat(min_lat, proj=ax.projection)
    ax.set_boundary(path, transform=ax.transData)

    if keep_equatorial_xlim:
        ax.set_xlim(*equatorial_x_limits(ax.projection))
    if keep_full_ylim:
        ax.set_ylim(*ax.projection.y_limits)
    else:
        ax.set_ylim(float(path.vertices[:, 1].min()), float(ax.projection.y_limits[1]))
    ax.set_aspect("equal")
    return path
