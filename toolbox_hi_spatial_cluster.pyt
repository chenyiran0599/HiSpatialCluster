# -*- coding: utf-8 -*-
"""
HiSpatialCluster ArcGIS Python Toolbox

Created on Fri Apr 28 11:18:13 2017

@author: cheny
"""

from tool_calculatedensity import CalculateDensityTool
from tool_findnrstdist import FindNrstDistTool
from tool_clswithcntr import ClassifyWithCntrTool
from tool_densfilter import DensFilterTool
from tool_generateboundary import ClsBoundaryTool

class Toolbox(object):
    def __init__(self):
        """
        HiSpatialCluster ArcGIS Python Toolbox
        """
        self.label = "HiSpatialCluster Toolbox"
        self.alias = "hsc toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CalculateDensityTool, FindNrstDistTool, ClassifyWithCntrTool,
                      DensFilterTool, ClsBoundaryTool]
        
