import glob
import geojson
import json

#Get data dictionary keys for each shapefile type
files = glob.glob('../geojson/*/*.geojson')
allkeys = dict()
shptypes = ['Experiment','Plots','Zones','HarvestAreas',
            'NeutronSWC','CropCanopy','PlantAnalysis',
            'SoilChemistry','DJH','KRT']
for shptype in shptypes:
    allkeys.update({shptype:[]})
for myfile in files:
    print(myfile)
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    shptype = myfile.split('_')[-1].split('.')[0]
    print(allkeys[shptype])
    #print(len(gj['features']))
    for feature in gj.features:
        #print(feature.properties)
        keys = feature.properties.keys()
        for key in keys:
            if key not in allkeys[shptype]:
                allkeys[shptype].append(key)
f = open('stats2_keys.txt','w')
condense = []
for shptype in allkeys:
    f.write(shptype + '\n')
    for key2 in sorted(allkeys[shptype]):
        f.write(key2 + '\n')
    f.write('\n')
    condense.append(sorted(allkeys[shptype]))
f.write('\n')
f.write('\n')
f.write('Combined keys\n')
flatten = [item for sublist in condense for item in sublist]
unique = sorted(list(set(flatten)))
for item in unique:
    f.write(item + '\n')
f.close()
