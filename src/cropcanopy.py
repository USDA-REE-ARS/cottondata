import bson
import json
import geojson
from osgeo import osr

class CropCanopy:
    def __init__(self,ccid=None,geometry=None,cc_label=None):

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

        #Establish crop canopy flag id
        self.ccid = ccid
        if self.ccid is None:
            self.ccid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(ccid):
            raise ValueError('Invalid ObjectId in CropCanopy')
        self.doc.update({'_id':self.ccid})
        self.doc.update({'ccid':self.ccid})

        #Set feature properties
        if cc_label is not None:
            self.doc['properties'].update({'cc_label':cc_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.ccid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
