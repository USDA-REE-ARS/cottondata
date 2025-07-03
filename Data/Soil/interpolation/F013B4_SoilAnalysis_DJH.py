import pandas as pd
from osgeo import ogr

shapefile = '../F013B4_SoilAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
spdata = []
for feature in layer:
    core = feature.GetField('Core')
    utmx = feature.GetField('UTMX')
    utmy = feature.GetField('UTMY')
    spdata.append([core,utmx,utmy])
spatialdata = pd.DataFrame(spdata, columns=['Core','UTMX','UTMY'])

datafile = '../F013B4_SoilAnalysis_DJH.xlsx'
soildf = pd.read_excel(datafile,sheet_name='SoilDF')

newdf = pd.merge(soildf,spatialdata,on="Core",how='left')

newdf.to_csv('F013B4_SoilAnalysis_DJH.csv',index=False)
