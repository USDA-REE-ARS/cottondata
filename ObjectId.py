import bson
import sys

numid = int(sys.argv[1])

f = open('ObjectId.csv','w')
f.write('ID,ObjectId\n')

for i in list(range(numid)):
    oid = str(bson.objectid.ObjectId())
    f.write('{:d},{:s}\n'.format((i+1),oid))

f.close()
