# spatial_cluster_fs
Clustering spatial points with algorithm of Fast Search, high performace computing implements of CUDA or parallel in CPU, and runnable implements on python standalone or arcgis.

## Package Requirements for GPU:

CUDA 7.5 or later; numba and cudatoolkit; python 64bit (using arcgis pro for python 64bit)

Install with Anaconda: conda insall -c numba cudatoolkit=8.0(if with CUDA 8.0)

Or install with unofficial binaries for python extension packages to avoid compile llvmlite

## Toolbox Version

There's two version of toolbox. One is for ArcGIS Desktop that is 32bit and with Python 2.7, which has no support for CUDA. Another is for ArcGIS Pro that is 64bit and with Python 3, which is full support with CUDA.

## Method Reference

 A. Rodriguez, A. Laio, "Clustering by fast search and find of density peaks", Science, vol. 344, no. 6191, pp. 1492-1496, 2014. 

https://doi.org/10.1126/science.1242072

