# -*- coding: utf-8 -*-
"""
Model 3. Land use scenarios

Combining the different wallpapers (<10% building footprint, 10-40%, > 40%) for each scnenario.

@author: jvano
"""
# %%

import arcpy
import pandas as pd

from arcpy import env
from arcpy.sa import *
from osgeo import gdal
from os.path import exists

import geopandas as gpd
import pandas as pd

arcpy.env.overwriteOutput = True
# Enable ArcGIS extensions
arcpy.CheckOutExtension("Spatial")
# %%
UFA_scenarios = ['BAU']  # ,'small', 'large']
# 'low_rise', 'high_rise'] # only applies for apartments & offices
#height_scenarios = ['_high_rise', '_low_rise']
#height_scenarios_s = ['_HR', '_LR']
height_scenarios = ['_low_rise']
height_scenarios_s = ['_LR']
WLO = ['hoog_']
#scenario = ['_DichtBij_', '_Ruim_']
#scenario_kort = ['DB', 'R']

scenario = ['_Ruim_', 'DichtBij']
scenario_kort = ['R', 'DB']

WP = ['1', '2', '3']  # scenario 1 = 30% continuous GI including =>10% trees, scenario 2 = 15% mixed GI spread over area, scenario 3 = < 5% low vegetation
# per scenario, wallpaper is selected based on % of building footprint, classified as < 10%, 10-40%, > 40%
classes = ['10', '40', '100']

# %% Merging the different wallpaper classifications for the land use and GI output data
# ArcPy python environment

# could also be BGT_veg_reclass_40 or _100, all the same but coppies to avoid overwriting in wallpapering.
BGT_2018 = 'E:/Paper IV/Data/GIS_data/wallpapering/DB_BAU_HR/BGT_veg_reclass_10.tif'

for UFA in UFA_scenarios:
    for height, height_s in zip(height_scenarios, height_scenarios_s):
        for W in WLO:
            for s, sk in zip(scenario, scenario_kort): 
                directory = 'E:/Paper IV/Data/GIS_data/wallpapering/'
                for wp in WP:
                    # cut out the wallpapered pieces from the rest of the map, for each of the building footprint classifications
                    for c in classes:
                        scenario_name = sk+ '_BAU'+height_s+'_'+c+'.shp'
                        out = ExtractByMask(directory+sk+'_'+'BAU' + height_s+'/wallpaper_workspace/BGT_veg_reclass_' + c +'_' + wp +'.tif', directory+sk+'_'+'BAU' + height_s+'/'+scenario_name, "INSIDE")
                        # '1_10_LCEU.tif'
                        out.save(directory+sk+'_'+'BAU' + height_s+'/'+sk+'_'+wp+'_'+c+'_BGT.tif')
                        print(scenario_name)
                        print(wp)
                    arcpy.management.MosaicToNewRaster(directory+sk+'_'+'BAU' + height_s+'/'+sk+'_'+wp+"_10_BGT.tif;"+directory+sk+'_'+'BAU' + height_s+'/'+sk+'_'+wp+"_40_BGT.tif;"+directory+sk+'_'+'BAU' + height_s+'/'+sk+'_'+wp+"_100_BGT.tif;"+BGT_2018, directory+sk+'_'+'BAU' + height_s+'/', sk+'_'+wp+'_out_BGT.tif',
                                                       'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]',
                                                       "16_BIT_UNSIGNED", None, 1, "FIRST", "FIRST")
            