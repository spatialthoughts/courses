"""Choropleth maps with and without normalization.

This example builds a world choropleth of fossil CO2 emissions and shows why
normalization matters:

* Total emissions (Mt CO2)      -> NOT normalized. Large, populous countries
                                   dominate simply because they are big.
* Per capita emissions (t CO2)  -> normalized by population. This reveals how
                                   emissions-intensive each country actually is.

Data is fetched dynamically at run time and nothing is stored in the repository.
Source downloads go to a temporary folder; the joined shapefile and the two
map images are written to an ``output/`` folder next to this script.

Data sources
------------
* Country boundaries : Natural Earth, 1:10m Admin 0 - Countries (India POV).
                       https://www.naturalearthdata.com/
* CO2 emissions      : Global Carbon Project - Fossil CO2 Emissions, 2025v15
                       (Andrew, R.M. & Peters, G.P., CICERO). CC-BY 4.0.
                       https://doi.org/10.5281/zenodo.17417124

Run with an environment that has geopandas and matplotlib, e.g.:
    /opt/miniconda3/envs/python_foundation/bin/python co2_choropleth_normalization.py
"""

import os
import tempfile
import urllib.request

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import BoundaryNorm

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Natural Earth is served from its CDN. The naturalearthdata.com download page
# links here.
BOUNDARIES_URL = (
    'https://naciscdn.org/naturalearth/10m/cultural/'
    'ne_10m_admin_0_countries_ind.zip'
)
# Flat CSV with one row per country-year. It already contains both the total
# ("Total", Mt CO2) and the normalized ("Per Capita", t CO2) values.
EMISSIONS_URL = (
    'https://zenodo.org/records/17417124/files/GCB2025v15_MtCO2_flat.csv'
)

ISO_COLUMN = 'ISO 3166-1 alpha-3'          # join key in the CO2 table
EQUAL_EARTH = 'EPSG:8857'                  # Equal Earth projection for the maps

# Palette and legend follow this reference map:
# https://mapfast.co/images/choropleth-map-guide/world-co2-emissions-per-capita-2022.png
# Sequential blue-purple ramp, with a horizontal colour bar whose classes are
# spaced evenly and whose top class is open ended (">").
CMAP = 'BuPu'
# Class breaks. The last value is an open-ended ">" bin.
TOTAL_BINS = [1, 10, 30, 100, 300, 1000, 3000, 10000]      # Mt CO2
PERCAPITA_BINS = [0.1, 0.5, 1, 2, 4, 5, 6, 9, 20]          # t CO2 per person
MISSING_COLOR = '#f0f0f0'                                  # "no data" countries

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'output')

ATTRIBUTION = (
    'Data: Global Carbon Project - Fossil CO2 Emissions (GCB 2025v15), '
    'Andrew & Peters 2025, CC-BY 4.0   |   '
    'Boundaries: Natural Earth (India POV)   |   Projection: Equal Earth'
)


# ---------------------------------------------------------------------------
# Fetch and join
# ---------------------------------------------------------------------------

def fetch_data(download_dir):
    """Download the boundaries and the CO2 table into download_dir."""
    boundaries_path = os.path.join(download_dir, 'ne_10m_admin_0_countries_ind.zip')
    emissions_path = os.path.join(download_dir, 'GCB2025v15_MtCO2_flat.csv')

    print('Downloading country boundaries ...')
    urllib.request.urlretrieve(BOUNDARIES_URL, boundaries_path)

    print('Downloading CO2 emissions table ...')
    urllib.request.urlretrieve(EMISSIONS_URL, emissions_path)

    return boundaries_path, emissions_path


def latest_year_emissions(emissions_path):
    """Return a DataFrame of per-country emissions for the most recent year."""
    df = pd.read_csv(emissions_path)

    latest_year = int(df.loc[df['Total'].notna(), 'Year'].max())
    print(f'Latest year with data: {latest_year}')

    year_df = df[df['Year'] == latest_year].copy()

    # Keep real countries only: valid 3-letter ISO code, drop the "WLD" world
    # aggregate.
    year_df = year_df.dropna(subset=[ISO_COLUMN])
    year_df = year_df[year_df[ISO_COLUMN].str.len() == 3]
    year_df = year_df[year_df[ISO_COLUMN] != 'WLD']

    year_df = year_df[[ISO_COLUMN, 'Total', 'Per Capita']].rename(
        columns={'Total': 'co2_total', 'Per Capita': 'co2_percap'}
    )
    year_df['year'] = latest_year
    return year_df


