datadir=DATADIR
proj=PROJ
obsnum=OBSNUM
calmodel=CALMODEL
modeldir=MODELDIR
ncpus=NCPUS
calnotxt=`echo $calmodel | sed "s/.txt//"`
imsize=4000
scale=0.0133

cd DATADIR/PROJ/OBSNUM

# Hack to work around broken PYTHONPATH lookup
if [[ ! -d mwapy ]]
then
    mkdir mwapy
    mkdir mwapy/pb
    cd mwapy/pb
    for beammatrix in $MWA_CODE_BASE/MWA_Tools/mwapy/pb/*atrix.fits
    do
        ln -s $beammatrix
    done
    cd ../../
fi


# Only run if the solutions don't already exist, and are not zero-size
if [[ ! -s *_solutions.bin ]]
then
    $aprun calibrate -j ${ncpus} -p gains_new.txt phases_new.txt -m ${modeldir}/${calmodel} -minuv 20 -applybeam ${obsnum}.ms ${obsnum}_${calnotxt}_solutions.bin
fi

#flag out the bad tile
#time $aprun flagantennae ${obsnum}.ms 87,88,96,97,98,99,100,101,102,103,106,109,112,113

# Apply the solutions (uncomment first 4 lines if it is a field observation
#if [[ ! -s *_solutions.bin ]]
#then
#       cp ../1132168688_self_solutions.bin .
#fi
time $aprun applysolutions ${obsnum}.ms ${obsnum}_${calnotxt}_solutions.bin

#set the phase centre (only for field observations) Orion = Top   GC= Bottom
#$aprun chgcentre $obsnum.ms 05h35m17.3s -05d23m28s
#$aprun chgcentre ${obsnum}.ms 17h45m40.036s -29d00m28.17s

#plot the calibration solutions
time $aprun plot_aocals.py *_solutions.bin

# Really fast clean to check the image
$aprun wsclean -name ${obsnum}_shallow -size 4000 4000 -niter 4000000 -stopnegative -scale ${scale} -pol I -smallinversion -j ${ncpus} ${obsnum}.ms