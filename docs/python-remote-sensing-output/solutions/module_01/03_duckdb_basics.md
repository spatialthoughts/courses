Query parameters for commonly used cities


```python
country_iso2 = 'IN'
city_name = 'Bengaluru'
region = 'IN-KA'

country_iso2 = 'NP'
city_name = 'Paunauti'
region = 'NP-P3'

country_iso2 = 'US'
city_name = 'Golden'
region = 'US-CO'

country_iso2 = 'US'
city_name = 'Fairbanks'
region = 'US-AK'

country_iso2 = 'IT'
city_name = 'Catania'
region = 'IT-82'

country_iso2 = 'US'
city_name = 'Louisville'
region = 'US-CO'

country_iso2 = 'AR'
city_name = 'Buenos Aires'
region = 'AR-C'
```

### Exercise

View the resulting boundary.


```python
city_gdf = gpd.GeoDataFrame(
    results,
    geometry=gpd.GeoSeries.from_wkb(results['geometry'].apply(bytes)),
    crs='EPSG:4326'
)

viz(city_gdf)
```


```python
if 'google.colab' in str(get_ipython()):
    drive_folder_root = 'MyDrive'
    drive_data_folder = 'python-remote-sensing'
    drive_folder_path = os.path.join(
          '/content/drive', drive_folder_root, drive_data_folder)
    aoi_filepath = os.path.join(drive_folder_path, 'aoi.geojson')
else:
    aoi_filepath = os.path.join(output_folder, 'aoi.geojson')
aoi_filepath
```


```python
city_gdf.to_file(aoi_filepath)
```
