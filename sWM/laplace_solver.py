# code from https://github.com/khanlab/hippunfold/blob/master/hippunfold/workflow/scripts/laplace_coords.py

# solves Laplace equation over the domain of white matter, using grey matter as the source and ventricles as the sink. inputs are expected to be Free/FastSurfer aparc+aseg.mgz or .nii.gz files


import nibabel as nib
import numpy as np
import skfmm
from scipy.ndimage import binary_dilation
from astropy.convolution import convolve as nan_convolve
import sys
import os
import glob

print('starting laplace solver')
in_seg = sys.argv[1]
out_laplace = sys.argv[2]
max_iters = sys.argv[3] # was 1000

print('in_seg: '      + in_seg)
print('out_laplace: ' + out_laplace)
print('max_iters: '   + max_iters)
max_iters = int(max_iters)

# parameters
convergence_threshold = 1e-4
kernelSize = 3 # in voxels
alpha = 0.1 # add some weighting of the distance transform
fg_labels = [41, 2]
src_labels = np.concatenate((np.arange(1000,2999), [0]))
#sink_labels = [4, 43, 31, 63, 5, 44] # ventricles



# load data
lbl_nib = nib.load(in_seg)
lbl = lbl_nib.get_fdata()
print('loaded data and parameters')

# initialize foreground , source, and sink
fg = np.isin(lbl,fg_labels)
#fg = binary_dilation(fg) # dilate to make sure we always "catch" neighbouring surfaces in our gradient
source = np.isin(lbl,src_labels)
source[fg] = 0
sink = 1-fg-source
#sink = np.isin(lbl,sink_labels)

# initialize solution with fast marching
# fast march forward
phi = np.ones_like(lbl)
phi[source == 1] = 0
mask = np.ones_like(lbl)
mask[fg == 1] = 0
mask[source == 1] = 0
phi = np.ma.MaskedArray(phi, mask)
forward = skfmm.travel_time(phi, np.ones_like(lbl))
init_coords = forward.data
init_coords = init_coords-np.min(init_coords)
init_coords = init_coords / np.max(init_coords)
init_coords[fg == 0] = 0

# set up filter (27NN)
hl = np.ones([kernelSize, kernelSize, kernelSize])
hl = hl / np.sum(hl)

# initialize coords
coords = np.zeros(init_coords.shape)
coords[fg == 1] = init_coords[fg == 1]
coords[source == 1] = 0
coords[sink == 1] = 1

print('initialized solution')

upd_coords = coords.copy()

# iterate until the solution doesn't change anymore (or reach max iters)
for i in range(max_iters):

    upd_coords = nan_convolve(coords, hl, fill_value=np.nan, preserve_nan=True)

    upd_coords[source == 1] = 0
    upd_coords[sink == 1] = 1

    # check difference between last
    diff_coords = coords - upd_coords
    diff_coords[np.isnan(diff_coords)] = 0
    ssd = (diff_coords * diff_coords).sum(axis=None)
    print(f'itaration {i}, convergence: {ssd}')
    if ssd < convergence_threshold:
        break
    coords = upd_coords

coords = coords*(1-alpha) + (init_coords*alpha)

coords[source==1] = -0.01
# save file
print('saving ...')
fout = out_laplace
coords_nib = nib.Nifti1Image(coords, lbl_nib.affine, lbl_nib.header)
print(fout)
nib.save(coords_nib, out_laplace)

dx,dy,dz = np.gradient(coords)
i_d = nib.Nifti1Image(dx, lbl_nib.affine, lbl_nib.header)
fout = out_laplace + '_dx'
print(fout)
nib.save(i_d, fout)

i_d = nib.Nifti1Image(dy, lbl_nib.affine, lbl_nib.header)
fout = out_laplace + '_dy'
print(fout)
nib.save(i_d, fout)

i_d = nib.Nifti1Image(dz, lbl_nib.affine, lbl_nib.header)
fout = out_laplace + '_dz'
print(fout)
nib.save(i_d, fout)
