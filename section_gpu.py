# -*- coding: utf-8 -*-
"""
Codes for GPU Caculation.

Created on Thu Apr 27 19:47:13 2017

@author: cheny
"""
import numpy as np
import math
        
def calc_density_gpu(xs,ys,weights,kernel_type,cutoffd=0,sigma=0):
    from numba import cuda, float64,float32
    @cuda.jit
    def calc_density_gauss_cuda(xs,ys,weights,densitys,sigma,n):
        '''
        Numba Cuda code for calculate density.
        xs: lons' array
        ys: lats' array
        weights: weights' array
        densitys: results' array
        sigma: param in gauss kernel
        n: array size
        '''
        i=cuda.grid(1)
        if i<n:
            xi=xs[i]
            yi=ys[i]
            density=float64(0)
            threads_hold=float32((3*sigma)**2)
            for j in range(n):
                xd=xs[j]-xi
                yd=ys[j]-yi
                weightj=weights[j]
                distpow2=xd**2+yd**2
                if distpow2<threads_hold:
                    density+=math.exp(-float64(distpow2)/(sigma**2))*weightj
            densitys[i]=density
            
    
    @cuda.jit
    def calc_density_cutoff_cuda(xs,ys,weights,densitys,cutoffd,n):
        '''
        Numba Cuda code for calculate density.
        xs: lons' array
        ys: lats' array
        weights: weights' array
        densitys: results' array
        cutoffd: param in cut-off kernel
        n: array size
        '''
        i=cuda.grid(1)
        if i<n:
            xi=xs[i]
            yi=ys[i]
            density=float64(0)
            threads_hold=cutoffd**2    
            for j in range(n):
                xd=xs[j]-xi
                yd=ys[j]-yi
                weightj=weights[j]
                distpow2=xd**2+yd**2
                if distpow2<threads_hold:
                    density+=weightj
            densitys[i]=density
            
            
    xs=np.ascontiguousarray((xs-xs.min()).astype(np.float32))
    ys=np.ascontiguousarray((ys-ys.min()).astype(np.float32))
    n=xs.shape[0]
    threadsperblock = 1024
    blockspergrid = np.int((n + (threadsperblock - 1)) / threadsperblock)
    dev_denss=cuda.device_array(n)
    if kernel_type=='GAUSS':
        calc_density_gauss_cuda[blockspergrid,threadsperblock](cuda.to_device(xs),cuda.to_device(ys),cuda.to_device(np.ascontiguousarray(weights)),dev_denss,sigma,n)
    else:
        calc_density_cutoff_cuda[blockspergrid,threadsperblock](cuda.to_device(xs),cuda.to_device(ys),cuda.to_device(np.ascontiguousarray(weights)),dev_denss,cutoffd,n)
    return dev_denss.copy_to_host()
        
        
def calc_nrst_dist_gpu(gids,xs,ys,densities):   
    from numba import cuda, float64,float32
    @cuda.jit
    def calc_nrst_dist_cuda(gids,xs,ys,densities,nrst_dists,parent_gids,n):
        '''
        Numba Cuda code for calculate nearest point with higher density.
        gids: identifier of geometry
        xs: lons' array
        ys: lats' array
        densities: densities' array
        nrst_dists: results of the nearest distance
        parent_gids: results of gid of the nearest point with higher density
        n: array size
        '''
        i=cuda.grid(1)
        if i<n:
            xi=xs[i]
            yi=ys[i]
            density=densities[i]
            nrst_dist=float32(1e100)
            parent_gid=np.int(-1)
            for j in range(n):
                xd=xs[j]-xi
                yd=ys[j]-yi
                gidd=gids[j]
                distpow2=xd**2+yd**2
                if densities[j]>density and distpow2<nrst_dist:
                    nrst_dist=distpow2
                    parent_gid=gidd
            nrst_dists[i]=math.sqrt(float64(nrst_dist))
            parent_gids[i]=parent_gid
    
    n=xs.shape[0]
    xs=np.ascontiguousarray((xs-xs.min()).astype(np.float32))
    ys=np.ascontiguousarray((ys-ys.min()).astype(np.float32))
    threadsperblock = 1024
    blockspergrid = np.int((n + (threadsperblock - 1)) / threadsperblock)
    dev_nrst_dists=cuda.device_array(n)
    dev_parent_gids=cuda.device_array_like(gids)
    calc_nrst_dist_cuda[blockspergrid,threadsperblock](cuda.to_device(np.ascontiguousarray(gids))\
                       ,cuda.to_device(xs),cuda.to_device(ys),cuda.to_device(np.ascontiguousarray(densities))\
                       ,dev_nrst_dists,dev_parent_gids,n)
    return (dev_nrst_dists.copy_to_host(),dev_parent_gids.copy_to_host())
