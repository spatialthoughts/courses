# Working with pandas



```python
import os
import pandas as pd
```


```python
home_dir = os.path.expanduser('~')
print(home_dir)
```

    /Users/ujaval



```python
filename = 'worldcities.csv'
folder = 'Downloads/python_geospatial/'
path = os.path.join(home_dir, folder, filename)
print(path)
```


```python
df = pd.read_csv(path)
df.head()
```


```python
df.shape
```


```python
india_df = df[df['country']=='India'].copy()
india_df.shape
```


```python

```


```python
%run ./distance.ipynb
```


```python
india_df['distance'] = india_df.apply(lambda row: haversine_distance((77.56, 12.97), (row['lng'], row['lat'])), axis=1)
india_df['distance'] = india_df['distance'].apply(lambda x: '%.2f' % x)
display(india_df)
```


```python
output = os.path.join(home_dir, 'Downloads', 'output.csv')
print(output)
india_df.to_csv(output, index=False)
```


```python
# pip install geopy
from geopy import distance
```


```python
india_df['great_circle'] = india_df.apply(lambda row: distance.great_circle((12.97,77.56), (row['lat'], row['lng'])).km, axis=1)
display(india_df)
```


```python

```
