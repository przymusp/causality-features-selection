import re
import seaborn as sns
import matplotlib.pyplot as plt
from tools.global_measures import GLOBAL_MEASURES


class transform_into_figure(object):
    """Generates figures with diffrent mesures grouped by method type"""

    def __init__(self, tables, error_list):
        super(transform_into_figure, self).__init__()
        self.tables = tables
        self.error_list = error_list

        self.default_plot_styles = {
            "LinkAnalysis.*": {'ls': '-', 'marker': '*'},
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
            ax.plot(data_sorted[['method']],
                    data_sorted[[measure]], label=group[0], **plot_style)
        else:
            ax.axhline(y=data_sorted[[measure]].values[0][0],
                    label=group[0], **plot_style)

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

        data_slice_group = data_slice.groupby(['group', 'predict'])
        sns.husl_palette(n_colors=len(data_slice_group))
        # print(len(data_slice_group))

        for group, data in data_slice_group:
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
