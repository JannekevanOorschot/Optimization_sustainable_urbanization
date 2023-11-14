# -*- coding: utf-8 -*-
"""

Model 4.2 DSM Construction

@author: jvano

"""

#%% Import input data & modules

#import arcpy
import pandas as pd
import geopandas as gpd
import numpy as np
import glob, os

os.chdir('E:/Paper IV/Data')


#gebouwtypen = ['appartement', 'winkel', 'kantoor', 'vrijstaand', 'industrie', 'overheid', 'serieel']
#building_types = ['Apartment', 'Retail', 'Office', 'Detached', 'Industry', 'Services', 'Row']
#building_types = ['Detached', 'Ap_S', 'Ap_L', 'Office_S', 'Office_L', 'Industry', 'Services', 'Retail','Row']
building_types = ['Apartment', 'Retail', 'Office', 'Detached', 'Industry', 'Services', 'Row']
gebouwtypen_afk = ['appartement', 'Detailhandel', 'Kantoor', 'losstaand', 'NijverheidEnLogistiek', 'Overheid_kw_diensten',  'rijtjeswoning']


#Material intensities scenario 1 (Conventional) (kg/m2 GO)
MI_s1 = pd.read_excel(r'Excel_data/BGA.xlsx', sheet_name = 'Conventional')
MI_s1 = MI_s1.set_index('Building type')

#Material intensities scenario 2 (Biobased)
MI_s2 = pd.read_excel(r'Excel_data/BGA.xlsx', sheet_name = 'Biobased')
MI_s2 = MI_s2.set_index('Building type')

#Material intensities scenario 3 (Circular)
MI_s3 = pd.read_excel(r'Excel_data/BGA.xlsx', sheet_name = 'Circular')
MI_s3 = MI_s3.set_index('Building type')

# list of building materials
material_columns = list(MI_s1.columns)

mat_scenario = [MI_s1, MI_s2, MI_s3]

# UFA BAU (UFA in Dutch = GO)
GO_BAU = pd.read_excel(r'Excel_data/BGA.xlsx', sheet_name = 'UFA')
GO_BAU = GO_BAU.set_index('Building type')
GO_S = GO_BAU.copy()
GO_S['Value'] = GO_S['Value']*0.8
GO_L = GO_BAU.copy()
GO_L['Value'] = GO_L['Value']*1.2

GOs = [GO_BAU]#, GO_S, GO_L]
Height = ['HR', 'LR']
    
#%% Calculate constructed building material (2018-2050) per material per scenario

#All maps
os.chdir('E:/Paper IV/Data/GIS_data/PBL_data/Polygon/RtP')

WLO = ['WLO_hoog_']#, 'WLO_laag_']
scenario = ['DichtBij_', 'Ruim_']

# example input file: WLO_hoog_DichtBij_Bouw_appartement.shp

for w in WLO:
    for s in scenario:
        for h in Height:
            for (a,b) in zip(building_types, gebouwtypen_afk):
                file = gpd.read_file(w+s+'Bouw_'+b+'.shp')
                filename = w+s+'Bouw_'+b
                print(filename)
                # correct value for polygon size
                file['gc_adj']=file['gridcode']*(file['POLY_AREA']/10000)
                for index,g in enumerate(GOs):
                    if index == 0:
                        gnaam = 'GO_BAU'
                    elif index == 1:
                        gnaam = 'GO_S'
                    elif index == 2: 
                        gnaam = 'GO_L'
                    for index, MI, in enumerate(mat_scenario):
                        ms = 'M'+str(index) # 0 = Conventional, 1 = Biobased, 2 = Circular
                        for m in material_columns:
                            if b == 'appartement' and h == 'HR':
                                file[m] = np.NaN
                                file[m].loc[(file.gc_adj <= 5000)] = file['gc_adj']*g.loc[a,'Value']*MI.loc['Ap_S',m]
                                file[m].loc[(file.gc_adj > 5000)]= file['gc_adj']*g.loc[a,'Value']*MI.loc['Ap_L',m]
                            elif b == 'appartement' and h == 'LR':
                                file[m] = np.NaN
                                file[m] = file['gc_adj']*g.loc[a,'Value']*MI.loc['Ap_S',m]                        
                            elif b == 'Kantoor'and h == 'HR':
                                file[m] = np.NaN
                                file[m].loc[(file.gc_adj <= 5000)] = file['gc_adj']*g.loc[a,'Value']*MI.loc['Office_S',m]
                                file[m].loc[(file.gc_adj > 5000)]= file['gc_adj']*g.loc[a,'Value']*MI.loc['Office_L',m]                            
                            elif b == 'Kantoor'and h == 'LR':
                                file[m] = np.NaN
                                file[m] = file['gc_adj']*g.loc[a,'Value']*MI.loc['Office_S',m]                          
                            else:
                                file[m]= file['gc_adj']*g.loc[a, 'Value']*MI.loc[a,m]
                        file.to_file('E:/Paper IV/Data/GIS_data/Construction_2050/'+filename+'_'+gnaam+'_'+ms+'_'+h+'.shp')

#%% Total construction materials per scenario

os.chdir('E:/Paper IV/Data/GIS_data/Construction_2050')

#Names of some materials are shortened in previous step
materialen = ['Aluminum', 'Brick', 'Concrete','Bitumen', 'Electronic', 'Gypsum','Glass', 'Wood', 'Insulation', 'Lime sands', 'Ceramics', 'Copper', 'Plastics', 'Glue & pai', 'Mortar', 'Other biob', 'Other meta','Paper', 'Steel & ir', 'Stone', 'Sand']

WLO = ['WLO_hoog_']#, 'WLO_laag_']
scenario = ['DichtBij_Bouw_', 'Ruim_Bouw_']
factor = ['GO_BAU']#, 'GO_S', 'GO_L']
MI_s = ['M0', 'M1', 'M2']
Height = ['HR', 'LR']

#format: WLO_hoog_DichtBij_Bouw_appartement_GO_BAU_M0_HR.shp

total_con = pd.DataFrame(index = building_types, columns = materialen)

for w in WLO:
    for s in scenario: 
        for s1 in MI_s:
            for f in factor: 
                for h in Height: 
                    for (a,b) in zip(building_types, gebouwtypen_afk):
                        file1 = gpd.read_file(w+s+b+'_'+f+'_'+s1+'_'+h+'.shp')
                        filename = w+s+'_'+b+'_'+f+'_'+s1+'_'+h
                        for m in materialen:
                            total_con.loc[a,m] = file1.loc[:,m].sum()
                                    
                        print('Done with: '+filename)
                    total_con.to_excel('E:/Paper IV/Data/Excel_data/Output_DSM/'+w+'_'+s+'_'+s1+'_'+f+'_'+h+'.xlsx')
                    