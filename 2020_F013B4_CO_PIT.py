import os
import sys
import math
import experiment
import plot
import zone
import harvestarea
import neutronswc
import cropheight
import pandas as pd
from osgeo import ogr

fname = os.path.basename(__file__)
fname = os.path.splitext(fname)[0]

numtrt = 4
numrep = 6

########################################################################
#Experiment
shapefile = './Data/'+fname+'/'+fname+'_Experiment.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
if layer.GetFeatureCount() != 1:
    print('Experiment shapefile should have one feature.')
    sys.exit()
for feature in layer:
    eid = feature.GetField('ObjectId')
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in experiment shapefile.')
        sys.exit()
    exp_area = geometry.GetArea()
    myexp = experiment.Experiment(eid=eid,geometry=geometry,exp_label=fname)
myexp.setproperty('EXP_AREA',round(exp_area,6))

expmeta = {
    'EXNAME':'Precision irrigation technologies, Season 2 of 2',
    'OBJECTIVES':'See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'EXP_NARR':'See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'MAIN_FACTOR':'Irrigation management methods: increasing complexity of technologies used',
    'FACTORS':'Four irrigation management methods',
    'TRT_NO':4,
    'REP_NO':6,
    'METHODS':'See See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2020',
    'EXP_DUR':1,
    'CR_SYSTEM':'No-till cotton after winter barley cover crop',
    'LAST_NAME':'Thorp',
    'FIRST_NAME':'Kelly',
    'MID_INITIAL':'R',
    'PERSON_NOTES':'Field technicians: Matt Hagler and Suzette Maneely',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'kelly.thorp@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'Intense heat stress in late summer',
    'SUITE_NAME':'Precision irrigation technologies',
    'SUITE_OBJ':'See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'FL_NAME':'Field 13, Bench 4, Spans 4-6',
    'FL_LAT':33.07914, #from Google maps
    'FL_LONG':-111.97737, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'MDL':'Irrigation scheduling via an ET-based FAO56 soil water balance model, uniform irrigation',
            'SOL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with site-specific soil inputs, site-specific irrigation',
            'UAS':'Irrigation scheduling via an ET-based FAO56 soil water balance model with site-specific soil inputs and basal crop coefficients, uniform irrigation',
            'VRI':'Irrigation scheduling via an ET-based FAO56 soil water balance model with site-specific soil inputs and basal crop coefficients, site-specific irrigation'}

for key in trt_info.keys():
    data = {'trt_label':key,'description':trt_info[key]}
    myexp.addtreatment(data)
########################################################################

########################################################################
#Plots
shapefile = './Data/'+fname+'/'+fname+'_Plots.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
#spref = layer.GetSpatialRef()
#epsg = spref.GetAttrValue('AUTHORITY',1)
#lyrdef = plotlyr.GetLayerDefn()
#for i in list(range(lyrdef.GetFieldCount())):
#    print(lyrdef.GetFieldDefn(i).GetName())
yfile = './Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Plot Scale',skiprows=5)
plots = list()
for feature in layer:
    pid = feature.GetField('ObjectId')
    plt_label = feature.GetField('PlotID')
    trt_label = feature.GetField('Treatment')
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    plt_area = geometry.GetArea()
    myplot = plot.Plot(pid=pid,geometry=geometry,plt_label=plt_label,trt_label=trt_label)
    myexp.addpid(trt_label,myplot.getid())
    myplot.setproperty('PLT_AREA',round(plt_area,6))
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
    row = row.astype({'FBTCT':float})
    myplot.setproperty('HARM'  ,row.iloc[0]['HARM'])
    myplot.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%m/%d/%Y'))
    myplot.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    myplot.setproperty('GNDAT' ,row.iloc[0]['GNDAT'].strftime('%m/%d/%Y'))
    myplot.setproperty('FFRAC' ,round(row.iloc[0]['FFRAC' ],4))
    myplot.setproperty('SFRAC' ,round(row.iloc[0]['SFRAC' ],4))
    myplot.setproperty('TFRAC' ,round(row.iloc[0]['TFRAC' ],4))
    myplot.setproperty('FWCAG' ,round(row.iloc[0]['FWCAG' ],2))
    myplot.setproperty('SWCAG' ,round(row.iloc[0]['SWCAG' ],2))
    myplot.setproperty('WFWAH' ,round(row.iloc[0]['WFWAH' ],1))
    myplot.setproperty('WSWAH' ,round(row.iloc[0]['WSWAH' ],1))
    myplot.setproperty('WSCWAH',round(row.iloc[0]['WSCWAH'],1))
    myplot.setproperty('DFWAH' ,round(row.iloc[0]['DFWAH' ],1))
    myplot.setproperty('DSWAH' ,round(row.iloc[0]['DSWAH' ],1))
    myplot.setproperty('DSCWAH',round(row.iloc[0]['DSCWAH'],1))
    myplot.setproperty('QLDAT' ,row.iloc[0]['QLDAT'].strftime('%m/%d/%Y'))
    myplot.setproperty('FBMIC' ,round(row.iloc[0]['FBMIC' ],1))
    myplot.setproperty('FBLTH' ,round(row.iloc[0]['FBLTH' ],3))
    myplot.setproperty('FBUNI' ,round(row.iloc[0]['FBUNI' ],1))
    myplot.setproperty('FBSTR' ,round(row.iloc[0]['FBSTR' ],1))
    myplot.setproperty('FBELO' ,round(row.iloc[0]['FBELO' ],1))
    myplot.setproperty('FBCRD' ,round(row.iloc[0]['FBCRD' ],1))
    myplot.setproperty('FBCLB' ,round(row.iloc[0]['FBCLB' ],1))
    myplot.setproperty('FBTCT' ,round(row.iloc[0]['FBTCT' ],0))
    myplot.setproperty('FBTAR' ,round(row.iloc[0]['FBTAR' ],2))
    myplot.setproperty('FBSFI' ,round(row.iloc[0]['FBSFI' ],1))
    plots.append(myplot)
