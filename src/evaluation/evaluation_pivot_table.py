import sys
import pickle
from collections import defaultdict, Counter
import numpy as np
from tabulate import tabulate

import pandas as pd
from tools.global_measures import GLOBAL_MEASURES

class transform_into_pivot_tables(object):
    """Generates pivot tables with diffrent mesures grouped by method type"""

    def __init__(self, out_dir, tables, error_list):
        super(transform_into_pivot_tables, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.measures = GLOBAL_MEASURES.keys()
        self.out_dir = out_dir

    def generate_table(self, target, horizon, predict_model):
        """ Generate a pivot table of results

        :target: target variable
        :horizon: the future horizon used
        :predict_model: the prediction model used
        :returns: a pivot table with all the methods compared to each other

        """
        data_slice = self.tables[target][horizon][predict_model]
        data_slice = data_slice.sort_values('method')

        data_slice_group = data_slice.groupby(['group', 'predict'], as_index=False)

        ret_df = data_slice_group['group','predict', 'MASE'].min()
        ret_df['horizon'] = horizon
        ret_df['target'] = target
        ret_df['rank']=ret_df['MASE'].rank(method="min")
        # print ret_df.to_dict('index')
        return ret_df
        exit()
        # cmp_cols = ret_df['group']
        cmp_cols = []
        cmp_cols.append(ret_df['group'])
        for row in ret_df.itertuples():
            # if pivot is None:
            #     pivot = ret_df['MASE'] < row.MASE
            # else:
                # cmp_cols[row.group] = (ret_df['MASE'] < row.MASE).astype(int)
                cmp_cols.append((ret_df['MASE'] > row.MASE).astype(int))
                cmp_cols[-1].rename(row.group, inplace=True)
            # print row.group,
        # print cmp_cols
        return pd.concat(cmp_cols, axis=1).set_index(['group'])
        # print ret_df
        # exit()
        # # print ret_df.columns
        # # print ret_df
        # return ret_df

        # for group, data in data_slice_group:
        #     # for measure in self.measures:
        #     print data.min()

    def write(self, timeseries_prefix):
        self.timeseries_prefix = timeseries_prefix
        factory = lambda: defaultdict(factory)
        # summary = factory()

        summary = defaultdict(Counter)

        for target in self.tables:
            for horizon in self.tables[target]:
                for predict_model in self.tables[target][horizon]:
                    if horizon != 0 or predict_model == 'VECM-rolling': continue
                    ret_df = self.generate_table(target, horizon, predict_model)
                    for row in ret_df.itertuples():
                        summary[row.group][int(row.rank)] += 1
                    # if summary is None:
                    #     summary = self.generate_table(target, horizon, predict_model)
                    # else:
                    #     summary += self.generate_table(target, horizon, predict_model)
                        # df = self.generate_table(target, horizon, predict_model)
                        # summary = summary.append(df)
        # print summary
        rank = pd.DataFrame.from_dict(summary).fillna(0).T
        import seaborn as sns
        import matplotlib.pyplot as plt
        # from matplotlib import rcParams
        # rcParams.update({'figure.autolayout': True})
        plt.tick_params(axis='y', which='major', labelsize=5)
        plt.tick_params(axis='y', which='minor', labelsize=5)
        sns.set()
        plt.gcf().subplots_adjust(left=0.30)
        sns.heatmap(rank, annot=True, linewidths=.5, cmap="YlGnBu", robust=True, annot_kws={'size':'small'})
        # plt.tight_layout()
        plt.savefig("test.pdf")
        # stats = {
        #         'MASE' : {
        #             'sum':'sum',
        #             'median':'median',
        #             'mean' : 'mean',
        #             }
        #         }
        # print summary.groupby(['group', 'predict', 'horizon']).agg(stats)

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
