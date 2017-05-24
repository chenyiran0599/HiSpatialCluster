# -*- coding: utf-8 -*-
"""
Numba Cuda code for nearest point with higher density

Created on Thu Apr 27 19:47:13 2017

@author: cheny
"""
import numpy as np
import math,time

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
            parent_gid=int(-1)
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
    blockspergrid = int((n + (threadsperblock - 1)) / threadsperblock)
    dev_nrst_dists=cuda.device_array(n)
    dev_parent_gids=cuda.device_array_like(gids)
    calc_nrst_dist_cuda[blockspergrid,threadsperblock](cuda.to_device(np.ascontiguousarray(gids))\
                       ,cuda.to_device(xs),cuda.to_device(ys),cuda.to_device(np.ascontiguousarray(densities))\
                       ,dev_nrst_dists,dev_parent_gids,n)
    return (dev_nrst_dists.copy_to_host(),dev_parent_gids.copy_to_host())
    

def calc_nrst_dist_cpu(gids,xs,ys,densities,cpu_core):
    import arcpy
    from multiprocessing.dummy import Process
    import queue
    
    n=xs.shape[0]
    
    def calc_nrst_dist_np(gidxys,result_q,gids,xs,ys,densities):
        while True:
            try:
                i=gidxys.get_nowait()
                distpow2=(xs-xs[i])**2+(ys-ys[i])**2
                distpow2[densities<=densities[i]]=1e100
                pg=distpow2.argsort()[0]
                if distpow2[pg]>1e99:
                    result_q.put((i,1e10,-1))
                else:
                    result_q.put((i,math.sqrt(distpow2[pg]),gids[pg]))
            except queue.Empty:
                break;
                
    n=xs.shape[0]
    gidxys=queue.Queue()
    result_q=queue.Queue()
    for i in range(n):
        gidxys.put(i)
    
    arcpy.SetProgressor("step", "Find Point with Higher Density on CPU...",0, n, 1)
    
    ts=[]
    for i in range(cpu_core):
        t=Process(target=calc_nrst_dist_np,args=(gidxys,result_q,gids,xs,ys,densities))
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
    result_nd=[]
    result_pg=[]
    for v in result_a:
        result_nd.append(v[1])
        result_pg.append(v[2])
    return (np.array(result_nd),np.array(result_pg)) 
        
        
    
    
