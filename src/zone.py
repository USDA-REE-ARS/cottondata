import bson
import json
import geojson
from osgeo import osr

class Zone:
    def __init__(self,zid=None,geometry=None,zon_label=None):

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

        #Establish zone id
        self.zid = zid
        if self.zid is None:
            self.zid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(zid):
            raise ValueError('Invalid ObjectId in Zone')
        self.doc.update({'_id':self.zid})
        self.doc.update({'zid':self.zid})

        #Set feature properties
        if zon_label is not None:
            self.doc['properties'].update({'zon_label':zon_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.zid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
