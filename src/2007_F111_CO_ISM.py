import os
import sys
import math
import experiment
import plot
import harvestarea
import neutronswc
import cropcanopy
import pandas as pd
from osgeo import ogr
import geojson

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
myexp.setproperty('EXP_AREA',round(exp_area,6))

expmeta = {
    'EXNAME':'Irrigation scheduling methods, Season 1 of 1',
    #'OBJECTIVES':'Unpublished',
    #'EXP_NARR':'Unpublished',
    'MAIN_FACTOR':'Irrigation scheduling method',
    'FACTORS':'Four irrigation scheduling methods with typical and sparse planting density',
    'TRT_NO':8,
    'REP_NO':4,
    #'METHODS':'Unpublished',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 111',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2007',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton after camelina',
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
    #'SUITE_OBJ':'Unpublished',
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
fert = pd.read_excel(mfile,sheet_name='FertilizerDF')
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
    myplot.setproperty('CUL_NAME', 'Deltapine 449 BG/RR')
    myplot.setproperty('PDATE', '04/30/2007')
    myplot.setproperty('PLYR', 2007)
    myplot.setproperty('PLDAY', 120)
    myplot.setproperty('IROP', 'IR001')
    idata = dict()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+str(int(row['DOY']))
        IRVAL = row[plt_label]
        if not math.isnan(IRVAL):
            idata.update({key:round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = dict()
    for index, row in fert.iterrows():
        key = str(int(row['Year']))+str(int(row['DOY']))
        FEAMN = row[plt_label]
        if not math.isnan(FEAMN):
            fdata.update({key:round(FEAMN,1)})
    if fdata:
        myplot.setproperty('FEAMN',fdata)
    #Yield and fiber quality data
    if plt_label not in ['p01','p03']:
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
#Harvest Areas
shapefile = '../Data/'+fname+'/'+fname+'_HarvestAreas.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=26)
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p01)
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
    tb_label = feature.GetField('Tube') #(e.g., p11)
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
                swcitem.update({depth:round(row.loc[depcol],3)})
        key = '{:04d}{:03d}'.format(row.loc['Year'],row.loc['DOY'])
        if swcitem:
            swcdata.update({key:swcitem})
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
crpcns = list()
for feature in layer:
    ccid = feature.GetField('ObjectId')
    cc_label = feature.GetField('CCID')  #(e.g., p02-1)
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
        key = '2007'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(rowh.iloc[0][doycol]):
            CHTD = float(rowh.iloc[0][doycol])/100. #m
            htdata.update({key:round(CHTD,2)})
    if htdata:
        mycc.setproperty('CHTD',htdata)
    wddata = dict()
    roww = ccw.loc[ccw['CCID'] == cc_label]
    doycols = sorted([col for col in ccw.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2007'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(roww.iloc[0][doycol]):
            CWID = float(roww.iloc[0][doycol])/100. #m
            wddata.update({key:round(CWID,2)})
    if wddata:
        mycc.setproperty('CWID',wddata)
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
########################################################################
