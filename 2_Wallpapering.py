# -*- coding: utf-8 -*-
"""
Model 2. Land use scenarios

Wallpaper land cover tiles based on landcover scenario and building footprint class

@author: jvano
"""
#%%

import os

UFA_scenarios = ['BAU']#,'small', 'large']
height_scenarios = ['_HR','_LR'] # only applies for apartments & offices
WLO = ['hoog_']
scenarios = ['_DichtBij_', '_Ruim_']
skort = ['DB', 'R']

WP = ['1', '2', '3'] # scenario 1 = 30% continuous GI including =>10% trees, scenario 2 = 15% mixed GI spread over area, scenario 3 = < 5% low vegetation
classes = ['10', '40', '100'] # per scenario, wallpaper is selected based on % of building footprint, classified as < 10%, 10-40%, > 40%

#format PBL scenarios: buildings_fishnet_hoog__DichtBij_BAU_mid_rise_10.shp
# format: fishnet_hoog__DichtBij_BAU_high_rise_10.shp
# format needs to be shortened in order for the wallpaper module to work: DB_BAU_HR_10.shp

#%% 
# PCRaster python environment


for s in skort: 
    for c in classes:
        for hl in height_scenarios: 
            os.chdir('E:/Paper IV/Data/GIS_data/wallpapering/'+s+'_BAU'+hl)
            path = 'E:/Paper IV/Data/GIS_data/wallpapering/'+s+'_BAU'+hl+'/'
            raster = 'BGT_veg_reclass_'+c+'.tif' # same map x 3, but to avoid overriding 
            pvp = s+ '_BAU'+hl+'_'+c+'.shp' #number of maps equals number of building ground area classifications (in this case 3)
            print(pvp)
            # pvp filename is shortened because otherwise Wallpapering module does not not work
            svp = 'WP_'+c+'.shp' # map for each scenario x3 (3 building footprint classifications)
            commandstring = f'cmd /k "python wallpaper_raster.py --raster_path_list {raster} --scenarios_vector_path {svp} --parcels_vector_path {pvp}"'
            os.system(commandstring)
        