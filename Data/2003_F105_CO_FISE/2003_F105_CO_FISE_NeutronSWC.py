import pandas as pd

fname = '2003_F105_CO_FISE_NeutronSWC.xlsx'
sname = 'B'
row = 7 - 1
col = 253 - 1
doy = 282

data = pd.read_excel(fname,sname,header=None)

plots = [101,102,103,104,105,106,107,108,
         208,207,206,205,204,203,202,201,
         301,302,303,304,305,306,307,308,
         408,407,406,405,404,403,402,401]

fout = open('2003_F105_CO_FISE_NeutronSWC.csv','w')

for plot in plots:
    string = '2003,'+str(doy)+',FISE,'
    string += str(plot) + ','
    if data.iloc[row,col-3] == plot:
        for i in list(range(13,-1,-1)):
            #print(plot,i)
            string += '{:5.3f}'.format(data.iloc[row+i,col]) + ','
        fout.write(string[:-1] + '\n')
    else:
        print('plot IDs do not match')
    row += 15

fout.close()
