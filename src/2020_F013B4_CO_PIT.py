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
numrep = 6

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
    'EXNAME':'Precision irrigation technologies, Season 2 of 2',
    'OBJECTIVES':'See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'EXP_NARR':'See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'MAIN_FACTOR':'Irrigation management methods: increasing complexity of technologies used',
    'FACTORS':'Four irrigation management methods',
    'TRT_NO':4,
    'REP_NO':6,
    'METHODS':'See See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 13, Bench 4',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2020',
    'EXP_DUR':1,
    'CR_SYSTEM':'No-till cotton after winter barley cover crop',
    'LAST_NAME':'Thorp',
    'FIRST_NAME':'Kelly',
    'MID_INITIAL':'R',
    'PERSON_NOTES':'Field technicians: Matt Hagler and Suzette Maneely',
    'EX_ADDRESS':'21881 N. Cardon Ln., Maricopa, Arizona 85138',
    'EX_EMAIL':'kelly.thorp@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Maricopa, Arizona',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'Intense heat stress in late summer',
    'SUITE_NAME':'Precision irrigation technologies',
    'SUITE_OBJ':'See Thorp, K. R., Calleja, S., Pauli, D., Thompson, A. L., Elshikha, D. E., 2022. Agronomic outcomes of precision irrigation management technologies. Journal of the ASABE 65(1):135-150. doi:10.13031/ja.14950',
    'FL_NAME':'Field 13, Bench 4, Spans 4-6',
    'FL_LAT':33.07914, #from Google maps
    'FL_LONG':-111.97737, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'MDL':'Irrigation scheduling via an ET-based FAO56 soil water balance model, uniform irrigation',
            'SOL':'Irrigation scheduling via an ET-based FAO56 soil water balance model with site-specific soil inputs, site-specific irrigation',
            'UAS':'Irrigation scheduling via an ET-based FAO56 soil water balance model with site-specific soil inputs and basal crop coefficients, uniform irrigation',
            'VRI':'Irrigation scheduling via an ET-based FAO56 soil water balance model with site-specific soil inputs and basal crop coefficients, site-specific irrigation'}

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
    plt_label = feature.GetField('PlotID')
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
    myplot.setproperty('CUL_NAME', 'NexGen 5007 B2XF')
    myplot.setproperty('PDATE', '04/21/2020')
    myplot.setproperty('PLYR', 2020)
    myplot.setproperty('PLDAY', 112)
    myplot.setproperty('IROP', 'IR004')
    idata = dict()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+'{:03d}'.format(int(row['DOY']))
        if trt_label in ['MDL','UAS']:
            IRVAL = row[trt_label]
        else:
            trtplt = trt_label+plt_label[1:]
            pzones = [pzone for pzone in row.keys() if trtplt in pzone]
            IRVAL = row[pzones].mean()
        if not math.isnan(IRVAL):
            idata.update({key:round(IRVAL,1)})
    if idata:
        myplot.setproperty('IRVAL',idata)
    fdata = dict()
    fdata.update({'2020156':58.4})
    fdata.update({'2020178':38.9})
    fdata.update({'2020199':38.9})
    myplot.setproperty('FEAMN',fdata)
    myplot.setproperty('FEAMP',{'2020339':40.4})
    cdata = dict()
    cdata.update({'2020084':'Apply RoundUp (glyphosate)'})
    cdata.update({'2020100':'Apply Prowl (pendimethalin)'})
    cdata.update({'2020148':'Apply RoundUp (glyphosate)'})
    cdata.update({'2020189':'Apply RoundUp (glyphosate)'})
    cdata.update({'2020197':'Apply Carbine 50WG (flonicamid)'})
    cdata.update({'2020269':'Apply Ginstar (diuron, thidiazuron) and CottonQuik (urea sulfate, ethephon)'})
    cdata.update({'2020290':'Apply Ginstar (diuron, thidiazuron) and CottonQuik (urea sulfate, ethephon)'})
    myplot.setproperty('CH_NOTES',cdata)
    tdata = dict()
    tdata.update({'2020324':'Root pull'})
    tdata.update({'2020329':'Disk and rip'})
    tdata.update({'2020335':'Moldboard plow'})
    tdata.update({'2020336':'Disk and land plane'})
    tdata.update({'2020340':'S-tine'})
    myplot.setproperty('TI_NOTES',tdata)
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['PlotID'] == plt_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2020'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myplot.setproperty('FRCOV',fcdata)
    #Soil analysis
    row = soil.loc[soil['Plot'] == plt_label]
    em38 = dict()
    if not math.isnan(row.iloc[0]['2013d260EM38']):
        em38.update({'2013260':round(row.iloc[0]['2013d260EM38'],2)})
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
    row = row.astype({'FBTCT':float})
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
    if not math.isnan(row.iloc[0]['FWCAG']):
        myplot.setproperty('FWCAG' ,round(row.iloc[0]['FWCAG' ],2))
    if not math.isnan(row.iloc[0]['SWCAG']):
        myplot.setproperty('SWCAG' ,round(row.iloc[0]['SWCAG' ],2))
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
#Zones
shapefile = '../Data/'+fname+'/'+fname+'_Zones.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
shapes = driver.Open(shapefile, 0)
layer = shapes.GetLayer()
yfile = '../Data/'+fname+'/'+fname+'_Yield_Quality.xlsx'
yld = pd.read_excel(yfile,sheet_name='Zone Scale',skiprows=5)
mfile = '../Data/'+fname+'/'+fname+'_Management.xlsx'
irrig = pd.read_excel(mfile,sheet_name='IrrigationDF')
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='ZoneCover')
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilZones')
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
    idata = dict()
    for index, row in irrig.iterrows():
        key = str(int(row['Year']))+str(int(row['DOY']))
        izid = [izid for izid in row.keys() if zon_label in izid]
        if len(izid) == 0:
            continue
        elif len(izid) == 1:
            IRVAL = row[izid[0]]
            if not math.isnan(IRVAL):
                idata.update({key:round(IRVAL,1)})
        else:
            print('Unexpected zone search result.')
            sys.exit()
    if idata:
        myzone.setproperty('IRVAL',idata)
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['ZoneID'] == zon_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2020'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myzone.setproperty('FRCOV',fcdata)
    #Soil analysis
    row = soil.loc[soil['ZoneID'] == zon_label]
    em38 = dict()
    if not math.isnan(row.iloc[0]['2013d260EM38']):
        em38.update({'2013260':round(row.iloc[0]['2013d260EM38'],2)})
    if not math.isnan(row.iloc[0]['2015d118EM38']):
        em38.update({'2015118':round(row.iloc[0]['2015d118EM38'],2)})
    if not math.isnan(row.iloc[0]['2015d119EM38']):
        em38.update({'2015119':round(row.iloc[0]['2015d119EM38'],2)})
    if em38:
        myzone.setproperty('EM38',em38)
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
    if slsnd: myzone.setproperty('SLSND',slsnd)
    if slslt: myzone.setproperty('SLSLT',slslt)
    if slcly: myzone.setproperty('SLCLY',slcly)
    if slwp1: myzone.setproperty('SLWP1',slwp1)
    if slwp2: myzone.setproperty('SLWP2',slwp2)
    if slfc1: myzone.setproperty('SLFC1',slfc1)
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
    if slsnd_KRT:  myzone.setproperty('SLSND_KRT',slsnd_KRT)
    if slslt_KRT:  myzone.setproperty('SLSLT_KRT',slslt_KRT)
    if slcly_KRT:  myzone.setproperty('SLCLY_KRT',slcly_KRT)
    if slsnd2_KRT: myzone.setproperty('SLSND2_KRT',slsnd2_KRT)
    if slslt2_KRT: myzone.setproperty('SLSLT2_KRT',slslt2_KRT)
    if slcly2_KRT: myzone.setproperty('SLCLY2_KRT',slcly2_KRT)
    #Yield data
    row = yld.loc[yld['ZID'] == zon_label]
    if not math.isnan(row.iloc[0]['WBWAH']):
        myzone.setproperty('WBWAH',round(row.iloc[0]['WBWAH'],1))
    found=False
    for plot in plots:
        if plot.plt_label[1:] == zon_label[:2]:
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
yld = pd.read_excel(yfile,sheet_name='Raw Scale',skiprows=53)
ufile = '../Data/'+fname+'/'+fname+'_UAS.xlsx'
cover = pd.read_excel(ufile,sheet_name='HACover')
safile = '../Data/'+fname+'/'+fname+'_SoilAnalysis.xlsx'
soil = pd.read_excel(safile,sheet_name='SoilHA')
hareas = list()
for feature in layer:
    haid = feature.GetField('ObjectId')
    ha_label = feature.GetField('HID') #(e.g., p11W)
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
    row = row.astype({'FBTCT':float})
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
    if not math.isnan(row.iloc[0]['FWCAG']):
        myha.setproperty('FWCAG' ,round(row.iloc[0]['FWCAG' ],2))
    if not math.isnan(row.iloc[0]['SWCAG']):
        myha.setproperty('SWCAG' ,round(row.iloc[0]['SWCAG' ],2))
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
    #UAS crop cover fraction
    fcdata = dict()
    row = cover.loc[cover['HID'] == ha_label]
    doycols = sorted([col for col in cover.columns if col[:3]=='DOY'])
    for doycol in doycols:
        key = '2020'+'{:03d}'.format(int(doycol[3:]))
        if not math.isnan(row.iloc[0][doycol]):
            FRCOV = float(row.iloc[0][doycol])
            fcdata.update({key:round(FRCOV,3)})
    if fcdata:
        myha.setproperty('FRCOV',fcdata)
    #Soil analysis
    row = soil.loc[soil['HID'] == ha_label]
    em38 = dict()
    if not math.isnan(row.iloc[0]['2013d260EM38']):
        em38.update({'2013260':round(row.iloc[0]['2013d260EM38'],2)})
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
    tb_label = feature.GetField('TubeID') #(e.g., 11)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in neutronSWC shapefile.')
        sys.exit()
    mytube = neutronswc.NeutronSWC(tid=tid,geometry=geometry,tb_label=tb_label)
    #Neutron soil water content data
    rows = swc.loc[swc['TubeID'] == tb_label]
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
ccl = pd.read_excel(ccfile,sheet_name='LAImeter')
ccden = pd.read_excel(ccfile,sheet_name='Density')
ccdev = pd.read_excel(ccfile,sheet_name='Develop')
crpcns = list()
for feature in layer:
    ccid = feature.GetField('ObjectId')
    cc_label = feature.GetField('CCID')  #(e.g., 11N)
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
            key = '2020'+'{:03d}'.format(int(doycol[3:]))
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
            key = '2020'+'{:03d}'.format(int(doycol[3:]))
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
            key = '2020'+'{:03d}'.format(int(doycol[3:]))
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
        for doy in ['195','203','209','217','223','230','237','244','252']:
            if not math.isnan(rowdev.iloc[0]['NAWF'+doy]):
                nawf.update({'2020'+doy:round(rowdev.iloc[0]['NAWF'+doy],1)})
        if nawf:
            mycc.setproperty('NAWF',nawf)
    found = False
    for plot in plots:
        if plot.plt_label[1:] == cc_label[:2]:
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
    pa_label = feature.GetField('Sample')  #(e.g., p11-S1)
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
sc = pd.read_excel(scfile,sheet_name='SoilChemDF',skiprows=1)
scs = list()
for feature in layer:
    scid = feature.GetField('ObjectId')
    sc_label = feature.GetField('Core')  #(e.g., p12)
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in soil chemistry shapefile.')
        sys.exit()
    mysc = soilchemistry.SoilChemistry(scid=scid,geometry=geometry,sc_label=sc_label)
    #Soil chemistry data
    rows = sc[sc['Plot'] == sc_label]
    if not str(rows.iloc[0]['SOIL_DATE']) in ['nan','NaT']:
        mysc.setproperty('SOIL_DATE',rows.iloc[0]['SOIL_DATE'].strftime('%m/%d/%Y'))
    items={'SLPHW':1,'SLPHB':1,'SLEC':2,'SLOM':1,'SNO3':1,'SLPX':1,
           'SLKE':0,'SLSU':1,'SLZN':2,'SLFE':1,'SLMN':1,'SLCU':2,
           'SLCA':0,'SLMG':0,'SLNA':0,'SLCEC':1}
    for item in items.keys():
        scdata = dict()
        for depth in [20,60,100,140,180]:
            row = sc[(sc['Plot'] == sc_label) & (sc['Depth'] == depth)]
            if not math.isnan(row.iloc[0][item]):
                value = round(row.iloc[0][item],items[item])
                if items[item] == 0: value=int(value)
                scdata.update({depth:value})
        if scdata:
            mysc.setproperty(item,scdata)
    found = False
    for plot in plots:
        if plot.plt_label == sc_label:
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
            if plot.plt_label == row.iloc[0]['PlotID']:
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
            if plot.plt_label == row.iloc[0]['PlotID']:
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
