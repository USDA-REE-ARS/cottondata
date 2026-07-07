from pymongo import MongoClient
import geojson
import sys
import os

client = MongoClient("mongodb://localhost:27017/")

try:
    client.admin.command('ping')
    print("Connected!")
except Exception as e:
    print(f"Connection failed: {e}")

db = client["MaricopaCotton"]

exps = ['2002_F105_CO_FISE',
        '2003_F105_CO_FISE',
        '2007_F111_CO_ISM',
        '2009_F033_CO_RSIS',
        '2011_F033_CO_RSIS',
        '2014_F013B4_CO_ISOS',
        '2015_F013B4_CO_ISOS',
        '2016_F013B4_CO_ITR',
        '2017_F013B4_CO_ITR',
        '2018_F013B4_CO_ITR',
        '2019_F013B4_CO_PIT',
        '2020_F013B4_CO_PIT',
        '2021_F013B4_CO_ISSWC',
        '2022_F013B4_CO_IRATE',
        '2022_F013B4_CO_ISSWC',
        '2023_F013B4_CO_IRATE',
        '2023_F013B4_CO_TILL']

collections = ['Experiment',
               'Plot',
               'CropHarvest',
               'SoilWaterContent',
               'CropCanopy',
               'PlantAnalysis',
               'Zone',
               'SoilChemicalAnalysis']

for collection in collections:
    mycollection = db[collection]
    count = 0
    for exp in exps:
        myfile = '../geojson/'+exp+'/'+exp+'_'+collection+'.geojson'
        if os.path.exists(myfile):
            print(myfile)
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            for feature in gj.features:
                target_id = feature['_id']
                query = {'_id':target_id}
                update = {"$set":feature}
                mycollection.update_one(query,update,upsert=True)
                count += 1
    print('Updated {:d} records in '.format(count) + collection + '.')

for sa in ['F013B4_SoilPhysicalAnalysis_DJH.geojson',
           'F013B4_SoilPhysicalAnalysis_KRT.geojson',
           'F033_SoilPhysicalAnalysis_DJH.geojson',
           'F105_SoilPhysicalAnalysis_DJH.geojson',
           'F111_SoilPhysicalAnalysis_DJH.geojson']:
    mycollection = db['SoilPhysicalAnalysis']
    myfile = '../geojson/Soil/'+sa
    if os.path.exists(myfile):
        print(myfile)
        f = open(myfile,'r')
        gj = geojson.load(f)
        f.close()
        for feature in gj.features:
            target_id = feature['_id']
            query = {'_id':target_id}
            update = {"$set":feature}
            mycollection.update_one(query,update,upsert=True)
            count += 1
print('Updated {:d} records in '.format(count) + 'SoilPhysicalAnalysis.')

mycollection = db['Weather']
myfile = '../geojson/Weather/AZMET_Maricopa_station.geojson'
count=0
if os.path.exists(myfile):
    print(myfile)
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    for feature in gj.features:
        target_id = feature['_id']
        query = {'_id':target_id}
        update = {"$set":feature}
        mycollection.update_one(query,update,upsert=True)
        count += 1
print('Updated {:d} records in '.format(count) + 'Weather.')

#Then run mongodb-compass from command line.
