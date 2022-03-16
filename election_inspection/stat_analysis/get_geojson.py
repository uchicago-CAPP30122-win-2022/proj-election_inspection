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
apple_json = 'visual_analysis/apple/Apple V2.json'
birch_json = 'visual_analysis/birch/Birch V2.json'
chestnut_json = 'visual_analysis/chestnut/Chestnut.json'
lange_json = 'visual_analysis/lange/Lange Congressional.json'
szetela_json = 'visual_analysis/szetela/szetela.json'

map_names = ['apple', 'birch', 'chestnut', 'lange', 'szetela']
keep_cols = ['DISTRICT']

for map_name in map_names:
    input_csv = 'stat_analysis/' + map_name + '_results.csv'
    input_df = pd.read_csv(input_csv)
    to_export = input_df[keep_cols]
    map_gdf = gp.read_file(map_name + '_json')
    to_export.join(map_gdf.set_index('DISTRICT'), on = 'DISTRICT')
    to_export.to_file('visual_analysis/' + map_name + '_results.geojson', driver = 'GeoJSON')
