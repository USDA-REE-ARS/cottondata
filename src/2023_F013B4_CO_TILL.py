import os
import sys
import math
import experiment
import plot
import zone
import harvestarea
import neutronswc
import cropcanopy
import soilanalysis
import pandas as pd
from osgeo import ogr
import geojson

fname = os.path.basename(__file__)
fname = os.path.splitext(fname)[0]

numtrt = 4
numrep = 3

########################################################################
#Experiment
shapefile = '../Data/'+fname+'/'+fname+'_Experiment.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
if layer.GetFeatureCount() != 1:
    print('Experiment shapefile should have one feature.')
    sys.exit()
for feature in layer:
    eid = feature.GetField('ObjectId')
    geometry = feature.GetGeometryRef()
    geomcount = geometry.GetGeometryCount()
    nodecount = geometry.GetGeometryRef(0).GetPointCount()
    if geomcount != 1 or nodecount != 5:
        print('Polygons should have one geometry and five nodes.')
        sys.exit()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in experiment shapefile.')
        sys.exit()
    exp_area = geometry.GetArea()
    myexp = experiment.Experiment(eid=eid,geometry=geometry,exp_label=fname)
myexp.setproperty('EXP_AREA',round(exp_area,6))

expmeta = {
    'EXNAME':'Tillage and cover crop study, Season 1 of 1',
    #'OBJECTIVES':'See Thorp et al., TBD',
    #'EXP_NARR':'See Thorp et al., TBD',
    'MAIN_FACTOR':'Type of tillage: beds and furrows, on-the-flat, strip tillage, no tillage',
    'FACTORS':'Four tillage treatments',
    'TRT_NO':4,
    'REP_NO':3,
    #'METHODS':'See Thorp et al., TBD',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2023',
    'EXP_DUR':1,
    'CR_SYSTEM':'Strip-till cotton after winter barley cover crop',
    'LAST_NAME':'Thorp',
    'FIRST_NAME':'Kelly',
    'MID_INITIAL':'R',
    'PERSON_NOTES':'Field technicians: Matt Hagler and Suzette Maneely',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'kelly.thorp@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'',
    'SUITE_NAME':'Tillage and cover crop study',
    #'SUITE_OBJ':'See Thorp et al., TBD',
    'FL_NAME':'Field 13, Bench 4, Spans 4-6',
    'FL_LAT':33.07914, #from Google maps
    'FL_LONG':-111.97737, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'BEDS':'Cotton planted on raised beds after full tillage',
            'FLAT':'Cotton planted on the flat after full tillage',
            'STRIP':'Cotton planted into tilled strips within a terminated barley cover crop',
            'NOTILL':'Cotton planted into a terminated barley cover crop'}

for key in trt_info.keys():
    data = {'trt_label':key,'description':trt_info[key]}
    myexp.addtreatment(data)
########################################################################

