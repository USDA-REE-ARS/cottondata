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
    'EXNAME':'FAO-56 Irrigation Scheduling Experiment (FISE), Season 2 of 2',
    'OBJECTIVES':'See Hunsaker, D. J., Barnes, E. M., Clarke, T. R., Fitzgerald, G. J., Pinter, Jr., P. J., 2005. Cotton irrigation scheduling using remotely sensed and FAO-56 basal crop coefficients. Transactions of the ASAE. 48(4):1395-1407. doi:10.13031/2013.19197',
    'EXP_NARR':'See Hunsaker, D. J., Barnes, E. M., Clarke, T. R., Fitzgerald, G. J., Pinter, Jr., P. J., 2005. Cotton irrigation scheduling using remotely sensed and FAO-56 basal crop coefficients. Transactions of the ASAE. 48(4):1395-1407. doi:10.13031/2013.19197',
    'MAIN_FACTOR':'Irrigation scheduling method: FAO-56 stand-alone models versus remotely sensed FAO-56 basal crop coefficients',
    'FACTORS':'Two irrigation scheduling methodologies, three planting densities, and two nitrogen rates',
    'TRT_COUNT':12,
    'REP_NO':4,
    'METHODS':'See Hunsaker, D. J., Barnes, E. M., Clarke, T. R., Fitzgerald, G. J., Pinter, Jr., P. J., 2005. Cotton irrigation scheduling using remotely sensed and FAO-56 basal crop coefficients. Transactions of the ASAE. 48(4):1395-1407. doi:10.13031/2013.19197',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 105',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2003',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton on raised beds with furrow flood irrigation after winter barley cover crop',
    'LAST_NAME':'Hunsaker',
    'FIRST_NAME':'Douglas',
    'MID_INITIAL':'J',
    'PERSON_NOTES':'Field technicians: C. Arterberry, A. Ashley, M. Conley, R. Jackson, S. Johnson, C. Jones, W. Luckett, S. Maneely, C. O’Brien, D. Powers, S. Richards, and R. Rokey',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'doug.hunsaker@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'',
    'SUITE_NAME':'FAO-56 Irrigation Scheduling Experiment (FISE)',
    'SUITE_OBJ':'See Hunsaker, D. J., Barnes, E. M., Clarke, T. R., Fitzgerald, G. J., Pinter, Jr., P. J., 2005. Cotton irrigation scheduling using remotely sensed and FAO-56 basal crop coefficients. Transactions of the ASAE. 48(4):1395-1407. doi:10.13031/2013.19197',
    'FL_NAME':'Field 105',
    'FL_LAT':33.067406, #from Google maps
    'FL_LONG':-111.971473, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'FSL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with sparse plant density and low nitrogen rate (2 reps)',
            'FSH':'Irrigation scheduling via an ET-based FAO56 soil water balance model with sparse plant density and high nitrogen rate (2 reps)',
            'FTL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with typical plant density and low nitrogen rate (4 reps)',
            'FTH':'Irrigation scheduling via an ET-based FAO56 soil water balance model with typical plant density and high nitrogen rate (4 reps)',
            'FDL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with dense plant density and low nitrogen rate (2 reps)',
            'FDH':'Irrigation scheduling via an ET-based FAO56 soil water balance model with dense plant density and high nitrogen rate (2 reps)',
            'NSL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI, sparse plant density, and low nitrogen rate (2 reps)',
            'NSH':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI, sparse plant density, and high nitrogen rate (2 reps)',
            'NTL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI, typical plant density, and low nitrogen rate (4 reps)',
            'NTH':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI, typical plant density, and high nitrogen rate (4 reps)',
            'NDL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI, dense plant density, and low nitrogen rate (2 reps)',
            'NDH':'Irrigation scheduling via an ET-based FAO56 soil water balance model with Kcb from NDVI, dense plant density, and high nitogen rate (2 reps)'}

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
dfile = '../Data/'+fname+'/'+fname+'_CropCanopy.xlsx'
develop = pd.read_excel(dfile,sheet_name='PlotDevelop')
exfile = '../Data/'+fname+'/'+fname+'_Exotech.xlsx'
exndvi = pd.read_excel(exfile,sheet_name='EXNDVI')
irtfile = '../Data/'+fname+'/'+fname+'_MDIRT.xlsx'
irtcomp = pd.read_excel(irtfile,sheet_name='Composite')
irtcan  = pd.read_excel(irtfile,sheet_name='Canopy')
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
    myplot.setproperty('CUL_NAME', 'Deltapine 458 B/RR')
    myplot.setproperty('PDATE', '2003-04-08')
    myplot.setproperty('PLYR', 2003)
    myplot.setproperty('PLDAY', 98)
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
    #cdata = list()
    #myplot.setproperty('CH_NOTES',cdata)
    tdata = list()
    tdata.append({'date':'2003-03','value':'Rip, disk, laser level, raise beds'})
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
    #Proximal (Exotech) NDVI
    exndvidata = list()
    row = exndvi.loc[exndvi['Plot'] == plt_label]
    doycols = sorted([col for col in exndvi.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2003'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            NDVImean = float(row.iloc[0][doycol])
            exndvidata.append({'date':date,'value':round(NDVImean,3)})
    if exndvidata:
        myplot.setproperty('EXNDVI',exndvidata)
    #Proximal mid-day infrared thermometer (IRT)
    irtcompdata = list()
    row = irtcomp.loc[irtcomp['Plot'] == plt_label]
    doycols = sorted([col for col in irtcomp.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2003'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            irtcomptemp = float(row.iloc[0][doycol])
            irtcompdata.append({'date':date,'value':round(irtcomptemp,2)})
    if irtcompdata:
        myplot.setproperty('IRTLST',irtcompdata)
    irtcandata = list()
    row = irtcan.loc[irtcan['Plot'] == plt_label]
    doycols = sorted([col for col in irtcan.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2003'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(row.iloc[0][doycol]):
            irtcantemp = float(row.iloc[0][doycol])
            irtcandata.append({'date':date,'value':round(irtcantemp,2)})
    if irtcandata:
        myplot.setproperty('IRTLSTCAN',irtcandata)
    #Soil physical analysis
    row = soil.loc[soil['Plot'] == plt_label]
    em38h = list()
    if not math.isnan(row.iloc[0]['2002d092EM38H']):
        em38h.append({'date':'2002-04-02','value':round(row.iloc[0]['2002d092EM38H'],2)})
    if em38h:
        myplot.setproperty('EM38H',em38h)
    em38v = list()
    if not math.isnan(row.iloc[0]['2002d092EM38V']):
        em38v.append({'date':'2002-04-02','value':round(row.iloc[0]['2002d092EM38V'],2)})
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
    #Yield and fiber quality data
    if plt_label not in ['p901','p903','p905','p907']:
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
#Crop Harvest
shapefile = '../Data/'+fname+'/'+fname+'_CropHarvest.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_CropHarvest.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=28)
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p101)
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
    if plt_label not in ['p901','p903','p905','p907']:
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
    if not math.isnan(row.iloc[0]['2002d092EM38H']):
        em38h.append({'date':'2002-04-02','value':round(row.iloc[0]['2002d092EM38H'],2)})
    if em38h:
        myha.setproperty('EM38H',em38h)
    em38v = list()
    if not math.isnan(row.iloc[0]['2002d092EM38V']):
        em38v.append({'date':'2002-04-02','value':round(row.iloc[0]['2002d092EM38V'],2)})
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
    found=False
    for plot in plots:
        if plot.plt_label == ha_label:
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
    tb_label = str(feature.GetField('Tube')) #(e.g., 101)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in neutronSWC shapefile.')
        sys.exit()
    mytube = soilwatercontent.SoilWaterContent(tid=tid,geometry=geometry,tb_label=tb_label)
    #Neutron soil water content data
    rows = swc.loc[swc['Tube'] == int(tb_label)]
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
        if int(plot.plt_label[1:]) == int(tb_label):
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
ccs = pd.read_excel(ccfile,sheet_name='SPAD')
ccca = pd.read_excel(ccfile,sheet_name='ChlA')
ccden = pd.read_excel(ccfile,sheet_name='Density')
ccdev = pd.read_excel(ccfile,sheet_name='Develop')
crpcns = list()
for feature in layer:
    ccid = feature.GetField('ObjectId')
    cc_label = feature.GetField('CCID')  #(e.g., p101-1)
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
        key = '2003'+'{:03d}'.format(int(doycol[3:]))
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
        key = '2003'+'{:03d}'.format(int(doycol[3:]))
        date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
        if not math.isnan(roww.iloc[0][doycol]):
            CWID = float(roww.iloc[0][doycol])/100. #m
            wddata.append({'date':date,'value':round(CWID,2)})
    if wddata:
        mycc.setproperty('CWID',wddata)
    spaddata = list()
    rows = ccs.loc[ccs['CCID'] == cc_label]
    if not rows.empty:
        doycols = sorted([col for col in ccs.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2003'+'{:03d}'.format(int(doycol[3:]))
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(rows.iloc[0][doycol]):
                SPAD = float(rows.iloc[0][doycol])
                spaddata.append({'date':date,'value':round(SPAD,1)})
        if spaddata:
            mycc.setproperty('SPAD',spaddata)
    chladata = list()
    rows = ccca.loc[ccca['CCID'] == cc_label]
    if not rows.empty:
        doycols = sorted([col for col in ccca.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2003'+'{:03d}'.format(int(doycol[3:]))
            date = datetime.strptime(key,'%Y%j').strftime('%Y-%m-%d')
            if not math.isnan(rows.iloc[0][doycol]):
                CHLA = float(rows.iloc[0][doycol])
                chladata.append({'date':date,'value':round(CHLA,1)})
        if chladata:
            mycc.setproperty('CHLA',chladata)
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
    found = False
    for plot in plots:
        if plot.plt_label == cc_label[:4]:
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
    pa_label = feature.GetField('SID')  #(e.g., p101-S01)
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
    items={'PHTD':3,'STDD':1,'MSNODE':0,'PFNODE':0,'VBNUM':0,'VBNODE':0}
    for item in items.keys():
        padata = list()
        for i in list(range(row.iloc[0]['NumPlts'])):
            if not math.isnan(row.iloc[0][item+str(i+1)]):
                value = round(float(row.iloc[0][item+str(i+1)]),items[item])
                if items[item] == 0: value=int(value)
                padata.append(value)
        if padata:
            mypa.setproperty(item,round(np.mean(np.array(value)),max([items[item],2])))
    items={'SQRNUM':1,'FLRNUM':1,'GBNUM':1,'MBNUM':1,
           'LWPD':2,'SWPD':2,'CWPD':2,'LWAD':1,'SWAD':1,'MBWAD':1,
           'PWAD':1,'CWAD':1,'LAID_LAB':3}
    for item in items.keys():
        if not math.isnan(row.iloc[0][item]):
            value = round(float(row.iloc[0][item]),items[item])
            if items[item] == 0: value=int(value)
            mypa.setproperty(item,value)
    found = False
    for plot in plots:
        if plot.plt_label == pa_label[:4]:
            plot.addpaid(mypa.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for plant analysis %s' % pa_label)
    pas.append(mypa)
########################################################################

########################################################################
#Soil Physical Analysis
shapefile = '../Data/Soil/F105_SoilPhysicalAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilPhysicalAnalysis.xlsx'
sa = pd.read_excel(safile,sheet_name='SoilDJH')
for feature in layer:
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., p101)
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
for mypa in pas:
    features.append(mypa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_PlantAnalysis.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
