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
from scipy.spatial import Delaunay
try:
    import Queue as queue
except ImportError:
    import queue

    
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

def dens_filter_cpu(cls_input,cntr_input,id_field,cntr_id_field,dens_field,cls_output,dist_thrs,dens_thrs,cpu_core):    
    fieldsarray=[f.name for f in arcpy.Describe(cls_input).fields if f.type!='Geometry']
    fieldsarray+=['SHAPE@X','SHAPE@Y']
    
    arrays=arcpy.da.FeatureClassToNumPyArray(cls_input,fieldsarray)
    arrays=arrays[arrays[dens_field]>=dens_thrs]
    
    centerids=arcpy.da.FeatureClassToNumPyArray(cntr_input,[id_field])
    
    arcpy.SetProgressorPosition(1)
    
    centers_q=queue.Queue()
    results_q=queue.Queue()
    
    for i in centerids:
        centers_q.put(i[0])
    
    def filterbycenter(centers_q,results_q,arrays,cntr_id_field,id_field):
        while True:
            try:
                center_id=centers_q.get_nowait()
                cls_a=arrays[arrays[cntr_id_field]==center_id].copy()
                cls_q=queue.Queue()
                cls_q.put(center_id)
                cls_set=set([center_id])
                while not cls_q.empty():
                    c_p_id=cls_q.get_nowait()
                    c_p=cls_a[cls_a[id_field]==c_p_id]
                    x=c_p['SHAPE@X'][0]
                    y=c_p['SHAPE@Y'][0]
                    distpow2_a=(cls_a['SHAPE@X']-x)**2+(cls_a['SHAPE@Y']-y)**2
                    near_p_id=cls_a[distpow2_a<dist_thrs**2][id_field]
                    for i in near_p_id:
                        if i not in cls_set:
                            cls_q.put(i)
                            cls_set.add(i)
                            results_q.put(i)
                del cls_q,cls_a,cls_set                    
                
            except queue.Empty:
                break;     
          
    arcpy.SetProgressor("step", "Density Filtering Points...",0, arrays.shape[0], 1)
    
    ts=[]
    for i in range(cpu_core):
        t=Process(target=filterbycenter,args=(centers_q,results_q,arrays,cntr_id_field,id_field))
        t.start()
        ts.append(t)
    for t in ts:
        while t.is_alive():
            arcpy.SetProgressorPosition(centerids.shape[0]-centers_q.qsize())
            time.sleep(0.05)
    
    results_set=set()
    while not results_q.empty():
        results_set.add(results_q.get_nowait())
    
    results_a=[]
    for i in range(arrays.shape[0]):
        if arrays[id_field][i] in results_set:
            results_a.append(arrays[i])   
    
    if '64 bit' in sys.version and id_field==arcpy.Describe(cls_input).OIDFieldName:
        sadnl=list(arrays.dtype.names)
        sadnl[sadnl.index(id_field)]='OID@'
        arrays.dtype.names=tuple(sadnl)
        
    arcpy.da.NumPyArrayToFeatureClass(np.array(results_a,arrays.dtype),cls_output,\
                                      ('SHAPE@X','SHAPE@Y'),arcpy.Describe(cls_input).spatialReference) 
    
    return

def generate_cls_boundary(cls_input,cntr_id_field,boundary_output,cpu_core):
    arcpy.env.parallelProcessingFactor=cpu_core
    arcpy.SetProgressorLabel('Generating Delaunay Triangle...')
    arrays=arcpy.da.FeatureClassToNumPyArray(cls_input,['SHAPE@XY',cntr_id_field])
   
    cid_field_type=[f.type for f in arcpy.Describe(cls_input).fields if f.name==cntr_id_field][0]
    delaunay=Delaunay(arrays['SHAPE@XY']).simplices.copy()
    arcpy.CreateFeatureclass_management('in_memory','boundary_temp','POLYGON',spatial_reference=arcpy.Describe(cls_input).spatialReference)
    fc=r'in_memory\boundary_temp'
    arcpy.AddField_management(fc,cntr_id_field,cid_field_type)
    cursor = arcpy.da.InsertCursor(fc, [cntr_id_field,"SHAPE@"])
    arcpy.SetProgressorLabel('Copying Delaunay Triangle to Temp Layer...')
    for tri in delaunay:
        cid=arrays[cntr_id_field][tri[0]]
        if cid == arrays[cntr_id_field][tri[1]] and cid == arrays[cntr_id_field][tri[2]]:
            cursor.insertRow([cid,arcpy.Polygon(arcpy.Array([arcpy.Point(*arrays['SHAPE@XY'][i]) for i in tri]))])
    arcpy.SetProgressorLabel('Merging Delaunay Triangle...')
    arcpy.PairwiseDissolve_analysis(fc,boundary_output,cntr_id_field)
    arcpy.Delete_management(fc)
    
    return
