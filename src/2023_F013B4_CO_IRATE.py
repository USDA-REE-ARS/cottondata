import os
import sys
import math
import experiment
import plot
import cropharvest
import soilwatercontent
import cropcanopy
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
    'EXNAME':'Irrigation rate experiment, Season 2 of 2',
    'OBJECTIVES':'Unpublished Span 7 irrigation rate study',
    'EXP_NARR':'Unpublished Span 7 irrigation rate study',
    'MAIN_FACTOR':'Irrigation rate (40%%, 60%%, 80%%, and 100%% of full irrigation)',
    'FACTORS':'Four irrigation rates initiated at flowering (40%%, 60%%, 80%%, and 100%% of full irrigation)',
    'TRT_COUNT':4,
    'REP_NO':4,
    'METHODS':'Unpublished Span 7 irrigation rate study',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2023',
    'EXP_DUR':1,
    'CR_SYSTEM':'Strip-till cotton with overhead sprinkler irrigation after winter barley cover crop',
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
    'SUITE_NAME':'Irrigation rate experiment',
    'SUITE_OBJ':'Unpublished Span 7 irrigation rate study',
    'FL_NAME':'Field 13, Bench 4, Span 7',
    'FL_LAT':33.079177, #from Google maps
    'FL_LONG':-111.978450, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'IR040':'40 percent of full irrigation rate initiated at flowering',
            'IR060':'60 percent of full irrigation rate initiated at flowering',
            'IR080':'80 percent of full irrigation rate initiated at flowering',
            'IR100':'Full irrigation rate for the entire season'}

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
mfile = '../Data/'+fname+'/'+fname+'_Management.xlsx'
irrig = pd.read_excel(mfile,sheet_name='IrrigationDF')
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='PlotCover')
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilPlot')
plots = list()
for feature in layer:
    pid = feature.GetField('ObjectId')
    plt_label = feature.GetField('Plot')
    trt_label = feature.GetField('IrrRate')
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
    myplot.setproperty('CUL_NAME', 'NexGen 3195 B3XF')
    myplot.setproperty('PDATE', '2023-04-24')
    myplot.setproperty('PLYR', 2023)
    myplot.setproperty('PLDAY', 114)
    myplot.setproperty('IROP', 'IR004')
    idata = list()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+'{:03d}'.format(int(row['DOY']))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        IRVAL = row['IRVAL'+trt_label[2:]]
        if not math.isnan(IRVAL):
            idata.append({'date':date,'value':round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = list()
    fdata.append({'date':'2023-06-07','value':51.9})
    fdata.append({'date':'2023-06-27','value':51.9})
    fdata.append({'date':'2023-07-18','value':51.9})
    myplot.setproperty('FEAMN',fdata)
    cdata = list()
    cdata.append({'date':'2023-03-27','value':'Apply RoundUp (glyphosate)'})
    cdata.append({'date':'2023-04-20','value':'Apply Acumen (pendimethalin)'})
    cdata.append({'date':'2023-05-23','value':'Apply RoundUp (glyphosate)'})
    cdata.append({'date':'2023-06-06','value':'Apply RoundUp (glyphosate)'})
    cdata.append({'date':'2023-07-24','value':'Apply Mepstar6 (mepiquat chloride)'})
    cdata.append({'date':'2023-10-09','value':'Apply Redipik (diuron, thidiazuron)'})
    cdata.append({'date':'2023-10-25','value':'Apply Redipik (diuron, thidiazuron) and CottonQuik (urea sulfate, ethephon)'})
    myplot.setproperty('CH_NOTES',cdata)
    tdata = list()
    tdata.append({'date':'2023-04-17','value':'Strip tillage'})
    tdata.append({'date':'2023-12','value':'Root pull, rip, moldboard plow, disk, and land plane'})
    myplot.setproperty('TI_NOTES',tdata)
    #UAS crop cover fraction
    fcdata = list()
    row = cover.loc[cover['PlotID'] == plt_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2023'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.append({'date':date,'value':round(FRCOV,3)})
    if fcdata:
        myplot.setproperty('FRCOV',fcdata)
    #Soil physical analysis
    row = soil.loc[soil['Plot'] == plt_label]
    em38v = list()
    if not math.isnan(row.iloc[0]['2013d260EM38V']):
        em38v.append({'date':'2013-09-17','value':round(row.iloc[0]['2013d260EM38V'],2)})
    if not math.isnan(row.iloc[0]['2015d118EM38V']):
        em38v.append({'date':'2015-04-28','value':round(row.iloc[0]['2015d118EM38V'],2)})
    if not math.isnan(row.iloc[0]['2015d119EM38V']):
        em38v.append({'date':'2015-04-29','value':round(row.iloc[0]['2015d119EM38V'],2)})
    if em38v:
        myplot.setproperty('EM38V',em38v)
    slsnd = list()
    slslt = list()
    slcly = list()
    slwp1 = list()
    slwp2 = list()
    slfc1 = list()
    for depth in ['015','045','075','105','135','165']:
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
    slsnd_KRT = list()
    slslt_KRT = list()
    slcly_KRT = list()
    slsnd2_KRT = list()
    slslt2_KRT = list()
    slcly2_KRT = list()
    for depth in ['020','060','100','140','180']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd_KRT.append({'depth':int(depth),
                              'mindepth':int(depth)-20,
                              'maxdepth':int(depth)+20,
                              'value':round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt_KRT.append({'depth':int(depth),
                              'mindepth':int(depth)-20,
                              'maxdepth':int(depth)+20,
                              'value':round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly_KRT.append({'depth':int(depth),
                              'mindepth':int(depth)-20,
                              'maxdepth':int(depth)+20,
                              'value':round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSND2'+depth]):
            slsnd2_KRT.append({'depth':int(depth),
                               'mindepth':int(depth)-20,
                               'maxdepth':int(depth)+20,
                               'value':round(row.iloc[0]['SLSND2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT2'+depth]):
            slslt2_KRT.append({'depth':int(depth),
                               'mindepth':int(depth)-20,
                               'maxdepth':int(depth)+20,
                               'value':round(row.iloc[0]['SLSLT2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY2'+depth]):
            slcly2_KRT.append({'depth':int(depth),
                               'mindepth':int(depth)-20,
                               'maxdepth':int(depth)+20,
                               'value':round(row.iloc[0]['SLCLY2'+depth],2)})
    if slsnd_KRT:  myplot.setproperty('SLSND_GBM',slsnd_KRT)
    if slslt_KRT:  myplot.setproperty('SLSLT_GBM',slslt_KRT)
    if slcly_KRT:  myplot.setproperty('SLCLY_GBM',slcly_KRT)
    if slsnd2_KRT: myplot.setproperty('SLSND_GB',slsnd2_KRT)
    if slslt2_KRT: myplot.setproperty('SLSLT_GB',slslt2_KRT)
    if slcly2_KRT: myplot.setproperty('SLCLY_GB',slcly2_KRT)
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
    row = row.astype({'FBTCT':float})
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myplot.setproperty('HARM'  ,row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myplot.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%Y-%m-%d'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myplot.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not math.isnan(row.iloc[0]['BWCAH']):
        myplot.setproperty('BWCAH' ,round(row.iloc[0]['BWCAH' ],2))
    if not math.isnan(row.iloc[0]['DBWAH']):
        myplot.setproperty('DBWAH' ,round(row.iloc[0]['DBWAH' ],1))
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
    if not math.isnan(row.iloc[0]['DFWAH']):
        myplot.setproperty('DFWAH' ,round(row.iloc[0]['DFWAH' ],1))
    if not math.isnan(row.iloc[0]['DSWAH']):
        myplot.setproperty('DSWAH' ,round(row.iloc[0]['DSWAH' ],1))
    if not math.isnan(row.iloc[0]['DSCWAH']):
        myplot.setproperty('DSCWAH',round(row.iloc[0]['DSCWAH'],1))
    if not str(row.iloc[0]['QLDAT']) in ['nan','NaT']:
        myplot.setproperty('QLDAT' ,row.iloc[0]['QLDAT'].strftime('%Y-%m-%d'))
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
    myplot.setproperty('eid',myexp.getid())
    plots.append(myplot)
########################################################################

########################################################################
#Crop Harvest
shapefile = '../Data/'+fname+'/'+fname+'_CropHarvest.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_CropHarvest.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=64)
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='HACover')
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    chid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p1-1-W)
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
    myha = cropharvest.CropHarvest(chid=chid,geometry=geometry,ha_label=ha_label)
    myha.setproperty('HAREA',round(ha_area,6))
    #Yield and fiber quality data
    row = yld.loc[yld['HID'] == ha_label]
    row = row.astype({'FBTCT':float})
    if not str(row.iloc[0]['HARM']) in ['nan','NaT']:
        myha.setproperty('HARM',row.iloc[0]['HARM'])
    if not str(row.iloc[0]['HADAT']) in ['nan','NaT']:
        myha.setproperty('HADAT',row.iloc[0]['HADAT'].strftime('%Y-%m-%d'))
    if not math.isnan(row.iloc[0]['WBWAH']):
        myha.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    if not math.isnan(row.iloc[0]['BWCAH']):
        myha.setproperty('BWCAH' ,round(row.iloc[0]['BWCAH' ],2))
    if not math.isnan(row.iloc[0]['DBWAH']):
        myha.setproperty('DBWAH' ,round(row.iloc[0]['DBWAH' ],1))
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
    if not math.isnan(row.iloc[0]['DFWAH']):
        myha.setproperty('DFWAH' ,round(row.iloc[0]['DFWAH' ],1))
    if not math.isnan(row.iloc[0]['DSWAH']):
        myha.setproperty('DSWAH' ,round(row.iloc[0]['DSWAH' ],1))
    if not math.isnan(row.iloc[0]['DSCWAH']):
        myha.setproperty('DSCWAH',round(row.iloc[0]['DSCWAH'],1))
    if not str(row.iloc[0]['QLDAT']) in ['nan','NaT']:
        myha.setproperty('QLDAT',row.iloc[0]['QLDAT'].strftime('%Y-%m-%d'))
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
    fcdata = list()
    row = cover.loc[cover['HID'] == ha_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2023'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.append({'date':date,'value':round(FRCOV,3)})
    if fcdata:
        myha.setproperty('FRCOV',fcdata)
    #Soil physical analysis
    row = soil.loc[soil['HID'] == ha_label]
    em38v = list()
    if not math.isnan(row.iloc[0]['2013d260EM38V']):
        em38v.append({'date':'2013-09-17','value':round(row.iloc[0]['2013d260EM38V'],2)})
    if not math.isnan(row.iloc[0]['2015d118EM38V']):
        em38v.append({'date':'2015-04-28','value':round(row.iloc[0]['2015d118EM38V'],2)})
    if not math.isnan(row.iloc[0]['2015d119EM38V']):
        em38v.append({'date':'2015-04-29','value':round(row.iloc[0]['2015d119EM38V'],2)})
    if em38v:
        myha.setproperty('EM38V',em38v)
    slsnd = list()
    slslt = list()
    slcly = list()
    slwp1 = list()
    slwp2 = list()
    slfc1 = list()
    for depth in ['015','045','075','105','135','165']:
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
    slsnd_KRT = list()
    slslt_KRT = list()
    slcly_KRT = list()
    slsnd2_KRT = list()
    slslt2_KRT = list()
    slcly2_KRT = list()
    for depth in ['020','060','100','140','180']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd_KRT.append({'depth':int(depth),
                              'mindepth':int(depth)-20,
                              'maxdepth':int(depth)+20,
                              'value':round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt_KRT.append({'depth':int(depth),
                              'mindepth':int(depth)-20,
                              'maxdepth':int(depth)+20,
                              'value':round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly_KRT.append({'depth':int(depth),
                              'mindepth':int(depth)-20,
                              'maxdepth':int(depth)+20,
                              'value':round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSND2'+depth]):
            slsnd2_KRT.append({'depth':int(depth),
                               'mindepth':int(depth)-20,
                               'maxdepth':int(depth)+20,
                               'value':round(row.iloc[0]['SLSND2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT2'+depth]):
            slslt2_KRT.append({'depth':int(depth),
                               'mindepth':int(depth)-20,
                               'maxdepth':int(depth)+20,
                               'value':round(row.iloc[0]['SLSLT2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY2'+depth]):
            slcly2_KRT.append({'depth':int(depth),
                               'mindepth':int(depth)-20,
                               'maxdepth':int(depth)+20,
                               'value':round(row.iloc[0]['SLCLY2'+depth],2)})
    if slsnd_KRT:  myha.setproperty('SLSND_GBM',slsnd_KRT)
    if slslt_KRT:  myha.setproperty('SLSLT_GBM',slslt_KRT)
    if slcly_KRT:  myha.setproperty('SLCLY_GBM',slcly_KRT)
    if slsnd2_KRT: myha.setproperty('SLSND_GB',slsnd2_KRT)
    if slslt2_KRT: myha.setproperty('SLSLT_GB',slslt2_KRT)
    if slcly2_KRT: myha.setproperty('SLCLY_GB',slcly2_KRT)
    found=False
    for plot in plots:
        if plot.plt_label == ha_label[:4]:
            plot.addchid(myha.getid())
            myha.setproperty('pid',plot.getid())
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
    swcid = feature.GetField('ObjectId')
    tb_label = str(feature.GetField('Tube')) #(e.g., p1-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in neutronSWC shapefile.')
        sys.exit()
    mytube = soilwatercontent.SoilWaterContent(swcid=swcid,geometry=geometry,tb_label=tb_label)
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
                                'value':round(row.loc[depcol],5)})
    if swcdata:
        mytube.setproperty('SWLD',swcdata)
    found=False
    for plot in plots:
        if plot.plt_label == tb_label:
            plot.addswcid(mytube.getid())
            mytube.setproperty('pid',plot.getid())
            found=True
            break
    if not found:
        raise Exception('Did not find plot for neutron tube %s' % tb_label)
    tubes.append(mytube)
########################################################################

########################################################################
#Soil Physical Analysis
shapefile = '../Data/Soil/F013B4_SoilPhysicalAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDJH')
for feature in layer:
    spaid = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2014-p01-1)
    if sa_label in sa['Core'].values:
        row = sa[sa['Core'] == sa_label]
        found = False
        for plot in plots:
            if plot.plt_label == row.iloc[0]['Plot']:
                plot.addspaid(spaid)
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
#print('Plots:' + str(len(plots)))
for myplot in plots:
    features.append(myplot.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_Plot.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
#print('CropHarvest:' + str(len(hareas)))
for myha in hareas:
    features.append(myha.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_CropHarvest.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
#print('SoilWaterContent:' + str(len(tubes)))
for mytube in tubes:
    features.append(mytube.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_SoilWaterContent.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

########################################################################
