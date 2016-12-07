#!/usr/bin/python

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error, r2_score
import pandas as pd
import numpy as np
import sys
import tools.csv_helper as tools
import collections
import glob
import itertools
from jinja2 import Environment, PackageLoader, FileSystemLoader

env = Environment(loader=FileSystemLoader('src'))
template = env.get_template('evaluation.html')

# All used measures
global_measures = {
        'mse': mean_squared_error,
        'mae': mean_absolute_error,
        # 'evc': explained_variance_score,
        # 'r2': r2_score,
        'medae': median_absolute_error,
        # 'R': lambda x,y: 1, # placeholder
        }

def preaty_print(results_collection, methods_to_hotizon_dict):
    colors = itertools.cycle(["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"])
    measures = global_measures.keys()
    cmap = dict(zip(measures, colors))

    tables = collections.defaultdict(lambda : collections.defaultdict(dict))
    for predict_model in results_collection:
        for target in results_collection[predict_model]:
            for h in range(methods_to_hotizon_dict[predict_model]): # diffrent timehorizons
                df = pd.DataFrame.from_dict(results_collection[predict_model][target][h]).transpose()

                # r = df['mse'] * df['medae']
                # df['R']=r

                s = df.style
                # s.set_table_attributes('class="table table-striped table-sm')
                # s.set_properties(**{'font-size':'10pt'})
                for m in measures:
                   s.bar(subset=[m,], color=cmap[m])
                # tables[predict_model][target][h]=s.render()
                tables[target][h][predict_model]=s.render()
    return tables

# max_horizon is hardcoded into the prediction scripts
def get_slice_with_horizon(df, nbre_preds, target, horizon, max_horizon=5):
    return df[[target]].tail(nbre_preds + max_horizon - 1 - horizon).head(nbre_preds).values

def evaluate_prediction(original_data, target, predictions, horizon):
    """Evaluate prediction results

    :real_values: a transformed data frame with real values
    :predicted_file): a data frame with predicted values
    :returns: evaluation measurments

    """

    results = collections.defaultdict(dict)
    l = len(predictions)
    for m in global_measures:
        for i in range(horizon):
            results[i][m] = global_measures[m](get_slice_with_horizon(original_data, l, target, i) ,predictions.values[:,i])

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

    if len(sys.argv) != 3:
        print("Error: wrong arguments. Use %s org_data_file globing_expression" %(sys.argv[0]))
        exit(0)

    ## Read first prediction file to guess the number of predicted values
    try:
        original_data = tools.read_csv_and_metadata(sys.argv[1])
    except Exception as e:
        print ("Error: Could not read the file %s, exiting." %(sys.argv[1]))
        exit(0)

    prediction_method_horizon = {}

    results_collection = collections.defaultdict(lambda : collections.defaultdict(lambda : collections.defaultdict(dict)))
    error_list = []

    for f in glob.glob(sys.argv[2]):
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

        # Prediction model used
        predict_model = predictions.meta_header['predict_model'][0]
        # Selection method used
        selection_method = predictions.meta_header['method'][0]
        ## The target variable from metadata
        target = predictions.meta_header['predict'][0]

        # The size of predicted horizon
        horizon = len(predictions.columns)
        # For each prediction method only one prediction horizon is available
        if predict_model in prediction_method_horizon and prediction_method_horizon[predict_model] != horizon:
            error_list.append("Error: more then one horizon detected for method %s skipping file %s"  %(predict_model,f))
            continue
        else:
            prediction_method_horizon[predict_model] = horizon

        ## The number of predicted vectors (vector may be one dimensional or may include some additional time horizon prediction)
        nbre_preds = len(predictions.index)

        ret = evaluate_prediction(original_data, target, predictions, horizon)

        short_selection_method = tools.get_filename_from_method("", "", selection_method, "", "")
        for k,v in ret.items():
            results_collection[predict_model][target][k][short_selection_method] = ret[k]

    tables = preaty_print(results_collection, prediction_method_horizon)
    script = template.render(tables=tables, error_list=error_list)

    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    with open("results/evaluation/%s.html"%(timeseries_prefix,),"w") as f:
        f.write(script)
