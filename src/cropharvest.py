import bson
import json
import geojson
from osgeo import osr

class CropHarvest:
    def __init__(self,chid=None,geometry=None,ha_label=None):

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

        #Establish harvest area id
        self.chid = chid
        if self.chid is None:
            self.chid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(chid):
            raise ValueError('Invalid ObjectId in CropHarvest')
        self.doc.update({'chid':self.chid})
        self.doc.update({'id':self.chid}) #geojson standard id
        self.doc.update({'_id':self.chid}) #mongodb primary key

        #Set feature properties
        if ha_label is not None:
            self.doc['properties'].update({'ch_label':ha_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.chid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
