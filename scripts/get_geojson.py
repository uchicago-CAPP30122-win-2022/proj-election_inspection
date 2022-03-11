'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to convert the estimation results in csv into geojson file

Author: Victor Perez
Last modified: 10/03/2021
'''

import geopandas
import pandas as pd

filenames = ['map1', 'map2', 'map3', 'map4', 'map5']

for file in filenames:
    input_csv = 'data/' + filename + '_results.csv'
    input_df = pd.read_csv(input_csv)
    output_geojson

#Join datasets using vtd

#Join datasets using district number

#Export to geojson