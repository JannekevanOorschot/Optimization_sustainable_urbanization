# -*- coding: utf-8 -*-
"""
Model 1.4 DSM
Version adjusted on 10/09/2023 Nagoya University

Calculates EOL_RR and MRC per scenario 
Links primary and secondary share to GWP values

@author: jvano
"""
#%% Load modules and data

import geopandas as gpd
import pandas as pd
#import xlsxwriter
import os
import numpy as np

#Adjust building classification construction and calculate totals
mat = ['Steel', 'Copper', 'Aluminum', 'Other_meta', 'Wood', 'Concrete', 'Brick', 'Other_cons', 'Glass', 'Ceramics', 'Plastics', 'Insulation', 'Other', 'Other biobased']
RR_data = pd.read_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/RR_MRC_LCI.xlsx', sheet_name = 'RR_MRC_bp')
RR_data = RR_data.set_index('Material')
Insulation_data = pd.read_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/RR_MRC_LCI.xlsx', sheet_name = 'Insulation')
Insulation_data = Insulation_data.set_index('Unnamed: 0')

GWP_pr =pd.read_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/RR_MRC_LCI.xlsx', sheet_name = 'LCI_I')
GWP_pr = GWP_pr.set_index('Unnamed: 0')
GWP_sec =pd.read_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/RR_MRC_LCI.xlsx', sheet_name = 'LCI_II')
GWP_sec = GWP_sec.set_index('Unnamed: 0')

insulation_materials = ['Glass wool', 'EPS', 'Stone wool', 'XPS', 'PUR', 'Biobased insulation']

mat_adj = ['Steel', 'Copper', 'Aluminum', 'Other_meta', 'Wood_beam', 'Wood_board', 'CLT', 'Concrete', 'Brick', 'Other_cons', 'Glass', 'Ceramics', 'Plastics', 'Other', 'Other biobased', 'Glass wool', 'EPS', 'Stone wool', 'XPS', 'PUR', 'Biobased insulation' ]
demolition = pd.read_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/total_demolition.xlsx')
demolition = demolition.set_index('Unnamed: 0')
demolition['Other biobased'] = np.nan

UFA = ['BAU', 'S']
MI = ['M0', 'M1', 'M2'] # M0 = Conventional, M1 = biobased, M2 = circular
RR = ['rr', 'mrc'] #recycling rate & maximum recycled content
WLO = ['Hoog']# 'Laag']]
height = ['HR', 'LR']
Urbanization = ['DichtBij', 'Ruim']

#%% per construction file, sum columns to get total material inflow
c_totals = pd.DataFrame(columns=mat)
dir_c = 'E:/Paper IV/Data/Excel_data/Output_DSM/'
for c in os.listdir(dir_c):
    print(c)
    f = os.path.join(dir_c, c)
    file_c = pd.read_excel(f)
    scen_adj = c[9:-5]
    c_totals.loc[scen_adj,'Steel'] = file_c.loc[:,'Steel & ir'].sum()
    c_totals.loc[scen_adj,'Copper'] = file_c.loc[:,'Copper'].sum()
    c_totals.loc[scen_adj,'Aluminum'] = file_c.loc[:,'Aluminum'].sum()
    c_totals.loc[scen_adj,'Other_meta'] = file_c.loc[:,'Other meta'].sum()
    c_totals.loc[scen_adj,'Wood'] = file_c.loc[:,'Wood'].sum()
    c_totals.loc[scen_adj,'Concrete'] = file_c.loc[:,'Concrete'].sum()
    c_totals.loc[scen_adj,'Brick'] = file_c.loc[:,'Brick'].sum()
    c_totals.loc[scen_adj,'Other_cons'] = file_c.loc[:,'Bitumen'].sum()+file_c.loc[:,'Gypsum'].sum()+file_c.loc[:,'Lime sands'].sum()+file_c.loc[:,'Mortar'].sum()+file_c.loc[:,'Stone'].sum()+file_c.loc[:,'Sand'].sum()
    c_totals.loc[scen_adj,'Glass'] = file_c.loc[:,'Glass'].sum()
    c_totals.loc[scen_adj,'Ceramics'] = file_c.loc[:,'Ceramics'].sum()
    c_totals.loc[scen_adj,'Plastics'] = file_c.loc[:,'Plastics'].sum()
    c_totals.loc[scen_adj,'Insulation'] = file_c.loc[:,'Insulation'].sum()
    c_totals.loc[scen_adj,'Other'] = file_c.loc[:,'Electronic'].sum()+file_c.loc[:,'Glue & pai'].sum()+file_c.loc[:,'Paper'].sum()
    c_totals.loc[scen_adj,'Other biobased'] = file_c.loc[:,'Other biob'].sum()

#%% Splitting insulation materials into specific insulation types

for ins_m in insulation_materials:
    c_totals[ins_m] = np.nan
    c_totals[ins_m].iloc[0:2] = c_totals['Insulation'].iloc[0:2]*Insulation_data.loc['Conventional', ins_m]
    c_totals[ins_m].iloc[2:4] = c_totals['Insulation'].iloc[2:4]*Insulation_data.loc['Biobased', ins_m]
    c_totals[ins_m].iloc[4:6] = c_totals['Insulation'].iloc[4:6]*Insulation_data.loc['Circular', ins_m]
    c_totals[ins_m].iloc[6:8] = c_totals['Insulation'].iloc[6:8]*Insulation_data.loc['Conventional', ins_m]
    c_totals[ins_m].iloc[8:10] = c_totals['Insulation'].iloc[8:10]*Insulation_data.loc['Biobased', ins_m]
    c_totals[ins_m].iloc[10:12] = c_totals['Insulation'].iloc[10:12]*Insulation_data.loc['Circular', ins_m]
        
    demolition[ins_m] = np.nan    
    demolition[ins_m] = demolition['Insulation']*Insulation_data.loc[2018,ins_m]

