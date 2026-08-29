### Exercise

The [GEE Community Catalog](https://gee-community-catalog.org/) is a large collection of community curated datasets hosted on Earth Engine. The XEE extension works equally well on these datasets.

Access the [Global Annual Simulated NPP-VIIRS Nighttime Light Dataset (1992-2023)](https://gee-community-catalog.org/projects/srunet_npp_viirs_ntl/) dataset and plot a time-series of average nighttime lights for your region of interest.


```python
ntlCol = ee.ImageCollection('projects/sat-io/open-datasets/srunet-npp-viirs-ntl')

grid_params = helpers.extract_grid_params(ntlCol)

ds = xr.open_dataset(
    ntlCol,
    engine='ee',
    **grid_params,
    chunks={} # Enable dask
)
ds
```


```python
start_year = 1992
end_year = 2023

# Create a new time coordinate representing the years
years = pd.to_datetime([f'{year}-01-01' for year in range(start_year, end_year + 1)])

# Assign the new time coordinate to the dataset
ds['time'] = years

da = ds['b1']
bounds = aoi_gdf.total_bounds  # (minx, miny, maxx, maxy)
da_clipped = da.rio.clip_box(*bounds)
da_clipped
```


```python
%%time
da_clipped = da_clipped.compute()
```


```python
aggregated = da_clipped.xvec.zonal_stats(
    aoi_gdf.geometry,
    x_coords='x',
    y_coords='y',
    stats=['mean'],
    method='exactextract'
)
aggregated['name'] = ('geometry', aoi_gdf['primary_name'].values)
aggregated = aggregated.assign_coords({'name': aggregated['name']})
aggregated_gdf = aggregated.xvec.to_geodataframe(name='ntl_mean', geometry='geometry')
output_gdf = aggregated_gdf.reset_index()
output_gdf = output_gdf[['name', 'time', 'ntl_mean', 'geometry']]
```


```python
import matplotlib.pyplot as plt

# Create the plot
plt.figure(figsize=(8, 4))
plt.plot(output_gdf['time'], output_gdf['ntl_mean'], marker='o')

# Add labels and title
plt.xlabel('Year')
plt.ylabel('Average Nighttime Lights')
plt.title('Aggregated Nighttime Lights (NTL)')

# Set y-axis to start from 0
plt.ylim(ymin=0, ymax=60)

# Improve date formatting on x-axis
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
```
