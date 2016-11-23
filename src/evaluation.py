#!/usr/bin/python

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import median_absolute_error
import pandas as pd
import numpy as np
import sys
import tools.csv_helper as tools

if __name__ == "__main__":
    ## file of real values
    file_name = sys.argv[1]
    original_data = tools.read_csv_and_metadata(file_name)

    ## file of predictions
    predictions_namefile = sys.argv[2]
    predictions = tools.read_csv_and_metadata(predictions_namefile)
    target = predictions.meta_header['predict'][0]

    ## number of prediction or points from which 5 predictions are made with the vecm.
    nbre_preds = int (sys.argv[3])

    reals = np.ndarray(shape=(nbre_preds,5))
    #print result.size

    inc = 0
    nlin = len (original_data.values[:,0])

    #print dframe.values[0:5,0]
    for i in range(0,nbre_preds):
        vect = original_data[[target]]
        reals[i,:] = vect[nlin-5-inc:nlin-inc].values[:,0]
        inc = inc + 5


    print "==========="
    for i in range(0,5):
        print "Prediction Horoizon: ",i+1
        print "mse: ", round(mean_squared_error (reals[:,1],predictions.values[:,1]),4)
        print "mae: ", round(mean_absolute_error (reals[:,1],predictions.values[:,1]),4)
        print "variance: ", round(explained_variance_score (reals[:,1],predictions.values[:,1]),4)
        print "==========="

