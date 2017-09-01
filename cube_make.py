from astropy.io import fits
import numpy as np
import glob
import os, sys

#a list from glob
files=glob.glob('*_cube*-00*-image.fits')


files=sorted(files)
#files=files[:4]

for index, file in enumerate(files):
        chan=fits.open(file)
        if index==0:
                cube=chan[0].data[0,0,:,:].copy()
                cube.resize([1,len(files),2000,2000])
        else:
                cube[0,index,:,:]=chan[0].data[0,0,:,:]
        chan.close()

#cube=np.array([cube])

#os.rename('*_cube_*-0000*.fits', 'first.fits')

chan1=fits.open('first.fits')
chan1[0].data=cube
#chan1.header['NAXIS3']=95

chan1.writeto('Combined_sublow.fits', clobber=True)