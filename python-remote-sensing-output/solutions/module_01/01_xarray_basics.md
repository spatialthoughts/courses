### Exercise

Display the median composite for the month of May.

The snippet below takes our time-series and aggregate it to a monthly median composites `groupby()` method.

After aggregation, you will have a new dimension named `month`. Extract the DataArray for the chosen month using `sel()` method.


```python
monthly = ds.groupby('time.month').median(dim='time')
monthly
```


```python
selected = monthly.sel(month=5).to_array('band')
fig, ax = plt.subplots(1, 1)
fig.set_size_inches(5,5)
selected.sel(band=['red', 'green', 'blue']).plot.imshow(
    ax=ax,
    robust=True)
ax.set_title('RGB Visualization')
ax.set_axis_off()
plt.show()
```


```python
monthly_da = monthly.to_array('band')

fig, axes = plt.subplots(4, 3)
fig.set_size_inches(9, 12)

for index, ax in enumerate(axes.flat):
    month_da = monthly_da.isel(month=index)
    month_da.sel(band=['red', 'green', 'blue']).plot.imshow(
      ax=ax,
      vmin=0,
      vmax=3000)
    ax.set_title(f'{month_da.month.values}')
    ax.set_axis_off()

plt.tight_layout()
plt.show()
```
