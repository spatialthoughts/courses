"""Static theft hotspot map for City of London Police, 2024.

Loads the filtered theft CSV, drops the ~4% of points that snap outside City
of London (an anonymization artifact, not real City of London Police
incidents), computes a Gaussian KDE density surface in a metric CRS, and
renders it as a static matplotlib map with the underlying points overlaid.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

IN_PATH = "outputs/london_crime_2024_theft/london_theft_crimes_2024.csv"
OUT_PATH = "outputs/london_crime_2024_theft/theft_hotspot_kde.png"

# Metric CRS for correct KDE bandwidth (British National Grid, meters)
METRIC_CRS = "EPSG:27700"
GRID_RESOLUTION = 300j  # points per axis
PADDING_M = 150  # extent padding around the points, in meters

# dataviz skill reference palette
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
# Sequential blue ramp (light -> dark), steps 100..700
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"]

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
    return gdf.to_crs(METRIC_CRS)


def compute_kde(gdf):
    x = gdf.geometry.x.values
    y = gdf.geometry.y.values
    kde = gaussian_kde(np.vstack([x, y]))

    xmin, xmax = x.min() - PADDING_M, x.max() + PADDING_M
    ymin, ymax = y.min() - PADDING_M, y.max() + PADDING_M
    xx, yy = np.mgrid[xmin:xmax:GRID_RESOLUTION, ymin:ymax:GRID_RESOLUTION]
    positions = np.vstack([xx.ravel(), yy.ravel()])
    density = kde(positions).reshape(xx.shape)
    return density, (xmin, xmax, ymin, ymax), x, y


def plot(density, extent, x, y):
    cmap = LinearSegmentedColormap.from_list("theft_density", BLUE_RAMP)

    xmin, xmax, ymin, ymax = extent
    data_aspect = (xmax - xmin) / (ymax - ymin)
    fig_height = 7.0
    fig_width = max(6.0, min(14.0, fig_height * data_aspect + 1.6))  # + room for colorbar/labels

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    im = ax.imshow(density.T, origin="lower", extent=extent, cmap=cmap, alpha=0.9)
    ax.scatter(x, y, s=6, color=INK_PRIMARY, alpha=0.35, linewidths=0, zorder=3)

    ax.set_xlabel("Easting, British National Grid (m)", color=INK_SECONDARY)
    ax.set_ylabel("Northing, British National Grid (m)", color=INK_SECONDARY)
    ax.tick_params(colors=INK_MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_aspect("equal")

    # Tie the colorbar's height to the (aspect-adjusted) axes height, rather
    # than the figure's nominal layout, so it doesn't overshoot the plot.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="4%", pad=0.15)
    cbar = fig.colorbar(im, cax=cax)
    cbar.set_label("Relative theft density (Gaussian KDE)", color=INK_SECONDARY)
    cbar.ax.tick_params(colors=INK_MUTED, labelsize=8)
    cbar.outline.set_visible(False)

    fig.suptitle("City of London Police: theft hotspots, 2024",
                  color=INK_PRIMARY, fontsize=13, x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.955, "Other theft, Shoplifting, Theft from the person, Burglary, "
                           "Bicycle theft, Robbery, Vehicle crime — dots are individual incidents",
              fontsize=9, color=INK_MUTED, ha="left")

    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT_PATH, dpi=150)
    plt.close(fig)
    print(f"Saved {OUT_PATH}")


def main():
    gdf = load_points()
    density, extent, x, y = compute_kde(gdf)
    plot(density, extent, x, y)


if __name__ == "__main__":
    main()
