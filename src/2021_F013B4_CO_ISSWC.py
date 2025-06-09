import os
import sys
import math
import experiment
import plot
import harvestarea
import neutronswc
import cropcanopy
import plantanalysis
import soilanalysis
import pandas as pd
from osgeo import ogr
import geojson

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
myexp.setproperty('EXP_AREA',round(exp_area,6))

expmeta = {
    'EXNAME':'Soil water guided irrigation scheduling models, Season 1 of 2',
    'OBJECTIVES':'See Thorp, K. R., 2023. Combining soil water content data with computer simulation models for improved irrigation scheduling. Journal of the ASABE 66 (5), 1265-1279. doi:10.13031/ja.15591',
    'EXP_NARR':'See Thorp, K. R., 2023. Combining soil water content data with computer simulation models for improved irrigation scheduling. Journal of the ASABE 66 (5), 1265-1279. doi:10.13031/ja.15591',
    'MAIN_FACTOR':'Irrigation scheduling method: stand-alone models versus soil water assisted models',
    'FACTORS':'Six irrigation scheduling methods and two cotton varieties',
    'TRT_NO':12,
    'REP_NO':4,
    'METHODS':'See Thorp, K. R., 2023. Combining soil water content data with computer simulation models for improved irrigation scheduling. Journal of the ASABE 66 (5), 1265-1279. doi:10.13031/ja.15591',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2021',
    'EXP_DUR':1,
    'CR_SYSTEM':'Strip-till cotton after winter triticale cover crop',
    'LAST_NAME':'Thorp',
    'FIRST_NAME':'Kelly',
    'MID_INITIAL':'R',
    'PERSON_NOTES':'Field technicians: Matt Hagler and Suzette Maneely',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'kelly.thorp@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'Abnormally high precipitation during boll filling led to growthy cotton',
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
    myplot.setproperty('PLT_AREA',round(plt_area,6))
    #Management information
    if '3195' in trt_label:
        myplot.setproperty('CUL_NAME', 'NexGen 3195 B3XF')
    elif '4936' in trt_label:
        myplot.setproperty('CUL_NAME', 'NexGen 4936 B3XF')
    myplot.setproperty('PDATE', '04/20/2021')
    myplot.setproperty('PLYR', 2021)
    myplot.setproperty('PLDAY', 110)
    myplot.setproperty('IROP', 'IR004')
    idata = dict()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+'{:03d}'.format(int(row['DOY']))
        IRVAL = row[plt_label]
        if not math.isnan(IRVAL):
            idata.update({key:round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = dict()
    fdata.update({'2021159':51.9})
    fdata.update({'2021173':51.9})
    fdata.update({'2021195':45.4})
    myplot.setproperty('FEAMN',fdata)
    tdata = dict()
    tdata.update({'2021097':'Strip tillage'})
    cdata = dict()
    cdata.update({'2021091':'Apply RoundUp (glyphosate)'})
    cdata.update({'2021105':'Apply Velum Total (fluopyram)'})
    cdata.update({'2021106':'Apply Prowl (pendimethalin)'})
    cdata.update({'2021131':'Apply RoundUp (glyphosate)'})
    cdata.update({'2021166':'Apply RoundUp (glyphosate)'})
    cdata.update({'2021219':'Apply Carbine 50WG (flonicamid)'})
    cdata.update({'2021226':'Apply Carbine 50WG (flonicamid)'})
    cdata.update({'2021233':'Apply Carbine 50WG (flonicamid)'})
    cdata.update({'2021294':'Apply Ginstar (diuron, thidiazuron) and CottonQuik (urea sulfate, ethephon)'})
    cdata.update({'2021309':'Apply Ginstar (diuron, thidiazuron)'})
    tdata.update({'2021Fall':'Root pull, rip, moldboard plow, disk, and land plane'})
    myplot.setproperty('TI_NOTES',tdata)
    myplot.setproperty('CH_NOTES',cdata)
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
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
        myplot.setproperty('FBMIC' ,round(row.iloc[0]['FBMIC' ],2))
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
#Harvest Areas
shapefile = '../Data/'+fname+'/'+fname+'_HarvestAreas.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=84)
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
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mycc = cropcanopy.CropCanopy(ccid=ccid,geometry=geometry,cc_label=cc_label)
    #Crop canopy data
    htdata = dict()
    rowh = cch.loc[cch['CCID'] == cc_label]
    doycols = sorted([col for col in cch.columns if col[:3]=='DOY'])
    if not rowh.empty:
        for doycol in doycols:
            key = '2021'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(rowh.iloc[0][doycol]):
                CHTD = float(rowh.iloc[0][doycol])/100. #m
                htdata.update({key:round(CHTD,2)})
    if htdata:
        mycc.setproperty('CHTD',htdata)
    wddata = dict()
    roww = ccw.loc[ccw['CCID'] == cc_label]
    doycols = sorted([col for col in ccw.columns if col[:3]=='DOY'])
    if not roww.empty:
        for doycol in doycols:
            key = '2021'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(roww.iloc[0][doycol]):
                CWID = float(roww.iloc[0][doycol])/100. #m
                wddata.update({key:round(CWID,2)})
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
        nawf = dict()
        for doy in ['182','194','200','217','224','238','250']:
            if not math.isnan(rowdev.iloc[0]['NAWF'+doy]):
                nawf.update({'2021'+doy:round(rowdev.iloc[0]['NAWF'+doy],1)})
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
    pa_label = feature.GetField('Sample')  #(e.g., p01-1-S1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mypa = plantanalysis.PlantAnalysis(paid=paid,geometry=geometry,pa_label=pa_label)
    #Plant analysis data
    row = pa[pa['SID'] == pa_label]
    if not str(row.iloc[0]['PSDATE']) in ['nan','NaT']:
        mypa.setproperty('PSDATE',row.iloc[0]['PSDATE'].strftime('%m/%d/%Y'))
    items={'PHTD':2,'MSNODE':0,'PFNODE':0,'FRBNUM':0}
    for item in items.keys():
        padata = dict()
        for i in list(range(row.iloc[0]['NumPlts'])):
            if not math.isnan(row.iloc[0][item+str(i+1)]):
                value = round(float(row.iloc[0][item+str(i+1)]),items[item])
                if items[item] == 0: value=int(value)
                padata.update({i+1:value})
        if padata:
            mypa.setproperty(item,padata)
    items={'ABCNUM':1,'SQRNUM':1,'FLRNUM':1,'GBNUM':1,'MBNUM':1,
           'LWPD':2,'SWPD':2,'CWPD':2,'LWAD':1,'SWAD':1,'MBWAD':1,
           'PWAD':1,'CWAD':1,'LAIDL':3}
    for item in items.keys():
        if not math.isnan(row.iloc[0][item]):
            value = round(float(row.iloc[0][item]),items[item])
            if items[item] == 0: value=int(value)
            mypa.setproperty(item,value)
    found = False
    for plot in plots:
        if plot.plt_label == pa_label[:5]:
            plot.addpaid(mypa.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for plant analysis %s' % pa_label)
    pas.append(mypa)
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
    said = feature.GetField('ObjectId')
    sa_label = feature.GetField('Core')  #(e.g., p01-2)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mysa = soilanalysis.SoilAnalysis(said=said,geometry=geometry,sa_label=sa_label)
    #Soil analysis data
    rows = sa[sa['Plot'] == sa_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysa.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%m/%d/%Y'))
    items={'SLPHW':1,'SLPHB':1,'SLEC':2,'SLOM':1,'SNO3':1,'SLPX':1,
           'SLKE':0,'SLSU':1,'SLZN':2,'SLFE':1,'SLMN':1,'SLCU':2,
           'SLCA':0,'SLMG':0,'SLNA':0,'SLCEC':1}
    for item in items.keys():
        sadata = dict()
        for depth in [20,60,100,140,180]:
            row = sa[(sa['Plot'] == sa_label) & (sa['Depth'] == depth)]
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                sadata.update({depth:value})
        if sadata:
            mysa.setproperty(item,sadata)
    found = False
    for plot in plots:
        if plot.plt_label == sa_label:
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
for mypa in pas:
    features.append(mypa.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_plantanalysis.geojson','w') as f:
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
