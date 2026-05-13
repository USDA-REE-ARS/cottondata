import os
import glob
import geojson
import json

variable = 'zon_label'
print(variable)

#Report paths for each variable instance in geojson files
files = glob.glob('../geojson/*/*.geojson')

years = list()
fields = list()
exps = list()
shptypes = list()
vartypes = list()
#fout = open('variables.csv','w')
for myfile in sorted(files):
    f = open(myfile,'r')
    gj = geojson.load(f)
    f.close()
    mysplit = os.path.basename(myfile).split('_')
    if mysplit[1] == 'SoilPhysicalAnalysis':
        year = 'NA'
        field = mysplit[0]
        exp = 'NA'
        shptype = 'SoilPhysicalAnalysis' + mysplit[-1].split('.')[0]
    else:
        year = mysplit[0]
        field = mysplit[1]
        exp = mysplit[3]
        shptype = mysplit[-1].split('.')[0]
    for feature in gj.features:
        #print(feature.properties)
        keys = feature.properties.keys()
        for key in keys:
            if key == variable:
                vartype = type(feature.properties[key])
                string = year + ','
                string += field + ','
                string += exp + ','
                string += shptype + ','
                string += str(vartype) + '\n'
                #fout.write(string)

                if year not in years: years.append(year)
                if field not in fields: fields.append(field)
                if exp not in exps: exps.append(exp)
                if shptype not in shptypes: shptypes.append(shptype)
                if vartype not in vartypes: vartypes.append(vartype)
#fout.close()

print(years)
print(fields)
print(exps)
print(shptypes)
print(vartypes)
