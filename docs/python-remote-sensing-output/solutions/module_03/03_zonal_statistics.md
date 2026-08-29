### Exercise

[CHIRPS](https://www.chc.ucsb.edu/data/chirps3) - Climate Hazards Center InfraRed Precipitation with Station data - is gridded rainfall time-series data with coverage between 60°N to 60°S latitudes. The data is available aggregated over various time-periods.

The annual GeoTIFF files are available at https://data.chc.ucsb.edu/products/CHIRPS/v3.0/annual/global/tifs/.

Pick a year and calculate the average rainfall in each admin2 polygon.


```python
data_url = 'https://data.chc.ucsb.edu/products/CHIRPS/v3.0/annual/global/tifs/chirps-v3.0.2025.tif'
chirps_da = rxr.open_rasterio(
    data_url,
    chunks={'x': 1024, 'y': 1024},
)
chirps_da
```


```python
admin2_gdf_reprojected = admin2_gdf.to_crs(chirps_da.rio.crs)
bounds = admin2_gdf_reprojected.total_bounds  # (minx, miny, maxx, maxy)
chirps_da_clipped = chirps_da.rio.clip_box(*bounds)
chirps_da_clipped
```


```python
aggregated = chirps_da_clipped.xvec.zonal_stats(
    admin2_gdf_reprojected.geometry,
    x_coords='x',
    y_coords='y',
    stats=['mean'],
    method='exactextract'
)
```


```python
aggregated['adm2_name'] = ('geometry', admin2_gdf_reprojected['adm2_name'].values)
aggregated = aggregated.assign_coords({'adm2_name': aggregated['adm2_name']})
aggregated_gdf = aggregated.xvec.to_geodataframe(
    name='precipitation_mean', geometry='geometry')
aggregated_gdf = aggregated_gdf.reset_index()
aggregated_gdf = aggregated_gdf.rename(columns={'precipitation_mean': 'precipitation'})
aggregated_gdf = aggregated_gdf[['adm2_name', 'precipitation', 'geometry']]
aggregated_gdf.head()
```
