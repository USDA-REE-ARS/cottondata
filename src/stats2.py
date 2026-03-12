import glob
import geojson
import json

def count_all_values(nested_dict):
    count = 0
    for value in nested_dict.values():
        if isinstance(value, dict):
            # If the value is a dictionary, call the function recursively
            count += count_all_values(value)
        elif isinstance(value, list):
            count += len(value)
        else:
            count += 1
    return count

#Get data dictionary keys for each shapefile type and count values
files = glob.glob('../geojson/*/*.geojson')
allkeys = dict()
shptypes = ['Experiment','Plots','Zones','HarvestAreas',
            'NeutronSWC','CropCanopy','PlantAnalysis',
            'SoilChemistry','DJH','KRT']
for shptype in shptypes:
    allkeys.update({shptype:[]})
for myfile in files:
    if '1999' in myfile:
        continue
    print(myfile)
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    shptype = myfile.split('_')[-1].split('.')[0]
    #print(allkeys[shptype])
    #print(len(gj['features']))
    for feature in gj.features:
        #print(feature.properties)
        keys = feature.properties.keys()
        for key in keys:
            if key not in allkeys[shptype]:
                allkeys[shptype].append(key)
fout = open('stats2.txt','w')
condense = []
for shptype in shptypes:
    fout.write(shptype + '\n')
    for key2 in sorted(allkeys[shptype]):

        #Count features and values
        fcount = 0 #Number of features
        vcount = 0 #Number of values
        for myfile in files:
            if '1999' in myfile:
                continue
            if shptype not in myfile:
                continue
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            for feature in gj.features:
                value = feature.properties.get(key2)
                count = 0
                if value is not None:
                    if isinstance(value, list):
                        count = len(value)
                    elif isinstance(value, dict):
                        count = count_all_values(value)
                    else:
                        count = 1
                vcount+=count
                fcount+=1
        fout.write(key2 + ' ' + str(vcount) + '\n')
    fout.write("features " + str(fcount) + '\n')
    fout.write('\n')
    condense.append(sorted(allkeys[shptype]))
fout.write('\n')
fout.write('\n')
fout.write('Combined keys\n')
flatten = [item for sublist in condense for item in sublist]
unique = sorted(list(set(flatten)))
for item in unique:
    fout.write(item + '\n')
fout.close()

#Get number of soil profiles assessed with neutron probes
count=0
for myfile in files:
    if '1999' in myfile:
        continue
    if 'NeutronSWC' not in myfile:
        continue
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    for feature in gj.features:
        value = feature.properties.get('SWLD')
        if value is not None:
            count += len(value)
print(count)

#Get number of irrigation management schedules for plots
count=0
for myfile in files:
    if '1999' in myfile:
        continue
    if 'Plots' not in myfile:
        continue
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    for feature in gj.features:
        value = feature.properties.get('IRVAL')
        if value is not None:
            count += 1
print(count)

#Get number of irrigation management schedules for zones
count=0
for myfile in files:
    if '1999' in myfile:
        continue
    if 'Zones' not in myfile:
        continue
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    for feature in gj.features:
        value = feature.properties.get('IRVAL')
        if value is not None:
            count += 1
print(count)

