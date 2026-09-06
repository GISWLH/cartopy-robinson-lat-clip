#!/usr/bin/env python3
"""Draw a Robinson globe clipped at 60S without rectangular side cuts."""

from __future__ import annotations

from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from robinson_lat_clip import clip_robinson_south_of

OUT = Path(__file__).with_name("robinson_clip_60s.png")


def main() -> None:
    fig = plt.figure(figsize=(8.0, 4.2), facecolor="white")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=ccrs.Robinson())
    ax.set_global()
    ax.set_facecolor("white")
    ax.add_feature(cfeature.LAND, facecolor="#f7f7f7", edgecolor="none")
    ax.add_feature(cfeature.COASTLINE, linewidth=0.4, edgecolor="#888888")
    ax.plot(
        [-180, 180],
        [-60, -60],
        transform=ccrs.PlateCarree(),
        color="#666666",
        linewidth=0.6,
    )
    clip_robinson_south_of(ax, min_lat=-60.0)
    ax.spines["geo"].set_edgecolor("#cccccc")
    fig.savefig(OUT, dpi=140, facecolor="white")
    print(OUT)


if __name__ == "__main__":
    main()
