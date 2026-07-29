import os
import time
import geopandas as gpd
import pystac_client
import rioxarray as rxr
from dask.distributed import Client, progress
from odc.stac import configure_s3_access, load

data_folder = 'data'
output_folder = 'output'


def create_median_composite(data_folder, output_folder):
    aoi_filepath = os.path.join(data_folder, 'aoi.geojson')

    if not os.path.exists(aoi_filepath):
        print(f'AOI file not found at {aoi_filepath}. Using default AOI.')
        aoi_filepath = ('https://storage.googleapis.com/spatialthoughts-public-data'
                        '/python-remote-sensing/aoi.geojson')

    aoi_gdf = gpd.read_file(aoi_filepath)
    geometry = aoi_gdf.geometry.union_all()

    catalog = pystac_client.Client.open(
        'https://earth-search.aws.element84.com/v1')

    configure_s3_access(
        aws_unsigned=True,
    )

    year = 2024
    time_range = f'{year}'

    filters = {
        'eo:cloud_cover': {'lt': 30},
    }

    search = catalog.search(
        collections=['sentinel-2-c1-l2a'],
        intersects=geometry,
        datetime=time_range,
        query=filters,
    )
    items = search.item_collection()
    print(f'Found {len(items)} items')

    ds = load(
        items,
        bands=['red', 'green', 'blue', 'nir', 'scl'],
        resolution=10,
        crs='utm',
        bbox=geometry.bounds,
        chunks={'x': 1024, 'y': 1024},
        groupby='solar_day',
    )

    # Mask nodata values
    ds = ds.where(ds != 0)

    # Apply scale/offset to spectral bands only (exclude scl)
    scale = 0.0001
    offset = -0.1
    data_bands = [band for band in ds.data_vars if band != 'scl']
    for band in data_bands:
        ds[band] = ds[band] * scale + offset

    # Mask clouds using the SCL band (3: cloud shadow, 8/9: cloud, 10: cirrus)
    cloud_mask = ds.scl.isin([3, 8, 9, 10])
    ds = ds[data_bands].where(~cloud_mask)

    median_composite = ds.median(dim='time')
    rgb_composite = median_composite[['red', 'green', 'blue']]

    print('Computing median composite...')
    
    # We use the Dask distributed progress bar to monitor the computation
    # This requires us to start the computation using .persist()
    rgb_composite = rgb_composite.persist()
    # Watch progress of the computation
    progress(rgb_composite)
    # Load the result into memory once the computation is complete
    rgb_composite = rgb_composite.compute()

    rgb_composite_da = rgb_composite.to_array('band')
    image_crs = rgb_composite_da.rio.crs
    aoi_gdf_reprojected = aoi_gdf.to_crs(image_crs)
    rgb_composite_clipped = rgb_composite_da.rio.clip(aoi_gdf_reprojected.geometry)

    output_file = f'cloudfree_composite_{time_range}.tif'
    output_path = os.path.join(output_folder, output_file)
    rgb_composite_clipped.rio.to_raster(output_path, driver='COG')
    print(f'Wrote {output_path}')


def main():
    if not os.path.exists(data_folder):
        os.mkdir(data_folder)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    client = Client()
    print(client.dashboard_link)
    try:
        create_median_composite(data_folder, output_folder)
    finally:
        print('Shutting down the Dask client...')
        client.retire_workers()
        # Wait for a moment to ensure workers are retired
        # This prevents unneccessary scheduler warnings
        time.sleep(1)
        client.shutdown()    

if __name__ == '__main__':
    main()
