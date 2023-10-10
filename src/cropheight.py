import bson
import json
import geojson
from osgeo import osr

class CropHeight:
    def __init__(self,chid=None,geometry=None,ht_label=None):

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

        #Establish crop height flag id
        self.chid = chid
        if self.chid is None:
            self.chid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(chid):
            raise ValueError('Invalid ObjectId in CropHeight')
        self.doc.update({'_id':self.chid})
        self.doc.update({'chid':self.chid})

        #Set feature properties
        if ht_label is not None:
            self.doc['properties'].update({'ht_label':ht_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.chid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
