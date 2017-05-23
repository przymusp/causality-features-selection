import sys
import pickle
from collections import defaultdict, Counter
import numpy as np
from tabulate import tabulate

import pandas as pd
from tools.global_measures import GLOBAL_MEASURES

import seaborn as sns
import matplotlib.pyplot as plt

class transform_into_pivot_tables(object):
    """Generates pivot tables with diffrent mesures grouped by method type"""

    def __init__(self, out_dir, tables, error_list):
        super(transform_into_pivot_tables, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.measures = GLOBAL_MEASURES.keys()
        self.out_dir = out_dir

    def get_min_of_of_group(self, target, horizon, predict_model, measure):
        """ Generate a pivot table of results

        :target: target variable
        :horizon: the future horizon used
        :predict_model: the prediction model used
        :returns: a pivot table with all the methods compared to each other

        """
        data_slice = self.tables[target][horizon][predict_model]
        data_slice = data_slice.sort_values('method')

        # TODO: fix that
        # groups_to_remove = [ 'jdit', '_graph_reverse', 'reverse_0', 'lstoch', 'rstoch']
        # groups_to_remove = ['_graph_reverse', '_dstoch']
        groups_to_remove = ['UFSM', '_lstoch', '_rstoch', '_dstoch', 'jdit',]# '_granger__graph_reverse', 'te_graph']
        for grm in groups_to_remove:
            data_slice = data_slice[~data_slice.group.str.contains(grm)]

        groups_to_select = [] #[ 'Link' ]
        for grm in groups_to_select:
            data_slice = data_slice[data_slice.group.str.contains(grm)]

        data_slice_group = data_slice.groupby(['group', 'predict'], as_index=False)

        min_mase_group = data_slice_group['group','predict', measure].min()
        min_mase_group['horizon'] = horizon
        min_mase_group['target'] = target

        return min_mase_group


    def get_rank_mase_matrix(self, min_mase_group, measure):
        rank_mase = min_mase_group.copy()
        rank_mase['rank'] = min_mase_group[measure].rank(method="min")
        return rank_mase

    def get_comparison_mase_matrix(self, min_mase_group, measure):
        cmp_cols = []
        cmp_cols.append(min_mase_group['group'])
        for index, row in min_mase_group.iterrows():
                cmp_cols.append((min_mase_group[measure] > row[measure]).astype(int))
                cmp_cols[-1].rename(row.group, inplace=True)

        return pd.concat(cmp_cols, axis=1).set_index(['group'])

    def plot_comparison_summary(self, cmp_summary, out_fname):
        plt.gcf().subplots_adjust(left=0.30, bottom=0.30)
        self.__plot_heatmap(cmp_summary, out_fname)

    def plot_rank_summary(self, rank_summary, out_fname):
        heat_map = pd.DataFrame.from_dict(rank_summary).fillna(0).T

        # print heat_map
        # TODO: to check
        # heat_map = heat_map.sort_values(range(1,len(heat_map)), ascending=False)

        plt.gcf().subplots_adjust(left=0.30)
        self.__plot_heatmap(heat_map, out_fname)

    def __plot_heatmap(self, heat_map, out_fname):
        sns.set()
        sns.heatmap(heat_map, annot=True, linewidths=.5, cmap="YlGnBu", robust=True, annot_kws={'size':5})
        plt.setp( plt.gca().yaxis.get_majorticklabels(), rotation='horizontal' )
        plt.setp( plt.gca().xaxis.get_majorticklabels(), rotation='vertical' )
        plt.tick_params(axis='y', which='major', labelsize=5)
        plt.tick_params(axis='y', which='minor', labelsize=5)
        plt.tick_params(axis='x', which='major', labelsize=5)
        plt.tick_params(axis='x', which='minor', labelsize=5)
        plt.savefig(out_fname)
        plt.clf()

    def write(self, timeseries_prefix, measure, select_horizon, exclude_predict_models=[]):
        self.timeseries_prefix = timeseries_prefix
        factory = lambda: defaultdict(factory)
        # summary = factory()

        rank_summary = defaultdict(Counter)
        sum_measure = defaultdict(float)
        sum_imp_measure = defaultdict(float)
        count_measure = defaultdict(int)
        count_imp_measure = defaultdict(int)
        cmp_summary = None
        avg_measure_matrix = None

        c = 0
        for target in self.tables:
            for horizon in self.tables[target]:
                for predict_model in self.tables[target][horizon]:
                    if horizon != select_horizon or predict_model in exclude_predict_models:
                        continue

                    min_mase_matrix = self.get_min_of_of_group(target, horizon, predict_model, measure)

                    # for index, row in min_mase_matrix.iterrows():
                    #     sum_measure[row['group']] += row[measure]
                    #     count_measure[row['group']] += 1.0
                    #     count_imp_measure[row['group']] += 1 if row[measure] < 1 else 0
                    #     sum_imp_measure[row['group']] += row[measure] if row[measure] < 1 else 0

                    # print min_mase_matrix, target

                    # rank_matrix = self.get_rank_mase_matrix(min_mase_matrix, measure)
                    # for row in rank_matrix.itertuples():
                    #     rank_summary[row.group][int(row.rank)] += 1

                    temp_cmp_summary = self.get_comparison_mase_matrix(min_mase_matrix, measure)
                    if cmp_summary is None:
                        cmp_summary = temp_cmp_summary
                    else:
                        cmp_summary += temp_cmp_summary

        plot_fname_prefix = "%s/%s" %(self.out_dir, timeseries_prefix)
        # self.plot_rank_summary(rank_summary, plot_fname_prefix + "_rank_%s.pdf"%(measure))
        # avg = pd.DataFrame.from_dict(sum_measure, orient='index')
        # avg['avg'] = avg / pd.DataFrame.from_dict(count_measure, orient='index')
        # avg['count'] = pd.DataFrame.from_dict(count_measure, orient='index')
        # avg['count_imp'] = pd.DataFrame.from_dict(count_imp_measure, orient='index')
        # avg['avg_imp'] = pd.DataFrame.from_dict(sum_imp_measure, orient='index')
        # avg['avg_imp'] /= avg['count_imp']
        # print (avg)

        # avg_measure_matrix[measure] /= float(c)
        # print c
        # print avg_measure_matrix[measure]/c
        # self.__plot_heatmap(avg_measure_matrix, plot_fname_prefix + "_avg_%s.pdf"%(measure))
        self.plot_comparison_summary(cmp_summary, plot_fname_prefix + "_cmp_%s.pdf"%(measure))

def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    # exclude_pmodels = ['Auto_Arima Model', 'Arima', 'Univariate_model', 'VECM-rolling']
    exclude_pmodels = []
    exclude_smodels = []

    transform_into_pivot_tables(out_dir, tables_real, error_list).write(timeseries_prefix, 'MASE', 0, exclude_pmodels)


if __name__ == "__main__":
    main()
