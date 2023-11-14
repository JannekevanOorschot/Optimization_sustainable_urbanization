# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:40:47 2023

@author: jvano
"""


import arcpy, arcinfo
import pandas as pd
import numpy as np
import glob, os

from arcpy import env
from arcpy.sa import *

from osgeo import gdal
from os.path import exists

import geopandas as gpd
import os

#Enable ArcGIS extensions
arcpy.CheckOutExtension("Spatial")

arcpy.env.overwriteOutput = True


os.chdir('E:/Paper IV/Data/GIS_data/Invest')
directory = 'E:/Paper IV/Data/GIS_data/Invest/'
height = ['HR', 'LR']
urban = ['DB', 'R']
LU = ['1', '3']

#%% Cooling
#!!! Dit is een gemiddelde op gemeente niveau, niet op celniveau

ES_mean = pd.DataFrame(index = ['base', 'DB_1_LR', 'DB_1_HR', 'DB_3_LR', 'DB_3_HR','R_1_LR', 'R_1_HR', 'R_3_LR', 'R_3_HR' ], columns = ['Tanom', 'Wret'])

f = gpd.read_file(directory+'resultsCooling/HR/uhi_results_y0.shp')
ES_mean.loc['base', 'Tanom'] = f['avg_tmp_an'].mean()

for h in height:
    for u in urban:
        for l in LU:
            if h == 'HR':
                f = gpd.read_file(directory+'resultsCooling/'+h+'/uhi_results_'+u+'_'+l+'.shp')
            else:
                f = gpd.read_file(directory+'resultsCooling/'+h+'/'+u+'_'+l+'/uhi_results_'+u+'_'+l+'.shp')
            
            avg_t = f['avg_tmp_an'].mean()
            print(avg_t)
            ES_mean.loc[u+'_'+l+'_'+h,'Tanom']= avg_t
            
#%% Water retention
#!!! Dit is een gemiddelde op gemeente niveau, niet op celniveau

ff = gpd.read_file(directory+'resultsWater/HR/Gemeente_shapefiles/gem_y0.shp')
ES_mean.loc['base','Wret'] = ff['mean_reten'].mean()

for h in height:
    for u in urban:
        for l in LU:
            ff = gpd.read_file(directory+'resultsWater/'+h+'/Gemeente_shapefiles/gem_'+u+l+'.shp')
            avg_r = ff['mean_reten'].mean()
            print(avg_r)
            
            ES_mean.loc[u+'_'+l+'_'+h,'Wret']= avg_r
            
            
#%% Export files

ES_mean.to_excel('E:/Paper IV/Data/Excel_data/ES_mean.xlsx')
            

            
            

                                    


