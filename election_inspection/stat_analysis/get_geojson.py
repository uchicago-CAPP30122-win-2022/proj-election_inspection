'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to convert the estimation results in csv into geojson file

Author: Victor Perez
Last modified: 10/03/2021
'''

import pandas as pd
import geopandas as gp

# Map files
maps_dict = {}
maps_dict['apple'] = 'election_inspection/visual_analysis/apple/Apple V2.json'
maps_dict['birch'] = 'election_inspection/visual_analysis/birch/Birch V2.json'
maps_dict['chestnut'] = 'election_inspection/visual_analysis/chestnut/Chestnut.json'
maps_dict['lange'] = 'election_inspection/visual_analysis/lange/Lange Congressional.json'
maps_dict['szetela'] = 'election_inspection/visual_analysis/szetela/szetela.json'

keep_cols = ['DISTRICT', 'pop_perc_white', 
             'pop_perc_black', 'c_gini_index',
            'c_perc_hs_grad', 'predicted_turnout']

for map_name in maps_dict:
    input_csv = 'election_inspection/stat_analysis/' + map_name + '_results.csv'
    input_df = pd.read_csv(input_csv)
    to_export = input_df[keep_cols]
    to_export.rename(columns = {"pop_perc_white" : "PCT_WHITE",
                              "pop_perc_black" : "PCT_BLACK",
                              "c_gini_index" : "GINI_INDEX",
                              "c_perc_hs_grad": "PCT_HS_GRAD",
                              "predicted_turnout" : "PREDICTED_TURNOUT"})
    map_json = maps_dict[map_name]
    map_gdf = gp.read_file(map_json)
    map_gdf['DISTRICT'] = map_gdf['DISTRICT'].astype('int')
    map_gdf.join(to_export.set_index('DISTRICT'), on = 'DISTRICT')
    map_gdf.to_file('election_inspection/visual_analysis/' + map_name + '.geojson', driver = 'GeoJSON')



