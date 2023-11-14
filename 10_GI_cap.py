# -*- coding: utf-8 -*-
"""
Calculates m2 nature per capita

@author: jvano
"""

import arcpy
from arcpy.sa import *
import pandas as pd
import geopandas as gpd
import numpy as np
import glob, os
from pathlib import Path
arcpy.env.overwriteOutput = True

p = 'E:/Paper IV/Data/GIS_data/Invest/LULC/'
out = 'E:/Paper IV/Data/GIS_data/GI_cap/'
scen = ['base_unsigned', 'DB_1_BGT_EbA_HR', 'DB_3_BGT_EbA_HR', 'R_1_BGT_EbA_HR', 'R_3_BGT_EbA_HR', 'DB_1_BGT_EbA_LR', 'DB_3_BGT_EbA_LR', 'R_1_BGT_EbA_LR', 'R_3_BGT_EbA_LR']
# only high-rise
scen = ['base_unsigned', 'DB_1_BGT_EbA_HR', 'DB_3_BGT_EbA_HR', 'R_1_BGT_EbA_HR', 'R_3_BGT_EbA_HR']
pp = 'E:/Paper IV/Data/GIS_data/Inwoners/'
pop = ['hoog_DichtBijInwoners_2050.tif', 'hoog_RuimInwoners_2050.tif', 'Inwoners_2021_roundoff.tif']

#%% Focal statistics of green infrastructure
for s in scen:
    print(s)
    # Create map with vegetation (1) only. Other land-use types are classified as NODATA
    out_raster = arcpy.sa.Reclassify(p+s+".tif", "Value", "1 NODATA;2 NODATA;3 1;4 1;5 NODATA;6 1;7 1;8 NODATA;9 1;10 1;11 1;12 1;13 1;14 1;15 NODATA;16 NODATA; 17 NODATA;18 1;19 1;20 1;21 1;22 NODATA", "DATA"); out_raster.save(out+s+"_RC.tif")
    #grey infra map
    out_raster = arcpy.sa.Reclassify(p+s+".tif", "Value", "1 1;2 NODATA;3 NODATA;4 NODATA;5 1;6 NODATA;7 NODATA;8 NODATA;9 NODATA;10 NODATA;11 NODATA;12 NODATA;13 NODATA;14 NODATA;15 NODATA;16 NODATA; 17 NODATA;18 NODATA;19 NODATA;20 NODATA;21 NODATA;22 NODATA", "DATA"); out_raster.save(out+s+"grey_RC.tif")
    # Performs a neighborhood operation: each output cell is the sum of values within a rectangle of x cells. 
    OutRas = FocalStatistics(out+s+"_RC.tif", NbrRectangle(100,100,"CELL"), "SUM", "DATA")
    OutRas.save(out+s+"_FS.tif")

#%% Focal statistics of population
for p in pop:
    print(p)
    outRas = FocalStatistics(pp+p, NbrRectangle(100, 100, "CELL"), "SUM", "DATA")
    outRas.save(out+'/FS_'+p)
    
#%% Divide focal statistics of GI by focal statistics of pop
path_NL = 'E:/Paper IV/Data/GIS_data/NL/NL_nowater.shp'
pop = ['Inwoners_2021_roundoff.tif','hoog_DichtBijInwoners_2050.tif','hoog_DichtBijInwoners_2050.tif', 'hoog_RuimInwoners_2050.tif', 'hoog_RuimInwoners_2050.tif','hoog_DichtBijInwoners_2050.tif','hoog_DichtBijInwoners_2050.tif', 'hoog_RuimInwoners_2050.tif', 'hoog_RuimInwoners_2050.tif']    

for s,p in zip(scen,pop):
    print(s)
    rcc = RasterCalculator([out+s+"_FS.tif",out+'/FS_'+p], ['GI','pop'], 'GI/pop') 
    rcc.save(out+s+'_cap.tif')
    arcpy.ia.ZonalStatisticsAsTable(path_NL, "FID", out+s+'_cap.tif', out+s+'_cap.dbf', "DATA", "MEAN", "CURRENT_SLICE", [90], "AUTO_DETECT", "ARITHMETIC", 360)
    arcpy.conversion.TableToExcel( out+s+'_cap.dbf',  out+s+'_cap.xlsx')
    