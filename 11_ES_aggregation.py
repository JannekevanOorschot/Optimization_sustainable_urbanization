# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:46:37 2023

@author: jvano
"""

import arcpy
from arcpy.sa import *
import pandas as pd
import geopandas as gpd
import numpy as np
import glob, os
from pathlib import Path

d = 'E:/Paper IV/Data/GIS_data/PBL_data/basisjaar/Basisjaar_'
cd = 'E:/Paper IV/Data/GIS_data/CD_locations/'
cd_files = ['Basisjaar_dissolve.shp','Dense_CD_locations_dissolve.shp', 'Dense_stock_2050_dissolve.shp', 'Sparse_CD_locations_dissolve.shp', 'Sparse_stock_2050_dissolve.shp']
invest_d = 'E:/Paper IV/Data/GIS_data/Invest/'
g_d = 'E:/Paper IV/Data/GIS_data/GI_cap/'

#%% Combine input data to get a mask of stock, C&D locations

filepaths = [d+'Detailhandel.tif', d+'Kantoor.tif', d+'NijverheidEnLogistiek.tif', d+'Ov_consumentendiensten.tif', d+'Overheid_kw_diensten.tif', d+'Zak_dienstverlening.tif', d+'Appartement.tif', d+'losstaand.tif', d+'Rijtjeswoning.tif', d+'Twee_onder_1_kap.tif', d+'Vrijstaand.tif']

rcc = RasterCalculator(filepaths, ['1','2','3','4','5','6','7','8','9','10','11'], '1+2+3+4+5+6+7+8+9+10+11') 
rcc.save(d+'SOM.tif')

out_raster = arcpy.sa.Reclassify(d+'SOM.tif', "Value", "0 NODATA", "DATA"); out_raster.save(d+'SOM_reclassified.tif')

arcpy.conversion.RasterToPolygon(d+'SOM_reclassified.tif', d+'.shp', "NO_SIMPLIFY", "VALUE")

#%% ES aggregation for 2018, C&D 2018-2050 & 2050 Stock

# aggregation of 2018
out =  'E:/Paper IV/Data/GIS_data/Invest/ES_agg/'

t_d = 'resultsCooling/HR/'
t_d2 = 'E:/Paper IV/Data/GIS_data/Archive/resultsCooling/HR/'
w_d = 'resultsWater/HR/'

basefiles = [invest_d+t_d+'hm_y0.tif', t_d2+'T_air_y0.tif',invest_d+w_d+'retention_ratio_y0.tif', g_d+'base_unsigned_cap.tif']
names = ['hm_y0','t_air_y0','retention_ratio_y0', 'GI_cap_y0']

# Niet GI/cap maar totaal GI binnen 500m radius
basefiles = [g_d+'base_unsigned_FS.tif']
names = ['GI_500m_y0']

for b,n in zip(basefiles,names):
    print(n)
    arcpy.ia.ZonalStatisticsAsTable(cd+ 'Basisjaar_dissolve.shp', "Same", b, out+n+'.dbf', "DATA", "MEAN", "CURRENT_SLICE", [90], "AUTO_DETECT", "ARITHMETIC", 360)
    arcpy.conversion.TableToExcel(out+n+'.dbf', out+n+'.xlsx')

    
#%% aggregation for DB & R

height = ['HR', 'LR']
height = ['HR']
u_short = ['DB', 'R']
u_long = ['Dense', 'Sparse']

for h in height:
    t_d = 'resultsCooling/'+h+'/'
    t_d2 = 'E:/Paper IV/Data/GIS_data/InVest/resultsCooling/HR/airT/'+h+'/' # ik moet de locatie nog aanpassen want alles staat nu in de HR map, maar duurt t*ring lang
    w_d = 'resultsWater/'+h+'/'
    out = 'E:/Paper IV/Data/GIS_data/Invest/ES_agg/'+h+'/'
    for us, ul in zip(u_short,u_long):    
        basefiles = [invest_d+t_d+'hm_'+us+'_1.tif', invest_d+t_d+'hm_'+us+'_3.tif', t_d2+'T_air_'+us+'_1.tif', t_d2+'T_air_'+us+'_3.tif', invest_d+w_d+'retention_ratio_'+us+'_1.tif',invest_d+w_d+'retention_ratio_'+us+'_3.tif', g_d+us+'_1_BGT_EbA_'+h+'_cap.tif', g_d+us+'_3_BGT_EbA_'+h+'_cap.tif']
        names = ['hm_'+us+'_1','hm_'+us+'_3','t_air_'+us+'_1','t_air_'+us+'_3','retention_ratio_'+us+'_1','retention_ratio_'+us+'_3', 'GI_cap_'+us+'_1','GI_cap_'+us+'_3']
        
        # Niet GI/cap maar totaal GI binnen 500m radius
        basefiles = [g_d+us+'_1_BGT_EbA_'+h+'_FS.tif', g_d+us+'_3_BGT_EbA_'+h+'_FS.tif']
        names = [ 'GI_500m_'+us+'_1','GI_500m_'+us+'_3']
        
        for b,n in zip(basefiles,names):
            print(n)
            arcpy.ia.ZonalStatisticsAsTable(cd+ul+'_CD_dissolve.shp', "Same", b, out+n+'_CD.dbf', "DATA", "MEAN", "CURRENT_SLICE", [90], "AUTO_DETECT", "ARITHMETIC", 360)
            arcpy.conversion.TableToExcel(out+n+'_CD.dbf', out+n+'_CD.xlsx')
            arcpy.ia.ZonalStatisticsAsTable(cd+ul+'_stock_2050_dissolve.shp', "Same", b, out+n+'_Stock.dbf', "DATA", "MEAN", "CURRENT_SLICE", [90], "AUTO_DETECT", "ARITHMETIC", 360)
            arcpy.conversion.TableToExcel(out+n+'_Stock.dbf', out+n+'_Stock.xlsx')
    



