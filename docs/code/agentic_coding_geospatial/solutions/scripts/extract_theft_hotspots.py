"""Extract theft hotspot polygons from the quartic KDE surface.

Reuses the density-surface computation from theft_hotspot_kde_v2.py, takes
the grid cells classified "Greater than 5x mean" (the report's top
incremental-mean class), vectorizes them into polygons (8-connectivity, so
diagonally touching hot cells merge into one hotspot), and writes the result
as a GeoJSON in WGS84.
"""

import geopandas as gpd
import numpy as np
import rasterio.features
import rasterio.transform
from shapely.geometry import shape

from theft_hotspot_kde_v2 import (
    METRIC_CRS,
    compute_bandwidth,
    compute_cell_size,
    incremental_mean_classes,
    load_points,
    quartic_kde,
)

OUT_PATH = "outputs/london_crime_2024_theft/london_theft_hotspots.geojson"


def extract_hotspot_polygons(density, extent, threshold, cell_size):
    xmin, xmax, ymin, ymax = extent

    # rasterio expects row 0 = top (ymax), rows increasing downward;
    # density[i, j] has i over x (ascending) and j over y (ascending), so
    # transpose then flip vertically to match that convention.
    raster = np.flipud(density.T)
    mask = raster >= threshold

    # shapes() merges adjacent pixels only when they share the same VALUE, not
    # just the same mask — pass a constant field so all hot cells merge.
    constant_field = np.ones(raster.shape, dtype="uint8")
    transform = rasterio.transform.from_origin(xmin, ymax, cell_size, cell_size)
    shapes = rasterio.features.shapes(
        constant_field, mask=mask, transform=transform, connectivity=8
    )
    geoms = [shape(geom) for geom, _ in shapes]
    print(f"Vectorized {mask.sum():,} cells >= threshold into {len(geoms)} polygon(s) "
          f"before dissolve")
    return geoms


def main():
    x, y, weights = load_points()
    bandwidth = compute_bandwidth(x, y)
    cell_size = compute_cell_size(x, y)
    density, extent = quartic_kde(x, y, weights, bandwidth, cell_size)
    edges = incremental_mean_classes(density)
    threshold = edges[5]  # lower bound of the "Greater than 5x mean" class
    print(f"'Greater than 5x mean' threshold: {threshold:.3e}")

    geoms = extract_hotspot_polygons(density, extent, threshold, cell_size)
    if not geoms:
        raise SystemExit("No grid cells met the 'Greater than 5x mean' threshold — nothing to save.")

    gdf = gpd.GeoDataFrame({"hotspot_id": range(1, len(geoms) + 1)}, geometry=geoms, crs=METRIC_CRS)
    gdf["area_m2"] = gdf.geometry.area.round(1)
    gdf = gdf.sort_values("area_m2", ascending=False).reset_index(drop=True)
    gdf["hotspot_id"] = range(1, len(gdf) + 1)

    gdf_wgs84 = gdf.to_crs("EPSG:4326")
    gdf_wgs84.to_file(OUT_PATH, driver="GeoJSON")
    print(f"Saved {len(gdf_wgs84)} hotspot polygon(s) to {OUT_PATH}")
    print(gdf[["hotspot_id", "area_m2"]].to_string(index=False))


if __name__ == "__main__":
    main()
