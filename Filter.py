

import os
import argparse
import numpy as np
import astropy
from astropy.io import fits
import matplotlib
from matplotlib import pyplot as plt
from astropy.coordinates import SkyCoord  # High-level coordinates
from astropy.coordinates import ICRS, Galactic, FK4, FK5  # Low-level frames
from astropy.coordinates import Angle, Latitude, Longitude  # Angles
import astropy.units as u
from astropy import wcs
import math
import sys

mycube=sys.argv[1]
cat_files = sys.argv[2]
#ra=sys.argv[2]
#dec=sys.argv[3]

#Open a cube file
datacube = fits.open(mycube)
data = datacube[0].data
header = datacube[0].header

#Set the World Coordinates up

w = wcs.WCS(header, naxis=2)

#Get a list of frequencies within the cube

rp = datacube[0].header['CRPIX3']
rf = datacube[0].header['CRVAL3']
df = datacube[0].header['CDELT3']
nf = datacube[0].header['NAXIS3']
xvals = rf + df*(np.arange(nf)-rp)
xvals_small=xvals[0:100]


#Determine the nubmer of pixels per beam based on the header information.

bmaj=header['BMAJ']
bmin=header['BMIN']
cdelt1=header['CDELT1']
cdelt2=header['CDELT2']

beam_pix=math.sqrt((bmaj*bmin)/(-cdelt1*cdelt2))




#Set the input location of the potential spectral line

#ra='06:05:48.86'
#dec='+00:31:47.09'
file=open(cat_files)
for line in file:
    ra,dec = line.strip().split(",")
    ra=str(ra)
    dec=str(dec)
    c = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))


#Convert the world coordinates to pixel coordinates
    ypix,xpix=c.to_pixel(w,origin=0,mode='wcs')




#Get the pixel coordinates to build a box around the potential spectarl line

    xpix1=xpix-(beam_pix/2)
    xpix2=xpix+(beam_pix/2)
    ypix1=ypix-(beam_pix/2)
    ypix2=ypix+(beam_pix/2)



#Make a list of the signal for the spectra accross all the frequencies within the cube.

    signal=[]
    for x in range(0, 100):
        value = np.nanmean(data[:,x,xpix1:xpix2,ypix1:ypix2])
        #print rms_number_x
        signal.append(value)

    signal=np.multiply(signal,1.13)



    #Determine the maximum signal value

    max_signal=np.nan_to_num(signal)
    max_value = np.amax(max_signal)


    #Calculate the local RMS from the spectra

    RMS=np.nanstd(signal)
    RMS2=str(round(RMS,2))

    if RMS>0.5 AND max_value/RMS>5:
        with open('ra_dec_cat', 'a') as f:
        f.write(str(ra)+","+str(dec)+"\n")

        #Make a spectra

        bigfig=plt.figure(figsize=(20,12))
        ax1=bigfig.add_subplot(111)
        ax1.step(xvals_small/10**6,signal,color='blue')
        ax1.set_title("Orion Nebula "+str(round(xvals[0]/10**6,2)),fontsize=18)
        ax1.set_xlabel("Frequency (MHz)",fontsize=18)
        ax1.set_ylabel("Flux (Jy)",fontsize=18)
        ax1.tick_params(labelsize=15)




        ax2=ax1.twinx()
        ax2.step(xvals_small/10**6,signal/RMS,linewidth=2, color='red')
        ax2.set_ylabel("Signal to Noise Ratio", fontsize=18)
        ax2.tick_params(labelsize=14)
        ax1.text(xvals_small[60]/10**6, max_value+4 , 'Local RMS='+str(RMS2), fontsize=18)
        ax1ylims = ax1.get_ybound()
        ax2ylims = ax2.get_ybound()
        ax1factor = 1 * 6
        ax2factor = 1 * 6


        ax1.set_yticks(np.linspace(ax1ylims[0],
                               ax1ylims[1]+(ax1factor -
                               (ax1ylims[1]+ax1ylims[0]) % ax1factor) %
                               ax1factor,
                               7))
        ax2.set_yticks(np.linspace(ax2ylims[0],
                               ax2ylims[1]+(ax2factor -
                               (ax2ylims[1]+ax2ylims[0]) % ax2factor) %
                               ax2factor,
                               7))


        bigfig.savefig("Orion_"+str(ra)+"_"+str(round(xvals[0]/10**6,0))+"_.png")
   
