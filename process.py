import numpy as np
fh = open('trace.in')
raw = fh.readline()
dbm=np.array([float(i) for i in raw.rstrip('\n,').split(',')])
fh.close()
f = np.linspace(0,15,len(dbm))
np.savetxt('trace.out',np.stack((f,(np.array(dbm)+60)/10)).transpose())

fundamental = 0
for i in range(5):
    freq = (i+1)*145.
    val = freq/1000.*15
    idx=np.abs(f-val).argmin()
    print idx
    if i==0:
        fundamental = dbm[idx]
    print freq, round(dbm[idx],1), round(dbm[idx]-fundamental,1)

