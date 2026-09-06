# Why `set_extent(lat_min=-60)` cuts vertical sides

Robinson is an oval. Its projected width is largest at the equator and
shrinks toward the poles.

```text
full Robinson xlim  = equatorial width
60S projected width = ~80% of equatorial width
```

When Cartopy is asked to show only `lat >= -60` via `set_extent`, it
replaces the oval clip path with a **rectangle** whose `xlim` is the
projected width at 60°S. The equator is then wider than the axes, so
the left and right limbs become vertical cuts.

This package keeps equatorial `xlim` and clips with a truncated oval:

```text
ellipse  ∩  { y >= y(60S) }
```

The outline is still an ellipse on the sides, with a flat chord at 60°S.
