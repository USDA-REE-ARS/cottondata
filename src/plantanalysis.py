import bson
import json
import geojson
from osgeo import osr
from osgeo import ogr

class PlantAnalysis:
    def __init__(self,paid=None,geometry=None,pa_label=None):

        #Establish feature geometry in lon/lat (geojson standard)
        if geometry is not None:
            sprefin = geometry.GetSpatialReference()
            epsg = sprefin.GetAttrValue('AUTHORITY',1)
            if int(epsg) != 4326:
                sprefout = osr.SpatialReference()
                sprefout.ImportFromEPSG(4326) #Geographic WGS84
                coordtrans = osr.CoordinateTransformation(sprefin,sprefout)
                geometry.Transform(coordtrans)
            if geometry.GetGeometryType() == ogr.wkbPolygon:
                oring = geometry.GetGeometryRef(0)
                coords = list()
                for i in list(range(oring.GetPointCount())):
                    lat, lon, z = oring.GetPoint(i)
                    coords.append((lon,lat))
                poly=geojson.Polygon([coords],precision=8)
                self.doc = geojson.Feature(geometry=poly)
            elif geometry.GetGeometryType() == ogr.wkbMultiPoint:
                coords = list()
                for i in range(geometry.GetGeometryCount()):
                    point = geometry.GetGeometryRef(i)
                    coords.append((point.GetX(),point.GetY()))
                points=geojson.MultiPoint(coords,precision=8)
                self.doc = geojson.Feature(geometry=points)
            elif geometry.GetGeometryType() == ogr.wkbPoint:
                coords = (geometry.GetX(),geometry.GetY())
                point=geojson.Point(coords,precision=8)
                self.doc = geojson.Feature(geometry=point)
        else:
            self.doc = geojson.Feature()

        #Establish plant analysis sample id
        self.paid = paid
        if self.paid is None:
            self.paid = str(bson.objectid.ObjectId())
        if not bson.objectid.ObjectId.is_valid(paid):
            raise ValueError('Invalid ObjectId in PlantAnalysis')
        self.doc.update({'_id':self.paid})
        self.doc.update({'paid':self.paid})

        #Set feature properties
        if pa_label is not None:
            self.doc['properties'].update({'pa_label':pa_label})

    def __str__(self):
        return str(json.dumps(self.doc,indent=4))

    def getid(self):
        return self.paid

    def setproperty(self,key,value):
        self.doc['properties'].update({key:value})
