# Agent notes

This is a small Cartopy helper, not a hydrology analysis repo.

- Keep the public API in `src/robinson_lat_clip/clip.py`.
- Do not call `ax.set_extent(lat_min=...)` as the crop. That is the bug.
- Tests must keep proving that equatorial `xlim` survives the clip.
- Do not commit GitHub tokens or `.env` files.
