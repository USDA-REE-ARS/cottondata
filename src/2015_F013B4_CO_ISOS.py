import os
import sys
import math
import experiment
import plot
import cropharvest
import soilwatercontent
import cropcanopy
import plantanalysis
import pandas as pd
from osgeo import ogr
import geojson
from datetime import datetime
import numpy as np

fname = os.path.basename(__file__)
fname = os.path.splitext(fname)[0]

numtrt = 5
numrep = 2

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
    'EXNAME':'Irrigation scheduling methods for overhead sprinkler, Season 1 of 2',
    'OBJECTIVES':'See Thorp, K. R., Hunsaker, D. J., Bronson, K. F., Andrade-Sanchez, P., Barnes, E. M., 2017. Cotton irrigation scheduling using a crop growth model and FAO-56 methods: Field and simulation studies. Transactions of the ASABE. 60(6):2023-2039. doi:10.13031/trans.12323',
    'EXP_NARR':'See Thorp, K. R., Hunsaker, D. J., Bronson, K. F., Andrade-Sanchez, P., Barnes, E. M., 2017. Cotton irrigation scheduling using a crop growth model and FAO-56 methods: Field and simulation studies. Transactions of the ASABE. 60(6):2023-2039. doi:10.13031/trans.12323',
    'MAIN_FACTOR':'Irrigation scheduling method',
    'FACTORS':'Four irrigation scheduling methods and a stress treatment',
    'TRT_COUNT':5,
    'REP_NO':2,
    'METHODS':'See Thorp, K. R., Hunsaker, D. J., Bronson, K. F., Andrade-Sanchez, P., Barnes, E. M., 2017. Cotton irrigation scheduling using a crop growth model and FAO-56 methods: Field and simulation studies. Transactions of the ASABE. 60(6):2023-2039. doi:10.13031/trans.12323',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2015',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton on raised beds with overhead sprinkler irrigation after winter barley cover crop',
    'LAST_NAME':'Thorp',
    'FIRST_NAME':'Kelly',
    'MID_INITIAL':'R',
    'PERSON_NOTES':'Field technicians: Matt Hagler, Suzette Maneely, and Bill Luckett',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'kelly.thorp@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'',
    'SUITE_NAME':'Irrigation scheduling methods for overhead sprinkler',
    'SUITE_OBJ':'See Thorp, K. R., Hunsaker, D. J., Bronson, K. F., Andrade-Sanchez, P., Barnes, E. M., 2017. Cotton irrigation scheduling using a crop growth model and FAO-56 methods: Field and simulation studies. Transactions of the ASABE. 60(6):2023-2039. doi:10.13031/trans.12323',
    'FL_NAME':'Field 13, Bench 4, Spans 1-5 and 7',
    'FL_LAT':33.07914, #from Google maps
    'FL_LONG':-111.97737, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'FAO':'Irrigation scheduling via an ET-based FAO56 soil water balance model',
            'CropMod':'Irrigation scheduling via the DSSAT CSM-CROPGRO-Cotton model',
            'SEB':'Irrigation scheduling via a surface energy balance model (unrealized)',
            'NDVI':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from remotely sensed NDVI (unrealized)',
            'Stress':'Water stressed treatment with 30%% of the FAO irrigation amount'}

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
    myplot.setproperty('PDATE', '2015-04-29')
    myplot.setproperty('PLYR', 2015)
    myplot.setproperty('PLDAY', 119)
    myplot.setproperty('IROP', 'IR004')
    idata = list()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+'{:03d}'.format(int(row['DOY']))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        IRVAL = row[trt_label]
        if round(IRVAL,1) > 0.0:
            idata.append({'date':date,'value':round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = list()
    fdata.append({'date':'2015-06-09','value':43.5})
    fdata.append({'date':'2015-06-24','value':43.5})
    fdata.append({'date':'2015-07-07','value':43.5})
    myplot.setproperty('FEAMN',fdata)
    plpd = {'p02':11.0,'p03':10.8,'p04':10.0,'p05':10.1,'p06':9.8,
            'p07':10.1,'p08':10.6,'p09':9.5,'p10':9.6,'p11':8.6}
    myplot.setproperty('PLPD',plpd[plt_label])
    #Crop development data (location unknown for emergence and first leaf)
    #Using field average for each plot for emergence and first leaf
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
        if not str(row.iloc[0]['ADAT']) in ['nan','NaT']:
            myplot.setproperty('ADAT',row.iloc[0]['ADAT'].strftime('%Y-%m-%d'))
        if not math.isnan(row.iloc[0]['ADOY']):
            myplot.setproperty('ADOY',int(round(row.iloc[0]['ADOY'],0)))
        nawf = list()
        for doy in ['188','194','203','208','215','223','236','251']:
            key = '2015'+doy
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
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=38)
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    chid = feature.GetField('ObjectId')
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
    myha = cropharvest.CropHarvest(chid=chid,geometry=geometry,ha_label=ha_label)
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
        if plot.plt_label == ha_label[:3]:
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
    tb_label = str(feature.GetField('Tube')) #(e.g., p01-1)
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
        if plot.plt_label == tb_label[:3]:
            plot.addswcid(mytube.getid())
            mytube.setproperty('pid',plot.getid())
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
        key = '2015'+'{:03d}'.format(int(doycol[3:]))
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
        key = '2015'+'{:03d}'.format(int(doycol[3:]))
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
            key = '2015'+'{:03d}'.format(int(doycol[3:]))
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
        if not str(rowdev.iloc[0]['ADAT']) in ['nan','NaT']:
            mycc.setproperty('ADAT',rowdev.iloc[0]['ADAT'].strftime('%Y-%m-%d'))
        if not math.isnan(rowdev.iloc[0]['ADOY']):
            mycc.setproperty('ADOY',int(round(rowdev.iloc[0]['ADOY'],0)))
        nawf = list()
        for doy in ['188','194','203','208','215','223','236','251']:
            key = '2015'+doy
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(rowdev.iloc[0]['NAWF'+doy]):
                nawf.append({'date':date,'value':round(float(rowdev.iloc[0]['NAWF'+doy]),1)})
        if nawf:
            mycc.setproperty('NAWF',nawf)
    found = False
    for plot in plots:
        if plot.plt_label == cc_label[:3]:
            plot.addccid(mycc.getid())
            mycc.setproperty('pid',plot.getid())
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
    pa_label = feature.GetField('SID')  #(e.g., p02N-S1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plant analysis shapefile.')
        sys.exit()
    mypa = plantanalysis.PlantAnalysis(paid=paid,geometry=geometry,pa_label=pa_label)
    #Plant analysis data
    row = pa[pa['SID'] == pa_label]
    if not str(row.iloc[0]['PSDATE']) in ['nan','NaT']:
        date = row.iloc[0]['PSDATE'].strftime('%Y-%m-%d')
        mypa.setproperty('PSDATE',date)
        items={'CHTD':2,'CWID':2,'LAID_FLD':3}
        for item in items.keys():
            if not math.isnan(row.iloc[0][item]):
                value = round(float(row.iloc[0][item]),items[item])
                mypa.setproperty(item,[{'date':date,'value':value}])
    if not math.isnan(row.iloc[0]['NumPlts']):
        pltcnt = int(row.iloc[0]['NumPlts'])
        mypa.setproperty('PLTCNT',int(pltcnt))
    items={'PHTD':2,'MSNODE':0,'PFNODE':0,'FRBNUM':0}
    for item in items.keys():
        padata = list()
        for i in list(range(row.iloc[0]['NumPlts'])):
            if not math.isnan(row.iloc[0][item+str(i+1)]):
                value = round(float(row.iloc[0][item+str(i+1)]),items[item])
                if items[item] == 0: value=int(value)
                padata.append(value)
        if padata:
            mypa.setproperty(item,round(np.mean(np.array(padata)),2))
    items={'ABSNUM':1,'SQRNUM':1,'FLRNUM':1,'GBNUM':1,'MBNUM':1,
           'LWPD':2,'SWPD':2,'CWPD':2,'LWAD':1,'SWAD':1,'PWAD':1,
           'CWAD':1,'LAID_LAB':3,'SDPB':1,'BBFRAC':3,'BSFRAC':3,
           'BFFRAC':3}
    for item in items.keys():
        if not math.isnan(row.iloc[0][item]):
            value = round(float(row.iloc[0][item]),items[item])
            if items[item] == 0: value=int(value)
            mypa.setproperty(item,value)
    found = False
    for plot in plots:
        if plot.plt_label == pa_label[:3]:
            plot.addpaid(mypa.getid())
            mypa.setproperty('pid',plot.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for plant analysis %s' % pa_label)
    pas.append(mypa)
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
            raise Exception('Did not find plot for soil analysis %s' % sa_label)

shapefile = '../Data/Soil/F013B4_SoilPhysicalAnalysis_KRT.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilKRT')
for feature in layer:
    spaid = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 2016-p01-1)
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

features = list()
#print('CropCanopy:' + str(len(crpcns)))
for mycrpcn in crpcns:
    features.append(mycrpcn.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_CropCanopy.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()

features = list()
#print('PlantAnalysis:' + str(len(pas)))
for mypa in pas:
    features.append(mypa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_PlantAnalysis.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
