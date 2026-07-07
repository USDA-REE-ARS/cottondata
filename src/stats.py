#This script is out of date.
#It was used for a early Cotton Inc report.

import glob

#Plots
pfiles = glob.glob('../geojson/*/*_plots.geojson')
for pfile in pfiles:
    print(pfile)
keys = {'Polygon':0,'Feature':0,'geometry':0,'properties':0,'PLT_AREA':0,
        'HARM':0,'HADAT':0,'WBWAH':0,'DBWAH':0,'BWCAH':0,'GNDAT':0,
        'FFRAC':0,'SFRAC':0,'TFRAC':0,'FWCAG':0,'SWCAG':0,'DFWAH':0,
        'DSWAH':0,'DSCWAH':0,'WFWAH':0,'WSWAH':0,'WSCWAH':0,'QLDAT':0,
        'FBMIC':0,'FBLTH':0,'FBUNI':0,'FBSTR':0,'FBELO':0,'FBCRD':0,
        'FBCLB':0,'FBCGR':0,'FBTCT':0,'FBTAR':0,'FBSFI':0,'CUL_NAME':0,
        'PDATE':0,'IRVAL':0,'SWLD':0,'CHTD':0,'CWID':0,'PLPAD':0,'STDD':0}
for pfile in sorted(pfiles):
    f = open(pfile,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        for key in keys:
            if key in line:
                keys[key] = keys[key]+1
    #print(pfile,keys['WBWAH'],keys['Polygon'])

for key in sorted(keys.keys()):
    print(key,keys[key])

#Zones
zfiles = glob.glob('../geojson/*/*_zones.geojson')
for zfile in zfiles:
    print(zfile)
keys = {'Polygon':0,'Feature':0,'geometry':0,'properties':0,'ZON_AREA':0,
        'HARM':0,'HADAT':0,'WBWAH':0,'DBWAH':0,'BWCAH':0,'GNDAT':0,
        'FFRAC':0,'SFRAC':0,'TFRAC':0,'FWCAG':0,'SWCAG':0,'DFWAH':0,
        'DSWAH':0,'DSCWAH':0,'WFWAH':0,'WSWAH':0,'WSCWAH':0,'QLDAT':0,
        'FBMIC':0,'FBLTH':0,'FBUNI':0,'FBSTR':0,'FBELO':0,'FBCRD':0,
        'FBCLB':0,'FBCGR':0,'FBTCT':0,'FBTAR':0,'FBSFI':0,'CUL_NAME':0,
        'PDATE':0,'IRVAL':0}
for zfile in sorted(zfiles):
    f = open(zfile,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        for key in keys:
            if key in line:
                keys[key] = keys[key]+1
    #print(zfile,keys['WBWAH'],keys['Polygon'])

for key in sorted(keys.keys()):
    print(key,keys[key])

#Harvest areas
hafiles = glob.glob('../geojson/*/*_harvestareas.geojson')
for hafile in hafiles:
    print(hafile)
keys = {'Polygon':0,'Feature':0,'geometry':0,'properties':0,'HA_AREA':0,
        'HARM':0,'HADAT':0,'WBWAH':0,'DBWAH':0,'BWCAH':0,'GNDAT':0,
        'FFRAC':0,'SFRAC':0,'TFRAC':0,'FWCAG':0,'SWCAG':0,'DFWAH':0,
        'DSWAH':0,'DSCWAH':0,'WFWAH':0,'WSWAH':0,'WSCWAH':0,'QLDAT':0,
        'FBMIC':0,'FBLTH':0,'FBUNI':0,'FBSTR':0,'FBELO':0,'FBCRD':0,
        'FBCLB':0,'FBCGR':0,'FBTCT':0,'FBTAR':0,'FBSFI':0,'CUL_NAME':0,
        'PDATE':0,'IRVAL':0}
for hafile in sorted(hafiles):
    f = open(hafile,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        for key in keys:
            if key in line:
                keys[key] = keys[key]+1
    #print(hafile,keys['WBWAH'],keys['Polygon'])

for key in sorted(keys.keys()):
    print(key,keys[key])

#Neutron Soil Water Content
swcfiles = glob.glob('../geojson/*/*_neutronswc.geojson')
for swcfile in swcfiles:
    print(swcfile)
keys = {'Point':0,'Feature':0,'geometry':0,'properties':0,'tb_label':0,'SWLD':0}
numdats=0
numvals=0
for swcfile in sorted(swcfiles):
    f = open(swcfile,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        for key in keys:
            if key in line:
                keys[key] = keys[key]+1
        numnum = sum(c.isdigit() for c in line)
        if numnum == 7 and ": {" in line:
            numdats+=1
        if ": 0." in line:
            numvals+=1

for key in sorted(keys.keys()):
    print(key,keys[key])
print(numdats)
print(numvals)

#Crop Canopy Measurements
ccfiles = glob.glob('../geojson/*/*_cropcanopy.geojson')
for ccfile in ccfiles:
    print(ccfile)
keys = {'Point':0,'Feature':0,'geometry':0,'properties':0,'cc_label':0,'CHTD':0,'CWID':0}
numdats_ht=0
numdats_wd=0
for ccfile in sorted(ccfiles):
    f = open(ccfile,'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        for key in keys:
            if key in line:
                keys[key] = keys[key]+1
        if 'CHTD' in line:
            chtd = True
            cwid = False
        if 'CWID' in line:
            chtd = False
            cwid = True
        if ": 0." in line or ": 1." in line or ": 2." in line:
            if chtd:
                numdats_ht+=1
            if cwid:
                numdats_wd+=1

for key in sorted(keys.keys()):
    print(key,keys[key])
print(numdats_ht)
print(numdats_wd)
