#!/usr/bin/python

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error
import pandas as pd
import numpy as np
import sys
import tools.csv_helper as tools
import collections

# All used measures
global_measures = {
        'mse': mean_squared_error,
        'mae': mean_absolute_error,
        'evc': explained_variance_score,
        }

def preaty_print(results_collection):
    # TODO: Fix that
    colors = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
    measures = global_measures.keys()
    cmap = dict(zip(measures, colors[:len(measures)]))

    for target in results_collection:
        for h in range(5): # diffrent timehorizons
            print ("<h3>Target: %s Time horizon: %s</h3>" % (target, h))
            df = pd.DataFrame.from_dict(results_collection[target][h]).transpose()
            s = df.style
            for m in measures:
               s.bar(subset=[m,], color=cmap[m])
            print (s.render())

def transform_real_values(df, nbre_preds, target):
    # transform real values into correct form
    reals = []
    for h in range(nbre_preds):
        reals.append(df[[target]][-nbre_preds - 5 + h: -nbre_preds + h].values.T[0])
    return np.stack(reals)

def evaluate_prediction(original_data, predictions):
    """Evaluate prediction results

    :real_values: a transformed data frame with real values
    :predicted_file): a data frame with predicted values
    :returns: evaluation measurments

    """

    results = collections.defaultdict(dict)
    for m in global_measures:
        for i in range(5):
            results[i][m] = global_measures[m](original_data[:,i],predictions.values[:,i])

    return results


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: at least 2 files are needed to compare")
        exit(0)

    ## Read first prediction file to guess the number of predicted values
    original_data = tools.read_csv_and_metadata(sys.argv[1])

    # Cache for orginal data representation suitable for prediction comparison
    folded_orginal_data_dict = collections.defaultdict(dict)

    # Results
    results_collection = collections.defaultdict(lambda : collections.defaultdict(dict))

    for f in sys.argv[2:]:
        ## Read the predictions
        predictions = tools.read_csv_and_metadata(f)

        # Complain and exit if predict field is messed up in input file
        if len(predictions.meta_header['predict']) > 1:
            print("Error: more then one prediction variables found in predict meta header. Exiting.")
            exit(0)

        # Complain and exit if predict_model field does notexist or is empty
        if len(predictions.meta_header['predict_model'])  != 1:
            print("Error: predict_model field in meta header of file has bad value. Exiting.")
            exit(0)

        predict_model = predictions.meta_header['predict_model'][0]
        selection_method = predictions.meta_header['method'][0]

        ## Get the target variable from metadata
        target = predictions.meta_header['predict'][0]

        ## number of prediction or points from which 5 predictions are made with the vecm.
        nbre_preds = len(predictions.index)

        if nbre_preds in folded_orginal_data_dict[target]:
            real_data = folded_orginal_data_dict[nbre_preds]
        else:
            folded_orginal_data_dict[nbre_preds] = transform_real_values(original_data, nbre_preds, target)
            real_data = folded_orginal_data_dict[nbre_preds]

        if len(folded_orginal_data_dict[target]) > 1:
            print("Error: more then different number of predictions detected in files. Exiting.")
            exit(0)

        ret = evaluate_prediction(real_data, predictions)

        for k,v in ret.items():
            results_collection[target][k][selection_method] = ret[k]

    preaty_print(results_collection)
