# -*- coding: utf-8 -*-
"""
Numba Cuda code for calculate density.

Created on Thu Apr 27 19:47:13 2017

@author: cheny
"""


import numpy as np
import math
import time
        
def calc_density_gpu(xs,ys,weights,kernel_type,cutoffd=0,sigma=0):
    from numba import cuda, float32, float64
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
    blockspergrid = int((n + (threadsperblock - 1)) / threadsperblock)
    dev_denss=cuda.device_array(n)
    if kernel_type=='GAUSS':
        calc_density_gauss_cuda[blockspergrid,threadsperblock](cuda.to_device(xs),cuda.to_device(ys),cuda.to_device(np.ascontiguousarray(weights)),dev_denss,sigma,n)
    else:
        calc_density_cutoff_cuda[blockspergrid,threadsperblock](cuda.to_device(xs),cuda.to_device(ys),cuda.to_device(np.ascontiguousarray(weights)),dev_denss,cutoffd,n)
    return dev_denss.copy_to_host()
        
        

    
def calc_density_cpu(xs,ys,weights,kernel_type,cpu_core,cutoffd=0,sigma=0):
    from multiprocessing.dummy import Process
    import queue
    import arcpy

    xs=xs-xs.min()
    ys=ys-ys.min()
        
    def calc_density_np(gidxys,result_q,xs,ys,weights,kernel_type,cutoffd=0,sigma=0):
        while True:
            try:
                i=gidxys.get_nowait()
                distpow2=(xs-xs[i])**2+(ys-ys[i])**2
                if kernel_type=='GAUSS':
                    result_q.put( (i,((distpow2<((3*sigma)**2))*np.exp(-distpow2/(sigma**2))*weights).sum()))
                else:
                    result_q.put( (i,((distpow2<(cutoffd**2))*weights).sum()))                    
            except queue.Empty:
                break;
        
    n=xs.shape[0]
    gidxys=queue.Queue()
    result_q=queue.Queue()
    for i in range(n):
        gidxys.put(i)
    
    arcpy.SetProgressor("step", "Calculate Densities on CPU...",0, n, 1)
    
    ts=[]
    for i in range(cpu_core):
        t=Process(target=calc_density_np,args=(gidxys,result_q,xs,ys,weights,kernel_type,cutoffd,sigma))
        t.start()
        ts.append(t)
    for t in ts:
        while t.is_alive():
            arcpy.SetProgressorPosition(n-gidxys.qsize())
            time.sleep(0.05)
        
    result_a=[]
    while result_q.empty()==False:
        result_a.append(result_q.get())
    result_a.sort()
    result_d=[]
    for v in result_a:
        result_d.append(v[1])
    return np.array(result_d)