import sys
import pandas as pd
from tools.global_measures import GLOBAL_MEASURES
import pickle
from collections import defaultdict, Counter
import numpy as np
import matplotlib.pyplot as plot
import matplotlib as mpl
import seaborn as sns
sns.set(color_codes=True)

class transform_into_excel(object):

    def __init__(self, out_dir, tables, error_list):
        super(transform_into_excel, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.out_dir = out_dir

    def write(self, timeseries_prefix):
        # Write excel
        # TODO: write error list to separate spreadsheet
        # writer = pd.ExcelWriter(
        #     "%s/%s.xls" % (self.out_dir, timeseries_prefix,))
        #ret = defaultdict(lambda : defaultdict(lambda : defaultdict(Counter)))
        ret = defaultdict(list)
        mase = defaultdict(list)
        i=0
        for target_name in self.tables:
            for horizon in self.tables[target_name]:
                if horizon > 0:
                    continue
                for predict_model, val in self.tables[target_name][horizon].items():


                    for m in val.groupby(["group"]).min().iterrows():
                        # print m, m[1]['MASE'], #list(enumerate(m))
                        group = m[0]

                        # Plot sorted by N, (N,MASE)
                        # if "granger" in group and predict_model == "Vecm":
                        #     i+=1
                        #     if i >10: 
                        #         continue;
                        #     # colormap = mpl.cm.get_cmap("Dark2")
                        #     # print (val['group'])
                        #     ret1 = val[val['group'] == group ][['MASE','method']]
                        #     ret1["N"] = pd.to_numeric(ret1["method"].str.split(":").str.get(0))
                        #     print (ret1["N"].values, ret1["MASE"].values)
                        #     ret1 = ret1[ret1['MASE']<10]
                        #     plot.plot('N','MASE', data=ret1.sort_values(by=['N']))#, color=colormap.colors[i])
                        if "LinkAnalysis" in group and not "LinkAnalysisLL" in group:
                            min_MASE = val[(val["group"] == group) & (val['MASE'] == m[1]['MASE'])]
                            graph = "granger" if "granger" in group else "te"
                            reverse = 1 if "reverse_1" in group else 0
                            variables = int(min_MASE["method"].iloc[0].split(":")[0])
                            row_mase = min_MASE["MASE"].iloc[0]

                            ret[predict_model + "_" + graph + "_" + str(reverse)].append(variables)
                            mase[predict_model + "_" + graph + "_" + str(reverse)].append(row_mase)

                            #{'MASE': min_MASE["MASE"].iloc[0], "variables" : variables}

                        # print m
                    # exit()
                    # val.to_excel(writer, sheet_name="%s_%s_%s" %
                    #              (target_name, horizon, predict_model))

                    # print predict_model, type(val)
        # writer.close()

        # plot.savefig("plot.png")
        # exit()
        df = pd.DataFrame.from_dict(mase)
        df1 = pd.DataFrame.from_dict(ret)

        sns.pairplot(df1)
        plot.savefig("ret.png")
        vector = np.zeros(len(df))
        i=0
        for model in ["Vecm", "lstm"]:
            for graph in ["granger", "te"]:
                i+=1
                col = model + "_" + graph + "_"
                df1_measure = df[col + "1"]
                df2_measure = df[col + "0"]
                df1_count = df1[col + "1"]
                df2_count = df1[col + "0"]

                print "==", col, "=="
                compare_results("reverse", "normal", df1_measure, df2_measure, df1_count, df2_count)

                vector += df1_measure

        for reverse in ["1","0"]:
            for graph in ["granger", "te"]:
                col = "_" + graph + "_" + reverse
                df1_measure = df["Vecm" + col]
                df2_measure = df["lstm" + col]
                df1_count = df1["Vecm" + col]
                df2_count = df1["lstm" + col]
                print "==", col, "=="
                compare_results("Vecm", "lstm", df1_measure, df2_measure, df1_count, df2_count)
        # print vector

def compare_results(name1, name2, df1_measure, df2_measure, df1_count, df2_count):
    l = float(len(df1_count))

    print "Measure ", name1, " < ", name2,
    print ((df1_measure < df2_measure).sum()) / l
    print "Variables count ", name1, " < ", name2,
    print ((df1_count < df2_count).mean()) / l

    print "Variables count ", name1, " == ", name2,
    print ((df1_count == df2_count).mean()) / l
    print "Mean abs diff ", name1, " ", name2,
    print ((df1_count - df2_count).abs().mean())
    print "Measure and var. count", name1, " < ", name2,
    print ((df1_count < df2_count) & (df1_measure < df2_measure)).sum() / l
    print "Measure and var. count", name1, " > ", name2,
    print ((df1_count > df2_count) & (df1_measure > df2_measure)).sum() / l

    print "Measure and var. count", name1, " = ", name2,
    print ((df1_count == df2_count) & (df1_measure == df2_measure)).sum() / l
    print "==========="


def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    transform_into_excel(out_dir, tables_real, error_list).write(timeseries_prefix)


if __name__ == "__main__":
    main()