def build_joined_layer(boundaries_path, emissions_path):
    """Join CO2 emissions onto the country polygons."""
    countries = gpd.read_file(boundaries_path)
    countries = countries[['NAME', 'ISO_A3_EH', 'geometry']].rename(
        columns={'NAME': 'name', 'ISO_A3_EH': 'iso_a3'}
    )

    emissions = latest_year_emissions(emissions_path)

    joined = countries.merge(
        emissions, left_on='iso_a3', right_on=ISO_COLUMN, how='left'
    )
    joined = joined.drop(columns=[ISO_COLUMN])

    matched = joined['co2_total'].notna().sum()
    print(f'Joined emissions for {matched} of {len(joined)} country polygons')
    return joined


# ---------------------------------------------------------------------------
# Mapping
# ---------------------------------------------------------------------------

def make_map(gdf, column, bins, title, subtitle, legend_label, out_path):
    """Render one 300 dpi Equal Earth choropleth.

    ``bins`` are the class breaks; the last break starts an open-ended ">" class.
    The classes are drawn as an evenly spaced horizontal colour bar, matching the
    reference map.
    """
    gdf_ee = gdf.to_crs(EQUAL_EARTH)

    cmap = plt.get_cmap(CMAP)
    norm = BoundaryNorm(bins, cmap.N, extend='max')

    fig, ax = plt.subplots(1, 1, figsize=(16, 8.5))

    gdf_ee.plot(
        ax=ax,
        column=column,
        cmap=cmap,
        norm=norm,
        linewidth=0.3,
        edgecolor='#333333',
        missing_kwds={'color': MISSING_COLOR},
    )

    ax.set_axis_off()

    # Horizontal colour bar: evenly spaced classes, arrow on the open-ended max.
    colourbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=cmap),
        ax=ax,
        orientation='horizontal',
        spacing='uniform',
        extend='max',
        ticks=bins,
        shrink=0.45,
        pad=0.03,
        aspect=40,
    )
    tick_labels = [f'{b:g}' for b in bins[:-1]] + [f'>{bins[-1]:g}']
    colourbar.ax.set_xticklabels(tick_labels)
    colourbar.ax.tick_params(labelsize=9)
    colourbar.ax.set_title(legend_label, fontsize=11, fontweight='bold', pad=8)
    colourbar.outline.set_visible(False)
    # Attribution sits just below the colour bar.
    colourbar.ax.set_xlabel(ATTRIBUTION, fontsize=8, color='#666666', labelpad=10)

    # Title and subtitle, kept close together.
    fig.text(0.5, 0.99, title, ha='center', va='top',
             fontsize=20, fontweight='bold')
    fig.text(0.5, 0.945, subtitle, ha='center', va='top',
             fontsize=12, color='#444444')

    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'Wrote {out_path}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    download_dir = tempfile.mkdtemp(prefix='co2_choropleth_')

    boundaries_path, emissions_path = fetch_data(download_dir)
    joined = build_joined_layer(boundaries_path, emissions_path)

    shapefile_path = os.path.join(OUTPUT_DIR, 'countries_with_co2_emissions.shp')
    joined.to_file(shapefile_path)
    print(f'Wrote {shapefile_path}')

    year = int(joined['year'].dropna().iloc[0])

    make_map(
        joined,
        column='co2_total',
        bins=TOTAL_BINS,
        title=f'Fossil CO2 Emissions by Country, {year}',
        subtitle='Total emissions - not normalized: big, populous countries dominate',
        legend_label='(Total CO2, Mt)',
        out_path=os.path.join(OUTPUT_DIR, f'co2_total_{year}.png'),
    )

    make_map(
        joined,
        column='co2_percap',
        bins=PERCAPITA_BINS,
        title=f'Fossil CO2 Emissions by Country, {year}',
        subtitle='Per capita emissions - normalized by population: emissions intensity per person',
        legend_label='(Tons CO2 per person)',
        out_path=os.path.join(OUTPUT_DIR, f'co2_per_capita_{year}.png'),
    )

    print('Done.')


if __name__ == '__main__':
    main()
