#!/usr/bin/python

import sys
import glob
from functools import partial
from collections import defaultdict, OrderedDict
import itertools
import re
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score, median_absolute_error, r2_score
import pandas as pd
import numpy as np
import tools.csv_helper as tools
from jinja2 import Environment, FileSystemLoader

# All used measures
GLOBAL_MEASURES = {
    'mse': mean_squared_error,
    'mae': mean_absolute_error,
    # 'evc': explained_variance_score,
    # 'r2': r2_score,
    'medae': median_absolute_error,
    # 'R': lambda x,y: 1, # placeholder
    # place holder the MASE, requires extra data and will be set up later in
    # the evaluation
    'MASE': lambda x, y: 0,
}

def transform_into_output_tables(results_collection, methods_to_hotizon_dict):

    # Add univariate model to other prediction models
    u_model = None
    if "Univariate_model" in results_collection:
        u_model = results_collection['Univariate_model']

    tables = defaultdict(lambda: defaultdict(dict))

    for predict_model in results_collection:

        if predict_model == "Univariate_model":
            continue

        for target in results_collection[predict_model]:
            # diffrent timehorizons
            for horizon in range(methods_to_hotizon_dict[predict_model]):
                x = [
                    OrderedDict(
                        {'predict': predict_model, 'group': group,
                            'method': mtype}.items()
                        + measures.items())
                    for group in results_collection[predict_model][target][horizon]
                    for mtype, measures in results_collection[predict_model][target][horizon][group].items()
                ]
                if u_model is not None:
                    x.append(OrderedDict(
                        {'predict': 'Univariate_model',
                            'group': 'Univariate_model', 'method': 0}.items()
                        + u_model[target][horizon]['Univariate_model'][0].items()
                    ))

                df = pd.DataFrame.from_dict(x)
                df.set_index(["predict", "group", "method"])
                tables[target][horizon][predict_model] = df

    return tables


def get_slice_with_horizon(df, nbre_preds, target, horizon, max_horizon=5):
    # max_horizon is hardcoded into the prediction scripts
    return df[[target]].tail(nbre_preds + max_horizon - 1 - horizon).head(nbre_preds).values


def MASE(training_series, testing_series, prediction_series):
    # TODO: be carefull with the training and testing dataset as, paper is not
    # clear about that
    training_len = len(training_series)
    differences = np.abs(np.diff(training_series.T)).sum() / (training_len - 1)
    errors = np.abs(testing_series - prediction_series)
    return errors.mean() / differences


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
            data_slice = get_slice_with_horizon(
                original_data, len(predictions), target, horizon)
            results[horizon][mkey] = measure(
                data_slice, predictions.values[:, horizon])

    return results


def check_fields_in_metaheader(predictions, dict_to_check, fields, fname, error_list):
    if len(predictions.columns) == 0:
        error_list.append("Error: File %s, has no columns." % (fname))
        return False

    for field in fields:
        if field not in predictions.meta_header:
            error_list.append(
                "Error: File %s, field %s\n not found in meta header." % (fname, field))
            return False
        if len(predictions.meta_header[field]) != 1:
            error_list.append(
                "Error: File %s, field %s\n has more then one value in meta_header." % (fname, field))
            return False
        if len(predictions.meta_header[field][0].strip()) == 0:
            error_list.append(
                "Error: File %s, field %s\n value is empty in meta_header." % (fname, field))
            return False
    return True


