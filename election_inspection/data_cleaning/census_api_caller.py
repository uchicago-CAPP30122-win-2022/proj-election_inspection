'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to retrieve data about Michigan from the Census Bureau API.

Author: Christian Jordan
'''
import requests
import pandas as pd


def get_census_data(year, dataset, var_lst, unit, dataset_topic):
    '''
    Function to retrieve data for Michigan from the Census Bureau's API.

    Input:
        year : (int) year of data
        dataset : (str) dataset name
        var_lst : (list) list of variables
        unit : (str) geographical unit the data has been taken from
    
    Output:
        pandas dataframe (returns None if request is bad)
    '''
    api_key = "83fdc3ae9f205e7d930e9b92321c489fbcc4707e"
    
    # Build query
    query_base = f"https://api.census.gov/data/{year}/{dataset}"
    query_vars = f"?get={','.join(var_lst)}"
    query_geo = f"&for={unit}:*&in=state:26"
    key = f"&key={api_key}"
    query = query_base + query_vars + query_geo + key

    # Query API
    response = requests.get(query)
    if not response.status_code == requests.codes.ok:
            return None
    print(f'Retrieved {dataset_topic} data from Census Bureau API.')

    # Build dataframe
    data_json = response.json()
    census_df = pd.DataFrame(data_json[1:], columns=data_json[0])
    census_df = census_df.drop('state', axis=1)
    
    return census_df