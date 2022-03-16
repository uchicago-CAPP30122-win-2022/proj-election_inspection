'''
Election Inspection

Christian Jordan, Alejandro Navarrete, Victor Perez

Script with auxiliary functions estimate the regression
model of voter turnout

Author: Victor Perez
Last modified: 15/03/2021
'''

import numpy as np


def forward_selection_AIC(df, y_col, X_cols):
    '''
    Performs forward selection to find the 'best' explanatory
    variables of a model using AIC
    Inputs:
        df (pandas dataframe) dataset
        y_col (int) index or name of the dependent variable
    Returns:
        list of indices of selected explanatory variables
    '''
    y = get_y(df, y_col)
    n = df.shape[0]
    k_cols = []
    aic_star = float('inf')
    for i in X_cols:
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


def forward_selection_AR2(df, y_col, X_cols):
    '''
    Performs forward selection to find the 'best' explanatory
    variables of a model using adjusted R2
    Inputs:
        df (pandas dataframe) dataset
        y_col (int) index or name of the dependent variable
    Returns:
        list of indices of selected explanatory variables
    '''
    y = get_y(df, y_col)
    n = df.shape[0]
    k_cols = []
    ar2_star = float('-inf')
    for i in X_cols:
        cols_available = list(set(X_cols) - set(k_cols))
        best_k = float('-inf')
        ar2_k = float('-inf')
        for k in cols_available:
            X = get_X(df, k_cols + [k])
            betas = regress(X, y)
            yhat = predict(betas, X)
            ar2 = get_adjusted_R2(yhat, y, n, X.shape[1])
            if ar2_k < ar2:
                best_k = k
                ar2_k = ar2
        if ar2_star < ar2_k:
            ar2_star = ar2_k
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
    X1 = np.concatenate((X,
                        np.ones((X.shape[0])).reshape(-1, 1)), 
                        axis = 1)
    return X1


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
    return np.linalg.lstsq(X, y, rcond = None)[0]


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
        k (int) number of coefficient estimates
    Returns:
        AIC (float)
    '''   
    ssr = ((y - yhat) ** 2).sum()
    return n * np.log(ssr / n) + 2 * k


def get_adjusted_R2(yhat, y, n, k):
    '''
    Calculates the Adjusted R2 of a regression 
    model
    Inputs:
        y (series) dependent variable
        yhat (series) predicted values
        n (int) number of observations
        k (int) number of coefficient estimates
    Returns:
        Adujsted R2 (float)
    '''
    sst = ((y - y.mean()) ** 2).sum()
    ssr = ((y - yhat) ** 2).sum()    
    dofn = n - 1
    dofd = n - k
    return (1 - (ssr / dofn) / (sst / dofd))
