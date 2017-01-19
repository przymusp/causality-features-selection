#!/usr/bin/python

import sys
import glob
from functools import partial

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error, r2_score
import pandas as pd
import numpy as np
import tools.csv_helper as tools
from collections import defaultdict
import itertools
from jinja2 import Environment, PackageLoader, FileSystemLoader

# All used measures
GLOBAL_MEASURES = {
    'mse': mean_squared_error,
    'mae': mean_absolute_error,
    # 'evc': explained_variance_score,
    # 'r2': r2_score,
    'medae': median_absolute_error,
    # 'R': lambda x,y: 1, # placeholder
    # place holder the MASE, requires extra data and will be set up later in the evaluation
    'MASE': lambda x, y: 0,
}

class transform_into_html(object):

    """Generate HTML from tables"""

    def __init__(self, tables, error_list):
        self.colors = itertools.cycle(["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"])
        self.measures = GLOBAL_MEASURES.keys()
        self.cmap = dict(zip(self.measures, self.colors))
        # highlight the maximum in a Series yellow.
        self.underline_top_10 = lambda style: ['text-decoration: underline;' if table_row < 10 else '' for table_row in style.rank(method='max')]

        self.tables = tables
        self.error_list = error_list
        self.tables_html = defaultdict(dict)

    def _transform_into_html(self, df):
        style = df.style
        # style.set_table_attributes('class="table table-striped table-sm')
        # style.set_properties(**{'font-size':'10pt'})
        for measure in self.measures:
            style.bar(subset=[measure,], color=self.cmap[measure])
            style.apply(self.underline_top_10)

        return style.render()

    def transform(self):
        for target in self.tables:
            for horizon in self.tables[target]:
                self.tables_html[target][horizon] = self._transform_into_html(self.tables[target][horizon])

    def write(self, timeseries_prefix):
        self.transform()
        # Write HTML
        env = Environment(loader=FileSystemLoader('src'))
        template = env.get_template('evaluation.html')
        script = template.render(tables=self.tables_html, error_list=self.error_list)
        with open("results/evaluation/%s.html"%(timeseries_prefix), "w") as f:
            f.write(script)

def transform_into_output_tables(results_collection, methods_to_hotizon_dict):

    tables = defaultdict(lambda: defaultdict(dict))
    tables_real = defaultdict(dict)

    for predict_model in results_collection:
        for target in results_collection[predict_model]:
            for h in range(methods_to_hotizon_dict[predict_model]): # diffrent timehorizons
                df = pd.DataFrame.from_dict(results_collection[predict_model][target][h]).T
                df.index = predict_model + df.index
                tables[target][h][predict_model] = df

        for target in results_collection[predict_model]:
            for h in range(methods_to_hotizon_dict[predict_model]): # diffrent timehorizons
                df = pd.concat(tables[target][h].values())
                df.index.name = 'Method'

                tables_real[target][h] = df

    return tables_real

def get_slice_with_horizon(df, nbre_preds, target, horizon, max_horizon=5):
    # max_horizon is hardcoded into the prediction scripts
    return df[[target]].tail(nbre_preds + max_horizon - 1 - horizon).head(nbre_preds).values

def MASE(training_series, testing_series, prediction_series):
    # TODO: be carefull with the training and testing dataset as, paper is not clear about that
    n = len(training_series)
    d = np.abs(np.diff(training_series.T)).sum() / (n-1)
    errors = np.abs(testing_series - prediction_series)
    return errors.mean()/d

def evaluate_prediction(original_data, target, predictions, horizon_range):
    """Evaluate prediction results

    :real_values: a transformed data frame with real values
    :predicted_file): a data frame with predicted values
    :returns: evaluation measurments

    """

    results = defaultdict(dict)
    testing_data_index = len(original_data) - len(predictions) - horizon_range
    testing_data = original_data[[target]].head(testing_data_index).values
    GLOBAL_MEASURES['MASE'] = partial(MASE, testing_data)

    for mkey, measure in GLOBAL_MEASURES.items():
        for horizon in range(horizon_range):
            data_slice = get_slice_with_horizon(original_data, len(predictions), target, horizon)
            results[horizon][mkey] = measure(data_slice, predictions.values[:, horizon])

    return results

