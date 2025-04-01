import bson
import json
import geojson
from osgeo import osr

class Plot:
    def __init__(self,pid=None,geometry=None,plt_label=None,trt_label=None):

        #Establish feature geometry in lon/lat (geojson standard)
        if geometry is not None:
            sprefin = geometry.GetSpatialReference()
            epsg = sprefin.GetAttrValue('AUTHORITY',1)
            if int(epsg) != 4326:
                sprefout = osr.SpatialReference()
                sprefout.ImportFromEPSG(4326) #Geographic WGS84
                coordtrans = osr.CoordinateTransformation(sprefin,sprefout)
                geometry.Transform(coordtrans)
            oring = geometry.GetGeometryRef(0)
            coords = list()
            for i in list(range(oring.GetPointCount())):
                lat, lon, z = oring.GetPoint(i)
                coords.append((lon,lat))
            poly=geojson.Polygon([coords],precision=8)
            self.doc = geojson.Feature(geometry=poly)
        else:
            self.doc = geojson.Feature()

        #Establish plot id
        self.pid = pid
        if self.pid is None:
            self.pid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(pid):
            raise ValueError('Invalid ObjectId in Plot')
        self.doc.update({'_id':self.pid})
        self.doc.update({'pid':self.pid})

        #Set feature properties
        self.plt_label = plt_label
        if plt_label is not None:
            self.doc['properties'].update({'plt_label':plt_label})
        if trt_label is not None:
            self.doc['properties'].update({'trt_label':trt_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.pid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})

    def addhaid(self,haid):
        if 'haids' in self.doc['properties'].keys():
            self.doc['properties']['haids'].append(haid)
        else:
            self.doc['properties'].update({'haids':[haid]})

    def addtid(self,tid):
        if 'tids' in self.doc['properties'].keys():
            self.doc['properties']['tids'].append(tid)
        else:
            self.doc['properties'].update({'tids':[tid]})

    def addccid(self,ccid):
        if 'ccids' in self.doc['properties'].keys():
            self.doc['properties']['ccids'].append(ccid)
        else:
            self.doc['properties'].update({'ccids':[ccid]})

    def addsaid(self,said):
        if 'saids' in self.doc['properties'].keys():
            self.doc['properties']['saids'].append(said)
        else:
            self.doc['properties'].update({'saids':[said]})

    def addzid(self,zid):
        if 'zids' in self.doc['properties'].keys():
            self.doc['properties']['zids'].append(zid)
        else:
            self.doc['properties'].update({'zids':[zid]})
