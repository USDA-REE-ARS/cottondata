import glob
import geojson
import json
import sys

#Get number of GeoJSON objects of each type for each experiment
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

shptypes = ['Experiment','Plot','Zone','CropHarvest',
            'SoilWaterContent','CropCanopy','PlantAnalysis',
            'SoilChemicalAnalysis']

fout = open('stats3.txt','w')
for exp in exps:
    files = glob.glob('../geojson/'+exp+'/*.geojson')
    string = exp + '&'
    for shptype in shptypes:
        numfeat=0
        for myfile in files:
            if shptype in myfile:
                f = open(myfile,'r')
                gj = geojson.load(f)
                f.close()
                numfeat = len(gj.features)
                break
        string += str(numfeat) + '&'
    fout.write(string[:-1] + '\n')

numfeat=0
for sa in ['F013B4_SoilPhysicalAnalysis_DJH.geojson',
           'F013B4_SoilPhysicalAnalysis_KRT.geojson',
           'F033_SoilPhysicalAnalysis_DJH.geojson',
           'F105_SoilPhysicalAnalysis_DJH.geojson',
           'F111_SoilPhysicalAnalysis_DJH.geojson']:
    myfile = '../geojson/Soil/'+sa
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    numfeat+=len(gj.features)
fout.write(str(numfeat)+'\n')

numfeat=0
f = open('../geojson/Weather/AZMET_Maricopa_station.geojson')
gj = geojson.load(f)
f.close()
numfeat+=len(gj.features)
fout.write(str(numfeat)+'\n')

fout.close()

