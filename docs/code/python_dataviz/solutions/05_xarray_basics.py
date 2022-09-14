selected = da.sel(lat=28.6, lon=77.2, method='nearest')
max_anomaly = selected.where(selected==selected.max(), drop=True)

print(max_anomaly.time.values[0])
print(max_anomaly.time.dt.strftime('%Y-%m-%d').values[0])
