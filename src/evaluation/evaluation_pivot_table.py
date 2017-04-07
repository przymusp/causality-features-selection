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

    def get_min_of_of_group(self, target, horizon, predict_model):
        """ Generate a pivot table of results

        :target: target variable
        :horizon: the future horizon used
        :predict_model: the prediction model used
        :returns: a pivot table with all the methods compared to each other

        """
        data_slice = self.tables[target][horizon][predict_model]
        data_slice = data_slice.sort_values('method')

        data_slice_group = data_slice.groupby(['group', 'predict'], as_index=False)

        min_mase_group = data_slice_group['group','predict', 'MASE'].min()
        min_mase_group['horizon'] = horizon
        min_mase_group['target'] = target

        # TODO: fix that
        # groups_to_remove = [ 'jdit', '_graph_reverse', 'reverse_0', 'lstoch', 'rstoch']
        groups_to_remove = ['_graph_reverse']
        for grm in groups_to_remove:
            min_mase_group = min_mase_group[~min_mase_group.group.str.contains(grm)]

        groups_to_select = [] #[ 'Link' ]
        for grm in groups_to_select:
            min_mase_group = min_mase_group[min_mase_group.group.str.contains(grm)]

        return min_mase_group


    def get_rank_mase_matrix(self, min_mase_group):
        rank_mase = min_mase_group.copy()
        rank_mase['rank'] = min_mase_group['MASE'].rank(method="min")
        return rank_mase

    def get_comparison_mase_matrix(self, min_mase_group):
        cmp_cols = []
        cmp_cols.append(min_mase_group['group'])
        for row in min_mase_group.itertuples():
                cmp_cols.append((min_mase_group['MASE'] > row.MASE).astype(int))
                cmp_cols[-1].rename(row.group, inplace=True)

        return pd.concat(cmp_cols, axis=1).set_index(['group'])

    def plot_comparison_summary(self, cmp_summary, out_fname):
        plt.gcf().subplots_adjust(left=0.30, bottom=0.30)
        self.__plot_heatmap(cmp_summary, out_fname)

    def plot_rank_summary(self, rank_summary, out_fname):
        heat_map = pd.DataFrame.from_dict(rank_summary).fillna(0).T

        # TODO: to check
        heat_map = heat_map.sort_values(range(1,len(heat_map)), ascending=False)

        plt.gcf().subplots_adjust(left=0.30)
        self.__plot_heatmap(heat_map, out_fname)

    def __plot_heatmap(self, heat_map, out_fname):
        sns.set()
        sns.heatmap(heat_map, annot=True, linewidths=.5, cmap="YlGnBu", robust=True, annot_kws={'size':5})
        plt.setp( plt.gca().yaxis.get_majorticklabels(), rotation='horizontal' )
        plt.tick_params(axis='y', which='major', labelsize=5)
        plt.tick_params(axis='y', which='minor', labelsize=5)
        plt.tick_params(axis='x', which='major', labelsize=5)
        plt.tick_params(axis='x', which='minor', labelsize=5)
        plt.savefig(out_fname)
        plt.clf()

    def write(self, timeseries_prefix):
        self.timeseries_prefix = timeseries_prefix
        factory = lambda: defaultdict(factory)
        # summary = factory()

        rank_summary = defaultdict(Counter)
        cmp_summary = None

        for target in self.tables:
            for horizon in self.tables[target]:
                for predict_model in self.tables[target][horizon]:
                    if horizon != 0 or predict_model == 'VECM-rolling': continue

                    min_mase_matrix = self.get_min_of_of_group(target, horizon, predict_model)

                    rank_matrix = self.get_rank_mase_matrix(min_mase_matrix)
                    for row in rank_matrix.itertuples():
                        rank_summary[row.group][int(row.rank)] += 1

                    temp_cmp_summary = self.get_comparison_mase_matrix(min_mase_matrix)
                    if cmp_summary is None:
                        cmp_summary = temp_cmp_summary
                    else:
                        cmp_summary += temp_cmp_summary
        plot_fname_prefix = "%s/%s" %(self.out_dir, timeseries_prefix)
        self.plot_rank_summary(rank_summary, plot_fname_prefix + "_rank.pdf")
        self.plot_comparison_summary(cmp_summary, plot_fname_prefix + "_cmp.pdf")

def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    transform_into_pivot_tables(out_dir, tables_real, error_list).write(timeseries_prefix)


if __name__ == "__main__":
    main()
