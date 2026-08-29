### Exercise

[Scipy for Xarray (`xrscipy`)](https://xr-scipy.readthedocs.io/en/stable/index.html) package wraps the popular scipy package for Xarray and provides many useful time-series processing functions. The code snippet below uses [`xrscipy.signal.savgol_filter`](https://xr-scipy.readthedocs.io/en/1.0.0/generated/xrscipy.other.signal.savgol_filter.html) function to apply a Savitzky-Golay filter on our gap-filled NDVI time-series.

Try SG-Filter with different values of window_length and polyorder and plot the results on a chart.


```python
# Use the equally spaced interpolated time-series
time_series_interpolated = time_series_interpolated.compute()

# savgol_filter() requires integers as time index
# We save the original time index values and
# overwrite it with sequential integers
timestamps = time_series_interpolated.time
time_series_interpolated.coords['time'] = np.arange(len(timestamps))

# Apply the SG filter
window_length = 5 # Size of filter window
polyorder = 2 # Order of the polynomial used in the filtering

time_series_sg = xrs.savgol_filter(
    time_series_interpolated,
    window_length = window_length,
    polyorder = polyorder,
    mode='nearest',
    dim = 'time'
)

# Write back the original timestamps
time_series_sg.coords['time'] = timestamps
time_series_interpolated.coords['time'] = timestamps
```


```python
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(15, 7)
time_series_interpolated.plot.line(
    ax=ax, x='time',
    marker='^', color='#66c2a4',
    linestyle='--', linewidth=1, markersize=2)
time_series_sg.plot.line(
    ax=ax, x='time',
    marker='o', color='#238b45',
    linestyle='-', linewidth=1, markersize=4)

# Format the x-axis to display dates as YYYY-MM
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

ax.set_title('Original vs. SG-Filtered NDVI Time-Series')

plt.show()
```


    
![](python-remote-sensing-output/solutions/module_02/03_extracting_time_series_files/03_extracting_time_series_2_0.png)
    

