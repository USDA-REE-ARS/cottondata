import bson
import json
import geojson
from osgeo import osr

class Experiment:
    def __init__(self,eid=None,geometry=None,exp_label=None):

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

        #Establish experiment id
        self.eid = eid
        if self.eid is None:
            self.eid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(eid):
            raise ValueError('Invalid ObjectId in Experiment')
        self.doc.update({'_id':self.eid})
        self.doc.update({'eid':self.eid})

        #Set feature properties
        self.exp_label = exp_label
        if exp_label is not None:
            self.doc['properties'].update({'exp_label':exp_label})
        self.doc['properties'].update({'trt_info':[]})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.eid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})

    def addtreatment(self,mydict):
        mydict.update({'pids':[]})
        self.doc['properties']['trt_info'].append(mydict)

    def addpid(self,trt_label,pid):
        for item in self.doc['properties']['trt_info']:
            if item['trt_label'] == trt_label:
                item['pids'].append(pid)
        if 'pids' in self.doc['properties'].keys():
            self.doc['properties']['pids'].append(pid)
        else:
            self.doc['properties'].update({'pids':[pid]})
