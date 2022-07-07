## Elevation Profile Plot from a GPS Track


```python
import pandas as pd
import geopandas as gpd
import os

%matplotlib inline
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
```


```python
data_pkg_path = 'data'
gpx_path = os.path.join(data_pkg_path, 'gps', 'sample_gps_track.gpx')

# GPX files contain many layers. Read the 'track_points' layer
gdf = gpd.read_file(gpx_path, layer='track_points')
gdf = gdf[['track_fid','ele', 'time', 'speed', 'geometry']]
gdf
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_fid</th>
      <th>ele</th>
      <th>time</th>
      <th>speed</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>916.334</td>
      <td>2020-02-22T05:18:17+00:00</td>
      <td>7.28</td>
      <td>POINT (77.58614 12.91214)</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>917.815</td>
      <td>2020-02-22T05:18:19+00:00</td>
      <td>6.12</td>
      <td>POINT (77.58627 12.91213)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>919.915</td>
      <td>2020-02-22T05:18:21+00:00</td>
      <td>6.00</td>
      <td>POINT (77.58637 12.91212)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>918.828</td>
      <td>2020-02-22T05:18:23+00:00</td>
      <td>9.41</td>
      <td>POINT (77.58651 12.91210)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>919.799</td>
      <td>2020-02-22T05:18:27+00:00</td>
      <td>2.98</td>
      <td>POINT (77.58663 12.91208)</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>194</th>
      <td>0</td>
      <td>897.430</td>
      <td>2020-02-22T05:26:52+00:00</td>
      <td>9.01</td>
      <td>POINT (77.60109 12.90462)</td>
    </tr>
    <tr>
      <th>195</th>
      <td>0</td>
      <td>895.481</td>
      <td>2020-02-22T05:26:54+00:00</td>
      <td>7.88</td>
      <td>POINT (77.60123 12.90462)</td>
    </tr>
    <tr>
      <th>196</th>
      <td>0</td>
      <td>894.034</td>
      <td>2020-02-22T05:26:56+00:00</td>
      <td>5.53</td>
      <td>POINT (77.60135 12.90462)</td>
    </tr>
    <tr>
      <th>197</th>
      <td>0</td>
      <td>894.315</td>
      <td>2020-02-22T05:26:58+00:00</td>
      <td>5.02</td>
      <td>POINT (77.60145 12.90460)</td>
    </tr>
    <tr>
      <th>198</th>
      <td>0</td>
      <td>893.181</td>
      <td>2020-02-22T05:27:01+00:00</td>
      <td>3.49</td>
      <td>POINT (77.60156 12.90459)</td>
    </tr>
  </tbody>
</table>
<p>199 rows × 5 columns</p>
</div>



Let's use the timestamp contained in the 'time' column as the index. This will allow us to filter and plot the time-series data easily. We must first convert the time column to datetime type with an appropriate timezone.


```python
gdf['time'] = pd.to_datetime(gdf['time'])
gdf = gdf.set_index('time')
gdf.index = gdf.index.tz_convert('Asia/Kolkata')
gdf
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_fid</th>
      <th>ele</th>
      <th>speed</th>
      <th>geometry</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2020-02-22 10:48:17+05:30</th>
      <td>0</td>
      <td>916.334</td>
      <td>7.28</td>
      <td>POINT (77.58614 12.91214)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:19+05:30</th>
      <td>0</td>
      <td>917.815</td>
      <td>6.12</td>
      <td>POINT (77.58627 12.91213)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:21+05:30</th>
      <td>0</td>
      <td>919.915</td>
      <td>6.00</td>
      <td>POINT (77.58637 12.91212)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:23+05:30</th>
      <td>0</td>
      <td>918.828</td>
      <td>9.41</td>
      <td>POINT (77.58651 12.91210)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:27+05:30</th>
      <td>0</td>
      <td>919.799</td>
      <td>2.98</td>
      <td>POINT (77.58663 12.91208)</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2020-02-22 10:56:52+05:30</th>
      <td>0</td>
      <td>897.430</td>
      <td>9.01</td>
      <td>POINT (77.60109 12.90462)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:56:54+05:30</th>
      <td>0</td>
      <td>895.481</td>
      <td>7.88</td>
      <td>POINT (77.60123 12.90462)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:56:56+05:30</th>
      <td>0</td>
      <td>894.034</td>
      <td>5.53</td>
      <td>POINT (77.60135 12.90462)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:56:58+05:30</th>
      <td>0</td>
      <td>894.315</td>
      <td>5.02</td>
      <td>POINT (77.60145 12.90460)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:57:01+05:30</th>
      <td>0</td>
      <td>893.181</td>
      <td>3.49</td>
      <td>POINT (77.60156 12.90459)</td>
    </tr>
  </tbody>
