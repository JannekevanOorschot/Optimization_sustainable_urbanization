# -*- coding: utf-8 -*-
"""

Model 4.1 DSM Building stock 2018

@author: jvano

"""

#%% import and explore data

import pandas as pd
import numpy as np
import geopandas as gpd
import glob, os

#%% load Files & edit Material DataBase
M_total_NL = pd.DataFrame()
M_total_gem = pd.DataFrame()


building_types = ['Detached', 'Row', 'Ap_S', 'Ap_L', 'Retail', 'Office_S', 'Office_L', 'Industry', 'Service']

# BAG data per municipality
# test: Amsterdam
#os.chdir('C:/Users/jvano/OneDrive - Universiteit Leiden/Files/MFA_buildings/GIS/SJ_pand_vobj_Amsterdam')
# All municipalities
os.chdir('E:/Paper IV/Data/GIS_data/SJ_pand_vobj_gemeente')

all_years = np.arange(1900,2019,1)
I_gebouwen = pd.DataFrame(0, index = all_years, columns = building_types)
        
#%%    
gemeenten = []
for shpfile in glob.glob("*.shp"):
    filename = os.path.splitext(shpfile)[0]
    gemeenten.append(filename)

MI_db = pd.read_excel(r'E:/Paper IV/Data/Excel_data/BGA.xlsx', sheet_name = 'Historic')
 
MI_db['Building type'] = MI_db['Building type'].fillna(method='ffill')
tuples = list(zip(MI_db['Building type'], MI_db['Cohort']))

MI_db.index = tuples
MI_db.drop(['Building type', 'Cohort'], axis = 1, inplace = True)

material_columns = list(MI_db.columns)

material_index = list(MI_db.index)

#%% Loop through each municpality

for file in glob.glob("*.shp"):       
    
    BAGx = gpd.read_file(file)
    
    BAG = BAGx[['bouwjaar', 'status', 'gebruiksdo','gebruiks_1', 'geometry', 'GO','shape_Area']].copy()
    
    #2018 is start jaar, dus bouw na 2018 uit bestand verwijderen
    built_after_2018 = BAG[ BAG['bouwjaar'] > 2018].index
    BAG.drop(built_after_2018, inplace = True)
    
    filename = os.path.splitext(file)[0]
    print(filename)
    woningtypering = gpd.read_file(r'C:/Users/jvano/OneDrive - Universiteit Leiden/Files/MFA_buildings/Data/woningtypering_gem/'+filename+'.shp')
    
    # appartement : woning waaraan meerdere verblijfsobjecten zijn gerelateerd, ongeacht het gebruiksdoel van deze verblijfsobjecten, minimaal één 'woonfunctie'
    # vrijstaande woning: woning zonder andere verbonden verblijfsobjecten
    # tussen- of geschakelde woning: woning die met meerdere panden met een verblijsobject is verbonden, ook geschakelde woningen. 
    # hoekwoning: eerste of laatste woning in een serie panden. 
    # twee-onder-een-kap: deze woning is verbonden met een enkel pand met een verblijsobject en dit pand is alleen met het eerstgenoemde pand verbonden. 
    woningtypering = woningtypering[['Woningtype', 'geometry']]
    

#%% Spatial join woningtypering & BAG

    BAG_1 = gpd.sjoin(BAG, woningtypering, how = 'left', op = 'intersects')
    BAG_1 = BAG_1[~BAG_1.index.duplicated(keep='first')]
    

#%% Vormfactoren Metabolic: GO (gebruiksoppervlak)/BVO (bruto gebruiksoppervlak) --> nodig voor materiaalintensiteiten Metabolic (ook in dataset Heeren & Fishman (2020))

