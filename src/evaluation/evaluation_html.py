from collections import defaultdict
import itertools
from jinja2 import Environment, FileSystemLoader
from tools.global_measures import GLOBAL_MEASURES


class transform_into_html(object):

    """Generate HTML from tables"""

    def __init__(self, tables, error_list):
        self.colors = itertools.cycle(
            ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"])
        self.measures = GLOBAL_MEASURES.keys()
        self.cmap = dict(zip(self.measures, self.colors))
        # highlight the maximum in a Series yellow.
        self.underline_top_10 = lambda style:\
            ['text-decoration: underline;' if table_row < 10 else '' for table_row in style.rank(method='max')]

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
                    self.tables_html[target][horizon][predict_model] =\
                    self._to_html(self.tables[target][horizon][predict_model])

    def write(self, timeseries_prefix):
        self.transform()
        # Write HTML
        env = Environment(loader=FileSystemLoader('src'))
        template = env.get_template('evaluation.html')
        script = template.render(
            tables=self.tables_html, error_list=self.error_list)
        fname = "results/evaluation/%s.html" % (timeseries_prefix)
        with open(fname, "w") as f:
            f.write(script)
