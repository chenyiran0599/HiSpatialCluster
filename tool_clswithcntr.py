# -*- coding: utf-8 -*-
"""
Created on Thu May 11 11:03:05 2017

@author: cheny
"""

from arcpy import Parameter
import arcpy
import numpy.lib.recfunctions as recfunctions
import numpy as np

class ClassifyWithCntrTool(object):
    def __init__(self):
        """Classify Tool"""
        self.label = "3 Find Center and Classify Tool"
        self.description = "Find Center and Classify for Fast Search Cluster."
        self.canRunInBackground = True
        self.cntr_addr=''
        self.cls_addr=''

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        #1
        paraminput = Parameter(
                displayName="Input Points",
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
        paramidfield.filter.list = ['Short','Long','OID']
        
        #3
        paramparentidfield = Parameter(                
                displayName="Parent ID Field",
                name="parent_id_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        paramparentidfield.parameterDependencies = [paraminput.name]
        paramparentidfield.filter.list = ['Short','Long']
        paramparentidfield.value='PARENTID'
        
        #4
        parammultifield = Parameter(                
                displayName="Multiply Field",
                name="multi_field",
                datatype="Field",
                parameterType="Required",
                direction="Input")
        # Set the filter to accept only fields that are Short or Long type
        parammultifield.filter.list = ['Short','Long','Float','Single','Double']
        parammultifield.parameterDependencies = [paraminput.name]
        parammultifield.value='MULTIPLY'
        
        #5
        paramcntroutput = Parameter(
                displayName="Output Center Points",
                name="out_cntr_points",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Output")
        
        #6
        paramclsoutput = Parameter(
                displayName="Output Classified Points",
                name="out_cls_points",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Output")
                
        #7
        paramcntrnum = Parameter(
                displayName="Maxinum Number of Center Points",
                name="cntr_num",
                datatype="GPLong",
                parameterType="Required",
                direction="Input"
                )
        paramcntrnum.value=100
        
        params = [paraminput,paramidfield,paramparentidfield,
                  parammultifield,paramcntrnum,paramcntroutput,paramclsoutput]
        return params
    
        
    def updateParameters(self, parameters):
        if parameters[0].altered and not parameters[1].altered:
            parameters[1].value=arcpy.Describe(parameters[0].valueAsText).OIDFieldName
            
        if (parameters[0].altered or parameters[4].altered) and not parameters[5].altered:#parameters[5].valueAsText==self.cntr_addr:
            in_fe=parameters[0].valueAsText            
            cntrnum=parameters[4].value
            self.cntr_addr=parameters[5].value=in_fe[:len(in_fe)-4]+'_%dcntr'%cntrnum+in_fe[-4:] if in_fe[-3:]=='shp' else in_fe+'_%dcntr'%cntrnum
            
        if (parameters[0].altered or parameters[4].altered) and not parameters[6].altered:#parameters[6].valueAsText==self.cls_addr:
            in_fe=parameters[0].valueAsText            
            cntrnum=parameters[4].value
            self.cls_addr=parameters[6].value=in_fe[:len(in_fe)-4]+'_%dcntr_cls'%cntrnum+in_fe[-4:] if in_fe[-3:]=='shp' else in_fe+'_%dcntr_cls'%cntrnum                
        return


    def execute(self, parameters, messages):
        input_feature=parameters[0].valueAsText 
        id_field=parameters[1].valueAsText
        pid_field=parameters[2].valueAsText
        multi_field=parameters[3].valueAsText
        cntr_num=parameters[4].value
        
        cntr_output=parameters[5].valueAsText
        cls_output=parameters[6].valueAsText
        
        arcpy.SetProgressor("step", "Find Center and Classify...",0, 6, 1)
        
        arrays=arcpy.da.FeatureClassToNumPyArray(input_feature,['*'])
        
        cls_cntr_a=[arrays[id_field][i] for i in arrays[multi_field].argsort()[-cntr_num:]]
        
        arcpy.SetProgressorPosition(1)
        
        cls_tree={}

        for i in range(len(arrays)):
            idx=arrays[id_field][i]
            if idx not in cls_cntr_a:
                pgid=arrays[pid_field][i]
                if pgid in cls_tree.keys():
                    cls_tree[pgid].append(idx)
                else:
                    cls_tree[pgid]=[idx]
        
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
        for i in range(len(arrays)):
            idx=arrays[id_field][i]
            result_cls.append(result_map[idx])
            if idx in cls_cntr_a:
                result_cntr.append(arrays[i])
                
        arcpy.SetProgressorPosition(4)
        
#        if id_field==arcpy.Describe(input_feature).OIDFieldName:
#            sadnl=list(arrays.dtype.names)
#            sadnl[sadnl.index(id_field)]='OID@'
#            arrays.dtype.names=tuple(sadnl)

        result_struct=recfunctions.append_fields(arrays,'CNTR_ID',data=np.array(result_cls),usemask=False)
        arcpy.da.NumPyArrayToFeatureClass(result_struct,cls_output,('Shape'),arcpy.Describe(input_feature).spatialReference)        
       
        arcpy.SetProgressorPosition(5)
        
        arcpy.da.NumPyArrayToFeatureClass(np.array(result_cntr,arrays.dtype),cntr_output,\
                                          ('Shape'),arcpy.Describe(input_feature).spatialReference) 
        
        arcpy.SetProgressorPosition(6)
        
        return
