import os
import sys
import math
import experiment
import plot
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

numtrt = 16
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
    'EXNAME':'Irrigation timing and rate experiment, Season 1 of 3',
    'OBJECTIVES':'See Thorp, K. R., Thompson, A. L., Bronson, K. F., 2020. Irrigation rate and timing effects on Arizona cotton yield, water productivity, and fiber quality. Agricultural Water Management 234, 106146. doi:10.1016/j.agwat.2020.106146',
    'EXP_NARR':'See Thorp, K. R., Thompson, A. L., Bronson, K. F., 2020. Irrigation rate and timing effects on Arizona cotton yield, water productivity, and fiber quality. Agricultural Water Management 234, 106146. doi:10.1016/j.agwat.2020.106146',
    'MAIN_FACTOR':'Irrigation timing and rate: Combinations of four irrigation rates (60%%, 80%%, 100%%, and 120%% of full irrigation) in two time periods (first square to peak bloom and peak bloom to 90%% open boll)',
    'FACTORS':'Irrigation timing and rate: Combinations of four irrigation rates (60%%, 80%%, 100%%, and 120%% of full irrigation) in two time periods (first square to peak bloom and peak bloom to 90%% open boll)',
    'TRT_COUNT':16,
    'REP_NO':4,
    'METHODS':'See Thorp, K. R., Thompson, A. L., Bronson, K. F., 2020. Irrigation rate and timing effects on Arizona cotton yield, water productivity, and fiber quality. Agricultural Water Management 234, 106146. doi:10.1016/j.agwat.2020.106146',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2016',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton on-the-flat after winter barley cover crop',
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
    'SUITE_NAME':'Irrigation timing and rate experiment',
    'SUITE_OBJ':'See Thorp, K. R., Thompson, A. L., Bronson, K. F., 2020. Irrigation rate and timing effects on Arizona cotton yield, water productivity, and fiber quality. Agricultural Water Management 234, 106146. doi:10.1016/j.agwat.2020.106146',
    'FL_NAME':'Field 13, Bench 4, Spans 2-6',
    'FL_LAT':33.07914, #from Google maps
    'FL_LONG':-111.97737, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'60-60':'60%% irrigation rate from first square to peak bloom and 60%% irrigation rate from peak bloom to 90%% open boll',
            '60-80':'60%% irrigation rate from first square to peak bloom and 80%% irrigation rate from peak bloom to 90%% open boll',
            '60-100':'60%% irrigation rate from first square to peak bloom and 100%% irrigation rate from peak bloom to 90%% open boll',
            '60-120':'60%% irrigation rate from first square to peak bloom and 120%% irrigation rate from peak bloom to 90%% open boll',
            '80-60':'80%% irrigation rate from first square to peak bloom and 60%% irrigation rate from peak bloom to 90%% open boll',
            '80-80':'80%% irrigation rate from first square to peak bloom and 80%% irrigation rate from peak bloom to 90%% open boll',
            '80-100':'80%% irrigation rate from first square to peak bloom and 100%% irrigation rate from peak bloom to 90%% open boll',
            '80-120':'80%% irrigation rate from first square to peak bloom and 120%% irrigation rate from peak bloom to 90%% open boll',
            '100-60':'100%% irrigation rate from first square to peak bloom and 60%% irrigation rate from peak bloom to 90%% open boll',
            '100-80':'100%% irrigation rate from first square to peak bloom and 80%% irrigation rate from peak bloom to 90%% open boll',
            '100-100':'100%% irrigation rate from first square to peak bloom and 100%% irrigation rate from peak bloom to 90%% open boll',
            '100-120':'100%% irrigation rate from first square to peak bloom and 120%% irrigation rate from peak bloom to 90%% open boll',
            '120-60':'120%% irrigation rate from first square to peak bloom and 60%% irrigation rate from peak bloom to 90%% open boll',
            '120-80':'120%% irrigation rate from first square to peak bloom and 80%% irrigation rate from peak bloom to 90%% open boll',
            '120-100':'120%% irrigation rate from first square to peak bloom and 100%% irrigation rate from peak bloom to 90%% open boll',
            '120-120':'120%% irrigation rate from first square to peak bloom and 120%% irrigation rate from peak bloom to 90%% open boll'}

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
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='PlotCover')
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
    myplot.setproperty('CUL_NAME', 'Deltapine 1549 B2XF')
    myplot.setproperty('PDATE', '04/25/2016')
    myplot.setproperty('PLYR', 2016)
    myplot.setproperty('PLDAY', 116)
    myplot.setproperty('IROP', 'IR004')
    idata = dict()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+'{:03d}'.format(int(row['DOY']))
        IRVAL = row[trt_label]
        if not math.isnan(IRVAL):
            idata.update({key:round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = dict()
    fdata.update({'2016155':37.3})
    fdata.update({'2016168':37.4})
    fdata.update({'2016190':37.3})
    myplot.setproperty('FEAMN',fdata)
    cdata = dict()
    cdata.update({'2016053':'Apply RoundUp (glyphosate)'})
    cdata.update({'2016111':'Apply Aim (carfentrazone-ethyl) and Gramoxone (paraquat dichloride)'})
    cdata.update({'2016112':'Apply Prowl (pendimethalin)'})
    cdata.update({'2016201':'Apply Carbine (flonicamid)'})
    cdata.update({'2016215':'Apply Carbine (flonicamid) and Pix (mepiquat chloride)'})
    cdata.update({'2016221':'Apply Transform (sulfoxaflor)'})
    cdata.update({'2016233':'Apply Sivanto (flupyradifurone)'})
    cdata.update({'2016237':'Apply Transform (sulfoxaflor)'})
    cdata.update({'2016254':'Apply Admiral (pyriproxyfen)'})
    cdata.update({'2016281':'Apply Ginstar (diuron, thidiazuron)'})
    cdata.update({'2016298':'Apply Ginstar (diuron, thidiazuron) and CottonQuik (urea sulfate, ethephon)'})
    myplot.setproperty('CH_NOTES',cdata)
    tdata = dict()
    tdata.update({'2016067':'Rip'})
    tdata.update({'2016068':'Disk'})
    tdata.update({'2016069':'Land plane'})
    tdata.update({'2016112':'Field cultivator and S-tine'})
    tdata.update({'2016336':'Root pull'})
    tdata.update({'2016337':'Disk'})
    tdata.update({'2016342':'Rip'})
    tdata.update({'2016344':'Moldboard plow'})
    tdata.update({'2016346':'Disk'})
    tdata.update({'2016347':'Land plane'})
    myplot.setproperty('TI_NOTES',tdata)
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['PlotID'] == plt_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2016'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myplot.setproperty('FRCOV',fcdata)
    #Crop development data (location unknown)
    #Using field average for each plot
    myplot.setproperty('EDATE', '05/07/2016')
    myplot.setproperty('PLYRE', 2016)
    myplot.setproperty('PLDOE', 128)
    myplot.setproperty('LF1D', '05/17/2016')
    #Soil analysis
    row = soil.loc[soil['Plot'] == plt_label]
    em38v = dict()
    if not math.isnan(row.iloc[0]['2013d260EM38V']):
        em38v.update({'2013260':round(row.iloc[0]['2013d260EM38V'],2)})
    if em38v:
        myplot.setproperty('EM38V',em38v)
    em38 = dict()
    if not math.isnan(row.iloc[0]['2015d118EM38']):
        em38.update({'2015118':round(row.iloc[0]['2015d118EM38'],2)})
    if not math.isnan(row.iloc[0]['2015d119EM38']):
        em38.update({'2015119':round(row.iloc[0]['2015d119EM38'],2)})
    if em38:
        myplot.setproperty('EM38',em38)
    slsnd = dict()
    slslt = dict()
    slcly = dict()
    slwp1 = dict()
    slwp2 = dict()
    slfc1 = dict()
    for depth in ['015','045','075','105','135','165']:
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
    slsnd_KRT = dict()
    slslt_KRT = dict()
    slcly_KRT = dict()
    slsnd2_KRT = dict()
    slslt2_KRT = dict()
    slcly2_KRT = dict()
    for depth in ['020','060','100','140','180']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd_KRT.update({int(depth):round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt_KRT.update({int(depth):round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly_KRT.update({int(depth):round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSND2'+depth]):
            slsnd2_KRT.update({int(depth):round(row.iloc[0]['SLSND2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT2'+depth]):
            slslt2_KRT.update({int(depth):round(row.iloc[0]['SLSLT2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY2'+depth]):
            slcly2_KRT.update({int(depth):round(row.iloc[0]['SLCLY2'+depth],2)})
    if slsnd_KRT:  myplot.setproperty('SLSND_KRT',slsnd_KRT)
    if slslt_KRT:  myplot.setproperty('SLSLT_KRT',slslt_KRT)
    if slcly_KRT:  myplot.setproperty('SLCLY_KRT',slcly_KRT)
    if slsnd2_KRT: myplot.setproperty('SLSND2_KRT',slsnd2_KRT)
    if slslt2_KRT: myplot.setproperty('SLSLT2_KRT',slslt2_KRT)
    if slcly2_KRT: myplot.setproperty('SLCLY2_KRT',slcly2_KRT)
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
    row = row.astype({'FBMIC':float})
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
        myplot.setproperty('FBMIC' ,round(row.iloc[0]['FBMIC' ],0))
    if not math.isnan(row.iloc[0]['FBLTH']):
        myplot.setproperty('FBLTH' ,round(row.iloc[0]['FBLTH' ],2))
    if not math.isnan(row.iloc[0]['FBUNI']):
        myplot.setproperty('FBUNI' ,round(row.iloc[0]['FBUNI' ],1))
    if not math.isnan(row.iloc[0]['FBSTR']):
        myplot.setproperty('FBSTR' ,round(row.iloc[0]['FBSTR' ],1))
    if not math.isnan(row.iloc[0]['FBELO']):
        myplot.setproperty('FBELO' ,round(row.iloc[0]['FBELO' ],1))
    if not math.isnan(row.iloc[0]['FBSFI']):
        myplot.setproperty('FBSFI' ,round(row.iloc[0]['FBSFI' ],1))
    if not math.isnan(row.iloc[0]['BBFRAC']):
        myplot.setproperty('BBFRAC',round(row.iloc[0]['BBFRAC' ],3))
    if not math.isnan(row.iloc[0]['BSFRAC']):
        myplot.setproperty('BSFRAC',round(row.iloc[0]['BSFRAC' ],3))
    if not math.isnan(row.iloc[0]['BFFRAC']):
        myplot.setproperty('BFFRAC',round(row.iloc[0]['BFFRAC' ],3))
    plots.append(myplot)
########################################################################

########################################################################
#Harvest Areas
shapefile = '../Data/'+fname+'/'+fname+'_HarvestAreas.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=42)
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='HACover')
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., 01-1A)
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
    row = row.astype({'FBMIC':float})
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
        myha.setproperty('FBMIC' ,round(row.iloc[0]['FBMIC' ],0))
    if not math.isnan(row.iloc[0]['FBLTH']):
        myha.setproperty('FBLTH' ,round(row.iloc[0]['FBLTH' ],2))
    if not math.isnan(row.iloc[0]['FBUNI']):
        myha.setproperty('FBUNI' ,round(row.iloc[0]['FBUNI' ],1))
    if not math.isnan(row.iloc[0]['FBSTR']):
        myha.setproperty('FBSTR' ,round(row.iloc[0]['FBSTR' ],1))
    if not math.isnan(row.iloc[0]['FBELO']):
        myha.setproperty('FBELO' ,round(row.iloc[0]['FBELO' ],1))
    if not math.isnan(row.iloc[0]['FBSFI']):
        myha.setproperty('FBSFI' ,round(row.iloc[0]['FBSFI' ],1))
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['HID'] == ha_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2016'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myha.setproperty('FRCOV',fcdata)
    #Soil analysis
    row = soil.loc[soil['HID'] == ha_label]
    em38v = dict()
    if not math.isnan(row.iloc[0]['2013d260EM38V']):
        em38v.update({'2013260':round(row.iloc[0]['2013d260EM38V'],2)})
    if em38v:
        myha.setproperty('EM38V',em38v)
    em38 = dict()
    if not math.isnan(row.iloc[0]['2015d118EM38']):
        em38.update({'2015118':round(row.iloc[0]['2015d118EM38'],2)})
    if not math.isnan(row.iloc[0]['2015d119EM38']):
        em38.update({'2015119':round(row.iloc[0]['2015d119EM38'],2)})
    if em38:
        myha.setproperty('EM38',em38)
    slsnd = dict()
    slslt = dict()
    slcly = dict()
    slwp1 = dict()
    slwp2 = dict()
    slfc1 = dict()
    for depth in ['015','045','075','105','135','165']:
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
    slsnd_KRT = dict()
    slslt_KRT = dict()
    slcly_KRT = dict()
    slsnd2_KRT = dict()
    slslt2_KRT = dict()
    slcly2_KRT = dict()
    for depth in ['020','060','100','140','180']:
        if not math.isnan(row.iloc[0]['SLSND'+depth]):
            slsnd_KRT.update({int(depth):round(row.iloc[0]['SLSND'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT'+depth]):
            slslt_KRT.update({int(depth):round(row.iloc[0]['SLSLT'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY'+depth]):
            slcly_KRT.update({int(depth):round(row.iloc[0]['SLCLY'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSND2'+depth]):
            slsnd2_KRT.update({int(depth):round(row.iloc[0]['SLSND2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLSLT2'+depth]):
            slslt2_KRT.update({int(depth):round(row.iloc[0]['SLSLT2'+depth],2)})
        if not math.isnan(row.iloc[0]['SLCLY2'+depth]):
            slcly2_KRT.update({int(depth):round(row.iloc[0]['SLCLY2'+depth],2)})
    if slsnd_KRT:  myha.setproperty('SLSND_KRT',slsnd_KRT)
    if slslt_KRT:  myha.setproperty('SLSLT_KRT',slslt_KRT)
    if slcly_KRT:  myha.setproperty('SLCLY_KRT',slcly_KRT)
    if slsnd2_KRT: myha.setproperty('SLSND2_KRT',slsnd2_KRT)
    if slslt2_KRT: myha.setproperty('SLSLT2_KRT',slslt2_KRT)
    if slcly2_KRT: myha.setproperty('SLCLY2_KRT',slcly2_KRT)
    found=False
    for plot in plots:
        if plot.plt_label[1:] == ha_label[:4]:
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
tdrfile = '../Data/'+fname+'/'+fname+'_SurfaceTDR.xlsx'
tdr = pd.read_excel(tdrfile,sheet_name='MiniTrase')
tubes = list()
for feature in layer:
    tid = feature.GetField('ObjectId')
    tb_label = feature.GetField('Tube') #(e.g., 01-1)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in neutronSWC shapefile.')
        sys.exit()
    mytube = neutronswc.NeutronSWC(tid=tid,geometry=geometry,tb_label=tb_label)
    #Setup swcdata with neutron and TDR measurement dates
    swcdata = dict()
    tdoys = [int(col[3:]) for col in tdr.columns if col[:3]=='DOY']
    ndoys = list(set(swc['DOY'].tolist()))
    doys = sorted(list(set(tdoys+ndoys)))
    for doy in doys:
        key = '2016'+'{:03d}'.format(doy)
        swcdata.update({key:{}})
    #Surface TDR soil water content measurements
    row = tdr.loc[tdr['PlotID'] == tb_label]
    doycols = sorted([col for col in row.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2016'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            STDR = float(row.iloc[0][doycol])/100. #cm3/cm3
            swcdata[key].update({'00TDR':round(STDR,5)})
    #Neutron soil water content data
    rows = swc.loc[swc['Tube'] == tb_label]
    rows = rows.sort_values(by='DOY')
    depcols = sorted([col for col in rows.columns if col[-2:]=='cm'])
    for i, row in rows.iterrows():
        key = '{:04d}{:03d}'.format(row.loc['Year'],row.loc['DOY'])
        for depcol in depcols:
            if not math.isnan(row.loc[depcol]):
                depth = int(depcol[1:-2])
                swcdata[key].update({depth:round(row.loc[depcol],5)})
    if swcdata:
        mytube.setproperty('SWLD',swcdata)
    found=False
    for plot in plots:
        if plot.plt_label[1:] == tb_label:
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
    cc_label = feature.GetField('CCID')  #(e.g., 01-1A)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in crop canopy shapefile.')
        sys.exit()
    mycc = cropcanopy.CropCanopy(ccid=ccid,geometry=geometry,cc_label=cc_label)
    #Crop canopy data
    htdata = dict()
    rowh = cch.loc[cch['CCID'] == cc_label]
    doycols = sorted([col for col in cch.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2016'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(rowh.iloc[0][doycol]):
            CHTD = float(rowh.iloc[0][doycol])/100. #m
            htdata.update({key:round(CHTD,2)})
    if htdata:
        mycc.setproperty('CHTD',htdata)
    wddata = dict()
    roww = ccw.loc[ccw['CCID'] == cc_label]
    doycols = sorted([col for col in ccw.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2016'+'{:03d}'.format(int(doycol[3:]))
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
            key = '2016'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(rowl.iloc[0][doycol]):
                LAID = float(rowl.iloc[0][doycol])
                laidata.update({key:round(LAID,2)})
        if laidata:
            mycc.setproperty('LAIDF',laidata)
    rowden = ccden.loc[ccden['CCID'] == cc_label]
    if not rowden.empty:
        if not math.isnan(rowden.iloc[0]['PLPD']):
            PLPD = float(rowden.iloc[0]['PLPD'])
            mycc.setproperty('PLPD',round(PLPD,1))
    rowdev = ccdev.loc[ccdev['CCID'] == cc_label]
    if not rowdev.empty:
        if not str(rowdev.iloc[0]['ADAT']) in ['nan','NaT']:
            mycc.setproperty('ADAT',rowdev.iloc[0]['ADAT'].strftime('%m/%d/%Y'))
        if not math.isnan(rowdev.iloc[0]['ADOY']):
            mycc.setproperty('ADOY',int(round(rowdev.iloc[0]['ADOY'],0)))
        nawf = dict()
        for doy in ['193','200','207','214','221','228','235','242','256']:
            if not math.isnan(rowdev.iloc[0]['NAWF'+doy]):
                nawf.update({'2016'+doy:round(float(rowdev.iloc[0]['NAWF'+doy]),1)})
        if nawf:
            mycc.setproperty('NAWF',nawf)
    found = False
    for plot in plots:
        if plot.plt_label[1:] == cc_label[:4]:
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
        print('Unexpected spatial reference in plant analysis shapefile.')
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
    sc_label = feature.GetField('Core')  #(e.g., N1)
    plt_label = feature.GetField('Plot') #(e.g., p01-1)
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
    items={'SNO3':1}
    for item in items.keys():
        scdata = dict()
        for depth in [15,45,75,105]:
            row = sc[(sc['Sample'] == sc_label) & (sc['Depth'] == depth)]
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                scdata.update({depth:value})
        if scdata:
            mysc.setproperty(item,scdata)
    found = False
    for plot in plots:
        if plot.plt_label == plt_label:
            plot.addscid(mysc.getid())
            found = True
            break
    if not found:
        raise Exception('Did not find plot for soil chemistry %s' % sc_label)
    scs.append(mysc)
########################################################################

########################################################################
#Soil Analysis
shapefile = '../Data/Soil/F013B4_SoilAnalysis_DJH.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
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

shapefile = '../Data/Soil/F013B4_SoilAnalysis_KRT.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
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
