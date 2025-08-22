import os
import sys
import math
import soilanalysis
import pandas as pd
from osgeo import ogr
import geojson

########################################################################
#F013B4_SoilAnalysis_DJH
shapefile = '../Data/Soil/F013B4_SoilAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/Soil/F013B4_SoilAnalysis_DJH.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDF')
sas = list()
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2014-p01-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mysa = soilanalysis.SoilAnalysis(said=said,geometry=geometry,sa_label=sa_label)
    #Soil analysis data
    rows = sa[sa['Core'] == sa_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%m/%Y'))
    items={'SLSND':2,'SLSLT':2,'SLCLY':2,'SLTX':-99,'SLWP1':3,'SLWP2':3,'SLFC1':3}
    for item in items.keys():
        sadata = dict()
        for depth in [15,45,75,105,135,165]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if items[item] < 0.:
                value = row.iloc[0][item]
                sadata.update({depth:value})
            elif not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                sadata.update({depth:value})
        if sadata:
            mysa.setproperty(item,sadata)
    sas.append(mysa)
features = list()
for mysa in sas:
    features.append(mysa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/Soil/F013B4_SoilAnalysis_DJH.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################

########################################################################
#F013B4_SoilAnalysis_KRT
shapefile = '../Data/Soil/F013B4_SoilAnalysis_KRT.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/Soil/F013B4_SoilAnalysis_KRT.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDF')
sas = list()
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2016-p01-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mysa = soilanalysis.SoilAnalysis(said=said,geometry=geometry,sa_label=sa_label)
    #Soil analysis data
    rows = sa[sa['Core'] == sa_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%m/%Y'))
    items={'SLSND':1,'SLSLT':1,'SLCLY':1,'SLSND2':1,'SLSLT2':1,'SLCLY2':1}
    for item in items.keys():
        sadata = dict()
        for depth in [20,60,100,140,180]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if row.empty: continue
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                sadata.update({depth:value})
        if sadata:
            mysa.setproperty(item,sadata)
    sas.append(mysa)
features = list()
for mysa in sas:
    features.append(mysa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/Soil/F013B4_SoilAnalysis_KRT.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################

########################################################################
#F033_SoilAnalysis_DJH
shapefile = '../Data/Soil/F033_SoilAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/Soil/F033_SoilAnalysis_DJH.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDF')
sas = list()
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2019-p01-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mysa = soilanalysis.SoilAnalysis(said=said,geometry=geometry,sa_label=sa_label)
    #Soil analysis data
    rows = sa[sa['Core'] == sa_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%m/%Y'))
    items={'SLSND':2,'SLSLT':2,'SLCLY':2,'SLTX':-99,'SLWP1':3,'SLWP2':3,'SLFC1':3}
    for item in items.keys():
        sadata = dict()
        for depth in [15,45,75,105,135,150,165,210]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if not row.empty:
                if items[item] < 0.:
                    value = row.iloc[0][item]
                    sadata.update({depth:value})
                elif not math.isnan(row.iloc[0][item]):
                    value = round(row.iloc[0][item],items[item])
                    if items[item] == 0: value=int(value)
                    sadata.update({depth:value})
        if sadata:
            mysa.setproperty(item,sadata)
    sas.append(mysa)
features = list()
for mysa in sas:
    features.append(mysa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/Soil/F033_SoilAnalysis_DJH.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
