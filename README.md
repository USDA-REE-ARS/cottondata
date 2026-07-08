# cottondata
Repository of USDA-ARS precision cotton irrigation research data from Maricopa, Arizona, 2002-2023

# Description
The repository provides 17 experiment-years of USDA-ARS precision cotton irrigation research data from Maricopa, Arizona, collected during cotton field studies at the Maricopa Agricultural Center (MAC) from 2002 to 2023. The data are organized into several geospatial data layers, including Experiment, Plot, Zone, CropHarvest, SoilWaterContent, CropCanopy, PlantAnaysis, SoilChemicalAnalysis, SoilPhysicalAnalysis, and Weather. The "Data" directory provides original field data in shapefile and spreadsheet formats. The "src" directory provides Python scripts that read data from shapefiles and spreadsheets, organize the data using a data object model, and export the data to GeoJSON object files. The "geojson" directory provides the GeoJSON object files for each of the 17 experiment-years. The "docs" directory provides a data dictionary for 203 variable codes, prepared as a Latex document. Soil data for the four field sites and weather data from the Arizona Meteorological Network (AZMET) station at MAC are also provided.

# Key source codes

[rebuild.py](https://github.com/kthorp/cottondata/tree/main/src/rebuild.py) - Runs the entire workflow to build GeoJSON object files from the provided shapefile and spreadsheet data. This code should not need to be run unless changes to the data sources or workflow are made.

[stats2.py](https://github.com/kthorp/cottondata/tree/main/src/stats2.py) - Evaluates variable codes in the data dictionary and summarizes the number of values for each variable in each geospatial data layer.

[stats3.py](https://github.com/kthorp/cottondata/tree/main/src/stats3.py) - Evaluates the number of GeoJSON objects for each data type and experiment-year.

[mongodb.py](https://github.com/kthorp/cottondata/tree/main/src/mongodb.py) - Demonstrates loading the entire data set into a MongoDB NoSQL database.

[cottondata.py](https://github.com/kthorp/cottondata/tree/main/src/cottondata.py) - Demonstrates reading the entire data set from GeoJSON object files into a CottonData object in computer memory and computing linkages among GeoJSON objects. This module is likely most useful for users aiming to develop custom code for interaction with the data set.

# Further information

Further information about the data set is provided in the following publication:
Thorp, K. R., Hunsaker, D. J., French, A. N., Elshikha, D. E. M., Pinter, Jr., P. J., Barnes, E. M., 2026. Two decades of precision cotton irrigation research data at Maricopa, Arizona. Scientific Data. In review.