########################################################################

########################################################################
#Zones
shapefile = './Data/'+fname+'/'+fname+'_Zones.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
zones = list()
for feature in layer:
    zid = feature.GetField('ObjectId')
    zon_label = feature.GetField('ZoneID')
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    zon_area = geometry.GetArea()
    myzone = zone.Zone(zid=zid,geometry=geometry,zon_label=zon_label)
    myzone.setproperty('ZON_AREA',round(zon_area,6))
    for plot in plots:
        if plot.plt_label == zon_label[:2]:
            plot.addzid(myzone.getid())
    zones.append(myzone)
########################################################################

########################################################################
#Harvest Areas
shapefile = './Data/'+fname+'/'+fname+'_HarvestAreas.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = './Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=53)
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., 11W)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    ha_area = geometry.GetArea()
    myha = harvestarea.HarvestArea(haid=haid,geometry=geometry,ha_label=ha_label)
    myha.setproperty('HA_AREA',round(ha_area,6))
    #Yield and fiber quality data
    row = yld.loc[yld['HID'] == ha_label]
    row = row.astype({'FBTCT':float})
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myha.setproperty('HARM',row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myha.setproperty('HADAT',row.iloc[0]['HADAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myha.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not str(row.iloc[0]['GNDAT']) in ['nan','NaT']:
        myha.setproperty('GNDAT',row.iloc[0]['GNDAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['FFRAC']):
        myha.setproperty('FFRAC' ,round(row.iloc[0]['FFRAC' ],4))
    if not math.isnan(row.iloc[0]['SFRAC']):
        myha.setproperty('SFRAC' ,round(row.iloc[0]['SFRAC' ],4))
    if not math.isnan(row.iloc[0]['TFRAC']):
        myha.setproperty('TFRAC' ,round(row.iloc[0]['TFRAC' ],4))
    if not math.isnan(row.iloc[0]['FWCAG']):
        myha.setproperty('FWCAG' ,round(row.iloc[0]['FWCAG' ],2))
    if not math.isnan(row.iloc[0]['SWCAG']):
        myha.setproperty('SWCAG' ,round(row.iloc[0]['SWCAG' ],2))
    if not math.isnan(row.iloc[0]['WFWAH']):
        myha.setproperty('WFWAH' ,round(row.iloc[0]['WFWAH' ],1))
    if not math.isnan(row.iloc[0]['WSWAH']):
        myha.setproperty('WSWAH' ,round(row.iloc[0]['WSWAH' ],1))
    if not math.isnan(row.iloc[0]['WSCWAH']):
        myha.setproperty('WSCWAH',round(row.iloc[0]['WSCWAH'],1))
    if not math.isnan(row.iloc[0]['DFWAH']):
        myha.setproperty('DFWAH' ,round(row.iloc[0]['DFWAH' ],1))
    if not math.isnan(row.iloc[0]['DSWAH']):
        myha.setproperty('DSWAH' ,round(row.iloc[0]['DSWAH' ],1))
    if not math.isnan(row.iloc[0]['DSCWAH']):
        myha.setproperty('DSCWAH',round(row.iloc[0]['DSCWAH'],1))
    if not str(row.iloc[0]['QLDAT']) in ['nan','NaT']:
        myha.setproperty('QLDAT',row.iloc[0]['QLDAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['FBMIC']):
        myha.setproperty('FBMIC' ,round(row.iloc[0]['FBMIC' ],1))
    if not math.isnan(row.iloc[0]['FBLTH']):
        myha.setproperty('FBLTH' ,round(row.iloc[0]['FBLTH' ],3))
    if not math.isnan(row.iloc[0]['FBUNI']):
        myha.setproperty('FBUNI' ,round(row.iloc[0]['FBUNI' ],1))
    if not math.isnan(row.iloc[0]['FBSTR']):
        myha.setproperty('FBSTR' ,round(row.iloc[0]['FBSTR' ],1))
    if not math.isnan(row.iloc[0]['FBELO']):
        myha.setproperty('FBELO' ,round(row.iloc[0]['FBELO' ],1))
    if not math.isnan(row.iloc[0]['FBCRD']):
        myha.setproperty('FBCRD' ,round(row.iloc[0]['FBCRD' ],1))
    if not math.isnan(row.iloc[0]['FBCLB']):
        myha.setproperty('FBCLB' ,round(row.iloc[0]['FBCLB' ],1))
    if not str(row.iloc[0]['FBCGR']) in ['nan','NaT']:
        myha.setproperty('FBCGR' ,row.iloc[0]['FBCGR'])
    if not math.isnan(row.iloc[0]['FBTCT']):
        myha.setproperty('FBTCT' ,round(row.iloc[0]['FBTCT' ],0))
    if not math.isnan(row.iloc[0]['FBTAR']):
        myha.setproperty('FBTAR' ,round(row.iloc[0]['FBTAR' ],2))
    if not math.isnan(row.iloc[0]['FBSFI']):
        myha.setproperty('FBSFI' ,round(row.iloc[0]['FBSFI' ],1))
    found=False
    for plot in plots:
        if plot.plt_label == ha_label[:3]:
            plot.addhaid(myha.getid())
            found=True
            break
    if not found:
        raise Exception('Did not find plot for HA %s' % ha_label)
    hareas.append(myha)
########################################################################

########################################################################
#Neutron Soil Water Content
shapefile = './Data/'+fname+'/'+fname+'_NeutronSWC.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
tubes = list()
for feature in layer:
    tid = feature.GetField('ObjectId')
    tb_label = feature.GetField('TubeID') #(e.g., 11) 
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mytube = neutronswc.NeutronSWC(tid=tid,geometry=geometry,tb_label=tb_label)

    for plot in plots:
        if plot.plt_label == tb_label:
            plot.addtid(mytube.getid())
    tubes.append(mytube)
########################################################################

########################################################################
#Crop Height
shapefile = './Data/'+fname+'/'+fname+'_CropHeight.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
crphts = list()
for feature in layer:
    chid = feature.GetField('ObjectID')
    ht_label = feature.GetField('CHID')  #(e.g., 11N)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    myht = cropheight.CropHeight(chid=chid,geometry=geometry,ht_label=ht_label)

    for plot in plots:
        if plot.plt_label == ht_label[:2]:
            plot.addchid(myht.getid())
    crphts.append(myht)
########################################################################

########################################################################
#Write geojson files
f = open('./geojson/'+fname+'/'+fname+'_experiment.geojson','w')
f.write(myexp.__str__())
f.close()

f = open('./geojson/'+fname+'/'+fname+'_plots.geojson','w')
for myplot in plots:
    f.write(myplot.__str__())
f.close()

f = open('./geojson/'+fname+'/'+fname+'_zones.geojson','w')
for myzone in zones:
    f.write(myzone.__str__())
f.close()

f = open('./geojson/'+fname+'/'+fname+'_harvestareas.geojson','w')
for myha in hareas:
    f.write(myha.__str__())
f.close()

f = open('./geojson/'+fname+'/'+fname+'_neutronswc.geojson','w')
for mytube in tubes:
    f.write(mytube.__str__())
f.close()

f = open('./geojson/'+fname+'/'+fname+'_cropheight.geojson','w')
for mycrpht in crphts:
    f.write(mycrpht.__str__())
f.close()

########################################################################
