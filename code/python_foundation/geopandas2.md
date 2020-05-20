conda create --name python_foundation
conda activate python_foundation
conda install geopandas


```python
import os
import pandas as pd
import geopandas as gpd
```


```python
home_dir = os.path.expanduser('~')
places_file = 'ne_10m_populated_places_simple.shp'
states_file = 'ne_10m_admin_1_states_provinces.shp'
folder = 'Downloads/python_geospatial/'
places_path = os.path.join(home_dir, folder, places_file)
states_path = os.path.join(home_dir, folder, states_file)


```


```python
home_state = 'Karnataka'
places = gpd.read_file(places_path)
states = gpd.read_file(states_path)
filtered = states[states['name'] == home_state]
filtered
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
      <th>featurecla</th>
      <th>scalerank</th>
      <th>adm1_code</th>
      <th>diss_me</th>
      <th>iso_3166_2</th>
      <th>wikipedia</th>
      <th>iso_a2</th>
      <th>adm0_sr</th>
      <th>name</th>
      <th>name_alt</th>
      <th>...</th>
      <th>name_nl</th>
      <th>name_pl</th>
      <th>name_pt</th>
      <th>name_ru</th>
      <th>name_sv</th>
      <th>name_tr</th>
      <th>name_vi</th>
      <th>name_zh</th>
      <th>ne_id</th>
      <th>geometry</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2237</th>
      <td>Admin-1 scale rank</td>
      <td>2</td>
      <td>IND-2446</td>
      <td>2446</td>
      <td>IN-KA</td>
      <td>None</td>
      <td>IN</td>
      <td>1</td>
      <td>Karnataka</td>
      <td>Maisur|Mysore</td>
      <td>...</td>
      <td>Karnataka</td>
      <td>Karnataka</td>
      <td>Karnataka</td>
      <td>Карнатака</td>
      <td>Karnataka</td>
      <td>Karnataka</td>
      <td>Karnataka</td>
      <td>卡纳塔克邦</td>
      <td>1159311889</td>
      <td>POLYGON ((74.85426 12.76529, 74.85475 12.78701...</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 84 columns</p>
</div>




```python
filtered = gpd.clip(places, filtered)
```


```python
filtered.to_crs('EPSG:3857', inplace=True)
home_city = 'Bangalore'
home_city_geom = filtered[filtered['name'] == home_city].geometry
home_city_geom
filtered['distance'] = filtered.apply(lambda row: home_city_geom.distance(row.geometry)/1e3, axis=1)
filtered
# reproj
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
      <th>scalerank</th>
      <th>natscale</th>
      <th>labelrank</th>
      <th>featurecla</th>
      <th>name</th>
      <th>namepar</th>
      <th>namealt</th>
      <th>diffascii</th>
      <th>nameascii</th>
      <th>adm0cap</th>
      <th>...</th>
      <th>rank_min</th>
      <th>geonameid</th>
      <th>meganame</th>
      <th>ls_name</th>
      <th>ls_match</th>
      <th>checkme</th>
      <th>min_zoom</th>
      <th>ne_id</th>
      <th>geometry</th>
      <th>distance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3893</th>
      <td>7</td>
      <td>20</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Mandya</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Mandya</td>
      <td>0.0</td>
      <td>...</td>
      <td>9</td>
      <td>1263814.0</td>
      <td>None</td>
      <td>Mandya</td>
      <td>1</td>
      <td>0</td>
      <td>6.7</td>
      <td>1159141819</td>
      <td>POINT (708594.997 1390387.448)</td>
      <td>82.329836</td>
    </tr>
    <tr>
      <th>3894</th>
      <td>7</td>
      <td>20</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Kolar</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Kolar</td>
      <td>0.0</td>
      <td>...</td>
      <td>9</td>
      <td>1266305.0</td>
      <td>None</td>
      <td>Kolar</td>
      <td>1</td>
      <td>0</td>
      <td>6.7</td>
      <td>1159141823</td>
      <td>POINT (839755.895 1454034.354)</td>
      <td>64.964058</td>
    </tr>
    <tr>
      <th>3895</th>
      <td>7</td>
      <td>20</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Shimoga</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Shimoga</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1256515.0</td>
      <td>None</td>
      <td>Shimoga</td>
      <td>1</td>
      <td>0</td>
      <td>6.7</td>
      <td>1159141827</td>
      <td>POINT (560496.928 1540097.416)</td>
      <td>240.942206</td>
    </tr>
    <tr>
      <th>3896</th>
      <td>7</td>
      <td>20</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Raichur</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Raichur</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1259012.0</td>
      <td>None</td>
      <td>Raichur</td>
      <td>1</td>
      <td>0</td>
      <td>6.7</td>
      <td>1159141831</td>
      <td>POINT (751761.078 1793650.092)</td>
      <td>359.150536</td>
    </tr>
    <tr>
      <th>3897</th>
      <td>7</td>
      <td>20</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Hospet</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Hospet</td>
      <td>0.0</td>
      <td>...</td>
      <td>9</td>
      <td>1269935.0</td>
      <td>None</td>
      <td>Hospet</td>
      <td>1</td>
      <td>0</td>
      <td>6.7</td>
      <td>1159141837</td>
      <td>POINT (647642.540 1689806.461)</td>
      <td>285.617094</td>
    </tr>
    <tr>
      <th>3898</th>
      <td>7</td>
      <td>20</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Bidar</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Bidar</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1275738.0</td>
      <td>None</td>
      <td>Bidar</td>
      <td>1</td>
      <td>0</td>
      <td>6.7</td>
      <td>1159141841</td>
      <td>POINT (766698.089 1983461.990)</td>
      <td>548.144629</td>
    </tr>
    <tr>
      <th>5352</th>
      <td>6</td>
      <td>30</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Bijapur</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Bijapur</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1275701.0</td>
      <td>None</td>
      <td>Bijapur</td>
      <td>1</td>
      <td>0</td>
      <td>6.0</td>
      <td>1159147195</td>
      <td>POINT (575641.275 1861484.053)</td>
      <td>471.465697</td>
    </tr>
    <tr>
      <th>5942</th>
      <td>6</td>
      <td>30</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Tumkur</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Tumkur</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1254089.0</td>
      <td>None</td>
      <td>Tumkur</td>
      <td>1</td>
      <td>0</td>
      <td>6.0</td>
      <td>1159148523</td>
      <td>POINT (727472.167 1474588.129)</td>
      <td>63.545735</td>
    </tr>
    <tr>
      <th>5943</th>
      <td>6</td>
      <td>30</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Davangere</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Davangere</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1273368.0</td>
      <td>None</td>
      <td>Davangere</td>
      <td>1</td>
      <td>0</td>
      <td>6.0</td>
      <td>1159148525</td>
      <td>POINT (599150.723 1599906.678)</td>
      <td>242.627637</td>
    </tr>
    <tr>
      <th>5944</th>
      <td>6</td>
      <td>30</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Bellary</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Bellary</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1276509.0</td>
      <td>None</td>
      <td>Bellary</td>
      <td>1</td>
      <td>0</td>
      <td>6.0</td>
      <td>1159148527</td>
      <td>POINT (705769.731 1675820.482)</td>
      <td>250.873955</td>
    </tr>
    <tr>
      <th>5945</th>
      <td>6</td>
      <td>30</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Belgaum</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Belgaum</td>
      <td>0.0</td>
      <td>...</td>
      <td>11</td>
      <td>1276533.0</td>
      <td>None</td>
      <td>Belgaum</td>
      <td>1</td>
      <td>0</td>
      <td>6.0</td>
      <td>1159148531</td>
      <td>POINT (447003.454 1754066.458)</td>
      <td>459.097519</td>
    </tr>
    <tr>
      <th>6616</th>
      <td>4</td>
      <td>50</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Hubli</td>
      <td>None</td>
      <td>Hubli-Dharwad</td>
      <td>0</td>
      <td>Hubli</td>
      <td>0.0</td>
      <td>...</td>
      <td>11</td>
      <td>1269920.0</td>
      <td>Hubli-Dharwad</td>
      <td>Hubli</td>
      <td>1</td>
      <td>0</td>
      <td>5.6</td>
      <td>1159150013</td>
      <td>POINT (513208.476 1698360.826)</td>
      <td>372.818211</td>
    </tr>
    <tr>
      <th>6617</th>
      <td>4</td>
      <td>50</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Mangalore</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Mangalore</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1263780.0</td>
      <td>None</td>
      <td>Mangalore</td>
      <td>1</td>
      <td>0</td>
      <td>5.6</td>
      <td>1159150015</td>
      <td>POINT (483726.670 1426084.689)</td>
      <td>293.936275</td>
    </tr>
    <tr>
      <th>6618</th>
      <td>4</td>
      <td>50</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Mysore</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Mysore</td>
      <td>0.0</td>
      <td>...</td>
      <td>11</td>
      <td>1262321.0</td>
      <td>Mysore</td>
      <td>Mysore</td>
      <td>1</td>
      <td>0</td>
      <td>5.6</td>
      <td>1159150017</td>
      <td>POINT (680308.521 1361603.018)</td>
      <td>122.059657</td>
    </tr>
    <tr>
      <th>6619</th>
      <td>4</td>
      <td>50</td>
      <td>1</td>
      <td>Populated place</td>
      <td>Gulbarga</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>Gulbarga</td>
      <td>0.0</td>
      <td>...</td>
      <td>10</td>
      <td>1270752.0</td>
      <td>None</td>
      <td>Gulbarga</td>
      <td>1</td>
      <td>0</td>
      <td>5.6</td>
      <td>1159150019</td>
      <td>POINT (693390.810 1919186.238)</td>
      <td>491.022011</td>
    </tr>
    <tr>
      <th>7303</th>
      <td>1</td>
      <td>300</td>
      <td>1</td>
      <td>Admin-1 capital</td>
      <td>Bangalore</td>
      <td>None</td>
      <td>Bengaluru</td>
      <td>0</td>
      <td>Bangalore</td>
      <td>0.0</td>
      <td>...</td>
      <td>13</td>
      <td>1277333.0</td>
      <td>Bangalore</td>
      <td>Bangalore</td>
      <td>1</td>
      <td>0</td>
      <td>3.7</td>
      <td>1159151543</td>
      <td>POINT (777514.534 1435424.092)</td>
      <td>0.000000</td>
    </tr>
  </tbody>
</table>
<p>16 rows × 40 columns</p>
</div>




```python

```


```python

```
