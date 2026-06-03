import geojson
import os

class CottonData:
    """A class containing the Maricopa precision cotton irrigation data

    Attributes
    ----------
    Experiment : dict
        Provides Experimemt geojson records based on eid
    Plot : dict
        Provides Plot geojson records based on pid
    Zone : dict
        Provides Zone geojson records based on zid
    CropHarvest : dict
        Provides CropHarvest geojson records based on chid
    SoilWaterContent : dict
        Provides SoilWaterContent geojson records based on swcid
    CropCanopy : dict
        Provides CropCanopy geojson records based on ccid
    PlantAnalysis : dict
        Provides PlantAnalysis geojson records based on paid
    SoilChemicalAnalysis : dict
        Provides SoilChemicalAnalysis geojson records based on scaid
    SoilPhysicalAnalysis : dict
        Provides SoilPhysicalAnalysis geojson records based on spaid
    Weather : dict
        Provides Weather geojson records based on wid
    exp2eid : dict
        Provides eid based on experiment code
    eid2pid : dict
        Provides pids based on eid
    pid2zid : dict
        Provides zids based on pid
    pid2chid : dict()
        Provides chids based on pid
    pid2swcid : dict()
        Provides swcids based on pid
    pid2ccid : dict()
        Provides ccids based on pid
    pid2paid : dict()
        Provides paids based on pid
    pid2scaid : dict()
        Provides scaids based on pid
    pid2spaid : dict()
        Provides spaids based on pid
    """
    def __init__(self):

        exps = ['2002_F105_CO_FISE',
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

        #Experiment
        self.Experiment = dict()
        self.exp2eid = dict()
        self.eid2pid = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_Experiment.geojson'
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            eids = list()
            for feature in gj.features:
                eid = feature['eid']
                eids.append(eid)
                if eid in self.Experiment.keys():
                    print('Non-Unique ID issue in Experiment: ' + str(eid))
                self.Experiment.update({eid:feature})
                pids = feature['properties']['pids']
                self.eid2pid.update({eid:pids})
            self.exp2eid.update({exp:eids})
        print('Loaded {:d} Experiment records'.format(len(self.Experiment)))

        #Plot
        self.Plot = dict()
        self.pid2zid = dict()
        self.pid2chid = dict()
        self.pid2swcid = dict()
        self.pid2ccid = dict()
        self.pid2paid = dict()
        self.pid2scaid = dict()
        self.pid2spaid = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_Plot.geojson'
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            for feature in gj.features:
                pid = feature['pid']
                if pid in self.Plot.keys():
                    print('Non-Unique ID issue in Plot: ' + str(pid))
                self.Plot.update({pid:feature})
                try:
                    zids = feature['properties']['zids']
                    self.pid2zid.update({pid:zids})
                except:
                    self.pid2zid.update({pid:[]})
                try:
                    chids = feature['properties']['chids']
                    self.pid2chid.update({pid:chids})
                except:
                    self.pid2chid.update({pid:[]})
                try:
                    swcids = feature['properties']['swcids']
                    self.pid2swcid.update({pid:swcids})
                except:
                    self.pid2swcid.update({pid:[]})
                try:
                    ccids = feature['properties']['ccids']
                    self.pid2ccid.update({pid:ccids})
                except:
                    self.pid2ccid.update({pid:[]})
                try:
                    paids = feature['properties']['paids']
                    self.pid2paid.update({pid:paids})
                except:
                    self.pid2paid.update({pid:[]})
                try:
                    scaids = feature['properties']['scaids']
                    self.pid2scaid.update({pid:scaids})
                except:
                    self.pid2scaid.update({pid:[]})
                try:
                    spaids = feature['properties']['spaids']
                    self.pid2spaid.update({pid:spaids})
                except:
                    self.pid2spaid.update({pid:[]})
        print('Loaded {:d} Plot records'.format(len(self.Plot)))

        #Zone
        self.Zone = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_Zone.geojson'
            if os.path.exists(myfile):
                f = open(myfile,'r')
                gj = geojson.load(f)
                f.close()
                for feature in gj.features:
                    zid = feature['zid']
                    if zid in self.Zone.keys():
                        print('Non-Unique ID issue in Zone: ' + str(zid))
                    self.Zone.update({zid:feature})
        print('Loaded {:d} Zone records'.format(len(self.Zone)))

        #CropHarvest
        self.CropHarvest = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_CropHarvest.geojson'
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            for feature in gj.features:
                chid = feature['chid']
                if chid in self.CropHarvest.keys():
                    print('Non-Unique ID issue in CropHarvest: ' + str(chid))
                self.CropHarvest.update({chid:feature})
        print('Loaded {:d} CropHarvest records'.format(len(self.CropHarvest)))

        #SoilWaterContent
        self.SoilWaterContent = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_SoilWaterContent.geojson'
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            for feature in gj.features:
                swcid = feature['swcid']
                if swcid in self.SoilWaterContent.keys():
                    print('Non-Unique ID issue in SoilWaterContent: ' + str(swcid))
                self.SoilWaterContent.update({swcid:feature})
        print('Loaded {:d} SoilWaterContent records'.format(len(self.SoilWaterContent)))

        #CropCanopy
        self.CropCanopy = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_CropCanopy.geojson'
            if os.path.exists(myfile):
                f = open(myfile,'r')
                gj = geojson.load(f)
                f.close()
                for feature in gj.features:
                    ccid = feature['id']
                    if ccid in self.CropCanopy.keys():
                        print('Non-Unique ID issue in CropCanopy: ' + str(ccid))
                    self.CropCanopy.update({ccid:feature})
        print('Loaded {:d} CropCanopy records'.format(len(self.CropCanopy)))

        #PlantAnalysis
        self.PlantAnalysis = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_PlantAnalysis.geojson'
            if os.path.exists(myfile):
                f = open(myfile,'r')
                gj = geojson.load(f)
                f.close()
                for feature in gj.features:
                    paid = feature['id']
                    if paid in self.PlantAnalysis.keys():
                        print('Non-Unique ID issue in PlantAnalysis: ' + str(paid))
                    self.PlantAnalysis.update({paid:feature})
        print('Loaded {:d} PlantAnalysis records'.format(len(self.PlantAnalysis)))

        #SoilChemicalAnalysis
        self.SoilChemicalAnalysis = dict()
        for exp in exps:
            myfile = '../geojson/'+exp+'/'+exp+'_SoilChemicalAnalysis.geojson'
            if os.path.exists(myfile):
                f = open(myfile,'r')
                gj = geojson.load(f)
                f.close()
                for feature in gj.features:
                    scaid = feature['id']
                    if scaid in self.SoilChemicalAnalysis.keys():
                        print('Non-Unique ID issue in SoilChemicalAnalysis: ' + str(scaid))
                    self.SoilChemicalAnalysis.update({scaid:feature})
        print('Loaded {:d} SoilChemicalAnalysis records'.format(len(self.SoilChemicalAnalysis)))

        #SoilPhysicalAnalysis
        self.SoilPhysicalAnalysis = dict()
        spafiles = ['F013B4_SoilPhysicalAnalysis_DJH.geojson',
                    'F013B4_SoilPhysicalAnalysis_KRT.geojson',
                    'F033_SoilPhysicalAnalysis_DJH.geojson',
                    'F105_SoilPhysicalAnalysis_DJH.geojson',
                    'F111_SoilPhysicalAnalysis_DJH.geojson']
        for spafile in spafiles:
            myfile = '../geojson/Soil/'+spafile
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            for feature in gj.features:
                spaid = feature['id']
                if spaid in self.SoilPhysicalAnalysis.keys():
                    print('Non-Unique ID issue in SoilPhysicalAnalysis: ' + str(spaid))
                self.SoilPhysicalAnalysis.update({spaid:feature})
        print('Loaded {:d} SoilPhysicalAnalysis records'.format(len(self.SoilPhysicalAnalysis)))

        #Weather
        self.Weather = dict()
        wthfiles = ['AZMET_Maricopa_station.geojson']
        for wthfile in wthfiles:
            myfile = '../geojson/Weather/'+wthfile
            f = open(myfile,'r')
            gj = geojson.load(f)
            f.close()
            for feature in gj.features:
                wid = feature['id']
                if wid in self.Weather.keys():
                    print('Non-Unique ID issue in Weather: ' + str(wid))
                self.Weather.update({wid:feature})
        print('Loaded {:d} Weather record'.format(len(self.Weather)))

        #print(len(self.exp2eid))
        #print(len(self.eid2pid))
        #count=0
        #for key in self.eid2pid.keys():
        #    count+=len(self.eid2pid[key])
        #print(count)
        #count=0
        #for key in self.pid2zid.keys():
        #    count+=len(self.pid2zid[key])
        #print(count)
        #count=0
        #for key in self.pid2chid.keys():
        #    count+=len(self.pid2chid[key])
        #print(count)
        #count=0
        #for key in self.pid2swcid.keys():
        #    count+=len(self.pid2swcid[key])
        #print(count)
        #count=0
        #for key in self.pid2ccid.keys():
        #    count+=len(self.pid2ccid[key])
        #print(count)
        #count=0
        #for key in self.pid2paid.keys():
        #    count+=len(self.pid2paid[key])
        #print(count)
        #count=0
        #for key in self.pid2scaid.keys():
        #    count+=len(self.pid2scaid[key])
        #print(count)
        #count=0
        #for key in self.pid2spaid.keys():
        #    count+=len(self.pid2spaid[key])
        #print(count)

if __name__ == "__main__":
    mycottondata = CottonData()
