# -*- coding: utf-8 -*-
"""
Find Point with Higher Density

Created on Sat May  6 10:01:09 2017

@author: cheny
"""

from arcpy import Parameter
import arcpy
from multiprocessing import cpu_count
import numpy.lib.recfunctions as recfunctions
import sys


class FindNrstDistTool(object):
    def __init__(self):
        """Find Point with Higher Density Tool"""
        self.label = "2 Find Point with Higher Density Tool"
        self.description = "Find Point with Higher Density for Fast Search Cluster."
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        #1
        paraminput = Parameter(
                displayName="Input Points with Densities",
                name="in_points",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Input")
        paraminput.filter.list = ["Point"]
        
        
        #2
        paramidfield = Parameter(                
                displayName="Identifier Field",
                name="id_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        paramidfield.parameterDependencies = [paraminput.name]
        paramidfield.filter.list = ['Short','Long']
        
        #3
        paramdens = Parameter(                
                displayName="Density Field",
                name="density_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        # Set the filter to accept only fields that are Short or Long type
        paramdens.filter.list = ['Short','Long','Float','Single','Double']
        paramdens.parameterDependencies = [paraminput.name]
        paramdens.value='DENSITY'
        
        #4
        paramoutput = Parameter(
                displayName="Output Result Points",
                name="out_points",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Output")
        
        #5
        paramdevice = Parameter(
                displayName="Device for Calculation",
                name="calc_device",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
                )
        paramdevice.filter.list=['CPU','GPU']
        paramdevice.value='CPU'
        
        #6
        paramcpuc = Parameter(
                displayName="CPU Parallel Cores",
                name="cpu_cores",
                datatype="GPLong",
                parameterType="Required",
                direction="Input"
                )
        paramcpuc.value=cpu_count()
        
        params = [paraminput,paramidfield,paramdens,
                  paramoutput,paramdevice,paramcpuc]
        return params
    
    def updateParameters(self, parameters):
        
        if parameters[0].altered and not parameters[1].altered:
            parameters[1].value=arcpy.Describe(parameters[0].valueAsText).OIDFieldName
        
        if parameters[4].value=='CPU':
            parameters[5].enabled=1
        else:
            parameters[5].enabled=0   
            
        if parameters[0].altered and not parameters[3].altered:
            in_fe=parameters[0].valueAsText   
            parameters[3].value=in_fe[:len(in_fe)-4]+'_nrstdist'+in_fe[-4:] if in_fe[-3:]=='shp' else in_fe+'_nrstdist'
        
        return


    def execute(self, parameters, messages):
        input_feature=parameters[0].valueAsText 
        id_field=parameters[1].valueAsText
        dens_field=parameters[2].valueAsText
        output_feature=parameters[3].valueAsText
        calc_device=parameters[4].valueAsText
        
        if '64 bit' not in sys.version and calc_device=='GPU':
            arcpy.AddError('Platform is 32bit and has no support for GPU/CUDA.')
            return

        arcpy.SetProgressorLabel('Calculating Point with Higher Density ...')
        
        arrays=arcpy.da.FeatureClassToNumPyArray(input_feature,[id_field,'SHAPE@X','SHAPE@Y',dens_field])
        
        results=0
        if calc_device=='GPU':
            from section_gpu import calc_nrst_dist_gpu
            results=calc_nrst_dist_gpu(arrays[id_field],arrays['SHAPE@X'],arrays['SHAPE@Y'],arrays[dens_field])
        else:
            from section_cpu import calc_nrst_dist_cpu
            results=calc_nrst_dist_cpu(arrays[id_field],arrays['SHAPE@X'],arrays['SHAPE@Y'],arrays[dens_field],parameters[5].value)
        
        struct_arrays=recfunctions.append_fields(recfunctions.append_fields(recfunctions.append_fields(arrays,'NRSTDIST',data=results[0])\
                                                                            ,'PARENTID',data=results[1])\
                                                 ,'MULTIPLY',data=results[0]*arrays[dens_field],usemask=False)            
        if '64 bit' in sys.version and id_field==arcpy.Describe(input_feature).OIDFieldName:
            sadnl=list(struct_arrays.dtype.names)
            sadnl[sadnl.index(id_field)]='OID@'
            struct_arrays.dtype.names=tuple(sadnl)
            
        arcpy.da.NumPyArrayToFeatureClass(struct_arrays,output_feature,\
                                          ('SHAPE@X','SHAPE@Y'),arcpy.Describe(input_feature).spatialReference)   
            
        return