def read_and_evaluate_results():
    if len(sys.argv) != 3:
        print("Error: wrong arguments. Use %s org_data_file globing_expression" % (
            sys.argv[0]))
        exit(0)

    # Read the orginal data file
    try:
        original_data = tools.read_csv_and_metadata(sys.argv[1])
    except:
        print("Error: Could not read the file %s, exiting." % (sys.argv[1]))
        exit(0)

    prediction_method_horizon = {}
    results_collection = defaultdict(lambda: defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))))
    error_list = []

    n_components_match = re.compile("n_components\s*=\s*([0-9]+)\s*[,)]")

    for fname in glob.glob(sys.argv[2]):
        # Read the predictions
        try:
            predictions = tools.read_csv_and_metadata(fname)
        except Exception as e:
            # print(e)
            error_list.append(
                "Error: Could not read file %s, moving to next file" % (fname))
            continue

        meta_header = predictions.meta_header
        # Complain and continue if fields are messed up in input file
        # meta_header
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
            error_list.append("Error: more then one horizon detected for method %s skipping file %s" % (
                predict_model, fname))
            continue

        # If the prediction horizon match the previously set one or when this
        # the first time we see horizon
        prediction_method_horizon[predict_model] = horizon

        # The number of predicted vectors (vector may be one dimensional or may include some additional time horizon prediction)
        # nbre_preds = len(predictions.index)

        try:
            ret = evaluate_prediction(
                original_data, target, predictions, horizon)
        except Exception as e:
            print(e)
            error_list.append(
                "Error: Evaluation of predictions failed, skipping file %s" % (fname))
            continue

        # This will fail if name does not match, but then the
        # prediction/selection methods must be fixed
        try:
            selection_method_group_name, id_name = \
                predictions.meta_header['method'][0].split('(')[:2]
        except Exception as exception:
            print("Error: could parse the selection method name,\
                    please use 'method_group_name(other_params, n_components=k, other_params)'.\
                    If no n_components param is found group is treated as one element group.")
        r_match = n_components_match.search(id_name)

        id_name = 0
        if r_match is not None:
            id_name = int(r_match.group(1))

        for k, evaluation_result in ret.items():
            results_collection[predict_model][target][k][
                selection_method_group_name][id_name] = evaluation_result

    return results_collection, prediction_method_horizon, error_list


class transform_into_excel(object):

    def __init__(self, tables, error_list):
        super(transform_into_excel, self).__init__()
        self.tables = tables
        self.error_list = error_list

    def write(self, timeseries_prefix):
        # Write excel
        # TODO: write error list to separate spreadsheet
        writer = pd.ExcelWriter(
            "results/evaluation/%s.xls" % (timeseries_prefix,))
        for target_name in self.tables:
            for horizon in self.tables[target_name]:
                for predict_model, val in self.tables[target_name][horizon].items():
                    val.to_excel(writer, sheet_name="%s_%s_%s" %
                                 (target_name, horizon, predict_model))
        writer.close()


