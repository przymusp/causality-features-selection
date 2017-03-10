import sys
from collections import defaultdict
import itertools
import pickle

from jinja2 import Environment, FileSystemLoader
from tools.global_measures import GLOBAL_MEASURES


class transform_into_html(object):

    """Generate HTML from tables"""

    def __init__(self, out_dir, tables, error_list):
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
        self.out_dir = out_dir

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
        env = Environment(loader=FileSystemLoader('src/evaluation/'))
        template = env.get_template('evaluation.html')
        script = template.render(
            tables=self.tables_html, error_list=self.error_list)
        fname = "%s/%s.html" % (self.out_dir, timeseries_prefix)
        with open(fname, "w") as f:
            f.write(script)

def main():
    # Set the output prefix
    timeseries_prefix = sys.argv[1].split("/")[-1].split(".")[0]

    out_dir = sys.argv[2]
    in_dir = out_dir.replace("evaluation","pre_evaluation")

    with open("%s/%s.pickle"%(in_dir, timeseries_prefix),"rb") as in_file:
        tables_real = pickle.load(in_file)
        error_list  = pickle.load(in_file)

    transform_into_html(out_dir, tables_real, error_list).write(timeseries_prefix)


if __name__ == "__main__":
    main()
