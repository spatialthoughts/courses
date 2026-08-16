"""Static theft hotspot map for City of London Police, 2024 — v2.

Same data prep as theft_hotspot_kde.py (filter to City of London, drop the
~4% of points that snap outside it), but the density surface and its legend
now follow Chainey (2005), "Mapping Crime: Understanding Hot Spots"
(documents/hotspots.pdf):

- A Nearest Neighbor Index (NNI) test for clustering is run first (a convex
  hull, not a bounding rectangle, is used for the area — the report flags
  bounding-rectangle NNI as biased).
- Density is a hand-implemented quartic kernel (bounded, meters-based search
  radius), not scipy's unbounded Gaussian kernel.
- Grid cell size follows Ratcliffe's (1999b) rule: shorter bounding-box side / 150.
- Bandwidth follows Williamson et al. (1999): the mean K-th-nearest-neighbor
  distance (K=6, a "strategic view" order per the report's own examples).
- The legend uses the report's incremental-mean-multiple classification
  (0-mean, mean-2x, 2x-3x, 3x-4x, 4x-5x, >5x) instead of a continuous colorbar.
"""

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree, ConvexHull

IN_PATH = "outputs/london_crime_2024_theft/london_theft_crimes_2024.csv"
OUT_PATH = "outputs/london_crime_2024_theft/theft_hotspot_kde_v2.png"

METRIC_CRS = "EPSG:27700"  # British National Grid, meters
PADDING_M = 150
BANDWIDTH_K = 6  # K-th nearest neighbor order (Williamson et al., 1999)
RATCLIFFE_DIVISOR = 150  # Ratcliffe (1999b) grid cell size rule

SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]
CLASS_LABELS = ["0 to mean", "Mean to 2x mean", "2x to 3x mean",
                "3x to 4x mean", "4x to 5x mean", "Greater than 5x mean"]

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "text.color": INK_PRIMARY,
    "font.family": "sans-serif",
    "font.size": 10,
})


def load_points():
    df = pd.read_csv(IN_PATH)
    before = len(df)
    df = df[df["LSOA name"].str.startswith("City of London")]
    print(f"Kept {len(df):,} of {before:,} rows within City of London "
          f"(dropped {before - len(df):,} points that snapped outside the area)")

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df["Longitude"], df["Latitude"]), crs="EPSG:4326"
    )
    gdf = gdf.to_crs(METRIC_CRS)
    x_raw, y_raw = gdf.geometry.x.values, gdf.geometry.y.values

    # data.police.uk anonymizes locations by snapping to a small fixed set of
    # points, not the true incident coordinate — so most "points" here are
    # exact duplicates. Nearest-neighbor statistics must run on the unique
    # snap locations (their spacing is what's real); the KDE below still
    # weights each unique location by its incident count so busy locations
    # read as hotter.
    coords = np.column_stack([x_raw, y_raw]).round(3)
    unique_coords, weights = np.unique(coords, axis=0, return_counts=True)
    x, y = unique_coords[:, 0], unique_coords[:, 1]
    print(f"{len(x_raw):,} incidents snap to only {len(x):,} unique locations "
          f"(max {weights.max()} incidents sharing one point) — nearest-neighbor "
          f"statistics and bandwidth below use the {len(x):,} unique locations, "
          f"weighted by incident count")
    return x, y, weights


def nni_test(x, y):
    """Nearest Neighbor Index on unique locations, area from the convex hull
    (not a bounding rectangle)."""
    coords = np.column_stack([x, y])
    n = len(coords)
    tree = cKDTree(coords)
    dists, _ = tree.query(coords, k=2)  # k=0 col is self (dist 0); k=1 col is nearest neighbor
    observed_mean_nn = dists[:, 1].mean()

    hull_area = ConvexHull(coords).volume  # 2D ConvexHull.volume is the polygon area
    expected_mean_nn = 0.5 * np.sqrt(hull_area / n)
    nni = observed_mean_nn / expected_mean_nn

    se = 0.26136 / np.sqrt(n ** 2 / hull_area)
    z = (observed_mean_nn - expected_mean_nn) / se

    verdict = "clustered" if nni < 1 else "dispersed/uniform" if nni > 1 else "random"
    print(f"NNI test: n={n:,}, convex hull area={hull_area:,.0f} m^2")
    print(f"  observed mean NN distance = {observed_mean_nn:.2f} m, "
          f"expected (CSR) = {expected_mean_nn:.2f} m")
    print(f"  NNI = {nni:.3f}, z-score = {z:.2f} -> {verdict} "
          f"(NNI<1 clustered, =1 random, >1 dispersed; more negative z = more confidence)")
    return nni, z


def compute_bandwidth(x, y, k=BANDWIDTH_K):
    coords = np.column_stack([x, y])
    tree = cKDTree(coords)
    dists, _ = tree.query(coords, k=k + 1)  # col 0 = self, col k = k-th nearest neighbor
    bandwidth = dists[:, k].mean()
    print(f"Bandwidth (mean K={k} nearest-neighbor distance): {bandwidth:.1f} m")
    return bandwidth


