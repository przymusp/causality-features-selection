import sys
import pandas as pd
from tools.global_measures import GLOBAL_MEASURES
import pickle

from collections import defaultdict

class transform_into_best_excel(object):

    def __init__(self, out_dir, tables, error_list):
        super(transform_into_best_excel, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.out_dir = out_dir

    def write(self, timeseries_prefix):
        # TODO: fix callculate it per horizon
        # Write excel
        # TODO: write error list to separate spreadsheet
        target_min = {}
        for target_name in self.tables:
            for horizon in self.tables[target_name]:
                for predict_model, val in self.tables[target_name][horizon].items():
                    target_min[target_name] = val.iloc[val['rmse'].idxmin()][['rmse', 'group', 'predict', 'method']]

        writer = pd.ExcelWriter(
            "%s/%s_best.xls" % (self.out_dir, timeseries_prefix,))
        pd.DataFrame.from_dict(target_min).to_excel(writer)
        writer.close()

class transform_into_best_horizon_excel(object):

    def __init__(self, out_dir, tables, error_list):
        self.tables = tables
        self.error_list = error_list
        self.out_dir = out_dir

    def write(self, timeseries_prefix):
        # Write excel
        # TODO: write error list to separate spreadsheet
        target_min = {}
        c = 0
        for target_name in self.tables:
            for horizon in self.tables[target_name]:
                for predict_model, val in self.tables[target_name][horizon].items():
                    if not target_min.has_key(target_name):
                        target_min[target_name] = val
                    else:
                        target_min[target_name] += val
                    c += 1
        for target in target_min:
            target_min[target] = val.iloc[val['rmse'].idxmin()][['rmse', 'group', 'predict', 'method']]
            target_min[target]['rmse'] /= c


        writer = pd.ExcelWriter(
            "%s/%s_best_avg.xls" % (self.out_dir, timeseries_prefix,))
        pd.DataFrame.from_dict(target_min).to_excel(writer)
        writer.close()

def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    transform_into_best_excel(out_dir, tables_real, error_list).write(timeseries_prefix)
    transform_into_best_horizon_excel(out_dir, tables_real, error_list).write(timeseries_prefix)


if __name__ == "__main__":
    main()
