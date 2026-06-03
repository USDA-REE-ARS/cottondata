# cottondata
Repository of USDA-ARS precision cotton irrigation data from Maricopa, Arizona, 2002-2023

The repository provides 17 experiment-years of USDA-ARS precision cotton irrigation data from Maricopa, Arizona, collected from 2002 to 2023. The "Data" directory provides data in shapefile and spreadsheet format.  The "src" directory provides Python scripts that read data from shapefiles and spreadsheets. The data is organized within a data object model in computer memory prior to being exported as GeoJSON object files. The "geojson" directory provides the GeoJSON object files for each of the 17 experiment-years. Soil data for the four field sites and weather data from the Arizona Meteorological Network (AZMET) station are also provided.

rebuild.py - Runs the entire workflow to build GeoJSON object files from the provided shapefile and spreadsheet data.

cottondata.py - Reads the entire data set from GeoJSON object files into the CottonData object in computer memory and computes linkages among GeoJSON objects.

Further information is provided in the following publication:
Thorp, K. R., Hunsaker, D. J., French, A. N., Elshikha, D. E. M., Pinter, Jr., P. J., Barnes, E. M., 2026. Two decades of precision cotton irrigation research data at Maricopa, Arizona. Scientific Data. In preparation.
