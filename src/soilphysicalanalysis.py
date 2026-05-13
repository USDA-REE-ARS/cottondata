import bson
import json
import geojson
from osgeo import osr

class SoilPhysicalAnalysis:
    def __init__(self,said=None,geometry=None,sa_label=None):

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
        self.said = said
        if self.said is None:
            self.said = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(said):
            raise ValueError('Invalid ObjectId in SoilPhysicalAnalysis')
        self.doc.update({'_id':self.said})
        self.doc.update({'said':self.said})

        #Set feature properties
        if sa_label is not None:
            self.doc['properties'].update({'sa_label':sa_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.said

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
