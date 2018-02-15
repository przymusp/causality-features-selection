import sys
import pandas as pd
from tools.global_measures import GLOBAL_MEASURES
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

from collections import defaultdict, Counter

def translate_name(group):
    names = {
            'Part-GFS_granger_graph' : "Hmamouche'17",
            "LinkAnalysis_te__graph" : "TRWR",
            "LinkAnalysis_granger__graph" : "GRWR",
            "LinkAnalysisLL_granger__graph" : "LGRWR",
            "LinkAnalysisLL_te__graph" : "LTRWR",
            "dm_PCA" : "PCA",
            "Ar":"U",
            "Arima":"U",
            'naive_benchmark':'U',
            'UFSM ':"Sun\'14",
            }
    if "reduced" in group:
        print(name)
    for name in names:
        if name in group:
            group_tmp = group
            group = names[name]
            break
    return group

def report_data(target):
    names = ["GDP251", "FYFF", "CPIAUCSL", "FedFunds", "RGDP", "CPI-ALL" ]
    for n in names:
        if target in names:
            return True
    return False


class transform_into_best_excel(object):

    def __init__(self, out_dir, tables, error_list):
        super(transform_into_best_excel, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.out_dir = out_dir

    def compare_with_naive(self, target_min, measure):
        horizon = 0
        ties = Counter()
        target_top = defaultdict(Counter)
        for target_name in target_min[horizon]:
            df = target_min[horizon][target_name]
            naive = list(set(df[df['group'] == 'naive_benchmark'][measure]))[0]
            ar    = list(set(df[df['group'] == 'Ar'][measure]))[0]
            arima = list(set(df[df['group'] == 'Auto_Arima'][measure]))[0]
            print df[measure] < naive #, ar, arima

    def get_top_rank_by_measure(self, target_min, measure):
        horizon = 0
        ties = Counter()
        target_top = defaultdict(Counter)
        for target_name in target_min[horizon]:
            ranking = target_min[horizon][target_name][measure].rank(method="dense")
            ignore_group = []
            for i in range(1,4):
                df = target_min[horizon][target_name][ranking == i]
                # if report_data(target_name) and i == 1 and measure == 'rmse':
                #     print measure, target_name, df[['rmse', 'predict', 'group']]
                if len(set(df["predict"] + df["group"])) > 1:
                    ties[i] +=1
                    # print (i, df[["predict","group"]])

                for index, row in df.iterrows():
                    group = translate_name(row['group'])
                    if (group == 'U' and (group +"+"+ row['predict']) in ignore_group):
                        # print i, row["predict"], row["group"], row["method"]
                        continue
                    ignore_group.append(group +"+"+ row['predict'])
                    ignore_group.append(row['method'])
                    target_top[group +"+"+ row['predict']][i] += 1
        heatmap = pd.DataFrame.from_dict(target_top).T.fillna(0)
        # print (measure)
        # print (heatmap)
        # print (((heatmap/len(target_min[horizon]))*100.0).round(1)).to_latex()
        # print (heatmap.sum())
        # print (ties)
        # print heatmap.to_latex()
        self.__plot_heatmap(heatmap, self.timeseries_prefix.split(".")[0]+measure+".pdf")

    def write(self, timeseries_prefix):
        target_min = defaultdict(lambda : defaultdict(list))
        self.timeseries_prefix = timeseries_prefix
        for target_name in self.tables:
            for horizon in self.tables[target_name]:
                for predict_model, val in self.tables[target_name][horizon].items():
                    val['horizon'] = horizon
                    target_min[horizon][target_name].append(val)

                target_min[horizon][target_name] = pd.concat(target_min[horizon][target_name], ignore_index=True)
        self.get_top_rank_by_measure(target_min, "rmse")
        self.get_top_rank_by_measure(target_min, "MASE")

        #self.compare_with_naive(target_min, "rmse")
        #self.compare_with_naive(target_min, "MASE")




    def __plot_heatmap(self, heat_map, out_fname):
        sns.set()
        # ax = plt.figure(figsize=(4,3))
        sns.heatmap(heat_map, annot=True, linewidths=.5, cmap="YlGnBu", robust=True, annot_kws={'size':8}, fmt='g')
        plt.setp( plt.gca().yaxis.get_majorticklabels(), rotation='horizontal' )
        plt.xlabel("Top ranking")
        # plt.setp( plt.gca().xaxis.get_majorticklabels(), rotation='vertical' )
        plt.tick_params(axis='y', which='major', labelsize=6)
        plt.tick_params(axis='y', which='minor', labelsize=6)
        plt.tick_params(axis='x', which='major', labelsize=9)
        plt.tick_params(axis='x', which='minor', labelsize=9)
        plt.savefig(out_fname)
        plt.clf()

            # pd.DataFrame.from_dict(ret).to_excel(writer, sheet_name=str(horizon))

        # writer.close()



def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    transform_into_best_excel(out_dir, tables_real, error_list).write(timeseries_prefix)


if __name__ == "__main__":
    main()