</table>
<p>199 rows × 4 columns</p>
</div>



Using time as index allows us to filter the data as follows


```python
gdf_subset = gdf['2020-02-22T10:48:00':'2020-02-22T10:49:00']
gdf_subset
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>track_fid</th>
      <th>ele</th>
      <th>speed</th>
      <th>geometry</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2020-02-22 10:48:17+05:30</th>
      <td>0</td>
      <td>916.334</td>
      <td>7.28</td>
      <td>POINT (77.58614 12.91214)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:19+05:30</th>
      <td>0</td>
      <td>917.815</td>
      <td>6.12</td>
      <td>POINT (77.58627 12.91213)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:21+05:30</th>
      <td>0</td>
      <td>919.915</td>
      <td>6.00</td>
      <td>POINT (77.58637 12.91212)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:23+05:30</th>
      <td>0</td>
      <td>918.828</td>
      <td>9.41</td>
      <td>POINT (77.58651 12.91210)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:27+05:30</th>
      <td>0</td>
      <td>919.799</td>
      <td>2.98</td>
      <td>POINT (77.58663 12.91208)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:34+05:30</th>
      <td>0</td>
      <td>922.455</td>
      <td>0.69</td>
      <td>POINT (77.58672 12.91209)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:39+05:30</th>
      <td>0</td>
      <td>924.852</td>
      <td>2.20</td>
      <td>POINT (77.58682 12.91206)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:43+05:30</th>
      <td>0</td>
      <td>921.261</td>
      <td>4.51</td>
      <td>POINT (77.58693 12.91204)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:45+05:30</th>
      <td>0</td>
      <td>921.716</td>
      <td>5.79</td>
      <td>POINT (77.58705 12.91202)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:47+05:30</th>
      <td>0</td>
      <td>921.995</td>
      <td>6.77</td>
      <td>POINT (77.58718 12.91204)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:49+05:30</th>
      <td>0</td>
      <td>920.757</td>
      <td>7.18</td>
      <td>POINT (77.58732 12.91201)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:51+05:30</th>
      <td>0</td>
      <td>916.095</td>
      <td>7.53</td>
      <td>POINT (77.58745 12.91201)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:53+05:30</th>
      <td>0</td>
      <td>916.769</td>
      <td>5.09</td>
      <td>POINT (77.58755 12.91199)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:55+05:30</th>
      <td>0</td>
      <td>916.842</td>
      <td>4.51</td>
      <td>POINT (77.58766 12.91200)</td>
    </tr>
    <tr>
      <th>2020-02-22 10:48:58+05:30</th>
      <td>0</td>
      <td>917.014</td>
      <td>4.23</td>
      <td>POINT (77.58774 12.91195)</td>
    </tr>
  </tbody>
</table>
</div>



We can now plot the elevation against the timestamp using Matplotlib. Since we have a large number of timestamps, we can use `set_major_locator()` to define what labels will be present on the axis.

Since our timestamps are timezone aware, we can also plot a timezone name (i.e. IST) along with the label.


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)
gdf['ele'].plot(kind='line', ax=ax, color='black')
plt.tight_layout()
plt.title('Elevation Profile', fontsize = 18)
plt.ylabel('Elevation (meters)', size = 15)
plt.xlabel(None)
# Show a ticket every 5 minute
xlocator = mdates.MinuteLocator(interval=1)

xformat = mdates.DateFormatter('%H:%M %Z', tz=gdf.index.tz)  # adds some extra formatting, but not required

ax.xaxis.set_major_locator(xlocator)
ax.xaxis.set_major_formatter(xformat)

plt.show()
```


    
![](python-dataviz-output/supplement_elevation_profile_plot_files/supplement_elevation_profile_plot_8_0.png)
    

