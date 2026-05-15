import os
import sys
import math
import experiment
import plot
import zone
import cropharvest
import soilwatercontent
import cropcanopy
import plantanalysis
import pandas as pd
from osgeo import ogr
import geojson
from datetime import datetime

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
myexp.setproperty('FAREA',round(exp_area,6))

expmeta = {
    'EXNAME':'Field-scale remote sensing-based irrigation scheduling, Season 1 of 2',
    'OBJECTIVES':'See Hunsaker, D. J., French, A. N., Waller, P. M., Bautista, E., Thorp, K. R., Bronson, K. F., Andrade-Sanchez, P., 2015. Comparison of traditional and ET-based irrigation scheduling of surface-irrigated cotton in the arid southwestern USA. Agricultural Water Management 159, 209-224. doi:10.1016/j.agwat.2015.06.016',
    'EXP_NARR':'See Hunsaker, D. J., French, A. N., Waller, P. M., Bautista, E., Thorp, K. R., Bronson, K. F., Andrade-Sanchez, P., 2015. Comparison of traditional and ET-based irrigation scheduling of surface-irrigated cotton in the arid southwestern USA. Agricultural Water Management 159, 209-224. doi:10.1016/j.agwat.2015.06.016',
    'MAIN_FACTOR':'Irrigation scheduling method: ET-based soil water balance and remote sensing-based methods',
    'FACTORS':'Four irrigation scheduling methods',
    'TRT_COUNT':4,
    'REP_NO':4,
    'METHODS':'See Hunsaker, D. J., French, A. N., Waller, P. M., Bautista, E., Thorp, K. R., Bronson, K. F., Andrade-Sanchez, P., 2015. Comparison of traditional and ET-based irrigation scheduling of surface-irrigated cotton in the arid southwestern USA. Agricultural Water Management 159, 209-224. doi:10.1016/j.agwat.2015.06.016',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 33',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2009',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton on raised beds with furrow flood irrigation after fallow',
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
#Plot
shapefile = '../Data/'+fname+'/'+fname+'_Plot.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
#spref = layer.GetSpatialRef()
#epsg = spref.GetAttrValue('AUTHORITY',1)
#lyrdef = plotlyr.GetLayerDefn()
#for i in list(range(lyrdef.GetFieldCount())):
#    print(lyrdef.GetFieldDefn(i).GetName())
yfile = '../Data/'+fname+'/'+fname+'_CropHarvest.xlsx'
yld = pd.read_excel(yfile,sheet_name='Plot Scale',skiprows=5)
dfile = '../Data/'+fname+'/'+fname+'_CropCanopy.xlsx'
develop = pd.read_excel(dfile,sheet_name='PlotDevelop')
mfile = '../Data/'+fname+'/'+fname+'_Management.xlsx'
irrig = pd.read_excel(mfile,sheet_name='IrrigationDF')
rsfile = '../Data/'+fname+'/'+fname+'_RS.xlsx'
ndvi = pd.read_excel(rsfile,sheet_name='PlotNDVI')
lst = pd.read_excel(rsfile,sheet_name='PlotLST')
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilPlot')
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
    myplot.setproperty('PLTA',round(plt_area,6))
    #Management information
    myplot.setproperty('CUL_NAME', 'Deltapine 1044 B2RF')
    myplot.setproperty('PDATE', '2009-04-22')
    myplot.setproperty('PLYR', 2009)
    myplot.setproperty('PLDAY', 112)
    myplot.setproperty('IROP', 'IR001')
    idata = list()
    idata.append({'date':'2009-03-12','value':300.0}) #Prewater
    idata.append({'date':'2009-04-06','value':100.0}) #Prewater
    row = irrig[irrig['PlotID'] == plt_label]
    for i in range(1,10):
        IrrDOY = row.iloc[0]['IrrDOY'+str(i)]
        IRVAL = float(row.iloc[:]['IrrRate'+str(i)].mean())
        key = '2009'+'{:03d}'.format(int(IrrDOY))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if round(IRVAL,1) > 0.0:
            idata.append({'date':date,'value':round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = list()
    fdata.append({'date':'2009-06-01','value':56.0})
    myplot.setproperty('FEAMN',fdata)
    cdata = list()
    cdata.append({'date':'2009-06-24','value':'Apply Pix Plus (mepiquat chloride)'})
    cdata.append({'date':'2009-06-24','value':'Apply Layby Pro (linuron, diuron)'})
    cdata.append({'date':'2009-07-11','value':'Apply insecticide (whitefly)'})
    cdata.append({'date':'2009-08-08','value':'Apply Carbine (flonicamid)'})
    cdata.append({'date':'2009-08-28','value':'Apply insecticide (whitefly)'})
    cdata.append({'date':'2009-09-25','value':'Apply Ginstar (diuron, thidiazuron)'})
    cdata.append({'date':'2009-10-09','value':'Apply defoliant'})
    cdata.append({'date':'2009-10-11','value':'Apply defoliant'})
    myplot.setproperty('CH_NOTES',cdata)
    tdata = list()
    tdata.append({'date':'2009-03','value':'Laser level, raise beds'})
    tdata.append({'date':'2009-04-17','value':'Rotary hoe'})
    tdata.append({'date':'2009-04-21','value':'Mulch beds'})
    tdata.append({'date':'2009-05-14','value':'Field cultivator'})
    tdata.append({'date':'2009-06-01','value':'Field cultivator'})
    tdata.append({'date':'2009-06-24','value':'Field cultivator'})
    tdata.append({'date':'2009-11-09','value':'Shredder'})
    myplot.setproperty('TI_NOTES',tdata)
    #Crop Development
    row = develop.loc[develop['Plot'] == plt_label]
    if not row.empty:
        if not str(row.iloc[0]['EDATE']) in ['nan','NaT']:
            myplot.setproperty('EDATE',row.iloc[0]['EDATE'].strftime('%Y-%m-%d'))
        if not math.isnan(row.iloc[0]['PLYRE']):
            myplot.setproperty('PLYRE',int(row.iloc[0]['PLYRE']))
        if not math.isnan(row.iloc[0]['PLDOE']):
            myplot.setproperty('PLDOE',int(round(row.iloc[0]['PLDOE'],0)))
        if not str(row.iloc[0]['ADAT']) in ['nan','NaT']:
            myplot.setproperty('ADAT',row.iloc[0]['ADAT'].strftime('%Y-%m-%d'))
        if not math.isnan(row.iloc[0]['ADOY']):
            myplot.setproperty('ADOY',int(round(row.iloc[0]['ADOY'],0)))
        nawf = list()
        for doy in ['219','226','230']:
            key = '2009'+doy
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(row.iloc[0]['NAWF'+doy]):
                nawf.append({'date':date,'value':round(float(row.iloc[0]['NAWF'+doy]),1)})
        if nawf:
            myplot.setproperty('NAWF',nawf)
    #Remote sensing NDVI and land surface temperature (LST)
    ndvidata = list()
    row = ndvi.loc[ndvi['Plot'] == plt_label]
    doycols = sorted([col for col in ndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            ndvidata.append({'date':date,'value':round(NDVImean,3)})
    if ndvidata:
        myplot.setproperty('RSNDVI',ndvidata)
    lstdata = list()
    row = lst.loc[lst['Plot'] == plt_label]
    doycols = sorted([col for col in lst.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            LSTmean = float(row.iloc[0][doycol])
            lstdata.append({'date':date,'value':round(LSTmean,1)})
    if lstdata:
        myplot.setproperty('RSLST',lstdata)
    #Soil physical analysis
    row = soil.loc[soil['Plot'] == plt_label]
    em38h = list()
    if not math.isnan(row.iloc[0]['2009d079EM38H']):
        em38h.append({'date':'2009-03-20','value':round(row.iloc[0]['2009d079EM38H'],2)})
    if em38h:
        myplot.setproperty('EM38H',em38h)
    em38v = list()
    if not math.isnan(row.iloc[0]['2009d079EM38V']):
        em38v.append({'date':'2009-03-20','value':round(row.iloc[0]['2009d079EM38V'],2)})
    if em38v:
        myplot.setproperty('EM38V',em38v)
    slsnd = list()
    slslt = list()
    slcly = list()
    slwp1 = list()
    slwp2 = list()
    slfc1 = list()
    for depth in ['015','045','075','105','135','165','210']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLWP1'+depth]):
            slwp1.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLWP1'+depth],3)})
        if not math.isnan(row.iloc[0]['SLWP2'+depth]):
            slwp2.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLWP2'+depth],3)})
        if not math.isnan(row.iloc[0]['SLFC1'+depth]):
            slfc1.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLFC1'+depth],3)})
    if slsnd: myplot.setproperty('SLSND_M',slsnd)
    if slslt: myplot.setproperty('SLSLT_M',slslt)
    if slcly: myplot.setproperty('SLCLY_M',slcly)
    if slwp1: myplot.setproperty('SLWP',slwp1)
    if slwp2: myplot.setproperty('SLWP2',slwp2)
    if slfc1: myplot.setproperty('SLFC1',slfc1)
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myplot.setproperty('HARM'  ,row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myplot.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%Y-%m-%d'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myplot.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not str(row.iloc[0]['GNDAT']) in ['nan','NaT']:
        myplot.setproperty('GNDAT' ,row.iloc[0]['GNDAT'].strftime('%Y-%m-%d'))
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
#Zone
shapefile = '../Data/'+fname+'/'+fname+'_Zone.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_CropHarvest.xlsx'
yld = pd.read_excel(yfile,sheet_name='Zone Scale',skiprows=5)
mfile = '../Data/'+fname+'/'+fname+'_Management.xlsx'
irrig = pd.read_excel(mfile,sheet_name='IrrigationDF')
rsfile = '../Data/'+fname+'/'+fname+'_RS.xlsx'
ndvi = pd.read_excel(rsfile,sheet_name='ZoneNDVI')
lst = pd.read_excel(rsfile,sheet_name='ZoneLST')
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilZone')
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
    idata = list()
    idata.append({'date':'2009-03-12','value':300.0}) #Prewater
    idata.append({'date':'2009-04-06','value':100.0}) #Prewater
    row = irrig[irrig['ZoneID'] == zon_label]
    for i in range(1,10):
        IrrDOY = row.iloc[0]['IrrDOY'+str(i)]
        IRVAL = float(row.iloc[0]['IrrRate'+str(i)])
        key = '2009'+'{:03d}'.format(int(IrrDOY))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if round(IRVAL,1) > 0.0:
            idata.append({'date':date,'value':round(IRVAL,1)})
    if idata:
        myzone.setproperty('IRVAL',idata)
    #Remote sensing NDVI and land surface temperature (LST)
    ndvidata = list()
    row = ndvi.loc[ndvi['ZoneID'] == zon_label]
    doycols = sorted([col for col in ndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            ndvidata.append({'date':date,'value':round(NDVImean,3)})
    if ndvidata:
        myzone.setproperty('RSNDVI',ndvidata)
    lstdata = list()
    row = lst.loc[lst['ZoneID'] == zon_label]
    doycols = sorted([col for col in lst.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            LSTmean = float(row.iloc[0][doycol])
            lstdata.append({'date':date,'value':round(LSTmean,1)})
    if lstdata:
        myzone.setproperty('RSLST',lstdata)
    #Soil physical analysis
    row = soil.loc[soil['ZoneID'] == zon_label]
    em38h = list()
    if not math.isnan(row.iloc[0]['2009d079EM38H']):
        em38h.append({'date':'2009-03-20','value':round(row.iloc[0]['2009d079EM38H'],2)})
    if em38h:
        myzone.setproperty('EM38H',em38h)
    em38v = list()
    if not math.isnan(row.iloc[0]['2009d079EM38V']):
        em38v.append({'date':'2009-03-20','value':round(row.iloc[0]['2009d079EM38V'],2)})
    if em38v:
        myzone.setproperty('EM38V',em38v)
    slsnd = list()
    slslt = list()
    slcly = list()
    slwp1 = list()
    slwp2 = list()
    slfc1 = list()
    for depth in ['015','045','075','105','135','165','210']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLWP1'+depth]):
            slwp1.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLWP1'+depth],3)})
        if not math.isnan(row.iloc[0]['SLWP2'+depth]):
            slwp2.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLWP2'+depth],3)})
        if not math.isnan(row.iloc[0]['SLFC1'+depth]):
            slfc1.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLFC1'+depth],3)})
    if slsnd: myzone.setproperty('SLSND_M',slsnd)
    if slslt: myzone.setproperty('SLSLT_M',slslt)
    if slcly: myzone.setproperty('SLCLY_M',slcly)
    if slwp1: myzone.setproperty('SLWP',slwp1)
    if slwp2: myzone.setproperty('SLWP2',slwp2)
    if slfc1: myzone.setproperty('SLFC1',slfc1)
    #Yield data
    row = yld.loc[yld['ZID'] == zon_label]
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myzone.setproperty('HARM'  ,row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myzone.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%Y-%m-%d'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myzone.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not str(row.iloc[0]['GNDAT']) in ['nan','NaT']:
        myzone.setproperty('GNDAT' ,row.iloc[0]['GNDAT'].strftime('%Y-%m-%d'))
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
#Crop Harvest
shapefile = '../Data/'+fname+'/'+fname+'_CropHarvest.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_CropHarvest.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=32)
rsfile = '../Data/'+fname+'/'+fname+'_RS.xlsx'
ndvi = pd.read_excel(rsfile,sheet_name='HANDVI')
lst = pd.read_excel(rsfile,sheet_name='HALST')
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
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
    myha = cropharvest.CropHarvest(haid=haid,geometry=geometry,ha_label=ha_label)
    myha.setproperty('HAREA',round(ha_area,6))
    #Yield and fiber quality data
    row = yld.loc[yld['HID'] == ha_label]
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myha.setproperty('HARM',row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myha.setproperty('HADAT',row.iloc[0]['HADAT'].strftime('%Y-%m-%d'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myha.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not str(row.iloc[0]['GNDAT']) in ['nan','NaT']:
        myha.setproperty('GNDAT',row.iloc[0]['GNDAT'].strftime('%Y-%m-%d'))
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
    ndvidata = list()
    row = ndvi.loc[ndvi['HID'] == ha_label]
    doycols = sorted([col for col in ndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            ndvidata.append({'date':date,'value':round(NDVImean,3)})
    if ndvidata:
        myha.setproperty('RSNDVI',ndvidata)
    lstdata = list()
    row = lst.loc[lst['HID'] == ha_label]
    doycols = sorted([col for col in lst.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            LSTmean = float(row.iloc[0][doycol])
            lstdata.append({'date':date,'value':round(LSTmean,1)})
    if lstdata:
        myha.setproperty('RSLST',lstdata)
    #Soil physical analysis
    row = soil.loc[soil['HID'] == ha_label]
    em38h = list()
    if not math.isnan(row.iloc[0]['2009d079EM38H']):
        em38h.append({'date':'2009-03-20','value':round(row.iloc[0]['2009d079EM38H'],2)})
    if em38h:
        myha.setproperty('EM38H',em38h)
    em38v = list()
    if not math.isnan(row.iloc[0]['2009d079EM38V']):
        em38v.append({'date':'2009-03-20','value':round(row.iloc[0]['2009d079EM38V'],2)})
    if em38v:
        myha.setproperty('EM38V',em38v)
    slsnd = list()
    slslt = list()
    slcly = list()
    slwp1 = list()
    slwp2 = list()
    slfc1 = list()
    for depth in ['015','045','075','105','135','165','210']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLWP1'+depth]):
            slwp1.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLWP1'+depth],3)})
        if not math.isnan(row.iloc[0]['SLWP2'+depth]):
            slwp2.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLWP2'+depth],3)})
        if not math.isnan(row.iloc[0]['SLFC1'+depth]):
            slfc1.append({'depth':int(depth),
                          'mindepth':int(depth)-15,
                          'maxdepth':int(depth)+15,
                          'value':round(row.iloc[0]['SLFC1'+depth],3)})
    if slsnd: myha.setproperty('SLSND_M',slsnd)
    if slslt: myha.setproperty('SLSLT_M',slslt)
    if slcly: myha.setproperty('SLCLY_M',slcly)
    if slwp1: myha.setproperty('SLWP',slwp1)
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
#Soil Water Content
shapefile = '../Data/'+fname+'/'+fname+'_SoilWaterContent.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
swcfile = '../Data/'+fname+'/'+fname+'_SoilWaterContent.xlsx'
swc = pd.read_excel(swcfile,sheet_name='Summary')
tubes = list()
for feature in layer:
    tid = feature.GetField('ObjectId')
    tb_label = str(feature.GetField('Tube')) #(e.g., p01-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in neutronSWC shapefile.')
        sys.exit()
    mytube = soilwatercontent.SoilWaterContent(tid=tid,geometry=geometry,tb_label=tb_label)
    #Neutron soil water content data
    rows = swc.loc[swc['Tube'] == tb_label]
    rows = rows.sort_values(by='DOY')
    depcols = sorted([col for col in rows.columns if col[-2:]=='cm'])
    swcdata = list()
    for i, row in rows.iterrows():
        for depcol in depcols:
            if not math.isnan(row.loc[depcol]):
                depth = int(depcol[1:-2])
                key = '{:04d}{:03d}'.format(row.loc['Year'],row.loc['DOY'])
                date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
                swcdata.append({'date':date,
                                'type':'NP',
                                'depth':depth,
                                'mindepth':depth-10,
                                'maxdepth':depth+10,
                                'value':round(row.loc[depcol],3)})
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
ccl = pd.read_excel(ccfile,sheet_name='LAImeter')
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
    htdata = list()
    rowh = cch.loc[cch['CCID'] == cc_label]
    doycols = sorted([col for col in cch.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(rowh.iloc[0][doycol]):
            CHTD = float(rowh.iloc[0][doycol])/100. #m
            htdata.append({'date':date,'value':round(CHTD,2)})
    if htdata:
        mycc.setproperty('CHTD',htdata)
    wddata = list()
    roww = ccw.loc[ccw['CCID'] == cc_label]
    doycols = sorted([col for col in ccw.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2009'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(roww.iloc[0][doycol]):
            CWID = float(roww.iloc[0][doycol])/100. #m
            wddata.append({'date':date,'value':round(CWID,2)})
    if wddata:
        mycc.setproperty('CWID',wddata)
    laidata = list()
    rowl = ccl.loc[ccl['CCID'] == cc_label]
    if not rowl.empty:
        doycols = sorted([col for col in ccl.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2009'+'{:03d}'.format(int(doycol[3:]))
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(rowl.iloc[0][doycol]):
                LAID = float(rowl.iloc[0][doycol])
                laidata.append({'date':date,'value':round(LAID,2)})
        if laidata:
            mycc.setproperty('LAID_FLD',laidata)
    rowden = ccden.loc[ccden['CCID'] == cc_label]
    if not rowden.empty:
        if not math.isnan(rowden.iloc[0]['PLPD']):
            PLPD = float(rowden.iloc[0]['PLPD'])
            mycc.setproperty('PLPD',round(PLPD,1))
    rowdev = ccdev.loc[ccdev['CCID'] == cc_label]
    if not rowdev.empty:
        nawf = list()
        for doy in ['219','226','230']:
            key = '2009'+doy
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(rowdev.iloc[0]['NAWF'+doy]):
                nawf.append({'date':date,'value':round(float(rowdev.iloc[0]['NAWF'+doy]),1)})
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
        mypa.setproperty('PSDATE',row.iloc[0]['PSDATE'].strftime('%Y-%m-%d'))
    items={'SQRNUM':1,'FLRNUM':1,'GBNUM':1,'MBNUM':1,
           'LWPD':2,'SWPD':2,'CWPD':2,'LWAD':1,'SWAD':1,'PWAD':1,
           'CWAD':1,'LAID_LAB':3}
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
#Soil Physical Analysis
shapefile = '../Data/Soil/F033_SoilPhysicalAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
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
            raise Exception('Did not find plot for soil physical analysis %s' % sa_label)
########################################################################

########################################################################
#Write geojson files
directory = '../geojson/'+fname
for filename in os.listdir(directory):
    if filename.endswith('.geojson'):
        file_path = os.path.join(directory,filename)
        os.remove(file_path)

fc = geojson.FeatureCollection([myexp.doc])
with open('../geojson/'+fname+'/'+fname+'_Experiment.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myplot in plots:
    features.append(myplot.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_Plot.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myzone in zones:
    features.append(myzone.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_Zone.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for myha in hareas:
    features.append(myha.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_CropHarvest.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
for mytube in tubes:
    features.append(mytube.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_SoilWaterContent.geojson','w') as f:
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
########################################################################