#%% Splitting wood into specific wood types

# for M0 and M3:
c_totals['Wood_beam'] = np.nan
c_totals['Wood_board'] = np.nan
c_totals['CLT'] = np.nan
c_totals['Wood_beam'].iloc[[0,1,4,5,6,7,10,11]] = c_totals['Wood'].iloc[[0,1,4,5,6,7,10,11]]*0.82
c_totals['Wood_board'].iloc[[0,1,4,5,6,7,10,11]] = c_totals['Wood'].iloc[[0,1,4,5,6,7,10,11]]*0.18

# for M2:
c_totals['Wood_beam'].iloc[[2,3,8,9]] = c_totals['Wood'].iloc[[2,3,8,9]]*0.82*0.53
c_totals['Wood_board'].iloc[[2,3,8,9]] = c_totals['Wood'].iloc[[2,3,8,9]]*0.18*0.53
c_totals['CLT'].iloc[[2,3,8,9]] = c_totals['Wood'].iloc[[2,3,8,9]]*0.47

demolition['Wood_beam'] = np.nan
demolition['Wood_board'] = np.nan
demolition['Wood_beam'] = demolition['Wood']*0.82
demolition['Wood_board'] = demolition['Wood']*0.18

#%% Calculate primary and secondary material inflow, and link to environmental impact 

secondary_materials = pd.DataFrame(columns = mat_adj)
primary_materials = pd.DataFrame(columns = mat_adj)
GWP_primary = pd.DataFrame(columns=mat_adj)
GWP_secondary = pd.DataFrame(columns=mat_adj)
#Materialen = ['Beton', 'Baksteen','Overige constructiematerialen', 'Staal & Ijzer', 'Steenwol', 'Glaswol', 'EPS', 'XPS', 'PUR', 'Houtvezels', 'Keramiek', 'Glas', 'Hout beam','Hout board', 'Overig', 'Kunststoffen', 'Aluminium', 'Koper', 'Overige metalen', 'Overige biobased materialen']

# Results are the same for each MI UFA and floor scenarios, results only differ for RS (urbanization) scenarios
# Glass to glass wool is not considerd right now (only glass to glass and glass wool)
# in Scenario WLO_hoog_Dichtbij, in all scenarios mrc > rr_m in case of choosing actual recycling rates (BAU)

for h in height:
    for ms in MI:
        for w in WLO:
            for u in Urbanization:
                for m in mat_adj:
                    #_DichtBij_Bouw__M0_GO_BAU_HR
                    c = c_totals.loc['_'+u+'_Bouw__'+ms+'_GO_BAU_'+h]
                    print(c)
                    c_m = c.loc[m]
                    print(c_m)
                    if m == 'CLT':
                        d_m = 0
                    else:                        
                        d = demolition.loc['WLO_hoog_'+u]
                        d_m = d.loc[m]
                    
                    rr = RR_data.loc[m, 'EOL_RR']
                    mrc = RR_data.loc[m, 'MRC']
                    
                    rr_m = rr*d_m
                    mrc_m = c_m*mrc

                    if rr_m == 0 or mrc_m ==0:
                        secondary_m = 0
                        
                    elif rr_m <=  mrc_m:
                        secondary_m = rr_m
                        
                    elif rr_m > mrc_m:
                        secondary_m = mrc_m
                            
                    primary_m = c_m-secondary_m
                    secondary_materials.loc['_'+u+'_Bouw__'+ms+'_GO_BAU_'+h, m] = secondary_m
                    primary_materials.loc['_'+u+'_Bouw__'+ms+'_GO_BAU_'+h, m] = primary_m
                    
                    # some of the GWP values already present a share of secondary material    
                    if GWP_sec.loc[m, 'Secondary_share_GWP'] > 0:
                        primary_in_sec = (1-mrc)*secondary_m
                        secondary = secondary_m + primary_in_sec
                        primary = c_m - primary_in_sec
                        GWP_primary_m = primary*GWP_pr.loc[m,'IPCC 2013 | climate change | GWP 100a']
                        GWP_secondary_m = secondary*GWP_sec.loc[m,'IPCC 2013 | climate change | GWP 100a']
    
                    else:
                        primary = c_m-secondary_m
                        GWP_primary_m = primary*GWP_pr.loc[m,'IPCC 2013 | climate change | GWP 100a']
                        GWP_secondary_m = secondary_m*GWP_sec.loc[m,'IPCC 2013 | climate change | GWP 100a']
                        
                    GWP_primary.loc['_'+u+'_Bouw__'+ms+'_GO_BAU_'+h, m]=GWP_primary_m
                    GWP_secondary.loc['_'+u+'_Bouw__'+ms+'_GO_BAU_'+h, m]=GWP_secondary_m                       
        

secondary_materials.to_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/Primary_secondary_10092023/Secondary_materials.xlsx')
primary_materials.to_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/Primary_secondary_10092023/Primary_materials.xlsx')
GWP_primary.to_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/Primary_secondary_10092023/GWP_primary.xlsx')
GWP_secondary.to_excel('E:/Paper IV/Data/Excel_data/MFA&LCA/Primary_secondary_10092023/GWP_secondary.xlsx')
