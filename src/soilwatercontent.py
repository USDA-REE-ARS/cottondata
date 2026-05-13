import bson
import json
import geojson
from osgeo import osr

class SoilWaterContent:
    def __init__(self,tid=None,geometry=None,tb_label=None):

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

        #Establish neutron tube id
        self.tid = tid
        if self.tid is None:
            self.tid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(tid):
            raise ValueError('Invalid ObjectId in SoilWaterContent')
        self.doc.update({'_id':self.tid})
        self.doc.update({'tid':self.tid})

        #Set feature properties
        if tb_label is not None:
            self.doc['properties'].update({'tb_label':tb_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.tid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