# Metabolic classificatie (met edit voor afstemming met BAG data)
    
    VF_detached = (0.75+0.67)/2 #gemiddelde van 2-onder-1 kap, vrijstaand
    VF_row = 0.69
    VF_ap_S = 0.92
    VF_ap_L = (0.895+0.915)/2 # idem aan kantoor groot
    VF_office_S = (0.91+0.935+0.91)/3 # gemiddelde van kantoor klein (= gemiddelde katnoor klein & middelgroot), bijeenkomst klein (= gemiddelde van bijeenkomst klein & middelgroot) en zorg klein
    VF_office_L = (0.895+0.915)/2 # gemiddelde van kantoor groot (= gemiddelde kantoor groot & middelgroot), bijeenkomst groot (= gemiddelde van bijeenkomst groot & middelgroot)
    VF_onderwijs = (0.92+0.93+0.93)/3 # gemiddelde van basisschool, middelbare school en hoge school/universiteit
    VF_zorg = 0.88 # zorg groot
    VF_service = (VF_onderwijs+VF_zorg)/2
    VF_retail = 0.91
    VF_bedrijfshal = (0.97+0.91)/2 # gemiddelde van bedrijfsruimten klein en overig klein
    VF_distributie = (0.99+0.94)/2 # gemiddelde van bedrijfsruimten groot en overig groot
    VF_industry = (VF_bedrijfshal+VF_distributie)/2

#%% Classificatie gebouwen MB

# Classificatie (op basis van GO, niet BVO)
    
    BAG_1['Class'] = np.NaN

    BAG_1['Class'].loc[(BAG_1.gebruiks_1 == 'kantoorfunctie') & (BAG_1.GO <=5000)] = 'Office_S'
    
    BAG_1['Class'].loc[(BAG_1.gebruiks_1 == 'kantoorfunctie') & (BAG_1.GO > 5000)] = 'Office_L'
    
    BAG_1['Class'].loc[(BAG_1.gebruiks_1 == 'overige gebruiksfunctie') | \
                       (BAG_1.gebruiks_1 == 'bijeenkomstfunctie') | \
                           (BAG_1.gebruiks_1 == 'logiesfunctie') |\
                               (BAG_1.gebruiks_1 == 'sportfunctie') | \
                                   (BAG_1.gebruiks_1 == 'onderwijsfunctie') | \
                                       (BAG_1.gebruiks_1 == 'overige gebruiksfunctie') | \
                                           (BAG_1.gebruiks_1 == 'gezondheidszorgfunctie')] = 'Service'        
    
    BAG_1['Class'].loc[BAG_1.gebruiksdo == 'industriefunctie'] = 'Industry'
    
    BAG_1['Class'].loc[(BAG_1.gebruiksdo == 'winkelfunctie')] = 'Retail'
    
    BAG_1['Class'].loc[((BAG_1.Woningtype == 'vrijstaande woning') | (BAG_1.Woningtype == 'twee-onder-een-kap' ))] = "Detached" 
    
    BAG_1['Class'].loc[((BAG_1.Woningtype == 'tussenwoning/geschakeld') | (BAG_1.Woningtype == 'hoekwoning' ))] = "Row"
    
    BAG_1['Class'].loc[((BAG_1.Woningtype == 'appartement') & (BAG_1.GO <= 5000))] = "Ap_S" # tot 6 lagen, 6*3 meter per etage = 18m
    
    BAG_1['Class'].loc[((BAG_1.Woningtype == 'appartement') & (BAG_1.GO > 5000))] = 'Ap_L'        
    
    
#%% Conversie GO BVO
        
    BAG_1['Opp_BVO'] = np.NaN
    
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Detached')] = BAG_1['GO']/VF_detached
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Row')] = BAG_1['GO']/VF_row
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Ap_S')] = BAG_1['GO']/VF_ap_S
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Ap_L')] = BAG_1['GO']/VF_ap_L
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Office_S')] = BAG_1['GO']/VF_office_S
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Office_L')] = BAG_1['GO']/VF_office_L
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Service')] = BAG_1['GO']/VF_service
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Industry')] = BAG_1['GO']/VF_industry
    BAG_1['Opp_BVO'].loc[(BAG_1.Class == 'Retail')] = BAG_1['GO']/VF_retail

