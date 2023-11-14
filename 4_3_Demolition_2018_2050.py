"""

Model 4.3 DSM Demolition

@author: jvano

Loops through BAG stocks for each municipality (gemeente), spatial join with demolition scenarios, 
if BAG and demolition data overlaps, BAG building is assumed to be demolished. 

SPATIAL JOIN DOES NOT WORK

"""

#%%
print('1. Import modules')

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

#%%
print('2. Define workspace')

directory = 'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/GIS_data/'
workspace_sloop = directory+"Demolition_2050/Input_SJ.gdb"
workspace_BAG = directory+"BAG_2018_original_classification/Stock_2018.gdb"
workspace_out = directory+"Demolition_2050/Output_SJ.gdb"

# Municipalities
#gemeenten = ['Amsterdam']#, 'Roerdalen']
municipalities = gpd.read_file(directory+"CBS_Gemeente/Municipalities_355.shp")

#munlist_unsorted = list(municipalities['statnaam'])
#gemeenten = sorted(munlist_unsorted)
#or whole list of gemeenten:
os.chdir('C:/Users/jvano/OneDrive - Universiteit Leiden/Files/MFA_buildings/GIS/SJ_pand_vobj_gemeente')
gemeenten = []
gemeenten_ = []
for shpfile in glob.glob("*.shp"):
    filename = os.path.splitext(shpfile)[0]
    filename_2 = filename.replace(' ', '_')
    gemeenten_.append(filename_2)
    gemeenten.append(filename)

WLO = ['WLO_hoog_']#, 'WLO_laag_']
scenario = ['DichtBij', 'Ruim']

# Only run when not already calculated, takes a long time. Shapefile Stock data 2018 to feature geodatabase 
#for g in gemeenten:
#    arcpy.conversion.FeatureClassToGeodatabase(directory+"BAG_2018_original_classification/"+g+"_voorraden.shp", workspace_BAG)


#%%
print('3. Merge demolition maps of building types')
input_merge = directory+'Demolition_2050/Input/'
for w in WLO:
    for s in scenario:
        # merge demolition maps of building types per scenario (PBL assumes all buildings are demolished within gridcell)
        arcpy.management.Merge([input_merge+w+s+'_Sloop_appartement.shp',\
                                input_merge+w+s+'_Sloop_Kantoor.shp',\
                                    input_merge+w+s+'_Sloop_Detailhandel.shp',\
                                        input_merge+w+s+'_Sloop_Overheid_kw_diensten.shp',\
                                            input_merge+w+s+'_Sloop_NijverheidEnLogistiek.shp',\
                                                input_merge+w+s+'_Sloop_losstaand.shp',\
                                                    input_merge+w+s+'_Sloop_rijtjeswoning.shp'], directory+'Demolition_2050/Merge_dem.gdb/'+w+s+'_merge')
        arcpy.management.DeleteField(directory+'Demolition_2050/Merge_dem.gdb/'+w+s+"_merge", "POLY_AREA", "DELETE_FIELDS")
#%%
print('4. Spatial join Building stock with merged demolition map when they overlap')
for gem, gem_ in zip(gemeenten, gemeenten_):
    print('start with: ')
    print(gem)
    # select municipality shapefile
    gem_selection = municipalities.loc[(municipalities.Gemeentena == gem)] 
    gem_selection.to_file(directory+'CBS_Gemeente/gem/'+gem+'.shp')  
    arcpy.conversion.FeatureClassToGeodatabase(directory+'CBS_Gemeente/gem/'+gem+'.shp', directory+'CBS_Gemeente/gem1.gdb')                                                                               
    gem_voorraad = workspace_BAG+'/'+gem_+'_voorraden'
    arcpy.management.FeatureToPoint(gem_voorraad, workspace_BAG+'/'+gem_+'point' , "CENTROID")
    gem_voorraad = workspace_BAG+'/'+gem_+'point'
    commandstring = f'Steel "Steel" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Steel,-1,-1;'
    commandstring += f'Copper "Copper" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Copper,-1,-1;'
    commandstring += f'Aluminum "Aluminum" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Aluminum,-1,-1;'
    commandstring += f'Other_meta "Other_meta" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Other_meta,-1,-1;'
    commandstring += f'Wood "Wood" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Wood,-1,-1;'
    commandstring += f'Concrete "Concrete" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Concrete,-1,-1;'
    commandstring += f'Brick "Brick" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Brick,-1,-1;'
    commandstring += f'Other_cons "Other_cons" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Other_cons,-1,-1;'
    commandstring += f'Glass "Glass" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Glass,-1,-1;'
    commandstring += f'Ceramics "Ceramics" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Ceramics,-1,-1;'
    commandstring += f'Plastics "Plastics" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Plastics,-1,-1;'
    commandstring += f'Insulation "Insulation" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Insulation,-1,-1;'
    commandstring += f'Other "Other" true true false 8 Double 0 0,Sum,#,{gem_voorraad},Other,-1,-1;'
    for w in WLO:
        
        for s in scenario: 
            # select only demolition cells that fall within municipal borders
            dem_selection = arcpy.management.SelectLayerByLocation(directory+'Demolition_2050/Merge_dem.gdb/'+w+s+"_merge", "HAVE_THEIR_CENTER_IN", directory+'CBS_Gemeente/gem1.gdb/'+gem_, None, "NEW_SELECTION", "NOT_INVERT")
            arcpy.management.DefineProjection(dem_selection, 'PROJCS["RD_New",GEOGCS["GCS_Amersfoort",DATUM["D_Amersfoort",SPHEROID["Bessel_1841",6377397.155,299.1528128]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Double_Stereographic"],PARAMETER["False_Easting",155000.0],PARAMETER["False_Northing",463000.0],PARAMETER["Central_Meridian",5.38763888888889],PARAMETER["Scale_Factor",0.9999079],PARAMETER["Latitude_Of_Origin",52.15616055555555],UNIT["Meter",1.0]]')
            print('done')
            arcpy.analysis.SpatialJoin(dem_selection, workspace_BAG+'/'+gem_+"point", workspace_out+'/'+gem_+'_'+w+s, "JOIN_ONE_TO_ONE", "KEEP_ALL", commandstring,"INTERSECT", None, '')
 
#%%
print('5. Calculate total demolished materials per scenario')
for w in WLO:
    for s in scenario:
        munlist = []
        for m in gemeenten_:
            mun_scen = directory+'Demolition_2050/Output_SJ.gdb/'+m+'_'+w+s
            munlist.append(mun_scen)
        arcpy.management.Merge(munlist, directory+'Demolition_2050/NL_'+w+s+'.shp')
        
mat = ['Steel', 'Copper', 'Aluminum', 'Other_meta', 'Wood', 'Concrete', 'Brick', 'Other_cons', 'Glass', 'Ceramics', 'Plastics', 'Insulation', 'Other']

total_dem = pd.DataFrame(columns =mat)

for w in WLO:
    for s in scenario:
        for m in mat:
            scen = gpd.read_file(directory+'Demolition_2050/NL_'+w+s+'.shp')
            total_dem.loc[w+s,m] = scen.loc[:,m].sum()
            
total_dem.to_excel('C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/Documents/Data/total_demolition.xlsx')
