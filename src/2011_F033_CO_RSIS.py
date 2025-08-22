import os
import sys
import math
import experiment
import plot
import zone
import harvestarea
import neutronswc
import cropcanopy
import plantanalysis
import soilchemistry
import pandas as pd
from osgeo import ogr
import geojson

fname = os.path.basename(__file__)
fname = os.path.splitext(fname)[0]

numtrt = 4
numrep = 4

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
    'EXNAME':'Field-scale remote sensing-based irrigation scheduling, Season 2 of 2',
    'OBJECTIVES':'See Hunsaker, D. J., French, A. N., Waller, P. M., Bautista, E., Thorp, K. R., Bronson, K. F., Andrade-Sanchez, P., 2015. Comparison of traditional and ET-based irrigation scheduling of surface-irrigated cotton in the arid southwestern USA. Agricultural Water Management 159, 209-224. doi:10.1016/j.agwat.2015.06.016',
    'EXP_NARR':'See Hunsaker, D. J., French, A. N., Waller, P. M., Bautista, E., Thorp, K. R., Bronson, K. F., Andrade-Sanchez, P., 2015. Comparison of traditional and ET-based irrigation scheduling of surface-irrigated cotton in the arid southwestern USA. Agricultural Water Management 159, 209-224. doi:10.1016/j.agwat.2015.06.016',
    'MAIN_FACTOR':'Irrigation scheduling method: ET-based soil water balance and remote sensing-based methods',
    'FACTORS':'Four irrigation scheduling methods',
    'TRT_NO':4,
    'REP_NO':4,
    'METHODS':'See Hunsaker, D. J., French, A. N., Waller, P. M., Bautista, E., Thorp, K. R., Bronson, K. F., Andrade-Sanchez, P., 2015. Comparison of traditional and ET-based irrigation scheduling of surface-irrigated cotton in the arid southwestern USA. Agricultural Water Management 159, 209-224. doi:10.1016/j.agwat.2015.06.016',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 33',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2011',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton after fallow',
    'LAST_NAME':'Hunsaker',
    'FIRST_NAME':'Douglas',
    'MID_INITIAL':'J',
    'PERSON_NOTES':'Field technicians: Tom Clarke, Dick Simer, Suzette Maneely, and Bill Luckett',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'doug.hunsaker@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'',
    'SUITE_NAME':'Field-scale remote sensing-based irrigation scheduling',
    'SUITE_OBJ':'See Hunsaker, D. J., French, A. N., Waller, P. M., Bautista, E., Thorp, K. R., Bronson, K. F., Andrade-Sanchez, P., 2015. Comparison of traditional and ET-based irrigation scheduling of surface-irrigated cotton in the arid southwestern USA. Agricultural Water Management 159, 209-224. doi:10.1016/j.agwat.2015.06.016',
    'FL_NAME':'Field 33',
    'FL_LAT':33.074142, #from Google maps
    'FL_LONG':-111.991038, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'MAC':'Irrigation schedule used by the local farm manager',
            'FAO':'Irrigation scheduling via a spatial ET-based FAO56 soil water balance model with mean 45%% management allowed depletion among zones',
            'VI_A':'Irrigation scheduling via a spatial ET-based FAO56 soil water balance model with Kcb from NDVI and mean 45%% management allowed depletion among zones',
            'VI_B':'Irrigation scheduling via a spatial ET-based FAO56 soil water balance model with Kcb from NDVI and 5%% of zones at 65%% management allowed depletion'}

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
rsfile = '../Data/'+fname+'/'+fname+'_RS.xlsx'
ndvi = pd.read_excel(rsfile,sheet_name='PlotsNDVI')
lst = pd.read_excel(rsfile,sheet_name='PlotsLST')
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilPlots')
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
    myplot.setproperty('CUL_NAME', 'Deltapine 1044 B2RF')
    if int(plt_label[1:3]) in range(12,17):
        myplot.setproperty('PDATE', '04/19/2011')
        myplot.setproperty('PLYR', 2011)
        myplot.setproperty('PLDAY', 109)
    if int(plt_label[1:3]) in range(1,12):
        myplot.setproperty('PDATE', '04/20/2011')
        myplot.setproperty('PLYR', 2011)
        myplot.setproperty('PLDAY', 110)
    fdata = dict()
    fdata.update({'2011151':56.0})
    myplot.setproperty('FEAMN',fdata)
    cdata = dict()
    cdata.update({'2011181':'Apply layby herbicide'})
    cdata.update({'2011200':'Apply insecticide'})
    cdata.update({'2011205':'Apply insecticide'})
    cdata.update({'2011257':'Apply Ginstar (diuron, thidiazuron) and Finish (ethephon, cyclanilide)'})
    cdata.update({'2011277':'Apply sodium chlorate'})
    cdata.update({'2011280':'Apply paraquat'})
    myplot.setproperty('CH_NOTES',cdata)
    tdata = dict()
    tdata.update({'2011053':'Disk'})
    tdata.update({'2011054':'Rip'})
    tdata.update({'2011057':'Moldboard plow'})
    tdata.update({'2011068':'Laser level'})
    tdata.update({'2011081':'Raise beds'})
    tdata.update({'2011102':'Field cultivator'})
    tdata.update({'2011104':'Mulch beds'})
    tdata.update({'2011129':'Field cultivator'})
    myplot.setproperty('TI_NOTES',tdata)
    #Remote sensing NDVI and land surface temperature (LST)
    ndvidata = dict()
    row = ndvi.loc[ndvi['Plot'] == plt_label]
    doycols = sorted([col for col in ndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2011'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            ndvidata.update({key:round(NDVImean,3)})
    if ndvidata:
        myplot.setproperty('RSNDVI',ndvidata)
    lstdata = dict()
    row = lst.loc[lst['Plot'] == plt_label]
    doycols = sorted([col for col in lst.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2011'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            LSTmean = float(row.iloc[0][doycol])
            lstdata.update({key:round(LSTmean,1)})
    if lstdata:
        myplot.setproperty('RSLST',lstdata)
    #Soil analysis
    row = soil.loc[soil['Plot'] == plt_label]
    em38h = dict()
    if not math.isnan(row.iloc[0]['2009d079EM38H']):
        em38h.update({'2009079':round(row.iloc[0]['2009d079EM38H'],2)})
    if em38h:
        myplot.setproperty('EM38H',em38h)
    em38v = dict()
    if not math.isnan(row.iloc[0]['2009d079EM38V']):
        em38v.update({'2009079':round(row.iloc[0]['2009d079EM38V'],2)})
    if em38v:
        myplot.setproperty('EM38V',em38v)
    slsnd = dict()
    slslt = dict()
    slcly = dict()
    slwp1 = dict()
    slwp2 = dict()
    slfc1 = dict()
    for depth in ['015','045','075','105','135','165','210']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd.update({int(depth):round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt.update({int(depth):round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly.update({int(depth):round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLWP1'+depth]):
            slwp1.update({int(depth):round(row.iloc[0]['SLWP1'+depth],3)})
        if not math.isnan(row.iloc[0]['SLWP2'+depth]):
            slwp2.update({int(depth):round(row.iloc[0]['SLWP2'+depth],3)})
        if not math.isnan(row.iloc[0]['SLFC1'+depth]):
            slfc1.update({int(depth):round(row.iloc[0]['SLFC1'+depth],3)})
    if slsnd: myplot.setproperty('SLSND',slsnd)
    if slslt: myplot.setproperty('SLSLT',slslt)
    if slcly: myplot.setproperty('SLCLY',slcly)
    if slwp1: myplot.setproperty('SLWP1',slwp1)
    if slwp2: myplot.setproperty('SLWP2',slwp2)
    if slfc1: myplot.setproperty('SLFC1',slfc1)
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myplot.setproperty('HARM'  ,row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myplot.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myplot.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
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
    plots.append(myplot)
########################################################################

########################################################################
#Zones
shapefile = '../Data/'+fname+'/'+fname+'_Zones2.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Zone Scale',skiprows=5)
mfile = '../Data/'+fname+'/'+fname+'_Management.xlsx'
irrig = pd.read_excel(mfile,sheet_name='IrrigationDF')
rsfile = '../Data/'+fname+'/'+fname+'_RS.xlsx'
ndvi = pd.read_excel(rsfile,sheet_name='Zones2NDVI')
lst = pd.read_excel(rsfile,sheet_name='Zones2LST')
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilZones2')
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
        print('Unexpected spatial reference in zone shapefile.')
        sys.exit()
    zon_area = geometry.GetArea()
    myzone = zone.Zone(zid=zid,geometry=geometry,zon_label=zon_label)
    myzone.setproperty('ZON_AREA',round(zon_area,6))
    #Management information
    myzone.setproperty('IROP', 'IR001')
    idata = dict()
    idata.update({'2011090':300.0}) #Prewater
    row = irrig[irrig['ZoneID'] == zon_label]
    for i in range(1,10):
        IrrDOY = row.iloc[0]['IrrDOY'+str(i)]
        IRVAL = float(row.iloc[0]['IrrRate'+str(i)])
        key = '2011'+'{:03d}'.format(int(IrrDOY))
        if round(IRVAL,1) > 0.0:
            idata.update({key:round(IRVAL,1)})
    if idata:
        myzone.setproperty('IRVAL',idata)
    #Remote sensing NDVI and land surface temperature (LST)
    ndvidata = dict()
    row = ndvi.loc[ndvi['ZoneID'] == zon_label]
    doycols = sorted([col for col in ndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2011'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            ndvidata.update({key:round(NDVImean,3)})
    if ndvidata:
        myzone.setproperty('RSNDVI',ndvidata)
    lstdata = dict()
    row = lst.loc[lst['ZoneID'] == zon_label]
    doycols = sorted([col for col in lst.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2011'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            LSTmean = float(row.iloc[0][doycol])
            lstdata.update({key:round(LSTmean,1)})
    if lstdata:
        myzone.setproperty('RSLST',lstdata)
    #Soil analysis
    row = soil.loc[soil['ZoneID'] == zon_label]
    em38h = dict()
    if not math.isnan(row.iloc[0]['2009d079EM38H']):
        em38h.update({'2009079':round(row.iloc[0]['2009d079EM38H'],2)})
    if em38h:
        myzone.setproperty('EM38H',em38h)
    em38v = dict()
    if not math.isnan(row.iloc[0]['2009d079EM38V']):
        em38v.update({'2009079':round(row.iloc[0]['2009d079EM38V'],2)})
    if em38v:
        myzone.setproperty('EM38V',em38v)
    slsnd = dict()
    slslt = dict()
    slcly = dict()
    slwp1 = dict()
    slwp2 = dict()
    slfc1 = dict()
    for depth in ['015','045','075','105','135','165','210']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd.update({int(depth):round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt.update({int(depth):round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly.update({int(depth):round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLWP1'+depth]):
            slwp1.update({int(depth):round(row.iloc[0]['SLWP1'+depth],3)})
        if not math.isnan(row.iloc[0]['SLWP2'+depth]):
            slwp2.update({int(depth):round(row.iloc[0]['SLWP2'+depth],3)})
        if not math.isnan(row.iloc[0]['SLFC1'+depth]):
            slfc1.update({int(depth):round(row.iloc[0]['SLFC1'+depth],3)})
    if slsnd: myzone.setproperty('SLSND',slsnd)
    if slslt: myzone.setproperty('SLSLT',slslt)
    if slcly: myzone.setproperty('SLCLY',slcly)
    if slwp1: myzone.setproperty('SLWP1',slwp1)
    if slwp2: myzone.setproperty('SLWP2',slwp2)
    if slfc1: myzone.setproperty('SLFC1',slfc1)
    #Yield data
    row = yld.loc[yld['ZID'] == zon_label]
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myzone.setproperty('HARM'  ,row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myzone.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myzone.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not str(row.iloc[0]['GNDAT']) in ['nan','NaT']:
        myzone.setproperty('GNDAT' ,row.iloc[0]['GNDAT'].strftime('%m/%d/%Y'))
    if not math.isnan(row.iloc[0]['FFRAC']):
        myzone.setproperty('FFRAC' ,round(row.iloc[0]['FFRAC' ],4))
    if not math.isnan(row.iloc[0]['SFRAC']):
        myzone.setproperty('SFRAC' ,round(row.iloc[0]['SFRAC' ],4))
    if not math.isnan(row.iloc[0]['TFRAC']):
        myzone.setproperty('TFRAC' ,round(row.iloc[0]['TFRAC' ],4))
    if not math.isnan(row.iloc[0]['WFWAH']):
        myzone.setproperty('WFWAH' ,round(row.iloc[0]['WFWAH' ],1))
    if not math.isnan(row.iloc[0]['WSWAH']):
        myzone.setproperty('WSWAH' ,round(row.iloc[0]['WSWAH' ],1))
    if not math.isnan(row.iloc[0]['WSCWAH']):
        myzone.setproperty('WSCWAH',round(row.iloc[0]['WSCWAH'],1))
    found=False
    for plot in plots:
        if plot.plt_label == zon_label[:3]:
            plot.addzid(myzone.getid())
            found=True
            break
    if not found:
        raise Exception('Did not find plot for zone %s' % zon_label)
    zones.append(myzone)
########################################################################

########################################################################
#Harvest Areas
shapefile = '../Data/'+fname+'/'+fname+'_HarvestAreas.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=32)
rsfile = '../Data/'+fname+'/'+fname+'_RS.xlsx'
ndvi = pd.read_excel(rsfile,sheet_name='HANDVI')
lst = pd.read_excel(rsfile,sheet_name='HALST')
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p01-01)
    geometry = feature.GetGeometryRef()
    geomcount = geometry.GetGeometryCount()
    nodecount = geometry.GetGeometryRef(0).GetPointCount()
    if geomcount != 1 or nodecount != 5:
        print('Polygons should have one geometry and five nodes.')
        sys.exit()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in harvest area shapefile.')
        sys.exit()
    ha_area = geometry.GetArea()
    myha = harvestarea.HarvestArea(haid=haid,geometry=geometry,ha_label=ha_label)
    myha.setproperty('HA_AREA',round(ha_area,6))
    #Yield and fiber quality data
    row = yld.loc[yld['HID'] == ha_label]
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
    if not math.isnan(row.iloc[0]['WFWAH']):
        myha.setproperty('WFWAH' ,round(row.iloc[0]['WFWAH' ],1))
    if not math.isnan(row.iloc[0]['WSWAH']):
        myha.setproperty('WSWAH' ,round(row.iloc[0]['WSWAH' ],1))
    if not math.isnan(row.iloc[0]['WSCWAH']):
        myha.setproperty('WSCWAH',round(row.iloc[0]['WSCWAH'],1))
    #Remote sensing NDVI and land surface temperature (LST)
    ndvidata = dict()
    row = ndvi.loc[ndvi['HID'] == ha_label]
    doycols = sorted([col for col in ndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2011'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            ndvidata.update({key:round(NDVImean,3)})
    if ndvidata:
        myha.setproperty('RSNDVI',ndvidata)
    lstdata = dict()
    row = lst.loc[lst['HID'] == ha_label]
    doycols = sorted([col for col in lst.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2011'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            LSTmean = float(row.iloc[0][doycol])
            lstdata.update({key:round(LSTmean,1)})
    if lstdata:
        myha.setproperty('RSLST',lstdata)
    #Soil analysis
    row = soil.loc[soil['HID'] == ha_label]
    em38h = dict()
    if not math.isnan(row.iloc[0]['2009d079EM38H']):
        em38h.update({'2009079':round(row.iloc[0]['2009d079EM38H'],2)})
    if em38h:
        myha.setproperty('EM38H',em38h)
    em38v = dict()
    if not math.isnan(row.iloc[0]['2009d079EM38V']):
        em38v.update({'2009079':round(row.iloc[0]['2009d079EM38V'],2)})
    if em38v:
        myha.setproperty('EM38V',em38v)
    slsnd = dict()
    slslt = dict()
    slcly = dict()
    slwp1 = dict()
    slwp2 = dict()
    slfc1 = dict()
    for depth in ['015','045','075','105','135','165','210']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd.update({int(depth):round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt.update({int(depth):round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly.update({int(depth):round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLWP1'+depth]):
            slwp1.update({int(depth):round(row.iloc[0]['SLWP1'+depth],3)})
        if not math.isnan(row.iloc[0]['SLWP2'+depth]):
            slwp2.update({int(depth):round(row.iloc[0]['SLWP2'+depth],3)})
        if not math.isnan(row.iloc[0]['SLFC1'+depth]):
            slfc1.update({int(depth):round(row.iloc[0]['SLFC1'+depth],3)})
    if slsnd: myha.setproperty('SLSND',slsnd)
    if slslt: myha.setproperty('SLSLT',slslt)
    if slcly: myha.setproperty('SLCLY',slcly)
    if slwp1: myha.setproperty('SLWP1',slwp1)
    if slwp2: myha.setproperty('SLWP2',slwp2)
    if slfc1: myha.setproperty('SLFC1',slfc1)
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
        print('Unexpected spatial reference in neutronSWC shapefile.')
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
                swcitem.update({depth:round(row.loc[depcol],3)})
        key = '{:04d}{:03d}'.format(row.loc['Year'],row.loc['DOY'])
        if swcitem:
            swcdata.update({key:swcitem})
    if swcitem:
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
ccl = pd.read_excel(ccfile,sheet_name='LAImeter')
ccs = pd.read_excel(ccfile,sheet_name='SPAD')
ccden = pd.read_excel(ccfile,sheet_name='Density')
ccdev = pd.read_excel(ccfile,sheet_name='Develop')
crpcns = list()
for feature in layer:
    ccid = feature.GetField('ObjectId')
    cc_label = feature.GetField('CCID')  #(e.g., p01-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in crop canopy shapefile.')
        sys.exit()
    mycc = cropcanopy.CropCanopy(ccid=ccid,geometry=geometry,cc_label=cc_label)
    #Crop canopy data
    htdata = dict()
    rowh = cch.loc[cch['CCID'] == cc_label]
    if not rowh.empty:
        doycols = sorted([col for col in cch.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2011'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(rowh.iloc[0][doycol]):
                CHTD = float(rowh.iloc[0][doycol])/100. #m
                htdata.update({key:round(CHTD,2)})
        if htdata:
            mycc.setproperty('CHTD',htdata)
    wddata = dict()
    roww = ccw.loc[ccw['CCID'] == cc_label]
    if not roww.empty:
        doycols = sorted([col for col in ccw.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2011'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(roww.iloc[0][doycol]):
                CWID = float(roww.iloc[0][doycol])/100. #m
                wddata.update({key:round(CWID,2)})
        if wddata:
            mycc.setproperty('CWID',wddata)
    laidata = dict()
    rowl = ccl.loc[ccl['CCID'] == cc_label]
    if not rowl.empty:
        doycols = sorted([col for col in ccl.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2011'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(rowl.iloc[0][doycol]):
                LAID = float(rowl.iloc[0][doycol])
                laidata.update({key:round(LAID,2)})
        if laidata:
            mycc.setproperty('LAIDF',laidata)
    spaddata = dict()
    rows = ccs.loc[ccs['CCID'] == cc_label]
    if not rows.empty:
        doycols = sorted([col for col in ccs.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2011'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(rows.iloc[0][doycol]):
                SPAD = float(rows.iloc[0][doycol])
                spaddata.update({key:round(SPAD,1)})
        if spaddata:
            mycc.setproperty('SPAD',spaddata)
    rowden = ccden.loc[ccden['CCID'] == cc_label]
    if not rowden.empty:
        if not math.isnan(rowden.iloc[0]['PLPD']):
            PLPD = float(rowden.iloc[0]['PLPD'])
            mycc.setproperty('PLPD',round(PLPD,1))
    rowdev = ccdev.loc[ccdev['CCID'] == cc_label]
    if not rowdev.empty:
        if not str(rowdev.iloc[0]['EDATE']) in ['nan','NaT']:
            mycc.setproperty('EDATE',rowdev.iloc[0]['EDATE'].strftime('%m/%d/%Y'))
        if not math.isnan(rowdev.iloc[0]['PLYRE']):
            mycc.setproperty('PLYRE',int(rowdev.iloc[0]['PLYRE']))
        if not math.isnan(rowdev.iloc[0]['PLDOE']):
            mycc.setproperty('PLDOE',int(round(rowdev.iloc[0]['PLDOE'],0)))
        if not str(rowdev.iloc[0]['ADAT']) in ['nan','NaT']:
            mycc.setproperty('ADAT',rowdev.iloc[0]['ADAT'].strftime('%m/%d/%Y'))
        if not math.isnan(rowdev.iloc[0]['ADOY']):
            mycc.setproperty('ADOY',int(round(rowdev.iloc[0]['ADOY'],0)))
        nawf = dict()
        for doy in ['213']:
            if not math.isnan(rowdev.iloc[0]['NAWF'+doy]):
                nawf.update({'2011'+doy:round(float(rowdev.iloc[0]['NAWF'+doy]),1)})
        if nawf:
            mycc.setproperty('NAWF',nawf)
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
#Plant Analysis
shapefile = '../Data/'+fname+'/'+fname+'_PlantAnalysis.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
pafile = '../Data/'+fname+'/'+fname+'_PlantAnalysis.xlsx'
pa = pd.read_excel(pafile,sheet_name='PlantDF')
pas = list()
for feature in layer:
    paid = feature.GetField('ObjectId')
    pa_label = feature.GetField('Sample')  #(e.g., p01-S1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plant analysis shapefile.')
        sys.exit()
    mypa = plantanalysis.PlantAnalysis(paid=paid,geometry=geometry,pa_label=pa_label)
    #Plant analysis data
    row = pa[pa['SID'] == pa_label]
    if not str(row.iloc[0]['PSDATE']) in ['nan','NaT']:
        mypa.setproperty('PSDATE',row.iloc[0]['PSDATE'].strftime('%m/%d/%Y'))
    items={'SQRNUM':1,'FLRNUM':1,'GBNUM':1,'MBNUM':1,
           'LWPD':2,'SWPD':2,'CWPD':2,'LWAD':1,'SWAD':1,'PWAD':1,
           'CWAD':1,'LAIDL':3}
    for item in items.keys():
        if not math.isnan(row.iloc[0][item]):
            value = round(float(row.iloc[0][item]),items[item])
            if items[item] == 0: value=int(value)
            mypa.setproperty(item,value)
    found = False
    for plot in plots:
        if plot.plt_label == pa_label[:3]:
            plot.addpaid(mypa.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for plant analysis %s' % pa_label)
    pas.append(mypa)
########################################################################

########################################################################
#Soil Chemistry
shapefile = '../Data/'+fname+'/'+fname+'_SoilChemistry.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
scfile = '../Data/'+fname+'/'+fname+'_SoilChemistry.xlsx'
sc = pd.read_excel(scfile,sheet_name='SoilChemDF')
scs = list()
for feature in layer:
    scid = feature.GetField('ObjectId')
    sc_label = feature.GetField('Tube')  #(e.g., p01-2)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in soil chemistry shapefile.')
        sys.exit()
    mysc = soilchemistry.SoilChemistry(scid=scid,geometry=geometry,sc_label=sc_label)
    #Soil chemistry data
    rows = sc[sc['Sample'] == sc_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysc.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%m/%d/%Y'))
    items={'SNO3':2}
    for item in items.keys():
        scdata = dict()
        for depth in [30,60,90]:
            row = sc[(sc['Sample'] == sc_label) & (sc['Depth'] == depth)]
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                scdata.update({depth:value})
        if scdata:
            mysc.setproperty(item,scdata)
    found = False
    for plot in plots:
        if plot.plt_label == sc_label[:3]:
            plot.addscid(mysc.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for soil chemistry %s' % sc_label)
    scs.append(mysc)
########################################################################

########################################################################
#Soil Analysis
shapefile = '../Data/Soil/F033_SoilAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDJH')
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2009-p01-1)
    if sa_label in sa['Core'].values:
        row = sa[sa['Core'] == sa_label]
        found = False
        for plot in plots:
            if plot.plt_label == row.iloc[0]['Plot']:
                plot.addsaid(said)
                found = True
                break
        if not found:
            raise Exception('Did not find plot for soil analysis %s' % sa_label)
########################################################################

########################################################################
#Write geojson files
fc = geojson.FeatureCollection([myexp.doc])
with open('../geojson/'+fname+'/'+fname+'_Experiment.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myplot in plots:
    features.append(myplot.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_Plots.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myzone in zones:
    features.append(myzone.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_Zones.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myha in hareas:
    features.append(myha.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_HarvestAreas.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mytube in tubes:
    features.append(mytube.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_NeutronSWC.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mycrpcn in crpcns:
    features.append(mycrpcn.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_CropCanopy.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mypa in pas:
    features.append(mypa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_PlantAnalysis.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mysc in scs:
    features.append(mysc.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_SoilChemistry.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
