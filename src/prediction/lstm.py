#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from math import sqrt

from joblib import Parallel, delayed

import numpy as np
import pandas as pd
import pprint

import os
from tools.csv_helper import *
from tqdm import tqdm



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
###################################################
def timeseries_to_supervised(data, lag = 1):
    df = pd.DataFrame(data[:,1:])
    columns = [df.shift(i) for i in range (0, lag+1)]
    #columns.append(pd.DataFrame(data[:,0]))
    columns = pd.concat(columns, axis=1)
    columns = pd.concat((pd.DataFrame(data[:,0]),columns), axis=1)
    #df.fillna(0, inplace=True)
    return columns[lag:]

####################################################
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
#####################################################
def inverse_normalize (M,minMax):
    for i in range(M.shape[0]):
        M[i] = M[i] * (minMax[1] - minMax[0]) + minMax[0]
    return M

######################################################

# fit an LSTM network to training data
def fit_lstm(model, train, look_back, batch_size, nb_epoch, neurons):
    X, y = train[:, 1:train.shape[1]], train[:, 0]
    X = X.reshape(X.shape[0], look_back, X.shape[1] / look_back)

    #model = Sequential()
    #model.add (LSTM (neurons, batch_input_shape = (batch_size, X.shape[1], X.shape[2])))
    #model.add(Dense(1))
    #
    #model.compile(loss='mean_squared_error', optimizer='adam')

    #for i in range(nb_epoch):
    model.fit(X, y, epochs=nb_epoch, batch_size=batch_size, verbose=0, shuffle=False)
        #model.reset_states()
    return model
#####################################################
# make a one-step forecast
def forecast_lstm(model,look_back, batch_size, X):
    X = X.reshape(1, look_back, len(X)/look_back)
    yhat = model.predict(X, batch_size=batch_size)
    return yhat[0,0]

#################################################################################
<<<<<<< HEAD
def imp_LSTM (data, nbre_preds, p, nbre_iterations, neurons, batchSize = 1):
=======
def imp_LSTM (model, data, nbre_preds, p, nbre_iterations, neurons):
>>>>>>> c9ea0c376e20f7af40f500dd3a6cdf8834766c26

    # normalize the data
    minMax = normalize(data)

    # transform the data to supervised learning
    modelS = toSuppervisedData(data,p)
    X = modelS.data
    # Extract target variables
<<<<<<< HEAD
    targets = model.targets
=======
    targets = modelS.targets

    #print (targets.shape[1],X.shape[1])

>>>>>>> c9ea0c376e20f7af40f500dd3a6cdf8834766c26
    predictions = np.empty ([nbre_preds, 1])
    reals = targets[targets.shape[0] - nbre_preds:targets.shape[0],:]
    X = np.concatenate ((targets[:,0:1], X), axis = 1)
<<<<<<< HEAD
    limit = X.shape[0] - nbre_preds
    train, test = X[0:limit], X[limit:X.shape[0]]
    lstm_model =  fit_lstm(train, p, batchSize, nbre_iterations, neurons)
=======

    limit = X.shape[0] - nbre_preds

    train, test = X[limit-40:limit], X[limit:X.shape[0]]
    lstm_model =  fit_lstm(model, train, p, 10, nbre_iterations, neurons)

>>>>>>> c9ea0c376e20f7af40f500dd3a6cdf8834766c26
    prediction = []

    for j in range(0, nbre_preds):
        limit = X.shape[0] - nbre_preds + j
        train, test = X[limit-1:limit], X[limit:limit+1]
        Xx, yy = test[0, 1:test.shape[1]], test[0, 0]

        # prediction
        yhat = forecast_lstm(lstm_model,p, batchSize, Xx)
        prediction.append(yhat)
        #print (yhat)

        # update the model: online learning
        X_update = np.concatenate ((train, test), axis = 0)
        Xx, yy = X_update[:, 1:X.shape[1]], X_update[:, 0]
        Xx = Xx.reshape(Xx.shape[0], p, Xx.shape[1] / p)

<<<<<<< HEAD
        lstm_model.fit(Xx, yy, epochs=1, batch_size= min (batchSize, Xx.shape[0]))
    #lstm_model.reset_states()
    
    
    predictions[:,0] = prediction
    predictions = inverse_normalize (predictions,minMax[0,:])
    reals = inverse_normalize (reals, minMax[0,:])

    return np.array(predictions),reals
#################################################################################

def predictbase (fname, output_directory, reset = 0):
    
    fname_ = fname.split('/')[-1]
    out_fname = output_directory + "/_lstm_" + fname_
    
    X_train = read_csv_and_metadata(fname)
    meta_header = X_train.meta_header
    nbre_preds = int (meta_header['number_predictions'][0])
