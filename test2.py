#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 19:57:59 2023

@author: lconcha
"""


import copy
import nibabel as nib
import numpy as np
#from scipy.interpolate import RegularGridInterpolator
import sys
from mayavi import mlab


# in mansfield: /misc/lauterbur/lconcha/TMP/swm/
# in syphon: /datos/syphon/lconcha/tmp/laplace

in_surf_scanner = 'lh_white_scanner.gii'
in_surf_trk = 'lh_white_scanner.trk'
in_laplace = 'sub-74277_lap_100.nii'
out_surf_prefix = 'sub-74277_lap_100_beeee'
depth = 2


in_surf = in_surf_scanner

# load data
surf = nib.load(in_surf)
V = surf.get_arrays_from_intent('NIFTI_INTENT_POINTSET')[0].data
F = surf.get_arrays_from_intent('NIFTI_INTENT_TRIANGLE')[0].data
laplace = nib.load(in_laplace)
lp = laplace.get_fdata()
print('loaded data and parameters')


V2 = V.copy()
V2[:,:] = V - laplace.affine[:3,3].T
for xyz in range(3):
    V2[:,xyz] = V2[:,xyz]*(1/laplace.affine[xyz,xyz])

    
x = V[:,0]
y = V[:,1]
z = V[:,2]

x2 = V2[:,0]
y2 = V2[:,1]
z2 = V2[:,2]
 
mlab.points3d(x,y,z)
mlab.points3d(x2,y2,z2)
mlab.volume_slice(lp)
 