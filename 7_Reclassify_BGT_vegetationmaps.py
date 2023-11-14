# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 18:49:16 2023
An attempt to reclassify BGT based on aggregation of classes from BGT and merging with % maps of trees, shrubs and grasses from RIVM

@author: jvano
"""


#%%
print("1. Package installation & import")

import arcpy, arcinfo
import pandas as pd
import numpy as np
import glob, os

from arcpy import env
from arcpy.sa import *
from osgeo import gdal
from os.path import exists

import geopandas as gpd
import pandas as pd

arcpy.env.overwriteOutput = True
#Enable ArcGIS extensions
arcpy.CheckOutExtension("Spatial")

bgt = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/GIS_data/bgt.tif'
# trees = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/work_file/Wallpapering/H_DB_BAU_HR/Trees_10.tif'
# shrubs = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/work_file/Wallpapering/H_DB_BAU_HR/Shrubs_10.tif' 
# grass = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/work_file/Wallpapering/H_DB_BAU_HR/Grass_10.tif'

trees = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/GIS_data/RIVM_groen_lagen_10_10m/Bomen_0.tif'
grass = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/GIS_data/RIVM_groen_lagen_10_10m/Gras_0.tif'
shrubs = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/GIS_data/RIVM_groen_lagen_10_10m/Struiken_0.tif'
\
bgt1 = Raster(bgt)
trees1 = Raster(trees)
shrubs1 = Raster(shrubs)
grass1 = Raster(grass)

#%%
print("2. Reclassify")
# Con(in_conditional_raster, in_true_raster_or_constant, {in_false_raster_or_constant}, {where_clause})
#                                                           OPTIONAL                       OPTIONAL

outCon = Con((((bgt1 == 801) | (bgt1 == 805)| (bgt1 == 812) | (bgt1 == 814)) & (trees1 >50)), 9, \
              Con((((bgt1 == 801) | (bgt1 == 805)| (bgt1 == 812) | (bgt1 == 814)) & (trees1 <=50)), 10, \
                  Con(((bgt1 == 802) | (bgt1 == 804)| (bgt1 == 806)), 8, \
                      Con((((bgt1 == 803) | (bgt1 == 605)) & (trees1 +shrubs1+grass1 <= 50)), 2, \
                          Con((((bgt1 == 803) | (bgt1 == 605)) & (trees1 +shrubs1+grass1 >50) & (trees1>(grass1+shrubs1))), 3, \
                              Con((((bgt1 == 803) | (bgt1 == 605)) & (trees1+shrubs1+grass1 > 50)&(trees1<=(grass1+shrubs1))), 4, \
                                  Con((((bgt1 == 807) | (bgt1 == 809)| (bgt1 == 811)| (bgt1 == 401)) &  (grass1+shrubs1>50)), 13, \
                                    Con((((bgt1 == 807)| (bgt1 == 809)| (bgt1 == 811)| (bgt1 == 401)) & (shrubs1+grass1 <= 50)), 14, \
                                          Con((((bgt1 == 810) | (bgt1 == 813)| (bgt1 == 815)| (bgt1 == 817)| (bgt1 == 601)| (bgt1 == 808)| (bgt1 == 0)) & (shrubs1+grass1+trees1 <= 10)) , 15, \
                                              Con((((bgt1 == 810) | (bgt1 == 813)| (bgt1 == 815)| (bgt1 == 817)| (bgt1 == 601)| (bgt1 == 808)| (bgt1 == 0)) & (trees1+shrubs1+grass1 > 10) & (trees1+shrubs1+grass1 <= 50) & (trees1>(grass1+shrubs1))), 16, \
                                                  Con((((bgt1 == 810) | (bgt1 == 813)| (bgt1 == 815)| (bgt1 == 817)| (bgt1 == 601)| (bgt1 == 808)| (bgt1 == 0)) & (trees1+shrubs1+grass1 > 10) & (trees1+shrubs1+grass1 <= 50) & (trees1<=(grass1+shrubs1))), 17, \
                                                      Con((((bgt1 == 810) | (bgt1 == 813)| (bgt1 == 815)| (bgt1 == 817)| (bgt1 == 601)| (bgt1 == 808)| (bgt1 == 0)) & (trees1+shrubs1+grass1 > 50) & (trees1+shrubs1+grass1 <= 70) & (trees1>(grass1+shrubs1))), 18, \
                                                          Con((((bgt1 == 810) | (bgt1 == 813)| (bgt1 == 815)| (bgt1 == 817)| (bgt1 == 601)| (bgt1 == 808)| (bgt1 == 0)) & (trees1+shrubs1+grass1 > 50) & (trees1+shrubs1+grass1 <= 70)  &(trees1<=(grass1+shrubs1))), 19, \
                                                              Con((((bgt1 == 810) | (bgt1 == 813)| (bgt1 == 815)| (bgt1 == 817)| (bgt1 == 601)| (bgt1 == 808)| (bgt1 == 0)) & (trees1+shrubs1+grass1 > 70) & (trees1>(grass1+shrubs1))), 20, \
                                                                  Con((((bgt1 == 810) | (bgt1 == 813)| (bgt1 == 815)| (bgt1 == 817)| (bgt1 == 601)| (bgt1 == 808)| (bgt1 == 0)) & (trees1+shrubs1+grass1 > 70) & (trees1<=(grass1+shrubs1))), 21, \
                                                                      Con(((bgt1 == 816) & (grass1+shrubs1+trees1 > 50)), 11, \
                                                                          Con(((bgt1 == 816) & (grass1+shrubs1+trees1<= 50)), 12, \
                                                                              Con((((bgt1 == 602) | (bgt1 == 604)| (bgt1 == 603)| (bgt1 == 402)| (bgt1 == 300)) & (trees1+shrubs1+grass1 <= 50)), 5, \
                                                                                  Con((((bgt1 == 602) | (bgt1 == 604)| (bgt1 == 603)| (bgt1 == 402)| (bgt1 == 300)) & (trees1 +shrubs1+grass1 >50) & (trees1>(grass1+shrubs1))), 6, \
                                                                                      Con((((bgt1 == 602) | (bgt1 == 604)| (bgt1 == 603)| (bgt1 == 402)| (bgt1 == 300)) & (trees1 +shrubs1+grass1 >50) & (trees1<=(grass1+shrubs1))), 7, \
                                                                                          Con(((bgt1 == 501) | (bgt1 == 502)| (bgt1 == 503)| (bgt1 == 701)| (bgt1 == 702)| (bgt1 == 703)| (bgt1 == 704)), 22, \
                                                                                              Con((bgt1==200),1,0))))))))))))))))))))))

outCon.save('C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/GIS_data/BGT_veg_reclass.tif')

