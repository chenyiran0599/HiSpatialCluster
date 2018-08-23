# HiSpatialCluster
Clustering spatial points with algorithm of Fast Search, high performace computing implements of CUDA or parallel in CPU, and runnable implements on python standalone or arcgis.

## Package Requirements for CPU:

All Package Requirements has been met with ArcGIS 10.1 and later or ArcGIS Pro.

## Package Requirements for GPU:

CUDA 7.5 or later; numba and cudatoolkit; python 64bit (using arcgis pro for python 64bit)

Install cudatoolkit in Python with Anaconda: conda install -c numba cudatoolkit=8.0(if with CUDA 8.0)

Or install with unofficial binaries for python extension packages to avoid compiling llvmlite

## Toolbox Note

Codes are fixed to fit both Python 2 & 3, which means it is suitable for both ArcGIS Desktop with 32bit Python 2 and ArcGIS Pro with 64bit Python 3.

Because CUDA 7.5 and later requires 64bit platform, note that 32bit Python has no support for CUDA, but this tool in 32bit environments still has the parallel acceleration in CPU. It is possible to use GPU in ArcGIS Desktop with Backgroud Processing 64bit, but has not been proved yet.

## Usage

### for ArcGIS

Create folder connection to the folder of source files in ArcGIS Desktop, and open the file "toolbox_hi_spatial_cluster.pyt" in ArcGIS.

Or right click the toolbox in "project panel", click "add toolbox" in ArcGIS Pro, and choose the file "toolbox_hi_spatial_cluster.pyt".

For more details about ArcGIS Python Toolbox, please see https://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/a-quick-tour-of-python-toolboxes.htm (ArcGIS Pro) or https://desktop.arcgis.com/en/arcmap/latest/analyze/creating-tools/a-quick-tour-of-python-toolboxes.htm (ArcMap).

#### Step by step

(1) Run "Calculating Density Tool" to calculate the density;

(2) Run "Finding Nearest High-Density Points Tool" to find the nearest point with higher density;

(3) Run "Finding Centers and Classification Tool" to classify, note that the results of Step 2 could be reused for different number of classes;

That's all. If the results could not meet the requirements of the research, the two steps are provided as follows:

(4) Run "Density Filtering Tool" and the noises may be removed by the threshold of density;

(5) Run "Generating Class Boundaries Tool" and the referenced boundaries for visulization may be generated.

### for python scripts

Follow the "example_work_with_postgis.py". It's prefered to use the Anaconda with python 3 64-bit.

## Method Reference

 Chen Y, Huang Z, Pei T, Liu Y. HiSpatialCluster: A novel high-performance software tool for clustering massive spatial points. *Transactions in GIS*. 2018;00:1-24. https://doi.org/10.1111/tgis.12463

