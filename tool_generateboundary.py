# -*- coding: utf-8 -*-
"""
Generate Class Boundaries Tool

Created on Thu May 11 11:03:05 2017

@author: cheny
"""

from arcpy import Parameter
import arcpy
from section_cpu import generate_cls_boundary
from multiprocessing import cpu_count

class ClsBoundaryTool(object):
    def __init__(self):
        """Boundaries Tool"""
        self.label = "5 Post Processing - Generate Class Boundaries"
        self.description = "Post Processing - Generate Class Boundaries"
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
        paramcntridfield = Parameter(                
                displayName="Center ID Field",
                name="cntr_id_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        paramcntridfield.parameterDependencies = [paramclsinput.name]
        paramcntridfield.filter.list = ['Short','Long']
        paramcntridfield.value='CNTR_ID'
                
        #3
        paramboundaryoutput = Parameter(
                displayName="Output Class Boundaries",
                name="boundary_output",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Output")          
        
        #4
        paramdevice = Parameter(
                displayName="Device for Calculation",
                name="calc_device",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
                )
        paramdevice.filter.list=['CPU']
        paramdevice.value='CPU'
        
        #5
        paramcpuc = Parameter(
                displayName="CPU Parallel Cores",
                name="cpu_cores",
                datatype="GPLong",
                parameterType="Required",
                direction="Input"
                )
        paramcpuc.value=cpu_count()
        
        params = [paramclsinput,paramcntridfield,paramboundaryoutput,
                  paramdevice,paramcpuc]
        return params
    
        
    def updateParameters(self, parameters):
              
        if parameters[0].altered and not parameters[2].altered:
            in_fe=parameters[0].valueAsText   
            parameters[2].value=in_fe[:len(in_fe)-4]+'_boundary'+in_fe[-4:] if in_fe[-3:]=='shp' else in_fe+'_boundary'
                          
        return


    def execute(self, parameters, messages):
        cls_input=parameters[0].valueAsText 
        cntr_id_field=parameters[1].valueAsText
        boundary_output=parameters[2].valueAsText
        
        cpu_core=parameters[4].value
        
        generate_cls_boundary(cls_input,cntr_id_field,boundary_output,cpu_core)
        
        return