def check_fields_in_metaheader(predictions, dict_to_check, fields, fname, error_list):
    if len(predictions.columns) == 0:
        error_list.append("Error: File %s, has no columns." %(fname))
        return False

    for field in fields:
        if field not in predictions.meta_header:
            error_list.append("Error: File %s, field %s\n not found in meta header." %(fname, field))
            return False
        if len(predictions.meta_header[field]) != 1:
            error_list.append("Error: File %s, field %s\n has more then one value in meta_header." %(fname, field))
            return False
        if len(predictions.meta_header[field][0].strip()) == 0:
            error_list.append("Error: File %s, field %s\n value is empty in meta_header." %(fname, field))
            return False
    return True

def read_and_evaluate_results():
    if len(sys.argv) != 3:
        print("Error: wrong arguments. Use %s org_data_file globing_expression" %(sys.argv[0]))
        exit(0)

    ## Read the orginal data file
    try:
        original_data = tools.read_csv_and_metadata(sys.argv[1])
    except:
        print ("Error: Could not read the file %s, exiting." %(sys.argv[1]))
        exit(0)

    prediction_method_horizon = {}
    results_collection = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    error_list = []

    for fname in glob.glob(sys.argv[2]):
        ## Read the predictions
        try:
            predictions = tools.read_csv_and_metadata(fname)
        except Exception as e:
            # print(e)
            error_list.append("Error: Could not read file %s, moving to next file" %(fname))
            continue

        meta_header = predictions.meta_header
        # Complain and continue if fields are messed up in input file meta_header
        fields = ['predict', 'predict_model', 'method']
        if not check_fields_in_metaheader(predictions, meta_header, fields, fname, error_list):
            continue

        # Extract fields from meta_header and data
        predict_model = predictions.meta_header['predict_model'][0]
        selection_method = predictions.meta_header['method'][0]
        target = predictions.meta_header['predict'][0]
        horizon = len(predictions.columns)

        # For each prediction method only one prediction horizon is available
        if predict_model in prediction_method_horizon \
                and prediction_method_horizon[predict_model] != horizon:
            error_list.append("Error: more then one horizon detected for method %s skipping file %s"%(predict_model, fname))
            continue

        # If the prediction horizon match the previously set one or when this the first time we see horizon
        prediction_method_horizon[predict_model] = horizon

        # The number of predicted vectors (vector may be one dimensional or may include some additional time horizon prediction)
        # nbre_preds = len(predictions.index)

        try:
            ret = evaluate_prediction(original_data, target, predictions, horizon)
        except Exception as e:
            print (e)
            error_list.append("Error: Evaluation of predictions failed, skipping file %s"%(fname))
            continue

        short_selection_method = tools.get_filename_from_method("", "", selection_method, "", "")
        # print (selection_method)
        for k, evaluation_result in ret.items():
            results_collection[predict_model][target][k][short_selection_method] = evaluation_result

    return results_collection, prediction_method_horizon, error_list

def write_results_to_excel(timeseries_prefix, tables, error_list):
    # Write excel
    # TODO: write error list to separate spreadsheet
    writer = pd.ExcelWriter("results/evaluation/%s.xls"%(timeseries_prefix,))
    for target_name in tables:
        for horizon_name, horizon_val in tables[target_name].items():
            horizon_val.to_excel(writer, sheet_name="%s_%s"%(target_name, horizon_name))
    writer.close()


def main():
    results_collection, prediction_method_horizon, error_list = read_and_evaluate_results()

    # Get the output touple
    tables_real = transform_into_output_tables(results_collection, prediction_method_horizon)

    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    write_results_to_excel(timeseries_prefix, tables_real, error_list)
    transform_into_html(tables_real, error_list).write(timeseries_prefix)

if __name__ == "__main__":
    main()

