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
X_cols = list(range(1,20))

# Define the index position of the dependent variable
y_col = 20

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
    means = clean_df.groupby(['DISTRICT']).mean()
    X = estimation_util.get_X(means, X_cols)
    means['predicted_turnout'] = estimation_util.predict(betas, X)
    means.to_csv('election_inspection/stat_analysis/' + map_name + '_results.csv')


# Define the filenames of the files for each map
map_names = ['apple', 'birch', 'chestnut', 'lange', 'szetela']
for name in map_names:
    write_prediction_csv(betas, best_X_cols, name, clean)


# Create the results at the vtd for visualization
X = estimation_util.get_X(clean, best_X_cols)
clean['predicted_turnout'] = estimation_util.predict(betas, X)
clean.to_csv('election_inspection/stat_analysis/vtd_results.csv')
