#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
from math import sqrt

from joblib import Parallel, delayed

import numpy as np
import pandas as pd
import pprint

from tools.csv_helper import *

###################################################
class toSuppervisedData:
    targets = np.empty([0,0],dtype=float)
    data = np.empty([0,0],dtype=float)
    
    ## constructor
    def __init__(self, X, p):
        self.targets = self.targets_decomposition (X,p)
        self.data = self.matrix_decomposition (X,p)

    ## p-decomposition of a vector
    def vector_decomposition (self,x,p):
        n = len(x)
        output = np.empty([n-p,p],dtype=float)
        for i in range (n-p):
            for j in range (p):
                output[i,j] = x[i+j]
        return output
 #########
    # p-decomposition of a target
    def target_decomposition (self,x,p):
        n = len(x)
        output = np.empty([n-p,1],dtype=float)
        for i in range (n-p):
            output[i] = x[i+p]
        return output
 ########
    # p-decomposition of a matrix
    def matrix_decomposition (self,x,p):
        output = np.empty([0,0],dtype=float)
        out = np.empty([0,0],dtype=float)
        for i in range(x.shape[1]):
            out = self.vector_decomposition(x[:,i],p)
            #print (out)
            if output.size == 0:
                output = out
            else:
                output = np.concatenate ((output,out),axis=1)

        return output
#########
    # extract all the targets decomposed
    def targets_decomposition (self,x,p):
        output = np.empty([0,0],dtype=float)
        out = np.empty([0,0],dtype=float)
        for i in range(x.shape[1]):
            out = self.target_decomposition(x[:,i],p)
            if output.size == 0:
                output = out
            else:
                output = np.concatenate ((output,out),axis=1)

        return output

################################################################################
def normalize (M):
    minMax = np.empty ([M.shape[1], 2])
    for i in range(M.shape[1]):
        #print (M[:,i])
        max = np.max(M[:,i])
        min = np.min(M[:,i])
        minMax[i,0] = min
        minMax[i,1] = max

        for j in range(M.shape[0]):
            M[j,i] = (M[j,i] - min) / (max - min)

    return minMax
################################################################################
def inverse_normalize (M,minMax):
    for i in range(M.shape[0]):
        M[i] = M[i] * (minMax[1] - minMax[0]) + minMax[0]
    return M

#################################################################################

# fit an LSTM network to training data
def fit_lstm(train, batch_size, nb_epoch, neurons):
    X, y = train[:, 1:train.shape[1]], train[:, 0]
    X = X.reshape(X.shape[0], 1, X.shape[1])
    
    model = Sequential()
    model.add (LSTM (neurons, batch_input_shape = (batch_size, X.shape[1], X.shape[2])))
    model.add(Dense(1))
    
    model.compile(loss='mean_squared_error', optimizer='adam')
    
    for i in range(nb_epoch):
        model.fit(X, y, epochs=1, batch_size=batch_size, verbose=0, shuffle=False)
        model.reset_states()
    return model
#################################################################################
# make a one-step forecast
def forecast_lstm(model, batch_size, X):
    X = X.reshape(1, 1, len(X))
    yhat = model.predict(X, batch_size=batch_size)
    return yhat[0,0]

#################################################################################
def LSTM_MODEL (X_train, nbre_preds, p, nbre_iterations, neurons):

    # normalize the data
    minMax = normalize(X_train)

    # transform the data to supervised learning
    if p > 0:
        model = toSuppervisedData(X_train, p)
        X = model.data
        targets = model.targets
        
        current_target = targets[:,0:1]
        current_predictors = targets[:,1:targets.shape[1]]
        X = np.concatenate ((current_predictors, X), axis = 1)
        X = np.concatenate ((current_target, X), axis = 1)
    
    if p == 0:
        X = X_train

    predictions = np.empty ([nbre_preds, 1])

    reals = targets[targets.shape[0] - nbre_preds:targets.shape[0],:]
    
    limit = X.shape[0] - nbre_preds

    train, test = X[0:limit], X[limit:X.shape[0]]
    lstm_model =  fit_lstm(train, 1, nbre_iterations, neurons)

    prediction = []
    
    for j in range(0, nbre_preds):
        limit = X.shape[0] - nbre_preds + j
        train, test = X[0:limit], X[limit:limit+1]
        Xx, yy = test[0, 1:test.shape[1]], test[0, 0]
            
        # prediction
        yhat = forecast_lstm(lstm_model, 1, Xx)
        prediction.append(yhat)
        #print (yhat)
    
        # update the model: online learning
        X_update = np.concatenate ((train, test), axis = 0)
        Xx, yy = X_update[:, 1:X.shape[1]], X_update[:, 0]
        Xx = Xx.reshape(Xx.shape[0], 1, Xx.shape[1])

        lstm_model.fit(Xx, yy, epochs=1, batch_size=1)
        lstm_model.reset_states()
    
    
    predictions[:,0] = prediction
    predictions = inverse_normalize (predictions,minMax[0,:])
    reals = inverse_normalize (reals, minMax[0,:])
    
    return np.array(predictions),reals
#################################################################################

def predictbase(fname, output_directory):
 
    X_train = read_csv_and_metadata(fname)
    
    meta_header = X_train.meta_header
    
    # Read meta-data
    barch_size= 1
    nbre_preds = int (meta_header['number_predictions'][0])
    nbre_iterations = 1000
    p = int (meta_header['lag_parameter'][0])
    horizon = int (meta_header['horizon'][0])
    target_names =  (meta_header['predict'])
    
    # Compute the number of neurones
    neurones = int (float ((X_train.values.shape[1] * p + 1) * (2.0 / 3.0)))
    #neurones = int (X_train.values.shape[1] * p)
    
    predictions, reals = LSTM_MODEL (X_train.values, nbre_preds, p, nbre_iterations, neurones)
    predictions = pd.DataFrame (predictions[:,0])
    
    # Put meta-data for the output file
    predictions.meta_header = X_train.meta_header
    predictions.meta_header['predict_model'] = ["lstm_prediction"]
    predictions.meta_header['predict'] = [target_names[0],]
    
    fname = fname.split('/')[-1]
    
    out_fname = output_directory + "/_lstm_predict_" + fname
    
    write_csv_with_metadata(predictions, out_fname)


#################################################################################
def main ():
    
    fnames, output_directory = sys.argv[1:-1], sys.argv[-1]
    Parallel(-1)(delayed(predictbase)(fname, output_directory) for fname in fnames)


if __name__ == "__main__":
    main()


































