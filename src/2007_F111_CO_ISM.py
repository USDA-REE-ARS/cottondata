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

numtrt = 8
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
    'EXNAME':'Irrigation scheduling methods, Season 1 of 1',
    'OBJECTIVES':'See Maqsood, H., Hunsaker, D. J., Waller, P., Thorp, K. R., French, A., Elshikha, D. E., Loeffler, R., 2023. WINDS model demonstration with field data from a furrow-irrigated cotton experiment. Water 15, 1544. doi:10.3390/w15081544',
    'EXP_NARR':'See Maqsood, H., Hunsaker, D. J., Waller, P., Thorp, K. R., French, A., Elshikha, D. E., Loeffler, R., 2023. WINDS model demonstration with field data from a furrow-irrigated cotton experiment. Water 15, 1544. doi:10.3390/w15081544',
    'MAIN_FACTOR':'Irrigation scheduling method',
    'FACTORS':'Four irrigation scheduling methods with typical and sparse planting density',
    'TRT_COUNT':8,
    'REP_NO':4,
    'METHODS':'See Maqsood, H., Hunsaker, D. J., Waller, P., Thorp, K. R., French, A., Elshikha, D. E., Loeffler, R., 2023. WINDS model demonstration with field data from a furrow-irrigated cotton experiment. Water 15, 1544. doi:10.3390/w15081544',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 111',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2007',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton on raised beds with furrow flood irrigation after camelina',
    'LAST_NAME':'Hunsaker',
    'FIRST_NAME':'Douglas',
    'MID_INITIAL':'J',
    'PERSON_NOTES':'Field technicians: Tom Clarke, Don Powers, Suzette Maneely, and Bill Luckett',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'doug.hunsaker@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'',
    'SUITE_NAME':'Irrigation scheduling methods',
    'SUITE_OBJ':'See Maqsood, H., Hunsaker, D. J., Waller, P., Thorp, K. R., French, A., Elshikha, D. E., Loeffler, R., 2023. WINDS model demonstration with field data from a furrow-irrigated cotton experiment. Water 15, 1544. doi:10.3390/w15081544',
    'FL_NAME':'Field 111',
    'FL_LAT':33.068602, #from Google maps
    'FL_LONG':-111.974241, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'FAO-S':'Irrigation scheduling via an ET-based FAO56 soil water balance model with sparse plant density',
            'FAO-T':'Irrigation scheduling via an ET-based FAO56 soil water balance model with typical plant density',
            'ND-S':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI and sparse plant density',
            'ND-T':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI and typical plant density',
            'AZ-S':'Irrigation scheduling via the AZSched software with sparse plant density',
            'AZ-T':'Irrigation scheduling via the AZSched software with typical plant density',
            'CM-S':'Irrigation scheduling via the DSSAT CSM-CROPGRO-Cotton model with sparse plant density',
            'CM-T':'Irrigation scheduling via the DSSAT CSM-CROPGRO-Cotton model with typical plant density'}

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
fert = pd.read_excel(mfile,sheet_name='FertilizerDF')
exfile = '../Data/'+fname+'/'+fname+'_Exotech.xlsx'
exndvi = pd.read_excel(exfile,sheet_name='EXNDVI')
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
    myplot.setproperty('CUL_NAME', 'Deltapine 449 BG/RR')
    myplot.setproperty('PDATE', '2007-04-30')
    myplot.setproperty('PLYR', 2007)
    myplot.setproperty('PLDAY', 120)
    myplot.setproperty('IROP', 'IR001')
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
    for index, row in fert.iterrows():
        key = str(int(row['Year']))+'{:03d}'.format(int(row['DOY']))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        FEAMN = row[plt_label]
        if not math.isnan(FEAMN):
            fdata.append({'date':date,'value':round(FEAMN,1)})
    if fdata:
        myplot.setproperty('FEAMN',fdata)
    tdata = list()
    tdata.append({'date':'2007-04','value':'Rip, disk, laser level, raise beds'})
    myplot.setproperty('TI_NOTES',tdata)
    #cdata = dict()
    #myplot.setproperty('CH_NOTES',cdata)
    #Proximal (Exotech) NDVI
    exndvidata = list()
    row = exndvi.loc[exndvi['Plot'] == plt_label]
    doycols = sorted([col for col in exndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2007'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            exndvidata.append({'date':date,'value':round(NDVImean,3)})
    if exndvidata:
        myplot.setproperty('EXNDVI',exndvidata)
    #Soil physical analysis
    row = soil.loc[soil['Plot'] == plt_label]
    em38h = list()
    if not math.isnan(row.iloc[0]['2008d291EM38H']):
        em38h.append({'date':'2008-10-17','value':round(row.iloc[0]['2008d291EM38H'],2)})
    if not math.isnan(row.iloc[0]['2008d313EM38H']):
        em38h.append({'date':'2008-11-08','value':round(row.iloc[0]['2008d313EM38H'],2)})
    if em38h:
        myplot.setproperty('EM38H',em38h)
    em38v = list()
    if not math.isnan(row.iloc[0]['2008d290EM38V']):
        em38v.append({'date':'2008-10-16','value':round(row.iloc[0]['2008d290EM38V'],2)})
    if not math.isnan(row.iloc[0]['2008d313EM38V']):
        em38v.append({'date':'2008-11-08','value':round(row.iloc[0]['2008d313EM38V'],2)})
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
    for depth in ['195','225','255','285']:
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
    if slsnd: myplot.setproperty('SLSND_M',slsnd)
    if slslt: myplot.setproperty('SLSLT_M',slslt)
    if slcly: myplot.setproperty('SLCLY_M',slcly)
    if slwp1: myplot.setproperty('SLWP',slwp1)
    if slwp2: myplot.setproperty('SLWP2',slwp2)
    if slfc1: myplot.setproperty('SLFC1',slfc1)
    #Yield and fiber quality data
    if plt_label not in ['p01','p03']:
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
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=26)
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    chid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p01)
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
    #Soil physical analysis
    row = soil.loc[soil['HID'] == ha_label]
    em38h = list()
    if not math.isnan(row.iloc[0]['2008d291EM38H']):
        em38h.append({'date':'2008-10-17','value':round(row.iloc[0]['2008d291EM38H'],2)})
    if not math.isnan(row.iloc[0]['2008d313EM38H']):
        em38h.append({'date':'2008-11-08','value':round(row.iloc[0]['2008d313EM38H'],2)})
    if em38h:
        myha.setproperty('EM38H',em38h)
    em38v = list()
    if not math.isnan(row.iloc[0]['2008d290EM38V']):
        em38v.append({'date':'2008-10-16','value':round(row.iloc[0]['2008d290EM38V'],2)})
    if not math.isnan(row.iloc[0]['2008d313EM38V']):
        em38v.append({'date':'2008-11-08','value':round(row.iloc[0]['2008d313EM38V'],2)})
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
    for depth in ['195','225','255','285']:
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
    if slsnd: myha.setproperty('SLSND_M',slsnd)
    if slslt: myha.setproperty('SLSLT_M',slslt)
    if slcly: myha.setproperty('SLCLY_M',slcly)
    if slwp1: myha.setproperty('SLWP',slwp1)
    if slwp2: myha.setproperty('SLWP2',slwp2)
    if slfc1: myha.setproperty('SLFC1',slfc1)
    found=False
    for plot in plots:
        if plot.plt_label == ha_label:
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
    tb_label = str(feature.GetField('Tube')) #(e.g., p11)
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
                if depth==15:
                    sensor='TDR'
                    adjust=15
                else:
                    sensor='NP'
                    adjust=10
                swcdata.append({'date':date,
                                'type':sensor,
                                'depth':depth,
                                'mindepth':depth-adjust,
                                'maxdepth':depth+adjust,
                                'value':round(row.loc[depcol],3)})
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
#Crop Canopy
shapefile = '../Data/'+fname+'/'+fname+'_CropCanopy.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
ccfile = '../Data/'+fname+'/'+fname+'_CropCanopy.xlsx'
cch = pd.read_excel(ccfile,sheet_name='Height')
ccw = pd.read_excel(ccfile,sheet_name='Width')
ccden = pd.read_excel(ccfile,sheet_name='Density')
crpcns = list()
for feature in layer:
    ccid = feature.GetField('ObjectId')
    cc_label = feature.GetField('CCID')  #(e.g., p02-1)
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
        key = '2007'+'{:03d}'.format(int(doycol[3:]))
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
        key = '2007'+'{:03d}'.format(int(doycol[3:]))
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
#Soil Physical Analysis
shapefile = '../Data/Soil/F111_SoilPhysicalAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDJH')
for feature in layer:
    spaid = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., 20062007camelinap02)
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
########################################################################
