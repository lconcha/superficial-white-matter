# code from https://github.com/khanlab/hippunfold/blob/master/hippunfold/workflow/scripts/create_warps.py

# shifts a wm surface inward along a Laplace field

import copy
import nibabel as nib
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import sys

print('starting surface shift')

in_surf = sys.argv[1]
in_laplace = sys.argv[2]
out_surf_prefix = sys.argv[3]
def arg2float_list(arg):
    return list(map(float, arg.split(',')))
if len(sys.argv)>4:
    depth = arg2float_list(sys.argv[4])
else:
    depth = [1,2,3] # default depths

convergence_threshold = 1e-4
step_size = 0.1 # mm
# the laplace gradient is very small/noisy near the outer extrema (eg. gyral peaks in V1). Thus, for the first few iterations, we will add the surface normals to the laplace gradient to help it get away from its initial start point. THIS CAN RESULT IN SELF-INTERSECTIONS
alpha = [0.75, 0.25] # start and end weightings on the normalized face normals. 
alpha_decay_exp = 2 # higher values means less use of surface normals at further depths. 
max_iters = int(depth[-1]/step_size)


# load data
surf = nib.load(in_surf)
V = surf.get_arrays_from_intent('NIFTI_INTENT_POINTSET')[0].data
F = surf.get_arrays_from_intent('NIFTI_INTENT_TRIANGLE')[0].data
laplace = nib.load(in_laplace)
lp = laplace.get_fdata()
print('loaded data and parameters')

# laplace to gradient
dx,dy,dz = np.gradient(lp)

# make interpolator of gradients
points = (range(lp.shape[0]), range(lp.shape[1]), range(lp.shape[2]))
interp_x = RegularGridInterpolator(points, dx)
interp_y = RegularGridInterpolator(points, dy)
interp_z = RegularGridInterpolator(points, dz)
print('gradient interpolator ready')

# face normal weights
weights = np.linspace(alpha[0],alpha[1],max_iters+1)**alpha_decay_exp
# normals
normals = np.ones(F.shape)*np.nan
for f in range(len(F)):
    normals[f,:] = np.cross(V[F[f,1]]-V[F[f,0]], V[F[f,2]]-V[F[f,0]])
mean_normals = np.ones(V.shape)*np.nan
for v in range(len(V)):
    i_faces = np.where(F==v)[0]
    mean_normals[v,:] = np.mean(normals[i_faces],axis=0)
# normalize the normals to 1
magnitude = np.sqrt(mean_normals[:,0]**2 + mean_normals[:,1]**2 + mean_normals[:,2]**2)
mean_normals[:,0] = mean_normals[:,0] * (step_size/magnitude)
mean_normals[:,1] = mean_normals[:,1] * (step_size/magnitude)
mean_normals[:,2] = mean_normals[:,2] * (step_size/magnitude)
print('face normals calculated and normalized')

distance_travelled = np.zeros((len(V)))
n=0
for d in depth:
    # apply inverse affine to surface to get to matrix space
    print(laplace.affine)
    V[:,:] = V - laplace.affine[:3,3].T
    for xyz in range(3):
        V[:,xyz] = V[:,xyz]*(1/laplace.affine[xyz,xyz])
    for i in range(max_iters):
        Vnew = copy.deepcopy(V)
        pts = distance_travelled < d
        stepx = interp_x(V[pts,:])
        stepy = interp_y(V[pts,:])
        stepz = interp_z(V[pts,:])
        magnitude = np.sqrt(stepx**2 + stepy**2 + stepz**2)
        if len(magnitude)>0:
            for m in range(len(pts)):
                if magnitude[m]>0:
                    stepx[m] = stepx[m] * (step_size/magnitude[m])
                    stepy[m] = stepy[m] * (step_size/magnitude[m])
                    stepy[m] = stepz[m] * (step_size/magnitude[m])
        Vnew[pts,0] += stepx*(1-weights[n]) - mean_normals[pts,0]*weights[n]
        Vnew[pts,1] += stepy*(1-weights[n]) - mean_normals[pts,1]*weights[n]
        Vnew[pts,2] += stepz*(1-weights[n]) - mean_normals[pts,2]*weights[n]
        distance_travelled[pts] += step_size
        ssd = np.sum((V-Vnew)**2,axis=None)
        print(f'itaration {i}, convergence: {ssd}, still moving: {np.sum(pts)}')
        if ssd < convergence_threshold:
            break
        V[:,:] = Vnew[:,:]
    # return to world coords
    for xyz in range(3):
        V[:,xyz] = V[:,xyz]*(laplace.affine[xyz,xyz])
    V[:,:] = V + laplace.affine[:3,3].T

    nib.save(surf, out_surf_prefix + str(d) + 'mm.surf.gii')
