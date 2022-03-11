'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to estimate the regression model of voter turnout

Author: Victor Perez
Last modified: 09/03/2021
'''

import numpy as np
import pandas as pd

# Read the clean data
clean = pd.read_csv('/data/data.csv')

# Define the name or index position of the explanatory variables
X_cols = []

# Define the name or index position of the dependent variable
y_col = []

# Estimate model
X = get_X(clean, X_cols)
y = get_y(clean, y_col)
betas = regress(X, y)

# Write the results with predicted values for every map dataset
filenames = ['map1', 'map2', 'map3', 'map4', 'map5']
for file in filenames:
    get_prediction_csv(betas, X_cols, file)


def get_prediction_csv(betas, X_cols, filename):
    '''
    Concatenates the predicted values to a dataframe
    and exports the results as a csv
    '''
    input_csv = 'data/' + filename + '.csv'
    output_csv = 'data/' + filename + '_results.csv'
    prediction_data = pd.read_csv(input_csv)
    X = get_X(prediction_data, X_cols)
    prediction_data['predicted_turnout'] = predict(betas, X)
    prediction_data.to_csv(output_csv)


def concatenate_ones(X):
    '''
    Concatenates a column of ones to X
    for the intercept
    Inputs (df) X
    Returns X with a column of ones 
    '''

    ones = np.ones((X.shape[0], 1))
    return np.hstack([ones, X])


def get_X(df, columns):
    '''
    Returns matrix for a given list of column positions
    '''

    try:
        X = df.loc[:, columns].values
    except:
        X = df.iloc[:, columns].values
    X = concatenate_ones(X)
    return X


def get_y(df, column):
    '''
    Return the outcome column for a given column position
    '''
    
    try:
        y = df.loc[:, [column]].values
    except:
        y = df.iloc[:, [column]].values
    return y


def regress(X, y):
    '''
    Runs the OLS regression of y on X
    Inputs: 
    X (df) explanatory variables
    y (df) dependent variable
    Returns coefficient estimates
    '''

    return np.linalg.lstsq(X, y, rcond=None)[0]


def predict(betas, X):
    '''
    Calculates the predicted values
    '''
    return np.dot(X, betas)


# def get_rsq(X, y, betas):
#     '''
#     Return R-squared, the coefficient of determination
#     '''
#     yhat = np.matmul(X, betas)
#     ssto = ((y - y.mean())**2).sum()
#     ssr = ((yhat - y.mean())**2).sum()
#     return (ssr/ssto)