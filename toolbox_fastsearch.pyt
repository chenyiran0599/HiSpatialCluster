# -*- coding: utf-8 -*-
"""
Fast Search Cluster Arcgis Python Toolbox

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
        Fast Search Cluster Arcgis Python Toolbox
        """
        self.label = "Fast Search Cluster Toolbox"
        self.alias = "fsc toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CalculateDensityTool, FindNrstDistTool, ClassifyWithCntrTool,
                      DensFilterTool, ClsBoundaryTool]
        
