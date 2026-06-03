import os
import sys
import math
import pandas as pd
from osgeo import ogr, osr
import geojson
import bson
import datetime

class Weather:
    def __init__(self,wid=None,geometry=None,w_label=None):

        #Establish feature geometry in lon/lat (geojson standard)
        if geometry is not None:
            sprefin = geometry.GetSpatialReference()
            epsg = sprefin.GetAttrValue('AUTHORITY',1)
            if int(epsg) != 4326:
                sprefout = osr.SpatialReference()
                sprefout.ImportFromEPSG(4326) #Geographic WGS84
                coordtrans = osr.CoordinateTransformation(sprefin,sprefout)
                geometry.Transform(coordtrans)
            coords = (geometry.GetX(),geometry.GetY())
            point=geojson.Point(coords,precision=8)
            self.doc = geojson.Feature(geometry=point)
        else:
            self.doc = geojson.Feature()

        #Establish weather id
        self.wid = wid
        if self.wid is None:
            self.wid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(wid):
            raise ValueError('Invalid ObjectId in Weather')
        self.doc.update({'wid':self.wid})
        self.doc.update({'id':self.wid}) #geojson standard id
        self.doc.update({'_id':self.wid}) #mongodb primary key

        #Set feature properties
        if w_label is not None:
            self.doc['properties'].update({'w_label':w_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.wid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})

directory = '../geojson/Weather'
for filename in os.listdir(directory):
    if filename.endswith('.geojson'):
        file_path = os.path.join(directory,filename)
        os.remove(file_path)

########################################################################
#Arizona Meteorological Network (AZMET) station, Maricopa, Arizona
#Daily weather data included from 1987-2023
shapefile = '../Data/Weather/AZMET_Maricopa_station.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
wfile = '../Data/Weather/AZMET_Maricopa_station_1987-2023.xlsx'
wth = pd.read_excel(wfile,sheet_name='WeatherDF')
wth['key'] = wth['Year'].astype('string') + '-' + wth['DOY'].map('{:03d}'.format)
wths = list()
for feature in layer:
    wid = feature.GetField('ObjectId')
    w_label = 'AZMET_Maricopa'
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in weather shapefile.')
        sys.exit()
    mywth = Weather(wid=wid,geometry=geometry,w_label=w_label)
    #AZMET Maricopa weather data, 1987-2023
    REFHT = 2.0
    mywth.setproperty('REFHT',REFHT)
    WNDHT = 3.0
    mywth.setproperty('WNDHT',WNDHT)
    items={'TMAX':1,'TMIN':1,'TAVD':1,'RHMXD':1,'RHUMD':1,'RHAVD':1,
           'VPDAVD':2,'SRAD':2,'RAIN':2,'STMX1':1,'STMN1':1,'STAV1':1,
           'STMX2':1,'STMN2':1,'STAV2':1,'WNDSP':1,'WNDRN':1,'WNDD':0,
           'WNDDSD':0,'WNDMX':1,'HTUNT':1,'REFET':1,'ASCEETO':1,'VPRSD':2,
           'TDEW':1}
    for item in items.keys():
        wdata = list()
        tcurrent = datetime.datetime.strptime('1987-001', '%Y-%j')
        tdelta = datetime.timedelta(days=1)
        while tcurrent <= datetime.datetime.strptime('2023-365', '%Y-%j'):
            key = tcurrent.strftime('%Y-%j')
            row = wth[wth['key'] == key]
            date = datetime.datetime.strptime(key,'%Y-%j').strftime('%Y-%m-%d')
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                if item[:2] not in ['ST']:
                    mydict = {'date':date,'value':value}
                else:
                    if item in ['STMX1','STMN1','STAV1']:
                        if int(key[:4])<1999:
                            depth = round(2*2.54,2) #2 inch to cm
                        else:
                            depth = round(4*2.54,2) #4 inch to cm
                    elif item in ['STMX2','STMN2','STAV2']:
                        if int(key[:4])<1999:
                            depth = round(4*2.54,2) #4 inch to cm
                        else:
                            depth = round(20*2.54,2) #20 inch to cm
                    mydict = {'date':date,'depth':depth,'value':value}
                wdata.append(mydict)
            tcurrent = tcurrent + tdelta
        if wdata:
            mywth.setproperty(item,wdata)
    wths.append(mywth)
features = list()
for mywth in wths:
    features.append(mywth.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/Weather/AZMET_Maricopa_station.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
