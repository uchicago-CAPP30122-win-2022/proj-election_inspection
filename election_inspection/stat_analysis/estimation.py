'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to estimate the regression model of voter turnout

Author: Victor Perez
Last modified: 15/03/2021
'''

import pandas as pd
import estimation_util

clean = pd.read_csv('working_dataset.csv', index_col = 0)

# Define the index position of the explanatory variables
X_cols = list(range(3,23))

# Define the index position of the dependent variable
y_col = 23

best_X_cols = estimation_util.forward_selection_AIC(clean, y_col, X_cols)
X = estimation_util.get_X(clean, best_X_cols)
y = estimation_util.get_y(clean, y_col)
betas = estimation_util.regress(X, y)


def write_prediction_csv(betas, X_cols, map_name, clean_df):
    '''
    Concatenates the predicted values to a dataframe
    and exports the results as a csv
    '''
    map = pd.read_csv('election_inspection/stat_analysis/' + map_name + '_vtd_joined.csv',
                       index_col = 0)
    clean_df = clean_df.join(map)
    sums = clean_df.loc[:, ['DISTRICT', 'total_pop', 'pop_perc_white', 'c_perc_hs_grad', 'turnout2018_registered', 'c_pop_pct_urban']]
    sums = sums.groupby(['DISTRICT']).sum()
    means = clean_df.groupby(['DISTRICT']).mean()
    X = estimation_util.get_X(collapsed, X_cols)
    means['predicted_turnout'] = estimation_util.predict(betas, X)
    results = means.join(sums)
    results.to_csv('election_inspection/stat_analysis/' + map_name + '_results.csv')


# Define the filenames of the files for each map
map_names = ['apple', 'birch', 'chestnut', 'lange', 'szetela']
for name in map_names:
    write_prediction_csv(betas, best_X_cols, name, clean)
