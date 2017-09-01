#!/usr/bin/python
"""
Read in a calibrator binary file as produced by Andre Offringa's tools
 
These files are not documented, but you can find the relevant code by grepping for WriteSolution. The _header struct is defined at thebottom of solutionfile.h and populated at the top.
 
2016-03-23 first version john.morgan@icrar.org
"""
import os, struct, pyfits
from collections import namedtuple
import numpy as np
 
# use of struct based on:
# http://stevendkay.wordpress.com/2009/09/05/beginning-digital-elevation-model-work-with-python/
 
CAL_FILE="1124707696_self_solutions.bin"
HEADER_FORMAT="8s6I"
Header = namedtuple("header", "intro fileType structureType intervalCount antennaCount channelCount polarizationCount")
 
assert struct.calcsize("I") == 4, "Error, unexpected unsigned int size used by python struct"
assert struct.calcsize("c") == 1, "Error, unexpected char size used by python struct"
 
with open(CAL_FILE, "rb") as f:
    #first read header
    header_string = f.read(struct.calcsize(HEADER_FORMAT))
    header = Header._make(struct.unpack(HEADER_FORMAT, header_string))
    # Check header is OK
    assert header.intro[:-1] == "MWAOCAL", "File is not a calibrator file"
    assert header.fileType == 0, "fileType %d not recognised. Only 0 (complex Jones solutions) is recognised in mwatools/solutionfile.h as of 2013-08-30" % header.fileType
    assert header.structureType == 0, "structureType not recognised. Only 0 (ordered real/imag, polarization, channel, antenna, time) is recognised in mwatools/solutionfile.h as of 2013-08-30" % header.structureType
    print header
 
    f.seek(struct.calcsize(HEADER_FORMAT), os.SEEK_SET) # skip header. os.SEEK_SET means seek relative to start of file
 
    count = header.intervalCount * header.antennaCount * header.channelCount * header.polarizationCount
    #reading directly into a complex64 array doens't work for some reason: #data_complex = np.fromfile(f, dtype=np.complex64, count=count)
    raw_data = np.fromfile(f, dtype=np.float64, count=count*2)
    #reshape with each real, complex pair on the final axis
    raw_data = raw_data.reshape((header.intervalCount, header.antennaCount, header.channelCount, header.polarizationCount, 2))
    #copy into complex array
    data = np.empty((header.intervalCount, header.antennaCount, header.channelCount, header.polarizationCount), dtype=np.complex64)
    data = raw_data[:, :, :, :, 0] + 1j*raw_data[:, :, :, :, 1]
 
    #print complex, amp and phase for a small subset of the data (first interval, first antenna, a few of the channels, all 4 polarisations
    print data[0, 0, 4:32, :]
    print abs(data[0, 0, 4:64, :])
    print np.angle(data[0, 0, 4:64, :])