=======
        lstm_model.fit(Xx, yy, epochs=1, batch_size=1, verbose=0)
        #lstm_model.reset_states()


    predictions[:,0] = prediction



    predictions = inverse_normalize (predictions,minMax[0,:])
    reals = inverse_normalize (reals, minMax[0,:])

#print (pd.DataFrame (predictions))
    return np.array(predictions),reals
#################################################################################

def predictbase (fname, output_directory):

    import os
    os.environ["THEANO_FLAGS"] = "base_compiledir=theano_cache/" + str(os.getpid()%12)
    import keras
    from keras.models import load_model
    from keras.models import Sequential
    from keras.layers import LSTM, Dense
    from keras.models import model_from_json
    import theano.gof as thelock


    X_train = read_csv_and_metadata(fname)

    meta_header = X_train.meta_header

    # Read meta-data
    barch_size= 1
    nbre_preds = int (meta_header['number_predictions'][0])
    nbre_iterations = 40
>>>>>>> c9ea0c376e20f7af40f500dd3a6cdf8834766c26
    p = int (meta_header['lag_parameter'][0])
    horizon = 1
    target_names =  (meta_header['predict'])
<<<<<<< HEAD
    #rest  =  (X_train.shape[0] - nbre_preds - p) % 10
    X_train = X_train.tail (X_train.shape[0] * 7 / 10)
    batchSize = 1
    nbre_iterations = 100
    
    if not os.path.exists(out_fname):
        n_predictions = 0
    
    if os.path.exists(out_fname):
        predictions = read_csv_and_metadata(out_fname)
        n_predictions = predictions.shape [0]
    
    if n_predictions < nbre_preds or reset == 1:
        print ("Processing file %s" % out_fname)
        neurones = int (X_train.values.shape[1] * p)
        predictions, reals = imp_LSTM (X_train.values, nbre_preds, p, nbre_iterations, neurones, batchSize)
        predictions = pd.DataFrame (predictions[:,0])
    
        # Put meta-data for the output file
        predictions.meta_header = X_train.meta_header
        predictions.meta_header['predict_model'] = ["lstm"]
        predictions.meta_header['predict'] = [target_names[0],]

    
        write_csv_with_metadata(predictions, out_fname)
    else:
        print ( bcolors.OKGREEN + "File %s already exist" % out_fname + bcolors.ENDC)
    print ("Done...")
=======

    # Compute the number of neurones
    neurones = int (float ((X_train.values.shape[1] * p + 1) * (2.0 / 3.0)))
    #neurones = int (X_train.values.shape[1] * p)
    # m = load_model("models/lstm" + str(int(X_train.values.shape[1])))
    m = build_model(int(X_train.values.shape[1]))
    predictions, reals = imp_LSTM (m, X_train.values, nbre_preds, p, nbre_iterations, neurones)
    predictions = pd.DataFrame (predictions[:,0])

    # Put meta-data for the output file
    predictions.meta_header = X_train.meta_header
    predictions.meta_header['predict_model'] = ["lstm"]
    predictions.meta_header['predict'] = [target_names[0],]

    fname = fname.split('/')[-1]

    out_fname = output_directory + "/_lstm_" + fname

    write_csv_with_metadata(predictions, out_fname)
>>>>>>> c9ea0c376e20f7af40f500dd3a6cdf8834766c26


#################################################################################
def build_model(i):
    model = Sequential()
    neurons = int (float ((i * 1 + 1) * (2.0 / 3.0)))
    batch_size = 10
    model.add (LSTM (neurons, batch_input_shape = (batch_size, 4, i)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='sgd')
    return model

def main ():
    #print ("############")
    #for i in tqdm(range(2,150)):
    #    m = build_model(i)
    #    m.save("models/lstm"+str(i))
    #    print (m.to_json())
    #    model = model_from_json(json_string)
    #    exit(0)

    fnames, output_directory = sys.argv[1:-1], sys.argv[-1]
<<<<<<< HEAD
    Parallel(-1)(delayed(predictbase)(fname, output_directory, reset = 0) for fname in fnames)
                 
                 
if __name__ == "__main__":
    main()
































=======
    #model = Sequential()
    #model.add (LSTM (10, batch_input_shape = (10, 10, 10)))
    #model.add(Dense(1))
    #model.compile(loss='mean_squared_error', optimizer='adam')
    Parallel(-1)(delayed(predictbase)(fname, output_directory) for fname in fnames)
>>>>>>> c9ea0c376e20f7af40f500dd3a6cdf8834766c26


if __name__ == "__main__":
    main()
