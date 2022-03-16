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

apple = pd.read_csv('data/csv/apple_vtd_joined.csv')
birch = pd.read_csv('data/csv/birch_vtd_joined.csv')
chestnut = pd.read_csv('data/csv/chestnut_vtd_joined.csv')
lange = pd.read_csv('data/csv/lange_vtd_joined.csv')
szetela = pd.read_csv('data/csv/szetela_vtd_joined.csv')

df.join(other.set_index('key'), on='key')
clean.join(apple.set_index('GEOID20'), on = 'GEOID20')


# Define the index position of the explanatory variables
X_cols = list(range(5,22))

# Define the index position of the dependent variable
y_col = 22

best_X_cols = estimation_util.forward_selection_AIC(clean, y_col, X_cols)
X = estimation_util.get_X(clean, best_X_cols)
y = estimation_util.get_y(clean, y_col)
betas = estimation_util.regress(X, y)


# Define the filenames of the files for each map
filenames = ['apple', 'birch', 'chestnut', 'lange', 'szetela']
for file in filenames:
    write_prediction_csv(betas, best_X_cols, file)


def write_prediction_csv(betas, X_cols, filename):
    '''
    Concatenates the predicted values to a dataframe
    and exports the results as a csv
    '''
    input_csv = 'data/csv/' + filename + '.csv'
    output_csv = 'data/csv/' + filename + '_results.csv'
    prediction_data = pd.read_csv(input_csv)
    X = estimation_util.get_X(prediction_data, X_cols)
    prediction_data['predicted_turnout'] = estimation_util.predict(betas, X)
    prediction_data.to_csv(output_csv)
