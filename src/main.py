import os

pyfiles = ['1999_F105_CO_AGIIS.py',
           '2002_F105_CO_FISE.py',
           '2003_F105_CO_FISE.py',
           '2007_F111_CO_ISM.py',
           '2009_F033_CO_RSIS.py',
           '2011_F033_CO_RSIS.py',
           '2014_F013B4_CO_ISOS.py',
           '2015_F013B4_CO_ISOS.py',
           '2016_F013B4_CO_ITR.py',
           '2017_F013B4_CO_ITR.py',
           '2018_F013B4_CO_ITR.py',
           '2019_F013B4_CO_PIT.py',
           '2020_F013B4_CO_PIT.py',
           '2021_F013B4_CO_ISSWC.py',
           '2022_F013B4_CO_IRATE.py',
           '2022_F013B4_CO_ISSWC.py',
           '2023_F013B4_CO_IRATE.py',
           '2023_F013B4_CO_TILL.py']

for pyfile in pyfiles:
    print('Running ' + pyfile)
    command = 'python ' + pyfile
    os.system(command)
print('Finished!')
