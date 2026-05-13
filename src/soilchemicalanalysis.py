import bson
import json
import geojson
from osgeo import osr

class SoilChemicalAnalysis:
    def __init__(self,scid=None,geometry=None,sc_label=None):

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

        #Establish soil analysis core id
        self.scid = scid
        if self.scid is None:
            self.scid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(scid):
            raise ValueError('Invalid ObjectId in SoilChemicalAnalysis')
        self.doc.update({'_id':self.scid})
        self.doc.update({'scid':self.scid})

        #Set feature properties
        if sc_label is not None:
            self.doc['properties'].update({'sc_label':sc_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.scid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
