import pandas as pd

fname = '2011_F033_CO_RSIS_NeutronSWC.xlsx'

tabs = ['MAC 1','NDB 2','FAO 3','NDA 4',
        'MAC 5','FAO 6','NDA 7','NDB 8',
        'FAO 9','NDB 10','MAC 11','NDA 12',
        'FAO 13','NDA 14','MAC 15','NDB 16']

last = {'MAC 1':262,
        'NDB 2':262,
        'FAO 3':259,
        'NDA 4':259,
        'MAC 5':262,
        'FAO 6':259,
        'NDA 7':259,
        'NDB 8':262,
        'FAO 9':259,
        'NDB 10':262,
        'MAC 11':262,
        'NDA 12':259,
        'FAO 13':259,
        'NDA 14':259,
        'MAC 15':262,
        'NDB 16':262}

depths = [10,30,50,70,90,110,130,150,170,190,210,230,250,270,290]

fout = open('2011_F033_CO_RSIS_NeutronSWC.csv','w')

for tab in tabs:
    data = pd.read_excel(fname,tab,header=None)
    col = 1
    endcol = False
    while not endcol:

        row = 2

        doy = str(data.iloc[row,col])
        if doy[:3] not in ['DOY']:
            raise Exception("Not the right DOY cell")
        else:
            doy = int(doy[3:])

        for i in list(range(1,8)):
            row+=2
            plotnum = float(data.iloc[row,col])
            plotid = 'p{:02d}-{:d}'.format(int(str(int(plotnum))[:-1]),int(str(int(plotnum))[-1]))

            string = '2009,'+str(doy)+',RSIS,'+plotid+','

            for j in list(range(14,-1,-1)):
                if int(data.iloc[row+j,col+1]) != depths[j]:
                    raise Exception("Not the right depth")
                else:
                    string += '{:5.3f},'.format(float(data.iloc[row+j,col+2]))

            fout.write(string[:-1] + '\n')

            row+=14

        col+=7

        if doy==last[tab]:
            col = 1
            endcol = True

fout.close()
