# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 07:12:46 2023
Adjusted 07/09/2023

@author: jvano
"""

import arcpy
from arcpy.sa import *
import pandas as pd
import geopandas as gpd
import numpy as np
import glob, os
from pathlib import Path

#%%
path_PBL = 'E:/Paper IV/Data/GIS_data/PBL_data'
scenarios = ['hoog_DichtBij', 'hoog_Ruim']
building_types = ['appartement', 'losstaand','rijtjeswoning']
out = 'E:/Paper IV/Data/GIS_data/Inwoners/'
I_y0 = 'E:/Paper IV/Data/GIS_data/Inwoners/Inwoners_2021.tif'

#%% Creation of population maps
for s in scenarios:
    list_bt = []
    for bt in building_types:
        btloc = path_PBL+s+'/WLO_'+s+'_Bouw_'+bt+'.tif'
        list_bt.append(btloc)
    # Sum rasters of dwellings per scenario (Mosaic to new raster)
    arcpy.management.MosaicToNewRaster(list_bt, out, s+"_mosaic.tif", 'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]', "16_BIT_UNSIGNED", None, 1, "SUM", "FIRST")
    # Remove 0's
    out_raster = arcpy.sa.Reclassify(out+s+'_mosaic.tif', "Value", "0 NODATA", "DATA"); out_raster.save(out+s+'_mosaic_reclassify.tif')
    # Assuming on average 2 persons per dwelling (based on statistics CBS huishoudensgrootte)
    out_rc = RasterCalculator([out+s+'_mosaic_reclassify.tif'],['A'],'A*2')
    out_rc.save(out+s+'_mosaic_reclassify_RC.tif')
    # Raster to point, en point to raster to convert total household size to the middle of 100x100 m cel (10x10 m)
    arcpy.conversion.RasterToPoint(out+s+'_mosaic_reclassify_RC.tif', out+s+'_mosaic_reclassify_RC.shp', "Value")
    modify_mask = RasterCalculator([out+s+'_mosaic_reclassify_RC.tif'],['A'],'Int(A*100)')
    modify_mask.save(out+s+'_mask.tif')
    # Raster to Polygon to create a mask to cut out population from 2021 map
    arcpy.conversion.RasterToPolygon(out+s+'_mask.tif', out+s+'_mask.shp', "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
    arcpy.conversion.PointToRaster(out+s+'_mosaic_reclassify_RC.shp', "grid_code", out+s+'_mosaic_reclassify_RC_PtR_10m.tif', "MOST_FREQUENT", "NONE", 10, "BUILD")    
    out_raster = arcpy.sa.ExtractByMask(I_y0, out+s+'_mask.shp', "OUTSIDE", '15400 308600 268300 606700 PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]],VERTCS["EGM96_Geoid",VDATUM["EGM96_Geoid"],PARAMETER["Vertical_Shift",0.0],PARAMETER["Direction",1.0],UNIT["Meter",1.0]]'); out_raster.save(out+s+'_clip_inwoners.tif')
    # Mosaic to create new population map
    arcpy.management.MosaicToNewRaster([out+s+'_clip_inwoners.tif',out+s+'_mosaic_reclassify_RC_PtR_10m.tif' ],out,s+'Inwoners_2050.tif','PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]', "16_BIT_UNSIGNED", None, 1, "SUM", "FIRST")

