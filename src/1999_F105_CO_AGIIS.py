import os
import sys
import math
import experiment
import plot
import harvestarea
import neutronswc
import cropheight
import pandas as pd
from osgeo import ogr

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
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in experiment shapefile.')
        sys.exit()
    exp_area = geometry.GetArea()
    myexp = experiment.Experiment(eid=eid,geometry=geometry,exp_label=fname)
myexp.setproperty('EXP_AREA',round(exp_area,6))

expmeta = {
    'EXNAME':'Agricultural Irrigation Imaging System (AGIIS, "Ag Eyes"), Season 2 of 2',
    'OBJECTIVES':'See Kostrzewski, M., Waller, P., Guertin, P., Haberland, J., Colaizzi, P., Barnes, E., Thompson, T., Clarke, T., Riley, E., Choi, C., 2002. Ground-base remote sensing of water and nitrogen stress. Transactions of the ASAE. 46(1):29-38. doi:10.13031/2013.12546',
    'EXP_NARR':'See Kostrzewski, M., Waller, P., Guertin, P., Haberland, J., Colaizzi, P., Barnes, E., Thompson, T., Clarke, T., Riley, E., Choi, C., 2002. Ground-base remote sensing of water and nitrogen stress. Transactions of the ASAE. 46(1):29-38. doi:10.13031/2013.12546',
    'MAIN_FACTOR':'Optimal and low irrigation and optimal and low nitrogen',
    'FACTORS':'Optimal and low irrigation and optimal and low nitrogen',
    'TRT_NO':4,
    'REP_NO':4,
    'METHODS':'See Kostrzewski, M., Waller, P., Guertin, P., Haberland, J., Colaizzi, P., Barnes, E., Thompson, T., Clarke, T., Riley, E., Choi, C., 2002. Ground-base remote sensing of water and nitrogen stress. Transactions of the ASAE. 46(1):29-38. doi:10.13031/2013.12546',
    'EXPER_TYPE':'ET001',
    'SITE_NAME':'Maricopa Agricultural Center, Field 105',
    'SITE_TYPE':'ST001',
    'MGMT_TYPE':'MT001',
    'EXP_YEAR': '1999',
    'EXP_DUR':1,
    'CR_SYSTEM':'Cotton after winter cover crop',
    'LAST_NAME':'',
    'FIRST_NAME':'',
    'MID_INITIAL':'',
    'PERSON_NOTES':'',
    'EX_ADDRESS':'',
    'EX_EMAIL':'',
    'INSTITUTION':'',
    'IN_TYPE':'IT004',
    'IN_ROLE':'IL001',
    'CMPLC':'',
    'SUITE_NAME':'Agricultural Irrigation Imaging System (AGIIS, "Ag Eyes")',
    'SUITE_OBJ':'See Kostrzewski, M., Waller, P., Guertin, P., Haberland, J., Colaizzi, P., Barnes, E., Thompson, T., Clarke, T., Riley, E., Choi, C., 2002. Ground-base remote sensing of water and nitrogen stress. Transactions of the ASAE. 46(1):29-38. doi:10.13031/2013.12546',
    'FL_NAME':'Field 105',
    'FL_LAT':33.067406, #from Google maps
    'FL_LONG':-111.971473, #from Google maps
    'FLELE':361}
for key in expmeta.keys():
    myexp.setproperty(key,expmeta[key])

trt_info = {'WN':'Optimal water and nitrogen',
            'Wn':'Optimal water and low nitrogen',
            'wN':'Low water and optimal nitrogen',
            'wn':'Low water and low nitrogen'}

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
plots = list()
for feature in layer:
    pid = feature.GetField('ObjectId')
    plt_label = feature.GetField('Plot')
    trt_label = feature.GetField('Treatment')
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    plt_area = geometry.GetArea()
    myplot = plot.Plot(pid=pid,geometry=geometry,plt_label=plt_label,trt_label=trt_label)
    myexp.addpid(trt_label,myplot.getid())
    myplot.setproperty('PLT_AREA',round(plt_area,6))
    #Yield and fiber quality data
    row = yld.loc[yld['PID'] == plt_label]
    myplot.setproperty('HARM'  ,row.iloc[0]['HARM'])
    myplot.setproperty('HADAT' ,row.iloc[0]['HADAT'].strftime('%m/%d/%Y'))
    myplot.setproperty('WBWAH' ,round(row.iloc[0]['WBWAH' ],1))
    myplot.setproperty('FFRAC' ,round(row.iloc[0]['FFRAC' ],4))
    myplot.setproperty('SFRAC' ,round(row.iloc[0]['SFRAC' ],4))
    myplot.setproperty('TFRAC' ,round(row.iloc[0]['TFRAC' ],4))
    myplot.setproperty('WFWAH' ,round(row.iloc[0]['WFWAH' ],1))
    myplot.setproperty('WSWAH' ,round(row.iloc[0]['WSWAH' ],1))
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
    ha_label = feature.GetField('HID') #(e.g., 1N)
    geometry = feature.GetGeometryRef()
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
        if plot.plt_label == ha_label[:-1]:
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
tubes = list()
for feature in layer:
    tid = feature.GetField('ObjectId')
    tb_label = feature.GetField('Tube') #(e.g., 1N) 
    geometry = feature.GetGeometryRef()
    epsg = geometry.GetSpatialReference().GetAttrValue('AUTHORITY',1)
    if int(epsg) != 32612: #WGS84 UTM Zone 12 N
        print('Unexpected spatial reference in plot shapefile.')
        sys.exit()
    mytube = neutronswc.NeutronSWC(tid=tid,geometry=geometry,tb_label=tb_label)

    for plot in plots:
        if plot.plt_label == tb_label[:-1]:
            plot.addtid(mytube.getid())
    tubes.append(mytube)
########################################################################

########################################################################
#Write geojson files
f = open('../geojson/'+fname+'/'+fname+'_experiment.geojson','w')
f.write(myexp.__str__())
f.close()

f = open('../geojson/'+fname+'/'+fname+'_plots.geojson','w')
for myplot in plots:
    f.write(myplot.__str__())
f.close()

f = open('../geojson/'+fname+'/'+fname+'_harvestareas.geojson','w')
for myha in hareas:
    f.write(myha.__str__())
f.close()

f = open('../geojson/'+fname+'/'+fname+'_neutronswc.geojson','w')
for mytube in tubes:
    f.write(mytube.__str__())
f.close()

########################################################################
