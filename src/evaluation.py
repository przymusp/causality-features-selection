#!/usr/bin/python

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error
import pandas as pd
import numpy as np
import sys
import tools.csv_helper as tools
import collections
from jinja2 import Environment, PackageLoader, FileSystemLoader

env = Environment(loader=FileSystemLoader('src'))
template = env.get_template('evaluation.html')

# All used measures
global_measures = {
        'mse': mean_squared_error,
        'mae': mean_absolute_error,
        'evc': explained_variance_score,
        }

def preaty_print(results_collection):
    # TODO: Fix colors if more measures appear
    colors = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
    measures = global_measures.keys()
    cmap = dict(zip(measures, colors[:len(measures)]))

    tables = collections.defaultdict(dict)
    for target in results_collection:
        for h in range(5): # diffrent timehorizons
            # print ("<h3 style='text-align:center'>Target: %s Time horizon: %s</h3>" % (target, h))
            df = pd.DataFrame.from_dict(results_collection[target][h]).transpose()

            s = df.style
            # s.set_properties(**{'font-size':'10pt'})
            for m in measures:
               s.bar(subset=[m,], color=cmap[m])
            tables[target][h]=s.render()
    return tables

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

def check_field_in_header(dict_to_check, field, fname, error_list):
    if field not in predictions.meta_header:
        error_list.append("Error: File %s, field %s\n not found in meta header." %(fname, field))
        return False
    if len(predictions.meta_header[field])  != 1:
        error_list.append("Error: File %s, field %s\n has more then one value in  meta_header." %(fname, field))
        return False
    return True


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Error: at least 2 files are needed to compare")
        exit(0)

    ## Read first prediction file to guess the number of predicted values
    try:
        original_data = tools.read_csv_and_metadata(sys.argv[1])
    except Exception as e:
        print ("Error: Could not read the file %s, exiting." %(f))
        exit(0)

    # Cache for orginal data representation suitable for prediction comparison
    folded_orginal_data_dict = collections.defaultdict(dict)

    # Results
    results_collection = collections.defaultdict(lambda : collections.defaultdict(dict))

    error_list = []

    required_meta_header_fields_checkers = {}

    # print("<ul>")
    for f in sys.argv[2:]:
        # print("<li> Processing file %s" %(f,))
        ## Read the predictions
        try:
            predictions = tools.read_csv_and_metadata(f)
        except Exception as e:
            error_list.append("Error: Could not read file %s, moving to next file" %(f))
            continue

        meta_header = predictions.meta_header
        # Complain and continue if fields are messed up in input file meta_header
        if not check_field_in_header(meta_header, 'predict', f, error_list)\
                or not check_field_in_header(meta_header, 'predict_model', f, error_list)\
                or not check_field_in_header(meta_header, 'method', f, error_list):
            continue

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

        # if len(folded_orginal_data_dict[target]) > 1:
        #     # print("Error: more then different number of predictions detected in files. Moving to the next file.")
        #     continue

        ret = evaluate_prediction(real_data, predictions)

        short_selection_method = tools.get_filename_from_method("", "", selection_method, "", "")
        for k,v in ret.items():
            results_collection[target][k][short_selection_method] = ret[k]


    tables = preaty_print(results_collection)
    script = template.render(tables=tables, error_list=error_list)
    print (script.encode('utf-8'))