class transform_into_figure(object):
    """Generates figures with diffrent mesures grouped by method type"""

    def __init__(self, tables, error_list):
        super(transform_into_figure, self).__init__()
        self.tables = tables
        self.error_list = error_list

        self.default_plot_styles = {
            "LinkAnalysis_te_graph.*": {'ls': '-', 'marker': '*'},
            "LinkAnalysis_granger_graph.*": {'ls': '-', 'marker': '*'},
            "Granger_.*": {'ls': '-', 'marker': 'o'},
            "dm_.*": {'ls': '-', 'marker': 'd'},
            "UFSM": {'ls': '-', 'marker': 'D'},
            "default": {'ls': '-'},
        }
        # colors = sns.color_palette("cubehelix", len(self.default_plot_styles.keys()))self.timeseries_prefix = t
        # for i, style in enumerate(self.default_plot_styles):
        #     self.default_plot_styles[style]['color'] = colors[i]

        self.measures = GLOBAL_MEASURES.keys()

    def _get_plot_style(self, name):
        for pstyle in self.default_plot_styles:
            if re.match(pstyle, name):
                return self.default_plot_styles[pstyle]
        return self.default_plot_styles['default']

    def _plot_group_measure(self, ax, data_sorted, group, measure):
        plot_style = self._get_plot_style(group[0])

        if len(data_sorted) > 1:
            ax.plot(data_sorted[['method']], data_sorted[
                    [measure]], label=group[0], **plot_style)
        else:
            ax.axhline(y=data_sorted[[measure]].values[0][
                       0], label=group[0], **plot_style)

        ax.set_yscale('log')

    def _plot_to_file(self, target, horizon, predict_model):
        data_slice = self.tables[target][horizon][predict_model]
        data_slice = data_slice.sort_values('method')

        # Set up plot grid
        cols = 2
        # Callculate number of rows (ceiling(rows/cols)) + 1 row for legend
        rows = (len(self.measures) + cols - 1) / cols  # + 1

        f = plt.figure(figsize=(16.5, 11.7), dpi=100)
        measure_to_grid = {}
        for i, measure in enumerate(self.measures):
            splot = plt.subplot2grid((rows, cols), (i / cols, i % cols))
            splot.set_title(measure)
            measure_to_grid[measure] = splot

        for group, data in data_slice.groupby(['group', 'predict']):
            for measure in self.measures:
                self._plot_group_measure(
                    measure_to_grid[measure], data, group, measure)

        # plot legend in separare plot
        ax_legend = measure_to_grid[self.measures[0]]
        plt.figlegend(*ax_legend.get_legend_handles_labels(),
                      loc='lower center', ncol=7, fontsize='xx-small',
                      bbox_to_anchor=(0.5, 0), bbox_transform=plt.gcf().transFigure)
        plt.tight_layout()

        plt.savefig("results/evaluation/%s_%s_%s_%s.png" %
                    (self.timeseries_prefix, target, str(horizon), predict_model))
        plt.clf()
        plt.cla()
        plt.close()

    def write(self, timeseries_prefix):
        self.timeseries_prefix = timeseries_prefix
        for target in self.tables:
            for horizon in self.tables[target]:
                for predict_model in self.tables[target][horizon]:
                    self._plot_to_file(target, horizon, predict_model)

class transform_into_html(object):

    """Generate HTML from tables"""

    def __init__(self, tables, error_list):
        self.colors = itertools.cycle(
            ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"])
        self.measures = GLOBAL_MEASURES.keys()
        self.cmap = dict(zip(self.measures, self.colors))
        # highlight the maximum in a Series yellow.
        self.underline_top_10 = lambda style:\
            ['text-decoration: underline;'
             if table_row < 10 else '' for table_row in style.rank(method='max')]

        self.tables = tables
        self.error_list = error_list
        self.tables_html = defaultdict(lambda: defaultdict(dict))

    def _to_html(self, df):

        style = df.style
        # style.set_table_attributes('class="table table-striped table-sm')
        # style.set_properties(**{'font-size':'10pt'})
        for measure in self.measures:
            style.bar(subset=[measure, ], color=self.cmap[measure])
            style.apply(self.underline_top_10, subset=[measure, ])

        return style.render()

    def transform(self):
        for target in self.tables:
            for horizon in self.tables[target]:
                for predict_model in self.tables[target][horizon]:
                    self.tables_html[target][horizon][predict_model] = self._to_html(
                        self.tables[target][horizon][predict_model])

    def write(self, timeseries_prefix):
        self.transform()
        # Write HTML
        env = Environment(loader=FileSystemLoader('src'))
        template = env.get_template('evaluation.html')
        script = template.render(
            tables=self.tables_html, error_list=self.error_list)
        with open("results/evaluation/%s.html" % (timeseries_prefix), "w") as f:
            f.write(script)


def main():
    results_collection, prediction_method_horizon, error_list = read_and_evaluate_results()

    # Get the output touple
    tables_real = transform_into_output_tables(
        results_collection, prediction_method_horizon)

    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    transform_into_excel(tables_real, error_list).write(timeseries_prefix)
    transform_into_figure(tables_real, error_list).write(timeseries_prefix)
    transform_into_html(tables_real, error_list).write(timeseries_prefix)

if __name__ == "__main__":
    main()