########################################################################
#Plots
shapefile = '../Data/'+fname+'/'+fname+'_Plots.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
#spref = layer.GetSpatialRef()
#epsg = spref.GetAttrValue('AUTHORITY',1)
#lyrdef = plotlyr.GetLayerDefn()
#for i in list(range(lyrdef.GetFieldCount())):
#    print(lyrdef.GetFieldDefn(i).GetName())
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Plot Scale',skiprows=5)
mfile = '../Data/'+fname+'/'+fname+'_Management.xlsx'
irrig = pd.read_excel(mfile,sheet_name='IrrigationDF')
dfile = '../Data/'+fname+'/'+fname+'_CropCanopy.xlsx'
develop = pd.read_excel(dfile,sheet_name='PlotDevelop')
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='PlotCover')
plots = list()
for feature in layer:
    pid = feature.GetField('ObjectId')
    plt_label = feature.GetField('Plot')
    trt_label = feature.GetField('Treatment')
    geometry = feature.GetGeometryRef()
    geomcount = geometry.GetGeometryCount()
    nodecount = geometry.GetGeometryRef(0).GetPointCount()
    if geomcount != 1 or nodecount != 5:
        print('Polygons should have one geometry and five nodes.')
        sys.exit()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    plt_area = geometry.GetArea()
    myplot = plot.Plot(pid=pid,geometry=geometry,plt_label=plt_label,trt_label=trt_label)
    myexp.addpid(trt_label,myplot.getid())
    myplot.setproperty('PLT_AREA',round(plt_area,6))
    #Management information
    myplot.setproperty('CUL_NAME', 'NexGen 3195 B3XF')
    myplot.setproperty('PDATE', '04/24/2023')
    myplot.setproperty('PLYR', 2023)
    myplot.setproperty('PLDAY', 114)
    myplot.setproperty('IROP', 'IR004')
    idata = dict()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+str(int(row['DOY']))
        IRVAL = row['IRVAL100']
        if not math.isnan(IRVAL):
            idata.update({key:round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = dict()
    fdata.update({'2023158':51.9})
    fdata.update({'2023178':51.9})
    fdata.update({'2023199':51.9})
    myplot.setproperty('FEAMN',fdata)
    tdata = dict()
    cdata = dict()
    if int(plt_label[1:]) >= 7:
        tdata.update({'20230404':'Disk'})
        tdata.update({'20230411':'Land plane'})
        if trt_label == 'BEDS':
            tdata.update({'20230417':'Raise beds'})
        cdata.update({'20230411':'Apply Acumen (pendimethalin)'})
    elif int(plt_label[1:]) < 7:
        if trt_label == 'STRIP':
            tdata.update({'20230417':'Strip tillage'})
        cdata.update({'20230420':'Apply Acumen (pendimethalin)'})
    if int(plt_label[1:]) <= 8:
        cdata.update({'20230523':'Apply RoundUp (glyphosate)'})
        cdata.update({'20230606':'Apply RoundUp (glyphosate)'})
    cdata.update({'20230724':'Apply Mepstar6 (mepiquat chloride)'})
    cdata.update({'20231009':'Apply Redipik (diuron, thidiazuron)'})
    cdata.update({'20231025':'Apply Redipik (diuron, thidiazuron) and CottonQuik (urea sulfate, ethephon)'})
    if tdata:
        myplot.setproperty('TI_NOTES',tdata)
    myplot.setproperty('CH_NOTES',cdata)
    #Crop Development
    row = develop.loc[develop['Plot'] == plt_label]
    if not str(row.iloc[0]['EDATE']) in ['nan','NaT']:
        myplot.setproperty('EDATE',row.iloc[0]['EDATE'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['PLYRE']):
        myplot.setproperty('PLYRE',int(row.iloc[0]['PLYRE']))
    if not math.isnan(row.iloc[0]['PLDOE']):
        myplot.setproperty('PLDOE',int(round(row.iloc[0]['PLDOE'],0)))
    if not str(row.iloc[0]['LF1D']) in ['nan','NaT']:
        myplot.setproperty('LF1D',row.iloc[0]['EDATE'].strftime('%m/%d/%Y'))
    if not str(row.iloc[0]['ADAT']) in ['nan','NaT']:
        myplot.setproperty('ADAT',row.iloc[0]['ADAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['ADOY']):
        myplot.setproperty('ADOY',int(round(row.iloc[0]['ADOY'],0)))
    nawf = dict()
    for doy in ['184','194','201','208','215','236']:
        if not math.isnan(row.iloc[0]['NAWF'+doy]):
            nawf.update({'2023'+doy:round(row.iloc[0]['NAWF'+doy],1)})
    if nawf:
        myplot.setproperty('NAWF',nawf)
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['PlotID'] == plt_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2023'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myplot.setproperty('FRCOV',fcdata)
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
    row = row.astype({'FBTCT':float})
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myplot.setproperty('HARM'  ,row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myplot.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myplot.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not math.isnan(row.iloc[0]['BWCAH']):
        myplot.setproperty('BWCAH' ,round(row.iloc[0]['BWCAH' ],2))
    if not math.isnan(row.iloc[0]['DBWAH']):
        myplot.setproperty('DBWAH' ,round(row.iloc[0]['DBWAH' ],1))
    if not str(row.iloc[0]['GNDAT']) in ['nan','NaT']:
        myplot.setproperty('GNDAT' ,row.iloc[0]['GNDAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['FFRAC']):
        myplot.setproperty('FFRAC' ,round(row.iloc[0]['FFRAC' ],4))
    if not math.isnan(row.iloc[0]['SFRAC']):
        myplot.setproperty('SFRAC' ,round(row.iloc[0]['SFRAC' ],4))
    if not math.isnan(row.iloc[0]['TFRAC']):
        myplot.setproperty('TFRAC' ,round(row.iloc[0]['TFRAC' ],4))
    if not math.isnan(row.iloc[0]['WFWAH']):
        myplot.setproperty('WFWAH' ,round(row.iloc[0]['WFWAH' ],1))
    if not math.isnan(row.iloc[0]['WSWAH']):
        myplot.setproperty('WSWAH' ,round(row.iloc[0]['WSWAH' ],1))
    if not math.isnan(row.iloc[0]['WSCWAH']):
        myplot.setproperty('WSCWAH',round(row.iloc[0]['WSCWAH'],1))
    if not math.isnan(row.iloc[0]['DFWAH']):
        myplot.setproperty('DFWAH' ,round(row.iloc[0]['DFWAH' ],1))
    if not math.isnan(row.iloc[0]['DSWAH']):
        myplot.setproperty('DSWAH' ,round(row.iloc[0]['DSWAH' ],1))
    if not math.isnan(row.iloc[0]['DSCWAH']):
        myplot.setproperty('DSCWAH',round(row.iloc[0]['DSCWAH'],1))
    if not str(row.iloc[0]['QLDAT']) in ['nan','NaT']:
        myplot.setproperty('QLDAT' ,row.iloc[0]['QLDAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['FBMIC']):
        myplot.setproperty('FBMIC' ,round(row.iloc[0]['FBMIC' ],1))
    if not math.isnan(row.iloc[0]['FBLTH']):
        myplot.setproperty('FBLTH' ,round(row.iloc[0]['FBLTH' ],3))
    if not math.isnan(row.iloc[0]['FBUNI']):
        myplot.setproperty('FBUNI' ,round(row.iloc[0]['FBUNI' ],1))
    if not math.isnan(row.iloc[0]['FBSTR']):
        myplot.setproperty('FBSTR' ,round(row.iloc[0]['FBSTR' ],1))
    if not math.isnan(row.iloc[0]['FBELO']):
        myplot.setproperty('FBELO' ,round(row.iloc[0]['FBELO' ],1))
    if not math.isnan(row.iloc[0]['FBCRD']):
        myplot.setproperty('FBCRD' ,round(row.iloc[0]['FBCRD' ],1))
    if not math.isnan(row.iloc[0]['FBCLB']):
        myplot.setproperty('FBCLB' ,round(row.iloc[0]['FBCLB' ],1))
    if not math.isnan(row.iloc[0]['FBTCT']):
        myplot.setproperty('FBTCT' ,round(row.iloc[0]['FBTCT' ],0))
    if not math.isnan(row.iloc[0]['FBTAR']):
        myplot.setproperty('FBTAR' ,round(row.iloc[0]['FBTAR' ],2))
    if not math.isnan(row.iloc[0]['FBSFI']):
        myplot.setproperty('FBSFI' ,round(row.iloc[0]['FBSFI' ],1))
    plots.append(myplot)
########################################################################

########################################################################
#Zones
shapefile = '../Data/'+fname+'/'+fname+'_Zones.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='ZoneCover')
zones = list()
for feature in layer:
    zid = feature.GetField('ObjectId')
    zon_label = feature.GetField('ZoneID')
    geometry = feature.GetGeometryRef()
    geomcount = geometry.GetGeometryCount()
    nodecount = geometry.GetGeometryRef(0).GetPointCount()
    if geomcount != 1 or nodecount != 5:
        print('Polygons should have one geometry and five nodes.')
        sys.exit()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    zon_area = geometry.GetArea()
    myzone = zone.Zone(zid=zid,geometry=geometry,zon_label=zon_label)
    myzone.setproperty('ZON_AREA',round(zon_area,6))
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['ZoneID'] == zon_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2023'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myzone.setproperty('FRCOV',fcdata)
    for plot in plots:
        if plot.plt_label == zon_label[:3]:
            plot.addzid(myzone.getid())
    zones.append(myzone)
########################################################################

########################################################################
#Harvest Areas
shapefile = '../Data/'+fname+'/'+fname+'_HarvestAreas.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=84)
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='HACover')
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p01-01-E)
    geometry = feature.GetGeometryRef()
    geomcount = geometry.GetGeometryCount()
    nodecount = geometry.GetGeometryRef(0).GetPointCount()
    if geomcount != 1 or nodecount != 5:
        print('Polygons should have one geometry and five nodes.')
        sys.exit()
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
    if not math.isnan(row.iloc[0]['BWCAH']):
        myha.setproperty('BWCAH' ,round(row.iloc[0]['BWCAH' ],2))
    if not math.isnan(row.iloc[0]['DBWAH']):
        myha.setproperty('DBWAH' ,round(row.iloc[0]['DBWAH' ],1))
    if not str(row.iloc[0]['GNDAT']) in ['nan','NaT']:
        myha.setproperty('GNDAT',row.iloc[0]['GNDAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['FFRAC']):
        myha.setproperty('FFRAC' ,round(row.iloc[0]['FFRAC' ],4))
    if not math.isnan(row.iloc[0]['SFRAC']):
        myha.setproperty('SFRAC' ,round(row.iloc[0]['SFRAC' ],4))
    if not math.isnan(row.iloc[0]['TFRAC']):
        myha.setproperty('TFRAC' ,round(row.iloc[0]['TFRAC' ],4))
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
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['HID'] == ha_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2023'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myha.setproperty('FRCOV',fcdata)
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
shapefile = '../Data/'+fname+'/'+fname+'_NeutronSWC.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
swcfile = '../Data/'+fname+'/'+fname+'_NeutronSWC.xlsx'
swc = pd.read_excel(swcfile,sheet_name='Summary')
tubes = list()
for feature in layer:
    tid = feature.GetField('ObjectId')
    tb_label = feature.GetField('Tube') #(e.g., p01-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mytube = neutronswc.NeutronSWC(tid=tid,geometry=geometry,tb_label=tb_label)
    #Neutron soil water content data
    rows = swc.loc[swc['Tube'] == tb_label]
    rows = rows.sort_values(by='DOY')
    depcols = sorted([col for col in rows.columns if col[-2:]=='cm'])
    swcdata = dict()
    for i, row in rows.iterrows():
        swcitem = dict()
        for depcol in depcols:
            if not math.isnan(row.loc[depcol]):
                depth = int(depcol[1:-2])
                swcitem.update({depth:round(row.loc[depcol],5)})
        key = '{:04d}{:03d}'.format(row.loc['Year'],row.loc['DOY'])
        if swcitem:
            swcdata.update({key:swcitem})
    if swcdata:
        mytube.setproperty('SWLD',swcdata)
    found=False
    for plot in plots:
        if plot.plt_label == tb_label[:3]:
            plot.addtid(mytube.getid())
            found=True
            break
    if not found:
        raise Exception('Did not find plot for neutron tube %s' % tb_label)
    tubes.append(mytube)
########################################################################

########################################################################
#Crop Canopy
shapefile = '../Data/'+fname+'/'+fname+'_CropCanopy.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
ccfile = '../Data/'+fname+'/'+fname+'_CropCanopy.xlsx'
cch = pd.read_excel(ccfile,sheet_name='Height')
ccw = pd.read_excel(ccfile,sheet_name='Width')
ccden = pd.read_excel(ccfile,sheet_name='Density')
ccdev = pd.read_excel(ccfile,sheet_name='Develop')
crpcns = list()
for feature in layer:
    ccid = feature.GetField('ObjectID')
    cc_label = feature.GetField('CCID')  #(e.g., p01-01)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mycc = cropcanopy.CropCanopy(ccid=ccid,geometry=geometry,cc_label=cc_label)
    #Crop canopy data
    htdata = dict()
    rowh = cch.loc[cch['CCID'] == cc_label]
    doycols = sorted([col for col in cch.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2023'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(rowh.iloc[0][doycol]):
            CHTD = float(rowh.iloc[0][doycol])/100. #m
            htdata.update({key:round(CHTD,2)})
    if htdata:
        mycc.setproperty('CHTD',htdata)
    wddata = dict()
    roww = ccw.loc[ccw['CCID'] == cc_label]
    doycols = sorted([col for col in ccw.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2023'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(roww.iloc[0][doycol]):
            CWID = float(roww.iloc[0][doycol])/100. #m
            wddata.update({key:round(CWID,2)})
    if wddata:
        mycc.setproperty('CWID',wddata)
    rowden = ccden.loc[ccden['CCID'] == cc_label]
    if not math.isnan(rowden.iloc[0]['PLAPD']):
        PLAPD = float(rowden.iloc[0]['PLAPD'])
        mycc.setproperty('PLAPD',round(PLAPD,1))
    rowdev = ccdev.loc[ccdev['CCID'] == cc_label]
    if not str(rowdev.iloc[0]['EDATE']) in ['nan','NaT']:
        mycc.setproperty('EDATE',rowdev.iloc[0]['EDATE'].strftime('%m/%d/%Y'))
    if not math.isnan(rowdev.iloc[0]['PLYRE']):
        mycc.setproperty('PLYRE',int(rowdev.iloc[0]['PLYRE']))
    if not math.isnan(rowdev.iloc[0]['PLDOE']):
        mycc.setproperty('PLDOE',int(round(rowdev.iloc[0]['PLDOE'],0)))
    if not str(rowdev.iloc[0]['LF1D']) in ['nan','NaT']:
        mycc.setproperty('LF1D',rowdev.iloc[0]['LF1D'].strftime('%m/%d/%Y'))
    if not str(rowdev.iloc[0]['ADAT']) in ['nan','NaT']:
        mycc.setproperty('ADAT',rowdev.iloc[0]['ADAT'].strftime('%m/%d/%Y'))
    if not math.isnan(rowdev.iloc[0]['ADOY']):
        mycc.setproperty('ADOY',int(round(rowdev.iloc[0]['ADOY'],0)))
    found = False
    for plot in plots:
        if plot.plt_label == cc_label[:3]:
            plot.addccid(mycc.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for crop canopy %s' % cc_label)
    crpcns.append(mycc)
########################################################################

########################################################################
#Soil Analysis
shapefile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDF',skiprows=1)
sas = list()
for feature in layer:
    said = feature.GetField('ObjectID')
    sa_label = feature.GetField('Core')  #(e.g., p01)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mysa = soilanalysis.SoilAnalysis(said=said,geometry=geometry,sa_label=sa_label)
    #Soil analysis data
    items={'SLPHW':1,'SLPHB':1,'SLEC':2,'SLOM':1,'SNO3':1,'SLPX':1,
           'SLKE':0,'SLSU':1,'SLZN':2,'SLFE':1,'SLMN':1,'SLCU':2,
           'SLCA':0,'SLMG':0,'SLNA':0,'SLCEC':1}
    for item in items.keys():
        sadata = dict()
        saitem = dict()
        for depth in [20,60,100,140,180]:
            row = sa[(sa['Plot'] == sa_label) & (sa['Depth'] == depth)]
            if not math.isnan(row.iloc[0][item]):
                if items[item] > 0:
                    saitem.update({depth:round(row.iloc[0][item],items[item])})
                else:
                    saitem.update({depth:int(row.iloc[0][item])})
        key = '{:04d}{:03d}'.format(row.iloc[0]['Year'],row.iloc[0]['DOY'])
        if saitem:
            sadata.update({key:saitem})
        if sadata:
            mysa.setproperty(item,sadata)
    found = False
    for plot in plots:
        if plot.plt_label == sa_label[:3]:
            plot.addsaid(mysa.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for soil analysis %s' % sa_label)
    sas.append(mysa)
########################################################################

########################################################################
#Write geojson files
fc = geojson.FeatureCollection([myexp.doc])
with open('../geojson/'+fname+'/'+fname+'_experiment.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myplot in plots:
    features.append(myplot.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_plots.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myzone in zones:
    features.append(myzone.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_zones.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myha in hareas:
    features.append(myha.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_harvestareas.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mytube in tubes:
    features.append(mytube.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_neutronswc.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mycrpcn in crpcns:
    features.append(mycrpcn.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_cropcanopy.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mysa in sas:
    features.append(mysa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_soilanalysis.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
