import os
import sys
import math
import experiment
import plot
import cropharvest
import soilwatercontent
import cropcanopy
import soilchemicalanalysis
import pandas as pd
from osgeo import ogr
import geojson
from datetime import datetime

fname = os.path.basename(__file__)
fname = os.path.splitext(fname)[0]

numtrt = 12
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
    'EXNAME':'Soil water guided irrigation scheduling models, Season 2 of 2',
    'OBJECTIVES':'See Thorp, K. R., 2023. Combining soil water content data with computer simulation models for improved irrigation scheduling. Journal of the ASABE 66 (5), 1265-1279. doi:10.13031/ja.15591',
    'EXP_NARR':'See Thorp, K. R., 2023. Combining soil water content data with computer simulation models for improved irrigation scheduling. Journal of the ASABE 66 (5), 1265-1279. doi:10.13031/ja.15591',
    'MAIN_FACTOR':'Irrigation scheduling method: stand-alone models versus soil water assisted models',
    'FACTORS':'Six irrigation scheduling methods and two cotton varieties',
    'TRT_COUNT':12,
    'REP_NO':4,
    'METHODS':'See Thorp, K. R., 2023. Combining soil water content data with computer simulation models for improved irrigation scheduling. Journal of the ASABE 66 (5), 1265-1279. doi:10.13031/ja.15591',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2022',
    'EXP_DUR':1,
    'CR_SYSTEM':'Strip-till cotton with overhead sprinkler irrigation after winter triticale cover crop',
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
    'SUITE_NAME':'Soil water guided irrigation scheduling models',
    'SUITE_OBJ':'See Thorp, K. R., 2023. Combining soil water content data with computer simulation models for improved irrigation scheduling. Journal of the ASABE 66 (5), 1265-1279. doi:10.13031/ja.15591',
    'FL_NAME':'Field 13, Bench 4, Spans 4-6',
    'FL_LAT':33.07914, #from Google maps
    'FL_LONG':-111.97737, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'FAO_NG4936':'Irrigation scheduling via an ET-based FAO56 soil water balance model and cotton cultivar NG4936',
            'CSM_NG4936':'Irrigation scheduling via the DSSAT CSM-CROPGRO-Cotton model and cotton cultivar NG4936',
            'AQC_NG4936':'Irrigation scheduling via the AquaCrop model and cotton cultivar NG4936',
            'FAOSWC_NG4936':'Irrigation scheduling via an ET-based FAO56 soil water balance model with soil water content feedback and cotton cultivar NG4936',
            'CSMSWC_NG4936':'Irrigation scheduling via the DSSAT CSM-CROPGRO-Cotton model with soil water content feedback and cotton cultivar NG4936',
            'AQCSWC_NG4936':'Irrigation scheduling via the AquaCrop model with soil water content feedback and cotton cultivar NG4936',
            'FAO_NG3195':'Irrigation scheduling via an ET-based FAO56 soil water balance model and cotton cultivar NG3195',
            'CSM_NG3195':'Irrigation scheduling via the DSSAT CSM-CROPGRO-Cotton model and cotton cultivar NG3195',
            'AQC_NG3195':'Irrigation scheduling via the AquaCrop model and cotton cultivar NG3195',
            'FAOSWC_NG3195':'Irrigation scheduling via an ET-based FAO56 soil water balance model with soil water content feedback and cotton cultivar NG3195',
            'CSMSWC_NG3195':'Irrigation scheduling via the DSSAT CSM-CROPGRO-Cotton model with soil water content feedback and cotton cultivar NG3195',
            'AQCSWC_NG3195':'Irrigation scheduling via the AquaCrop model with soil water content feedback and cotton cultivar NG3195'}

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
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilPlot')
plots = list()
for feature in layer:
    pid = feature.GetField('ObjectId')
    plt_label = feature.GetField('Plot')
    trt_label = feature.GetField('Treatment')+'_'+feature.GetField('Cultivar')
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
    if '3195' in trt_label:
        myplot.setproperty('CUL_NAME', 'NexGen 3195 B3XF')
    elif '4936' in trt_label:
        myplot.setproperty('CUL_NAME', 'NexGen 4936 B3XF')
    myplot.setproperty('PDATE', '2022-04-21')
    myplot.setproperty('PLYR', 2022)
    myplot.setproperty('PLDAY', 111)
    myplot.setproperty('IROP', 'IR004')
    idata = list()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+'{:03d}'.format(int(row['DOY']))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        IRVAL = row[plt_label]
        if not math.isnan(IRVAL):
            idata.append({'date':date,'value':round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = list()
    fdata.append({'date':'2022-06-07','value':45.4})
    fdata.append({'date':'2022-07-01','value':51.9})
    fdata.append({'date':'2022-07-22','value':51.9})
    myplot.setproperty('FEAMN',fdata)
    cdata = list()
    cdata.append({'date':'2022-03-21','value':'Apply RoundUp (glyphosate)'})
    cdata.append({'date':'2022-04-14','value':'Apply Prowl (pendimethalin)'})
    if int(plt_label[1:3]) <= 8:
        cdata.append({'date':'2022-04-16','value':'Apply RoundUp (glyphosate)'})
    else:
        cdata.append({'date':'2022-04-19','value':'Apply RoundUp (glyphosate)'})
    cdata.append({'date':'2022-06-16','value':'Apply RoundUp (glyphosate)'})
    cdata.append({'date':'2022-07-18','value':'Apply RoundUp (glyphosate), Gin Out (mepiquat chloride), and Transform (sulfoxaflor)'})
    cdata.append({'date':'2022-08-09','value':'Apply Gin Out (mepiquat chloride) and Transform (sulfoxaflor)'})
    cdata.append({'date':'2022-08-25','value':'Apply Gin Out (mepiquat chloride) and Transform (sulfoxaflor)'})
    cdata.append({'date':'2022-09-30','value':'Apply Ginstar (diuron, thidiazuron) and CottonQuik (urea sulfate, ethephon)'})
    cdata.append({'date':'2022-10-14','value':'Apply Ginstar (diuron, thidiazuron)'})
    myplot.setproperty('CH_NOTES',cdata)
    tdata = list()
    tdata.append({'date':'2022-04-14','value':'Strip tillage'})
    tdata.append({'date':'2022-12','value':'Root pull, rip, moldboard plow, disk, and land plane'})
    myplot.setproperty('TI_NOTES',tdata)
    #Crop development data
    row = develop.loc[develop['Plot'] == plt_label]
    if not row.empty:
        if not str(row.iloc[0]['EDATE']) in ['nan','NaT']:
            myplot.setproperty('EDATE',row.iloc[0]['EDATE'].strftime('%Y-%m-%d'))
        if not math.isnan(row.iloc[0]['PLYRE']):
            myplot.setproperty('PLYRE',int(row.iloc[0]['PLYRE']))
        if not math.isnan(row.iloc[0]['PLDOE']):
            myplot.setproperty('PLDOE',int(round(row.iloc[0]['PLDOE'],0)))
        if not str(row.iloc[0]['LF1D']) in ['nan','NaT']:
            myplot.setproperty('LF1D',row.iloc[0]['LF1D'].strftime('%Y-%m-%d'))
        nawf = list()
        for doy in ['186','192','206','220','227','234','241','251']:
            key = '2022'+doy
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(row.iloc[0]['NAWF'+doy]):
                nawf.append({'date':date,'value':round(float(row.iloc[0]['NAWF'+doy]),1)})
        if nawf:
            myplot.setproperty('NAWF',nawf)
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
    plots.append(myplot)
########################################################################

########################################################################
#Crop Harvest
shapefile = '../Data/'+fname+'/'+fname+'_CropHarvest.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_CropHarvest.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=84)
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p01-1-NW)
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
        if plot.plt_label == ha_label[:5]:
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
                                'value':round(row.loc[depcol],5)})
    if swcdata:
        mytube.setproperty('SWLD',swcdata)
    found=False
    for plot in plots:
        if plot.plt_label == tb_label:
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
    ccid = feature.GetField('ObjectId')
    cc_label = feature.GetField('CCID')  #(e.g., p01-1N)
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
        key = '2022'+'{:03d}'.format(int(doycol[3:]))
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
        key = '2022'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(roww.iloc[0][doycol]):
            CWID = float(roww.iloc[0][doycol])/100. #m
            wddata.append({'date':date,'value':round(CWID,2)})
    if wddata:
        mycc.setproperty('CWID',wddata)
    rowden = ccden.loc[ccden['CCID'] == cc_label]
    if not rowden.empty:
        if not math.isnan(rowden.iloc[0]['PLPD']):
            PLPD = float(rowden.iloc[0]['PLPD'])
            mycc.setproperty('PLPD',round(PLPD,1))
    rowdev = ccdev.loc[ccdev['CCID'] == cc_label]
    if not rowdev.empty:
        if not str(rowdev.iloc[0]['EDATE']) in ['nan','NaT']:
            mycc.setproperty('EDATE',rowdev.iloc[0]['EDATE'].strftime('%Y-%m-%d'))
        if not math.isnan(rowdev.iloc[0]['PLYRE']):
            mycc.setproperty('PLYRE',int(rowdev.iloc[0]['PLYRE']))
        if not math.isnan(rowdev.iloc[0]['PLDOE']):
            mycc.setproperty('PLDOE',int(round(rowdev.iloc[0]['PLDOE'],0)))
        if not str(rowdev.iloc[0]['LF1D']) in ['nan','NaT']:
            mycc.setproperty('LF1D',rowdev.iloc[0]['LF1D'].strftime('%Y-%m-%d'))
        nawf = list()
        for doy in ['186','192','206','220','227','234','241','251']:
            key = '2022'+doy
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(rowdev.iloc[0]['NAWF'+doy]):
                nawf.append({'date':date,'value':round(rowdev.iloc[0]['NAWF'+doy],1)})
        if nawf:
            mycc.setproperty('NAWF',nawf)
    found = False
    for plot in plots:
        if plot.plt_label == cc_label[:5]:
            plot.addccid(mycc.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for crop canopy %s' % cc_label)
    crpcns.append(mycc)
########################################################################

########################################################################
#Soil Chemical Analysis
shapefile = '../Data/'+fname+'/'+fname+'_SoilChemicalAnalysis.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
scfile = '../Data/'+fname+'/'+fname+'_SoilChemicalAnalysis.xlsx'
sc = pd.read_excel(scfile,sheet_name='SoilChemDF',skiprows=1)
scs = list()
for feature in layer:
    scid = feature.GetField('ObjectId')
    sc_label = feature.GetField('Core')  #(e.g., p01-2)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in soil chemistry shapefile.')
        sys.exit()
    mysc = soilchemicalanalysis.SoilChemicalAnalysis(scid=scid,geometry=geometry,sc_label=sc_label)
    #Soil chemistry data
    rows = sc[sc['Plot'] == sc_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysc.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%Y-%m-%d'))
    items={'SLPHW':1,'SLPHB':1,'SLEC':2,'SLOM':1,'SNO3':1,'SLPX':1,
           'SLKE':0,'SLSU':1,'SLZN':2,'SLFE':1,'SLMN':1,'SLCU':2,
           'SLCA':0,'SLMG':0,'SLNA':0,'SLCEC':1}
    for item in items.keys():
        scdata = list()
        for depth in [20,60,100,140,180]:
            row = sc[(sc['Plot'] == sc_label) & (sc['Depth'] == depth)]
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                scdata.append({'depth':depth,
                               'mindepth':depth-20,
                               'maxdepth':depth+20,
                               'value':value})
        if scdata:
            mysc.setproperty(item,scdata)
    found = False
    for plot in plots:
        if plot.plt_label == sc_label:
            plot.addscid(mysc.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for soil chemical analysis %s' % sc_label)
    scs.append(mysc)
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
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2014-p01-1)
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

shapefile = '../Data/Soil/F013B4_SoilPhysicalAnalysis_KRT.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilKRT')
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2016-p01-1)
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
for mysc in scs:
    features.append(mysc.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_SoilChemicalAnalysis.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
