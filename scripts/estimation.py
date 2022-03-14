'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script to estimate the regression model of voter turnout

Author: Victor Perez
Last modified: 12/03/2021
'''

import numpy as np
import pandas as pd
import math



clean = pd.read_csv('/data/csv/data.csv')

# Define the index position of the explanatory variables
X_cols = []

# Define the index position of the dependent variable
y_col = []

best_X_cols = forward_selection(clean, y_col, len(X_cols))
X = get_X(clean, best_X_cols)
y = get_y(clean, y_col)
betas = regress(X, y)

# Define the filenames of the files for each map
filenames = ['map1', 'map2', 'map3', 'map4', 'map5']
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
    X = get_X(prediction_data, X_cols)
    prediction_data['predicted_turnout'] = predict(betas, X)
    prediction_data.to_csv(output_csv)


def forward_selection(df, y_col, x_num):
    '''
    Performs forward selection to find the 'best' explanatory
    variables of a model using AIC
    Inputs:
        df (pandas dataframe) dataset
        y_col (int) index or name of the dependent variable
        x_num (int) number of max explanatory variables to
            include in the model
    Returns:
        list of indices of selected explanatory variables
    '''
    y = get_y(df, y_col)
    n = df.shape[0]
    k_cols = []
    aic_star = float('inf')
    for _ in x_num:
        cols_available = list(set(X_cols) - set(k_cols))
        best_k = float('inf')
        aic_k = float('inf')
        for k in cols_available:
            X = get_X(df, k_cols + [k])
            betas = regress(X, y)
            yhat = predict(betas, X)
            aic = get_AIC(y, yhat, n, X.shape[1])
            if aic < aic_k:
                best_k = k
                aic_k = aic
        if aic_k < aic_star:
            aic_star = aic_k
            k_cols.append(best_k)
            continue
        break
    return k_cols


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
    X = df.iloc[:, columns].values
    X = concatenate_ones(X)
    return X


def get_y(df, column):
    '''
    Return the outcome column for a given column position
    '''
    return df.iloc[:, [column]].values


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


def get_AIC(y, yhat, n, k):
    '''
    Calculates the Akaike Information Criteria
    of a regression model 
    Inputs:
        y (series) dependent variable
        yhat (series) predicted values
        n (int) number of observations
        k (int) number of dependent variables
    Returns:
        AIC (float)
    '''
    dof = n - k
    ssr  = ((yhat - y.mean()) ** 2).sum()
    sigma = math.sqrt(ssr / dof)
    return 2 * k + 2 * math.log(2.5 * sigma ) + dof
