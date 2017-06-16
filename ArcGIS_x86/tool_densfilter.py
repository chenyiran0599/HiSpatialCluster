# -*- coding: utf-8 -*-
"""
Density Filter Tool

Created on Thu May 11 11:03:05 2017

@author: cheny
"""

from arcpy import Parameter
import arcpy
import numpy.lib.recfunctions as recfunctions
import numpy as np

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
        paramidfield.filter.list = ['Short','Long','OID']
        
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
        paramdistthrs.value=30.0

        #8
        paramdensthrs= Parameter(
                displayName="Density Threshold for Density Connection",
                name="densthrs",
                datatype="GPDouble",
                parameterType="Required",
                direction="Input"
                )
        paramdensthrs.value=1.5
        
        params = [paramclsinput,paramcntrinput,paramidfield,paramcntridfield,paramdens,paramclsoutput,paramdistthrs,paramdensthrs]
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
        
        arcpy.SetProgressor("step", "Density Filtering...",0, 6, 1)
        
        arrays=arcpy.da.FeatureClassToNumPyArray(cls_input,[id_field,'SHAPE@X','SHAPE@Y',cntr_id_field,dens_field])
        
        cls_cntr_a=[arrays[id_field][i] for i in arrays[multi_field].argsort()[-cntr_num:]]
        
        arcpy.SetProgressorPosition(1)
        
        cls_tree={}

        for record in arrays:
            if record[0] not in cls_cntr_a:
                pgid=record[3]
                if pgid in cls_tree.keys():
                    cls_tree[pgid].append(record[0])
                else:
                    cls_tree[pgid]=[record[0]]
        
        arcpy.SetProgressorPosition(2)
        
        result_map={}
                
        def appendallchild(cls_tree,result_map,cur_gid,cntr_gid):
            result_map[cur_gid]=cntr_gid
            if cur_gid in cls_tree.keys():
                for c_gid in cls_tree[cur_gid]:
                    appendallchild(cls_tree,result_map,c_gid,cntr_gid)
                
        for cntr_gid in cls_cntr_a:
            appendallchild(cls_tree,result_map,cntr_gid,cntr_gid)
            
        arcpy.SetProgressorPosition(3)
        
        result_cls=[]
        result_cntr=[]
        for record in arrays:
            result_cls.append(result_map[record[0]])
            if record[0] in cls_cntr_a:
                result_cntr.append(record)
                
        arcpy.SetProgressorPosition(4)
        
        if id_field==arcpy.Describe(input_feature).OIDFieldName:
            sadnl=list(arrays.dtype.names)
            sadnl[sadnl.index(id_field)]='OID@'
            arrays.dtype.names=tuple(sadnl)
        
        arcpy.da.NumPyArrayToFeatureClass(np.array(result_cntr,arrays.dtype),cntr_output,\
                                          ('SHAPE@X','SHAPE@Y'),arcpy.Describe(input_feature).spatialReference) 
        
        arcpy.SetProgressorPosition(5)
        
        result_struct=recfunctions.append_fields(recfunctions.drop_fields(recfunctions.drop_fields(arrays,pid_field)\
                                                                          ,multi_field)\
                                                 ,'CNTR_ID',data=np.array(result_cls),usemask=False)
        arcpy.da.NumPyArrayToFeatureClass(result_struct,cls_output,('SHAPE@X','SHAPE@Y'),arcpy.Describe(input_feature).spatialReference)        
        
        arcpy.SetProgressorPosition(6)
        
        return
