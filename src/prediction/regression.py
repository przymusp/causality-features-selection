#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn import linear_model
from sklearn import svm
from sklearn import tree
from math import sqrt
from sklearn.metrics import mean_squared_error

from joblib import Parallel, delayed

import numpy as np
import pandas as pd


from tools.csv_helper import *



def predictbase(fname, output_directory, nbre_months = ""):
    
    models = {
        "SVM" : svm.SVR(),
        #"LinearRegression" :linear_model.LinearRegression(),
        #"BayesianRidge" :linear_model.BayesianRidge(),
        #"Lasso1" :linear_model.Lasso(alpha = 0.1),
        #"Lasso2" :linear_model.Lasso(alpha = 0.2),
        #"Lasso3" :linear_model.Lasso(alpha = 0.3),
        "Ridge1" :linear_model.Ridge(alpha = 0.1),
        "Ridge2" :linear_model.Ridge(alpha = 0.2),
        "Ridge3" :linear_model.Ridge(alpha = 0.3),
        "OrthogonalMatchingPursuit" :linear_model.OrthogonalMatchingPursuit(),
        "DecisionTreeRegressorMaxDepth2" :tree.DecisionTreeRegressor(max_depth=2),
        "DecisionTreeRegressorMaxDepth3" :tree.DecisionTreeRegressor(max_depth=3),
        "DecisionTreeRegressorMaxDepth4" :tree.DecisionTreeRegressor(max_depth=4),
        "DecisionTreeRegressorMaxDepth5" :tree.DecisionTreeRegressor(max_depth=5),
        "DecisionTreeRegressorMaxDepth6" :tree.DecisionTreeRegressor(max_depth=6),
        "TheilSenRegressor" :linear_model.TheilSenRegressor(random_state=42),
        "HuberRegressor" :linear_model.HuberRegressor(),
        "LassoLarsIC" :linear_model.LassoLarsIC(criterion='bic')
}

    data = read_csv_and_metadata(fname)
    meta_header = data.meta_header
    
    # Read meta-data
    nbre_preds = int (meta_header['number_predictions'][0])
    target_names =  (meta_header['predict'])
    X_train = pd.DataFrame
    
    
    for name_model in models:
        k_predictions = pd.DataFrame
        X_train = data
        header_ = []
        #print ("############")
        for nbre_exps in range(0,8):
            header_.extend (["experiment_" + str(nbre_exps+1)])
            test = X_train.tail (nbre_preds).values[:,1:]
            real = X_train.tail (nbre_preds).values[:,0]
            train = X_train.head(X_train.shape[0] - nbre_preds)

            if train.shape[0] > 30:
                train = train.tail (30).values
                X_train = X_train.head(X_train.shape[0] - 30)
            else:
                break

            x_train = train[:,1:]
            y_train = train[:,0]

            model = models[name_model]
            model.fit(x_train, y_train)
            predictions = model.predict (test)
            
            

            for k in range (0, predictions.shape[0]):
                if predictions[k] < 0:
                    predictions[k] = 0.0
                predictions[k] = predictions[k] - real[k]
  
    
            predictions = pd.DataFrame (predictions)
        
            if k_predictions.empty:
                k_predictions = predictions
            else:
                k_predictions = pd.concat ((k_predictions,predictions), axis = 1)


        # Put meta-data for the output file
        k_predictions.meta_header = X_train.meta_header
        k_predictions.meta_header['predict_model'] = [name_model]
        k_predictions.meta_header['predict'] = [target_names[0],]
        k_predictions.meta_header['experiment_type'] = ['competition']
        fname = fname.split('/')[-1]
        out_fname = output_directory + "/" + name_model + "_" + fname

        write_csv_with_metadata(k_predictions, out_fname, header = header_)

#################################################################################
def main ():

    fnames, output_directory = sys.argv[1:-1], sys.argv[-1]
    data_name = output_directory.split("/")[-1]
    #evaluation_directory = "results/evaluation" + data_name + "/"
    
    #if os.path.exists(evaluation_directory + "myfile.csv"):
    #    f = file(evaluation_directory + "myfile.csv", "r+")
    #else:
    #   f = file(evaluation_directory + "myfile.csv", "w")
    
    nbre_months = sys.argv[-1].split("_")[-1].split(".")[0]
 
    Parallel(-1)(delayed(predictbase)(fname, output_directory, nbre_months) for fname in fnames)

if __name__ == "__main__":
    main()



































