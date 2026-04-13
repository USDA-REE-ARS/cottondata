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
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%Y-%m'))
    items={'SLSND_M':2,'SLSLT_M':2,'SLCLY_M':2,'SLTX':-99,'SLWP':3,'SLWP2':3,'SLFC1':3}
    for item in items.keys():
        sadata = list()
        for depth in [15,45,75,105,135,165]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if items[item] < 0.:
                value = row.iloc[0][item]
                sadata.append({'depth':int(depth),
                               'mindepth':int(depth)-15,
                               'maxdepth':int(depth)+15,
                               'value':value})
            elif not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                sadata.append({'depth':int(depth),
                               'mindepth':int(depth)-15,
                               'maxdepth':int(depth)+15,
                               'value':value})
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
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%Y-%m'))
    items={'SLSND_GBM':1,'SLSLT_GBM':1,'SLCLY_GBM':1,'SLSND_GB':1,'SLSLT_GB':1,'SLCLY_GB':1}
    for item in items.keys():
        sadata = list()
        for depth in [20,60,100,140,180]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if row.empty: continue
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                sadata.append({'depth':int(depth),
                               'mindepth':int(depth)-20,
                               'maxdepth':int(depth)+20,
                               'value':value})
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
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%Y-%m'))
    items={'SLSND_M':2,'SLSLT_M':2,'SLCLY_M':2,'SLTX':-99,'SLWP':3,'SLWP2':3,'SLFC1':3}
    for item in items.keys():
        sadata = list()
        for depth in [15,45,75,105,135,150,165,210]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if not row.empty:
                if items[item] < 0.:
                    value = row.iloc[0][item]
                    sadata.append({'depth':int(depth),
                                   'mindepth':int(depth)-15,
                                   'maxdepth':int(depth)+15,
                                   'value':value})
                elif not math.isnan(row.iloc[0][item]):
                    value = round(row.iloc[0][item],items[item])
                    if items[item] == 0: value=int(value)
                    sadata.append({'depth':int(depth),
                                   'mindepth':int(depth)-15,
                                   'maxdepth':int(depth)+15,
                                   'value':value})
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

########################################################################
#F111_SoilAnalysis_DJH
shapefile = '../Data/Soil/F111_SoilAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/Soil/F111_SoilAnalysis_DJH.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDF')
sas = list()
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 20062007camelinap11)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mysa = soilanalysis.SoilAnalysis(said=said,geometry=geometry,sa_label=sa_label)
    #Soil analysis data
    rows = sa[sa['Core'] == sa_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%Y-%m'))
    items={'SLSND_M':2,'SLSLT_M':2,'SLCLY_M':2,'SLTX':-99,'SLWP':3,'SLWP2':3,'SLFC1':3}
    for item in items.keys():
        sadata = list()
        for depth in [15,45,75,105,135,165,195,225,255,285]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if not row.empty:
                if items[item] < 0.:
                    value = row.iloc[0][item]
                    sadata.append({'depth':int(depth),
                                   'mindepth':int(depth)-15,
                                   'maxdepth':int(depth)+15,
                                   'value':value})
                elif not math.isnan(row.iloc[0][item]):
                    value = round(row.iloc[0][item],items[item])
                    if items[item] == 0: value=int(value)
                    sadata.append({'depth':int(depth),
                                   'mindepth':int(depth)-15,
                                   'maxdepth':int(depth)+15,
                                   'value':value})
        if sadata:
            mysa.setproperty(item,sadata)
    sas.append(mysa)
features = list()
for mysa in sas:
    features.append(mysa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/Soil/F111_SoilAnalysis_DJH.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################

########################################################################
#F105_SoilAnalysis_DJH
shapefile = '../Data/Soil/F105_SoilAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/Soil/F105_SoilAnalysis_DJH.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDF')
sas = list()
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., p101)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mysa = soilanalysis.SoilAnalysis(said=said,geometry=geometry,sa_label=sa_label)
    #Soil analysis data
    rows = sa[sa['Core'] == sa_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%Y'))
    items={'SLSND_M':2,'SLSLT_M':2,'SLCLY_M':2,'SLTX':-99,'SLWP':3,'SLWP2':3,'SLFC1':3}
    for item in items.keys():
        sadata = list()
        for depth in [15,45,75,105,135,165]:
            row = sa[(sa['Core'] == sa_label) & (sa['Depth'] == depth)]
            if not row.empty:
                if items[item] < 0.:
                    value = row.iloc[0][item]
                    sadata.append({'depth':int(depth),
                                   'mindepth':int(depth)-15,
                                   'maxdepth':int(depth)+15,
                                   'value':value})
                elif not math.isnan(row.iloc[0][item]):
                    value = round(row.iloc[0][item],items[item])
                    if items[item] == 0: value=int(value)
                    sadata.append({'depth':int(depth),
                                   'mindepth':int(depth)-15,
                                   'maxdepth':int(depth)+15,
                                   'value':value})
        if sadata:
            mysa.setproperty(item,sadata)
    sas.append(mysa)
features = list()
for mysa in sas:
    features.append(mysa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/Soil/F105_SoilAnalysis_DJH.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
