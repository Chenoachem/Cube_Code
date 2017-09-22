
import astropy
from astropy.io import fits
from astropy.modeling import models
import numpy as np
import matplotlib
#get_ipython().magic(u'matplotlib inline')
from matplotlib import pyplot
import os
import sys

mycube=sys.argv[1]


#open the continuum subtracted fits file
subcube = fits.open(mycube)
data = subcube[0].data
header = subcube[0].header

# we can just delete the stokes axis
rm_cube = data[:,0:100,:,:]


#replace all the zeros with nans before doing statistical calculations
rm_cube[rm_cube==0] = np.nan



#calculate the standard deviation but ignoring nans
rms_cube=np.nanstd(rm_cube, axis=1)


#make a signal to noise map
snr=rm_cube/rms_cube

#save the signal to noise cube to a fits file
subcube[0].data = np.float32(snr)
subcube.writeto('Orion_snr.fits', clobber=True)
subcube[0].data=np.float32(rms_cube)
subcube.writeto('Orion_rms.fits', clobber=True)
