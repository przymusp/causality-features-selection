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
    nbre_preds = len(predictions.index)

    reals = np.ndarray(shape=(nbre_preds,5))
    #print result.size

    inc = 0
    nlin = len (original_data.values[:,0])

    #print dframe.values[0:5,0]
    for i in range(0,nbre_preds):
        vect = original_data[[target]]
        reals[i,:] = vect[nlin-5-inc:nlin-inc].values[:,0]
        inc = inc + 5
    results = np.ndarray(shape=(5,3))

    print predictions.values[:,1]
    columns = ["mse","mae","variance"]
    rows = []
    print ("===========")
    for i in range(0,5):
        rows.append ("h" + str(i+1))
        results[i,0] = round(mean_squared_error (reals[:,i],predictions.values[:,i]),4)
        results[i,1] = round(mean_absolute_error (reals[:,i],predictions.values[:,i]),4)
        results[i,2] = round(explained_variance_score (reals[:,i],predictions.values[:,i]),4)

    df_results = pd.DataFrame(results, index = rows, columns = columns)
    print (df_results)
