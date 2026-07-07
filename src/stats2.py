import glob
import geojson
import json
import sys

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

#Get geojson property keys for each shapefile type and count values
files = glob.glob('../geojson/*/*.geojson')
allkeys = dict()
shptypes = ['Experiment','Plot','Zone','CropHarvest',
            'SoilWaterContent','CropCanopy','PlantAnalysis',
            'SoilChemicalAnalysis','DJH','KRT','station']
for shptype in shptypes:
    allkeys.update({shptype:[]})
for myfile in sorted(files):
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
                        print("I don't think this should happen anymore but it did.")
                        sys.exit()
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
unique = sorted(list(set(flatten)), key=str.casefold)
for item in unique:
    fout.write(item + '\n')
fout.close()

#Get counts related to SWC measurements
fcount=0
pcount=0
mcount=0
for myfile in files:
    if '1999' in myfile:
        continue
    if 'SoilWaterContent' not in myfile:
        continue
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    for feature in gj.features:
        fcount+=1
        value = feature.properties.get('SWLD')
        if isinstance(value, list):
            mcount += len(value)
            dates = list()
            for item in value:
                dates.append(item['date'])
            dates = list(set(dates))
            pcount+=len(dates)
        elif isinstance(value, dict):
            print("I don't think this should happen anymore but it did.")
            sys.exit()
            count = count_all_values(value)
        else:
            print("This shouldn't happen either, but it did.")
print("SWC")
print("Access tubes: {:d}".format(fcount))
print("Profiles: {:d}".format(pcount))
print("Measurements: {:d}".format(mcount))

#Get number of irrigation management schedules for plots
count=0
for myfile in files:
    if '1999' in myfile:
        continue
    if 'Plot' not in myfile:
        continue
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    for feature in gj.features:
        value = feature.properties.get('IRVAL')
        if value is not None:
            count += 1
        #else:
        #    print(feature.properties.get('PDATE'))
        #    print(feature.properties.get('plt_label'))
print("Plot schedules: {:d}".format(count))

#Get number of irrigation management schedules for zones
count=0
for myfile in files:
    if '1999' in myfile:
        continue
    if 'Zone' not in myfile:
        continue
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    for feature in gj.features:
        value = feature.properties.get('IRVAL')
        if value is not None:
            count += 1
print("Zone schedules: {:d}".format(count))
