# HiSpatialCluster
Clustering spatial points with algorithm of Fast Search, high performace computing implements of CUDA or parallel in CPU, and runnable implements on python standalone or arcgis.

## Package Requirements for CPU:

All Package Requirements has been met with ArcGIS 10.1 and later or ArcGIS Pro.

## Package Requirements for GPU:

CUDA 7.5 or later; numba and cudatoolkit; python 64bit (using arcgis pro for python 64bit)

Install cudatoolkit in Python with Anaconda: conda insall -c numba cudatoolkit=8.0(if with CUDA 8.0)

Or install with unofficial binaries for python extension packages to avoid compiling llvmlite

## Toolbox Note

Codes are fixed to fit both Python 2 & 3, which means it is suitable for both ArcGIS Desktop with 32bit Python 2 and ArcGIS Pro with 64bit Python 3.

Because CUDA 7.5 and later requires 64bit platform, note that 32bit Python has no support for CUDA, but this tool in 32bit environments still has the parallel acceleration in CPU. It is possible to use GPU in ArcGIS Desktop with Backgroud Processing 64bit, but has not been proved yet.

## Usage

### for ArcGIS

Create folder connection to the folder of source files in ArcGIS Desktop, and open the file "toolbox_hi_spatial_cluster.pyt" in ArcGIS.

Or right click the toolbox in "project panel", click "add toolbox" in ArcGIS Pro, and choose the file "toolbox_hi_spatial_cluster.pyt".

### for python scripts

Follow the "example_work_with_postgis.py". It's prefered to use the Anaconda with python 3 64-bit.

## Method Reference

 A. Rodriguez, A. Laio, "Clustering by fast search and find of density peaks", Science, vol. 344, no. 6191, pp. 1492-1496, 2014. 

https://doi.org/10.1126/science.1242072

