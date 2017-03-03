import pandas as pd
from tools.global_measures import GLOBAL_MEASURES

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
