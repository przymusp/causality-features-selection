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
        'MASE': lambda x,y: 0 # place holder the MASE, requires extra data and will be set up later in the evaluation
        }

def transform_into_html_setup():
        colors = itertools.cycle(["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"])
        measures = global_measures.keys()
        cmap = dict(zip(measures, colors))

        def underline_top_10(s):
            '''
            highlight the maximum in a Series yellow.
            '''
            return ['text-decoration: underline;' if v < 10 else '' for v in s.rank(method='max')]

        def transform_into_html_inner(df):
            s = df.style
            # s.set_table_attributes('class="table table-striped table-sm')
            # s.set_properties(**{'font-size':'10pt'})
            for m in measures:
               s.bar(subset=[m,], color=cmap[m])
               s.apply(underline_top_10)

            return s.render()
        return transform_into_html_inner

# TODO: Just a dirty metaprograming hack, rewrite later for readability
transform_into_html = transform_into_html_setup()

def transform_into_output_tables(results_collection, methods_to_hotizon_dict):

    tables = collections.defaultdict(lambda : collections.defaultdict(dict))
    tables_str = collections.defaultdict(dict)
    tables_real = collections.defaultdict(dict)

    for predict_model in results_collection:
        for target in results_collection[predict_model]:
            for h in range(methods_to_hotizon_dict[predict_model]): # diffrent timehorizons
                df = pd.DataFrame.from_dict(results_collection[predict_model][target][h]).transpose()
                df.index = predict_model + df.index
                tables[target][h][predict_model]=df

        for target in results_collection[predict_model]:
            for h in range(methods_to_hotizon_dict[predict_model]): # diffrent timehorizons
                df = pd.concat(tables[target][h].values())
                df.index.name = 'Method'

                tables_str[target][h] = transform_into_html(df)
                tables_real[target][h] = df

    return tables_str, tables_real

def get_slice_with_horizon(df, nbre_preds, target, horizon, max_horizon=5):
    # max_horizon is hardcoded into the prediction scripts
    return df[[target]].tail(nbre_preds + max_horizon - 1 - horizon).head(nbre_preds).values

def MASE(training_series, testing_series, prediction_series):
    # TODO: be carefull with the training and testing dataset as, paper is not clear about that
    n = len(training_series)
    d = np.abs(  np.diff( training_series.T) ).sum() / (n-1)
    errors = np.abs(testing_series - prediction_series )
    return errors.mean()/d

def evaluate_prediction(original_data, target, predictions, horizon):
    """Evaluate prediction results

    :real_values: a transformed data frame with real values
    :predicted_file): a data frame with predicted values
    :returns: evaluation measurments

    """

    results = collections.defaultdict(dict)
    l = len(predictions)
    l_all = len(original_data)


    global_measures['MASE'] = lambda x,y: MASE(original_data[[target]].head(l_all - l - horizon).values,x,y)

    for m in global_measures:
        for i in range(horizon):
            results[i][m] = global_measures[m](get_slice_with_horizon(original_data, l, target, i) ,predictions.values[:,i])

    return results

def check_fields_in_metaheader(dict_to_check, fields, fname, error_list):
    for field in fields:
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
        if not check_fields_in_metaheader(meta_header, ['predict', 'predict_model', 'method'], f, error_list):
            continue

        # Prediction model used
        predict_model = predictions.meta_header['predict_model'][0]
        # Selection method used
        selection_method = predictions.meta_header['method'][0]
        # The target variable from metadata
        target = predictions.meta_header['predict'][0]
        # The size of predicted horizon
        horizon = len(predictions.columns)

        # For each prediction method only one prediction horizon is available
        if predict_model in prediction_method_horizon and prediction_method_horizon[predict_model] != horizon:
            error_list.append("Error: more then one horizon detected for method %s skipping file %s"  %(predict_model,f))
            continue
        else:
            # If the prediction horizon match the previously set one or when this the first time we see horizon
            prediction_method_horizon[predict_model] = horizon

        ## The number of predicted vectors (vector may be one dimensional or may include some additional time horizon prediction)
        nbre_preds = len(predictions.index)

        ret = evaluate_prediction(original_data, target, predictions, horizon)

        short_selection_method = tools.get_filename_from_method("", "", selection_method, "", "")
        print (selection_method)
        for k,v in ret.items():
            results_collection[predict_model][target][k][short_selection_method] = v


    # Get the output touple
    tables_str, tables_real = transform_into_output_tables(results_collection, prediction_method_horizon)

    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    # Write excel
    writer = pd.ExcelWriter("results/evaluation/%s.xls"%(timeseries_prefix,))
    for target_name, target_val in tables_real.items():
        for horizon_name, horizon_val in tables_real[target_name].items():
            horizon_val.to_excel(writer, sheet_name="%s_%s"%(target_name, horizon_name))
    writer.close()

    # Write HTML
    script = template.render(tables=tables_str, error_list=error_list)
    with open("results/evaluation/%s.html"%(timeseries_prefix,),"w") as f:
        f.write(script)
