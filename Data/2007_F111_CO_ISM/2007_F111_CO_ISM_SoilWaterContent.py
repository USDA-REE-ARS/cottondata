import pandas as pd

fname = '2007_F111_CO_ISM_NeutronSWC.xlsx'
sname = 'B'
row = 7 - 1
col = 68 - 1
doy = 274

data = pd.read_excel(fname,sname,header=None)

plots = ['p02','p04','p05','p06','p07','p08','p10',
         'p11','p12','p13','p14','p15','p16','p17','p18',
         'p21','p22','p23','p24','p25','p26','p27','p28',
         'p31','p32','p33','p34','p35','p36','p37','p38',
         'p41','p42','p43','p44','p45','p46','p47','p48']

fout = open('2007_F111_CO_ISM_NeutronSWC.csv','w')

for plot in plots:
    string = '2007,'+str(doy)+',ISM,'
    string += str(plot) + ','
    if data.iloc[row,col-3] == int(plot[1:]):
        for i in list(range(13,-1,-1)):
            #print(plot,i)
            string += '{:5.3f}'.format(data.iloc[row+i,col]) + ','
        fout.write(string[:-1] + '\n')
    else:
        print('plot IDs do not match')
    row += 15

fout.close()
