'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to match vtd to districts
Uses geojson join to merge the vtds with the district maps 
using the points of the vtds to check that they are inside
the polygon of the district maps

Exports a csv file with the results for each merge 

Author: Victor Perez
Last modified: 10/03/2021
'''

import geopandas
import pandas as pd

apple_json = 'maps/apple/Apple V2.json'
birch_json = 'maps/birch/Birch V2.json'
chestnut_json = 'maps/chestnut/Chestnut.json'
lange_json = 'maps/lange/Lange Congressional.json'
szetela_json = 'maps/szetela/szetela.json'

apple_gdf = geopandas.read_file(apple_json)

vtd_df = pd.read_csv('/data/data.csv')

vtd_gdf = geopandas.GeoDataFrame(vtd_df,
                                 geometry = geopandas.points_from_xy(vtd_df.Longitude,
                                                                     vtd_df.Latitude))

csv_joined_files(apple_json, vtd_gdf, 'data/apple_vtd_joined.csv')
#csv_joined_files(birch_json, vtd_gdf, 'data/birch_vtd_joined.csv')
#csv_joined_files(chestnut_json, vtd_gdf, 'data/chestnut_vtd_joined.csv')
#csv_joined_files(lange_json, vtd_gdf, 'data/lange_vtd_joined.csv')
#csv_joined_files(szetela_json, vtd_gdf, 'data/szetela_vtd_joined.csv')


def csv_joined_files(map_json, vtd_gdf, filename):
    '''
    Writes a csv with  the map of vtd ids and the district ids
    Inputs:
        map_json (json file) district map file
        vtd_gdf (geopandas dataframe) VTD file
        filename (str) filename of the csv to save
    '''
    map_gdf = geopandas.read_file(map_json)
    join_gdf = vtd_gdf.sjoin(map_gdf, how = "left")
    join_gdf.drop('geometry', axis = 1).to_csv(filename)
