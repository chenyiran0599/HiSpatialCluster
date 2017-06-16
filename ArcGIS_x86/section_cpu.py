# -*- coding: utf-8 -*-
"""
Codes for CPU Parallel Calculation.

Created on Thu Apr 27 19:47:13 2017

@author: cheny
"""
import numpy as np
import math,time
import arcpy
from multiprocessing.dummy import Process
import Queue as queue

    
def calc_density_cpu(xs,ys,weights,kernel_type,cpu_core,cutoffd=0,sigma=0):
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

def calc_nrst_dist_cpu(gids,xs,ys,densities,cpu_core):
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
