#!/bin/bash

# don't forget:
# anaconda_on
# conda activate micapipe

# Run in directory where you want the tests to live

export SUBJECTS_DIR=/misc/lauterbur/lconcha/TMP/glaucoma/fs_glaucoma
sID=sub-74277
nIter_lap=100

# convert surfaces for later use
mris_convert --to-scanner ${SUBJECTS_DIR}/${sID}/surf/lh.white lh_white_scanner.gii
mris_convert --to-tkr     ${SUBJECTS_DIR}/${sID}/surf/lh.white lh_white_tkr.gii


# copy the segmentation we need
cp ${SUBJECTS_DIR}/${sID}/mri/aparc+aseg.mgz .

python /misc/lauterbur/lconcha/code/superficial-white-matter/sWM/laplace_solver.py \
  aparc+aseg.mgz \
  ${sID}_lap_${nIter_lap} \
  $nIter_lap