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
gpx_path = os.path.join(data_pkg_path, 'gps', 'summit.gpx')
# GPX files contain many layers. Read the 'track_points' layer
gdf = gpd.read_file(gpx_path, layer='track_points')
gdf = gdf[['track_fid','ele', 'time', 'geometry']]
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
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>3187.3</td>
      <td>2022-04-04 00:07:42+00:00</td>
      <td>POINT (78.56758 30.82669)</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>3194.4</td>
      <td>2022-04-04 00:07:54+00:00</td>
      <td>POINT (78.56747 30.82667)</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>3196.6</td>
      <td>2022-04-04 00:07:59+00:00</td>
      <td>POINT (78.56743 30.82670)</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>3196.8</td>
      <td>2022-04-04 00:08:04+00:00</td>
      <td>POINT (78.56741 30.82671)</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>3198.2</td>
      <td>2022-04-04 00:08:14+00:00</td>
      <td>POINT (78.56739 30.82668)</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2305</th>
      <td>0</td>
      <td>3150.8</td>
      <td>2022-04-04 06:05:58+00:00</td>
      <td>POINT (78.56878 30.82703)</td>
    </tr>
    <tr>
      <th>2306</th>
      <td>0</td>
      <td>3150.5</td>
      <td>2022-04-04 06:06:01+00:00</td>
      <td>POINT (78.56879 30.82704)</td>
    </tr>
    <tr>
      <th>2307</th>
      <td>0</td>
      <td>3150.3</td>
      <td>2022-04-04 06:06:06+00:00</td>
      <td>POINT (78.56883 30.82707)</td>
    </tr>
    <tr>
      <th>2308</th>
      <td>0</td>
      <td>3150.3</td>
      <td>2022-04-04 06:06:11+00:00</td>
      <td>POINT (78.56878 30.82710)</td>
    </tr>
    <tr>
      <th>2309</th>
      <td>0</td>
      <td>3150.5</td>
      <td>2022-04-04 06:06:16+00:00</td>
      <td>POINT (78.56877 30.82709)</td>
    </tr>
  </tbody>
</table>
<p>2310 rows × 4 columns</p>
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
      <th>geometry</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2022-04-04 05:37:42+05:30</th>
      <td>0</td>
      <td>3187.3</td>
      <td>POINT (78.56758 30.82669)</td>
    </tr>
    <tr>
      <th>2022-04-04 05:37:54+05:30</th>
      <td>0</td>
      <td>3194.4</td>
      <td>POINT (78.56747 30.82667)</td>
    </tr>
    <tr>
      <th>2022-04-04 05:37:59+05:30</th>
      <td>0</td>
      <td>3196.6</td>
      <td>POINT (78.56743 30.82670)</td>
    </tr>
    <tr>
      <th>2022-04-04 05:38:04+05:30</th>
      <td>0</td>
      <td>3196.8</td>
      <td>POINT (78.56741 30.82671)</td>
    </tr>
    <tr>
      <th>2022-04-04 05:38:14+05:30</th>
      <td>0</td>
      <td>3198.2</td>
      <td>POINT (78.56739 30.82668)</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2022-04-04 11:35:58+05:30</th>
      <td>0</td>
      <td>3150.8</td>
      <td>POINT (78.56878 30.82703)</td>
    </tr>
    <tr>
      <th>2022-04-04 11:36:01+05:30</th>
      <td>0</td>
      <td>3150.5</td>
      <td>POINT (78.56879 30.82704)</td>
    </tr>
    <tr>
      <th>2022-04-04 11:36:06+05:30</th>
      <td>0</td>
      <td>3150.3</td>
      <td>POINT (78.56883 30.82707)</td>
    </tr>
    <tr>
      <th>2022-04-04 11:36:11+05:30</th>
      <td>0</td>
      <td>3150.3</td>
      <td>POINT (78.56878 30.82710)</td>
    </tr>
    <tr>
      <th>2022-04-04 11:36:16+05:30</th>
      <td>0</td>
      <td>3150.5</td>
      <td>POINT (78.56877 30.82709)</td>
    </tr>
  </tbody>
</table>
<p>2310 rows × 3 columns</p>
</div>



Using time as index allows us to filter the data as follows


```python
gdf_subset = gdf['2022-04-04T09:00:00':'2022-04-04T09:30:00']
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
      <th>geometry</th>
    </tr>
    <tr>
      <th>time</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2022-04-04 09:08:44+05:30</th>
      <td>0</td>
      <td>3626.1</td>
      <td>POINT (78.54941 30.83630)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:10:01+05:30</th>
      <td>0</td>
      <td>3625.7</td>
      <td>POINT (78.54940 30.83636)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:10:06+05:30</th>
      <td>0</td>
      <td>3625.7</td>
      <td>POINT (78.54940 30.83636)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:11:25+05:30</th>
      <td>0</td>
      <td>3626.4</td>
      <td>POINT (78.54939 30.83628)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:11:30+05:30</th>
      <td>0</td>
      <td>3626.4</td>
      <td>POINT (78.54940 30.83629)</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2022-04-04 09:29:38+05:30</th>
      <td>0</td>
      <td>3539.5</td>
      <td>POINT (78.55257 30.83533)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:29:41+05:30</th>
      <td>0</td>
      <td>3539.9</td>
      <td>POINT (78.55259 30.83532)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:29:46+05:30</th>
      <td>0</td>
      <td>3539.1</td>
      <td>POINT (78.55261 30.83530)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:29:51+05:30</th>
      <td>0</td>
      <td>3539.0</td>
      <td>POINT (78.55265 30.83529)</td>
    </tr>
    <tr>
      <th>2022-04-04 09:29:56+05:30</th>
      <td>0</td>
      <td>3538.4</td>
      <td>POINT (78.55269 30.83528)</td>
    </tr>
  </tbody>
</table>
<p>166 rows × 3 columns</p>
</div>



We can now plot the elevation against the timestamp using Matplotlib. Since we have a large number of timestamps, we can use `set_major_locator()` to define what labels will be present on the axis.

Since our timestamps are timezone aware, we can also plot a timezone name (i.e. IST) along with the label.

We can also use a different style for our plot. You can run `plt.style.available` to see all available styles.


```python
plt.style.use('ggplot')
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15,7)
gdf['ele'].plot(kind='line', ax=ax, color='#2b8cbe')
plt.tight_layout()
plt.title('Elevation Profile', fontsize = 18)
plt.ylabel('Elevation (meters)', size = 15)
plt.xlabel(None)
# Show a tick every 30 minute
xlocator = mdates.MinuteLocator(interval=30)

xformat = mdates.DateFormatter('%H:%M %Z', tz=gdf.index.tz)  # adds some extra formatting, but not required

ax.xaxis.set_major_locator(xlocator)
ax.xaxis.set_major_formatter(xformat)
ax.set_ylim([3200, 3700])
ax.fill_between(gdf.index, gdf['ele'].values, color='grey', alpha=0.3)
plt.show()
```


    
![](python-dataviz-output/supplement_elevation_profile_plot_files/supplement_elevation_profile_plot_10_0.png)
    



```python
plt.style.use('default')
```
