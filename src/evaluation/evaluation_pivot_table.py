from tools.global_measures import GLOBAL_MEASURES

class transform_into_pivot_tables(object):
    """Generates pivot tables with diffrent mesures grouped by method type"""

    def __init__(self, tables, error_list):
        super(transform_into_pivot_tables, self).__init__()
        self.tables = tables
        self.error_list = error_list
        self.measures = GLOBAL_MEASURES.keys()

    def generate_table(self, target, horizon, predict_model):
        """ Generate a pivot table of results

        :target: target variable
        :horizon: the future horizon used
        :predict_model: the prediction model used
        :returns: a pivot table with all the methods compared to each other

        """
        data_slice = self.tables[target][horizon][predict_model]
        data_slice = data_slice.sort_values('method')

        data_slice_group = data_slice.groupby(['group', 'predict'])

        for group, data in data_slice_group:
            for measure in self.measures:
                pass

    def write(self, timeseries_prefix):
        self.timeseries_prefix = timeseries_prefix
        for target in self.tables:
            for horizon in self.tables[target]:
                for predict_model in self.tables[target][horizon]:
                    # self._plot_to_file(target, horizon, predict_model)
                    pass
