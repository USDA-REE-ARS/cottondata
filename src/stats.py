import glob

#Harvest areas
hafiles = glob.glob('../geojson/*/*_harvestareas.geojson')
for hafile in hafiles:
    print(hafile)
keys = {'Polygon':0,'Feature':0,'geometry':0,'properties':0,'HA_AREA':0,
        'HARM':0,'HADAT':0,'WBWAH':0,'DBWAH':0,'BWCAH':0,'GNDAT':0,
        'FFRAC':0,'SFRAC':0,'TFRAC':0,'FWCAG':0,'SWCAG':0,'DFWAH':0,
        'DSWAH':0,'DSCWAH':0,'WFWAH':0,'WSWAH':0,'WSCWAH':0,'QLDAT':0,
        'FBMIC':0,'FBLTH':0,'FBUNI':0,'FBSTR':0,'FBELO':0,'FBCRD':0,
        'FBCLB':0,'FBCGR':0,'FBTCT':0,'FBTAR':0,'FBSFI':0}
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

#Zones
zfiles = glob.glob('../geojson/*/*_zones.geojson')
for zfile in zfiles:
    print(zfile)
keys = {'Polygon':0,'Feature':0,'geometry':0,'properties':0,'ZON_AREA':0,
        'HARM':0,'HADAT':0,'WBWAH':0,'DBWAH':0,'BWCAH':0,'GNDAT':0,
        'FFRAC':0,'SFRAC':0,'TFRAC':0,'FWCAG':0,'SWCAG':0,'DFWAH':0,
        'DSWAH':0,'DSCWAH':0,'WFWAH':0,'WSWAH':0,'WSCWAH':0,'QLDAT':0,
        'FBMIC':0,'FBLTH':0,'FBUNI':0,'FBSTR':0,'FBELO':0,'FBCRD':0,
        'FBCLB':0,'FBCGR':0,'FBTCT':0,'FBTAR':0,'FBSFI':0}
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

#Plots
pfiles = glob.glob('../geojson/*/*_plots.geojson')
for pfile in pfiles:
    print(pfile)
keys = {'Polygon':0,'Feature':0,'geometry':0,'properties':0,'PLT_AREA':0,
        'HARM':0,'HADAT':0,'WBWAH':0,'DBWAH':0,'BWCAH':0,'GNDAT':0,
        'FFRAC':0,'SFRAC':0,'TFRAC':0,'FWCAG':0,'SWCAG':0,'DFWAH':0,
        'DSWAH':0,'DSCWAH':0,'WFWAH':0,'WSWAH':0,'WSCWAH':0,'QLDAT':0,
        'FBMIC':0,'FBLTH':0,'FBUNI':0,'FBSTR':0,'FBELO':0,'FBCRD':0,
        'FBCLB':0,'FBCGR':0,'FBTCT':0,'FBTAR':0,'FBSFI':0}
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
