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
    'EXNAME':'FAO-56 Irrigation Scheduling Experiment (FISE), Season 1 of 2',
    'OBJECTIVES':'See Hunsaker, D. J., Barnes, E. M., Clarke, T. R., Fitzgerald, G. J., Pinter, Jr., P. J., 2005. Cotton irrigation scheduling using remotely sensed and FAO-56 basal crop coefficients. Transactions of the ASAE. 48(4):1395-1407. doi:10.13031/2013.19197',
    'EXP_NARR':'See Hunsaker, D. J., Barnes, E. M., Clarke, T. R., Fitzgerald, G. J., Pinter, Jr., P. J., 2005. Cotton irrigation scheduling using remotely sensed and FAO-56 basal crop coefficients. Transactions of the ASAE. 48(4):1395-1407. doi:10.13031/2013.19197',
    'MAIN_FACTOR':'Irrigation scheduling method: stand-alone models versus soil water assisted models',
    'FACTORS':'Six irrigation scheduling methods and two cotton varieties',
    'TRT_NO':12,
    'REP_NO':4,
    'METHODS':'See Hunsaker, D. J., Barnes, E. M., Clarke, T. R., Fitzgerald, G. J., Pinter, Jr., P. J., 2005. Cotton irrigation scheduling using remotely sensed and FAO-56 basal crop coefficients. Transactions of the ASAE. 48(4):1395-1407. doi:10.13031/2013.19197',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 105',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '2002',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton after winter barley cover crop',
    'LAST_NAME':'Hunsaker',
    'FIRST_NAME':'Douglas',
    'MID_INITIAL':'J',
    'PERSON_NOTES':'Field technicians: C. Arterberry, A. Ashley, M. Conley, R. Jackson, S. Johnson, C. Jones, W. Luckett, S. Maneely, C. O’Brien, D. Powers, S. Richards, and R. Rokey',
    'EX_ADDRESS':'4331 E. Broadway Rd, Phoenix, Arizona 85040',
    'EX_EMAIL':'doug.hunsaker@usda.gov',
    'INSTITUTION':'USDA Agricultural Research Service, Phoenix, Arizona',
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
ccfile = '../Data/'+fname+'/'+fname+'_CropCanopy.xlsx'
cch = pd.read_excel(ccfile,sheet_name='Height')
ccw = pd.read_excel(ccfile,sheet_name='Width')
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
    myplot.setproperty('CUL_NAME', 'Deltapine 458 B/RR')
    myplot.setproperty('PDATE', '04/16/2002')
    myplot.setproperty('PLYR', 2002)
    myplot.setproperty('PLDAY', 106)
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
    if plt_label not in ['p901','p903','p905','p907']:
        row = yld.loc[yld['PID'] == plt_label]
        row = row.astype({'FBMIC':float,'FBUNI':float,'FBCRD':float})
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
        if not math.isnan(row.iloc[0]['FBCRD']):
            myplot.setproperty('FBCRD' ,round(row.iloc[0]['FBCRD' ],1))
        if not str(row.iloc[0]['FBCGR']) in ['nan','NaT']:
            myplot.setproperty('FBCGR' ,row.iloc[0]['FBCGR'])
        if not math.isnan(row.iloc[0]['FBTAR']):
            myplot.setproperty('FBTAR' ,round(row.iloc[0]['FBTAR' ],2))
    #Crop canopy data
    if plt_label not in ['p901','p903','p905','p907']:
        htdata = dict()
        rowh = cch.loc[cch['Plot'] == plt_label]
        doycols = sorted([col for col in cch.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2002'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(rowh.iloc[0][doycol]):
                CHTD = float(rowh.iloc[0][doycol])/100. #m
                htdata.update({key:round(CHTD,2)})
        if htdata:
            myplot.setproperty('CHTD',htdata)
        wddata = dict()
        roww = ccw.loc[ccw['Plot'] == plt_label]
        doycols = sorted([col for col in ccw.columns if col[:3]=='DOY'])
        for doycol in doycols:
            key = '2002'+'{:03d}'.format(int(doycol[3:]))
            if not math.isnan(roww.iloc[0][doycol]):
                CWID = float(roww.iloc[0][doycol])/100. #m
                wddata.update({key:round(CWID,2)})
        if wddata:
            myplot.setproperty('CWID',wddata)
    plots.append(myplot)
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
    tb_label = feature.GetField('Tube') #(e.g., 101)
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
        if int(plot.plt_label[1:]) == int(tb_label):
            plot.addtid(mytube.getid())
            found=True
            break
    if not found:
        raise Exception('Did not find plot for neutron tube %s' % tb_label)
    tubes.append(mytube)
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
for mytube in tubes:
    features.append(mytube.doc)
fc = geojson.FeatureCollection(features)
with open('../geojson/'+fname+'/'+fname+'_neutronswc.geojson','w') as f:
    geojson.dump(fc,f,indent=4)
f.close()
########################################################################
