import pyfao56.tools as tools
import geojson

exps = ['1999_F105_CO_AGIIS',
        '2002_F105_CO_FISE',
        '2003_F105_CO_FISE',
        '2007_F111_CO_ISM',
        '2009_F033_CO_RSIS',
        '2011_F033_CO_RSIS',
        '2014_F013B4_CO_ISOS',
        '2015_F013B4_CO_ISOS',
        '2016_F013B4_CO_ITR',
        '2017_F013B4_CO_ITR',
        '2018_F013B4_CO_ITR',
        '2019_F013B4_CO_PIT',
        '2020_F013B4_CO_PIT',
        '2021_F013B4_CO_ISSWC',
        '2022_F013B4_CO_IRATE',
        '2022_F013B4_CO_ISSWC',
        '2023_F013B4_CO_IRATE',
        '2023_F013B4_CO_TILL']

for exp in exps:

    if exp not in ['2018_F013B4_CO_ITR']:
        continue

    with open('../geojson/'+exp+'/'+exp+'_neutronswc.geojson','r') as f:
        data = geojson.load(f)

    for feature in data['features']:
        print(feature['properties']['tb_label'])
