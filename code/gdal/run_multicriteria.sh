gdal_rasterize -burn 1 -add -tr 100 100 -te 523843.7 177847.3 531169.1 183893.8 multicriteria.gpkg -l bicycle_thefts thefts.tif -ot Int16
gdal_rasterize -ot Int16 -burn 1 -tr 10 10 -te 523843.7 177847.3 531169.1 183893.8 multicriteria.gpkg -l cycling_routes routes.tif
gdal_rasterize -ot Int16 -burn 1 -tr 10 10 -te 523843.7 177847.3 531169.1 183893.8 multicriteria.gpkg -l cycle_parking existing_parking.tif
gdal_proximity.py routes.tif routes_proximity.tif -ot Int16 -distunits GEO
gdal_proximity.py existing_parking.tif existing_parking_proximity.tif -ot Int16 -distunits GEO
gdal_calc.py -A thefts.tif --outfile thefts_reclass.tif --calc="100*(A>20) + 50*(A>10)*(A<=20) + 10*(A<10)"
gdal_calc.py -A routes_proximity.tif --outfile routes_reclass.tif --calc="100*(A<=50) + 50*(A>50)*(A<=100) + 10*(A>100)"
gdal_calc.py -A existing_parking_proximity.tif --outfile existing_parking_reclass.tif --calc="100*(A>100) + 50*(A>50)*(A<=100) + 10*(A<50)"
gdalwarp -r average -tr 100 100 existing_parking_reclass.tif parking_reclass_resampled.tif
gdalwarp -r average -tr 100 100 routes_reclass.tif routes_reclass_resampled.tif
gdal_calc.py -A thefts_reclass.tif -B routes_reclass_resampled.tif -C parking_reclass_resampled.tif --outfile suitability.tif --calc="(A + B + C)/3" --NoDataValue=0
