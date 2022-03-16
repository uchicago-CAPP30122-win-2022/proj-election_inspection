'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to estimate the regression model of voter turnout

Author: Victor Perez
Last modified: 15/03/2021
'''

import pandas as pd
import estimation_util

clean = pd.read_csv('working_dataset.csv')
clean['GEOID20'] = clean['GEOID20'].astype('int')
clean['DISTRICT'] = clean['DISTRICT'].astype('int')

# Define the index position of the explanatory variables
X_cols = list(range(5,22))

# Define the index position of the dependent variable
y_col = 22

best_X_cols = estimation_util.forward_selection_AIC(clean, y_col, X_cols)
X = estimation_util.get_X(clean, best_X_cols)
y = estimation_util.get_y(clean, y_col)
betas = estimation_util.regress(X, y)

def write_prediction_csv(betas, X_cols, map_name, clean_df):
    '''
    Concatenates the predicted values to a dataframe
    and exports the results as a csv
    '''
    map = pd.read_csv('stat_analysis/' + map_name + '_vtd_joined.csv')
    clean_df.join(map.set_index('GEOID20'), on = 'GEOID20')
    collapsed = clean_df.groupby(['DISTRICT']).mean()
    X = estimation_util.get_X(collapsed, X_cols)
    collapsed['predicted_turnout'] = estimation_util.predict(betas, X)
    collapsed.to_csv('stat_analysis/' + map_name + '_results.csv')


# Define the filenames of the files for each map
map_names = ['apple', 'birch', 'chestnut', 'lange', 'szetela']
for name in map_names:
    write_prediction_csv(betas, best_X_cols, name, clean)


# apple = pd.read_csv('stat_analysis/apple_vtd_joined.csv')
# birch = pd.read_csv('stat_analysis/birch_vtd_joined.csv')
# chestnut = pd.read_csv('stat_analysis/chestnut_vtd_joined.csv')
# lange = pd.read_csv('stat_analysis/lange_vtd_joined.csv')
# szetela = pd.read_csv('stat_analysis/szetela_vtd_joined.csv')


