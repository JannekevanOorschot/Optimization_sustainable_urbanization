# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 09:43:08 2023

@author: jvano
"""

import pandas as pd
import geopandas as gpd

directory = 'E:/Paper IV/Data/GIS_data/LU_change/'
datalist = ['base_sparse', 'base_dense', 'HR_1_dense', 'HR_3_dense', 'HR_1_sparse', 'HR_3_sparse']
LUcodes = list(range(1, 23))
datastats = pd.DataFrame(index=datalist,columns = LUcodes)

#%%
for d in datalist:
    LUC = gpd.read_file(directory+d+'_CD.shp')
    for LU in LUcodes:
        print(LU)
        nr_rows = LUC.loc[LUC['grid_code'] == LU].count()
        datastats.loc[d,LU] = nr_rows[0]*100 # one cell is 100 m2

#%%

datastats.to_excel('E:/Paper IV/Data/Excel_data/LUchange_stats.xlsx')        
        