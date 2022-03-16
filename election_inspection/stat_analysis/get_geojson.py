'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to convert the estimation results in csv into geojson file

Author: Victor Perez
Last modified: 16/03/2021
'''

import stat_analysis
import pandas as pd
import geopandas as gp

def run_get_geojson():
    # Map files
    maps_dict = {}
    maps_dict['apple'] = 'election_inspection/visual_analysis/apple/Apple V2.json'
    maps_dict['birch'] = 'election_inspection/visual_analysis/birch/Birch V2.json'
    maps_dict['chestnut'] = 'election_inspection/visual_analysis/chestnut/Chestnut.json'
    maps_dict['lange'] = 'election_inspection/visual_analysis/lange/Lange Congressional.json'
    maps_dict['szetela'] = 'election_inspection/visual_analysis/szetela/szetela.json'
    maps_dict['vtd'] = 'election_inspection/visual_analysis/tl_2020_26_vtd20/tl_2020_26_vtd20.shp'

    keep_cols = ['pop_perc_white', 
                'pop_perc_black', 'c_gini_index',
                'c_perc_hs_grad', 'predicted_turnout']

    for map_name in maps_dict:
        input_csv = 'election_inspection/stat_analysis/' + map_name + '_results.csv'
        input_df = pd.read_csv(input_csv)
        
        map_json = maps_dict[map_name]
        map_gdf = gp.read_file(map_json)
        if map_name == 'vtd':
            input_df = input_df[keep_cols + ['GEOID20']]
            remove = map_gdf['GEOID20'].str.contains('Z')
            map_gdf = map_gdf[ ~remove]
            map_gdf['GEOID20'] = map_gdf['GEOID20'].astype('int64')
            map_gdf = map_gdf.join(input_df.set_index('GEOID20'), on = 'GEOID20')
        else:
            input_df = input_df[keep_cols + ['DISTRICT']]
            map_gdf['DISTRICT'] = map_gdf['DISTRICT'].astype('int64')
            map_gdf = map_gdf.join(input_df.set_index('DISTRICT'), on = 'DISTRICT')
        map_gdf = map_gdf.rename(columns = {"pop_perc_white" : "PCT_WHITE",
                                "pop_perc_black" : "PCT_BLACK",
                                "c_gini_index" : "GINI_IDX",
                                "c_perc_hs_grad": "PCT_HS_GRAD",
                                "predicted_turnout" : "PREDICTED_TURNOUT"})
        convert_cols = ['PCT_WHITE', 'PCT_BLACK', 'PCT_HS_GRAD', 'PREDICTED_TURNOUT']
        for col in convert_cols:
            map_gdf[col] = map_gdf[col] * 100
            map_gdf[col] = map_gdf[col].round(2)
        map_gdf.to_file('election_inspection/visual_analysis/' + map_name + '.geojson', driver = 'GeoJSON')