#%% Sorteren per bouwjaar
    
    for building_type in building_types:
        summed_buildingtype = BAG_1['Opp_BVO'].loc[(BAG_1.bouwjaar <= 1900) & (BAG_1.Class == building_type)].sum()
        I_gebouwen.at[1900, building_type] = I_gebouwen.at[1900, building_type] + summed_buildingtype
        for year in all_years:
            if year != 1900:
                summed_buildingtype = BAG_1['Opp_BVO'].loc[(BAG_1.bouwjaar == year) & (BAG_1.Class == building_type)].sum()
                I_gebouwen.at[year, building_type] = I_gebouwen.at[year, building_type] + summed_buildingtype


#%% Materialisatie gebouwen

    BAG_copy = BAG_1.copy()
#    floor_height = 3 # MI in kg/m2, Materiaal(kg/m2) = opp(m)*hoogte(m)/floor_height(mi)*MI (kg/m2)

    cohort_names = ['<1945', '1945-1970', '1970-2000', '>2000']
    cohort_ranges = [[0,1945], [1945,1970], [1970, 2000],[2000,3000]]

    #BAG_copy['floor_area'] = BAG_copy.loc[:,'Opp_BVO']

    for material in material_columns:
        BAG_copy[material]=np.nan

    for index,cohort in enumerate(cohort_ranges): #  maakt 2 kolommen, index 1,2,3,4,... + waarde (cohort)
        for building_type in building_types:
            BAG_class_cohort_filter = ((BAG_copy['bouwjaar'] >= cohort[0]) & (BAG_copy['bouwjaar'] < cohort[1]) & (BAG_copy['Class'] == building_type))
            BAG_filtered = BAG_copy[BAG_class_cohort_filter]
            for material in material_columns:
                index_name = (building_type, cohort_names[index])
                material_intensity = MI_db.at[index_name, material]          
                BAG_filtered[material] = BAG_filtered.loc[:,'Opp_BVO']*material_intensity # Ópp_BVO was eerst 'floor_area'. A value is trying to be set on a copy of a slice from a DataFrame. Try using .loc[row_indexer,col_indexer]=value instead http://pandas.pydata.org/pandas-docs/stable/indexing.html
                BAG_copy[BAG_class_cohort_filter] = BAG_filtered
    
    dir_out = "C:/Users/jvano/OneDrive - Universiteit Leiden/Files/PhD/Paper IV/Shared_Mike_Janneke/"
    BAG_copy.to_file(dir_out+"GIS_data/BAG_2018_original_classification/"+filename+"_voorraden.shp")
        
 
#%% Calculate total materialintensities in municipality for each class

    M_total_class = pd.DataFrame(columns = material_columns, index = material_index)

    for material in material_columns:
        value = BAG_copy[material].sum()
        M_total_gem.at[os.path.splitext(filename)[0], material] = value
        for building_type in building_types:
            for index,cohort in enumerate(cohort_ranges): #  maakt 2 kolommen, index 1,2,3,4,... + waarde (cohort)
                BAG_class_filter = ((BAG_copy['bouwjaar'] >= cohort[0]) & (BAG_copy['bouwjaar'] < cohort[1]) & (BAG_copy['Class'] == building_type))
                BAG_filtered = BAG_copy[BAG_class_filter]
                value1 = BAG_filtered[material].sum()
                index_name = (building_type, cohort_names[index])
                M_total_class.at[index_name, material]=value1
                
    M_total_NL = M_total_NL.add(M_total_class, fill_value=0)

    print("Einde loop: "+filename)
    
M_total_gem.to_excel(dir_out+'Documents/Stock_2018/M_total_per_municipality_2018.xlsx')
M_total_NL.to_excel(dir_out+'Documents/Stock_2018/M_total_2018.xlsx')  


I_gebouwen.to_excel(dir_out+'Documents/Stock_2018/Inflow_gebouwen_hist.xlsx')

