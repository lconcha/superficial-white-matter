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


 #V[:,:] = V - laplace.affine[:3,3].T

V2 = V.copy()
V3 = V.copy()


V2 = V2 - laplace.affine[:3,3].T

nvertices = V.shape[0]

for vindex in range(nvertices):
    thisv = V[vindex,:];
    
    thisv = thisv - laplace.affine[:3,3].T
    
    thisvpad = np.append(thisv,1)
    thisvpadtransformed = thisvpad.dot(laplace.affine)
    V2[vindex,:] = thisvpadtransformed[0:3]

    #thisvpad = np.append(thisv,1)
    #thisvpadtransformed = thisvpad.dot(np.linalg.inv(laplace.affine))
    #V3[vindex,:] = thisvpadtransformed[0:3]

    

#mlab.points3d(V[:,0],  V[:,1],  V[:,2], color=(1,1,1) )
mlab.points3d(V2[:,0], V2[:,1], V2[:,2], color=(1,0,0) )
#mlab.points3d(V3[:,0], V3[:,1], V3[:,2], color=(0,0,1) )
mlab.volume_slice(lp)
 
