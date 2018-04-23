#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

from sklearn import linear_model

from math import sqrt

from joblib import Parallel, delayed

import numpy as np
import pandas as pd
import pprint

import os

from tools.csv_helper import *
from tqdm import tqdm

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
            if output.size == 0:
                output = out
            else:
                output = np.concatenate ((output,out),axis=1)

        return output
######################################################
def Ridge (X, targets, nbre_preds):

    targets = np.array (targets)
    predictions = np.empty ([nbre_preds, targets.shape[1]])
    reals = targets[targets.shape[0] - nbre_preds:targets.shape[0],:]

    limit = X.shape[0] - nbre_preds
    X_train, test = X[0:limit], X[limit:X.shape[0]]
    Y_train = targets [0:limit]

    reg = linear_model.Ridge (alpha = .5)
    model = reg.fit (X_train, Y_train)

    for j in range(0, nbre_preds):
        limit = X.shape[0] - nbre_preds + j
        train, test = X[limit-1:limit], X[limit:limit+1]
        target, target_test = targets[limit-1:limit], targets[limit:limit+1]

        # prediction
        yhat = reg.predict (test)
        predictions [j] = yhat
            
        # update the model: online learning
        X_update = np.concatenate ((train, test), axis = 0)
        model = reg.fit (X_update, np.concatenate ((target, target_test), axis = 0))
    
    return pd.DataFrame (predictions)

#########################################################

def predictbase (fname, output_directory, reset = 0):
    fname_ = fname.split('/')[-1]
    print ("Processing: %s \n" % fname_)
    data = read_csv_and_metadata(fname)
    meta_header = data.meta_header
    nbre_preds = int (meta_header['number_predictions'][0])
    targets = meta_header['predict']
    

    p = int (meta_header['lag_parameter'][0])
    model = toSuppervisedData (data.values, p)
    X = model.data
    targets_ = model.targets
    
    for target in targets:
        out_fname = output_directory + "/Ridge_" + fname_ + "_" + target + "_Ridge.csv"
        predictions = Ridge (X, data[[target]], nbre_preds)
        
        predictions.meta_header = data.meta_header
        predictions.meta_header['predict_model'] = ["VAR-Ridge"]
        predictions.meta_header['method'] = ["Ridge"]
        predictions.meta_header['predict'] = [target,]
        write_csv_with_metadata(predictions, out_fname)


###########################################################
def main ():

    fnames, output_directory = sys.argv[1:-1], sys.argv[-1]
    predictbase (fnames[0], output_directory)

if __name__ == "__main__":
    main()





