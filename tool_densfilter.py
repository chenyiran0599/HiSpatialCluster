# -*- coding: utf-8 -*-
"""
Density Filter Tool

Created on Thu May 11 11:03:05 2017

@author: cheny
"""

from arcpy import Parameter
import arcpy
from section_cpu import dens_filter_cpu
from multiprocessing import cpu_count

class DensFilterTool(object):
    def __init__(self):
        """Classify Tool"""
        self.label = "4 Post Processing - Density Filter"
        self.description = "Post Processing - Density Filter"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        #1
        paramclsinput = Parameter(
                displayName="Input Classified Points",
                name="in_cls_points",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Input")
        paramclsinput.filter.list = ["Point"]

        #2
        paramcntrinput = Parameter(
                displayName="Input Centers Points",
                name="in_cntr_points",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Input")
        paramcntrinput.filter.list = ["Point"]
        
        #3
        paramidfield = Parameter(                
                displayName="Identifier Field",
                name="id_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        paramidfield.parameterDependencies = [paramclsinput.name]
        paramidfield.filter.list = ['Short','Long']
        
        #4
        paramcntridfield = Parameter(                
                displayName="Center ID Field",
                name="cntr_id_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        paramcntridfield.parameterDependencies = [paramclsinput.name]
        paramcntridfield.filter.list = ['Short','Long']
        paramcntridfield.value='CNTR_ID'

        #5
        paramdens = Parameter(                
                displayName="Density Field",
                name="density_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        # Set the filter to accept only fields that are Short or Long type
        paramdens.filter.list = ['Short','Long','Float','Single','Double']
        paramdens.parameterDependencies = [paramclsinput.name]
        paramdens.value='DENSITY'
                
        #6
        paramclsoutput = Parameter(
                displayName="Output Classified Points",
                name="out_cls_points",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Output")
                
        #7
        paramdistthrs = Parameter(
                displayName="Distance for Density Connection",
                name="distthrs",
                datatype="GPDouble",
                parameterType="Required",
                direction="Input"
                )
        paramdistthrs.value=100.0

        #8
        paramdensthrs= Parameter(
                displayName="Density Threshold for Density Connection",
                name="densthrs",
                datatype="GPDouble",
                parameterType="Required",
                direction="Input"
                )
        paramdensthrs.value=1.2
        
        #9
        paramdevice = Parameter(
                displayName="Device for Calculation",
                name="calc_device",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
                )
        paramdevice.filter.list=['CPU']
        paramdevice.value='CPU'
        
        #10
        paramcpuc = Parameter(
                displayName="CPU Parallel Cores",
                name="cpu_cores",
                datatype="GPLong",
                parameterType="Required",
                direction="Input"
                )
        paramcpuc.value=cpu_count()
        
        params = [paramclsinput,paramcntrinput,paramidfield,
                  paramcntridfield,paramdens,paramclsoutput,
                  paramdistthrs,paramdensthrs,paramdevice,
                  paramcpuc]
        return params
    
        
    def updateParameters(self, parameters):
        if parameters[0].altered and not parameters[2].altered:
            parameters[2].value=arcpy.Describe(parameters[0].valueAsText).OIDFieldName
            
        if parameters[0].altered and not parameters[5].altered:
            in_fe=parameters[0].valueAsText   
            parameters[5].value=in_fe[:len(in_fe)-4]+'_filter'+in_fe[-4:] if in_fe[-3:]=='shp' else in_fe+'_filter'
                          
        return


    def execute(self, parameters, messages):
        cls_input=parameters[0].valueAsText 
        cntr_input=parameters[1].valueAsText
        id_field=parameters[2].valueAsText
        cntr_id_field=parameters[3].valueAsText
        dens_field=parameters[4].valueAsText
        cls_output=parameters[5].valueAsText
        
        dist_thrs=parameters[6].value
        dens_thrs=parameters[7].value
        cpu_core=parameters[9].value
        
        dens_filter_cpu(cls_input,cntr_input,id_field,
                        cntr_id_field,dens_field,cls_output,
                        dist_thrs,dens_thrs,cpu_core)
        
        return