def compute_cell_size(x, y):
    width = x.max() - x.min()
    height = y.max() - y.min()
    cell_size = min(width, height) / RATCLIFFE_DIVISOR
    print(f"Grid cell size (Ratcliffe rule, shorter side / {RATCLIFFE_DIVISOR}): "
          f"{cell_size:.1f} m")
    return cell_size


def quartic_kde(x, y, weights, bandwidth, cell_size):
    xmin, xmax = x.min() - PADDING_M, x.max() + PADDING_M
    ymin, ymax = y.min() - PADDING_M, y.max() + PADDING_M
    xs = np.arange(xmin, xmax + cell_size, cell_size)
    ys = np.arange(ymin, ymax + cell_size, cell_size)
    xx, yy = np.meshgrid(xs, ys, indexing="ij")
    grid_points = np.column_stack([xx.ravel(), yy.ravel()])

    point_tree = cKDTree(np.column_stack([x, y]))
    grid_tree = cKDTree(grid_points)
    cells_per_point = point_tree.query_ball_tree(grid_tree, r=bandwidth)

    density = np.zeros(len(grid_points))
    norm_const = 3.0 / (np.pi * bandwidth ** 2)
    for i, cell_idxs in enumerate(cells_per_point):
        if not cell_idxs:
            continue
        idxs = np.asarray(cell_idxs)
        d = np.hypot(grid_points[idxs, 0] - x[i], grid_points[idxs, 1] - y[i])
        weight = weights[i] * norm_const * (1 - (d / bandwidth) ** 2) ** 2
        density[idxs] += weight

    print(f"Grid: {xx.shape[0]} x {xx.shape[1]} cells "
          f"({len(grid_points):,} total), {(density > 0).sum():,} cells with density > 0")
    return density.reshape(xx.shape), (xmin, xmax, ymin, ymax)


def incremental_mean_classes(density):
    positive = density[density > 0]
    mean_val = positive.mean()
    edges = [0, mean_val, 2 * mean_val, 3 * mean_val, 4 * mean_val, 5 * mean_val,
              density.max() + 1e-12]
    print(f"Incremental-mean legend: mean grid-cell density (cells>0) = {mean_val:.3e}")
    return edges


def plot(density, extent, edges, x, y, weights):
    cmap = ListedColormap(BLUE_RAMP)
    norm = BoundaryNorm(edges, cmap.N)

    xmin, xmax, ymin, ymax = extent
    data_aspect = (xmax - xmin) / (ymax - ymin)
    fig_height = 7.0
    fig_width = max(6.0, min(14.0, fig_height * data_aspect + 1.6))

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.imshow(density.T, origin="lower", extent=extent, cmap=cmap, norm=norm, alpha=0.9)
    # marker area scales with incident count at each unique (snapped) location
    ax.scatter(x, y, s=8 + 2.5 * weights, color=INK_PRIMARY, alpha=0.4,
               linewidths=0, zorder=3)

    ax.set_xlabel("Easting, British National Grid (m)", color=INK_SECONDARY)
    ax.set_ylabel("Northing, British National Grid (m)", color=INK_SECONDARY)
    ax.tick_params(colors=INK_MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_aspect("equal")

    patches = [mpatches.Patch(color=BLUE_RAMP[i], label=CLASS_LABELS[i]) for i in range(6)]
    legend = ax.legend(handles=patches, title="Theft density\n(quartic KDE, incremental-mean classes)",
                        loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False,
                        fontsize=8.5, labelcolor=INK_SECONDARY, title_fontsize=8.5)
    legend.get_title().set_color(INK_SECONDARY)

    fig.suptitle("City of London Police: theft hotspots, 2024 (v2)",
                  color=INK_PRIMARY, fontsize=13, x=0.02, ha="left", y=0.995)
    fig.text(0.02, 0.965,
              "Other theft, Shoplifting, Theft from the person, Burglary, Bicycle theft,\n"
              "Robbery, Vehicle crime — marker size = incidents at that snapped location.\n"
              "Raw density, not a rate: City of London's ~8,000 residents are vastly\n"
              "outnumbered by its daytime worker/visitor population, so this reflects\n"
              "activity concentration, not necessarily per-capita risk.",
              fontsize=8, color=INK_MUTED, ha="left", va="top")

    fig.tight_layout(rect=(0, 0, 0.80, 0.80))
    fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {OUT_PATH}")


def main():
    x, y, weights = load_points()
    nni_test(x, y)
    bandwidth = compute_bandwidth(x, y)
    cell_size = compute_cell_size(x, y)
    density, extent = quartic_kde(x, y, weights, bandwidth, cell_size)
    edges = incremental_mean_classes(density)
    plot(density, extent, edges, x, y, weights)


if __name__ == "__main__":
    main()
